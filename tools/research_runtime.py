"""Bounded research packets, conservative round commits, and CLI telemetry.

No model calls occur in this module. Token budgets use UTF-8 bytes as a
conservative upper estimate, not billing tokens. Missing usage remains unknown.
"""
from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

PHASES = {
    'triage': ('medium', 'explore'),
    'research': ('high', 'explore'),
    'experiment': ('medium', 'computation'),
    'literature': ('medium', 'literature-check'),
    'audit': ('high', 'proof-audit'),
    'critical-audit': ('xhigh', 'proof-audit'),
    'stuck-escalation': ('xhigh', 'explore'),
}
BUDGET = dict(packet_target_tokens=12000, packet_hard_tokens=48000,
              max_evidence_slices=8, max_single_evidence_tokens=12000)
PROTECTED = ('CURRENT_STATE.md', 'progress.md', 'verification-ledger.md',
             'proof-map.md', 'ideas.md', 'research-tree.md', '.conjecture-status', '.runtime/evidence.json')
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
    efforts = config.get('phase_effort', {})
    if not isinstance(efforts, dict):
        raise ValueError('phase_effort must be a table')
    effort = efforts.get(phase, config.get('reasoning_effort', 'high')
                         if phase == 'research' else PHASES[phase][0])
    if effort not in {'medium', 'high', 'xhigh'}:
        raise ValueError(f'unsupported effort: {effort}')
    if effort == 'xhigh' and phase not in {'critical-audit', 'stuck-escalation'}:
        raise ValueError('xhigh requires critical-audit or stuck-escalation phase')
    return {**config, 'phase': phase, 'reasoning_effort': effort}


def evidence_slice(project: Path, spec: dict, mode: str, budget: dict) -> tuple[str, dict]:
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
    number = 0
    with path.open(encoding='utf-8') as handle:
        for number, line in enumerate(handle, 1):
            if number > end:
                break
            if number >= start:
                selected.append(line)
                count += len(line.encode())
                if count > budget['max_single_evidence_tokens']:
                    raise ValueError(f'evidence slice exceeds budget: {spec["file"]}')
    if number < end:
        raise ValueError(f'evidence range beyond EOF: {spec["file"]}')
    purpose = spec.get('purpose')
    if not isinstance(purpose, str) or not purpose.strip() or '\n' in purpose:
        raise ValueError('evidence purpose required')
    body = ''.join(selected)
    return (f'### {spec["file"]}#L{start}-L{end}\nSource: {source}; {purpose}\n\n{body}',
            {**spec, 'slice_sha256': sha(body.encode()), 'bytes': count})


