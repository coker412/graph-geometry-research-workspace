from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "update_manifest", SOURCE_ROOT / "tools" / "update_manifest.py"
)
assert SPEC is not None and SPEC.loader is not None
manifest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manifest)


class UpdateManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        manifest.ROOT = root
        manifest.MANIFEST = root / "MANIFEST.sha256"
        (root / "source.txt").write_text("first\n", encoding="utf-8")
        ignored = root / ".git" / "objects"
        ignored.mkdir(parents=True)
        (ignored / "private").write_text("ignored\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_write_and_check_detects_drift(self) -> None:
        self.assertEqual(manifest.write_manifest(), 0)
        self.assertEqual(manifest.check_manifest(), 0)
        (manifest.ROOT / "source.txt").write_text("second\n", encoding="utf-8")
        self.assertEqual(manifest.check_manifest(), 1)

    def test_check_rejects_unlisted_files(self) -> None:
        self.assertEqual(manifest.write_manifest(), 0)
        (manifest.ROOT / "new.txt").write_text("new\n", encoding="utf-8")
        self.assertEqual(manifest.check_manifest(), 1)


if __name__ == "__main__":
    unittest.main()
