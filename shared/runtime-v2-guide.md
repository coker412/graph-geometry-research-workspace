# Mathematics research runtime V2

An ordinary call is a research step. The runner prepares its context packet and applies structured results. The synchronized configuration sets ordinary research to `medium`; first decisions and steps requiring a mechanism review use `high`. `CURRENT_STATE`, proof-map, verification-ledger, and progress retain long-term memory.

## Phases and configuration

`problems/important-conjectures/runner.toml` sets `phase = "research"` by default. An item's `config.toml` may override it. The model cannot promote its own phase.

These are built-in defaults; actual runs use `[phase_effort]` and decision overrides:

| Phase | Default effort | Protocol |
|---|---|---|
| triage | medium | explore |
| research | high | explore |
| experiment | medium | computation |
| literature | medium | literature-check |
| audit | high | proof-audit |
| critical-audit | xhigh | proof-audit |
| stuck-escalation | xhigh | explore |

Ordinary phases reject xhigh. Literature requires an explicit connected mode; changing phase does not enable networking. An empty `model` uses the CLI default and is recorded as unresolved, so it cannot support model-specific pricing. Check the installed version with `codex --version`. Supported effort levels depend on the selected model.

Ordinary rounds default to `runtime_version = 2`; version 1 uses compatibility prompts. `mixed-isolated` retains compatibility closing and bubblewrap isolation, normally with three calls: parallel offline/connected branches and then integration. The connected and integration calls use medium and high respectively. Mixed runs do not use the V2 shared-state writer.

## Context packets

An ordinary round creates:

```text
projects/<project>/.runtime/rounds/<round-id>/
  RESEARCH_PACKET.md
  PACKET.json
  BASELINE.json
  ROUND_RESULT.json
  COMMIT.json
  APPLIED.json
  before/
  after/
```

Packets contain the core rules, phase protocol, formal problem, short state, designated evidence slices, and assessment requirements. They do not automatically traverse old progress, proof maps, or all notes. If no slice list exists, read the necessary direct pointers from short state and return slices for the next round. External dependencies still require the applicable literature or certification protocol; a packet cannot replace missing premises.

Project `.runtime/evidence.json` example:

```json
{
  "evidence": [{
    "file": "notes/lemma.md",
    "start": 12,
    "end": 40,
    "sha256": "insert-the-full-file-64-character-SHA256-here",
    "purpose": "Saturation estimate needed at the current gap",
    "source": "internal-offline"
  }]
}
```

Paths must stay inside the project; symlinks and directory escapes are rejected. Invalid line ranges, stale hashes, or noninternal evidence in an offline packet prevent a model call. Whole slices beyond the inline budget retain file, lines, full-file hash, and purpose, marked NOT INLINED. Read the source slice before using it. Never truncate a proof or remove premises to fit.

Large evidence is checked incrementally for the full specified range and hash, while only complete fitting slices are retained. Deferred loading avoids first joining the whole file; integrity-check costs still grow with file size. Hashes detect content changes, not truthful provenance or correct mathematics. If line numbers move, select and verify a new slice.

Short state targets 6 KiB, warns above 8 KiB, and has a V2 limit of 12 KiB/300 lines. Legacy state retains a 32 KiB/300-line check. The writer preserves scope, existing mathematical status, and the evidence ceiling. Changes to these sections need explicit conservative migration, not inferred edits or truncated hypotheses.

`context_budget` uses explicit UTF-8 bytes:

```toml
packet_target_bytes = 32768
packet_hard_bytes = 65536
max_evidence_slices = 8
max_single_evidence_bytes = 12288
```

Legacy `*_tokens` keys remain byte-unit aliases; conflicting aliases are rejected. These limits control automatic loading, not saved proofs or evidence archives. Results allow at most eight evidence entries, each checked independently for path, range, source, and hash. Keep complete fitting slices in listed priority order and defer the rest. If even rules, state, and evidence references exceed the hard limit, explicitly reduce working state before calling the model.

