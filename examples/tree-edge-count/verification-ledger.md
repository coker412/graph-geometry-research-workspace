# Verification ledger

## VL-1

- Object: `P0` and dependencies `A1`, `S1`, `S2`.
- Conclusion: a finite nonempty undirected simple tree satisfies $|E|=|V|-1$.
- Evidence level: `proof-draft`.
- Source: `internal-offline`.
- Evidence: `problem.md`, `notes/proof.md`, `proof-map.md`.
- Boundary checks recorded: one- and two-vertex trees agree with the formula; empty graphs are excluded.
- Counterexample checks recorded: paths and stars agree with the formula; these examples are not a general proof.
- Dependencies: longest-path endpoints are leaves; leaf deletion preserves connectedness and acyclicity.
- Remaining gap: no complete independent certification of the candidate yet.
- Consequence: do not upgrade `P0` to `agent-verified` or `human-verified` before the required review.
