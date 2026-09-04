#!/usr/bin/env python3
"""Initialize and audit bounded CURRENT_STATE.md entries for all projects."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PROJECTS_ROOT = ROOT / "projects"
TEMPLATE = ROOT / "templates" / "project_template" / "CURRENT_STATE.md"
MAX_LINES = 300
MAX_BYTES = 32 * 1024
REQUIRED_HEADINGS = (
    "## Control",
    "## Problem and scope",
    "## Current mathematical status",
    "## Active proof frontier",
    "## Next bounded round",
    "## Evidence pointers",
)


def projects(name: str | None) -> list[Path]:
    if name:
        if Path(name).name != name or name in {".", ".."}:
            raise ValueError("project must be one directory name under projects/")
        project = PROJECTS_ROOT / name
        if not project.is_dir():
            raise ValueError(f"project not found: {name}")
        return [project]
    if not PROJECTS_ROOT.is_dir():
        return []
    return sorted(path for path in PROJECTS_ROOT.iterdir() if path.is_dir())


def pending_template(project: Path) -> str:
    content = TEMPLATE.read_text(encoding="utf-8")
    content = content.replace(
        "- updated-at: YYYY-MM-DDTHH:MM:SS+TZ",
        f"- updated-at: {datetime.now().astimezone().isoformat(timespec='seconds')}",
    )
    content = content.replace(
        "- migration-status: `complete`", "- migration-status: `pending`"
    )
    content = content.replace(
        "- queue-status: `queued`", "- queue-status: `not-managed-by-queue`"
    )
    content = content.replace(
        "- search-contract: `either`", "- search-contract: `not-configured`"
    )
    content = content.replace(
        "- evidence-ceiling: `conjecture`",
        "- evidence-ceiling: `unmigrated-see-verification-ledger`",
    )
    content = content.replace(
        "- Formal statement:", f"- Formal statement: see `{project.name}/README.md` and project sources."
    )
    content = content.replace(
        "- Strongest usable results:",
        "- Strongest usable results: see existing evidence; migration changes no evidence level.",
    )
    return content


def validate(path: Path) -> list[str]:
    if not path.is_file():
        return ["missing CURRENT_STATE.md"]
    content = path.read_text(encoding="utf-8")
    issues: list[str] = []
    if len(content.encode("utf-8")) > MAX_BYTES:
        issues.append(f"larger than {MAX_BYTES} bytes")
    if len(content.splitlines()) > MAX_LINES:
        issues.append(f"longer than {MAX_LINES} lines")
    for heading in REQUIRED_HEADINGS:
        if heading not in content:
            issues.append(f"missing heading: {heading}")
    if "- schema-version: 1" not in content:
        issues.append("missing schema-version 1")
    if not any(
        marker in content
        for marker in (
            "- migration-status: `pending`",
            "- migration-status: `complete`",
        )
    ):
        issues.append("invalid migration-status")
    return issues


def initialize(name: str | None) -> int:
    created = 0
    for project in projects(name):
        path = project / "CURRENT_STATE.md"
        if path.exists():
            print(f"EXISTS {path.relative_to(ROOT)}")
            continue
        path.write_text(pending_template(project), encoding="utf-8")
        created += 1
        print(f"CREATED {path.relative_to(ROOT)}")
    print(f"project current-state initialized: {created}")
    return 0


def audit(name: str | None) -> int:
    failed = False
    pending = 0
    checked = 0
    for project in projects(name):
        checked += 1
        path = project / "CURRENT_STATE.md"
        issues = validate(path)
        if issues:
            failed = True
            for issue in issues:
                print(f"FAIL {project.name}: {issue}")
            continue
        content = path.read_text(encoding="utf-8")
        if "- migration-status: `pending`" in content:
            pending += 1
            print(f"PENDING {project.name}")
        else:
            print(f"OK {project.name}")
    print(f"project current-state checked={checked} pending={pending} failed={failed}")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "audit"):
        child = sub.add_parser(command)
        child.add_argument("--project", help="one directory name under projects/")
    args = parser.parse_args()
    try:
        return initialize(args.project) if args.command == "init" else audit(args.project)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
