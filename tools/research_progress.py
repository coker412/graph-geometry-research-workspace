#!/usr/bin/env python3
"""Evidence-bound progress assessments. This is not a mathematical verifier."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re


DIRECTORY = Path("notes/progress-assessment")
KINDS = {
    "frontier-advance": "核心缺口缩小",
    "route-elimination": "有效排除路线",
    "enabling-result": "工具或条件结果",
    "experimental-signal": "计算线索",
    "reformulation": "缺口重新表述",
    "repeat": "重复既有工作",
    "inconclusive": "本轮未得结论",
    "regression": "依赖失效，需回退",
    "candidate-solution": "完整候选，须认证",
}
LEVELS = {"conjecture", "experimental", "partial-result", "proof-draft",
          "agent-verified", "human-verified", "formalized"}
ASSESSMENT_LIMIT = 128 * 1024


def empty_result() -> dict:
    return {
        "claimed_kind": "inconclusive", "claim": "", "gap_after": "",
        "discharged_obligations": [], "new_obligations": [],
        "main_problem_effect": "", "scope_limitations": "",
        "evidence_level": "proof-draft", "evidence": [], "next_test": "",
    }


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def read(path: Path) -> dict:
    if path.stat().st_size > ASSESSMENT_LIMIT:
        raise ValueError(f"assessment file too large: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path.name}")
    return value


def write_new(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def local_file(project: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("evidence must be a project-relative path")
    path = (project / relative).resolve()
    if not path.is_relative_to(project.resolve()) or not path.is_file():
        raise ValueError(f"missing or out-of-project evidence: {relative}")
    return path


def text_fields(value: dict, names: tuple[str, ...]) -> None:
    for name in names:
        if not isinstance(value.get(name), str) or not value[name].strip():
            raise ValueError(f"missing text: {name}")


def round_dir(project: Path, round_id: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", round_id):
        raise ValueError("invalid round id")
    directory = project / DIRECTORY / round_id
    if not directory.resolve().is_relative_to(project.resolve()):
        raise ValueError("assessment directory escapes project")
    return directory


def prepare(project: Path, round_id: str, attempt: int, *, retrospective=False,
            baseline: Path | None = None) -> Path:
    if baseline is not None and not retrospective:
        raise ValueError("prospective baseline must be the live CURRENT_STATE.md")
    previous = summary(project)
    directory = round_dir(project, round_id)
    # Never reuse a completed/interrupted packet for a new launch.
    directory.mkdir(parents=True, exist_ok=False)
    baseline = baseline or project / "CURRENT_STATE.md"
    before = baseline.read_bytes()
    (directory / "BEFORE.md").write_bytes(before)
    write_new(directory / "START.json", {
        "schema_version": 1, "round_id": round_id, "attempt": attempt,
        "kind": "retrospective" if retrospective else "prospective",
        "baseline_source": str(baseline),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "before_sha256": digest(directory / "BEFORE.md"),
        "previous_decision": previous["decision"],
        "previous_family": (previous["latest"] or {}).get("family"),
        "previous_round_id": (previous["latest"] or {}).get("round_id"),
    })
    write_new(directory / "PLAN.json", {
        "author_id": "", "family_id": "", "obstacle_id": "",
        "mechanism": "", "gap_before": "", "acceptance_test": "",
        "reopening_basis": "none",
        "strategy_review": "none",
    })
    write_new(directory / "RESULT.json", empty_result())
    return directory


def seal_plan(project: Path, directory: Path) -> None:
    plan = read(directory / "PLAN.json")
    text_fields(plan, ("author_id", "family_id", "obstacle_id", "mechanism",
                       "gap_before", "acceptance_test", "reopening_basis"))
    start = read(directory / "START.json")
    if digest(directory / "BEFORE.md") != start["before_sha256"]:
        raise ValueError("baseline changed")
    if start["kind"] == "prospective":
        action = start.get("previous_decision", {}).get("action")
        if action == "switch-route" and plan["family_id"] == start.get("previous_family"):
            if plan["reopening_basis"].strip().casefold() == "none":
                raise ValueError("route change required: select another family or cite a new reopening mechanism file")
            local_file(project, plan["reopening_basis"])
        if action == "review-strategy":
            local_file(project, plan.get("strategy_review", ""))
    write_new(directory / "PLAN.lock.json", {
        "sha256": digest(directory / "PLAN.json"),
        "before_sha256": start["before_sha256"],
        "sealed_at": datetime.now(timezone.utc).isoformat(),
    })


def validate_result(result: dict) -> None:
    text_fields(result, ("claim", "gap_after", "main_problem_effect",
                         "scope_limitations", "next_test"))
    if result.get("claimed_kind") not in KINDS or result.get("evidence_level") not in LEVELS:
        raise ValueError("invalid outcome kind or evidence level")
    for key in ("discharged_obligations", "new_obligations", "evidence"):
        if not isinstance(result.get(key), list):
            raise ValueError(f"expected list: {key}")
        if not all(isinstance(x, str) and x.strip() for x in result[key]):
            raise ValueError(f"invalid entries: {key}")
    if not result["evidence"]:
        raise ValueError("need a proof, calculation, or exact failure record")


def sealed_bundle(project: Path, directory: Path) -> dict:
    start = read(directory / "START.json")
    lock = read(directory / "PLAN.lock.json")
    if digest(directory / "BEFORE.md") != start["before_sha256"]:
        raise ValueError("baseline changed")
    if lock["before_sha256"] != start["before_sha256"]:
        raise ValueError("plan baseline mismatch")
    if digest(directory / "PLAN.json") != lock["sha256"]:
        raise ValueError("plan changed after sealing; record a new plan instead")
    result = read(directory / "RESULT.json")
    validate_result(result)
    evidence = {name: digest(local_file(project, name)) for name in result["evidence"]}
    return {
        "start_sha256": digest(directory / "START.json"),
        "plan_sha256": lock["sha256"],
        "plan_lock_sha256": digest(directory / "PLAN.lock.json"),
        "result_sha256": digest(directory / "RESULT.json"),
        "evidence_sha256": evidence,
    }


def seal_result(project: Path, directory: Path) -> None:
    bundle = sealed_bundle(project, directory)
    write_new(directory / "RESULT.lock.json", bundle)
    write_new(directory / "REVIEW.template.json", {
        "reviewer_id": "", "reviewer_role": "independent-agent",
        "bundle": bundle, "verdict": "uncertain", "assessed_kind": "inconclusive",
        "baseline_comparison": "", "critical_path_effect": "",
        "scope_and_quantifiers": "", "new_burden_check": "",
        "same_obstacle_as_previous": False, "new_mechanism_verified": False,
        "whole_family_eliminated": False,
        "report": "", "report_sha256": "",
    })


def import_round_result(project: Path, directory: Path) -> None:
    """Derive a self-report view, never a review or mathematical certification.

    The queue calls this after V2 validation/application. Historical hand-written
    results and locks are immutable; absent progress metadata keeps the old path.
    The source result is itself hashed evidence, so changing it invalidates the view.
    """
    if any((directory / name).exists() for name in
           ("RESULT.lock.json", "REVIEW.template.json", "REVIEW.json")):
        raise ValueError("assessment already sealed or reviewed; preserve the original")
    target = directory / "RESULT.json"
    if read(target) != empty_result():
        raise ValueError("refusing to overwrite an authored RESULT.json")
    source = local_file(project, f".runtime/rounds/{directory.name}/ROUND_RESULT.json")
    value = read(source)
    packet = read(source.parent / "PACKET.json")
    if (value.get("schema_version") != 1 or value.get("round_id") != directory.name
            or value.get("packet_sha256") != packet.get("packet_sha256")
            or not packet.get("packet_sha256")):
        raise ValueError("round result identity or packet mismatch")
    meta = value.get("progress")
    if not isinstance(meta, dict):
        raise ValueError("ROUND_RESULT.progress must be an object")
    text_fields(meta, ("claimed_kind", "main_problem_effect", "scope_limitations", "evidence_level"))
    if meta["evidence_level"] not in {"conjecture", "experimental", "partial-result", "proof-draft"}:
        raise ValueError("derived self-report cannot claim an evidence upgrade")
    text_fields(value, ("summary", "active_gap", "next_target", "acceptance"))
    for entry in value["evidence"]:
        if digest(local_file(project, entry["file"])) != entry.get("sha256"):
            raise ValueError("source evidence changed before assessment import")
    result = {
        **{key: meta[key] for key in ("claimed_kind", "main_problem_effect", "scope_limitations", "evidence_level")},
        "claim": value["summary"], "gap_after": value["active_gap"],
        "discharged_obligations": value["closed_gaps"], "new_obligations": value["new_gaps"],
        "next_test": value["next_target"] + "\nAcceptance: " + value["acceptance"],
        "evidence": list(dict.fromkeys([entry["file"] for entry in value["evidence"]]
                                      + [str(source.relative_to(project.resolve()))])),
    }
    validate_result(result)
    for name in result["evidence"]:
        local_file(project, name)
    # Check the sealed plan before replacing even the empty generated template.
    start, lock = read(directory / "START.json"), read(directory / "PLAN.lock.json")
    if (digest(directory / "BEFORE.md") != start["before_sha256"]
            or lock["before_sha256"] != start["before_sha256"]
            or digest(directory / "PLAN.json") != lock["sha256"]):
        raise ValueError("baseline or sealed plan changed")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    seal_result(project, directory)


def assess(project: Path, directory: Path) -> dict:
    assessment = {"round_id": directory.name, "status": "unknown", "kind": None,
                  "attempt": 0, "prospective": False, "reason": "尚无完整评估"}
    try:
        start = read(directory / "START.json")
        if type(start.get("attempt")) is not int or start["attempt"] < 0:
            raise ValueError("invalid attempt number")
        assessment.update(attempt=start["attempt"], prospective=start["kind"] == "prospective")
        if (directory / "FINISH.json").is_file():
            finished = read(directory / "FINISH.json")
            if finished.get("return_code") != 0 or finished.get("timed_out"):
                assessment.update(status="execution-error", reason="本轮执行失败或超时，不据此判定数学停滞")
                return assessment
        plan = read(directory / "PLAN.json")
        assessment.update(family=plan.get("family_id", ""), obstacle=plan.get("obstacle_id", ""),
                          mechanism=plan.get("mechanism", ""))
        if not (directory / "RESULT.lock.json").is_file():
            assessment["reason"] = "本轮尚未提交或封存结果；不计作空转"
            return assessment
        bundle = sealed_bundle(project, directory)
        if bundle != read(directory / "RESULT.lock.json"):
            raise ValueError("result or evidence changed after sealing")
        result = read(directory / "RESULT.json")
        assessment.update(claimed_kind=result["claimed_kind"], claim=result["claim"],
                          gap_before=plan["gap_before"], gap_after=result["gap_after"],
                          evidence_level=result["evidence_level"], next_test=result["next_test"])
        assessment["result_signature"] = hashlib.sha256(json.dumps(
            {"result": result, "evidence": bundle["evidence_sha256"]},
            ensure_ascii=False, sort_keys=True,
        ).encode()).hexdigest()
        if not (directory / "REVIEW.json").is_file():
            assessment.update(status="self-report", reason="仅作者自评，尚无独立进展审查")
            return assessment
        review = read(directory / "REVIEW.json")
        text_fields(review, ("reviewer_id", "baseline_comparison", "critical_path_effect",
                             "scope_and_quantifiers", "new_burden_check", "report", "report_sha256"))
        if review.get("reviewer_role") not in {"independent-agent", "human"}:
            raise ValueError("progress assessment requires an independent reviewer")
        if review["reviewer_id"] == plan["author_id"]:
            raise ValueError("author cannot independently review their own progress")
        if review.get("bundle") != bundle:
            raise ValueError("review does not match frozen evidence")
        if digest(local_file(project, review["report"])) != review["report_sha256"]:
            raise ValueError("review report changed")
        for key in ("same_obstacle_as_previous", "new_mechanism_verified", "whole_family_eliminated"):
            if type(review.get(key)) is not bool:
                raise ValueError(f"expected boolean: {key}")
        if review.get("verdict") not in {"accept", "reject", "uncertain"}:
            raise ValueError("invalid review verdict")
        if review["verdict"] != "accept":
            assessment.update(status="disputed", reason=review["critical_path_effect"])
            return assessment
        kind = review.get("assessed_kind")
        if kind not in KINDS:
            raise ValueError("invalid reviewed outcome")
        if kind == "frontier-advance":
            if not result["discharged_obligations"]:
                raise ValueError("frontier advance must identify a discharged obligation")
            if result["evidence_level"] in {"conjecture", "experimental", "proof-draft"}:
                raise ValueError("unverified candidate/experiment cannot certify frontier advance")
        if kind == "route-elimination" and result["evidence_level"] in {"conjecture", "experimental", "proof-draft"}:
            raise ValueError("route elimination requires reviewed proof evidence")
        assessment.update(
            status="reviewed", kind=kind, reason=review["critical_path_effect"],
            same_obstacle=review["same_obstacle_as_previous"],
            new_mechanism=review["new_mechanism_verified"],
            whole_family_eliminated=review["whole_family_eliminated"],
            reviewer=review["reviewer_id"],
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        assessment.update(status="unknown", reason=str(exc))
    return assessment


def records(project: Path) -> list[dict]:
    base = project / DIRECTORY
    if not base.is_dir():
        return []
    directories = [d for d in base.iterdir()
                   if d.is_dir() and not d.is_symlink() and (d / "START.json").is_file()]
    def order(d):
        number = re.match(r"attempt-(\d+)", d.name)
        return (int(number[1]) if number else -1, d.name)
    rows = [assess(project, d) for d in sorted(directories, key=order)[-50:]]
    rows.sort(key=lambda r: (r["attempt"], r["round_id"]))
    seen = set()
    for row in rows:
        signature = row.get("result_signature")
        if signature and signature in seen and row.get("kind") == "frontier-advance":
            row.update(status="disputed", kind=None, reason="与近期结果及证据完全相同；不能重复记作缺口缩小")
        if signature:
            seen.add(signature)
    return rows


def decision(rows: list[dict], *, search_contract="either", stagnation_limit=0) -> dict:
    result = {"action": "assess", "no_frontier_rounds": 0, "repeat_rounds": 0,
              "reason": "缺少独立进展评估；不能判断推进或空转", "automatic_pause": False}
    if not rows:
        return result
    latest = rows[-1]
    if latest["status"] != "reviewed":
        result["reason"] = latest["reason"]
        return result
    kind = latest["kind"]
    # Only adjacent, completed prospective rounds count towards stagnation.
    # Unknown/unreviewed/missing rounds break the streak; they are not failures.
    expected = latest["attempt"]
    consecutive = []
    for row in reversed(rows):
        if (row["attempt"] != expected or row["status"] != "reviewed"
                or not row["prospective"]):
            break
        consecutive.append(row)
        expected -= 1
    for row in consecutive:
        if row["kind"] == "frontier-advance":
            break
        result["no_frontier_rounds"] += 1
    for row in consecutive:
        if row["kind"] not in {"repeat", "reformulation", "inconclusive"}:
            break
        if not row.get("same_obstacle") or row.get("new_mechanism"):
            break
        result["repeat_rounds"] += 1
    if kind in {"candidate-solution", "regression"}:
        result.update(action="certify", reason="冻结受影响依赖并认证；此工具不能认定主问题解决")
    elif (kind == "route-elimination" and latest.get("whole_family_eliminated")) or result["repeat_rounds"] >= 2:
        result.update(action="switch-route", reason="停止重复该机制；换方法族或提供可检验的重开依据")
    elif result["no_frontier_rounds"] >= 3:
        result.update(action="review-strategy", reason="连续三轮未缩小核心缺口；比较路线价值并建议是否暂停")
    elif kind == "frontier-advance":
        result.update(action="continue", reason="已有经审查的缺口缩小；执行下一项有界验收")
    elif kind == "route-elimination":
        result.update(action="bounded-test", reason="只排除了限定范围；停止该范围的重复搜索，测试尚未排除部分")
    else:
        result.update(action="bounded-test", reason="尚未确认核心缺口缩小；只安排一个能区分成败的测试")
    if search_contract == "affirmative-proof" or stagnation_limit == 0:
        result["constraint"] = "保持既定持续搜索承诺；换路线不等于停止整题，不自动设置 blocked"
    else:
        result["constraint"] = "整题停止仍需所有主要路线的结构性阻塞及既定再发散条件"
    return result


def summary(project: Path, **policy) -> dict:
    rows = records(project)
    # In-flight packets do not erase the most recent completed assessment.
    completed = [r for r in rows if any(
        (project / DIRECTORY / r["round_id"] / filename).is_file()
        for filename in ("RESULT.lock.json", "FINISH.json")
    )]
    latest = completed[-1] if completed else (rows[-1] if rows else None)
    return {"project": project.name, "latest": latest,
            "decision": decision(completed, **policy),
            "in_flight": [r["round_id"] for r in rows if r not in completed], "rounds": rows}


def finish(project: Path, directory: Path, return_code: int, timed_out: bool) -> None:
    write_new(directory / "FINISH.json", {
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "return_code": return_code, "timed_out": timed_out,
    })


def instruction(project: Path, directory: Path, previous: dict, *, round_result: bool = False,
                integration: bool = False) -> str:
    if integration:
        return f"""