def compile_packet(root: Path, project: Path, problem: Path, config: dict,
                   item: dict, mode: str, extra: str = '') -> tuple[str, dict]:
    phase = config.get('phase', 'research')
    if phase == 'literature' and mode != 'connected':
        raise ValueError('literature phase requires explicit connected information mode')
    overrides = config.get('context_budget', {})
    if not isinstance(overrides, dict) or set(overrides) - set(BUDGET):
        raise ValueError('unknown context budget fields')
    budget = {**BUDGET, **overrides}
    if any(type(v) is not int or v <= 0 for v in budget.values()):
        raise ValueError('context budgets must be positive integers')
    if budget['packet_target_tokens'] > budget['packet_hard_tokens']:
        raise ValueError('packet target exceeds hard budget')
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
        if path.stat().st_size > budget['packet_hard_tokens']:
            raise ValueError(f'packet component exceeds budget: {label}; select evidence slices')
        body = path.read_text(encoding='utf-8')
        sizes[label] = len(body.encode())
        parts.append(f'## {label}\n\n{body}')
    evidence = []
    manifest = local(project, '.runtime/evidence.json', exists=False)
    if manifest.exists():
        specs = read_json(manifest).get('evidence')
        if not isinstance(specs, list) or len(specs) > budget['max_evidence_slices']:
            raise ValueError('invalid evidence list or too many slices')
        for spec in specs:
            body, record = evidence_slice(project, spec, mode, budget)
            parts.append(body)
            evidence.append(record)
    else:
        parts.append('## Evidence selection\nNo slice manifest yet. Follow exact CURRENT_STATE IDs; '
                     'read only the needed ranges. Return hashed evidence slices for the next round. '
                     'Missing historical evidence is unknown, not disproved or certified.')
    header = (f'# Research packet\nPhase: {phase}\nInformation mode: {mode}\n'
              f'Search contract: {item.get("search_contract", "either")}\n'
              f'Stagnation threshold: {item.get("stagnation_rounds_before_blocked", 0)}\n'
              f'Project: {project}\nProblem SHA256: {digest(problem)}\n'
              'The state section supplies the objective, gap and next action. '
              'Included protocols are already loaded; do not re-read the full workflow.\n')
    sizes['evidence'] = sum(e['bytes'] for e in evidence)
    sizes['round-instructions'] = len(extra.encode())
    text = header + '\n\n'.join(parts) + '\n\n' + extra
    size = len(text.encode())
    if size > budget['packet_hard_tokens']:
        raise ValueError(f'packet exceeds conservative token budget: {size} > '
                         f'{budget["packet_hard_tokens"]}; select smaller state/evidence before calling Codex')
    warnings = []
    if size > budget['packet_target_tokens']:
        warnings.append('packet above soft target')
    if sizes['state'] > 8192:
        warnings.append('legacy CURRENT_STATE above 8 KiB; next V2 result must fit 12 KiB')
    return text, dict(bytes=size, token_upper_estimate=size, token_method='utf8-bytes-upper-bound',
                      components_bytes=sizes, evidence=evidence, warnings=warnings,
                      phase=phase, information_mode=mode, problem_sha256=digest(problem),
                      packet_sha256=sha(text.encode()), budget=budget)


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
    if value.get('schema_version') != 1 or value.get('round_id') != directory.name:
        raise ValueError('wrong result schema or round id')
    if value.get('packet_sha256') != read_json(directory / 'PACKET.json')['packet_sha256']:
        raise ValueError('result does not match this research packet')
    for key in ('summary', 'active_gap', 'next_target', 'acceptance', 'checks'):
        required_text(value, key)
    if value.get('round_status') not in {'progress', 'no-progress', 'candidate-solution', 'blocked'}:
        raise ValueError('unknown round_status')
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
    if len(evidence) > 8 or len(claims) > 32:
        raise ValueError('too many evidence slices or claims')
    packet = read_json(directory / 'PACKET.json')
    mode = packet['information_mode']
    budget = packet.get('budget', BUDGET)
    for spec in evidence:
        evidence_slice(project, spec, mode, budget)
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
    for key in ('active_routes', 'blocked_routes', 'new_gaps', 'closed_gaps'):
        values = value.get(key, [])
        if not isinstance(values, list) or len(values) > 32 or any(
            not isinstance(x, str) or '\n' in x or len(x) > 500 for x in values
        ):
            raise ValueError(f'invalid {key}')
    if value['round_status'] == 'candidate-solution':
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
    pattern = re.compile(r'^' + re.escape(heading) + r'\s*$.*?(?=^## |\Z)', re.M | re.S)
    replacement = heading + '\n\n' + body.strip() + '\n\n'
    if pattern.search(text):
        return pattern.sub(lambda _: replacement, text, count=1)
    return text.rstrip() + '\n\n' + replacement


