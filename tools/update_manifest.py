#!/usr/bin/env python3
"""Write or verify the public source manifest using only the standard library."""

from __future__ import annotations

import argparse
from hashlib import sha256
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.sha256"
IGNORED_DIRS = {".git", "__pycache__", ".pytest_cache", "exports"}
IGNORED_FILES = {"MANIFEST.sha256", "SETUP_REPORT.md"}


def source_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        if not path.is_file() or path.name in IGNORED_FILES or path.suffix == ".pyc":
            continue
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def current_entries() -> dict[str, str]:
    return {
        path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in source_files()
    }


def parse_manifest() -> tuple[dict[str, str], list[str]]:
    entries: dict[str, str] = {}
    errors: list[str] = []
    if not MANIFEST.is_file():
        return entries, ["missing MANIFEST.sha256"]
    for number, raw in enumerate(MANIFEST.read_text(encoding="utf-8").splitlines(), 1):
        try:
            digest, name = raw.split(maxsplit=1)
        except ValueError:
            errors.append(f"line {number}: malformed entry")
            continue
        relative = name.lstrip("* ")
        if relative.startswith("./"):
            relative = relative[2:]
        if not relative or relative.startswith("../") or Path(relative).is_absolute():
            errors.append(f"line {number}: unsafe path {relative!r}")
            continue
        if relative in entries:
            errors.append(f"line {number}: duplicate path {relative}")
            continue
        entries[relative] = digest
    return entries, errors


def write_manifest() -> int:
    entries = current_entries()
    content = "".join(f"{digest}  {name}\n" for name, digest in entries.items())
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".MANIFEST.", suffix=".tmp", dir=ROOT
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, MANIFEST)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"manifest written: {len(entries)} entries")
    return 0


def check_manifest() -> int:
    recorded, errors = parse_manifest()
    actual = current_entries()
    for name in sorted(actual.keys() - recorded.keys()):
        errors.append(f"unlisted file: {name}")
    for name in sorted(recorded.keys() - actual.keys()):
        errors.append(f"missing file: {name}")
    for name in sorted(actual.keys() & recorded.keys()):
        if actual[name] != recorded[name]:
            errors.append(f"checksum mismatch: {name}")
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print(f"manifest OK: {len(actual)} entries")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("write", "check"))
    args = parser.parse_args()
    return write_manifest() if args.command == "write" else check_manifest()


if __name__ == "__main__":
    raise SystemExit(main())
