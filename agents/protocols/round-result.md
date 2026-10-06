# ROUND_RESULT contract (schema 1)

Write ROUND_RESULT.json in the supplied round directory, using its round_id and
packet_sha256. Write proofs/experiments in project artifacts; leave protected
state to the runner. Its format/hash/journal checks never certify mathematics.

Required fields:
- schema_version: 1; round_id, packet_sha256: supplied strings.
- round_status: progress | no-progress | candidate-solution | blocked.
- queue_status: pushing | needs-human-review | needs-human-input |
  needs-escalation-approval | solved-awaiting-human-verification.
- summary, active_gap, next_target, acceptance, checks: concrete nonempty strings.
- active_routes, blocked_routes, new_gaps, closed_gaps: lists of strings.
  Reported gap closure is not certification.
- new_claims: list of {id, statement, assumptions, dependencies, checks, status,
  source, statement_file}; [] if none. IDs must be new. All claim fields are
  strings, NEVER arrays; statement/assumptions/dependencies/checks must be
  nonempty and at most 8192 UTF-8 bytes each (newline-separated entries allowed).
  status: conjecture | experimental | partial-result | proof-draft; higher levels
  need separate review and reconciliation. source: internal-offline |
  provided-source | web-source | mixed.
- evidence: at most 8 {file, start, end, sha256, purpose, source} entries.
  Paths are project-relative; lines inclusive and 1-based; SHA256 covers the
  whole file. Every statement_file needs an entry. Offline sources must be
  internal-offline. Include exact slices needed by the NEXT target, including
  inherited claims, comparisons, ledger/proof-map dependencies. Multiple slices
  of one file are valid. Evidence exceeding automatic-loading budgets remains
  valid: the next packet defers it with exact hashed pointers. Read those slices
  before use; never split proofs or drop hypotheses to fit loading budgets.
- progress: {claimed_kind, main_problem_effect, scope_limitations, evidence_level}.
  claimed_kind: frontier-advance | route-elimination | enabling-result |
  experimental-signal | reformulation | repeat | inconclusive | regression |
  candidate-solution. evidence_level is at most proof-draft. Seal PLAN before
  research. The runner derives/seals progress RESULT from this submission; do
  not write a second RESULT, seal it manually, or invent an independent REVIEW.
  Legacy submissions without progress retain their legacy assessment path.

candidate-solution covers the FULL original problem. Auxiliary lemmas, batch
subtargets, subquestions, special cases and sufficient-condition families use
progress with proof-draft claims and pushing, following the certification rules.
A full candidate requires queue_status=solved-awaiting-human-verification and:
- solution_scope: {kind: "full-original-problem", problem_sha256: <PACKET.json.problem_sha256>,
  unresolved_parts: [], coverage_statement: <all parts and quantifiers covered>}.
- audit: {checks: ["pass", ... ten entries], report_file: <path in evidence>};
  unlike claim.checks, audit.checks IS an array. Include a proof-draft main claim.
Read proof-audit (also counterexample-audit for counterexamples). The runner
freezes globally for review; it does not verify the proof. An incomplete audit
of a full candidate uses needs-human-review, not a claim that no candidate exists.

Keep state at target 6 KiB, maximum 12 KiB/300 lines. The writer refreshes the
Chinese frontier index while preserving original scope and evidence ceilings.
Name still-needed inherited IDs in summary/active_gap and retain their exact
slices; do not resubmit IDs or replace dependencies with an unspecific “see
ledger”. Corrections need an impact note naming affected downstream claims;
keep those conditional/GAP until reconciled. Use human holds only for concrete
blocking decisions or required integrity/certification recovery. Do not edit
protected files behind the writer. Route changes use the enabled protocol below;
otherwise propose them in notes. The writer does not reconstruct the proof DAG.

Before returning run the supplied read-only `tools/research_runtime.py check-result`
command and fix submission errors. It checks schema, hashes and state size,
not mathematical validity. Packet budgets, including legacy `_tokens` keys,
count UTF-8 bytes, not model tokens.

## Research task protocol 1 (only if PACKET.json or mixed START enables it)

One ordinary call, or one completed mixed-isolated integration, is one step.
A task persists until its original acceptance is met or
its route seriously exhausted; no minimum duration or compulsory breakthrough.
PLAN.research_task contains exactly {id, objective, acceptance, problem_sha256}.
Keep supplied identity/hash and existing objective/acceptance verbatim. For a
new task choose a critical-path obligation, with assumptions, quantifiers and
effect on the original gap in its acceptance. Fields are single-line. Seal PLAN.

After auxiliary success actually substitute into the original dependency chain
and attempt the bridge. Record added hypotheses, lost endpoints, uncontrolled
constants and circularity. A future promise is not evidence. If interrupted,
save the unfinished derivation and precise resumption point; keep the task pending.
Route exhaustion needs the attempted derivation, failed step, excluded scope,
and an actually tested alternative explaining how it could bypass the obstacle.
Exhausting a route never authorizes ending a continuous project.

Required ROUND_RESULT.research_task (mixed integration: RESULT.research_task):
- id: sealed ID; step_outcome: auxiliary | target-resolved | route-elimination | inconclusive.
- close_reason: continue | acceptance-met | route-exhausted | budget-exhausted | certification-pause.
- remaining_obligations: concrete strings; [] only if none remain for this task.
- bridge_evidence: nonempty list of notes/ or code/ paths included in evidence.
- acceptance_evidence: same path type, required for acceptance-met; also requires
  target-resolved and no remaining obligations. Auxiliary success cannot close it.
- failure_evidence, alternative_evidence: both required for route-exhausted;
  one file may hold clearly separated derivation/test sections.
Main candidates use certification-pause and the full-scope audit/hold. That
reason and budget-exhausted retain the task. All closures are author reports.

V2 route_changes: include only for new/blocked/eliminated/reopened mechanisms or
changed usable scope, maximum 16; updating blocked_routes alone is insufficient.
Reuse IDs; exclude only the failed assumptions/ansatz. Each entry: id, status
(active | blocked | eliminated | conditional), mechanism, scope,
reopening_condition, evidence (hashed notes/code paths). Reopening a stored
blocked/eliminated route needs reopening_evidence. Text fields are single-line;
put actual failure, reusable construction and tested replacement in evidence.
The writer preserves every cited slice in .runtime/routes.json and updates
managed ideas.md/research-tree.md sections without changing manual sections.
Mix retains compatibility route records and does not accept route_changes yet.
Never edit .runtime/research-task.json or .runtime/routes.json directly. Report
steps, claimed task acceptance and mathematical verification levels separately.
