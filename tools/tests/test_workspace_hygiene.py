from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "workspace_hygiene", SOURCE_ROOT / "tools" / "workspace_hygiene.py"
)
assert SPEC is not None and SPEC.loader is not None
hygiene = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hygiene)


class WorkspaceHygieneTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_latex_cleanup_is_dry_run_by_default(self) -> None:
        artifact = self.root / "projects" / "sample" / "paper" / "main.aux"
        artifact.parent.mkdir(parents=True)
        artifact.write_text("generated\n", encoding="utf-8")
        source = artifact.with_suffix(".tex")
        source.write_text("source\n", encoding="utf-8")
        research_log = self.root / "projects" / "sample" / "notes" / "ROUND-1.log"
        research_log.parent.mkdir(parents=True)
        research_log.write_text("research evidence\n", encoding="utf-8")

        self.assertEqual(hygiene.clean_latex(self.root, apply=False), 0)
        self.assertTrue(artifact.is_file())
        self.assertEqual(hygiene.clean_latex(self.root, apply=True), 0)
        self.assertFalse(artifact.exists())
        self.assertTrue(source.is_file())
        self.assertTrue(research_log.is_file())

    def test_log_retention_preserves_newest_and_compresses_losslessly(self) -> None:
        log_root = self.root / "agents" / "important-conjectures" / "logs" / "p"
        log_root.mkdir(parents=True)
        old = log_root / "old.jsonl"
        newest = log_root / "newest.jsonl"
        old.write_text("old event\n", encoding="utf-8")
        newest.write_text("new event\n", encoding="utf-8")
        old_time = (datetime.now(timezone.utc) - timedelta(days=60)).timestamp()
        os.utime(old, (old_time, old_time))

        selected = hygiene.log_candidates(
            self.root, older_than_days=30, keep_latest_per_slug=1
        )
        self.assertEqual(selected, [old])
        hygiene.compress_logs(
            self.root,
            older_than_days=30,
            keep_latest_per_slug=1,
            apply=False,
        )
        self.assertTrue(old.is_file())
        hygiene.compress_logs(
            self.root,
            older_than_days=30,
            keep_latest_per_slug=1,
            apply=True,
        )
        self.assertFalse(old.exists())
        compressed = old.with_name("old.jsonl.gz")
        self.assertTrue(compressed.is_file())
        with hygiene.gzip.open(compressed, "rt", encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "old event\n")
        self.assertTrue(newest.is_file())

    def test_paper_layout_rejects_new_project_root_manuscript(self) -> None:
        manuscript = self.root / "projects" / "sample" / "main.tex"
        manuscript.parent.mkdir(parents=True)
        manuscript.write_text("\\documentclass{article}\n", encoding="utf-8")

        self.assertEqual(hygiene.check_paper_layout(self.root, show_legacy=False), 1)
        self.assertEqual(hygiene.paper_layout_candidates(self.root), [manuscript])

    def test_paper_layout_accepts_paper_and_nonmanuscript_document_dirs(self) -> None:
        allowed = [
            self.root / "projects" / "sample" / "paper" / "main.tex",
            self.root / "projects" / "sample" / "paper" / "references.bib",
            self.root / "projects" / "sample" / "notes" / "audit.tex",
            self.root / "projects" / "sample" / "reports" / "report.tex",
            self.root / "projects" / "sample" / "study-zh" / "main.tex",
            self.root / "projects" / "sample" / "sources" / "source.bib",
        ]
        for path in allowed:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("test\n", encoding="utf-8")

        self.assertEqual(hygiene.paper_layout_candidates(self.root), [])
        self.assertEqual(hygiene.check_paper_layout(self.root, show_legacy=False), 0)


if __name__ == "__main__":
    unittest.main()
