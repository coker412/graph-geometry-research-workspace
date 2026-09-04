#!/usr/bin/env python3
"""Long-running, file-backed scheduler for important conjectures."""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import tomllib


ROOT = Path(__file__).resolve().parents[1]
QUEUE_ROOT = ROOT / "problems" / "important-conjectures"
ITEMS_ROOT = QUEUE_ROOT / "items"
RUNNER_CONFIG = QUEUE_ROOT / "runner.toml"
ITEM_TEMPLATE_ROOT = ROOT / "templates" / "important-conjecture"
RUNTIME_ROOT = ROOT / "agents" / "important-conjectures"
LANE_RUNTIME_ROOT = Path.home() / ".cache" / "graph-geometry-codex-lanes"
STOP_FILE = RUNTIME_ROOT / "STOP"
LOCK_FILE = RUNTIME_ROOT / "runner.lock"
CURRENT_STATE_NAME = "CURRENT_STATE.md"
CURRENT_STATE_MAX_LINES = 300
CURRENT_STATE_MAX_BYTES = 32 * 1024
CURRENT_STATE_REQUIRED_HEADINGS = (
    "## Control",
    "## Problem and scope",
    "## Current mathematical status",
    "## Active proof frontier",
    "## Next bounded round",
    "## Evidence pointers",
)

RUNNABLE_STATUSES = {"queued", "pushing"}
KNOWN_STATUSES = RUNNABLE_STATUSES | {
    "paused",
    "needs-human-review",
    "solved-awaiting-human-verification",
    "needs-human-input",
    "needs-escalation-approval",
    "blocked",
    "attempt-limit",
    "runtime-error",
    "completed",
}
HUMAN_SETTABLE_STATUSES = {
    "queued",
    "pushing",
    "paused",
    "blocked",
    "completed",
}
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SEARCH_CONTRACTS = {"affirmative-proof", "counterexample", "either"}
INFORMATION_MODES = {"offline", "connected", "mixed-isolated"}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_runner_config() -> dict:
    if not RUNNER_CONFIG.is_file():
        raise RuntimeError(f"找不到调度配置：{RUNNER_CONFIG}")
    config = load_toml(RUNNER_CONFIG)
    defaults = {
        "session_name": "important_conjectures",
        "model": "",
        "reasoning_effort": "xhigh",
        "attempt_timeout_minutes": 90,
        "max_wall_hours": 24,
        "idle_seconds": 60,
        "max_idle_cycles": 0,
        "information_mode": "",
        "web_search": True,
        "max_consecutive_runtime_failures": 3,
    }
    defaults.update(config)
    resolve_information_mode(defaults)
    return defaults


def resolve_information_mode(config: dict) -> str:
    """Resolve the explicit mode, falling back to the legacy web_search flag."""
    explicit = str(config.get("information_mode", "")).strip()
    if explicit:
        if explicit not in INFORMATION_MODES:
            allowed = ", ".join(sorted(INFORMATION_MODES))
            raise ValueError(f"未知 information_mode：{explicit}；可选值：{allowed}")
        return explicit
    return "connected" if bool(config.get("web_search", True)) else "offline"


def effective_information_mode(item: dict, config: dict) -> str:
    item_mode = str(item.get("information_mode", "")).strip()
    if item_mode:
        if item_mode not in INFORMATION_MODES:
            allowed = ", ".join(sorted(INFORMATION_MODES))
            raise ValueError(f"未知 information_mode：{item_mode}；可选值：{allowed}")
        return item_mode
    return resolve_information_mode(config)


def item_dir(slug: str) -> Path:
    return ITEMS_ROOT / slug


def project_dir(slug: str) -> Path:
    config_path = item_dir(slug) / "config.toml"
    if config_path.is_file():
        configured = str(load_toml(config_path).get("project_path", "")).strip()
        if configured:
            relative = Path(configured)
            if relative.is_absolute():
                raise ValueError("project_path 必须是工作区内的相对路径。")
            candidate = (ROOT / relative).resolve()
            projects_root = (ROOT / "projects").resolve()
            try:
                candidate.relative_to(projects_root)
            except ValueError as exc:
                raise ValueError("project_path 必须位于 projects/ 目录内。") from exc
            return candidate
    return ROOT / "projects" / f"conjecture-{slug}"


def validate_slug(slug: str) -> None:
    if not SLUG_RE.fullmatch(slug):
        raise ValueError("题目标识只能使用小写字母、数字、点、下划线和连字符。")


def discover_items() -> list[dict]:
    found: list[dict] = []
    if not ITEMS_ROOT.is_dir():
        return found
    for directory in ITEMS_ROOT.iterdir():
        if not directory.is_dir() or directory.name.startswith("."):
            continue
        config_path = directory / "config.toml"
        problem_path = directory / "problem.md"
        if not config_path.is_file() or not problem_path.is_file():
            continue
        try:
            config = load_toml(config_path)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            found.append({"slug": directory.name, "invalid": str(exc), "dir": directory})
            continue
        search_contract = str(config.get("search_contract", "either")).strip()
        if search_contract not in SEARCH_CONTRACTS:
            found.append(
                {
                    "slug": directory.name,
                    "invalid": f"未知 search_contract：{search_contract}",
                    "dir": directory,
                }
            )
            continue
        information_mode = str(config.get("information_mode", "")).strip()
        if information_mode and information_mode not in INFORMATION_MODES:
            found.append(
                {
                    "slug": directory.name,
                    "invalid": f"未知 information_mode：{information_mode}",
                    "dir": directory,
                }
            )
            continue
        try:
            stagnation_rounds = int(
                config.get("stagnation_rounds_before_blocked", 3)
            )
        except (TypeError, ValueError):
            stagnation_rounds = 0
        if stagnation_rounds < 0:
            found.append(
                {
                    "slug": directory.name,
                    "invalid": "stagnation_rounds_before_blocked 必须是非负整数",
                    "dir": directory,
                }
            )
            continue
        found.append(
            {
                "slug": directory.name,
                "dir": directory,
                "config": config,
                "title": str(config.get("title", directory.name)),
                "ready": bool(config.get("ready", False)),
                "enabled": bool(config.get("enabled", True)),
                "priority": int(config.get("priority", 100)),
                "max_attempts": int(config.get("max_attempts", 0)),
                "project_path": str(config.get("project_path", "")).strip(),
                "search_contract": search_contract,
                "information_mode": information_mode,
                "stagnation_rounds_before_blocked": stagnation_rounds,
            }
        )
    return sorted(found, key=lambda item: (-item.get("priority", -10**9), item["slug"]))


def status_path(slug: str) -> Path:
    return project_dir(slug) / ".conjecture-status"


def runtime_state_path(slug: str) -> Path:
    return project_dir(slug) / ".queue-runtime.json"


def read_status(slug: str) -> str:
    path = status_path(slug)
    if not path.is_file():
        return "queued"
    return path.read_text(encoding="utf-8").strip() or "queued"


def write_status(slug: str, status: str) -> None:
    if status not in KNOWN_STATUSES:
        raise ValueError(f"未知状态：{status}")
    status_path(slug).write_text(status + "\n", encoding="utf-8")


def read_runtime_state(slug: str) -> dict:
    path = runtime_state_path(slug)
    if not path.is_file():
        return {"attempts": 0, "consecutive_runtime_failures": 0}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"attempts": 0, "consecutive_runtime_failures": 0}


def write_runtime_state(slug: str, state: dict) -> None:
    runtime_state_path(slug).write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def current_state_template(item: dict, *, migration_status: str) -> str:
    legacy = migration_status == "pending"
    evidence_ceiling = "unmigrated-see-verification-ledger" if legacy else "conjecture"
    status_summary = (
        "Legacy state has not yet been summarized; this file changes no evidence level."
        if legacy
        else "The main statement remains a conjecture."
    )
    return f"""# Current State

This is the bounded entry point for the next research round. It summarizes current
state but does not replace the evidence files it cites. Keep it under
{CURRENT_STATE_MAX_LINES} lines and {CURRENT_STATE_MAX_BYTES // 1024} KiB.

## Control

- schema-version: 1
- updated-at: {now_iso()}
- migration-status: `{migration_status}`
- queue-status: `{read_status(item['slug'])}`
- search-contract: `{item.get('search_contract', 'either')}`
- evidence-ceiling: `{evidence_ceiling}`

## Problem and scope

- Formal input: `CURRENT_INPUT.md` and its immutable snapshot.
- Definitions and normalization: not yet audited.
- Scope exclusions: none recorded.

## Current mathematical status

- Strongest usable results: {'see the existing verification ledger' if legacy else 'none recorded'}.
- Current conclusion: {status_summary}
- Human decisions pending: none.

## Active proof frontier

- Smallest open gap: audit the statement and definitions.
- Active routes: not yet selected.
- Blocked routes worth remembering: none.

## Next bounded round

- Goal: audit definitions and form at least three genuinely different method families.
- Acceptance: record a precise gap, strict intermediate result, counterexample test,
  reproducible experiment, or verified literature distinction.

## Evidence pointers

- Verification ledger IDs: none.
- Active proof-map nodes: `P0`.
- Direct evidence files: none.

## History access

- Read `progress.md`, `ideas.md`, `research-tree.md`, and `proof-map.md` only for a
  named gap, node, route, or evidence pointer needed in the current round.
- Historical files remain authoritative evidence; this summary must never silently
  strengthen, weaken, or replace a mathematical claim.
"""


