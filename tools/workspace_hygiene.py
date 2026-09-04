#!/usr/bin/env python3
"""Report and safely compact generated workspace artifacts."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import gzip
from pathlib import Path
import shutil
import sys
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
LATEX_SUFFIXES = {
    ".aux",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".synctex.gz",
    ".toc",
    ".xdv",
}
AMBIGUOUS_LATEX_SUFFIXES = {".log", ".out"}


class Usage(NamedTuple):
    files: int
    bytes: int


def file_usage(paths: list[Path]) -> Usage:
    existing = [path for path in paths if path.is_file() and not path.is_symlink()]
    return Usage(len(existing), sum(path.stat().st_size for path in existing))


def latex_artifacts(root: Path) -> list[Path]:
    projects = root / "projects"
    if not projects.is_dir():
        return []
    found: list[Path] = []
    for path in projects.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        matched = next(
            (suffix for suffix in LATEX_SUFFIXES if path.name.endswith(suffix)), None
        )
        if matched is None:
            continue
        if matched in AMBIGUOUS_LATEX_SUFFIXES:
            stem = path.name[: -len(matched)]
            companions = (".tex", ".aux", ".fls", ".fdb_latexmk", ".xdv")
            if not any((path.parent / f"{stem}{suffix}").is_file() for suffix in companions):
                continue
        found.append(path)
    return found


def queue_logs(root: Path) -> list[Path]:
    log_root = root / "agents" / "important-conjectures" / "logs"
    if not log_root.is_dir():
        return []
    return [
        path
        for path in log_root.rglob("*.jsonl")
        if path.is_file() and not path.is_symlink()
    ]


def directory_bytes(path: Path) -> int:
    return sum(
        child.stat().st_size
        for child in path.rglob("*")
        if child.is_file() and not child.is_symlink()
    )


def environment_directories(root: Path) -> list[tuple[Path, int]]:
    candidates: list[Path] = []
    global_env = root / "environments"
    if global_env.is_dir():
        candidates.append(global_env)
    projects = root / "projects"
    if projects.is_dir():
        for project in projects.iterdir():
            if not project.is_dir():
                continue
            for relative in ("environments", ".venv", "venv"):
                path = project / relative
                if path.is_dir() and not path.is_symlink():
                    candidates.append(path)
            candidates.extend(
                path
                for path in project.rglob("pydeps")
                if path.is_dir() and not path.is_symlink()
            )
    return sorted(
        ((path, directory_bytes(path)) for path in candidates),
        key=lambda item: item[1],
        reverse=True,
    )


def human_bytes(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def report(root: Path) -> int:
    latex = file_usage(latex_artifacts(root))
    logs = file_usage(queue_logs(root))
    print(f"workspace: {root}")
    print(f"latex-artifacts: files={latex.files} size={human_bytes(latex.bytes)}")
    print(f"queue-jsonl-logs: files={logs.files} size={human_bytes(logs.bytes)}")
    environments = environment_directories(root)
    print(f"environment-directories: {len(environments)}")
    for path, size in environments[:10]:
        print(f"  {human_bytes(size):>10}  {path.relative_to(root)}")
    print("No files changed. Cleanup commands are dry-run unless --apply is supplied.")
    return 0


def clean_latex(root: Path, *, apply: bool) -> int:
    candidates = latex_artifacts(root)
    usage = file_usage(candidates)
    action = "REMOVE" if apply else "WOULD-REMOVE"
    for path in candidates:
        print(f"{action} {path.relative_to(root)}")
        if apply:
            path.unlink()
    print(f"latex-artifacts: files={usage.files} size={human_bytes(usage.bytes)}")
    if not apply:
        print("Dry run only; rerun with --apply to remove these regenerable files.")
    return 0


def log_candidates(
    root: Path, *, older_than_days: int, keep_latest_per_slug: int
) -> list[Path]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    selected: list[Path] = []
    by_parent: dict[Path, list[Path]] = {}
    for path in queue_logs(root):
        by_parent.setdefault(path.parent, []).append(path)
    for paths in by_parent.values():
        newest_first = sorted(paths, key=lambda path: path.stat().st_mtime, reverse=True)
        for path in newest_first[keep_latest_per_slug:]:
            modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            if modified < cutoff:
                selected.append(path)
    return sorted(selected)


def compress_logs(
    root: Path, *, older_than_days: int, keep_latest_per_slug: int, apply: bool
) -> int:
    candidates = log_candidates(
        root,
        older_than_days=older_than_days,
        keep_latest_per_slug=keep_latest_per_slug,
    )
    usage = file_usage(candidates)
    action = "COMPRESS" if apply else "WOULD-COMPRESS"
    for path in candidates:
        target = path.with_name(path.name + ".gz")
        if target.exists():
            print(f"SKIP existing target {target.relative_to(root)}")
            continue
        print(f"{action} {path.relative_to(root)}")
        if apply:
            with path.open("rb") as source, gzip.open(target, "wb", compresslevel=9) as out:
                shutil.copyfileobj(source, out)
            path.unlink()
    print(f"queue-jsonl-logs: files={usage.files} original-size={human_bytes(usage.bytes)}")
    if not apply:
        print("Dry run only; rerun with --apply to gzip these logs losslessly.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report or compact generated graph-geometry workspace artifacts"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("report", help="report generated artifacts and environment sizes")
    latex = sub.add_parser("latex", help="list or remove regenerable LaTeX artifacts")
    latex.add_argument("--apply", action="store_true", help="perform the removal")
    logs = sub.add_parser("logs", help="list or gzip older queue JSONL logs")
    logs.add_argument("--older-than-days", type=int, default=30)
    logs.add_argument("--keep-latest-per-slug", type=int, default=5)
    logs.add_argument("--apply", action="store_true", help="perform lossless compression")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "report":
        return report(ROOT)
    if args.command == "latex":
        return clean_latex(ROOT, apply=args.apply)
    if args.older_than_days < 0 or args.keep_latest_per_slug < 0:
        raise SystemExit("age and retention values must be nonnegative")
    return compress_logs(
        ROOT,
        older_than_days=args.older_than_days,
        keep_latest_per_slug=args.keep_latest_per_slug,
        apply=args.apply,
    )


if __name__ == "__main__":
    raise SystemExit(main())
