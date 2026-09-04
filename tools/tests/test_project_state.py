from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "project_state", SOURCE_ROOT / "tools" / "project_state.py"
)
assert SPEC is not None and SPEC.loader is not None
state = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(state)


class ProjectStateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        state.ROOT = root
        state.PROJECTS_ROOT = root / "projects"
        state.PROJECTS_ROOT.mkdir()
        state.TEMPLATE = SOURCE_ROOT / "templates" / "project_template" / "CURRENT_STATE.md"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_initialization_is_pending_and_non_destructive(self) -> None:
        project = state.PROJECTS_ROOT / "sample"
        project.mkdir()
        self.assertEqual(state.initialize(None), 0)
        path = project / "CURRENT_STATE.md"
        content = path.read_text(encoding="utf-8")
        self.assertIn("- migration-status: `pending`", content)
        self.assertEqual(state.validate(path), [])
        path.write_text(content + "preserved\n", encoding="utf-8")
        self.assertEqual(state.initialize("sample"), 0)
        self.assertTrue(path.read_text(encoding="utf-8").endswith("preserved\n"))

    def test_audit_rejects_unbounded_or_incomplete_state(self) -> None:
        project = state.PROJECTS_ROOT / "sample"
        project.mkdir()
        path = project / "CURRENT_STATE.md"
        path.write_text("# Current State\n", encoding="utf-8")
        self.assertEqual(state.audit(None), 1)
        self.assertTrue(state.validate(path))


if __name__ == "__main__":
    unittest.main()
