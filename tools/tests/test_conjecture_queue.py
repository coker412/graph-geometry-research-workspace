from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SOURCE_ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "conjecture_queue", SOURCE_ROOT / "tools" / "conjecture_queue.py"
)
assert SPEC is not None and SPEC.loader is not None
queue = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(queue)


class ConjectureQueueTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        queue.ROOT = root
        queue.QUEUE_ROOT = root / "problems" / "important-conjectures"
        queue.ITEMS_ROOT = queue.QUEUE_ROOT / "items"
        queue.RUNNER_CONFIG = queue.QUEUE_ROOT / "runner.toml"
        queue.ITEM_TEMPLATE_ROOT = SOURCE_ROOT / "templates" / "important-conjecture"
        queue.RUNTIME_ROOT = root / "agents" / "important-conjectures"
        queue.STOP_FILE = queue.RUNTIME_ROOT / "STOP"
        queue.LOCK_FILE = queue.RUNTIME_ROOT / "runner.lock"
        queue.ITEMS_ROOT.mkdir(parents=True)
        queue.RUNNER_CONFIG.write_text(
            'session_name = "test_queue"\nreasoning_effort = "xhigh"\n',
            encoding="utf-8",
        )
        (root / "projects").mkdir()
        (root / "AGENTS.md").write_text("test rules\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_add_prepare_snapshot_and_status(self) -> None:
        args = argparse.Namespace(slug="sample-problem", title="Sample Problem")
        self.assertEqual(queue.add_item(args), 0)
        item_path = queue.ITEMS_ROOT / "sample-problem"
        config_path = item_path / "config.toml"
        config_path.write_text(
            config_path.read_text(encoding="utf-8").replace(
                "ready = false", "ready = true"
            ),
            encoding="utf-8",
        )

        items = queue.discover_items()
        self.assertEqual([item["slug"] for item in items], ["sample-problem"])
        self.assertEqual(items[0]["search_contract"], "affirmative-proof")
        self.assertEqual(items[0]["stagnation_rounds_before_blocked"], 0)
        project = queue.ensure_project(items[0])
        first_snapshot = queue.create_input_snapshot(items[0], project)
        self.assertTrue((project / "progress.md").is_file())
        self.assertTrue((project / "verification-ledger.md").is_file())
        self.assertIn(
            "方法族登记表", (project / "ideas.md").read_text(encoding="utf-8")
        )
        self.assertIn(
            "信息来源/隔离",
            (project / "verification-ledger.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "搜索承诺：`affirmative-proof`",
            (project / "README.md").read_text(encoding="utf-8"),
        )
        self.assertTrue((first_snapshot / "problem.md").is_file())
        self.assertEqual(queue.read_status("sample-problem"), "queued")

        problem_path = item_path / "problem.md"
        problem_path.write_text(
            problem_path.read_text(encoding="utf-8") + "\nNew assumption.\n",
            encoding="utf-8",
        )
        second_snapshot = queue.create_input_snapshot(items[0], project)
        self.assertNotEqual(first_snapshot, second_snapshot)
        self.assertTrue(first_snapshot.is_dir())

        queue.write_status("sample-problem", "needs-human-review")
        self.assertEqual(queue.eligible_items(queue.discover_items()), [])
        self.assertEqual(queue.solution_holds(), [])
        queue.write_status("sample-problem", "solved-awaiting-human-verification")
        self.assertEqual(queue.solution_holds(), ["sample-problem"])

    def test_priority_and_prompt_boundaries(self) -> None:
        for slug, title, priority in (("lower", "Lower", 10), ("higher", "Higher", 200)):
            queue.add_item(argparse.Namespace(slug=slug, title=title))
            config_path = queue.ITEMS_ROOT / slug / "config.toml"
            content = config_path.read_text(encoding="utf-8")
            content = content.replace("ready = false", "ready = true")
            content = content.replace("priority = 100", f"priority = {priority}")
            config_path.write_text(content, encoding="utf-8")

        items = queue.discover_items()
        self.assertEqual([item["slug"] for item in items], ["higher", "lower"])
        project = queue.ensure_project(items[0])
        snapshot = queue.create_input_snapshot(items[0], project)
        prompt = queue.build_prompt(items[0], project, snapshot)
        self.assertIn("不得自动调用 Rethlas", prompt)
        self.assertIn("needs-human-review", prompt)
        self.assertIn("solved-awaiting-human-verification", prompt)
        self.assertIn("只允许修改本研究项目", prompt)
        self.assertIn("信息模式为 `connected`", prompt)
        self.assertIn("方法族登记表", prompt)
        self.assertIn("搜索承诺为 `affirmative-proof`", prompt)
        self.assertIn("不得仅因现有路线耗尽或连续停滞", prompt)

        offline_prompt = queue.build_prompt(
            items[0], project, snapshot, web_search=False
        )
        self.assertIn("信息模式为 `offline`", offline_prompt)
        self.assertIn("不要读取快照 references/", offline_prompt)
        self.assertIn("不得宣称结果新颖或问题开放", offline_prompt)

        command_config = queue.load_runner_config()
        command_config["codex_path"] = "/bin/true"
        connected_command = queue.codex_command(
            command_config, project, prompt, project / "connected-last.md"
        )
        self.assertIn("--search", connected_command)
        command_config["web_search"] = False
        offline_command = queue.codex_command(
            command_config, project, offline_prompt, project / "offline-last.md"
        )
        self.assertNotIn("--search", offline_command)

        counterexample_item = dict(items[0])
        counterexample_item["search_contract"] = "counterexample"
        counterexample_item["stagnation_rounds_before_blocked"] = 3
        counterexample_prompt = queue.build_prompt(
            counterexample_item, project, snapshot
        )
        self.assertIn("搜索承诺为 `counterexample`", counterexample_prompt)
        self.assertIn("至少 3 个没有发现新机制的再发散回合", counterexample_prompt)

        queue.write_status("higher", "needs-human-review")
        runnable = queue.eligible_items(queue.discover_items())
        self.assertEqual([item["slug"] for item in runnable], ["lower"])

    def test_explicit_project_path_adopts_existing_project(self) -> None:
        queue.add_item(argparse.Namespace(slug="existing", title="Existing"))
        existing = queue.ROOT / "projects" / "existing-research"
        existing.mkdir()
        preserved = existing / "README.md"
        preserved.write_text("existing material\n", encoding="utf-8")

        config_path = queue.ITEMS_ROOT / "existing" / "config.toml"
        content = config_path.read_text(encoding="utf-8")
        content = content.replace("ready = false", "ready = true")
        content = content.replace(
            'project_path = ""', 'project_path = "projects/existing-research"'
        )
        config_path.write_text(content, encoding="utf-8")

        item = queue.discover_items()[0]
        self.assertEqual(queue.project_dir("existing"), existing.resolve())
        project = queue.ensure_project(item)
        self.assertEqual(project, existing.resolve())
        self.assertEqual(preserved.read_text(encoding="utf-8"), "existing material\n")
        self.assertTrue((project / "verification-ledger.md").is_file())
        marker = project / ".conjecture-queue-project.json"
        self.assertIn('"adopted_existing": true', marker.read_text(encoding="utf-8"))

    def test_invalid_search_contract_is_rejected(self) -> None:
        queue.add_item(argparse.Namespace(slug="invalid-contract", title="Invalid"))
        config_path = queue.ITEMS_ROOT / "invalid-contract" / "config.toml"
        content = config_path.read_text(encoding="utf-8")
        content = content.replace(
            'search_contract = "affirmative-proof"',
            'search_contract = "wishful-thinking"',
        )
        config_path.write_text(content, encoding="utf-8")

        item = queue.discover_items()[0]
        self.assertIn("未知 search_contract", item["invalid"])
        self.assertEqual(queue.eligible_items([item]), [])

    def test_information_mode_resolution_and_item_override(self) -> None:
        self.assertEqual(
            queue.resolve_information_mode({"web_search": False}), "offline"
        )
        self.assertEqual(
            queue.resolve_information_mode({"web_search": True}), "connected"
        )
        self.assertEqual(
            queue.resolve_information_mode(
                {"information_mode": "mixed-isolated", "web_search": False}
            ),
            "mixed-isolated",
        )
        self.assertEqual(
            queue.effective_information_mode(
                {"information_mode": "offline"},
                {"information_mode": "connected"},
            ),
            "offline",
        )
        with self.assertRaisesRegex(ValueError, "未知 information_mode"):
            queue.resolve_information_mode({"information_mode": "hybrid"})

    def test_invalid_item_information_mode_is_rejected(self) -> None:
        queue.add_item(argparse.Namespace(slug="invalid-mode", title="Invalid Mode"))
        config_path = queue.ITEMS_ROOT / "invalid-mode" / "config.toml"
        content = config_path.read_text(encoding="utf-8").replace(
            'information_mode = ""', 'information_mode = "hybrid"'
        )
        config_path.write_text(content, encoding="utf-8")

        item = queue.discover_items()[0]
        self.assertIn("未知 information_mode", item["invalid"])
        self.assertEqual(queue.eligible_items([item]), [])

    def test_mixed_isolated_dry_run_shows_three_capability_lanes(self) -> None:
        queue.add_item(argparse.Namespace(slug="mixed", title="Mixed"))
        config_path = queue.ITEMS_ROOT / "mixed" / "config.toml"
        content = config_path.read_text(encoding="utf-8")
        content = content.replace("ready = false", "ready = true")
        content = content.replace(
            'information_mode = ""', 'information_mode = "mixed-isolated"'
        )
        config_path.write_text(content, encoding="utf-8")
        item = queue.discover_items()[0]
        config = queue.load_runner_config()
        config["codex_path"] = "/bin/true"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(queue.execute_attempt(item, config, dry_run=True), 0)
        rendered = output.getvalue()
        self.assertIn("并行离线分支", rendered)
        self.assertIn("并行联网分支", rendered)
        self.assertIn("汇合审计", rendered)
        self.assertIn("三次 Codex 调用", rendered)
        connected_line = next(
            line for line in rendered.splitlines() if "并行联网分支" in line
        )
        offline_line = next(
            line for line in rendered.splitlines() if "并行离线分支" in line
        )
        integration_line = next(
            line for line in rendered.splitlines() if "汇合审计：" in line
        )
        self.assertIn("--search", connected_line)
        self.assertNotIn("--search", offline_line)
        self.assertNotIn("--search", integration_line)
        self.assertFalse(queue.project_dir("mixed").exists())
        self.assertFalse(queue.RUNTIME_ROOT.exists())

    def test_connected_lane_uses_a_frozen_project_copy(self) -> None:
        queue.add_item(argparse.Namespace(slug="frozen", title="Frozen"))
        config_path = queue.ITEMS_ROOT / "frozen" / "config.toml"
        config_path.write_text(
            config_path.read_text(encoding="utf-8").replace(
                "ready = false", "ready = true"
            ),
            encoding="utf-8",
        )
        item = queue.discover_items()[0]
        project = queue.ensure_project(item)
        snapshot = queue.create_input_snapshot(item, project)
        (project / "progress.md").write_text("before checkpoint\n", encoding="utf-8")
        (project / "notes" / "absolute-path.md").write_text(
            f"see {project / 'progress.md'}\n", encoding="utf-8"
        )
        (project / "notes" / "outside-link").symlink_to(queue.ROOT / "AGENTS.md")

        with tempfile.TemporaryDirectory() as raw:
            lane_root, lane_project = queue.copy_connected_workspace(
                project, snapshot, Path(raw)
            )
            (project / "progress.md").write_text(
                "offline branch changed\n", encoding="utf-8"
            )
            self.assertEqual(
                (lane_project / "progress.md").read_text(encoding="utf-8"),
                "before checkpoint\n",
            )
            rewritten = (lane_project / "notes" / "absolute-path.md").read_text(
                encoding="utf-8"
            )
            self.assertNotIn(str(project), rewritten)
            self.assertIn(str(lane_project), rewritten)
            self.assertFalse((lane_project / "notes" / "outside-link").exists())
            lane_snapshot = lane_project / snapshot.relative_to(project)
            prompt = queue.build_connected_lane_prompt(
                item, lane_root, lane_project, lane_snapshot
            )
            self.assertIn("联网核查分支", prompt)
            self.assertIn("汇合点之前看不到你的结果", prompt)
            self.assertIn("web-source", prompt)
            wrapped = queue.bubblewrap_command(
                ["/bin/true"],
                lane_project,
                writable_dirs=[lane_project],
                hidden_dirs=[queue.ROOT],
            )
            self.assertIn("--ro-bind", wrapped)
            self.assertIn("--tmpfs", wrapped)
            self.assertEqual(wrapped[-1], "/bin/true")

    @unittest.skipUnless(queue.shutil.which("bwrap"), "bubblewrap is required")
    def test_mixed_isolated_attempt_runs_two_lanes_then_integration(self) -> None:
        queue.add_item(argparse.Namespace(slug="mixed-run", title="Mixed Run"))
        config_path = queue.ITEMS_ROOT / "mixed-run" / "config.toml"
        content = config_path.read_text(encoding="utf-8")
        content = content.replace("ready = false", "ready = true")
        content = content.replace(
            'information_mode = ""', 'information_mode = "mixed-isolated"'
        )
        config_path.write_text(content, encoding="utf-8")
        item = queue.discover_items()[0]

        with tempfile.TemporaryDirectory() as binary_dir:
            fake_codex = Path(binary_dir) / "fake-codex"
            fake_codex.write_text(
                """#!/usr/bin/env python3
from pathlib import Path
import sys

arguments = sys.argv[1:]
output = Path(arguments[arguments.index('--output-last-message') + 1])
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text('fake final message\\n', encoding='utf-8')
if '--search' in arguments:
    Path('CONNECTED_RESULT.md').write_text(
        '# Connected result\\n\\nweb-source test result\\n', encoding='utf-8'
    )
""",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            config = queue.load_runner_config()
            config["codex_path"] = str(fake_codex)
            config["attempt_timeout_minutes"] = 1
            self.assertEqual(queue.execute_attempt(item, config), 0)

        project = queue.project_dir("mixed-run")
        checkpoint = (
            project / "notes" / "mixed-isolated" / "attempt-0001"
        )
        self.assertIn(
            "web-source test result",
            (checkpoint / "connected" / "RESULT.md").read_text(encoding="utf-8"),
        )
        metadata = queue.json.loads(
            (checkpoint / "CHECKPOINT.json").read_text(encoding="utf-8")
        )
        self.assertEqual(metadata["mode"], "mixed-isolated")
        self.assertEqual(metadata["offline"]["return_code"], 0)
        self.assertEqual(metadata["connected"]["return_code"], 0)
        self.assertEqual(metadata["integration"]["return_code"], 0)
        runtime = queue.read_runtime_state("mixed-run")
        self.assertEqual(runtime["last_information_mode"], "mixed-isolated")
        self.assertEqual(
            set(runtime["last_lane_event_logs"]),
            {"offline", "connected", "integration"},
        )

    def test_failed_mixed_audit_cannot_freeze_as_solved(self) -> None:
        queue.add_item(argparse.Namespace(slug="mixed-failure", title="Mixed Failure"))
        config_path = queue.ITEMS_ROOT / "mixed-failure" / "config.toml"
        content = config_path.read_text(encoding="utf-8")
        content = content.replace("ready = false", "ready = true")
        content = content.replace(
            'information_mode = ""', 'information_mode = "mixed-isolated"'
        )
        config_path.write_text(content, encoding="utf-8")
        item = queue.discover_items()[0]
        config = queue.load_runner_config()

        def failed_mixed(*args: object, **kwargs: object) -> dict:
            logs = Path(args[4])
            event_log = logs / "failed.jsonl"
            event_log.parent.mkdir(parents=True, exist_ok=True)
            event_log.write_text("failure\n", encoding="utf-8")
            queue.write_status("mixed-failure", "solved-awaiting-human-verification")
            return {
                "return_code": 1,
                "timed_out": False,
                "event_log": event_log,
                "last_message": None,
                "lane_event_logs": {"offline": event_log},
            }

        with mock.patch.object(
            queue, "execute_mixed_isolated_attempt", side_effect=failed_mixed
        ):
            self.assertEqual(queue.execute_attempt(item, config), 1)
        self.assertEqual(queue.read_status("mixed-failure"), "needs-human-review")
        runtime = queue.read_runtime_state("mixed-failure")
        self.assertTrue(runtime["mixed_audit_incomplete"])

    def test_foreground_restart_clears_old_stop_request(self) -> None:
        queue.RUNTIME_ROOT.mkdir(parents=True)
        queue.STOP_FILE.write_text("old stop request\n", encoding="utf-8")
        args = argparse.Namespace(slug=None, once=True, dry_run=False)
        self.assertEqual(queue.run_loop(args), 0)
        self.assertFalse(queue.STOP_FILE.exists())
        self.assertFalse(queue.runner_lock_held())

    def test_dry_run_does_not_create_project_or_runtime_files(self) -> None:
        queue.add_item(argparse.Namespace(slug="dry-only", title="Dry Only"))
        config_path = queue.ITEMS_ROOT / "dry-only" / "config.toml"
        config_path.write_text(
            config_path.read_text(encoding="utf-8").replace(
                "ready = false", "ready = true"
            ),
            encoding="utf-8",
        )
        config = queue.load_runner_config()
        config["codex_path"] = "/bin/true"
        item = queue.eligible_items(queue.discover_items())[0]
        self.assertEqual(queue.execute_attempt(item, config, dry_run=True), 0)
        self.assertFalse(queue.project_dir("dry-only").exists())
        self.assertFalse(queue.RUNTIME_ROOT.exists())


if __name__ == "__main__":
    unittest.main()
