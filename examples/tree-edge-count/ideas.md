# Ideas

## Method families

| Family | Mechanism | Source | Decisive subgoal | Status | Test |
|---|---|---|---|---|---|
| F1 | Induction by deleting a leaf | internal-offline | A finite nontrivial tree has a leaf and remains a tree after deletion | proof-draft | One- and two-vertex trees |
| F2 | Sum of degrees | internal-offline | Control leaf count without using the target edge formula | proposed | Stars and paths |
| F3 | Grow from one vertex | internal-offline | Each added vertex adds exactly one edge | proposed | Existence of a valid expansion order |

## Current choice

Use F1. It reduces the target to a leaf lemma and preserves connectedness and acyclicity after deletion. F2 risks silently using the target formula to establish a leaf. F3 resembles F1 but requires an expansion order.

## Reopening conditions

- F2: find a leaf-count argument independent of $|E|=|V|-1$.
- F3: reopen when a constructive certificate distinct from leaf deletion is needed.
