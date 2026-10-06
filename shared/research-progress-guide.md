# Assessing mathematical progress

`./queue.sh progress` reports each problem's latest assessment and suggested next action. `./queue.sh status` reports execution status, which does not establish mathematical progress.

```bash
./queue.sh progress
./queue.sh progress --slug example-problem
./queue.sh progress --slug example-problem --json
```

Assess a scoped mathematical gap: obligations removed, premises added, and effect on the main problem. Do not use completion percentages, aggregate scores, word counts, agent counts, or file counts. Scripts check records and versions; independent reviewers assess the mathematical difference. Progress review does not replace proof certification.

## Categories

| Category | Evidence needed | Next action |
|---|---|---|
| Frontier advance | Reviewed removal of an original obligation, with quantifiers, dependencies, and added assumptions stated | Pursue the next bounded target |
| Valid exclusion | Rigorous refutation of a construction, parameter range, or method family | Stop the excluded search; only a whole-family exclusion directly rules out the family |
| Enabling or conditional result | Useful formula/reduction without closing the central gap | Test whether it helps the main problem |
| Experimental signal | Floating-point, sampled, or uncertified computation | Reproduce, stress-test, or seek a rigorous certificate |
| Reformulation | A new expression without demonstrated improvement in the original obligation | Test for a new mechanism |
| Repetition | The same obstacle or rediscovered result/failure | Change mechanism at the repetition threshold |
| Inconclusive | An attempted step without a justified conclusion | Keep the record without presenting it as progress |
| Invalid dependency | An error in a premise | Freeze and repair or retract the affected branch |
| Complete candidate | Claimed closure of all main-problem quantifiers | Follow certification; scripts cannot declare completion |
| Unknown | Missing material, unreviewed self-report, changed evidence, or disputed review | Complete the assessment; do not count mathematical stagnation |

Frontier advance may mean rigorously weakening assumptions on one route, not nearing a full solution. State restrictions such as local models, small parameter windows, or stronger assumptions.

A new transfer formula that still lacks a global estimate is initially an enabling result. Removing an unnecessary derivative assumption can weaken a route's premises. Certifying a root-free parameter window is an exclusion, not a counterexample.

## Round records

Before model execution, the queue saves the original CURRENT_STATE and its SHA-256, then creates:

```text
projects/<project>/notes/progress-assessment/<round>/
├── START.json
├── BEFORE.md
├── PLAN.json
├── PLAN.lock.json
├── RESULT.json
├── RESULT.lock.json
├── REVIEW.template.json
├── REVIEW.json
├── REVIEW.md
└── FINISH.json
```

Locks and review files appear only when their respective steps finish.

At the start, the root supplies stable method-family/obstacle IDs, the actual mechanism, original gap, and falsifiable acceptance target, then seals the plan. Record genuine changes of direction without retroactively changing acceptance to manufacture success.

```bash
conda run -n graphlab python tools/research_progress.py seal-plan   --project projects/<project> --round <round>
```

V2 rounds fill ROUND_RESULT and its progress object: category, main-problem effect, scope, and level. The runner derives and seals assessment RESULT from those same facts. PLAN remains sealed in advance, and proofs are written only once. Derived records bind round, packet, and source-result hashes; they do not overwrite manual RESULT or old locks. Missing information stays unknown. There is no automatic evidence upgrade or added review call; legacy results remain compatible.

Compatibility rounds fill RESULT with precise statements, remaining gaps, removed/added obligations, scope limits, original evidence levels, and project-relative evidence paths, then seal it:

```bash
conda run -n graphlab python tools/research_progress.py seal-result   --project projects/<project> --round <round>
```

This produces REVIEW.template.json. An independent reviewer creates REVIEW.json and a specific comparison in REVIEW.md, with the report's relative path and SHA-256. Author and reviewer must be different people or agents. The reviewer addresses:

1. Was the conclusion already present in the baseline or directly cited old evidence?
2. Which quantifier or obligation is now resolved, and how does this affect the main problem?
3. Has scope narrowed or the difficulty moved into a stronger assumption?
4. If an obstacle was bypassed, what new mathematical mechanism did it?
5. Which next test would decide whether to continue or change route?

