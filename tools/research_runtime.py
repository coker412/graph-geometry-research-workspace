"""Bounded research packets, conservative round commits, and CLI telemetry.

No model calls occur in this module. Packet budgets are UTF-8 bytes, not
billing tokens. Evidence integrity is independent of automatic context loading.
"""
from __future__ import annotations

import datetime as dt
import codecs
import fcntl
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import tempfile

_TASK_SPEC = importlib.util.spec_from_file_location("runtime_tasks", Path(__file__).with_name("research_tasks.py"))
tasks = importlib.util.module_from_spec(_TASK_SPEC)
_TASK_SPEC.loader.exec_module(tasks)

_STATE_SPEC = importlib.util.spec_from_file_location("runtime_state_schema", Path(__file__).with_name("project_state.py"))
state_schema = importlib.util.module_from_spec(_STATE_SPEC)
_STATE_SPEC.loader.exec_module(state_schema)


PHASES = {
    'triage': ('medium', 'explore'),
    'research': ('high', 'explore'),
    'experiment': ('medium', 'computation'),
    'literature': ('medium', 'literature-check'),
    'audit': ('high', 'proof-audit'),
    'critical-audit': ('xhigh', 'proof-audit'),
    'stuck-escalation': ('xhigh', 'explore'),
}
BUDGET = dict(packet_target_bytes=32768, packet_hard_bytes=65536,
              max_evidence_slices=8, max_single_evidence_bytes=12288)
LEGACY_BUDGET_KEYS = {'packet_target_tokens': 'packet_target_bytes',
                      'packet_hard_tokens': 'packet_hard_bytes',
                      'max_single_evidence_tokens': 'max_single_evidence_bytes'}
MAX_RESULT_EVIDENCE = 8


def context_budget(overrides: dict | None = None) -> dict:
    """Historical *_tokens keys counted bytes too; preserve their numeric values."""
    if overrides is None:
        overrides = {}
    if not isinstance(overrides, dict):
        raise ValueError('context budget must be an object')
    normalized = {}
    for key, value in overrides.items():
        canonical = LEGACY_BUDGET_KEYS.get(key, key)
        if canonical not in BUDGET:
            raise ValueError('unknown context budget fields')
        if canonical in normalized and normalized[canonical] != value:
            raise ValueError('conflicting legacy and byte budget values')
        normalized[canonical] = value
    budget = {**BUDGET, **normalized}
    if any(type(v) is not int or v <= 0 for v in budget.values()):
        raise ValueError('context budgets must be positive integers')
    if budget['packet_target_bytes'] > budget['packet_hard_bytes']:
        raise ValueError('packet target exceeds hard budget')
    return budget
PROTECTED = ('CURRENT_STATE.md', 'progress.md', 'verification-ledger.md',
             'proof-map.md', 'ideas.md', 'research-tree.md', '.conjecture-status', '.runtime/evidence.json', tasks.TASK_FILE, tasks.ROUTE_FILE)
LEVELS = {'conjecture', 'experimental', 'partial-result', 'proof-draft'}
SOURCES = {'internal-offline', 'provided-source', 'web-source', 'mixed'}
STATUS = {'pushing', 'needs-human-input', 'needs-human-review',
          'needs-escalation-approval', 'blocked', 'solved-awaiting-human-verification'}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> str | None:
    if not path.exists():
        return None
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temp, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temp.unlink(missing_ok=True)


