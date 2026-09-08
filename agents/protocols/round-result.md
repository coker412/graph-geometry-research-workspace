# ROUND_RESULT contract (schema 1)

Write ROUND_RESULT.json in the exact round directory supplied by the runner. Use
its round_id and packet_sha256. Do not modify the protected state files. Write
proofs, checks and experiments as normal project artifacts; the runner formats
and journals state updates without making mathematical judgments.

Required fields:
- schema_version: 1; round_id: string; packet_sha256: string.
- round_status: progress | no-progress | candidate-solution | blocked.
- queue_status: pushing | needs-human-review | needs-human-input |
  needs-escalation-approval | solved-awaiting-human-verification.
- summary, active_gap, next_target, acceptance, checks: concrete nonempty strings.
- active_routes, blocked_routes, new_gaps, closed_gaps: lists of strings.
  A reported closure is not certified by the writer.
- new_claims: list of {id, statement, assumptions, dependencies, checks, status,
  source, statement_file}. IDs must be new. status is conjecture, experimental,
  partial-result or proof-draft; higher levels require separate review records
  and explicit reconciliation. source is internal-offline, provided-source,
  web-source or mixed. No new claims is [].
- evidence: at most 8 entries {file, start, end, sha256, purpose, source}.
  Paths are project relative; start/end are inclusive 1-based line numbers;
  SHA256 covers the full file. Every claim statement_file needs an entry.
  Offline entries must be internal-offline. Include the evidence needed by the
  NEXT target, including ledger/proof-map slices where relevant.
- candidate-solution also requires audit: {checks: ["pass", ... ten entries],
  report_file: path included in evidence}, and a proof-draft main claim.
  Read proof-audit and, for counterexamples, counterexample-audit before writing.
  The runner then freezes globally for human review, never certifies the proof.

Keep next-round state within 12 KiB/300 lines, target 6 KiB. Inherited scope,
mathematical status and evidence ceiling remain verbatim. If those need revision
or legacy migration, submit a precise note and needs-human-review; do not edit
protected state behind the writer. Structural route changes can be proposed in
notes; the writer appends gap reports to proof-map without rewriting its DAG.