`PACKET.json` records all evidence and the reason for each deferred entry. `deferred_evidence` does not delete evidence. These are not billed tokens and do not bound CLI system prompts, tool definitions, or later tool outputs. Phase rules govern further reading; usage events record actual consumption.

Fixed rules precede project details, hashes, and round instructions, preserving a common prefix for each phase. `stable_prefix_bytes` and `stable_prefix_sha256` describe it. This enables potential cache reuse without guaranteeing a service cache hit.

Repeated slices with the same file, range, hash, and source are validated separately, then reuse the first body only when this shortens the input. Purposes and evidence records remain separate. Overlapping but different ranges are not merged. `evidence_dedup_saved_bytes` and `evidence_rendered_bytes` record byte savings and rendered size; `components_bytes.evidence` remains itemwise. No duplicates means zero savings, not a claimed token reduction.

## Results and certification

Follow the [ROUND_RESULT protocol](../agents/protocols/round-result.md). The researcher writes proofs, checks, calculations, and JSON fields. After validation, the runner appends progress, registers new claims, and updates short state and next-round slices. Gap changes are appended as reports requiring evidence review; the program does not rewrite the proof DAG.

With the task protocol enabled, report structural route changes through `route_changes` and evidence. The transaction writer updates the route table and dedicated ideas/research-tree sections. Compatibility rounds retain root ownership.

Before submission, run the same read-only validation used by the writer:

```bash
python tools/research_runtime.py check-result   --project <absolute-project-path> --round .runtime/rounds/<round-id>
```

The runtime preserves supported Chinese headings in existing state without adding duplicate English sections. Transaction snapshots retain previous duplicate content. It does not automatically rewrite the original problem or mathematical statements.

The writer accepts new IDs only, at evidence levels no higher than `proof-draft`. Existing claim upgrades, downgrades, and certification imports require explicit review and state reconciliation. A complete candidate must include ten checks and a hash-bound audit report, then triggers a global hold. Valid JSON is not mathematical certification. An incomplete main-candidate audit uses `needs-human-review`; an auxiliary candidate without independent certification may still support explicit conditional exploration or independent routes.

The writer parses and hashes the same result bytes, checks backup/start hashes and changes during commit, and rejects a write that would immediately invalidate its own cited evidence. Preserve immutable evidence first. Conflicts after journaling retain the scene for recovery; this is not a cross-file atomic transaction against arbitrary uncooperative edits.

Before writing, the runner checks shared files against starting hashes and saves before/after snapshots and a journal. Reapplying an unchanged completed result is idempotent; altering an applied result is rejected. If interrupted with `COMMIT.json` but no `APPLIED.json`, subsequent rounds stop for recovery. Inspect each before/after hash before restoring or completing the transaction. The runner does not overwrite researcher edits made after interruption. Backups restore state files; proof and experiment artifacts remain in their own directories.

### Execution counts and abnormal exits

`.queue-runtime.json` and `.conjecture-status` use atomic replacement. Only an absent count file means no executions. Corrupt files, invalid counts, or empty status files produce errors and remain intact; they are not reset to zero or queued. Dry-run selection does not rewrite state.

After preflight and before calling the model, persist `attempts` and `active_execution`: attempt, round ID, start time, mode, and log path. A failed reservation prevents the call; failed preflight does not count. Clear the marker only after closing. Handled timeouts/process failures still count once under the existing failure policy. A mixed execution also counts once despite possibly containing three calls.

On catchable interruption or wait errors, stop the launched process group and check for surviving descendants after the leader exits; append errors to existing logs. Mixed interruption signals both branches and waits for cleanup before removing isolated directories. A forced kill, power failure, or detached child requires separate inspection; a marker alone cannot establish that all processes stopped.