def render_updates(project: Path, directory: Path, result: dict) -> dict[str, bytes]:
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
    # Keep inherited scope and mathematical status verbatim. New claims are draft
    # references; they cannot replace accepted facts or the evidence ceiling.
    state = re.sub(r'^- updated-at:.*$', '- updated-at: ' + stamp, state, flags=re.M)
    state = re.sub(r'^- queue-status:.*$', f'- queue-status: `{status}`', state, flags=re.M)
    state = section_replace(state, '## Active proof frontier',
        f'- Smallest open gap: {result["active_gap"]}\n'
        f'- Active routes: {", ".join(result.get("active_routes", []))}\n'
        f'- Blocked routes: {", ".join(result.get("blocked_routes", []))}')
    state = section_replace(state, '## Next bounded round',
        f'- Goal: {result["next_target"]}\n- Acceptance: {result["acceptance"]}')
    pointers = [f'- `{e["file"]}#L{e["start"]}-L{e["end"]}`; sha256={e["sha256"]}; {e["purpose"]}'
                for e in result['evidence']]
    pointers += [f'- New claim `{c["id"]}`: `{c["status"]}`; see verification-ledger.md and `{c["statement_file"]}`'
                 for c in result['new_claims']]
    pointers.append(f'- Latest result: `{directory.relative_to(project)}/ROUND_RESULT.json`; '
                    'inherited facts retain their original ledger and evidence records.')
    state = section_replace(state, '## Evidence pointers', '\n'.join(pointers))
    if len(state.encode()) > 12288 or len(state.splitlines()) > 300:
        raise ValueError('new CURRENT_STATE exceeds 12 KiB/300 lines; revise working set explicitly')
    marker = f'<!-- runtime-round:{directory.name} -->'
    summary = (f'\n\n{marker}\n## {stamp} ({directory.name})\n\n'
               f'{result["summary"]}\n\nChecks: {result["checks"]}\n\n'
               f'Gap: {result["active_gap"]}\nNext: {result["next_target"]}\n'
               f'Result: `{directory.relative_to(project)}/ROUND_RESULT.json`\n')
    updates = {'CURRENT_STATE.md': state.encode(), '.conjecture-status': (status + '\n').encode(),
               'progress.md': local(project, 'progress.md').read_bytes() + summary.encode(),
               '.runtime/evidence.json': (json.dumps({'evidence': result['evidence']}, ensure_ascii=False, indent=2) + '\n').encode()}
    if result['new_claims']:
        entries = [marker]
        for c in result['new_claims']:
            entries.append(f'### {c["id"]} ({c["status"]})\n\n{c["statement"]}\n\n'
                           f'Assumptions: {c["assumptions"]}\nDependencies: {c["dependencies"]}\n'
                           f'Source: {c["source"]}\nChecks: {c["checks"]}\n'
                           f'Evidence: `{c["statement_file"]}` (hash and slice in round result).\n')
        updates['verification-ledger.md'] = local(project, 'verification-ledger.md').read_bytes() + ('\n\n' + '\n'.join(entries)).encode()
    if result.get('new_gaps') or result.get('closed_gaps'):
        delta = (f'\n\n{marker}\n### Frontier report (not certification)\n\n'
                 f'New gaps: {result.get("new_gaps", [])}\n'
                 f'Reported closures, subject to cited evidence: {result.get("closed_gaps", [])}\n'
                 f'Details: `{directory.relative_to(project)}/ROUND_RESULT.json`\n')
        updates['proof-map.md'] = local(project, 'proof-map.md').read_bytes() + delta.encode()
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
        for name, expected in baseline.items():
            if digest(local(project, name, exists=False)) != expected:
                raise ValueError(f'protected file changed during research: {name}')
        result = read_json(result_file)
        validate_result(project, directory, result)
        updates = render_updates(project, directory, result)
        journal = {}
        for name, data in updates.items():
            target = local(project, name, exists=False)
            backup = directory / 'before' / name
            if target.exists():
                atomic(backup, target.read_bytes())
            atomic(directory / 'after' / name, data)
            journal[name] = {'before': digest(target), 'after': sha(data)}
        write_json(directory / 'COMMIT.json', journal)
        for name, data in updates.items():
            atomic(local(project, name, exists=False), data)
        record = {'result_sha256': digest(result_file), 'files': journal,
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
