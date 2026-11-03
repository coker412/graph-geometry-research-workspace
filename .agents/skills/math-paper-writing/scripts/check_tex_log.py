#!/usr/bin/env python3
"""Summarize TeX/BibTeX/Biber diagnostics; does not run builds or certify a PDF."""

import argparse
import json
from pathlib import Path
import re
import sys


ERROR = re.compile(
    r"^!|Emergency stop|Fatal error|no output PDF file produced|"
    r"I couldn't open|I found no \\bib(?:data|style)|\bERROR\s+-|"
    r"^.+:\d+:\s*(?:.*\berror\b|Undefined control sequence|Missing |Extra |Runaway )",
    re.IGNORECASE,
)
WARNING = re.compile(
    r"(?:LaTeX(?: Font)?|Package\s+\S+|Class\s+\S+) Warning:|"
    r"^Warning--|\bWARN\s+-|undefined references|multiply[- ]defined|"
    r"(?:Citation|Reference).+undefined|(?:Overfull|Underfull) \\[hv]box|Missing character:",
    re.IGNORECASE,
)


def scan(path, limit):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not any(line.strip() for line in lines):
        raise ValueError(f"Empty log: {path}")
    result = {"path": str(path), "errors": 0, "warnings": 0,
              "error_examples": [], "warning_examples": []}
    for index, line in enumerate(lines):
        kind = "error" if ERROR.search(line) else "warning" if WARNING.search(line) else None
        if kind:
            result[kind + "s"] += 1
            examples = result[kind + "_examples"]
            if len(examples) < limit:
                examples.append({"line": index + 1, "text": "\n".join(lines[index:index + 3])})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path, help="Explicit .log/.blg files from the actual build")
    parser.add_argument("--examples", type=int, default=3, help="Max examples per severity per file; counts include all matches")
    args = parser.parse_args()
    if args.examples < 1:
        parser.error("--examples must be positive")
    reports, unreadable = [], []
    for path in args.logs:
        try:
            reports.append(scan(path, args.examples))
        except (OSError, ValueError) as error:
            unreadable.append(str(error))
    code = 2 if unreadable else int(any(r["errors"] or r["warnings"] for r in reports))
    print(json.dumps({"scope": "Log diagnostics only; build freshness and PDF not checked",
                      "files": reports, "unreadable": unreadable, "exit_code": code},
                     ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
