"""Portable checks for the identical helpers shipped with each standalone skill."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


sys.dont_write_bytecode = True  # Keep distributable skill folders free of test caches.


for parent in Path(__file__).resolve().parents:
    ROOT = parent if (parent / "math-paper-writing").is_dir() else parent / ".agents/skills"
    if (ROOT / "math-paper-writing").is_dir():
        break
SCRIPTS = ROOT / "math-paper-writing/scripts"


def module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


pdf = module("pdf_pages")
logs = module("check_tex_log")


class Helpers(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_tool(self, script, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                              capture_output=True, text=True)

    def make_pdf(self, name="paper with spaces.pdf", text="Alpha\nBeta"):
        try:
            import fitz
        except ImportError:
            self.skipTest("PyMuPDF required for PDF integration tests")
        path = self.root / name
        with fitz.open() as document:
            document.new_page().insert_text((50, 50), text)
            document.new_page()
            document.new_page().insert_text((50, 50), "Gamma")
            document.save(path)
        return path

    def test_standalone_copies_identical(self):
        for name in ["pdf_pages.py", "check_tex_log.py"]:
            self.assertEqual((SCRIPTS / name).read_bytes(),
                             (ROOT / "math-paper-study-guide/scripts" / name).read_bytes())

    def test_page_selection(self):
        self.assertEqual(pdf.select_pages("3,1-2,2", 3), [1, 2, 3])
        self.assertEqual(pdf.select_pages("all", 3), [1, 2, 3])
        for bad in ["0", "2-1", "4", "1,", "", "1-999999999"]:
            with self.assertRaises(ValueError):
                pdf.select_pages(bad, 3)

    def test_exact_text_search_and_blank_pages(self):
        source = self.make_pdf()
        import fitz
        cache = self.root / "cache/pages.json"
        data, hit = pdf.load_pages(source, cache)
        self.assertFalse(hit)
        with fitz.open(source) as document:
            self.assertEqual(data["pages"], [p.get_text(sort=True) for p in document])
        output = self.run_tool("pdf_pages.py", source, "--cache", cache, "--find", "alpha beta")
        self.assertEqual(output.returncode, 0, output.stderr)
        report = json.loads(output.stdout)
        self.assertEqual(report["matching_pages"], [1])
        self.assertEqual(report["empty_text_pages"], [2])
        output = self.run_tool("pdf_pages.py", source, "--cache", cache, "--pages", "3")
        self.assertEqual(output.returncode, 0, output.stderr)
        self.assertEqual(output.stdout.split("=== PDF PAGE 3 ===\n")[1], data["pages"][2] + "\n")
        self.assertEqual(self.run_tool("pdf_pages.py", source, "--cache", cache, "--pages", "9").returncode, 2)

    def test_cache_reuse_invalidation_and_safe_destination(self):
        source = self.make_pdf()
        cache = self.root / "cache.json"
        first, _ = pdf.load_pages(source, cache)
        with patch.dict(sys.modules, {"fitz": None}):
            self.assertEqual(pdf.load_pages(source, cache), (first, True))
        source.write_bytes(self.make_pdf("replacement.pdf", "Changed").read_bytes())
        second, hit = pdf.load_pages(source, cache)
        self.assertFalse(hit)
        self.assertNotEqual(first["source_sha256"], second["source_sha256"])
        self.assertIn("Changed", second["pages"][0])
        before = source.read_bytes()
        with self.assertRaises(ValueError):
            pdf.load_pages(source, source)
        self.assertEqual(source.read_bytes(), before)
        cache.write_text('{"user_data": true}', encoding="utf-8")
        before = cache.read_bytes()
        with self.assertRaises(ValueError):
            pdf.load_pages(source, cache)
        self.assertEqual(cache.read_bytes(), before)

    def test_diagnostics_are_counted_even_when_examples_limited(self):
        path = self.root / "main.log"
        path.write_text(r"""LaTeX Warning: Reference `eq:missing' on page 1 undefined on input line 8.
Package hyperref Warning: Token not allowed in a PDF string:
(hyperref)                removing `math shift' on input line 10.
Overfull \hbox (2.0pt too wide) in paragraph at lines 12--13
Underfull \vbox (badness 10000) has occurred while output is active
LaTeX Warning: Label `same' multiply defined.
Missing character: There is no 中 in font nullfont!
! Undefined control sequence.
./main.tex:22: Undefined control sequence.
""", encoding="utf-8")
        result = logs.scan(path, 1)
        self.assertEqual((result["warnings"], result["errors"]), (6, 2))
        self.assertEqual(len(result["warning_examples"]), 1)
        self.assertEqual(len(result["error_examples"]), 1)
        self.assertEqual(self.run_tool("check_tex_log.py", path).returncode, 1)
        path.write_text("Warning--I didn't find a database entry for missing\n[12] Biber.pm:55> WARN - Missing entry\n[13] Utils.pm:20> ERROR - Cannot find file\n")
        result = logs.scan(path, 3)
        self.assertEqual((result["warnings"], result["errors"]), (2, 1))

    def test_clean_missing_and_empty_logs(self):
        path = self.root / "main.log"
        path.write_text("Output written on main.pdf (1 page).\n")
        self.assertEqual(self.run_tool("check_tex_log.py", path).returncode, 0)
        self.assertEqual(self.run_tool("check_tex_log.py", path, self.root / "missing.blg").returncode, 2)
        path.write_text("")
        self.assertEqual(self.run_tool("check_tex_log.py", path).returncode, 2)


if __name__ == "__main__":
    unittest.main()
