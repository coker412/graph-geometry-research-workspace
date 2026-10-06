"""V2 regression tests use temporary projects and a mocked Codex process."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('v2_queue', ROOT / 'tools/conjecture_queue.py')
queue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(queue)
runtime = queue.runtime


class RuntimeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        queue.ROOT = self.root
        queue.QUEUE_ROOT = self.root / 'problems/important-conjectures'
        queue.ITEMS_ROOT = queue.QUEUE_ROOT / 'items'
        queue.RUNTIME_ROOT = self.root / 'agents/important-conjectures'
        queue.RUNNER_CONFIG = queue.QUEUE_ROOT / 'runner.toml'
        queue.ITEM_TEMPLATE_ROOT = ROOT / 'templates/important-conjecture'
        queue.ITEMS_ROOT.mkdir(parents=True)
        (self.root / 'projects').mkdir()
        shutil.copy2(ROOT / 'AGENTS.md', self.root / 'AGENTS.md')
        shutil.copytree(ROOT / 'agents/core', self.root / 'agents/core')
        shutil.copytree(ROOT / 'agents/protocols', self.root / 'agents/protocols')
        queue.RUNNER_CONFIG.write_text('web_search = false\n')
        queue.add_item(argparse.Namespace(slug='sample', title='sample'))
        self.item = queue.discover_items()[0]
        self.project = queue.ensure_project(self.item)
        self.snapshot = queue.create_input_snapshot(self.item, self.project)
        self.config = runtime.phase_config(queue.load_runner_config(), self.item)
        self.config['codex_path'] = '/bin/true'
        self.directory = self.project / '.runtime/rounds/test-1'

    def tearDown(self):
        self.temp.cleanup()

    def prepare(self):
        text, metadata = runtime.compile_packet(self.root, self.project,
            self.snapshot / 'problem.md', self.config, self.item, 'offline')
        runtime.prepare_round(self.project, self.directory, text, metadata)
        return metadata

    def result(self, directory=None):
        directory = directory or self.directory
        path = self.project / 'notes/lemma.md'
        path.write_text('# Lemma\nAssume n = 1. Then n squared = 1.\nDirect multiplication.\n')
        return dict(schema_version=1, round_id=directory.name,
            packet_sha256=runtime.read_json(directory / 'PACKET.json')['packet_sha256'],
            round_status='progress', queue_status='pushing', summary='Special case only.',
            active_gap='G2: arbitrary n', next_target='Test n = 2', acceptance='Exact multiplication',
            checks='Checked n = 1 with exact arithmetic', active_routes=['A1'], blocked_routes=[],
            new_gaps=['G2'], closed_gaps=[],
            new_claims=[dict(id='N1', statement='The n = 1 special case.',
                assumptions='n = 1', dependencies='none', checks='Direct multiplication',
                status='partial-result', source='internal-offline', statement_file='notes/lemma.md')],
            evidence=[dict(file='notes/lemma.md', start=1, end=3,
                sha256=runtime.digest(path), purpose='special-case proof', source='internal-offline')])

    def save(self, result):
        runtime.write_json(self.directory / 'ROUND_RESULT.json', result)

    def test_phase_routing_and_explicit_escalation(self):
        for phase, (effort, _) in runtime.PHASES.items():
            actual = runtime.phase_config({'phase': phase}, {})
            self.assertEqual(actual['reasoning_effort'], effort)
        with self.assertRaises(ValueError):
            runtime.phase_config({'reasoning_effort': 'xhigh'}, {})
        self.assertEqual(runtime.phase_config({}, {'config': {'phase': 'experiment'}})['phase'], 'experiment')
        with self.assertRaises(ValueError):
            runtime.phase_config({}, {'config': {'phase': 'invalid'}})

    def test_tree_and_dependency_index_refresh_without_erasing_authored_graphs(self):
        tree = self.project / 'research-tree.md'
        tree.write_text(tree.read_text() + '\n## 历史路线\n旧路线的明确适用范围。\n')
        self.prepare()
        result = self.result()
        self.save(result)
        runtime.apply_result(self.project, self.directory)
        text = tree.read_text()
        self.assertIn('G2: arbitrary n', text)
        self.assertIn('A1', text)
        self.assertIn('旧路线的明确适用范围。', text)
        self.assertNotIn('主问题：待审计', text)
        self.assertNotIn('P0 主问题<br/>conjecture', text)
        proof = (self.project / 'proof-map.md').read_text()
        self.assertIn('报告的依赖：none', proof)
        self.assertIn('假设：n = 1', proof)
        self.assertIn('`N1`（`partial-result`）', proof)
        self.assertNotIn('T0 主猜想<br/>conjecture', proof)
        # A manual edge is evidence-sensitive content, not a disposable template.
        authored = '```mermaid\nflowchart TD\n    L1 --> T1\n```'
        tree.write_text(text + '\n## 人工依赖\n' + authored + '\n')
        rendered = runtime.render_updates(self.project, self.directory, result)
        self.assertIn(authored, rendered['research-tree.md'].decode())

    def test_machine_status_updates_only_the_status_field_in_recovery_index(self):
        index = self.project / 'CURRENT_STATE.md'
        old = index.read_text()
        for status in ('paused', 'attempt-limit', 'needs-human-review'):
            queue.write_status(self.item['slug'], status)
            expected = runtime.re.sub(r'^- queue-status:.*$',
                f'- queue-status: `{status}`', old, flags=runtime.re.M)
            self.assertEqual(index.read_text(), expected)
            self.assertEqual(queue.read_status(self.item['slug']), status)

    def test_status_heading_case_does_not_leave_a_second_stale_summary(self):
        old = '# Tree\n\n## Current Status\nOld summary\n\n## Route Map\nKeep graph\n'
        new = runtime.section_replace(old, '## Current status', 'New summary')
        self.assertNotIn('Old summary', new)
        self.assertEqual(new.lower().count('## current status'), 1)
        self.assertIn('Keep graph', new)

    def test_byte_budget_aliases_and_conflicting_units(self):
        old = runtime.context_budget({'packet_target_tokens': 100, 'packet_hard_tokens': 200,
                                      'max_single_evidence_tokens': 80})
        self.assertEqual(old['packet_hard_bytes'], 200)
        self.assertEqual(old['max_single_evidence_bytes'], 80)
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            runtime.context_budget({'packet_hard_tokens': 200, 'packet_hard_bytes': 300})

    def test_large_chinese_proof_commits_under_old_small_packet_budget(self):
        self.config['context_budget'] = {'max_single_evidence_tokens': 8000}
        self.prepare()
        result = self.result()
        path = self.project / 'notes/lemma.md'
        body = '# Proof\n' + '保留完整证明和全部假设。' * 1000 + '\nConclusion.\n'
        path.write_text(body)
        result['evidence'][0]['sha256'] = runtime.digest(path)
        self.save(result)
        runtime.apply_result(self.project, self.directory)
        self.assertEqual(path.read_text(), body)
        text, meta = runtime.compile_packet(self.root, self.project,
            self.snapshot / 'problem.md', self.config, self.item, 'offline')
        self.assertIn('NOT INLINED', text)
        self.assertEqual(len(meta['deferred_evidence']), 1)
        self.assertIn(result['evidence'][0]['sha256'], text)
        self.assertFalse(meta['evidence'][0]['inlined'])
        self.assertTrue((self.directory / 'APPLIED.json').exists())
        # Deferral never makes a wrong hash acceptable.
        path.write_text(body + 'changed')
        with self.assertRaisesRegex(ValueError, 'stale evidence hash'):
            runtime.compile_packet(self.root, self.project, self.snapshot / 'problem.md',
                                   self.config, self.item, 'offline')

    def test_eight_archived_entries_with_six_inline_slots(self):
        self.prepare()
        result = self.result()
        entry = result['evidence'][0]
        result['evidence'] = [{**entry, 'purpose': f'use {i}'} for i in range(8)]
        runtime.validate_result(self.project, self.directory, result)
        runtime.write_json(self.project / '.runtime/evidence.json', {'evidence': result['evidence']})
        text, meta = runtime.compile_packet(self.root, self.project, self.snapshot / 'problem.md',
            {**self.config, 'context_budget': {'max_evidence_slices': 6}}, self.item, 'offline')
        self.assertEqual(len(meta['evidence']), 8)
        self.assertEqual(len(meta['deferred_evidence']), 2)
        self.assertIn('use 7', text)

    def test_total_budget_defers_whole_ranges_not_proof_prefixes(self):
        self.prepare()
        result = self.result()
        _, base = runtime.compile_packet(self.root, self.project, self.snapshot / 'problem.md',
                                         self.config, self.item, 'offline')
        path = self.project / 'notes/lemma.md'
        path.write_text('BEGINPROOF\n' + 'x' * 8000 + '\nENDPROOF\n')
        entry = {**result['evidence'][0], 'sha256': runtime.digest(path)}
        runtime.write_json(self.project / '.runtime/evidence.json', {'evidence': [entry]})
        cap = base['bytes'] + 2000
        text, meta = runtime.compile_packet(self.root, self.project, self.snapshot / 'problem.md',
            {**self.config, 'context_budget': {'packet_target_bytes': cap, 'packet_hard_bytes': cap}},
            self.item, 'offline')
        self.assertLessEqual(meta['bytes'], cap)
        self.assertIn('NOT INLINED', text)
        self.assertNotIn('BEGINPROOF', text)
        self.assertEqual(path.read_text().count('ENDPROOF'), 1)

    def test_chinese_frontiers_replace_old_duplicate_english_sections(self):
        state = self.project / 'CURRENT_STATE.md'
        text = state.read_text()
        for en, zh in [('Active proof frontier', '当前证明缺口'),
                       ('Next bounded round', '下一有界回合'), ('Evidence pointers', '证据指针')]:
            text = text.replace('## ' + en, '## ' + zh)
            text += '\n## ' + en + '\n\nStale duplicate.\n'
        state.write_text(text)
        self.prepare()
        self.save(self.result())
        runtime.apply_result(self.project, self.directory)
        after = state.read_text()
        for heading in ('当前证明缺口', '下一有界回合', '证据指针'):
            self.assertEqual(after.count('## ' + heading), 1)
        self.assertNotIn('## Active proof frontier', after)
        self.assertNotIn('Stale duplicate.', after)
        self.assertEqual((self.directory / 'before/CURRENT_STATE.md').read_text(), text)
        self.assertEqual(queue.validate_current_state(self.project), [])

    def test_packet_is_read_only_bounded_and_phase_specific(self):
        before = {p: p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        text, meta = runtime.compile_packet(self.root, self.project,
            self.snapshot / 'problem.md', self.config, self.item, 'offline')
        self.assertIn('## protocol', text)
        self.assertNotIn('# 文献核查', text)
        self.assertEqual(meta['bytes'], len(text.encode()))
        self.assertEqual(before, {p: p.read_bytes() for p in self.project.rglob('*') if p.is_file()})
        with self.assertRaises(ValueError):
            runtime.compile_packet(self.root, self.project, self.snapshot / 'problem.md',
                {**self.config, 'context_budget': {'packet_hard_tokens': 100, 'packet_target_tokens': 50}}, self.item, 'offline')
        with self.assertRaises(ValueError):
            runtime.compile_packet(self.root, self.project, self.snapshot / 'problem.md',
                {**self.config, 'phase': 'literature'}, self.item, 'offline')

    def test_packet_prefix_stable_across_projects_and_round_instructions(self):
        first, meta = runtime.compile_packet(self.root, self.project,
            self.snapshot / 'problem.md', self.config, self.item, 'offline', 'round one')
        other = self.root / 'projects/other'
        other.mkdir()
        (other / 'CURRENT_STATE.md').write_text('Different state')
        problem = other / 'problem.md'
        problem.write_text('Different problem')
        second, other_meta = runtime.compile_packet(self.root, other, problem,
            self.config, {**self.item, 'search_contract': 'counterexample'}, 'offline', 'round two')
        n = meta['stable_prefix_bytes']
        self.assertEqual(first.encode()[:n], second.encode()[:n])
        self.assertEqual(meta['stable_prefix_sha256'], other_meta['stable_prefix_sha256'])
        self.assertIn('Different problem', second)
        self.assertIn('counterexample', second)
        self.assertIn('round two', second)
        self.assertNotEqual(meta['packet_sha256'], other_meta['packet_sha256'])

    def test_duplicate_evidence_reuses_text_but_preserves_purposes_and_validation(self):
        path = self.project / 'notes/repeated.md'
        content = 'Complete evidence, with all hypotheses intact. ' * 30 + '\n'
        path.write_text(content)
        entry = dict(file='notes/repeated.md', start=1, end=1,
                     sha256=runtime.digest(path), source='internal-offline', purpose='first use')
        entries = [entry, {**entry, 'purpose': 'second use'}]
        manifest = self.project / '.runtime/evidence.json'
        runtime.write_json(manifest, {'evidence': entries})
        text, meta = runtime.compile_packet(self.root, self.project,
            self.snapshot / 'problem.md', self.config, self.item, 'offline')
        self.assertEqual(text.count(content), 1)
        self.assertIn('first use', text)
        self.assertIn('second use', text)
        self.assertEqual(len(meta['evidence']), 2)
        self.assertGreater(meta['evidence_dedup_saved_bytes'], 0)
        for patch in ({'source': 'web-source'}, {'sha256': '0'*64}):
            runtime.write_json(manifest, {'evidence': [entry, {**entry, **patch}]})
            with self.assertRaises(ValueError):
                runtime.compile_packet(self.root, self.project,
                    self.snapshot / 'problem.md', self.config, self.item, 'offline')

    def test_slice_rejects_stale_hash_escape_source_and_range(self):
        self.prepare()
        entry = self.result()['evidence'][0]
        for patch in ({'sha256': '0'*64}, {'file': '../AGENTS.md'}, {'source': 'web-source'},
                      {'end': 100}, {'start': 0}, {'end': True}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                runtime.evidence_slice(self.project, {**entry, **patch}, 'offline', runtime.BUDGET)
        link = self.project / 'notes/linked.md'
        link.symlink_to(self.project / 'notes/lemma.md')
        with self.assertRaises(ValueError):
            runtime.evidence_slice(self.project, {**entry, 'file': 'notes/linked.md'}, 'offline', runtime.BUDGET)
        (self.project / 'notes/lemma.md').write_text('')
        entry['sha256'] = runtime.digest(self.project / 'notes/lemma.md')
        with self.assertRaises(ValueError):
            runtime.evidence_slice(self.project, entry, 'offline', runtime.BUDGET)

    def test_commit_preserves_history_scope_levels_and_is_idempotent(self):
        meta = self.prepare()
        before = (self.project / 'CURRENT_STATE.md').read_text()
        progress = (self.project / 'progress.md').read_bytes()
        result = self.result()
        self.save(result)
        record = runtime.apply_result(self.project, self.directory)
        self.assertEqual(record, runtime.apply_result(self.project, self.directory))
        self.assertTrue((self.project / 'progress.md').read_bytes().startswith(progress))
        self.assertEqual((self.project / 'progress.md').read_text().count('runtime-round:test-1'), 1)
        after = (self.project / 'CURRENT_STATE.md').read_text()
        for line in before.splitlines():
            if line.startswith('- evidence-ceiling:'):
                self.assertIn(line, after)
        self.assertEqual(queue.validate_current_state(self.project), [])
        self.assertEqual(queue.read_status('sample'), 'pushing')
        self.assertTrue((self.directory / 'before/CURRENT_STATE.md').is_file())
        next_text, next_meta = runtime.compile_packet(self.root, self.project,
            self.snapshot / 'problem.md', self.config, self.item, 'offline')
        self.assertIn('Direct multiplication.', next_text)
        self.assertEqual(len(next_meta['evidence']), 1)
        self.assertLess(len(after.encode()), 12288)
        self.assertEqual(meta['packet_sha256'], result['packet_sha256'])

    def test_reject_promotion_and_wrong_packet_before_any_write(self):
        self.prepare()
        result = self.result()
        before = {n: runtime.digest(self.project / n) for n in runtime.PROTECTED}
        for level in ('agent-verified', 'human-verified', 'formalized'):
            changed = copy.deepcopy(result)
            changed['new_claims'][0]['status'] = level
            self.save(changed)
            with self.assertRaises(ValueError):
                runtime.apply_result(self.project, self.directory)
        changed = copy.deepcopy(result)
        changed['packet_sha256'] = '0'*64
        self.save(changed)
        with self.assertRaises(ValueError):
            runtime.apply_result(self.project, self.directory)
        self.assertEqual(before, {n: runtime.digest(self.project / n) for n in runtime.PROTECTED})
        self.assertFalse((self.directory / 'COMMIT.json').exists())

    def test_state_schema_failure_is_rejected_by_preflight_and_before_commit(self):
        state = self.project / 'CURRENT_STATE.md'
        state.write_text(state.read_text().replace('- schema-version: 1', '- schema-version: invalid'))
        self.prepare()
        self.save(self.result())
        before = {n: runtime.digest(self.project / n) for n in runtime.PROTECTED}
        check = subprocess.run([sys.executable, str(ROOT / 'tools/research_runtime.py'),
            'check-result', '--project', str(self.project), '--round',
            str(self.directory.relative_to(self.project))], capture_output=True, text=True)
        self.assertNotEqual(check.returncode, 0)
        self.assertIn('invalid rendered CURRENT_STATE', check.stderr)
        with self.assertRaisesRegex(ValueError, 'invalid rendered CURRENT_STATE'):
            runtime.apply_result(self.project, self.directory)
        self.assertEqual(before, {n: runtime.digest(self.project / n) for n in runtime.PROTECTED})
        self.assertFalse((self.directory / 'COMMIT.json').exists())

    def test_new_state_and_generated_summary_are_chinese_without_level_upgrade(self):
        state = self.project / 'CURRENT_STATE.md'
        self.assertIn('## 控制信息', state.read_text())
        self.assertIn('主命题仍为猜想', state.read_text())
        self.assertFalse((self.project / 'lean').exists())
        self.prepare()
        self.save(self.result())
        runtime.apply_result(self.project, self.directory)
        text = state.read_text()
        for label in ('本轮摘要：', '认证边界：', '当前缺口：', '验收：', '本轮结果：'):
            self.assertIn(label, text)
        self.assertIn('- evidence-ceiling: `conjecture`', text)
        self.assertEqual(queue.validate_current_state(self.project), [])

    def test_conflict_and_incomplete_transaction_do_not_overwrite(self):
        self.prepare()
        self.save(self.result())
        path = self.project / 'progress.md'
        path.write_text(path.read_text() + '\nResearcher edit\n')
        with self.assertRaisesRegex(ValueError, 'protected file changed'):
            runtime.apply_result(self.project, self.directory)
        self.assertIn('Researcher edit', path.read_text())
        runtime.write_json(self.directory / 'COMMIT.json', {})
        with self.assertRaisesRegex(ValueError, 'incomplete transaction'):
            runtime.apply_result(self.project, self.directory)

    def test_candidate_requires_audit_and_freezes_without_certification(self):
        self.prepare()
        result = self.result()
        result['round_status'] = 'candidate-solution'
        result['queue_status'] = 'solved-awaiting-human-verification'
        result['new_claims'][0]['status'] = 'proof-draft'
        self.save(result)
        with self.assertRaises(ValueError):
            runtime.apply_result(self.project, self.directory)
        result['audit'] = dict(checks=['pass']*10, report_file='notes/lemma.md')
        result['solution_scope'] = dict(
            kind='full-original-problem',
            problem_sha256=runtime.read_json(self.directory / 'PACKET.json')['problem_sha256'],
            unresolved_parts=[],
            coverage_statement='The claim covers every quantifier and conclusion in the formal input.',
        )
        self.save(result)
        runtime.apply_result(self.project, self.directory)
        self.assertEqual(queue.read_status('sample'), 'solved-awaiting-human-verification')
        self.assertNotIn('human-verified', (self.project / 'verification-ledger.md').read_text())

    def test_local_or_partial_candidate_cannot_trigger_global_freeze(self):
        self.prepare()
        result = self.result()
        result['round_status'] = 'candidate-solution'
        result['queue_status'] = 'solved-awaiting-human-verification'
        result['new_claims'][0]['status'] = 'proof-draft'
        result['audit'] = dict(checks=['pass']*10, report_file='notes/lemma.md')
        packet = runtime.read_json(self.directory / 'PACKET.json')
        for scope in (
            None,
            dict(kind='authorized-subproblem', problem_sha256=packet['problem_sha256'],
                 unresolved_parts=[], coverage_statement='Only a subproblem.'),
            dict(kind='full-original-problem', problem_sha256=packet['problem_sha256'],
                 unresolved_parts=['general n'], coverage_statement='The special case n=1 only.'),
        ):
            with self.subTest(scope=scope):
                changed = copy.deepcopy(result)
                if scope is not None:
                    changed['solution_scope'] = scope
                self.save(changed)
                with self.assertRaises(ValueError):
                    runtime.apply_result(self.project, self.directory)
        self.assertEqual(queue.read_status('sample'), 'queued')

    def test_commit_refreshes_state_and_proof_map_status_sections(self):
        self.prepare()
        result = self.result()
        self.save(result)
        runtime.apply_result(self.project, self.directory)
        state = (self.project / 'CURRENT_STATE.md').read_text()
        proof_map = (self.project / 'proof-map.md').read_text()
        self.assertIn('Special case only.', state)
        self.assertIn('`N1` (`partial-result`', state)
        self.assertNotIn('- 可用结果：尚未记录', state)
        self.assertIn('G2: arbitrary n', proof_map)
        self.assertIn('`N1` (`partial-result`', proof_map)

    def test_telemetry_counts_turns_tools_and_unknown_fields(self):
        path = self.project / 'events.jsonl'
        events = [dict(type='item.started', item=dict(id='1', type='command_execution')),
                  dict(type='item.completed', item=dict(id='1', type='command_execution')),
                  dict(type='turn.completed', usage=dict(input_tokens=100, cached_input_tokens=80, output_tokens=12)),
                  dict(type='turn.completed', usage=dict(input_tokens=50, cached_input_tokens=30, output_tokens=5))]
        path.write_text('stderr noise\n' + '\n'.join(json.dumps(e) for e in events))
        result = runtime.telemetry(path)
        self.assertEqual(result['input_tokens'], 150)
        self.assertEqual(result['tool_calls'], 1)
        self.assertIsNone(result['reasoning_output_tokens'])
        self.assertIsNone(result['files_read'])
        total = runtime.aggregate_usage({'offline': path, 'connected': self.project / 'missing'})
        self.assertEqual(total['input_tokens'], 150)
        self.assertFalse(total['complete'])

    def fake_process(self, command, project, event_log, timeout_seconds):
        directory = next((project / '.runtime/rounds').iterdir())
        result = self.result(directory)
        runtime.write_json(directory / 'ROUND_RESULT.json', result)
        event_log.write_text(json.dumps(dict(type='turn.completed', usage=dict(
            input_tokens=120, cached_input_tokens=20, output_tokens=10))) + '\n')
        return dict(return_code=0, timed_out=False)

    def test_shell_wrapper_preserves_dry_run_arguments(self):
        shutil.copy2(ROOT / 'queue.sh', self.root / 'queue.sh')
        (self.root / 'tools').mkdir(exist_ok=True)
        stub = self.root / 'tools/conjecture_queue.sh'
        stub.write_text('#!/bin/bash\nprintf "%s\\n" "$@"\n')
        stub.chmod(0o755)
        for verb, expected in (("run", ["run"]), ("once", ["run", "--once"]),
                               ("packet", ["packet"]), ("usage", ["usage"])):
            result = subprocess.run(['bash', str(self.root / 'queue.sh'), verb,
                '--dry-run', '--slug', 'sample'], capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.splitlines(), expected + ['--dry-run', '--slug', 'sample'])

    def test_oversized_state_and_duplicate_claim_do_not_mutate(self):
        # The compatibility audit permits 32 KiB, the V2 writer must not truncate it.
        path = self.project / 'CURRENT_STATE.md'
        path.write_text(path.read_text().replace('## 问题与范围',
            '## 问题与范围\n\n' + 'x' * 12500))
        self.prepare()
        result = self.result()
        self.save(result)
        before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'exceeds 12 KiB'):
            runtime.apply_result(self.project, self.directory)
        self.assertEqual(path.read_bytes(), before)
        result['new_claims'].append(copy.deepcopy(result['new_claims'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            runtime.validate_result(self.project, self.directory, result)

    def test_real_queue_wiring_with_mock_model(self):
        with mock.patch.object(queue, 'run_codex_process', side_effect=self.fake_process):
            self.assertEqual(queue.execute_attempt(self.item, self.config), 0)
        state = queue.read_runtime_state('sample')
        self.assertEqual(state['last_telemetry']['reasoning_effort'], 'high')
        self.assertEqual(state['last_telemetry']['usage']['input_tokens'], 120)
        self.assertEqual(state['last_telemetry']['result']['new_claims'], 1)
        self.assertEqual(queue.read_status('sample'), 'pushing')

    def test_queue_derives_assessment_from_one_model_result(self):
        def process(command, project, event_log, timeout_seconds):
            outcome = self.fake_process(command, project, event_log, timeout_seconds)
            directory = next((project / '.runtime/rounds').iterdir())
            assessment = queue.research_progress.round_dir(project, directory.name)
            plan = queue.research_progress.read(assessment / 'PLAN.json')
            plan.update(author_id='author', family_id='F1', obstacle_id='G1',
                        mechanism='special case', gap_before='all n unresolved',
                        acceptance_test='direct multiplication')
            runtime.write_json(assessment / 'PLAN.json', plan)
            queue.research_progress.seal_plan(project, assessment)
            value = runtime.read_json(directory / 'ROUND_RESULT.json')
            value['progress'] = dict(claimed_kind='enabling-result',
                main_problem_effect='n=1 case only', scope_limitations='n=1', evidence_level='proof-draft')
            runtime.write_json(directory / 'ROUND_RESULT.json', value)
            packet = (directory / 'RESEARCH_PACKET.md').read_text()
            self.assertIn('不重复填写 RESULT.json', packet)
            return outcome
        with mock.patch.object(queue, 'run_codex_process', side_effect=process) as model:
            self.assertEqual(queue.execute_attempt(self.item, self.config), 0)
            self.assertEqual(model.call_count, 1)
        state = queue.read_runtime_state('sample')
        self.assertNotIn('progress_import_error', state)
        self.assertEqual(state['progress_assessment']['status'], 'self-report')
        self.assertEqual(state['progress_assessment']['decision']['no_frontier_rounds'], 0)
        assessment = self.project / state['progress_assessment']['round']
        self.assertTrue((assessment / 'RESULT.lock.json').exists())
        self.assertFalse((assessment / 'REVIEW.json').exists())

    def test_invalid_result_and_preflight_never_silently_continue(self):
        def no_result(command, project, event_log, timeout_seconds):
            event_log.write_text('')
            return dict(return_code=0, timed_out=False)
        with mock.patch.object(queue, 'run_codex_process', side_effect=no_result):
            self.assertEqual(queue.execute_attempt(self.item, self.config), 1)
        self.assertEqual(queue.read_status('sample'), 'needs-human-review')
        # Simulate explicit recovery before testing the separate packet preflight.
        queue.write_status('sample', 'queued')
        config = {**self.config, 'context_budget': {'packet_hard_tokens': 50, 'packet_target_tokens': 25}}
        with mock.patch.object(queue, 'run_codex_process') as process:
            self.assertEqual(queue.execute_attempt(self.item, config), 1)
            process.assert_not_called()

    def test_assessment_import_failure_is_not_a_failed_research_round(self):
        def process(command, project, event_log, timeout_seconds):
            outcome = self.fake_process(command, project, event_log, timeout_seconds)
            directory = next((project / '.runtime/rounds').iterdir())
            value = runtime.read_json(directory / 'ROUND_RESULT.json')
            value['progress'] = {}  # Missing author assessment, not a failed proof.
            runtime.write_json(directory / 'ROUND_RESULT.json', value)
            return outcome
        with mock.patch.object(queue, 'run_codex_process', side_effect=process) as model:
            self.assertEqual(queue.execute_attempt(self.item, self.config), 0)
            self.assertEqual(model.call_count, 1)
        state = queue.read_runtime_state('sample')
        self.assertIn('progress_import_error', state)
        self.assertEqual(state['consecutive_runtime_failures'], 0)
        self.assertEqual(state['progress_assessment']['status'], 'unknown')
        self.assertEqual(queue.read_status('sample'), 'pushing')


if __name__ == '__main__':
    unittest.main()
