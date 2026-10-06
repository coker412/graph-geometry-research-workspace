# Authorized multi-agent research

## Dynamic search

When the researcher requests sustained multi-agent work and orchestration is available, the root manages assignments dynamically:

1. Initially send independent blind packets to explorers. Require concrete lemmas, constructions, equations, counterexamples, or precise gaps. Status-only reports, optimism, and calling the essential step routine are insufficient.
2. Maintain method families in `ideas.md`, grouped by mathematical mechanism rather than wording. Record each family's representation, key invariant, decisive subgoal, falsification test, obstacle, and reopening condition.
3. If explorers converge on the same family, retain the deepest or substantively different branches and reassign the others to underexplored families. Use information gain and concrete progress, not vote counts.
4. Keep incompatible approaches until their actual strengths and failures are clear. Only then permit focused combinations, recording parent routes and the new mechanism.
5. Preserve adversarial review. A proof auditor should normally receive only the formal statement, definitions, candidate proof, and dependencies, without persuasive discovery history. Findings must identify exact steps.
6. Under `affirmative-proof`, exhausted registered families trigger renewed exploration rather than an immediate global blocked status. Each such round must change the representation or mechanism; a new mechanism resets the stagnation count.

The root chooses a main route to pursue deeply each round, without imposing a permanent single-route restriction. Within authorized resources, a few independent branches may continue with concrete deliverables and stopping conditions. Their number follows expected information gain, not a fixed quota or duplicated work.

Auxiliary candidates receive stronger stepwise self-checks, counterexample tests, and applicable certification. Freeze their use as certified premises, not all exploration. Conditional derivations must retain assumptions and dependencies and propagate errors; independent routes may continue. Importance, publication potential, or the absence of an independent reviewer does not by itself pause the whole problem. Notify the researcher of these findings. Additional reviewers still require authorization, and self-review cannot raise evidence levels. Complete main candidates trigger whole-problem certification and a pause; required researcher decisions and runtime integrity failures follow queue rules.

Follow queue-core write ownership. In V2, the root combines branch artifacts in ROUND_RESULT, and the runner's transaction writer updates shared state. The root must not directly edit protected files. In manual/compatibility rounds, the root is the sole shared-state writer: append `progress.md`, rewrite `CURRENT_STATE.md`, register substantive progress, important failures, or level changes in `verification-ledger.md`, and update route/dependency files only when their structure changes. Explorers write separate artifacts such as `notes/branches/<round>/<branch-id>/RESULT.md`. Use `templates/blind-research-packet.md` for blind packets.