进展包：{directory}。离线 PLAN 已封存，不重新计划或封存；汇合实际变化记入最终 RESULT.json，
逐条保留来源标签，引用稳定证明文件，不锁定 live CHECKPOINT、状态或台账。完成后执行
`python {Path(__file__).resolve()} seal-result --project {project} --round {directory.name}`。
不新增独立评审调用；缺少获授权的独立 REVIEW 时保留 self-report，不计已验证推进或停滞。
原计划、旧锁及旧证据不可覆盖；关键候选仍按认证协议处理。
"""
    delivery = (
        "结束只填写 ROUND_RESULT.json，另在 progress 对象填 claimed_kind、main_problem_effect、"
        "scope_limitations、evidence_level（至多 proof-draft）。runner 从同一份结果生成并封存评估 RESULT；"
        "不重复填写 RESULT.json，不手动 seal-result。"
        if round_result else
        "结束填写 RESULT.json 的实际变化、范围、义务和稳定证据，用同一命令的 seal-result 封存。"
    )
    return f"""
进展包：{directory}；上轮动作：{previous['decision']['action']}。
开工填写 PLAN.json（作者、稳定方法族/障碍 ID、机制、原缺口、验收）；执行
`python {Path(__file__).resolve()} seal-plan --project {project} --round {directory.name}`。
PLAN 封存后不改；临时转向写入结果。{delivery}
证明正文只写一次，评估引用它；勿锁定仍会改写的状态/台账/CHECKPOINT。
普通回合不新增独立评审调用：没有获授权的独立审查者则保留 self-report，不填 REVIEW，
不计作已验证推进或数学停滞。候选解、决定性反例、高风险共同依赖及等级升级仍按认证协议处理。
START.previous_round_id 非空时按需比较该轮封存结果与直接证据，缺件按未知，不臆断全历史。
switch-route 须换机制或在 reopening_basis 给重开报告路径；review-strategy 另在 strategy_review
给策略比较报告路径。两者由 seal-plan 校验；改名不能绕过原障碍。建议不自动停题。
mixed-isolated 离线只封存 PLAN；汇合后才封存最终 RESULT，保持来源隔离。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "seal-plan", "seal-result", "report"])
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--round")
    parser.add_argument("--attempt", type=int, default=0)
    parser.add_argument("--retrospective", action="store_true",
                        help="historical/corrected assessment; excluded from stagnation streaks")
    parser.add_argument("--baseline", help="project-relative historical baseline, retrospective only")
    parser.add_argument("--from-round-result", action="store_true",
                        help="seal-result: derive the empty assessment from this round's V2 result")
    args = parser.parse_args()
    if args.from_round_result and args.command != "seal-result":
        parser.error("--from-round-result requires seal-result")
    project = args.project.resolve()
    if not project.is_dir():
        parser.error("project directory does not exist")
    try:
        if args.command == "report":
            print(json.dumps(summary(project), ensure_ascii=False, indent=2))
        else:
            if not args.round:
                parser.error("--round is required")
            directory = round_dir(project, args.round)
            if args.command == "prepare":
                baseline = local_file(project, args.baseline) if args.baseline else None
                prepare(project, args.round, args.attempt,
                        retrospective=args.retrospective, baseline=baseline)
            elif args.command == "seal-plan":
                seal_plan(project, directory)
            else:
                if args.from_round_result:
                    import_round_result(project, directory)
                else:
                    seal_result(project, directory)
            print(directory)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
