"""Exercise real packet/plan/writer boundaries without launching a model."""
import copy
import json
import unittest
from unittest import mock
import test_research_runtime as fixture

runtime = fixture.runtime
progress = fixture.queue.research_progress


class ResearchTaskTest(unittest.TestCase):
    def setUp(self):
        self.f = fixture.RuntimeTest()
        self.f.setUp()
        self.project = self.f.project
        self.f.config['research_task_version'] = 1

    def tearDown(self):
        self.f.tearDown()

    def step(self, number=1, review=False):
        self.f.directory = self.project / f'.runtime/rounds/attempt-{number:08d}'
        self.assessment = progress.prepare(self.project, self.f.directory.name, number,
            research_task_version=1, problem_sha256=runtime.digest(self.f.snapshot / 'problem.md'))
        plan = progress.read(self.assessment / 'PLAN.json')
        plan.update(author_id='author', family_id='uniform-bound', obstacle_id='endpoint',
                    mechanism='rescale and test boundary', gap_before='endpoint uniformity',
                    acceptance_test='bound independent of epsilon')
        if not plan['research_task']['objective']:
            plan['research_task'].update(objective='Uniform bound including endpoints',
                                        acceptance='Derive a bound independent of epsilon under original assumptions')
        if review:
            (self.project / 'notes/review.md').write_text('Interior estimates fail at the endpoint. Test rescaling next.\n')
            plan['strategy_review'] = 'notes/review.md'
        runtime.write_json(self.assessment / 'PLAN.json', plan)
        progress.seal_plan(self.project, self.assessment)
        self.f.prepare()
        value = self.f.result()
        # Distinct evidence files: later steps must not rewrite sealed earlier evidence.
        old = self.project / 'notes/lemma.md'
        new = self.project / f'notes/step-{number}.md'
        old.rename(new)
        value['new_claims'] = []
        value['evidence'][0]['file'] = str(new.relative_to(self.project))
        value['progress'] = dict(claimed_kind='enabling-result', main_problem_effect='Interior only',
                                 scope_limitations='Endpoint still open', evidence_level='proof-draft')
        value['research_task'] = dict(id=plan['research_task']['id'], step_outcome='auxiliary',
             close_reason='continue', bridge_evidence=[value['evidence'][0]['file']],
             remaining_obligations=['Endpoint uniformity'], acceptance_evidence=[],
             failure_evidence=[], alternative_evidence=[])
        return value

    def apply(self, value):
        self.f.save(value)
        applied = runtime.apply_result(self.project, self.f.directory)
        progress.import_round_result(self.project, self.assessment)
        progress.finish(self.project, self.assessment, 0, False)
        return applied

    def test_auxiliary_step_continues_same_target_across_calls(self):
        first = self.step()
        self.apply(first)
        second = self.step(2)
        self.assertEqual(first['research_task']['id'], second['research_task']['id'])
        self.apply(second)
        state = progress.summary(self.project)
        self.assertEqual(state['research_tasks']['active']['steps'], 2)
        self.assertEqual(state['research_tasks']['totals']['acceptance_reported'], 0)
        self.assertEqual(state['latest']['status'], 'self-report')
        self.assertEqual(state['decision']['no_frontier_rounds'], 0)

    def test_original_objective_and_acceptance_cannot_be_shrunk(self):
        self.apply(self.step())
        second = self.step(2)
        plan = progress.read(self.assessment / 'PLAN.json')
        start = progress.read(self.assessment / 'START.json')
        for key in ('objective', 'acceptance', 'id', 'problem_sha256'):
            changed = copy.deepcopy(plan)
            changed['research_task'][key] = 'interior only'
            with self.subTest(key=key), self.assertRaises(ValueError):
                runtime.tasks.validate_plan(changed, start)
        self.assertEqual(second['research_task']['id'], 'attempt-00000001')

    def test_auxiliary_cannot_close_task_and_must_have_bridge(self):
        value = self.step()
        for change in ({'close_reason': 'acceptance-met'}, {'bridge_evidence': []},
                       {'bridge_evidence': ['notes/nonexistent.md']}):
            changed = copy.deepcopy(value)
            changed['research_task'].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                runtime.validate_result(self.project, self.f.directory, changed)
        self.assertFalse((self.project / runtime.tasks.TASK_FILE).exists())

    def test_reported_acceptance_has_evidence_and_separate_counter(self):
        value = self.step()
        value['research_task'].update(step_outcome='target-resolved', close_reason='acceptance-met',
            remaining_obligations=[], acceptance_evidence=value['research_task']['bridge_evidence'])
        self.apply(value)
        state = progress.summary(self.project)
        self.assertIsNone(state['research_tasks']['active'])
        self.assertEqual(state['research_tasks']['totals'], dict(steps=1, acceptance_reported=1, routes_exhausted=0))
        self.assertEqual(state['latest']['status'], 'self-report')
        self.assertFalse((self.assessment / 'REVIEW.json').exists())
        self.assertNotEqual(self.step(2)['research_task']['id'], value['research_task']['id'])

    def test_route_exhaustion_requires_failure_and_tested_alternative(self):
        value = self.step()
        value['research_task'].update(close_reason='route-exhausted', step_outcome='route-elimination')
        with self.assertRaisesRegex(ValueError, 'failure_evidence'):
            runtime.validate_result(self.project, self.f.directory, value)
        value['research_task']['failure_evidence'] = value['research_task']['bridge_evidence']
        with self.assertRaisesRegex(ValueError, 'alternative_evidence'):
            runtime.validate_result(self.project, self.f.directory, value)
        value['research_task']['alternative_evidence'] = value['research_task']['bridge_evidence']
        self.apply(value)
        self.assertEqual(progress.summary(self.project)['research_tasks']['totals']['routes_exhausted'], 1)

    def test_budget_end_preserves_pending_task(self):
        value = self.step()
        value['research_task']['close_reason'] = 'budget-exhausted'
        self.apply(value)
        self.assertIsNotNone(progress.summary(self.project)['research_tasks']['active'])
        self.assertEqual(self.step(2)['research_task']['id'], value['research_task']['id'])

    def test_missing_or_upgraded_progress_rejected_before_commit(self):
        value = self.step()
        for metadata in (None, {}, {**value['progress'], 'evidence_level': 'agent-verified'},
                         {**value['progress'], 'claimed_kind': 'solved'}):
            changed = {**value, 'progress': metadata}
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                runtime.validate_result(self.project, self.f.directory, changed)
        self.assertFalse((self.f.directory / 'COMMIT.json').exists())

    def test_changed_sealed_plan_and_strategy_evidence_rejected(self):
        value = self.step(review=True)
        report = self.project / 'notes/review.md'
        report.write_text('changed after sealing')
        with self.assertRaisesRegex(ValueError, 'supporting|strategy'):
            runtime.validate_result(self.project, self.f.directory, value)
        plan = self.assessment / 'PLAN.json'
        plan.write_text(plan.read_text() + ' ')
        with self.assertRaisesRegex(ValueError, 'sealed'):
            runtime.validate_result(self.project, self.f.directory, value)

    def test_routes_persist_and_frontier_history_survives(self):
        ideas = self.project / 'ideas.md'
        ideas.write_text('# Ideas\n\n## Human route\nKeep this exact text.\n')
        pmap = self.project / 'proof-map.md'
        pmap.write_text('# Dependencies\n\n## Current status\nOld status\n\n### Frontier report (not certification)\nPrior gap and proof reference.\n')
        value = self.step()
        value['route_changes'] = [dict(id='R1', status='blocked', mechanism='interior estimate',
             scope='epsilon positive', reopening_condition='uniform endpoint estimate',
             evidence=value['research_task']['bridge_evidence'])]
        self.apply(value)
        self.assertIn('Keep this exact text.', ideas.read_text())
        self.assertIn('Prior gap and proof reference.', pmap.read_text())
        second = self.step(2)
        second['route_changes'] = [dict(value['route_changes'][0], status='active',
                                      evidence=second['research_task']['bridge_evidence'])]
        with self.assertRaisesRegex(ValueError, 'reopening_evidence'):
            runtime.validate_result(self.project, self.f.directory, second)
        second['route_changes'][0]['reopening_evidence'] = second['research_task']['bridge_evidence']
        self.apply(second)
        self.assertIn('Keep this exact text.', ideas.read_text())
        self.assertIn('Prior gap and proof reference.', pmap.read_text())
        self.assertEqual(pmap.read_text().count('## Frontier report'), 3)
        saved = runtime.tasks.read(self.project, runtime.tasks.ROUTE_FILE)['routes']['R1']
        self.assertEqual(saved['status'], 'active')
        self.assertEqual(saved['evidence_slices'][0]['sha256'], second['evidence'][0]['sha256'])

    def test_second_same_obstacle_triggers_review_without_certification(self):
        for n in range(1, 3):
            self.apply(self.step(n))
        report = progress.summary(self.project)
        self.assertEqual(report['scheduling']['action'], 'review-strategy')
        self.assertEqual(report['decision']['no_frontier_rounds'], 0)
        self.assertEqual(progress.scheduling_decision(report)['action'], 'review-strategy')
        self.apply(self.step(3, review=True))
        self.assertIsNone(progress.summary(self.project)['scheduling']['action'])

    def test_next_packet_discovers_persisted_route_with_scope_and_evidence(self):
        value = self.step()
        value['route_changes'] = [dict(id='R1', status='eliminated',
            mechanism='positive inverse shortcut', scope='positivity only; general inverse remains open',
            reopening_condition='new assumptions or a signed estimate',
            evidence=value['research_task']['bridge_evidence'])]
        self.apply(value)
        packet, meta = runtime.compile_packet(self.f.root, self.project,
            self.f.snapshot / 'problem.md', self.f.config, self.f.item, 'offline')
        self.assertEqual(meta['route_directory']['displayed_ids'], ['R1'])
        self.assertIn('general inverse remains open', packet)
        self.assertIn(value['evidence'][0]['sha256'], packet)
        self.assertIn('not certification', packet)
        self.assertEqual(meta['bytes'], len(packet.encode()))

    def test_route_preview_does_not_expose_online_or_unknown_provenance_offline(self):
        route = dict(status='blocked', mechanism='test', scope='restricted scope',
                     reopening_condition='new data', round_id='attempt-00000001')
        runtime.write_json(self.project / runtime.tasks.ROUTE_FILE, dict(routes={
            'offline-route': {**route, 'evidence_slices': [{'source': 'internal-offline'}]},
            'online-secret': {**route, 'mechanism': 'online-only detail',
                              'evidence_slices': [{'source': 'internal-offline'}, {'source': 'mixed'}]},
            'unknown-secret': route}))
        packet, meta = runtime.compile_packet(self.f.root, self.project,
            self.f.snapshot / 'problem.md', self.f.config, self.f.item, 'offline')
        self.assertNotIn('online-secret', packet)
        self.assertNotIn('online-only detail', packet)
        self.assertNotIn('unknown-secret', packet)
        self.assertEqual(meta['route_directory']['excluded_for_provenance'], 2)
        preview, _ = runtime.tasks.route_preview(self.project, 'connected', 8192)
        self.assertIn('online-secret', preview)
        self.assertNotIn('unknown-secret', preview)

    def test_route_preview_is_bounded_without_truncating_scope(self):
        routes = {f'R{i}': dict(status='eliminated', mechanism='test',
            scope='完整适用范围。' * 40, reopening_condition='new mechanism',
            round_id=f'attempt-{i:08d}', evidence_slices=[{'source': 'internal-offline'}])
            for i in range(12)}
        runtime.write_json(self.project / runtime.tasks.ROUTE_FILE, dict(routes=routes))
        preview, meta = runtime.tasks.route_preview(self.project, 'offline', 2200)
        self.assertLessEqual(len(preview.encode()), 2200)
        self.assertEqual(meta['displayed_ids'][0], 'R11')
        self.assertGreater(meta['omitted'], 0)
        for line in preview.splitlines():
            if line.startswith('{'):
                self.assertEqual(json.loads(line)['scope'], routes['R0']['scope'])

    def test_route_preview_cannot_displace_proof_at_packet_limit(self):
        value = self.step()
        self.apply(value)
        packet, before = runtime.compile_packet(self.f.root, self.project,
            self.f.snapshot / 'problem.md', self.f.config, self.f.item, 'offline')
        runtime.write_json(self.project / runtime.tasks.ROUTE_FILE, dict(routes={
            'R1': dict(status='blocked', scope='scope', mechanism='test',
                       reopening_condition='new data', round_id='attempt-00000001',
                       evidence_slices=value['evidence'])}))
        limit = len(packet.encode())
        config = {**self.f.config, 'context_budget': {
            'packet_target_bytes': limit, 'packet_hard_bytes': limit}}
        after_packet, after = runtime.compile_packet(self.f.root, self.project,
            self.f.snapshot / 'problem.md', config, self.f.item, 'offline')
        self.assertEqual(after_packet, packet)
        self.assertEqual(after['evidence'], before['evidence'])
        self.assertEqual(after['route_directory']['omitted'], 1)

    def test_trigger_enforced_by_next_plan_seal(self):
        for n in range(1, 3):
            self.apply(self.step(n))
        with self.assertRaises(ValueError):
            self.step(3)

    def test_active_task_cannot_be_silently_downgraded(self):
        self.apply(self.step())
        self.f.config['research_task_version'] = 0
        with self.assertRaisesRegex(ValueError, 'active research task'):
            self.f.prepare()

    def test_old_packet_still_closes_without_new_fields(self):
        self.f.config['research_task_version'] = 0
        self.f.prepare()
        value = self.f.result()
        self.f.save(value)
        runtime.apply_result(self.project, self.f.directory)
        self.assertFalse((self.project / runtime.tasks.TASK_FILE).exists())

    def test_idempotent_commit_does_not_double_count_steps(self):
        self.apply(self.step())
        before = (self.project / runtime.tasks.TASK_FILE).read_bytes()
        runtime.apply_result(self.project, self.f.directory)
        self.assertEqual(before, (self.project / runtime.tasks.TASK_FILE).read_bytes())

    def test_concurrent_task_edit_prevents_all_state_mutations(self):
        value = self.step()
        before = (self.project / 'CURRENT_STATE.md').read_bytes()
        runtime.write_json(self.project / runtime.tasks.TASK_FILE, {'external': 'edit'})
        self.f.save(value)
        with self.assertRaisesRegex(ValueError, 'protected file changed'):
            runtime.apply_result(self.project, self.f.directory)
        self.assertEqual(before, (self.project / 'CURRENT_STATE.md').read_bytes())
        self.assertFalse((self.f.directory / 'COMMIT.json').exists())

    def test_main_candidate_keeps_existing_certification_hold(self):
        value = self.step()
        path = value['evidence'][0]['file']
        value.update(round_status='candidate-solution', queue_status='solved-awaiting-human-verification',
            audit=dict(checks=['pass'] * 10, report_file=path),
            solution_scope=dict(kind='full-original-problem',
                problem_sha256=runtime.digest(self.f.snapshot / 'problem.md'), unresolved_parts=[],
                coverage_statement='Synthetic fixture asserts full scope, not an actual mathematical result.'),
            new_claims=[dict(id='MAIN', statement='Synthetic main candidate', assumptions='Original scope',
                dependencies='none', checks='Synthetic ten checks', status='proof-draft',
                source='internal-offline', statement_file=path)])
        with self.assertRaisesRegex(ValueError, 'certification pause'):
            runtime.validate_result(self.project, self.f.directory, value)
        value['research_task']['close_reason'] = 'certification-pause'
        self.apply(value)
        self.assertEqual(fixture.queue.read_status('sample'), 'solved-awaiting-human-verification')
        self.assertIsNotNone(progress.summary(self.project)['research_tasks']['active'])
        self.assertEqual(progress.summary(self.project)['research_tasks']['totals']['acceptance_reported'], 0)

    def test_real_queue_task_wiring_one_mock_call_one_execution(self):
        def process(command, project, event_log, timeout_seconds):
            outcome = self.f.fake_process(command, project, event_log, timeout_seconds)
            directory = next((project / '.runtime/rounds').iterdir())
            assessment = progress.round_dir(project, directory.name)
            plan = progress.read(assessment / 'PLAN.json')
            plan.update(author_id='author', family_id='bound', obstacle_id='uniformity',
                        mechanism='boundary test', gap_before='endpoint', acceptance_test='uniformity')
            plan['research_task'].update(objective='Uniform endpoint bound', acceptance='Original assumptions, all epsilon')
            runtime.write_json(assessment / 'PLAN.json', plan)
            progress.seal_plan(project, assessment)
            value = runtime.read_json(directory / 'ROUND_RESULT.json')
            value['progress'] = dict(claimed_kind='enabling-result', main_problem_effect='Interior only',
                scope_limitations='Endpoint unresolved', evidence_level='proof-draft')
            value['research_task'] = dict(id=plan['research_task']['id'], step_outcome='auxiliary',
                close_reason='continue', bridge_evidence=['notes/lemma.md'], remaining_obligations=['Endpoint'])
            runtime.write_json(directory / 'ROUND_RESULT.json', value)
            return outcome
        with mock.patch.object(fixture.queue, 'run_codex_process', side_effect=process) as model:
            self.assertEqual(fixture.queue.execute_attempt(self.f.item, self.f.config), 0)
            self.assertEqual(model.call_count, 1)
        state = fixture.queue.read_runtime_state('sample')
        self.assertEqual(state['attempts'], 1)
        self.assertEqual(state['progress_assessment']['status'], 'self-report')
        self.assertNotIn('progress_import_error', state)
        self.assertEqual(progress.summary(self.project)['research_tasks']['active']['steps'], 1)


