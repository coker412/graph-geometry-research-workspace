from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "research_progress", Path(__file__).resolve().parents[1] / "research_progress.py"
)
progress = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(progress)


class ResearchProgressTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        (self.project / "CURRENT_STATE.md").write_text("# Existing gap\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def put(self, path, data):
        path.write_text(json.dumps(data), encoding="utf-8")

    def packet(self, attempt=1, kind="frontier-advance", *, retrospective=False, reviewed=True):
        d = progress.prepare(self.project, f"attempt-{attempt:08d}", attempt,
                             retrospective=retrospective)
        plan = progress.read(d / "PLAN.json")
        plan.update(author_id="author", family_id="F1", obstacle_id="G1",
                    mechanism="explicit crossing integral", gap_before="need uniform estimate",
                    acceptance_test="prove uniformity including endpoints")
        self.put(d / "PLAN.json", plan)
        progress.seal_plan(self.project, d)
        proof = self.project / f"proof-{attempt}.md"
        proof.write_text(f"Detailed evidence for round {attempt}", encoding="utf-8")
        result = progress.read(d / "RESULT.json")
        result.update(claimed_kind=kind, claim=f"round {attempt} statement", gap_after="boundary remains",
                      discharged_obligations=["interior uniformity"], new_obligations=[],
                      main_problem_effect="interior is controlled", scope_limitations="interior only",
                      evidence_level="agent-verified", evidence=[proof.name], next_test="test boundary")
        self.put(d / "RESULT.json", result)
        progress.seal_result(self.project, d)
        if reviewed:
            self.review(d, kind)
        progress.finish(self.project, d, 0, False)
        return d

    def review(self, d, kind, **overrides):
        report = d / "REVIEW.md"
        report.write_text("Evidence comparison and exact scope of progress.", encoding="utf-8")
        review = progress.read(d / "REVIEW.template.json")
        review.update(reviewer_id="reviewer", verdict="accept", assessed_kind=kind,
                      baseline_comparison="the baseline lacks the new interior estimate",
                      critical_path_effect="one interior obligation removed; boundary remains",
                      scope_and_quantifiers="same family and all interior parameters",
                      new_burden_check="no extra assumption within stated scope",
                      same_obstacle_as_previous=kind in {"repeat", "reformulation", "inconclusive"},
                      report=str(report.relative_to(self.project)), report_sha256=progress.digest(report))
        review.update(overrides)
        self.put(d / "REVIEW.json", review)

    def test_valid_progress_is_reviewed_but_not_formal_verification(self):
        d = self.packet()
        row = progress.assess(self.project, d)
        self.assertEqual(row["status"], "reviewed")
        self.assertEqual(row["evidence_level"], "agent-verified")
        self.assertEqual(progress.summary(self.project)["decision"]["action"], "continue")

    def test_self_report_never_counts_as_verified_progress(self):
        self.packet(reviewed=False)
        report = progress.summary(self.project)
        self.assertEqual(report["latest"]["status"], "self-report")
        self.assertEqual(report["decision"]["no_frontier_rounds"], 0)
        self.assertEqual(report["decision"]["action"], "assess")

    def test_same_author_is_not_an_independent_reviewer(self):
        d = self.packet()
        self.review(d, "frontier-advance", reviewer_id="author")
        self.assertEqual(progress.assess(self.project, d)["status"], "unknown")

    def test_evidence_and_baseline_and_plan_and_review_tampering_are_detected(self):
        for filename in ("proof-1.md", "BEFORE.md", "PLAN.json", "RESULT.json", "REVIEW.md"):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temp:
                original = self.project
                self.project = Path(temp)
                (self.project / "CURRENT_STATE.md").write_text("before")
                d = self.packet()
                target = self.project / filename if filename.startswith("proof") else d / filename
                target.write_text(target.read_text() + "changed")
                self.assertEqual(progress.assess(self.project, d)["status"], "unknown")
                self.project = original

    def test_two_repeated_obstacles_require_route_change_not_project_stop(self):
        self.packet(1, "repeat")
        self.packet(2, "reformulation")
        report = progress.summary(self.project, search_contract="affirmative-proof", stagnation_limit=0)
        self.assertEqual(report["decision"]["action"], "switch-route")
        self.assertEqual(report["decision"]["repeat_rounds"], 2)
        self.assertFalse(report["decision"]["automatic_pause"])
        self.assertIn("不自动", report["decision"]["constraint"])

    def test_three_enabling_results_trigger_strategy_review(self):
        for n in range(1, 4):
            self.packet(n, "enabling-result")
        decision = progress.summary(self.project)["decision"]
        self.assertEqual(decision["action"], "review-strategy")
        self.assertEqual(decision["no_frontier_rounds"], 3)

    def test_missing_round_breaks_stagnation_streak(self):
        self.packet(1, "repeat")
        self.packet(3, "repeat")
        self.assertEqual(progress.summary(self.project)["decision"]["repeat_rounds"], 1)

    def test_unknown_finished_round_is_not_a_mathematical_failure(self):
        self.packet(1, "repeat")
        d = progress.prepare(self.project, "attempt-00000002", 2)
        progress.finish(self.project, d, 0, False)
        report = progress.summary(self.project)
        self.assertEqual(report["latest"]["status"], "unknown")
        self.assertEqual(report["decision"]["action"], "assess")
        self.assertEqual(report["decision"]["repeat_rounds"], 0)

    def test_inflight_does_not_hide_previous_review(self):
        self.packet()
        progress.prepare(self.project, "attempt-00000002", 2)
        report = progress.summary(self.project)
        self.assertEqual(report["latest"]["attempt"], 1)
        self.assertEqual(report["decision"]["action"], "continue")
        self.assertEqual(len(report["in_flight"]), 1)

    def test_retrospective_assessment_cannot_seed_automatic_stagnation(self):
        self.packet(1, "repeat", retrospective=True)
        self.packet(2, "repeat")
        self.assertEqual(progress.summary(self.project)["decision"]["repeat_rounds"], 1)

    def test_route_elimination_is_valuable_but_not_frontier_progress(self):
        d = self.packet(kind="route-elimination")
        decision = progress.summary(self.project)["decision"]
        self.assertEqual(decision["action"], "bounded-test")
        self.review(d, "route-elimination", whole_family_eliminated=True)
        decision = progress.summary(self.project)["decision"]
        self.assertEqual(decision["action"], "switch-route")
        self.assertEqual(decision["no_frontier_rounds"], 1)

    def test_experiment_cannot_be_accepted_as_certified_frontier_advance(self):
        d = self.packet(reviewed=False)
        result = progress.read(d / "RESULT.json")
        result["evidence_level"] = "experimental"
        self.put(d / "RESULT.json", result)
        bundle = progress.sealed_bundle(self.project, d)
        self.put(d / "RESULT.lock.json", bundle)
        self.review(d, "frontier-advance", bundle=bundle)
        self.assertEqual(progress.assess(self.project, d)["status"], "unknown")

    def test_runtime_failure_does_not_become_repeated_research_failure(self):
        d = self.packet(kind="repeat")
        self.put(d / "FINISH.json", {"return_code": 1, "timed_out": True})
        report = progress.summary(self.project)
        self.assertEqual(report["latest"]["status"], "execution-error")
        self.assertEqual(report["decision"]["repeat_rounds"], 0)

    def test_unrelated_evidence_paths_and_symlink_escape_are_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other) / "proof.md"
            outside.write_text("outside")
            (self.project / "escape").symlink_to(outside)
            for name in (str(outside), "escape", "../proof.md"):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    progress.local_file(self.project, name)

    def test_prepare_and_seal_never_overwrite_existing_packets(self):
        d = self.packet()
        before = (d / "START.json").read_bytes()
        with self.assertRaises(FileExistsError):
            progress.prepare(self.project, d.name, 1)
        with self.assertRaises(FileExistsError):
            progress.seal_plan(self.project, d)
        self.assertEqual((d / "START.json").read_bytes(), before)

    def test_route_change_is_checked_before_sealing_next_plan(self):
        self.packet(1, "repeat")
        self.packet(2, "repeat")
        d = progress.prepare(self.project, "attempt-00000003", 3)
        plan = progress.read(self.project / progress.DIRECTORY / "attempt-00000002/PLAN.json")
        self.put(d / "PLAN.json", plan)
        with self.assertRaisesRegex(ValueError, "route change required"):
            progress.seal_plan(self.project, d)
        plan["family_id"] = "F2"
        self.put(d / "PLAN.json", plan)
        progress.seal_plan(self.project, d)

    def test_strategy_review_required_after_three_auxiliary_rounds(self):
        for n in range(1, 4):
            self.packet(n, "enabling-result")
        d = progress.prepare(self.project, "attempt-00000004", 4)
        plan = progress.read(self.project / progress.DIRECTORY / "attempt-00000003/PLAN.json")
        self.put(d / "PLAN.json", plan)
        with self.assertRaises(ValueError):
            progress.seal_plan(self.project, d)
        (self.project / "strategy.md").write_text("Compare F1 with concrete F2 and F3 tests.")
        plan["strategy_review"] = "strategy.md"
        self.put(d / "PLAN.json", plan)
        progress.seal_plan(self.project, d)

    def test_identical_result_and_evidence_cannot_be_counted_twice(self):
        first = self.packet()
        second = self.packet(2, reviewed=False)
        result = progress.read(first / "RESULT.json")
        self.put(second / "RESULT.json", result)
        bundle = progress.sealed_bundle(self.project, second)
        self.put(second / "RESULT.lock.json", bundle)
        self.review(second, "frontier-advance", bundle=bundle)
        report = progress.summary(self.project)
        self.assertEqual(report["latest"]["status"], "disputed")
        self.assertEqual(report["decision"]["action"], "assess")

    def test_prospective_round_cannot_choose_an_old_baseline(self):
        with self.assertRaises(ValueError):
            progress.prepare(self.project, "attempt-1", 1,
                             baseline=self.project / "CURRENT_STATE.md")


if __name__ == "__main__":
    unittest.main()
