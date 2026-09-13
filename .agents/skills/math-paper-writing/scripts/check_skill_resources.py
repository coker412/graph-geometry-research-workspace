#!/usr/bin/env python3
"""Check internal routing and maintenance invariants for this skill."""

from __future__ import annotations

import re
import sys
from collections import deque
from pathlib import Path


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TODO_RE = re.compile(r"^\s*\[TODO:[^\n]*\]\s*$", re.MULTILINE)
CASE_RE = re.compile(r"^## (E\d{2})\s+—", re.MULTILINE)


def markdown_links(path: Path) -> list[str]:
    return LINK_RE.findall(path.read_text(encoding="utf-8"))


def main(skill_root: Path) -> int:
    failures: list[str] = []
    entrypoint = skill_root / "SKILL.md"
    references = skill_root / "references"
    ui = skill_root / "agents" / "openai.yaml"

    if not entrypoint.is_file():
        failures.append("SKILL.md is missing")
    if not references.is_dir():
        failures.append("references/ is missing")
    if failures:
        print("\n".join(failures))
        return 1

    markdown_files = [entrypoint, *sorted(references.glob("*.md"))]
    graph: dict[Path, set[Path]] = {path.resolve(): set() for path in markdown_files}

    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        if TODO_RE.search(text):
            failures.append(f"unfinished TODO marker: {path}")
        for target in markdown_links(path):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean_target = target.split("#", 1)[0]
            resolved = (path.parent / clean_target).resolve()
            if not resolved.exists():
                failures.append(f"broken local link: {path} -> {target}")
                continue
            if resolved.suffix == ".md":
                graph[path.resolve()].add(resolved)

    reachable: set[Path] = set()
    queue: deque[Path] = deque([entrypoint.resolve()])
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(graph.get(current, set()) - reachable)

    for reference in sorted(references.glob("*.md")):
        if reference.resolve() not in reachable:
            failures.append(f"unrouted reference: {reference}")

    evaluation = references / "evaluation-suite.md"
    if evaluation.is_file():
        evaluation_text = evaluation.read_text(encoding="utf-8")
        cases = CASE_RE.findall(evaluation_text)
        expected = [f"E{number:02d}" for number in range(1, 13)]
        if cases != expected:
            failures.append(f"evaluation cases are incomplete or unordered: {cases}")
        for case in expected:
            section_match = re.search(
                rf"^## {case}\s+—.*?(?=^## E\d{{2}}\s+—|^## Release gate|\Z)",
                evaluation_text,
                re.MULTILINE | re.DOTALL,
            )
            section = section_match.group(0) if section_match else ""
            if "**Required behavior:**" not in section:
                failures.append(f"{case} lacks required behavior")
            if not any(
                marker in section for marker in ("**Hard failure:**", "**Soft failure:**")
            ):
                failures.append(f"{case} lacks a failure criterion")

    if not ui.is_file():
        failures.append("agents/openai.yaml is missing")
    else:
        ui_text = ui.read_text(encoding="utf-8")
        for field in ("display_name:", "short_description:", "default_prompt:"):
            if field not in ui_text:
                failures.append(f"UI metadata lacks {field}")
        if "$math-paper-writing" not in ui_text:
            failures.append("default_prompt does not mention $math-paper-writing")

    if failures:
        print("Skill resource checks failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        f"Skill resource checks passed: {len(markdown_files)} Markdown files, "
        "all references routed, 12 evaluation cases complete."
    )
    return 0


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    raise SystemExit(main(root.resolve()))
