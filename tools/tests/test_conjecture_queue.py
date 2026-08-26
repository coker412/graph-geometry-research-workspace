from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import tempfile
import unittest


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
        project = queue.ensure_project(items[0])
        first_snapshot = queue.create_input_snapshot(items[0], project)
        self.assertTrue((project / "progress.md").is_file())
        self.assertTrue((project / "verification-ledger.md").is_file())
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
