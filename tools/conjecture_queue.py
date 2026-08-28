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
import threading
import time
import tomllib


ROOT = Path(__file__).resolve().parents[1]
QUEUE_ROOT = ROOT / "problems" / "important-conjectures"
ITEMS_ROOT = QUEUE_ROOT / "items"
RUNNER_CONFIG = QUEUE_ROOT / "runner.toml"
ITEM_TEMPLATE_ROOT = ROOT / "templates" / "important-conjecture"
RUNTIME_ROOT = ROOT / "agents" / "important-conjectures"
STOP_FILE = RUNTIME_ROOT / "STOP"
LOCK_FILE = RUNTIME_ROOT / "runner.lock"

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
        "web_search": True,
        "max_consecutive_runtime_failures": 3,
    }
    defaults.update(config)
    return defaults


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

    adopted_existing = project.exists() and not marker.is_file()
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
            "至少维护三个实质不同的方法族；每回合只深入推进一个方向。\n\n"
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
3. 项目中的 README.md、ideas.md、progress.md、verification-ledger.md、research-tree.md、proof-map.md
4. notes/ 中与当前缺口直接相关的材料

{information_mode}

{search_instruction}

本回合要求：
- 直接推进搜索承诺指定的目标；不得以问题可能公开为理由停止。
- 选择一个最有价值、可在本回合推进的具体动作。初始阶段先审计定义、量词、归一化和最小例子；随后至少形成三个实质不同的路线，但每回合只深入一个路线。
- 在 ideas.md 维护方法族登记表，按核心机制而不是表面措辞归类；记录信息来源、暴露范围、决定性子目标、证伪测试、结构性障碍和重开条件。若路线只是把主问题改写成等强引理，不视为取得进展。
- 若研究者已要求多智能体长跑且编排能力可用，按 research-workflow.md 动态分派：早期探索者使用不含热门路线和失败史的盲问题包；优先覆盖不足的方法族；候选证明另交对抗审计。子 Agent 只写独立分支产物，根 Agent 统一同步共享台账。
- 优先产生可复用的严格中间结果、反例测试、计算证据或精确缺口。{evidence_instruction}
- 推进要大胆：可以提出高风险引理、非常规构造和反例候选，并主动尝试修复失败路线。认证要保守：本回合新增的每一条数学推进都必须立即做与其强度相称的严格审查，明确检查定义、隐含假设、逻辑推出、反例、边界/除零/符号、外部定理假设以及是否只证明了弱化版本；把审查过程和结论写入 progress.md 或对应 notes 文件。
- 只允许修改本研究项目 {project}；不得修改题目源目录、其他项目、AGENTS.md 或工作区规则；不得提交 Git。
- 普通计算实验使用 graphlab 环境，记录命令、参数、随机种子和误差风险。
- 不得自动调用 Rethlas、网页端 Pro 或其他付费升级。若 Codex 层面同一精确缺口两次失败且适合升级，只准备完整交接稿，并把状态设为 needs-escalation-approval。
- 不写论文，不把计算观察写成定理，不把任何 Agent 结果升级为 human-verified。

证明冻结规则：
- 如果形成任何新的候选证明或严格中间结果，立即停止本回合的其他研究动作，逐项执行 AGENTS.md 的十条验证清单并主动寻找反例。审查完成前不得继续建立下游结论；证据等级最多标为 proof-draft。
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
2. 把本回合每一条新增数学推进、来源标签、隔离方式及十项检查结果登记到 verification-ledger.md；
3. 同步 README.md、ideas.md、research-tree.md、proof-map.md 中受本回合影响的状态；
4. 把证明草稿、计算或交接稿放入正确子目录；
5. 在 {project / '.conjecture-status'} 写入一个合法状态；
6. 最终答复简要列出本回合产物、检查、证据等级、未关闭缺口和下一步。
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


def codex_command(config: dict, project: Path, prompt: str, last_message: Path) -> list[str]:
    command = [
        locate_codex(config),
        "-C",
        str(project),
        "-s",
        "workspace-write",
        "-a",
        "never",
    ]
    if bool(config.get("web_search", True)):
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
            "--json",
            "--output-last-message",
            str(last_message),
            prompt,
        ]
    )
    return command


def append_history(slug: str, record: dict) -> None:
    history = RUNTIME_ROOT / "history.jsonl"
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    with history.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"slug": slug, **record}, ensure_ascii=False) + "\n")