def write_json(path: Path, data: dict) -> None:
    atomic(path, (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def read_json(path: Path, limit: int = 128 * 1024) -> dict:
    if path.stat().st_size > limit:
        raise ValueError(f'JSON too large: {path}')
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f'expected JSON object: {path}')
    return value


def local(project: Path, name: str, *, exists: bool = True) -> Path:
    if not isinstance(name, str) or not name or Path(name).is_absolute() or any(ord(c) < 32 for c in name):
        raise ValueError('expected project-relative path')
    path = project / name
    if '..' in Path(name).parts or not path.resolve().is_relative_to(project.resolve()):
        raise ValueError(f'path escapes project: {name}')
    # Reject aliases even within the project, to make manifests unambiguous.
    if any(p.is_symlink() for p in (path, *path.parents) if p != project.parent):
        raise ValueError(f'symlink not allowed: {name}')
    if exists and not path.is_file():
        raise ValueError(f'missing evidence: {name}')
    return path


def phase_config(config: dict, item: dict, state: dict | None = None) -> dict:
    phase = str(item.get('config', {}).get('phase', config.get('phase', 'research')))
    if phase not in PHASES:
        raise ValueError(f'unknown phase: {phase}')
    models = config.get('phase_model', {})
    if not isinstance(models, dict):
        raise ValueError('phase_model must be a table')
    model = str(models.get(phase, config.get('model', ''))).strip()
    efforts = config.get('phase_effort', {})
    if not isinstance(efforts, dict):
        raise ValueError('phase_effort must be a table')
    effort = efforts.get(phase, config.get('reasoning_effort', 'high')
                         if phase == 'research' else PHASES[phase][0])
    if effort not in {'medium', 'high', 'xhigh'}:
        raise ValueError(f'unsupported effort: {effort}')
    if effort == 'xhigh' and phase not in {'critical-audit', 'stuck-escalation'}:
        raise ValueError('xhigh requires critical-audit or stuck-escalation phase')
    return {**config, 'phase': phase, 'model': model, 'reasoning_effort': effort}


def evidence_slice(project: Path, spec: dict, mode: str, budget: dict | None = None,
                   *, capture_limit: int | None = None) -> tuple[str, dict]:
    # No budget means integrity-only validation, not permission to inline everything.
    limit = context_budget(budget)['max_single_evidence_bytes'] if budget is not None else None
    if not isinstance(spec, dict):
        raise ValueError('evidence entry must be an object')
    path = local(project, spec.get('file'))
    start, end = spec.get('start'), spec.get('end')
    if type(start) is not int or type(end) is not int or not 1 <= start <= end:
        raise ValueError('evidence requires 1-based start <= end')
    source = spec.get('source')
    if source not in SOURCES or (mode == 'offline' and source != 'internal-offline'):
        raise ValueError('offline packet requires explicit internal-offline evidence')
    expected = spec.get('sha256')
    if not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
        raise ValueError('evidence requires full-file sha256')
    if digest(path) != expected:
        raise ValueError(f'stale evidence hash: {spec["file"]}')
    selected = []
    count = 0
    number = 1
    last_seen = 0
    captured = True
    slice_digest = hashlib.sha256()
    file_digest = hashlib.sha256()
    decoder = io.IncrementalNewlineDecoder(codecs.getincrementaldecoder('utf-8')(), translate=True)

    def consume(decoded: str) -> None:
        nonlocal number, last_seen, count, captured
        parts = decoded.split('\n')
        for index, piece in enumerate(parts):
            if number > end:
                break
            if index < len(parts) - 1:
                piece += '\n'
            if not piece:
                continue
            last_seen = number
            if number >= start:
                encoded = piece.encode()
                slice_digest.update(encoded)
                count += len(encoded)
                if limit is not None and count > limit:
                    raise ValueError(f'evidence slice exceeds budget: {spec["file"]}')
                if capture_limit is not None and count > capture_limit:
                    selected.clear()
                    captured = False
                if captured:
                    selected.append(piece)
            if piece.endswith('\n'):
                number += 1

    # Hash exactly the bytes supplied to the decoder, including a huge single
    # line. Separate re-reads can miss an in-place edit that is later restored.
    with path.open('rb') as handle:
        for raw in iter(lambda: handle.read(65536), b''):
            file_digest.update(raw)
            if number <= end:
                consume(decoder.decode(raw))
        if number <= end:
            consume(decoder.decode(b'', final=True))
    if file_digest.hexdigest() != expected:
        raise ValueError(f'evidence changed while reading: {spec["file"]}')
    if digest(local(project, spec['file'])) != expected:
        raise ValueError(f'evidence changed while reading: {spec["file"]}')
    if last_seen < end:
        raise ValueError(f'evidence range beyond EOF: {spec["file"]}')
    purpose = spec.get('purpose')
    if not isinstance(purpose, str) or not purpose.strip() or '\n' in purpose:
        raise ValueError('evidence purpose required')
    body = ''.join(selected)
    rendered = (f'### {spec["file"]}#L{start}-L{end}\nSource: {source}; {purpose}\n\n{body}'
                if captured else '')
    return (rendered, {**spec, 'slice_sha256': slice_digest.hexdigest(), 'bytes': count})


def compile_packet(root: Path, project: Path, problem: Path, config: dict,
                   item: dict, mode: str, extra: str = '') -> tuple[str, dict]:
    phase = config.get('phase', 'research')
    task_version = config.get('research_task_version', 0)
    if type(task_version) is not int or task_version not in {0, 1}:
        raise ValueError('research_task_version must be 0 or 1')
    task_state = tasks.read(project, tasks.TASK_FILE)
    if task_state.get('active') and not task_version:
        raise ValueError('active research task requires research_task_version=1')
    if phase == 'literature' and mode != 'connected':
        raise ValueError('literature phase requires explicit connected information mode')
    budget = context_budget(config.get('context_budget', {}))
    parts = []
    sizes = {}
    for label, path in (
        ('constitution', root / 'AGENTS.md'),
        ('research-core', root / 'agents/core/research-core.md'),
        ('protocol', root / f'agents/protocols/{PHASES[phase][1]}.md'),
        ('queue-core', root / 'agents/core/queue-core.md'),
        ('result-contract', root / 'agents/protocols/round-result.md'),
        ('problem', problem), ('state', project / 'CURRENT_STATE.md'),
    ):
        if path.stat().st_size > budget['packet_hard_bytes']:
            raise ValueError(f'packet component exceeds budget: {label}; select evidence slices')
        body = path.read_text(encoding='utf-8')
        sizes[label] = len(body.encode())
        parts.append(f'## {label}\n\n{body}')
    # Keep shared instructions before project-specific values so consecutive
    # packets retain an identical prefix. This does not guarantee server caching.
    stable_parts = parts[:5]
    parts = parts[5:]
    evidence = []
    seen_slices = {}
    evidence_saved_bytes = 0
    evidence_rendered_bytes = 0
    evidence_parts = []
    deferred = []
    inline_count = 0
    manifest = local(project, '.runtime/evidence.json', exists=False)
    if manifest.exists():
        specs = read_json(manifest).get('evidence')
        if not isinstance(specs, list) or len(specs) > MAX_RESULT_EVIDENCE:
            raise ValueError('invalid evidence list or too many slices')
        for spec in specs:
            body, record = evidence_slice(project, spec, mode,
                capture_limit=budget['max_single_evidence_bytes'])
            reference = (f'### {spec["file"]}#L{spec["start"]}-L{spec["end"]}\n'
                         f'Source: {spec["source"]}; SHA256: {spec["sha256"]}\n'
                         f'Purpose: {spec["purpose"]}\n'
                         'NOT INLINED: read this exact hashed range before using it as evidence. '
                         'The complete proof is preserved; this pointer is not a proof summary.\n')
            if record['bytes'] > budget['max_single_evidence_bytes'] or inline_count >= budget['max_evidence_slices']:
                body = reference
                record['inlined'] = False
                deferred.append({**spec, 'reason': 'automatic loading slice/count budget'})
            else:
                inline_count += 1
                record['inlined'] = True
            # Validate every entry before deduplication, including source and hash.
            # Keep all records/purposes; only reuse identical evidence text.
            identity = (spec['file'], spec['start'], spec['end'],
                        spec['sha256'], spec['source'])
            if record['inlined'] and identity in seen_slices:
                reuse = (f'### {spec["file"]}#L{spec["start"]}-L{spec["end"]}\n'
                             f'Source: {spec["source"]}; {spec["purpose"]}\n\n'
                             f'Reuse evidence entry {seen_slices[identity]} above (same range and hash).')
                saving = len(body.encode()) - len(reuse.encode())
                if saving > 0:
                    body = reuse
                    evidence_saved_bytes += saving
            elif record['inlined']:
                seen_slices[identity] = len(evidence) + 1
            evidence_rendered_bytes += len(body.encode())
            evidence_parts.append((len(parts), record, reference))
            parts.append(body)
            evidence.append(record)
    else:
        parts.append('## Evidence selection\nNo slice manifest yet. Follow exact CURRENT_STATE IDs; '
                     'read only the needed ranges. Return hashed evidence slices for the next round. '
                     'Missing historical evidence is unknown, not disproved or certified.')
    header = (f'## Round context\nPhase: {phase}\nInformation mode: {mode}\n'
              f'Search contract: {item.get("search_contract", "either")}\n'
              f'Stagnation threshold: {item.get("stagnation_rounds_before_blocked", 0)}\n'
              f'Project: {project}\nProblem SHA256: {digest(problem)}\n'
              'The state section supplies the objective, gap and next action. '
              'Included protocols are already loaded; do not re-read the full workflow.\n')
    if task_version:
        header += ('Research task protocol: 1. One CLI call is an execution step, not task completion.\n'
                   'Preserve the sealed task objective; actually test the bridge to the main problem.\n'
                   'Read .runtime/routes.json by route ID when selecting or reopening a recorded route.\n'
                   'Task state (author reports, not certification):\n'
                   + json.dumps({k: task_state.get(k) for k in ('active', 'totals')}, ensure_ascii=False) + '\n')
    sizes['evidence'] = sum(e['bytes'] for e in evidence)
    sizes['round-instructions'] = len(extra.encode())
    prefix = '# Research packet\n\n' + '\n\n'.join(stable_parts) + '\n\n'
    def assemble():
        return prefix + header + '\n\n'.join(parts) + '\n\n' + extra
    text = assemble()
    size = len(text.encode())
    # Defer whole ranges, never cut a proof in the middle or drop its reference.
    # Reverse order preserves the priority chosen by the researcher in the manifest.
    for index, record, reference in reversed(evidence_parts):
        if size <= budget['packet_hard_bytes']:
            break
        if record['inlined'] and len(parts[index].encode()) > len(reference.encode()):
            evidence_rendered_bytes -= len(parts[index].encode()) - len(reference.encode())
            parts[index] = reference
            record['inlined'] = False
            deferred.append({k: record[k] for k in ('file', 'start', 'end', 'sha256', 'purpose', 'source')} |
                            {'reason': 'total packet byte budget'})
            text = assemble()
            size = len(text.encode())
    if size > budget['packet_hard_bytes']:
        raise ValueError(f'packet exceeds byte budget even with evidence references: {size} > '
                         f'{budget["packet_hard_bytes"]}; reduce non-evidence working state explicitly')
    # Route discovery uses spare space only: never evict selected proof evidence.
    route_directory = {}
    if task_version:
        preview, route_directory = tasks.route_preview(
            project, mode, min(8192, max(0, budget['packet_hard_bytes'] - size - 2)))
        sizes['route-directory'] = len(preview.encode())
        if preview:
            text += '\n\n' + preview
            size = len(text.encode())
    warnings = []
    if size > budget['packet_target_bytes']:
        warnings.append('packet above soft target')
    if deferred:
        warnings.append('some evidence is referenced, not inlined; read exact ranges before use')
    if route_directory.get('omitted'):
        warnings.append('route directory is partial; consult source-eligible records by ID as needed')
    if sizes['state'] > 8192:
        warnings.append('legacy CURRENT_STATE above 8 KiB; next V2 result must fit 12 KiB')
    return text, dict(research_task_version=task_version, bytes=size, budget_unit='utf8-bytes',
                      token_upper_estimate=size, token_method='utf8-bytes-upper-bound',
                      components_bytes=sizes, evidence=evidence, warnings=warnings,
                      phase=phase, information_mode=mode, problem_sha256=digest(problem),
                      packet_sha256=sha(text.encode()), budget=budget,
                      stable_prefix_bytes=len(prefix.encode()),
                      stable_prefix_sha256=sha(prefix.encode()),
                      evidence_rendered_bytes=evidence_rendered_bytes,
                      route_directory=route_directory,
                      deferred_evidence=deferred,
                      evidence_dedup_saved_bytes=evidence_saved_bytes)


def prepare_round(project: Path, directory: Path, packet: str, metadata: dict) -> None:
    directory.mkdir(parents=True, exist_ok=False)
    atomic(directory / 'RESEARCH_PACKET.md', packet.encode())
    write_json(directory / 'PACKET.json', metadata)
    baseline = {name: digest(local(project, name, exists=False)) for name in PROTECTED}
    write_json(directory / 'BASELINE.json', baseline)


def required_text(value: dict, key: str) -> str:
    text = value.get(key)
    if not isinstance(text, str) or not text.strip() or len(text.encode()) > 8192:
        raise ValueError(f'missing or oversized text: {key}')
    return text


def validate_result(project: Path, directory: Path, value: dict) -> None:
    if (type(value.get('schema_version')) is not int or value['schema_version'] != 1
            or value.get('round_id') != directory.name):
        raise ValueError('wrong result schema or round id')
    if value.get('packet_sha256') != read_json(directory / 'PACKET.json')['packet_sha256']:
        raise ValueError('result does not match this research packet')
    for key in ('summary', 'active_gap', 'next_target', 'acceptance', 'checks'):
        required_text(value, key)
    if value.get('round_status') not in {'progress', 'no-progress', 'candidate-solution', 'blocked'}:
        raise ValueError('unknown round_status')
    if value.get('audit') is not None and not isinstance(value['audit'], dict):
        raise ValueError('audit must be an object when supplied')
    for key in ('active_gap', 'next_target', 'acceptance'):
        if '\n' in value[key]:
            raise ValueError(f'{key} must be a single-line state field')
    status = value.get('queue_status', 'pushing')
    if status not in STATUS:
        raise ValueError('invalid or human-only queue status')
    if status == 'solved-awaiting-human-verification' and value['round_status'] != 'candidate-solution':
        raise ValueError('global freeze requires candidate-solution')
    # Stagnation certificates require human interpretation; do not auto-block.
    if status == 'blocked':
        raise ValueError('use needs-human-review for a stagnation certificate')
    evidence = value.get('evidence')
    claims = value.get('new_claims')
    if not isinstance(evidence, list) or not isinstance(claims, list):
        raise ValueError('evidence and new_claims must be lists')
    if len(evidence) > MAX_RESULT_EVIDENCE or len(claims) > 32:
        raise ValueError('too many evidence slices or claims')
    packet = read_json(directory / 'PACKET.json')
    mode = packet['information_mode']
    for spec in evidence:
        evidence_slice(project, spec, mode, capture_limit=0)
    ids = set()
    ledger_path = local(project, 'verification-ledger.md')
    ledger = ledger_path.read_text()
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError('claim must be an object')
        cid = required_text(claim, 'id')
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,79}', cid) or cid in ids:
            raise ValueError('invalid or duplicate claim id')
        if re.search(r'(?<![\w.-])' + re.escape(cid) + r'(?![\w.-])', ledger):
            raise ValueError(f'existing claim needs explicit review, cannot overwrite: {cid}')
        ids.add(cid)
        for key in ('statement', 'assumptions', 'checks', 'dependencies'):
            required_text(claim, key)
        if claim.get('status') not in LEVELS:
            raise ValueError('automatic writer cannot certify claims')
        if claim.get('source') not in SOURCES or (mode == 'offline' and claim['source'] != 'internal-offline'):
            raise ValueError('invalid claim provenance')
        if claim.get('statement_file') not in {spec['file'] for spec in evidence}:
            raise ValueError('claim requires a hashed evidence slice')
    tasks.validate(project, directory, packet, value)
    for key in ('active_routes', 'blocked_routes', 'new_gaps', 'closed_gaps'):
        values = value.get(key, [])
        if not isinstance(values, list) or len(values) > 32 or any(
            not isinstance(x, str) or '\n' in x or len(x) > 500 for x in values
        ):
            raise ValueError(f'invalid {key}')
    if value['round_status'] == 'candidate-solution':
        if status != 'solved-awaiting-human-verification':
            raise ValueError('candidate-solution must explicitly request the global freeze')
        scope = value.get('solution_scope')
        packet = read_json(directory / 'PACKET.json')
        if not isinstance(scope, dict):
            raise ValueError('candidate requires an explicit full-problem solution_scope')
        if scope.get('kind') != 'full-original-problem':
            raise ValueError('candidate-solution is reserved for the full original problem')
        if scope.get('problem_sha256') != packet.get('problem_sha256'):
            raise ValueError('candidate scope must bind the immutable formal problem snapshot')
        if scope.get('unresolved_parts') != []:
            raise ValueError('full-problem candidate cannot retain unresolved original parts')
        required_text(scope, 'coverage_statement')
        audit = value.get('audit')
        if not isinstance(audit, dict):
            raise ValueError('candidate requires audit record')
        if audit.get('checks') != ['pass'] * 10:
            raise ValueError('candidate requires ten explicit audit checks')
        if audit.get('report_file') not in {spec['file'] for spec in evidence}:
            raise ValueError('candidate requires hashed audit report')
        if not any(c['status'] == 'proof-draft' for c in claims):
            raise ValueError('candidate requires a proof-draft claim')