class SchedulingSignalTest(unittest.TestCase):
    def rows(self, count=2):
        return [dict(attempt=i, status='self-report', finished=True, prospective=True,
                     claimed_kind='inconclusive', obstacle='uniformity', strategy_review='none')
                for i in range(1, count + 1)]

    def test_two_same_obstacles_trigger_without_verified_stagnation(self):
        value = progress.self_report_signal(self.rows())
        self.assertEqual(value['action'], 'review-strategy')
        self.assertFalse(value['automatic_pause'])

    def test_failure_gap_inflight_and_retrospective_break_window(self):
        for updates in ({'status': 'execution-error'}, {'attempt': 7}, {'finished': False},
                        {'prospective': False}, {'claimed_kind': 'candidate-solution'}):
            rows = self.rows()
            rows[-1].update(updates)
            with self.subTest(updates=updates):
                self.assertIsNone(progress.self_report_signal(rows)['action'])

    def test_switch_and_certification_decisions_take_priority(self):
        for action in ('certify', 'switch-route', 'review-strategy'):
            decision = dict(action=action, reason='verified')
            self.assertEqual(progress.scheduling_decision(dict(decision=decision,
                scheduling=dict(action='review-strategy', basis='self-report'))), decision)


if __name__ == '__main__':
    unittest.main()
