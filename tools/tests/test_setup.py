from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


class SetupVerificationTest(unittest.TestCase):
    def test_initial_verification_selects_checkout_or_distribution(self):
        source = Path(__file__).resolve().parents[2] / "setup.sh"
        for git_kind in ("absent", "directory", "file"):
            with self.subTest(git_kind=git_kind), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                shutil.copy2(source, root / "setup.sh")
                (root / "AGENTS.md").write_text("__WORKSPACE_ROOT__")
                (root / "MANIFEST.sha256").touch()
                (root / "tools").mkdir()
                if git_kind == "directory":
                    (root / ".git").mkdir()
                elif git_kind == "file":
                    (root / ".git").write_text("gitdir: elsewhere")
                verifier = root / "tools/verify_teacher_framework.sh"
                verifier.write_text('#!/bin/bash\nprintf "%s" "$1" > "$(dirname "$0")/mode"\nexit 23\n')
                verifier.chmod(0o755)
                result = subprocess.run(
                    ["bash", str(root / "setup.sh"), "--check"],
                    env={**os.environ, "PYTHON_BIN": sys.executable,
                         "CONDA_ROOT": str(root / "missing-conda"),
                         "RETHLAS_ROOT": str(root.parent / "Rethlas")},
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 23, result.stderr)
                expected = "--distribution" if git_kind == "absent" else "--public-source"
                self.assertEqual((root / "tools/mode").read_text(), expected)


if __name__ == "__main__":
    unittest.main()
