"""Versioned mathematical work items and route deltas; never certification.

All writes are returned to the V2 transactional writer. This module calls no model.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

TASK_FILE = '.runtime/research-task.json'
ROUTE_FILE = '.runtime/routes.json'
CONTRACT_KEYS = ('id', 'objective', 'acceptance', 'problem_sha256')
CLOSE_REASONS = {'continue', 'acceptance-met', 'route-exhausted',
                 'budget-exhausted', 'certification-pause'}
OUTCOMES = {'auxiliary', 'target-resolved', 'route-elimination', 'inconclusive'}


def restored_routes(project: Path) -> dict:
    """Recover legacy multi-slice omissions from committed results, without writing.

    Only repair an unchanged route declaration bound to its original applied
    result. Manual route changes and uncommitted drafts are never reconstructed.
    """
    routes = read(project, ROUTE_FILE).get('routes', {})
    if not isinstance(routes, dict) or any(not isinstance(r, dict) for r in routes.values()):
        raise ValueError('routes must contain objects')
    results = {}
    for rid, route in routes.items():
        round_id = route.get('round_id', '')
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,79}', round_id):
            continue
        prefix = f'.runtime/rounds/{round_id}'
        if round_id not in results:
            applied = read(project, f'{prefix}/APPLIED.json')
            if not applied:
                continue
            result_path = project / prefix / 'ROUND_RESULT.json'
            result = read(project, f'{prefix}/ROUND_RESULT.json')
            if hashlib.sha256(result_path.read_bytes()).hexdigest() != applied.get('result_sha256'):
                raise ValueError('committed route result changed; cannot recover evidence slices')
            results[round_id] = result
        result = results[round_id]
        change = next((c for c in result.get('route_changes', []) if c['id'] == rid), None)
        if change and all(route.get(k) == v for k, v in change.items()):
            last_by_file = {e['file']: e for e in result['evidence']}
            legacy = [last_by_file[name] for name in change['evidence']]
            # Repair exactly the old writer's last-slice-only representation.
            # Different slices may be a deliberate manual correction.
            if route.get('evidence_slices') == legacy:
                routes[rid] = {**route, 'evidence_slices': [e for e in result['evidence']
                                                          if e['file'] in change['evidence']]}
    return routes


def route_preview(project: Path, mode: str, max_bytes: int) -> tuple[str, dict]:
    """Bounded discovery index, not evidence; preserve each displayed scope whole.

    Use only spare packet space. Unknown/online provenance must not leak into
    offline packets, even through a route's title or summary.
    """
    routes = restored_routes(project)
    if not isinstance(routes, dict):
        raise ValueError('routes must be an object')
    eligible = []
    allowed = {'internal-offline'} if mode == 'offline' else {
        'internal-offline', 'provided-source', 'web-source', 'mixed'}
    for rid, route in routes.items():
        if not isinstance(route, dict):
            raise ValueError('route must be an object')
        specs = route.get('evidence_slices', [])
        if not specs or not all(isinstance(s, dict) and s.get('source') in allowed for s in specs):
            continue
        entry = {key: route.get(key) for key in (
            'status', 'mechanism', 'scope', 'reopening_condition', 'round_id')}
        entry['id'] = rid
        entry['evidence_slices'] = specs
        eligible.append(entry)
    eligible.sort(key=lambda r: (r.get('round_id') or '', r['id']), reverse=True)
    heading = ('## Recorded routes (author reports, not certification)\n'
               'Discovery only; verify the cited hashes/ranges before using evidence. '
               'This is a partial index, not the current plan or an exhaustive history. '
               'Read .runtime/routes.json for other relevant IDs, respecting information mode.\n')
    selected = []
    rows = []

    def render():
        return (heading + f'Displayed {len(rows)} of {len(eligible)} source-eligible routes; '
                f'{len(routes) - len(eligible)} excluded for provenance.\n' + '\n'.join(rows))

    for entry in eligible:
        if len(selected) >= 8:
            break
        rows.append(json.dumps(entry, ensure_ascii=False))
        if len(render().encode()) > max_bytes:
            rows.pop()
            continue
        selected.append(entry['id'])
    body = render() if routes else ''
    if len(body.encode()) > max_bytes:
        body = ''
    return body, dict(displayed_ids=selected, eligible=len(eligible),
                      excluded_for_provenance=len(routes) - len(eligible),
                      omitted=len(eligible) - len(selected))


def read(project: Path, name: str) -> dict:
    path = project / name
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('symlink in task/route state')
    if not path.exists():
        return {}
    if path.stat().st_size > 128 * 1024:
        raise ValueError('task/route state too large; archive explicitly')
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError('task/route state must be an object')
    return value


def text(value: dict, key: str, limit: int = 2048) -> str:
    s = value.get(key)
    if not isinstance(s, str) or not s.strip() or '\n' in s or '\r' in s or len(s.encode()) > limit:
        raise ValueError(f'missing or oversized task/route text: {key}')
    return s


def contract(project: Path, round_id: str, problem_sha256: str) -> dict:
    state = read(project, TASK_FILE)
    active = state.get('active')
    if active:
        if active['contract']['problem_sha256'] != problem_sha256:
            raise ValueError('active research task binds a different problem; reconcile scope explicitly')
        return active['contract']
    return dict(id=round_id, objective='', acceptance='', problem_sha256=problem_sha256)


def validate_plan(plan: dict, start: dict) -> None:
    if start.get('research_task_version') != 1:
        return
    value = plan.get('research_task')
    if not isinstance(value, dict):
        raise ValueError('PLAN requires research_task')
    for key in CONTRACT_KEYS:
        text(value, key)
    expected = start['research_task']
    for key in CONTRACT_KEYS:
        if (key in {'id', 'problem_sha256'} or expected.get('objective')) and value[key] != expected[key]:
            raise ValueError('research task objective/acceptance is frozen across steps')
    if set(value) != set(CONTRACT_KEYS):
        raise ValueError('unexpected research task contract fields')


def frozen_plan(project: Path, round_id: str) -> dict:
    directory = project / 'notes/progress-assessment' / round_id
    start = read(project, str((directory / 'START.json').relative_to(project)))
    plan = read(project, str((directory / 'PLAN.json').relative_to(project)))
    lock = read(project, str((directory / 'PLAN.lock.json').relative_to(project)))
    if start.get('research_task_version') != 1:
        raise ValueError('task-enabled packet requires a task-enabled START')
    for name, expected in [('PLAN.json', lock.get('sha256')),
                           ('BEFORE.md', start.get('before_sha256'))]:
        path = directory / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('task plan/baseline is not sealed or has changed')
    if lock.get('before_sha256') != start.get('before_sha256'):
        raise ValueError('task plan baseline mismatch')
    for name, expected in lock.get('supporting_evidence_sha256', {}).items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('invalid supporting evidence path')
        path = project / relative
        if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
            raise ValueError('invalid supporting evidence path')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('sealed strategy/reopening evidence changed')
    validate_plan(plan, start)
    return plan['research_task']


def evidence_refs(value: dict, key: str, evidence: dict, *, required=False) -> list[str]:
    refs = value.get(key, [])
    if (not isinstance(refs, list) or len(refs) > 8 or
            any(not isinstance(p, str) or p not in evidence or
                not p.startswith(('notes/', 'code/')) for p in refs)):
        raise ValueError(f'{key} must reference hashed notes/code evidence')
    if required and not refs:
        raise ValueError(f'{key} requires actual derivation or failure evidence')
    return refs


def validate(project: Path, directory: Path, packet: dict, result: dict) -> None:
    version = packet.get('research_task_version', 0)
    if not version:
        if 'research_task' in result or result.get('route_changes'):
            raise ValueError('task/route changes require a versioned task packet')
        return
    if version != 1:
        raise ValueError('unsupported research task version')
    progress = result.get('progress')
    if not isinstance(progress, dict):
        raise ValueError('task result requires progress metadata')
    for key in ('claimed_kind', 'main_problem_effect', 'scope_limitations', 'evidence_level'):
        entry = progress.get(key)
        if not isinstance(entry, str) or not entry.strip():
            raise ValueError('task result requires complete progress metadata')
    if progress['claimed_kind'] not in {'frontier-advance', 'route-elimination', 'enabling-result',
            'experimental-signal', 'reformulation', 'repeat', 'inconclusive', 'regression', 'candidate-solution'}:
        raise ValueError('invalid progress outcome')
    if progress['evidence_level'] not in {'conjecture', 'experimental', 'partial-result', 'proof-draft'}:
        raise ValueError('task self-report cannot upgrade evidence level')
    value = result.get('research_task')
    if not isinstance(value, dict):
        raise ValueError('ROUND_RESULT requires research_task')
    fixed = frozen_plan(project, directory.name)
    if fixed['problem_sha256'] != packet['problem_sha256'] or value.get('id') != fixed['id']:
        raise ValueError('research task/packet identity mismatch')
    reason, outcome = value.get('close_reason'), value.get('step_outcome')
    if reason not in CLOSE_REASONS or outcome not in OUTCOMES:
        raise ValueError('invalid task closure or step outcome')
    remaining = value.get('remaining_obligations')
    if (not isinstance(remaining, list) or len(remaining) > 32 or
            any(not isinstance(s, str) or not s.strip() or len(s.encode()) > 2048 for s in remaining)):
        raise ValueError('remaining_obligations must list concrete proof gaps')
    evidence = {e['file']: e for e in result['evidence']}
    evidence_refs(value, 'bridge_evidence', evidence, required=True)
    evidence_refs(value, 'acceptance_evidence', evidence, required=reason == 'acceptance-met')
    evidence_refs(value, 'failure_evidence', evidence, required=reason == 'route-exhausted')
    evidence_refs(value, 'alternative_evidence', evidence, required=reason == 'route-exhausted')
    if reason == 'acceptance-met' and (outcome != 'target-resolved' or remaining or result.get('round_status') == 'no-progress'):
        raise ValueError('auxiliary work/open obligations cannot close a mathematical task')
    if reason == 'certification-pause' and result.get('queue_status') not in {
            'needs-human-review', 'solved-awaiting-human-verification'}:
        raise ValueError('certification-pause requires an actual review hold')
    if result.get('round_status') == 'candidate-solution' and reason != 'certification-pause':
        raise ValueError('main candidate must preserve certification pause, not claim task acceptance')
    changes = result.get('route_changes', [])
    if not isinstance(changes, list) or len(changes) > 16:
        raise ValueError('route_changes must be a bounded list')
    old_routes = read(project, ROUTE_FILE).get('routes', {})
    ids = set()
    for change in changes:
        if not isinstance(change, dict):
            raise ValueError('route change must be an object')
        rid = text(change, 'id', 80)
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', rid) or rid in ids:
            raise ValueError('invalid or duplicate route id')
        ids.add(rid)
        for key in ('mechanism', 'scope', 'reopening_condition'):
            text(change, key)
        if change.get('status') not in {'active', 'blocked', 'eliminated', 'conditional'}:
            raise ValueError('invalid author-reported route status')
        evidence_refs(change, 'evidence', evidence, required=True)
        reopening = old_routes.get(rid, {}).get('status') in {'blocked', 'eliminated'} and change['status'] in {'active', 'conditional'}
        evidence_refs(change, 'reopening_evidence', evidence, required=reopening)


def render(project: Path, directory: Path, result: dict, *,
           result_name: str = 'ROUND_RESULT.json') -> tuple[dict[str, bytes], str]:
    """Called only after validation; return writer-owned transaction additions."""
    if 'research_task' not in result:
        return {}, ''
    fixed = frozen_plan(project, directory.name)
    value = result['research_task']
    state = read(project, TASK_FILE)
    active = state.get('active') or {'contract': fixed, 'steps': 0}
    if active['contract'] != fixed:
        raise ValueError('live research task differs from sealed plan')
    totals = state.get('totals', {'steps': 0, 'acceptance_reported': 0, 'routes_exhausted': 0})
    totals['steps'] += 1
    active = {**active, 'steps': active['steps'] + 1, 'last_round': directory.name,
              'last_result': str((directory / result_name).relative_to(project)),
              'close_reason': value['close_reason'], 'remaining_obligations': value['remaining_obligations']}
    reason = value['close_reason']
    closed = reason in {'acceptance-met', 'route-exhausted'}
    if closed:
        totals['acceptance_reported' if reason == 'acceptance-met' else 'routes_exhausted'] += 1
    state = dict(schema_version=1, active=None if closed else active, latest=active, totals=totals,
                 evidence_level='self-report; no certification')
    encoded = (json.dumps(state, ensure_ascii=False, indent=2) + '\n').encode()
    if len(encoded) > 128 * 1024:
        raise ValueError('task state too large; keep concise obligations and full derivations in evidence files')
    updates = {TASK_FILE: encoded}
    note = (f'- 数学任务：`{fixed["id"]}`；已执行步骤：{active["steps"]}；结算：{reason}（作者自报，非认证）。\n'
            f'- 持续目标：{fixed["objective"]}\n- 原始验收：{fixed["acceptance"]}\n'
            f'- 任务与未结义务：`{TASK_FILE}`；本次回传证据：{", ".join(value["bridge_evidence"])}')
    routes = restored_routes(project) if result_name == 'ROUND_RESULT.json' else None
    if routes is not None and (result.get('route_changes') or
                              routes != read(project, ROUTE_FILE).get('routes', {})):
        for change in result.get('route_changes', []):
            routes[change['id']] = {**change, 'round_id': directory.name,
                                    'evidence_slices': [e for e in result['evidence']
                                                        if e['file'] in change['evidence']]}
        encoded = (json.dumps(dict(schema_version=1, routes=routes), ensure_ascii=False, indent=2) + '\n').encode()
        if len(encoded) > 128 * 1024:
            raise ValueError('route index too large; archive explicitly without losing evidence')
        updates[ROUTE_FILE] = encoded
    return updates, note