def section_replace(text: str, heading: str, body: str) -> str:
    chinese = {'## Current status': '## 当前状态',
               '## Current mathematical status': '## 当前数学状态',
               '## Active proof frontier': '## 当前证明缺口',
               '## Next bounded round': '## 下一有界回合',
               '## Evidence pointers': '## 证据指针'}
    names = [heading, chinese.get(heading, heading)]
    pattern = re.compile(r'^(?:' + '|'.join(map(re.escape, names)) + r')[ \t]*\n.*?(?=^## |\Z)', re.M | re.S | re.I)
    matches = list(pattern.finditer(text))
    display = matches[0].group().splitlines()[0] if matches else heading
    replacement = display + '\n\n' + body.strip() + '\n\n'
    if pattern.search(text):
        # Only these mutable frontier sections are replaced. The journal preserves
        # all old versions, including duplicate sections created by the old writer.
        used = False
        def replace(match):
            nonlocal used
            if used:
                return ''
            used = True
            return replacement
        return pattern.sub(replace, text)
    return text.rstrip() + '\n\n' + replacement


def render_updates(project: Path, directory: Path, result: dict) -> dict[str, bytes]:
    task_updates, task_note = tasks.render(project, directory, result)
    status = result.get('queue_status', 'pushing')
    if result['round_status'] == 'candidate-solution':
        status = 'solved-awaiting-human-verification'
    stamp = dt.datetime.now().astimezone().isoformat(timespec='seconds')
    state = local(project, 'CURRENT_STATE.md').read_text()
    # Normalize only frontier/index aliases. Inherited mathematical prose is kept.
    aliases = {
        'Active gap': 'Active proof frontier',
        'Current minimum gap and active routes': 'Active proof frontier',
        'Frontier and next bounded round': 'Active proof frontier',
        'Next bounded round and acceptance': 'Next bounded round',
        'Direct evidence pointers': 'Evidence pointers',
        'Precise evidence pointers': 'Evidence pointers',
        'Exact evidence pointers': 'Evidence pointers',
    }
    for old, new in aliases.items():
        state = re.sub(r'^## ' + re.escape(old) + r'[ \t]*$', '## ' + new, state, flags=re.M | re.I)
    # Keep inherited scope and evidence ceiling verbatim, but refresh the short
    # mathematical index. Evidence and certification remain in the ledger.
    state = re.sub(r'^- updated-at:.*$', '- updated-at: ' + stamp, state, flags=re.M)
    state = re.sub(r'^- queue-status:.*$', f'- queue-status: `{status}`', state, flags=re.M)
    claim_refs = ', '.join(
        f'`{c["id"]}` (`{c["status"]}`, `{c["statement_file"]}`)'
        for c in result['new_claims']
    ) or '本轮无新增声明'
    certification = (
        '原问题完整候选，仅作者自查，尚待独立认证与研究者复核'
        if result['round_status'] == 'candidate-solution'
        else '新增声明保留各自台账等级；候选与审计状态见本轮摘要及直接证据'
    )
    state = section_replace(state, '## Current mathematical status',
        f'- 本轮摘要：{result["summary"]}\n'
        f'- 新增声明：{claim_refs}\n'
        f'- 认证边界：{certification}。\n'
        '- 继承结果与精确假设以 `verification-ledger.md` 及其直接证据为准；本索引不提高证据等级。')
    state = section_replace(state, '## Active proof frontier',
        f'- 当前缺口：{result["active_gap"]}\n'
        f'- 活动路线：{", ".join(result.get("active_routes", []))}\n'
        f'- 受阻路线：{", ".join(result.get("blocked_routes", []))}')
    state = section_replace(state, '## Next bounded round',
        f'- 目标：{result["next_target"]}\n- 验收：{result["acceptance"]}\n' + task_note)
    pointers = [f'- `{e["file"]}#L{e["start"]}-L{e["end"]}`; sha256={e["sha256"]}; {e["purpose"]}'
                for e in result['evidence']]
    pointers += [f'- 新声明 `{c["id"]}`：`{c["status"]}`；见 verification-ledger.md 与 `{c["statement_file"]}`'
                 for c in result['new_claims']]
    pointers.append(f'- 本轮结果：`{directory.relative_to(project)}/ROUND_RESULT.json`；'
                    '继承事实保留原台账与证据记录。')
    state = section_replace(state, '## Evidence pointers', '\n'.join(pointers))
    if len(state.encode()) > 12288 or len(state.splitlines()) > 300:
        raise ValueError('new CURRENT_STATE exceeds 12 KiB/300 lines; revise working set explicitly')
    issues = state_schema.validate_content(state, max_bytes=state_schema.NEW_MAX_BYTES)
    if issues:
        raise ValueError('invalid rendered CURRENT_STATE: ' + '; '.join(issues))
    marker = f'<!-- runtime-round:{directory.name} -->'
    summary = (f'\n\n{marker}\n## {stamp} ({directory.name})\n\n'
               f'{result["summary"]}\n\nChecks: {result["checks"]}\n\n'
               f'Gap: {result["active_gap"]}\nNext: {result["next_target"]}\n'
               f'Result: `{directory.relative_to(project)}/ROUND_RESULT.json`\n')
    proof_map = local(project, 'proof-map.md').read_text()
    candidate_files = ', '.join(
        f'`{c["statement_file"]}`' for c in result['new_claims']
        if c['status'] == 'proof-draft'
    ) or 'none newly reported; consult the ledger for inherited drafts'
    audit_file = (result.get('audit') or {}).get('report_file', 'no new whole-proof audit')
    audit_ref = (f'`{audit_file}`' if audit_file != 'no new whole-proof audit'
                 else 'no new whole-proof audit')
    # Keep old nested frontier records outside the replaceable latest-status section.
    proof_map = proof_map.replace('### Frontier report (not certification)', '## Frontier report (not certification)')
    proof_map = section_replace(proof_map, '## Current status',
        f'- Target status: {certification}.\n'
        f'- Newly reported claims: {claim_refs}\n'
        f'- Current minimum gap: {result["active_gap"]}\n'
        f'- Candidate/evidence files: {candidate_files}\n'
        f'- Latest whole-proof audit: {audit_ref}')
    tree_path = local(project, 'research-tree.md', exists=False)
    tree = tree_path.read_text() if tree_path.exists() else '# Research Tree\n'
    tree = section_replace(tree, '## Current status',
        f'- 当前记录：`{directory.relative_to(project)}/ROUND_RESULT.json`；作者回传，不构成认证。\n'
        f'- 本轮摘要：{result["summary"]}\n'
        f'- 活动路线：{"; ".join(result.get("active_routes", [])) or "本轮未报告；不表示历史路线不存在"}\n'
        f'- 受阻路线：{"; ".join(result.get("blocked_routes", [])) or "本轮未报告"}\n'
        f'- 当前缺口：{result["active_gap"]}\n'
        f'- 下一步：{result["next_target"]}\n'
        '- 继承路线与结果保留原范围和等级；以下历史节点不自动构成当前证明。')
    # Replace only the original empty diagrams. Never regenerate an authored
    # dependency graph from route names or infer proof edges from free text.
    tree = tree.replace('```mermaid\nflowchart TD\n    P0["P0 主问题<br/>conjecture"]\n```',
        '当前路线、受阻机制和缺口见上方状态；结构增量见下方登记。\n'
        '尚未登记的路线关系保持未知，不能由单个主问题节点冒充研究树。')
    if result['new_claims']:
        body = '仅列本轮声明及作者报告的依赖；完整历史与认证见 `verification-ledger.md`。\n'
        for claim in result['new_claims']:
            body += (f'\n- `{claim["id"]}`（`{claim["status"]}`）：{claim["statement"]}\n'
                     f'  - 假设：{claim["assumptions"]}\n'
                     f'  - 报告的依赖：{claim["dependencies"]}\n'
                     f'  - 直接证据：`{claim["statement_file"]}`\n')
        proof_map = section_replace(proof_map, '## 本轮声明的依赖（作者自报）', body)
        proof_map = proof_map.replace(
            '```mermaid\nflowchart BT\n    T0["T0 主猜想<br/>conjecture"]\n```',
            '具体节点及其依赖见「本轮声明的依赖」和验证台账。\n'
            '当前缺口尚未关闭时，不存在由这些局部结果到主结论的已证箭头。')
    updates = {'CURRENT_STATE.md': state.encode(), '.conjecture-status': (status + '\n').encode(),
               'progress.md': local(project, 'progress.md').read_bytes() + summary.encode(),
               '.runtime/evidence.json': (json.dumps({'evidence': result['evidence']}, ensure_ascii=False, indent=2) + '\n').encode(),
               'proof-map.md': proof_map.encode(), 'research-tree.md': tree.encode()}
    if result['new_claims']:
        entries = [marker]
        for c in result['new_claims']:
            entries.append(f'### {c["id"]} ({c["status"]})\n\n{c["statement"]}\n\n'
                           f'Assumptions: {c["assumptions"]}\nDependencies: {c["dependencies"]}\n'
                           f'Source: {c["source"]}\nChecks: {c["checks"]}\n'
                           f'Evidence: `{c["statement_file"]}` (hash and slice in round result).\n')
        updates['verification-ledger.md'] = local(project, 'verification-ledger.md').read_bytes() + ('\n\n' + '\n'.join(entries)).encode()
    if result.get('new_gaps') or result.get('closed_gaps'):
        delta = (f'\n\n{marker}\n## Frontier report (not certification)\n\n'
                 f'New gaps: {result.get("new_gaps", [])}\n'
                 f'Reported closures, subject to cited evidence: {result.get("closed_gaps", [])}\n'
                 f'Details: `{directory.relative_to(project)}/ROUND_RESULT.json`\n')
        updates['proof-map.md'] = proof_map.encode() + delta.encode()
    updates.update(task_updates)
    if tasks.ROUTE_FILE in task_updates:
        routes = json.loads(task_updates[tasks.ROUTE_FILE])['routes']
        body = '以下为作者自报的结构增量；不改写人工登记或认证等级。权威数据：`.runtime/routes.json`。\n'
        for rid, route in sorted(routes.items()):
            body += (f'\n- `{rid}` [{route["status"]}]：{route["mechanism"]}；范围：{route["scope"]}；'
                     f'重开条件：{route["reopening_condition"]}；证据：{", ".join(route["evidence"])}。\n')
        for name in ('ideas.md', 'research-tree.md'):
            path = local(project, name, exists=False)
            old = (updates[name].decode() if name in updates
                   else path.read_text() if path.exists() else '# 路线记录\n')
            updates[name] = section_replace(old, '## 队列路线增量（作者自报）', body).encode()
    # A valid old hash is not enough when this very transaction changes the
    # evidence file. Reject before journaling rather than save an immediately
    # stale manifest that prevents the next packet from being compiled.
    final_hashes = {local(project, name, exists=False).resolve(): sha(data)
                    for name, data in updates.items()}
    for spec in result['evidence']:
        path = local(project, spec['file']).resolve()
        if path in final_hashes and final_hashes[path] != spec['sha256']:
            raise ValueError(f'evidence changes during commit: {spec["file"]}; '
                             'preserve the cited evidence in an immutable notes file')
    return updates