The reviewer may replace the author's `frontier-advance` judgment with `enabling-result` or `reformulation`. Preserve both judgments; mathematical truth is not a majority vote.

Reviews follow researcher authorization. Ordinary rounds do not add reviewer calls automatically, and this tool never starts a model. Without a reviewer, the result is `self-report`, not confirmed progress. JSON and hashes do not authenticate a person's identity or establish complete context independence.

In mixed-isolated mode, the offline branch seals PLAN without reading the connected branch. Seal final RESULT and assess progress only after integration. Preserve each finding's provenance and evidence level.

## Continue, change route, or review strategy

After two consecutive independently reviewed rounds of repetition, reformulation, or inconclusive work at the same obstacle without a new mechanism, the next round must change method family. To retain it, PLAN.reopening_basis must point to a concrete new-mechanism note. Renaming an ID is not a new method.

After three rounds without a reduced core gap, review the route's value. PLAN.strategy_review must point to a comparison of alternatives and a continue/pause recommendation. Auxiliary results and valid exclusions still retain their value; three rounds is a scheduling threshold, not a theorem of impossibility.

Missing reviews, timeouts, unknown rounds, or missing sequence numbers interrupt the independently reviewed streak. Retrospective records are explicitly marked and do not count as preregistration or toward consecutive stagnation thresholds. Unfinished packages do not replace the latest complete assessment. Reports inspect the latest 50 assessments; older evidence stays on disk and is not treated as searched.

The system currently provides advice. It does not automatically pause a problem, set `blocked`, remove a certification hold, or alter the search contract. Affirmative searches and zero stagnation thresholds retain their commitment. The researcher decides a whole-problem stop; abandoning a failed route does not abandon the project.

## What file checks establish

Hashes bind baseline, plan, result, evidence, and review. A changed input invalidates the previous review. Exact duplicate recent results/evidence cannot be repeatedly registered as frontier advances; renamed or semantically restated claims still need independent review. Project-bound path checks reject outside evidence and escaping symlinks.

These checks do not prove theorems, certify levels, or prevent fabrication by someone able to rewrite all records. The researcher can follow the report's evidence paths. Direct evidence controls when ledgers disagree.

Prepare a manual assessment:

```bash
conda run -n graphlab python tools/research_progress.py prepare   --project projects/<project> --round attempt-00000001-manual --attempt 1
```

Sealing preserves existing versions. Correct a sealed record in a new assessment while keeping the old package; its review cannot certify the revision. Use `prepare --retrospective` for later corrections or historical assessments, optionally with `--baseline notes/<evidence-file>` relative to the project.

## Self-reported scheduling feedback and tasks

Absent independent REVIEW still means no independently reviewed advance or stagnation. A separate self-report window triggers `review-strategy` after either:

- Two consecutive completed prospective steps at the same obstacle in the same task, including enabling-result, experimental-signal, and frontier-advance labels.
- Three consecutive steps reporting only auxiliary results, computational leads, route exclusions, or inconclusive work.

Failures, missing steps, unfinished/retrospective records, task changes, or ineligible categories interrupt the applicable window. Existing certification/route-change decisions take precedence. Changing the category alone does not reset the same-obstacle window. The next PLAN must reference a mechanism-comparison report; sealing binds its hash and resets the observation window.

The comparison identifies the failure derivation, excluded scope, tested new mechanism, and a test linking it back to the original problem. Repeating that an estimate is missing is insufficient. Scripts check existence and hashes, not the adequacy of the mathematics. This feedback uses the existing decision step at high effort; it does not add independent reviews, paid calls, or whole-problem holds.

With task-enabled ordinary V2 or mixed-isolated runs, the same objective persists across calls. Progress reports separate execution steps, self-reported accepted tasks, exhausted routes, and unfinished tasks. Check acceptance claims against evidence; certification and completion boundaries remain unchanged. See the [runtime guide](runtime-v2-guide.md).

In mixed mode, the offline branch seals task PLAN, integration fills RESULT.research_task, and the runner validates and atomically saves task state without counting replay twice. Old START=0 rounds keep their protocol. Structured route changes remain V2-only; mixed runs keep compatibility records. `partial-result` describes scope rather than proof certification. Neither it nor `proof-draft` can become a certified frontier advance or exclusion through progress REVIEW alone.
