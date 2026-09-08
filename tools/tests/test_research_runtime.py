"""V2 regression tests use temporary projects and a mocked Codex process."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
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
        result['new_claims'][0]['status'] = 'proof-draft'
        self.save(result)
        with self.assertRaises(ValueError):
            runtime.apply_result(self.project, self.directory)
        result['audit'] = dict(checks=['pass']*10, report_file='notes/lemma.md')
        self.save(result)
        runtime.apply_result(self.project, self.directory)
        self.assertEqual(queue.read_status('sample'), 'solved-awaiting-human-verification')
        self.assertNotIn('human-verified', (self.project / 'verification-ledger.md').read_text())

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
        path.write_text(path.read_text().replace('## Current mathematical status',
            '## Current mathematical status\n\n' + 'x' * 12500))
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

    def test_invalid_result_and_preflight_never_silently_continue(self):
        def no_result(command, project, event_log, timeout_seconds):
            event_log.write_text('')
            return dict(return_code=0, timed_out=False)
        with mock.patch.object(queue, 'run_codex_process', side_effect=no_result):
            self.assertEqual(queue.execute_attempt(self.item, self.config), 1)
        self.assertEqual(queue.read_status('sample'), 'needs-human-review')
        config = {**self.config, 'context_budget': {'packet_hard_tokens': 50, 'packet_target_tokens': 25}}
        with mock.patch.object(queue, 'run_codex_process') as process:
            self.assertEqual(queue.execute_attempt(self.item, config), 1)
            process.assert_not_called()


if __name__ == '__main__':
    unittest.main()