def apply_result(project: Path, directory: Path) -> dict:
    """Validate before mutation, detect concurrent edits, journal every file.

A crash leaves COMMIT.json without APPLIED.json; subsequent automatic attempts
must stop for recovery. No transaction is silently replayed over user edits.
"""
    directory = local(project, str(directory.relative_to(project) / 'BASELINE.json')).parent
    lock = local(project, '.runtime/state-writer.lock', exists=False)
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        applied = directory / 'APPLIED.json'
        result_file = directory / 'ROUND_RESULT.json'
        if applied.exists():
            record = read_json(applied)
            if record['result_sha256'] != digest(result_file):
                raise ValueError('applied result was modified')
            return record
        if (directory / 'COMMIT.json').exists():
            raise ValueError('incomplete transaction; inspect COMMIT.json and backups before recovery')
        baseline = read_json(directory / 'BASELINE.json')
        if set(baseline) != set(PROTECTED):
            raise ValueError('incomplete or unexpected protected-file baseline')
        for name, expected in baseline.items():
            if digest(local(project, name, exists=False)) != expected:
                raise ValueError(f'protected file changed during research: {name}')
        # Parse and hash the same bounded bytes. Hashing the path at the end
        # could bind APPLIED to a concurrent replacement we never validated.
        with result_file.open('rb') as result_handle:
            result_bytes = result_handle.read(128 * 1024 + 1)
        if len(result_bytes) > 128 * 1024:
            raise ValueError(f'JSON too large: {result_file}')
        result = json.loads(result_bytes)
        if not isinstance(result, dict):
            raise ValueError(f'expected JSON object: {result_file}')
        result_sha256 = sha(result_bytes)
        validate_result(project, directory, result)
        def check_evidence_unchanged():
            for spec in result['evidence']:
                if digest(local(project, spec['file'])) != spec['sha256']:
                    raise ValueError(f'evidence changed during commit: {spec["file"]}; '
                                     'inspect any COMMIT.json before recovery')
        updates = render_updates(project, directory, result)
        journal = {}
        for name, data in updates.items():
            target = local(project, name, exists=False)
            backup = directory / 'before' / name
            previous = target.read_bytes() if target.exists() else None
            previous_hash = sha(previous) if previous is not None else None
            if previous_hash != baseline[name]:
                raise ValueError(f'protected file changed during commit preparation: {name}')
            if previous is not None:
                atomic(backup, previous)
            atomic(directory / 'after' / name, data)
            journal[name] = {'before': previous_hash, 'after': sha(data)}
        if digest(result_file) != result_sha256:
            raise ValueError('round result changed during commit preparation')
        for name, expected in baseline.items():
            if digest(local(project, name, exists=False)) != expected:
                raise ValueError(f'protected file changed during commit preparation: {name}')
        check_evidence_unchanged()
        write_json(directory / 'COMMIT.json', journal)
        if digest(result_file) != result_sha256:
            raise ValueError('round result changed during commit; inspect COMMIT.json before recovery')
        check_evidence_unchanged()
        for name, data in updates.items():
            target = local(project, name, exists=False)
            if digest(target) != journal[name]['before']:
                raise ValueError(f'protected file changed during commit: {name}; inspect COMMIT.json before recovery')
            atomic(target, data)
        if digest(result_file) != result_sha256:
            raise ValueError('round result changed during commit; inspect COMMIT.json before recovery')
        for name, entry in journal.items():
            if digest(local(project, name)) != entry['after']:
                raise ValueError(f'committed file changed before completion: {name}; inspect COMMIT.json before recovery')
        check_evidence_unchanged()
        record = {'result_sha256': result_sha256, 'files': journal,
                  'result_class': result['round_status'], 'new_claims': len(result['new_claims']),
                  'reported_closed_gaps': len(result.get('closed_gaps', []))}
        write_json(applied, record)
        return record