def initialize_current_state(item: dict, project: Path, *, force_pending: bool) -> bool:
    path = project / CURRENT_STATE_NAME
    if path.exists():
        return False
    path.write_text(
        current_state_template(
            item, migration_status="pending" if force_pending else "complete"
        ),
        encoding="utf-8",
    )
    return True


def validate_current_state(project: Path) -> list[str]:
    path = project / CURRENT_STATE_NAME
    if not path.is_file():
        return [f"missing {CURRENT_STATE_NAME}"]
    content = path.read_text(encoding="utf-8")
    issues: list[str] = []
    byte_count = len(content.encode("utf-8"))
    line_count = len(content.splitlines())
    if byte_count > CURRENT_STATE_MAX_BYTES:
        issues.append(
            f"{CURRENT_STATE_NAME} is {byte_count} bytes; limit is {CURRENT_STATE_MAX_BYTES}"
        )
    if line_count > CURRENT_STATE_MAX_LINES:
        issues.append(
            f"{CURRENT_STATE_NAME} is {line_count} lines; limit is {CURRENT_STATE_MAX_LINES}"
        )
    for heading in CURRENT_STATE_REQUIRED_HEADINGS:
        if heading not in content:
            issues.append(f"{CURRENT_STATE_NAME} missing heading: {heading}")
    if "- schema-version: 1" not in content:
        issues.append(f"{CURRENT_STATE_NAME} missing schema-version 1")
    if "- migration-status: `pending`" not in content and (
        "- migration-status: `complete`" not in content
    ):
        issues.append(f"{CURRENT_STATE_NAME} has invalid migration-status")
    return issues