If `active_execution` remains, preserve counts, exclude the project from scheduling, and report the recovery location. Runnable state becomes `needs-human-review`; an existing main-result hold is preserved. Merely changing status to queued does not permit a rerun. First confirm old processes have stopped. Inspect call logs, ROUND_RESULT, assessments, and V2 COMMIT/APPLIED records. Resolve partial transactions, then reconcile history and counts. An absent call log does not justify subtracting a reserved attempt. Preserve raw records and a recovery explanation, atomically clear the inspected marker, and reconcile status. Technical recovery neither upgrades evidence nor substitutes for researcher acceptance.

An active persistent task cannot switch to a legacy/task_version=0 path that drops its obligations. Ordinary V2 and mixed-isolated must retain `research_task_version=1`, the objective, and acceptance criteria, or explicitly reconcile scope and outstanding obligations first. Task-state saving checks the 128 KiB read limit before transaction commit. Oversized results are rejected without changing the original state. Put full derivations in evidence files; retain only short obligations and pointers in state.

`run --once` returns the execution error code, except that a complete main-result global hold retains priority. Successful execution, structural checks, and saved files do not prove mathematical correctness.

## Inspect and validate

```bash
./queue.sh packet --slug <slug>           # Size/hash preview.
./queue.sh packet --slug <slug> --content # Packet body.
./queue.sh run --dry-run --slug <slug>    # No model call.
./queue.sh usage
./queue.sh usage --slug <slug> --json
./queue.sh state-audit
conda run -n graphlab python -m unittest discover -s tools/tests -v
```

Preview uses the current problem source without input snapshots or the actual launch's assessment instructions. The runner recompiles and fully checks the packet before calling. Missing projects, mixed mode, and over-budget packets produce explicit preview errors.

Telemetry records requested model, effort, phase, elapsed time, packet size, per-branch usage, visible tool calls, and result category. Cached input is a subset of input and is not added again. Reasoning tokens are recorded only when reported. File-read counts lack reliable events and remain null. Missing historical/failed-call usage remains unknown; partial branch totals are incomplete. Visible tool events do not enumerate all shell operations or child-agent usage. Progress categories are self-reports; independent assessment determines verified gap reduction.

The implementation's JSONL/configuration references are the [noninteractive guide](https://learn.chatgpt.com/docs/non-interactive-mode) and [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference). The recorded validation covers local implementation and simulated rounds, not controlled quality, latency, or savings comparisons using real model rounds.

## Mathematical tasks across calls

Introduced on 2026-09-26, `research_task_version = 1` enables persistent tasks for new ordinary V2 and mixed-isolated runners. An ordinary call or complete mixed branches-plus-integration cycle is one step. Attempt/time/quota limits retain their meaning; the task layer does not add calls.

PLAN fixes the objective and original acceptance. Later steps retain the same ID. Auxiliary results must include an actual attempt to apply them to the original problem. See [round-result.md](../agents/protocols/round-result.md) for JSON fields.

`.runtime/research-task.json` stores the task, obligations, and protocol counts. `.runtime/routes.json` stores self-reported structural changes and evidence hashes. V2 maintains both in one transaction; mixed closing atomically saves task state but retains compatibility route records. Preserve manually written ideas/research-tree content; update only dedicated sections. Historical proof-map gap reports stay outside replaceable latest-state sections.

`queue.sh progress` distinguishes execution steps, self-reported task acceptance, route exhaustion, and independent reviews. These counts do not retrospectively infer old calls' mathematical value or certify proofs.

PACKET determines protocol version; mixed runs use START. Old packets retain their closing path. Mixed integration returns `research_task` in compatibility RESULT; the runner seals and saves it without double-counting replay. Mixed results do not yet accept V2 `route_changes`. Existing Python runners do not hot-load updated modules; new starts use the update. An unfinished active task cannot silently revert to the old protocol.

The route catalog uses only remaining packet space, up to eight entries/8 KiB. It does not displace proof bodies. Filter by information provenance and retain full scope/evidence pointers. This is a partial self-reported catalog, not certification or full history. Report structural changes even within an unfinished task; changing only `blocked_routes` in short state is insufficient.
