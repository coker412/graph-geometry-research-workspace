#!/usr/bin/env python3
"""Cache unfiltered PDF text; print an index, literal-search hits, or complete pages."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile


FORMAT = "math-paper-pages-v1"


def load_pages(pdf, cache):
    if cache and cache.resolve() == pdf.resolve():
        raise ValueError("Cache must not overwrite the PDF")
    with pdf.open("rb") as stream:
        hasher = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
        digest = hasher.hexdigest()
    if cache and cache.exists():
        saved = json.loads(cache.read_text(encoding="utf-8"))
        if (not isinstance(saved, dict) or saved.get("format") != FORMAT
                or not isinstance(saved.get("pages"), list)
                or not saved["pages"]
                or not all(isinstance(p, str) for p in saved["pages"])):
            raise ValueError("Unrecognized cache; choose a different cache path")
        if saved.get("source_sha256") == digest:
            return saved, True
    try:
        import fitz
    except ImportError as error:
        raise ValueError("Fresh PDF extraction requires PyMuPDF in this Python environment") from error
    with fitz.open(pdf) as document:
        if document.needs_pass:
            raise ValueError("PDF requires a password")
        pages = [page.get_text(sort=True) for page in document]
    if not pages:
        raise ValueError("PDF contains no pages")
    saved = {"format": FORMAT, "source_sha256": digest,
             "extractor": "PyMuPDF " + fitz.VersionBind, "pages": pages}
    if cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        name = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                             dir=cache.parent, delete=False) as stream:
                name = stream.name
                json.dump(saved, stream, ensure_ascii=False)
                stream.write("\n")
            os.replace(name, cache)
        finally:
            if name and os.path.exists(name):
                os.unlink(name)
    return saved, False


def select_pages(spec, total):
    if spec == "all":
        return list(range(1, total + 1))
    selected = set()
    for part in spec.split(","):
        match = re.fullmatch(r"(\d+)(?:-(\d+))?", part.strip())
        if not match:
            raise ValueError("Pages must be 'all' or PDF page numbers such as 2,5-7")
        first, last = int(match[1]), int(match[2] or match[1])
        if not 1 <= first <= last <= total:
            raise ValueError(f"Page range must lie in 1..{total}: {part}")
        selected.update(range(first, last + 1))
    return sorted(selected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--cache", type=Path, help="Reusable derived JSON cache; refreshed if PDF bytes change")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--pages", help="1-based PDF pages, e.g. 2,5-7 or all; no text truncation")
    mode.add_argument("--find", help="Case-insensitive literal text; returns matching page numbers")
    args = parser.parse_args()
    try:
        saved, cached = load_pages(args.pdf, args.cache)
        pages = saved["pages"]
        report = {"source_sha256": saved["source_sha256"], "cache_hit": cached,
                  "pages": len(pages), "characters": sum(map(len, pages)),
                  "empty_text_pages": [n for n, p in enumerate(pages, 1) if not p.strip()]}
        if args.find is not None:
            needle = " ".join(args.find.casefold().split())
            if not needle:
                raise ValueError("Search text must not be empty")
            report["matching_pages"] = [n for n, p in enumerate(pages, 1)
                                        if needle in " ".join(p.casefold().split())]
        selected = select_pages(args.pages, len(pages)) if args.pages else []
        print(json.dumps(report, ensure_ascii=False))
        for n in selected:
            print(f"\n=== PDF PAGE {n} ===\n{pages[n - 1]}")
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"pdf_pages: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