def ensure_project(item: dict) -> Path:
    slug = item["slug"]
    source = item["dir"]
    project = project_dir(slug)
    marker = project / ".conjecture-queue-project.json"
    explicit_project = bool(str(item.get("project_path", "")).strip())
    if project.exists() and not project.is_dir():
        raise RuntimeError(f"目标项目路径不是目录：{project}")
    if project.exists() and not marker.is_file() and not explicit_project:
        raise RuntimeError(
            f"目标目录已经存在但不是队列创建的项目，拒绝覆盖：{project}"
        )

    marker_preexisting = marker.is_file()
    adopted_existing = project.exists() and not marker_preexisting
    project.mkdir(parents=True, exist_ok=True)
    for name in ("notes", "code", "lean", "rethlas", "input-snapshots"):
        (project / name).mkdir(exist_ok=True)

    if not marker.is_file():
        marker.write_text(
            json.dumps(
                {
                    "slug": slug,
                    "source": str(source.relative_to(ROOT)),
                    "created_at": now_iso(),
                    "adopted_existing": adopted_existing,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    initial_files = {
        "README.md": (
            f"# {item['title']}\n\n"
            "本目录由重要猜想队列创建。正式题目以 `CURRENT_INPUT.md` 指向的快照为准。\n\n"
            "## 当前状态\n\n"
            "- 证据等级：`conjecture`\n"
            f"- 搜索承诺：`{item.get('search_contract', 'either')}`\n"
            "- 当前路线：尚未开始\n"
            "- 最小缺口：尚未审计\n"
            "- 下一步：读取题目并完成定义审计\n"
        ),
        "references.md": "# References\n\n尚未开始文献审计。\n",
        "ideas.md": (
            "# Ideas\n\n"
            "至少维护三个实质不同的方法族。根 Agent 每回合选择一条主路线深入推进；"
            "独立分支可在额度允许时并行推进其他不兼容路线。\n\n"
            "## 覆盖审计\n\n"
            f"- 搜索承诺：`{item.get('search_contract', 'either')}`\n"
            f"- 阻塞前所需连续再发散轮次：{item.get('stagnation_rounds_before_blocked', 3)}（0 = 不因停滞自动 blocked）\n"
            "- 当前连续无新机制回合数：0\n\n"
            "## 方法族登记表\n\n"
            "| Family | 核心机制/表示 | 信息来源 | 暴露范围 | 决定性子目标 | 状态 | 结构性障碍 | 重开条件 |\n"
            "|---|---|---|---|---|---|---|---|\n"
        ),
        "progress.md": "# Progress\n\n",
        "verification-ledger.md": (
            "# Verification Ledger\n\n"
            "每条新增数学推进都必须登记；未经审查的观察不得进入证明依赖。\n\n"
            "| ID | 日期 | 数学陈述 | 信息来源/隔离 | 证据等级 | 十项检查与反例测试 | 结论 | 证据文件 |\n"
            "|---|---|---|---|---|---|---|---|\n"
        ),
        "research-tree.md": (
            "# Research Tree\n\n"
            "## 当前状态\n\n- 主问题：待审计\n- 当前主路线：待选择\n"
            "- 最新关键事件：队列项目已建立\n- 最大障碍：待审计\n- 下一步：定义审计\n\n"
            "## 路线图\n\n```mermaid\nflowchart TD\n"
            "    P0[\"P0 主问题<br/>conjecture\"]\n```\n"
        ),
        "proof-map.md": (
            "# Proof Map\n\n"
            "## 当前状态\n\n- 目标定理：待审计\n- 当前证据等级：`conjecture`\n"
            "- 当前最小缺口：尚无候选证明\n- 候选证明文件：无\n"
            "- 最近一次验证报告：无\n\n"
            "## 依赖图\n\n```mermaid\nflowchart BT\n"
            "    T0[\"T0 主猜想<br/>conjecture\"]\n```\n"
        ),
    }
    for relative, content in initial_files.items():
        path = project / relative
        if not path.exists():
            path.write_text(content, encoding="utf-8")

    initialize_current_state(
        item,
        project,
        force_pending=adopted_existing or marker_preexisting,
    )

    if not status_path(slug).exists():
        write_status(slug, "queued")
    if not runtime_state_path(slug).exists():
        write_runtime_state(slug, {"attempts": 0, "consecutive_runtime_failures": 0})
    return project


def source_files(source: Path) -> list[Path]:
    files = [source / "problem.md", source / "config.toml"]
    refs = source / "references"
    if refs.is_dir():
        files.extend(
            path
            for path in sorted(refs.rglob("*"))
            if path.is_file() and not path.is_symlink()
        )
    return files


def create_input_snapshot(item: dict, project: Path) -> Path:
    source = item["dir"]
    digest = hashlib.sha256()
    files = source_files(source)
    for path in files:
        relative = path.relative_to(source)
        digest.update(str(relative).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    short_hash = digest.hexdigest()[:16]
    destination = project / "input-snapshots" / short_hash
    if not destination.exists():
        destination.mkdir(parents=True)
        for path in files:
            relative = path.relative_to(source)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        (destination / "SNAPSHOT.json").write_text(
            json.dumps(
                {
                    "source": str(source.relative_to(ROOT)),
                    "sha256_prefix": short_hash,
                    "created_at": now_iso(),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    current = project / "CURRENT_INPUT.md"
    current.write_text(
        "# Current Input\n\n"
        f"- 来源：`{source.relative_to(ROOT)}`\n"
        f"- 不可变快照：`input-snapshots/{short_hash}/`\n"
        f"- 题目：`input-snapshots/{short_hash}/problem.md`\n"
        f"- 更新时间：{now_iso()}\n",
        encoding="utf-8",
    )
    return destination


def build_prompt(
    item: dict, project: Path, snapshot: Path, web_search: bool = True
) -> str:
    slug = item["slug"]
    search_contract = str(item.get("search_contract", "either"))
    stagnation_rounds = int(item.get("stagnation_rounds_before_blocked", 3))
    if stagnation_rounds == 0:
        blocked_instruction = "不得仅因现有路线耗尽或连续停滞而把题目设为 blocked；保持 pushing，在后续有边界回合持续生成新表述和新机制，直到完整结果、人工停止或其他必须暂停的状态。"
    else:
        blocked_instruction = f"只有所有主要路线均结构性阻塞，并且已经连续完成至少 {stagnation_rounds} 个没有发现新机制的再发散回合时才使用 blocked；写明最强中间结果、每条路线的精确障碍和停滞计数。发现新机制时把计数归零。"
    if search_contract == "affirmative-proof":
        search_instruction = f"""本题的搜索承诺为 `affirmative-proof`。在搜索调度上假定存在完整肯定证明，并把找到通过审计的完整肯定证明作为预期终点。不得因问题公开、困难、当前方法失败或已登记路线耗尽而降低目标或停止；应持续生成新的表述、不变量、分解、嵌入或构造。这个工作假定不是数学证据，主命题仍为 conjecture。任何主命题反例候选都必须完整记录和认证；若严格成立，它在逻辑上推翻工作假定并触发人工复核。"""
    elif search_contract == "counterexample":
        search_instruction = """本题的搜索承诺为 `counterexample`。持续寻找并严格认证足以否定主命题的反例，不以候选构造或有限参数检验代替证明。若出现完整肯定证明候选，同样必须记录并认证。"""
    else:
        search_instruction = """本题的搜索承诺为 `either`。完整肯定证明或经严格认证的决定性反例都可以成为预期终点；普通归约、局部计算和未闭合引理不能作为完成。"""
    if web_search:
        information_mode = """本次启动的信息模式为 `connected`：可以联网核查，但必须优先使用原始来源，逐项核对定义与假设。外部路线只能作为输入，不能替代关键证明。"""
        evidence_instruction = "文献结论必须核对原始定理、全部假设和定义一致性。"
        input_instruction = (
            f"2. {project / 'CURRENT_INPUT.md'} 及其指向的题目、配置和参考资料"
        )
    else:
        information_mode = """本次启动的信息模式为 `offline`：禁止公共互联网、连接器和新增外部数据源；不得读取题目快照 references/ 或项目 references.md 中的外部文献内容。只使用正式题目、明确允许的基础事实、内部生成且来源可追踪的项目状态、计算和推理。记忆中的外部定理只能登记为待核查线索，不能作为证明依据；不得宣称结果新颖或问题开放。"""
        evidence_instruction = "外部记忆只可记录为待核查线索，不得进入证明依赖。"
        input_instruction = (
            f"2. {project / 'CURRENT_INPUT.md'} 及其指向的 problem.md 和 config.toml；"
            "不要读取快照 references/"
        )
    return f"""你正在执行“重要猜想队列”的一个独立研究回合。

题目标识：{slug}
题目快照：{snapshot / 'problem.md'}
研究项目：{project}

先完整读取：
1. {ROOT / 'AGENTS.md'}
{input_instruction}
3. {project / CURRENT_STATE_NAME}
4. CURRENT_STATE.md 明确指向的 ledger 行、proof-map 节点、路线和直接证据
5. notes/ 中与当前最小缺口直接相关的材料

渐进读取规则：
- CURRENT_STATE.md 是下一回合的短入口，必须保持在 {CURRENT_STATE_MAX_LINES} 行和 {CURRENT_STATE_MAX_BYTES // 1024} KiB 以内；它只做索引和当前状态摘要，不替代证据。
- 不得默认完整重读 progress.md、ideas.md、research-tree.md、proof-map.md 或 verification-ledger.md。只读取当前目标实际需要的段落、节点和证据。
- 若 CURRENT_STATE.md 的 migration-status 为 `pending`，先读取 README/proof-map 的当前状态段、最近一个完整 progress 回合和其中引用的 ledger/证据，建立保守摘要；遗漏的旧结果按未知处理，不得自行降低或提高证据等级。随后把 migration-status 改为 `complete`。

{information_mode}

{search_instruction}

本回合要求：
- 直接推进搜索承诺指定的目标；不得以问题可能公开为理由停止。
- 根 Agent 选择一个最有价值的主路线深入推进。初始阶段先审计定义、量词、归一化和最小例子；随后至少形成三个实质不同的方法族。若有编排能力且额度允许，独立探索分支可同时推进其他相互不兼容的有界路线；“一个主路线”不是“整个回合只能研究一个思路”。
- 在 ideas.md 维护方法族登记表，按核心机制而不是表面措辞归类；记录信息来源、暴露范围、决定性子目标、证伪测试、结构性障碍和重开条件。若路线只是把主问题改写成等强引理，不视为取得进展。
- 若研究者已要求多智能体长跑且编排能力可用，按 research-workflow.md 动态分派：早期探索者使用不含热门路线和失败史的盲问题包；优先覆盖不足的方法族；在信息增益足够时维持少量独立分支，不设永久固定配额；候选证明另交对抗审计。子 Agent 只写独立分支产物，根 Agent 统一同步共享台账。
- 优先产生可复用的严格中间结果、反例测试、计算证据或精确缺口。{evidence_instruction}
- 推进要大胆：可以提出高风险引理、非常规构造和反例候选，并主动尝试修复失败路线。认证要保守：本回合新增的每一条数学推进都必须立即做与其强度相称的严格审查，明确检查定义、隐含假设、逻辑推出、反例、边界/除零/符号、外部定理假设以及是否只证明了弱化版本；把审查过程和结论写入 progress.md 或对应 notes 文件。
- 只允许修改本研究项目 {project}；不得修改题目源目录、其他项目、AGENTS.md 或工作区规则；不得提交 Git。
- 普通计算实验使用 graphlab 环境，记录命令、参数、随机种子和误差风险。
- 不得自动调用 Rethlas、网页端 Pro 或其他付费升级。若 Codex 层面同一精确缺口两次失败且适合升级，只准备完整交接稿，并把状态设为 needs-escalation-approval。
- 不写论文，不把计算观察写成定理，不把任何 Agent 结果升级为 human-verified。

证明冻结规则：
- 如果形成新的候选证明或严格中间结果，立即冻结依赖该结论的分支，逐项执行 AGENTS.md 的十条验证清单并主动寻找反例。审查完成前，该分支不得继续建立下游结论；证据等级最多标为 proof-draft。与该结论没有依赖关系、使用独立问题包且不写共享台账的分支可以继续。不要因为第一条候选引理出现就终止全部探索者。
- 对抗审计者只接收被冻结分支的正式陈述、证明和依赖清单。根 Agent 在安全汇合点统一写入共享台账，避免审计和探索分支并发覆盖。
- 经审查成立但尚未完整解决主猜想的中间引理或部分结果，应准确标为 partial-result 或 proof-draft，记录其适用范围和下一缺口；只要仍有明确路线，状态可以保持 pushing，之后继续公平轮询。
- 如果出现需要老师尽快判断的重要中间结果、潜在可发表现象或无法由当前 Agent 独立裁决的证明审计，把状态设为 needs-human-review。该状态只暂停当前题，不冻结其他猜想的轮询。
- 只有在已经给出主猜想的完整候选证明，或者给出并严格核验了足以彻底否定主猜想的反例，而且十项验证清单全部通过时，才把 {project / '.conjecture-status'} 改成单独一行 solved-awaiting-human-verification。这会冻结整个队列，等待老师逐步复核。单个 Codex 回合即使自检通过也最多是 proof-draft；只有独立 Agent/Rethlas 审查通过后才可标为 agent-verified。
- 如果题目有实质歧义，把状态改为 needs-human-input，并记录必须由老师决定的精确问题。
- 如果需要 Rethlas 升级许可，把状态改为 needs-escalation-approval；不得启动 Rethlas。
- 如果仍有明确可推进的下一步，状态保持 pushing。
- {blocked_instruction}
- blocked 路线只有出现能直接攻击原 gap 的新机制、不变量、构造、假设或工具才能重开；增加 Agent 数量、重复推导或改写措辞不是重开理由。

回合结束前必须：
1. 按 AGENTS.md 格式追加 progress.md；
2. 只把实质数学推进、关键失败或证据等级变化登记到 verification-ledger.md；
3. 重写 CURRENT_STATE.md，使其准确反映当前最小缺口、可用结果、活动路线、下一回合和证据指针，并通过大小与章节约束；
4. 仅当对应结构真的变化时更新 ideas.md、research-tree.md 或 proof-map.md；仅当项目稳定范围变化时更新 README.md，禁止向 README 追加逐回合日志；
5. 把证明草稿、计算或交接稿放入正确子目录；
6. 在 {project / '.conjecture-status'} 写入一个合法状态；
7. 最终答复简要列出本回合产物、检查、证据等级、未关闭缺口和下一步。
"""


def locate_codex(config: dict) -> str:
    explicit = str(config.get("codex_path", "")).strip()
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file() or not os.access(path, os.X_OK):
            raise RuntimeError(f"codex_path 不可执行：{path}")
        return str(path)
    found = shutil.which("codex")
    if not found:
        raise RuntimeError("PATH 中找不到 codex；请在 runner.toml 设置 codex_path。")
    return found


def codex_command(
    config: dict,
    project: Path,
    prompt: str,
    last_message: Path,
    *,
    web_search: bool | None = None,
    sandbox: str = "workspace-write",
) -> list[str]:
    command = [
        locate_codex(config),
        "-C",
        str(project),
        "-s",
        sandbox,
        "-a",
        "never",
    ]
    if web_search is None:
        web_search = resolve_information_mode(config) == "connected"
    if web_search:
        command.append("--search")
    model = str(config.get("model", "")).strip()
    if model:
        command.extend(["-m", model])
    effort = str(config.get("reasoning_effort", "")).strip()
    if effort:
        command.extend(["-c", f'model_reasoning_effort="{effort}"'])
    command.extend(
        [
            "exec",
            "--skip-git-repo-check",
            "--ephemeral",
            "--json",
            "--output-last-message",
            str(last_message),
            prompt,
        ]
    )
    return command


def bubblewrap_command(
    command: list[str],
    cwd: Path,
    *,
    writable_dirs: list[Path],
    hidden_dirs: list[Path],
    environment: dict[str, str] | None = None,
    writable_bindings: list[tuple[Path, Path]] | None = None,
) -> list[str]:
    """Wrap a lane command in an OS mount namespace without network isolation."""
    bubblewrap = shutil.which("bwrap")
    if not bubblewrap:
        raise RuntimeError(
            "mixed-isolated 需要 bubblewrap 提供文件系统隔离；当前 PATH 中找不到 bwrap。"
        )
    wrapped = [
        bubblewrap,
        "--die-with-parent",
        "--new-session",
        "--unshare-pid",
        "--ro-bind",
        "/",
        "/",
        "--proc",
        "/proc",
        "--dev",
        "/dev",
    ]
    for directory in writable_dirs:
        resolved = directory.resolve()
        if not resolved.is_dir():
            raise RuntimeError(f"mixed-isolated 可写目录不存在：{resolved}")
        wrapped.extend(["--bind", str(resolved), str(resolved)])
    for directory in hidden_dirs:
        resolved = directory.resolve()
        if not resolved.is_dir():
            raise RuntimeError(f"mixed-isolated 隐藏目录不存在：{resolved}")
        wrapped.extend(["--tmpfs", str(resolved)])
    for source, target in writable_bindings or []:
        resolved_source = source.resolve()
        resolved_target = target.resolve()
        if not resolved_source.is_dir():
            raise RuntimeError(
                f"mixed-isolated 私有绑定源不存在：{resolved_source}"
            )
        if not resolved_target.is_dir():
            raise RuntimeError(
                f"mixed-isolated 私有绑定目标不存在：{resolved_target}"
            )
        wrapped.extend(
            ["--bind", str(resolved_source), str(resolved_target)]
        )
    for name, value in (environment or {}).items():
        wrapped.extend(["--setenv", name, value])
    wrapped.extend(["--chdir", str(cwd.resolve()), "--", *command])
    return wrapped


def prepare_lane_codex_home(destination: Path) -> Path:
    """Create a private writable Codex runtime with only login bootstrap files."""
    destination.mkdir(parents=True, mode=0o700, exist_ok=True)
    source = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).resolve()
    for name in ("auth.json", "installation_id", "models_cache.json"):
        candidate = source / name
        if candidate.is_file() and not candidate.is_symlink():
            shutil.copy2(candidate, destination / name)
    return destination.resolve()


def append_history(slug: str, record: dict) -> None:
    history = RUNTIME_ROOT / "history.jsonl"
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    with history.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"slug": slug, **record}, ensure_ascii=False) + "\n")


def run_codex_process(
    command: list[str],
    cwd: Path,
    event_log: Path,
    timeout_seconds: int,
    label: str = "",
) -> dict:
    """Run one Codex process and stream its output to a dedicated event log."""
    event_log.parent.mkdir(parents=True, exist_ok=True)
    timed_out = False
    return_code = 1
    try:
        with event_log.open("w", encoding="utf-8") as output:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                start_new_session=True,
            )

            def pump_output() -> None:
                assert process.stdout is not None
                for line in process.stdout:
                    output.write(line)
                    output.flush()
                    prefix = f"[{label}] " if label else ""
                    print(prefix + line, end="", flush=True)

            output_thread = threading.Thread(target=pump_output, daemon=True)
            output_thread.start()
            try:
                return_code = process.wait(
                    timeout=None if timeout_seconds <= 0 else timeout_seconds
                )
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGINT)
                try:
                    return_code = process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        return_code = process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        return_code = process.wait()
            output_thread.join(timeout=10)
            if process.stdout is not None:
                process.stdout.close()
    except OSError as exc:
        event_log.write_text(f"runner error: {exc}\n", encoding="utf-8")
        print(f"[{label or 'codex'}] runner error: {exc}", file=sys.stderr, flush=True)
    return {"return_code": return_code, "timed_out": timed_out}


def copy_connected_workspace(
    project: Path, snapshot: Path, destination: Path
) -> tuple[Path, Path]:
    """Create a frozen workspace for the connected lane outside the live project."""
    lane_root = destination / "workspace"
    lane_project = lane_root / "project"
    lane_root.mkdir(parents=True)
    for relative in (
        Path("AGENTS.md"),
        Path("agents/instructions/research-workflow.md"),
        Path("agents/instructions/queue-and-escalation.md"),
    ):
        source = ROOT / relative
        if source.is_file():
            target = lane_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    def ignore_untrusted_entries(directory: str, names: list[str]) -> set[str]:
        ignored = {
            ".git",
            ".queue-runtime.json",
            ".conjecture-status",
            "__pycache__",
        }
        return {
            name
            for name in names
            if name in ignored or (Path(directory) / name).is_symlink()
        }

    shutil.copytree(
        project,
        lane_project,
        ignore=ignore_untrusted_entries,
    )
    replacements = (
        (str(project.resolve()), str(lane_project.resolve())),
        (str(ROOT.resolve()), str(lane_root.resolve())),
    )
    for path in lane_root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        if path.suffix not in {".md", ".toml", ".json", ".txt"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rewritten = content
        for old, new in replacements:
            rewritten = rewritten.replace(old, new)
        if rewritten != content:
            path.write_text(rewritten, encoding="utf-8")
    lane_snapshot = lane_project / snapshot.relative_to(project)
    if not (lane_snapshot / "problem.md").is_file():
        raise RuntimeError("联网隔离工作区缺少题目快照。")
    return lane_root, lane_project


def build_connected_lane_prompt(
    item: dict, lane_root: Path, lane_project: Path, lane_snapshot: Path
) -> str:
    return f"""你是 mixed-isolated 研究回合中的联网核查分支。

题目标识：{item['slug']}
冻结题目：{lane_snapshot / 'problem.md'}
冻结项目副本：{lane_project}

先完整读取：
1. {lane_root / 'AGENTS.md'}
2. {lane_root / 'agents/instructions/research-workflow.md'}
3. {lane_root / 'agents/instructions/queue-and-escalation.md'}
4. 冻结项目副本中的 CURRENT_STATE.md、它明确指向的证据和直接相关 notes

本分支允许使用公共互联网做文献核查。优先读取论文正文、出版方页面和作者版本，逐项核对
定理的定义、归一化与全部假设。每条外部结论都要给出可追踪链接并标记 `web-source`。

这是隔离分支。离线分支与本分支并行运行，汇合点之前看不到你的结果。你只能修改冻结项目
副本，不得访问或修改原研究项目、题目源目录或 Git 仓库，不得调用 Rethlas 或网页端 Pro。
不要改写共享台账或状态文件，也不要把文献中的断言当作已经证明的当前结论。

选择一个信息增益最高的动作：核查当前关键缺口是否已有可用定理，寻找能改变方法族的新机制，
或对冻结项目中的脆弱断言进行联网对抗审计。返回具体定理、公式、反例或精确适用性差异，
拒绝只有状态和泛泛建议的报告。

把完整结果写入 {lane_project / 'CONNECTED_RESULT.md'}。文件必须列出检索范围、来源链接、
可安全导入的结论、不能直接导入的线索、对离线路线的潜在影响及仍需独立验证的缺口。
最终答复只简要概括该文件。
"""


def build_mixed_integration_prompt(
    item: dict, project: Path, checkpoint: Path
) -> str:
    return f"""你正在执行 mixed-isolated 回合的汇合审计。

题目标识：{item['slug']}
研究项目：{project}
联网隔离结果：{checkpoint / 'connected' / 'RESULT.md'}
隔离清单：{checkpoint / 'CHECKPOINT.json'}

先完整读取 {ROOT / 'AGENTS.md'}、research-workflow.md、queue-and-escalation.md，以及项目的
CURRENT_STATE.md、它明确指向的 ledger 行、proof-map 节点和直接证据。不要默认完整重读
progress.md、ideas.md、research-tree.md、proof-map.md 或 verification-ledger.md。
离线分支已经在本项目完成本轮推进。联网分支只看过回合开始时的冻结副本，其结果直到现在
才被复制到项目中。

本汇合回合不允许新增互联网检索。逐条审计联网结果，核对来源、定义、假设和归一化；外部
材料只能关闭它实际证明的步骤。保留离线独立得到的节点为 `internal-offline`。从联网材料
导入的节点标为 `web-source`，受其影响的新推导标为 `mixed`。不得追溯性地把 mixed 节点
记为独立发现。

只导入经过审查且对当前项目有用的信息。无法核实或不能直接适用的内容保留为线索，不进入
proof map 的已证明依赖。同步本回合影响到的共享台账和状态，重写 CURRENT_STATE.md，并在 progress.md 记录汇合点、
来源污染边界、接受或拒绝的联网结论以及下一步。候选完整证明或决定性反例仍须执行十项
认证，证据等级不得自动升级为 human-verified。

只能修改 {project}，不得修改题目源、其他项目、工作区规则或 Git 仓库。回合结束时给出
产物、检查、证据等级、未关闭缺口和下一步。
"""


def persist_connected_checkpoint(
    project: Path,
    attempt_number: int,
    connected_result: Path,
    metadata: dict,
) -> Path:
    checkpoint = (
        project
        / "notes"
        / "mixed-isolated"
        / f"attempt-{attempt_number:04d}"
    )
    connected_dir = checkpoint / "connected"
    connected_dir.mkdir(parents=True, exist_ok=True)
    destination = connected_dir / "RESULT.md"
    if connected_result.is_file() and not connected_result.is_symlink():
        shutil.copy2(connected_result, destination)
    else:
        destination.write_text(
            "# Connected lane result\n\n联网分支没有生成可导入的结果。\n",
            encoding="utf-8",
        )
    (checkpoint / "CHECKPOINT.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return checkpoint


def execute_mixed_isolated_attempt(
    item: dict,
    config: dict,
    project: Path,
    snapshot: Path,
    logs: Path,
    attempt_number: int,
    timestamp: str,
) -> dict:
    """Run offline and connected lanes concurrently, then integrate at a checkpoint."""
    timeout_seconds = int(config.get("attempt_timeout_minutes", 90)) * 60
    offline_event = logs / f"attempt-{attempt_number:04d}-{timestamp}-offline.jsonl"
    offline_last = logs / f"attempt-{attempt_number:04d}-{timestamp}-offline-last.md"
    connected_event = logs / f"attempt-{attempt_number:04d}-{timestamp}-connected.jsonl"
    connected_last = logs / f"attempt-{attempt_number:04d}-{timestamp}-connected-last.md"
    integration_event = logs / f"attempt-{attempt_number:04d}-{timestamp}-integration.jsonl"
    integration_last = logs / f"attempt-{attempt_number:04d}-{timestamp}-last.md"

    offline_prompt = build_prompt(item, project, snapshot, web_search=False)
    offline_prompt += """

你是 mixed-isolated 的离线分支。另一个联网分支正在隔离工作区并行核查，但其输入和输出
在本回合汇合前对你不可见。保持 internal-offline 来源边界，不要搜索运行日志或隔离目录。
"""
    offline_codex_command = codex_command(
        config,
        project,
        offline_prompt,
        offline_last,
        web_search=False,
        sandbox="danger-full-access",
    )

    LANE_RUNTIME_ROOT.mkdir(parents=True, mode=0o700, exist_ok=True)
    with (
        tempfile.TemporaryDirectory(
            prefix=f"conjecture-{item['slug']}-mixed-"
        ) as raw,
        tempfile.TemporaryDirectory(
            prefix=f"conjecture-{item['slug']}-offline-codex-",
            dir=LANE_RUNTIME_ROOT,
        ) as offline_codex_raw,
        tempfile.TemporaryDirectory(
            prefix=f"conjecture-{item['slug']}-connected-codex-",
            dir=LANE_RUNTIME_ROOT,
        ) as connected_codex_raw,
    ):
        isolated_root = Path(raw)
        offline_codex_home = prepare_lane_codex_home(Path(offline_codex_raw))
        connected_codex_home = prepare_lane_codex_home(Path(connected_codex_raw))
        sandbox_registry_target = Path(
            f"/tmp/codex-bwrap-synthetic-mount-targets-{os.getuid()}"
        )
        sandbox_registry_target.mkdir(mode=0o700, exist_ok=True)
        offline_sandbox_registry = offline_codex_home / "bwrap-registry"
        connected_sandbox_registry = connected_codex_home / "bwrap-registry"
        offline_sandbox_registry.mkdir(mode=0o700)
        connected_sandbox_registry.mkdir(mode=0o700)
        lane_root, lane_project = copy_connected_workspace(
            project, snapshot, isolated_root
        )
        lane_snapshot = lane_project / snapshot.relative_to(project)
        connected_prompt = build_connected_lane_prompt(
            item, lane_root, lane_project, lane_snapshot
        )
        temporary_connected_event = isolated_root / "connected.jsonl"
        temporary_connected_last = isolated_root / "connected-last.md"
        connected_codex_command = codex_command(
            config,
            lane_project,
            connected_prompt,
            temporary_connected_last,
            web_search=True,
            sandbox="danger-full-access",
        )
        offline_command = bubblewrap_command(
            offline_codex_command,
            project,
            writable_dirs=[project, logs, offline_codex_home],
            hidden_dirs=[isolated_root, connected_codex_home],
            environment={"CODEX_HOME": str(offline_codex_home)},
            writable_bindings=[
                (offline_sandbox_registry, sandbox_registry_target)
            ],
        )
        connected_command = bubblewrap_command(
            connected_codex_command,
            lane_project,
            writable_dirs=[isolated_root, connected_codex_home],
            hidden_dirs=[ROOT, offline_codex_home],
            environment={"CODEX_HOME": str(connected_codex_home)},
            writable_bindings=[
                (connected_sandbox_registry, sandbox_registry_target)
            ],
        )

        results: dict[str, dict] = {}

        def run_lane(
            name: str, command: list[str], cwd: Path, event_log: Path
        ) -> None:
            results[name] = run_codex_process(
                command, cwd, event_log, timeout_seconds, label=name
            )

        offline_thread = threading.Thread(
            target=run_lane,
            args=("offline", offline_command, project, offline_event),
        )
        connected_thread = threading.Thread(
            target=run_lane,
            args=(
                "connected",
                connected_command,
                lane_project,
                temporary_connected_event,
            ),
        )
        offline_thread.start()
        connected_thread.start()
        offline_thread.join()
        connected_thread.join()

        if temporary_connected_event.is_file():
            shutil.copy2(temporary_connected_event, connected_event)
        if temporary_connected_last.is_file():
            shutil.copy2(temporary_connected_last, connected_last)
        lane_result = lane_project / "CONNECTED_RESULT.md"
        connected_result = lane_result if lane_result.is_file() else temporary_connected_last
        metadata = {
            "mode": "mixed-isolated",
            "attempt": attempt_number,
            "created_at": now_iso(),
            "input_snapshot": str(snapshot.relative_to(project)),
            "offline": results.get("offline", {}),
            "connected": results.get("connected", {}),
            "visibility_rule": (
                "connected output copied into the live project only after both lanes ended"
            ),
            "provenance": {
                "offline": "internal-offline",
                "connected": "web-source",
                "post-checkpoint": "mixed",
            },
        }
        checkpoint = persist_connected_checkpoint(
            project, attempt_number, connected_result, metadata
        )

    offline_result = results.get("offline", {"return_code": 1, "timed_out": False})
    connected_result_state = results.get(
        "connected", {"return_code": 1, "timed_out": False}
    )
    lane_failed = (
        offline_result["return_code"] != 0
        or connected_result_state["return_code"] != 0
        or offline_result["timed_out"]
        or connected_result_state["timed_out"]
    )
    if lane_failed:
        metadata["integration"] = {
            "status": "skipped",
            "reason": "offline or connected lane failed or timed out",
        }
        (checkpoint / "CHECKPOINT.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return {
            "return_code": 1,
            "timed_out": bool(
                offline_result["timed_out"] or connected_result_state["timed_out"]
            ),
            "event_log": offline_event,
            "last_message": offline_last if offline_last.is_file() else None,
            "lane_event_logs": {
                "offline": offline_event,
                "connected": connected_event,
            },
        }

    integration_prompt = build_mixed_integration_prompt(item, project, checkpoint)
    integration_command = codex_command(
        config,
        project,
        integration_prompt,
        integration_last,
        web_search=False,
    )
    integration_result = run_codex_process(
        integration_command,
        project,
        integration_event,
        timeout_seconds,
        label="integration",
    )
    metadata["integration"] = integration_result
    metadata["finished_at"] = now_iso()
    (checkpoint / "CHECKPOINT.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        **integration_result,
        "event_log": integration_event,
        "last_message": integration_last if integration_last.is_file() else None,
        "lane_event_logs": {
            "offline": offline_event,
            "connected": connected_event,
            "integration": integration_event,
        },
    }


def execute_attempt(item: dict, config: dict, dry_run: bool = False) -> int:
    slug = item["slug"]
    state = read_runtime_state(slug)
    attempt_number = int(state.get("attempts", 0)) + 1
    logs = RUNTIME_ROOT / "logs" / slug
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    event_log = logs / f"attempt-{attempt_number:04d}-{timestamp}.jsonl"
    last_message = logs / f"attempt-{attempt_number:04d}-{timestamp}-last.md"
    information_mode = effective_information_mode(item, config)

    if dry_run:
        project = project_dir(slug)
        snapshot = project / "input-snapshots" / "<computed-at-run-time>"
        print(f"[dry-run] 将运行：{slug}")
        print(f"[dry-run] 项目：{project}")
        print(f"[dry-run] 快照：{snapshot}")
        print(f"[dry-run] 信息模式：{information_mode}")
        if information_mode == "mixed-isolated":
            isolated = project / "<temporary-connected-copy>"
            offline_command = codex_command(
                config,
                project,
                "<离线研究提示词>",
                logs / "<offline-last.md>",
                web_search=False,
                sandbox="danger-full-access",
            )
            connected_command = codex_command(
                config,
                isolated,
                "<联网核查提示词>",
                logs / "<connected-last.md>",
                web_search=True,
                sandbox="danger-full-access",
            )
            integration_command = codex_command(
                config,
                project,
                "<汇合审计提示词>",
                logs / "<integration-last.md>",
                web_search=False,
            )
            print(
                "[dry-run] 并行离线分支："
                f"{shlex.join(offline_command[:-1])} <离线研究提示词>"
            )
            print(
                "[dry-run] 并行联网分支："
                f"{shlex.join(connected_command[:-1])} <联网核查提示词>"
            )
            print(
                "[dry-run] 汇合审计："
                f"{shlex.join(integration_command[:-1])} <汇合审计提示词>"
            )
            print("[dry-run] 额度提示：一次 mixed-isolated 回合包含三次 Codex 调用。")
        else:
            command = codex_command(
                config,
                project,
                "<研究提示词>",
                last_message,
                web_search=information_mode == "connected",
            )
            print(f"[dry-run] 命令：{shlex.join(command[:-1])} <研究提示词>")
        return 0

    project = ensure_project(item)
    snapshot = create_input_snapshot(item, project)
    logs.mkdir(parents=True, exist_ok=True)
    write_status(slug, "pushing")
    started_at = now_iso()
    print(
        f"[{started_at}] 开始 {slug}，第 {attempt_number} 回合，"
        f"mode={information_mode}",
        flush=True,
    )
    if information_mode == "mixed-isolated":
        outcome = execute_mixed_isolated_attempt(
            item,
            config,
            project,
            snapshot,
            logs,
            attempt_number,
            timestamp,
        )
    else:
        prompt = build_prompt(
            item,
            project,
            snapshot,
            web_search=information_mode == "connected",
        )
        command = codex_command(
            config,
            project,
            prompt,
            last_message,
            web_search=information_mode == "connected",
        )
        timeout_seconds = int(config.get("attempt_timeout_minutes", 90)) * 60
        result = run_codex_process(
            command, project, event_log, timeout_seconds
        )
        outcome = {
            **result,
            "event_log": event_log,
            "last_message": last_message if last_message.is_file() else None,
            "lane_event_logs": {information_mode: event_log},
        }

    return_code = int(outcome["return_code"])
    timed_out = bool(outcome["timed_out"])
    outcome_event_log = Path(outcome["event_log"])
    outcome_last_message = outcome.get("last_message")

    state["attempts"] = attempt_number
    state["last_started_at"] = started_at
    state["last_finished_at"] = now_iso()
    state["last_return_code"] = return_code
    state["last_timed_out"] = timed_out
    state["last_information_mode"] = information_mode
    state["last_event_log"] = str(outcome_event_log.relative_to(ROOT))
    state["last_message"] = (
        str(Path(outcome_last_message).relative_to(ROOT))
        if outcome_last_message is not None
        else None
    )
    state["last_lane_event_logs"] = {
        name: str(Path(path).relative_to(ROOT))
        for name, path in outcome.get("lane_event_logs", {}).items()
        if Path(path).is_file()
    }
    if return_code == 0 and not timed_out:
        state["consecutive_runtime_failures"] = 0
    else:
        state["consecutive_runtime_failures"] = int(
            state.get("consecutive_runtime_failures", 0)
        ) + 1
        if state["consecutive_runtime_failures"] >= int(
            config.get("max_consecutive_runtime_failures", 3)
        ):
            write_status(slug, "runtime-error")

    if (
        information_mode == "mixed-isolated"
        and (return_code != 0 or timed_out)
        and read_status(slug) == "solved-awaiting-human-verification"
    ):
        state["mixed_audit_incomplete"] = True
        write_status(slug, "needs-human-review")

    state_issues = validate_current_state(project)
    if state_issues:
        state["current_state_validation_errors"] = state_issues
        write_status(slug, "needs-human-review")
        print(
            f"CURRENT_STATE 验证失败，已暂停 {slug}：" + "; ".join(state_issues),
            file=sys.stderr,
            flush=True,
        )
    else:
        state.pop("current_state_validation_errors", None)

    status = read_status(slug)
    if status not in KNOWN_STATUSES:
        state["invalid_agent_status"] = status
        write_status(slug, "needs-human-input")
        status = "needs-human-input"
    write_runtime_state(slug, state)
    append_history(
        slug,
        {
            "attempt": attempt_number,
            "started_at": started_at,
            "finished_at": state["last_finished_at"],
            "return_code": return_code,
            "timed_out": timed_out,
            "status": status,
            "information_mode": information_mode,
            "event_log": state["last_event_log"],
            "lane_event_logs": state["last_lane_event_logs"],
        },
    )
    print(
        f"[{state['last_finished_at']}] 结束 {slug}：return={return_code}，status={status}",
        flush=True,
    )
    return return_code


def eligible_items(items: list[dict]) -> list[dict]:
    eligible: list[dict] = []
    for item in items:
        if item.get("invalid") or not item.get("ready") or not item.get("enabled"):
            continue
        state = read_runtime_state(item["slug"])
        attempts = int(state.get("attempts", 0))
        max_attempts = int(item.get("max_attempts", 0))
        if max_attempts > 0 and attempts >= max_attempts:
            if read_status(item["slug"]) in RUNNABLE_STATUSES:
                write_status(item["slug"], "attempt-limit")
            continue
        if read_status(item["slug"]) in RUNNABLE_STATUSES:
            eligible.append(item)
    return eligible


def solution_holds(items: list[dict] | None = None) -> list[str]:
    candidates = discover_items() if items is None else items
    return [
        item["slug"]
        for item in candidates
        if not item.get("invalid")
        and project_dir(item["slug"]).is_dir()
        and read_status(item["slug"]) == "solved-awaiting-human-verification"
    ]


def focus_lock_file(slug: str) -> Path:
    validate_slug(slug)
    return RUNTIME_ROOT / f"runner.{slug}.lock"


def focus_stop_file(slug: str) -> Path:
    validate_slug(slug)
    return RUNTIME_ROOT / f"STOP.{slug}"


def focus_session_name(config: dict, slug: str) -> str:
    validate_slug(slug)
    return f"{config['session_name']}__{slug}"


def lock_held(path: Path) -> bool:
    if not path.is_file():
        return False
    with path.open("a", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(handle, fcntl.LOCK_UN)
    return False


def runner_lock_held(slug: str | None = None) -> bool:
    return lock_held(focus_lock_file(slug) if slug else LOCK_FILE)


def active_focus_slugs(items: list[dict] | None = None) -> list[str]:
    candidates = discover_items() if items is None else items
    return [
        item["slug"]
        for item in candidates
        if not item.get("invalid") and runner_lock_held(item["slug"])
    ]


def wait_for_rescan(seconds: int, stop_file: Path | None = STOP_FILE) -> bool:
    """Wait up to seconds; return early when a safe-stop request appears."""
    deadline = time.monotonic() + max(1, seconds)
    while time.monotonic() < deadline:
        if stop_file is not None and stop_file.exists():
            return True
        time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))
    return bool(stop_file is not None and stop_file.exists())


def consume_stop_request(stop_file: Path | None = STOP_FILE) -> bool:
    if stop_file is None or not stop_file.exists():
        return False
    stop_file.unlink(missing_ok=True)
    return True


def run_loop(args: argparse.Namespace) -> int:
    config = load_runner_config()
    if args.dry_run:
        return run_loop_body(args, config, None)

    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    slug = args.slug
    if slug:
        validate_slug(slug)
    lock_file = focus_lock_file(slug) if slug else LOCK_FILE
    stop_file = focus_stop_file(slug) if slug else STOP_FILE
    with lock_file.open("w", encoding="utf-8") as lock_handle:
        try:
            fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            label = f"题目 {slug}" if slug else "公平队列"
            print(f"错误：{label} 的 runner 已经在运行。", file=sys.stderr)
            return 1
        if slug and runner_lock_held():
            print("错误：公平队列正在运行；请先安全停止后再启动单题 runner。", file=sys.stderr)
            return 1
        if not slug:
            focused = active_focus_slugs()
            if focused:
                print(
                    "错误：以下单题 runner 正在运行：" + ", ".join(focused),
                    file=sys.stderr,
                )
                return 1
        stop_file.unlink(missing_ok=True)
        return run_loop_body(args, config, stop_file)


def run_loop_body(args: argparse.Namespace, config: dict, stop_file: Path | None) -> int:
    started = time.monotonic()
    max_wall_hours = float(config.get("max_wall_hours", 24))
    idle_cycles = 0
    while True:
        if consume_stop_request(stop_file):
            print("检测到停止请求；将在当前回合边界退出。")
            return 0
        if max_wall_hours > 0 and time.monotonic() - started >= max_wall_hours * 3600:
            print(f"达到 max_wall_hours={max_wall_hours}；正常退出。")
            return 0

        items = discover_items()
        holds = solution_holds(items)
        if holds:
            print(
                "全局解答冻结：以下题目声称已完整解决，等待老师审查：" + ", ".join(holds),
                file=sys.stderr,
            )
            print("处理后用 set-status 明确改变状态，才能继续队列。", file=sys.stderr)
            return 3
        if args.slug:
            items = [item for item in items if item["slug"] == args.slug]
            if not items:
                print(f"错误：找不到题目 {args.slug}", file=sys.stderr)
                return 2
        runnable = eligible_items(items)
        if not runnable:
            idle_cycles += 1
            if args.once or args.dry_run:
                print("当前没有可运行题目。")
                return 0
            max_idle = int(config.get("max_idle_cycles", 0))
            if max_idle > 0 and idle_cycles >= max_idle:
                print(f"连续空闲 {idle_cycles} 次；正常退出。")
                return 0
            if wait_for_rescan(int(config.get("idle_seconds", 60)), stop_file):
                consume_stop_request(stop_file)
                print("检测到停止请求；在空闲扫描边界退出。")
                return 0
            continue

        idle_cycles = 0
        for item in runnable:
            if consume_stop_request(stop_file):
                return 0
            if read_status(item["slug"]) not in RUNNABLE_STATUSES:
                continue
            execute_attempt(item, config, dry_run=args.dry_run)
            if read_status(item["slug"]) == "solved-awaiting-human-verification":
                print("主问题声称已完整解决，触发全局解答冻结。", flush=True)
                return 3
            if args.once or args.dry_run:
                return 0


def add_item(args: argparse.Namespace) -> int:
    validate_slug(args.slug)
    destination = item_dir(args.slug)
    if destination.exists():
        print(f"错误：题目已存在：{destination}", file=sys.stderr)
        return 1
    destination.mkdir(parents=True)
    (destination / "references").mkdir()
    title = args.title or args.slug
    problem_template = (ITEM_TEMPLATE_ROOT / "problem.md").read_text(encoding="utf-8")
    config_template = (ITEM_TEMPLATE_ROOT / "config.toml").read_text(encoding="utf-8")
    (destination / "problem.md").write_text(
        problem_template.replace("{{TITLE}}", title), encoding="utf-8"
    )
    escaped_title = title.replace("\\", "\\\\").replace('"', '\\"')
    (destination / "config.toml").write_text(
        config_template.replace("{{TITLE}}", escaped_title), encoding="utf-8"
    )
    print(f"已创建：{destination.relative_to(ROOT)}")
    print("请填写 problem.md，核对 config.toml，然后把 ready = false 改为 ready = true。")
    return 0


def list_items() -> int:
    items = discover_items()
    if not items:
        print("队列为空。使用：./tools/conjecture_queue.sh add <slug> \"题目标题\"")
        return 0
    config = load_runner_config()
    print(
        f"{'SLUG':28} {'READY':5} {'ON':3} {'PRI':4} "
        f"{'ATTEMPTS':8} {'CONTRACT':17} {'MODE':16} STATUS"
    )
    for item in items:
        if item.get("invalid"):
            print(f"{item['slug']:28} ERROR: {item['invalid']}")
            continue
        slug = item["slug"]
        state = read_runtime_state(slug) if project_dir(slug).is_dir() else {"attempts": 0}
        print(
            f"{slug:28} {str(item['ready']):5} {str(item['enabled']):3} "
            f"{item['priority']:4} {int(state.get('attempts', 0)):8} "
            f"{item['search_contract']:17} "
            f"{effective_information_mode(item, config):16} "
            f"{read_status(slug)}"
        )
    return 0


def selected_state_items(slug: str | None) -> list[dict]:
    items = [item for item in discover_items() if not item.get("invalid")]
    if slug is None:
        return items
    validate_slug(slug)
    selected = [item for item in items if item["slug"] == slug]
    if not selected:
        raise ValueError(f"找不到题目：{slug}")
    return selected


def initialize_project_states(args: argparse.Namespace) -> int:
    created = 0
    for item in selected_state_items(args.slug):
        project = project_dir(item["slug"])
        if not project.is_dir():
            print(f"SKIP {item['slug']}: 项目尚未建立")
            continue
        if initialize_current_state(item, project, force_pending=True):
            created += 1
            print(f"CREATED {project / CURRENT_STATE_NAME}")
        else:
            print(f"EXISTS {project / CURRENT_STATE_NAME}")
    print(f"current-state initialized: {created}")
    return 0


def audit_project_states(args: argparse.Namespace) -> int:
    failed = False
    pending = 0
    checked = 0
    for item in selected_state_items(args.slug):
        project = project_dir(item["slug"])
        if not project.is_dir():
            print(f"SKIP {item['slug']}: 项目尚未建立")
            continue
        checked += 1
        issues = validate_current_state(project)
        if issues:
            failed = True
            for issue in issues:
                print(f"FAIL {item['slug']}: {issue}")
            continue
        content = (project / CURRENT_STATE_NAME).read_text(encoding="utf-8")
        if "- migration-status: `pending`" in content:
            pending += 1
            print(f"PENDING {item['slug']}: 下一研究回合先完成保守迁移")
        else:
            print(f"OK {item['slug']}")
    print(f"current-state checked={checked} pending={pending} failed={failed}")
    return 1 if failed else 0


def doctor() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        config = load_runner_config()
        print(f"runner.toml: OK ({RUNNER_CONFIG.relative_to(ROOT)})")
    except Exception as exc:  # diagnostic boundary
        print(f"runner.toml: FAIL ({exc})")
        return 1
    print(f"python: OK ({sys.executable}; {sys.version.split()[0]})")
    if os.environ.get("CONDA_DEFAULT_ENV") != "graphlab":
        warnings.append("当前 Python 不在 graphlab conda 环境中。")
    try:
        codex = locate_codex(config)
        result = subprocess.run(
            [codex, "--version"], capture_output=True, text=True, timeout=10, check=False
        )
        if result.returncode == 0:
            print(f"codex: OK ({codex}; {result.stdout.strip()})")
            login = subprocess.run(
                [codex, "login", "status"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if login.returncode == 0:
                login_message = (login.stdout or login.stderr).strip()
                print(f"codex login: OK ({login_message or 'authenticated'})")
            else:
                errors.append("Codex 尚未登录或登录状态检查失败")
        else:
            errors.append(f"codex --version 失败：{result.stderr.strip()}")
    except Exception as exc:
        errors.append(str(exc))
    tmux = shutil.which("tmux")
    if tmux:
        print(f"tmux: OK ({tmux})")
    else:
        errors.append("PATH 中找不到 tmux")
    items = discover_items()
    print(f"items: {len(items)}")
    missing_current_state = 0
    invalid_current_state = 0
    pending_current_state = 0
    for item in items:
        if item.get("invalid") or not project_dir(item["slug"]).is_dir():
            continue
        issues = validate_current_state(project_dir(item["slug"]))
        if issues == [f"missing {CURRENT_STATE_NAME}"]:
            missing_current_state += 1
        elif issues:
            invalid_current_state += 1
        else:
            content = (project_dir(item["slug"]) / CURRENT_STATE_NAME).read_text(
                encoding="utf-8"
            )
            if "- migration-status: `pending`" in content:
                pending_current_state += 1
    if missing_current_state:
        warnings.append(
            f"{missing_current_state} 个已有项目缺少 {CURRENT_STATE_NAME}；运行 state-init。"
        )
    if pending_current_state:
        warnings.append(
            f"{pending_current_state} 个项目的 {CURRENT_STATE_NAME} 等待保守迁移。"
        )
    if invalid_current_state:
        errors.append(
            f"{invalid_current_state} 个项目的 {CURRENT_STATE_NAME} 未通过结构或大小检查。"
        )
    mixed_requested = resolve_information_mode(config) == "mixed-isolated" or any(
        not item.get("invalid")
        and str(item.get("information_mode", "")).strip() == "mixed-isolated"
        for item in items
    )
    if mixed_requested:
        bubblewrap = shutil.which("bwrap")
        if bubblewrap:
            print(f"mixed isolation: OK ({bubblewrap})")
        else:
            errors.append("mixed-isolated 已启用，但 PATH 中找不到 bwrap")
    if not (ROOT / ".git" / "HEAD").is_file():
        warnings.append("当前工作区的 .git 不完整；队列可运行，但无法依赖 Git 审计。")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


def start_runner(args: argparse.Namespace) -> int:
    config = load_runner_config()
    slug = args.slug
    if slug:
        validate_slug(slug)
        matching = [item for item in discover_items() if item["slug"] == slug]
        if not matching:
            print(f"错误：找不到题目 {slug}", file=sys.stderr)
            return 2
        item = matching[0]
        if item.get("invalid") or not item.get("ready") or not item.get("enabled"):
            print(f"错误：题目 {slug} 当前不可运行。", file=sys.stderr)
            return 2
        if read_status(slug) not in RUNNABLE_STATUSES:
            print(
                f"错误：题目 {slug} 的状态为 {read_status(slug)}，不能自动继续。",
                file=sys.stderr,
            )
            return 2
    session = focus_session_name(config, slug) if slug else str(config["session_name"])
    holds = solution_holds()
    if holds:
        print(
            "错误：存在 solved-awaiting-human-verification，全局解答冻结中："
            + ", ".join(holds),
            file=sys.stderr,
        )
        print("请先审查并用 set-status 明确处理。", file=sys.stderr)
        return 3
    if slug and runner_lock_held():
        print("错误：公平队列正在运行；请先安全停止。", file=sys.stderr)
        return 1
    if not slug:
        focused = active_focus_slugs()
        if focused:
            print(
                "错误：以下单题 runner 正在运行：" + ", ".join(focused),
                file=sys.stderr,
            )
            return 1
    if runner_lock_held(slug):
        label = f"单题 runner {slug}" if slug else "队列 runner"
        print(f"{label} 已经在运行（可能是前台模式）。")
        return 0
    if doctor() != 0:
        print("错误：启动前健康检查未通过。", file=sys.stderr)
        return 1
    tmux = shutil.which("tmux")
    if not tmux:
        print("错误：PATH 中找不到 tmux。", file=sys.stderr)
        return 1
    existing = subprocess.run(
        [tmux, "has-session", "-t", session], capture_output=True, check=False
    )
    if existing.returncode == 0:
        print(f"队列 session 已存在：{session}")
        print(f"查看：tmux attach -t {session}")
        return 0
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    stop_file = focus_stop_file(slug) if slug else STOP_FILE
    stop_file.unlink(missing_ok=True)
    command = [sys.executable, str(Path(__file__).resolve()), "run"]
    if slug:
        command.extend(["--slug", slug])
    result = subprocess.run(
        [tmux, "new-session", "-d", "-s", session, shlex.join(command)], check=False
    )
    if result.returncode != 0:
        print("错误：无法启动 tmux 队列。", file=sys.stderr)
        return result.returncode
    if slug:
        print(f"已启动独立单题 runner：{slug}（{session}）")
    else:
        print(f"已启动重要猜想公平队列：{session}")
    print(f"查看实时输出：tmux attach -t {session}")
    print("退出查看但不中断：Ctrl-b，然后 d")
    if slug:
        print(f"安全停止：./tools/conjecture_queue.sh stop --slug {slug}")
    else:
        print("安全停止：./tools/conjecture_queue.sh stop")
    return 0


def stop_runner(args: argparse.Namespace) -> int:
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    if args.all:
        targets = [("公平队列", STOP_FILE)] + [
            (item["slug"], focus_stop_file(item["slug"]))
            for item in discover_items()
            if not item.get("invalid")
        ]
        for _, stop_file in targets:
            stop_file.write_text(f"requested_at={now_iso()}\n", encoding="utf-8")
        print("已请求停止全部 runner；各自会在当前 Codex 回合结束后退出。")
        return 0
    if args.slug:
        validate_slug(args.slug)
        stop_file = focus_stop_file(args.slug)
        label = f"单题 runner {args.slug}"
    else:
        stop_file = STOP_FILE
        label = "公平队列 runner"
    stop_file.write_text(f"requested_at={now_iso()}\n", encoding="utf-8")
    print(f"已请求停止{label}；它会在当前 Codex 回合结束后退出，不会强杀研究进程。")
    return 0


def show_status() -> int:
    config = load_runner_config()
    session = str(config["session_name"])
    tmux = shutil.which("tmux")
    running = False
    if tmux:
        running = (
            subprocess.run(
                [tmux, "has-session", "-t", session], capture_output=True, check=False
            ).returncode
            == 0
        )
    locked = runner_lock_held()
    if running:
        runner_status = f"running in tmux ({session})"
    elif locked:
        runner_status = "running in foreground or another supervisor"
    else:
        runner_status = f"not-running ({session})"
    print(f"runner: {runner_status}")
    print(f"stop-requested: {STOP_FILE.exists()}")
    focus_rows: list[str] = []
    for item in discover_items():
        if item.get("invalid"):
            continue
        slug = item["slug"]
        focus_session = focus_session_name(config, slug)
        in_tmux = bool(
            tmux
            and subprocess.run(
                [tmux, "has-session", "-t", focus_session],
                capture_output=True,
                check=False,
            ).returncode
            == 0
        )
        locked = runner_lock_held(slug)
        if in_tmux or locked or focus_stop_file(slug).exists():
            where = f"tmux:{focus_session}" if in_tmux else "foreground"
            focus_rows.append(
                f"{slug} ({where}, running={locked}, "
                f"stop-requested={focus_stop_file(slug).exists()})"
            )
    print("focused-runners: " + ("; ".join(focus_rows) if focus_rows else "none"))
    return list_items()


def watch_runner(args: argparse.Namespace) -> int:
    config = load_runner_config()
    session = (
        focus_session_name(config, args.slug)
        if args.slug
        else str(config["session_name"])
    )
    tmux = shutil.which("tmux")
    if not tmux:
        print("错误：PATH 中找不到 tmux。", file=sys.stderr)
        return 1
    exists = subprocess.run(
        [tmux, "has-session", "-t", session], capture_output=True, check=False
    )
    if exists.returncode != 0:
        print(f"错误：tmux session 不存在：{session}", file=sys.stderr)
        return 1
    return subprocess.run([tmux, "attach", "-t", session], check=False).returncode


def set_item_status(args: argparse.Namespace) -> int:
    validate_slug(args.slug)
    matching = [item for item in discover_items() if item["slug"] == args.slug]
    if not matching:
        print(f"错误：找不到题目 {args.slug}", file=sys.stderr)
        return 2
    ensure_project(matching[0])
    if args.status not in HUMAN_SETTABLE_STATUSES:
        print(f"错误：不允许人工设置状态 {args.status}", file=sys.stderr)
        return 2
    write_status(args.slug, args.status)
    print(f"{args.slug}: {args.status}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="重要猜想 Codex 长跑队列")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="建立一个老师填写的猜想条目")
    add.add_argument("slug")
    add.add_argument("title", nargs="?")
    sub.add_parser("list", help="列出全部猜想及状态")
    sub.add_parser("doctor", help="只读健康检查")
    state_init = sub.add_parser(
        "state-init", help=f"为已有项目补建 {CURRENT_STATE_NAME}，不覆盖现有文件"
    )
    state_init.add_argument("--slug", help="只处理指定题目；默认处理全部已有项目")
    state_audit = sub.add_parser(
        "state-audit", help=f"检查 {CURRENT_STATE_NAME} 的结构和大小"
    )
    state_audit.add_argument("--slug", help="只检查指定题目；默认检查全部已有项目")
    run = sub.add_parser("run", help="前台运行队列")
    run.add_argument("--once", action="store_true", help="只运行一个研究回合")
    run.add_argument("--dry-run", action="store_true", help="只展示下一回合，不调用 Codex")
    run.add_argument("--slug", help="只调度指定题目")
    start = sub.add_parser("start", help="在 tmux 中后台启动")
    start.add_argument("--slug", help="启动固定题目的独立 tmux runner")
    stop = sub.add_parser("stop", help="在当前回合结束后安全停止")
    stop_group = stop.add_mutually_exclusive_group()
    stop_group.add_argument("--slug", help="只停止指定单题 runner")
    stop_group.add_argument("--all", action="store_true", help="停止公平队列和全部单题 runner")
    sub.add_parser("status", help="显示 runner 和题目状态")
    watch = sub.add_parser("watch", help="进入队列的 tmux 实时终端")
    watch.add_argument("--slug", help="进入指定单题 runner 的 tmux")
    set_status = sub.add_parser("set-status", help="人工改变题目状态")
    set_status.add_argument("slug")
    set_status.add_argument("status", choices=sorted(HUMAN_SETTABLE_STATUSES))
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "add":
            return add_item(args)
        if args.command == "list":
            return list_items()
        if args.command == "doctor":
            return doctor()
        if args.command == "state-init":
            return initialize_project_states(args)
        if args.command == "state-audit":
            return audit_project_states(args)
        if args.command == "run":
            return run_loop(args)
        if args.command == "start":
            return start_runner(args)
        if args.command == "stop":
            return stop_runner(args)
        if args.command == "status":
            return show_status()
        if args.command == "watch":
            return watch_runner(args)
        if args.command == "set-status":
            return set_item_status(args)
    except (OSError, RuntimeError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
