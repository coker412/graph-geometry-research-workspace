# Reasoning escalation

Rethlas and web Pro require explicit authorization for each use. A stronger model does not change the evidence requirements. After Codex fails twice to close the same precise gap, first inspect existing project material, history/ledger/proof-map entries referenced by current state, and Rethlas results to check whether the argument already exists.

Prepare an unambiguous handoff: formal statement, definitions and normalizations, verified results, smallest gap, necessary failed approaches, objective, cost, and verification requirements. Include:

> Attempt a proof or counterexample directly. Do not stop because the problem may be open. Check any candidate result rigorously.

Prepare the material first. Request permission only if this external run is needed and lacks existing authorization. Read RETHLAS使用教程.md after Rethlas approval. Web Pro also requires approval before submission. Preparing a packet or failing twice with one mechanism does not itself pause other authorized research. Use needs-escalation-approval only when further work actually depends on an unauthorized external call. Independently review returned results and register raw responses and hashes. Follow queue-core write ownership when reconciling affected state; model strength cannot certify a result.

## Rethlas prerequisites

Before handing a problem to Rethlas, ensure that:

- The statement is complete and unambiguous.
- Definitions and normalizations have been audited.
- Known results and open obligations are separate.
- References are organized.
- The exact gap is written down.
- The researcher has approved this run.

Procedure:

1. Initialize the problem with `tools/rethlas/init_project.sh`.
2. Place the formal statement and `.refs/` materials in the project's `rethlas/problems/`.
3. Report the problem file, exact gap, and run objective.
4. After authorization, start the verification service.
5. Run `tools/rethlas/run_problem.sh` or its tmux wrapper.
6. Label `blueprint.md` at most `proof-draft`.
7. Only a passing independent verifier report bound to the current statement and proof snapshot supports `agent-verified`. The filename `blueprint_verified.md` is not certification.
8. Import verifier reports, failed approaches, and new lemmas.
9. Only stepwise researcher acceptance supports `human-verified`.

For an auxiliary candidate, suspend its use as a certified premise; explicitly conditional exploration and independent routes may continue. For a complete main candidate or decisive main counterexample, pause the whole problem, complete the applicable audits, and await researcher review. Do not extend the auxiliary-result continuation rule to a complete main candidate.

## Long runs in tmux

Use tmux for long Rethlas jobs rather than keeping the current agent in a polling loop.

Start or check the verifier:

```bash
./tools/rethlas/start_verifier_tmux.sh
curl -sf http://127.0.0.1:8091/health
```

Confirm that the service has a real executable absolute `CODEX_BIN`. If a stale service has invalid configuration and no generation is submitting verification:

```bash
RESTART_STALE=1 ./tools/rethlas/start_verifier_tmux.sh
```

Once the verifier is reachable:

```bash
MAX_ITERATIONS=6 ./tools/rethlas/run_problem_tmux.sh <project> <problem> <session>
```

Report the generation session, the verifier session `rethlas_verifier`, and these commands:

```text
tmux attach -t <session>
tmux attach -t rethlas_verifier
Detach without stopping: Ctrl-b, then d
```

Choose a readable, stable session name when none is supplied. Do not poll every few dozen seconds. Read logs when the researcher requests status or when a finished run needs analysis.