def telemetry(path: Path) -> dict:
    usage = {key: None for key in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens')}
    seen = set()
    calls = 0
    turns = 0
    malformed = 0
    if path.is_file():
        with path.open(encoding='utf-8', errors='replace') as handle:
            for line in handle:
                try:
                    event = json.loads(line)
                except (ValueError, TypeError):
                    malformed += 1
                    continue
                if not isinstance(event, dict):
                    continue
                if event.get('type') == 'turn.completed' and isinstance(event.get('usage'), dict):
                    turns += 1
                    for key in usage:
                        number = event['usage'].get(key)
                        if type(number) is int and number >= 0:
                            usage[key] = (usage[key] or 0) + number
                item = event.get('item')
                if event.get('type') in {'item.started', 'item.completed'} and isinstance(item, dict):
                    if item.get('type') in {'command_execution', 'mcp_tool_call', 'web_search', 'tool_call'}:
                        ident = item.get('id')
                        if ident is not None and ident not in seen:
                            seen.add(ident)
                            calls += 1
    return {**usage, 'completed_turns': turns, 'tool_calls': calls,
            'files_read': None, 'non_json_lines': malformed,
            'usage_available': turns > 0}


def aggregate_usage(logs: dict) -> dict:
    lanes = {name: telemetry(Path(path)) for name, path in logs.items()}
    totals = {}
    for key in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens', 'tool_calls'):
        values = [lane[key] for lane in lanes.values() if lane[key] is not None]
        totals[key] = sum(values) if values else None
    coverage = {key: sum(lane[key] is not None for lane in lanes.values()) for key in totals}
    return {**totals, 'lanes': lanes, 'field_coverage': coverage,
            'complete': bool(lanes) and all(x['usage_available'] for x in lanes.values())}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Read-only V2 result preflight; never calls a model.')
    parser.add_argument('command', choices=['check-result'])
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--round', required=True, help='project-relative round directory')
    args = parser.parse_args()
    project = args.project.resolve()
    try:
        directory = local(project, str(Path(args.round) / 'ROUND_RESULT.json')).parent
        validate_result(project, directory, read_json(directory / 'ROUND_RESULT.json'))
        # Check the future state size too, without creating a journal or changing files.
        render_updates(project, directory, read_json(directory / 'ROUND_RESULT.json'))
        print('OK: result schema, evidence integrity and state rendering; not mathematical certification')
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f'ERROR: {exc}\n')