def execute_attempt(item: dict, config: dict, dry_run: bool = False) -> int:
    slug = item["slug"]
    state = read_runtime_state(slug)
    attempt_number = int(state.get("attempts", 0)) + 1
    logs = RUNTIME_ROOT / "logs" / slug
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    event_log = logs / f"attempt-{attempt_number:04d}-{timestamp}.jsonl"
    last_message = logs / f"attempt-{attempt_number:04d}-{timestamp}-last.md"

    if dry_run:
        project = project_dir(slug)
        snapshot = project / "input-snapshots" / "<computed-at-run-time>"
        command = codex_command(config, project, "<研究提示词>", last_message)
        print(f"[dry-run] 将运行：{slug}")
        print(f"[dry-run] 项目：{project}")
        print(f"[dry-run] 快照：{snapshot}")
        print(f"[dry-run] 命令：{shlex.join(command[:-1])} <研究提示词>")
        return 0

    project = ensure_project(item)
    snapshot = create_input_snapshot(item, project)
    prompt = build_prompt(
        item, project, snapshot, web_search=bool(config.get("web_search", True))
    )
    logs.mkdir(parents=True, exist_ok=True)
    command = codex_command(config, project, prompt, last_message)
    write_status(slug, "pushing")
    started_at = now_iso()
    print(f"[{started_at}] 开始 {slug}，第 {attempt_number} 回合", flush=True)
    timed_out = False
    return_code = 1
    timeout_seconds = int(config.get("attempt_timeout_minutes", 90)) * 60
    with event_log.open("w", encoding="utf-8") as output:
        process = subprocess.Popen(
            command,
            cwd=project,
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
                print(line, end="", flush=True)

        output_thread = threading.Thread(target=pump_output, daemon=True)
        output_thread.start()
        try:
            return_code = process.wait(timeout=None if timeout_seconds <= 0 else timeout_seconds)
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

    state["attempts"] = attempt_number
    state["last_started_at"] = started_at
    state["last_finished_at"] = now_iso()
    state["last_return_code"] = return_code
    state["last_timed_out"] = timed_out
    state["last_event_log"] = str(event_log.relative_to(ROOT))
    state["last_message"] = str(last_message.relative_to(ROOT)) if last_message.exists() else None
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
            "event_log": state["last_event_log"],
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


def runner_lock_held() -> bool:
    if not LOCK_FILE.is_file():
        return False
    with LOCK_FILE.open("a", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(handle, fcntl.LOCK_UN)
    return False


def wait_for_rescan(seconds: int) -> bool:
    """Wait up to seconds; return early when a safe-stop request appears."""
    deadline = time.monotonic() + max(1, seconds)
    while time.monotonic() < deadline:
        if STOP_FILE.exists():
            return True
        time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))
    return STOP_FILE.exists()


def consume_stop_request() -> bool:
    if not STOP_FILE.exists():
        return False
    STOP_FILE.unlink(missing_ok=True)
    return True


def run_loop(args: argparse.Namespace) -> int:
    config = load_runner_config()
    if args.dry_run:
        return run_loop_body(args, config)

    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    with LOCK_FILE.open("w", encoding="utf-8") as lock_handle:
        try:
            fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("错误：另一个队列 runner 已经在运行。", file=sys.stderr)
            return 1
        STOP_FILE.unlink(missing_ok=True)
        return run_loop_body(args, config)


def run_loop_body(args: argparse.Namespace, config: dict) -> int:
    started = time.monotonic()
    max_wall_hours = float(config.get("max_wall_hours", 24))
    idle_cycles = 0
    while True:
        if consume_stop_request():
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
            if wait_for_rescan(int(config.get("idle_seconds", 60))):
                consume_stop_request()
                print("检测到停止请求；在空闲扫描边界退出。")
                return 0
            continue

        idle_cycles = 0
        for item in runnable:
            if consume_stop_request():
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
    print(
        f"{'SLUG':28} {'READY':5} {'ON':3} {'PRI':4} "
        f"{'ATTEMPTS':8} {'CONTRACT':17} STATUS"
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
            f"{item['search_contract']:17} {read_status(slug)}"
        )
    return 0


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
    print(f"items: {len(discover_items())}")
    if not (ROOT / ".git" / "HEAD").is_file():
        warnings.append("当前工作区的 .git 不完整；队列可运行，但无法依赖 Git 审计。")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


def start_runner() -> int:
    config = load_runner_config()
    session = str(config["session_name"])
    holds = solution_holds()
    if holds:
        print(
            "错误：存在 solved-awaiting-human-verification，全局解答冻结中："
            + ", ".join(holds),
            file=sys.stderr,
        )
        print("请先审查并用 set-status 明确处理。", file=sys.stderr)
        return 3
    if runner_lock_held():
        print("队列 runner 已经在运行（可能是前台模式）。")
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
    STOP_FILE.unlink(missing_ok=True)
    command = [sys.executable, str(Path(__file__).resolve()), "run"]
    result = subprocess.run(
        [tmux, "new-session", "-d", "-s", session, shlex.join(command)], check=False
    )
    if result.returncode != 0:
        print("错误：无法启动 tmux 队列。", file=sys.stderr)
        return result.returncode
    print(f"已启动重要猜想队列：{session}")
    print(f"查看实时输出：tmux attach -t {session}")
    print("退出查看但不中断：Ctrl-b，然后 d")
    print("安全停止：./tools/conjecture_queue.sh stop")
    return 0


def stop_runner() -> int:
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    STOP_FILE.write_text(f"requested_at={now_iso()}\n", encoding="utf-8")
    print("已请求停止；runner 会在当前 Codex 回合结束后退出，不会强杀研究进程。")
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
    return list_items()


def watch_runner() -> int:
    config = load_runner_config()
    session = str(config["session_name"])
    tmux = shutil.which("tmux")
    if not tmux:
        print("错误：PATH 中找不到 tmux。", file=sys.stderr)
        return 1
    exists = subprocess.run(
        [tmux, "has-session", "-t", session], capture_output=True, check=False
    )
    if exists.returncode != 0:
        print(f"错误：队列 tmux session 不存在：{session}", file=sys.stderr)
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
    run = sub.add_parser("run", help="前台运行队列")
    run.add_argument("--once", action="store_true", help="只运行一个研究回合")
    run.add_argument("--dry-run", action="store_true", help="只展示下一回合，不调用 Codex")
    run.add_argument("--slug", help="只调度指定题目")
    sub.add_parser("start", help="在 tmux 中后台启动")
    sub.add_parser("stop", help="在当前回合结束后安全停止")
    sub.add_parser("status", help="显示 runner 和题目状态")
    sub.add_parser("watch", help="进入队列的 tmux 实时终端")
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
        if args.command == "run":
            return run_loop(args)
        if args.command == "start":
            return start_runner()
        if args.command == "stop":
            return stop_runner()
        if args.command == "status":
            return show_status()
        if args.command == "watch":
            return watch_runner()
        if args.command == "set-status":
            return set_item_status(args)
    except (OSError, RuntimeError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
