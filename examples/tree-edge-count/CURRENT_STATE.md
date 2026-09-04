# Current State

## Control

- schema-version: 1
- updated-at: 2026-09-04T00:00:00+08:00
- migration-status: `complete`
- queue-status: `paused`
- search-contract: `affirmative-proof`
- evidence-ceiling: `proof-draft`

## Problem and scope

- Formal statement: every finite nonempty undirected simple tree satisfies \(|E|=|V|-1\).
- Definitions and normalization: tree means connected and acyclic; see `problem.md`.
- Scope exclusions: empty graphs, multigraphs, directed graphs, and infinite trees.

## Current mathematical status

- Strongest usable results: `S1` gives a leaf in every finite tree with at least two vertices.
- Current conclusion: `P0` has a complete induction candidate in `notes/proof.md`.
- Human decisions pending: none; the next step is independent proof audit.

## Active proof frontier

- Smallest open gap: no mathematical gap is currently identified; independent audit is missing.
- Active routes: `A1`, induction by deleting a leaf.
- Blocked routes worth remembering: none.

## Next bounded round

- Goal: audit `S1` and `P0` without reading the discovery narrative.
- Acceptance: check all hypotheses, the case \(|V|=1\), connectivity after deletion, and exact strength.

## Evidence pointers

- Verification ledger IDs: `VL-1`.
- Active proof-map nodes: `P0`, `A1`, `S1`, `S2`.
- Direct evidence files: `problem.md`, `notes/proof.md`, `proof-map.md`.

## History access

- Read `progress.md` only if the route choice or chronology matters.
- If this summary conflicts with direct evidence, direct evidence controls.
