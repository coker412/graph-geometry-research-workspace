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

    def test_completed_round_heading_variants_are_accepted_without_rewriting(self) -> None:
        project = state.PROJECTS_ROOT / "sample"
        project.mkdir()
        state.initialize("sample")
        path = project / "CURRENT_STATE.md"
        original = path.read_text(encoding="utf-8")
        for canonical, aliases in state.HEADING_ALIASES.items():
            for alias in aliases:
                with self.subTest(alias=alias):
                    content = original.replace(canonical, alias.upper() + " ##")
                    path.write_text(content, encoding="utf-8")
                    self.assertEqual(state.validate(path), [])
                    self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_mentions_and_fenced_examples_cannot_supply_missing_sections(self) -> None:
        canonical = "\n".join(state.REQUIRED_HEADINGS)
        for content in (
            "```markdown\n" + canonical + "\n```",
            "~~~~\n" + canonical + "\n~~~~",
            "\n".join("Mention: " + h for h in state.REQUIRED_HEADINGS),
        ):
            with self.subTest(content=content):
                self.assertEqual(state.missing_headings(content), list(state.REQUIRED_HEADINGS))
        self.assertEqual(state.missing_headings(canonical), [])
        self.assertIn("## Evidence pointers", state.missing_headings(
            canonical.replace("## Evidence pointers", "## Unrelated notes")
        ))


if __name__ == "__main__":
    unittest.main()
