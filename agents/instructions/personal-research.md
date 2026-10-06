# Personal workflow for geometry research

Use this guide for research planning and tool choices, not as a long prompt loaded every round. AGENTS.md controls evidence and authorization; phase protocols retain their roles. These are workflow recommendations, not measured improvements in mathematical success rates.

## One reviewable gap at a time

The researcher sets the formal problem, importance, and acceptable scope. The agent derives, checks sources, computes, and records evidence. For a new problem, settle geometric objects and conventions before choosing a main route. Each bounded round should produce a derivation, candidate construction, precise failed attempt, reproducible experiment, or checked external theorem. Report honestly when there is no new result.

Use the exploration protocol for initial route comparison, then focus on one critical gap. Work sequentially with one agent by default. Industry use of multiple agents does not authorize parallelism. Prepare independent review packets and launch only within authorization; reverse-checking by the same agent is still self-review.

A short delivery should explain how much of the original problem is resolved, the concrete new result, the weakest step, and its next test. Explain how auxiliary lemmas and special cases connect to the original problem. Existing continuous-search commitments remain in force.

## Reuse known results and explore the remaining gap

Follow `agents/protocols/literature-check.md`. In connected research, reuse existing comparisons and establish known coverage of the original problem and substantial intermediate targets before a long investment. Short derivations can clarify search terms; independent thinking does not require several blind rounds first. Explicit offline-first tasks preserve their statements, routes, and checks for an authorized connected handoff at the PLAN boundary. Do not silently switch modes. Routine calculations need no separate novelty search; complete main candidates immediately follow certification.

Search the original problem, key intermediate claims, and standard equivalent formulations. Trace references and later citations from the closest papers; use authors, MSC classes, or surveys to expand terminology. Abstracts and search snippets are leads. Read exact theorems, hypotheses, and needed proof mechanisms. Different notation or an imperfect direct substitution does not exclude overlap: test specialization, normalization, and short corollaries. Deliver the closest result, precise remaining difference, transformations tried, and the next reuse/check/research decision.

Once applicability is checked, record a known result as a usable input and apply it directly. Do not reprove it by default. Re-derivation needs an advance statement of purpose, scope, and stopping condition, such as checking a questionable step, constant, endpoint, or application. Extensions and alternative proofs need a concrete new goal and should reuse covered portions. Learning usually means reading the relevant proof, not automatically reproducing it in full. If overlap is discovered later, correct attribution, preserve useful derivations, stop duplicating covered work, and do not retrospectively call it planned verification or original progress. Read the closest paper's mechanism before a long proof investment when it addresses the same difficulty.

Keep a compact entry in references.md or a round note: exact claim, standard terminology, actual queries/citation paths, source version and theorem location, coverage, usable inputs, remaining gap, and next decision. Carry relevant comparisons and evidence pointers into later packets. Before web searching or declaring full text unavailable, locate local records/sources by author, title, or ID within allowed inputs. A failed mirror does not erase an available copy, but each application still needs a hypothesis check. Distinguish checked coverage from missing/incomplete coverage. Recheck only for substantive changes, new evidence, untested connections, or freshness requirements. Retry access only with a new source or method. Specify the next test for critical missing material rather than extending research indefinitely under unknown coverage.

An authorized literature task can finish with checked coverage or a reusable input; it need not manufacture a lemma. A proof task must still meet its original acceptance. Preserve single-researcher defaults, quotas, writer ownership, and attribution. Literature input does not raise evidence levels or authorize new modes, calls, or certification bypasses.

Recorded methodological sources, read on 2026-10-02: [Tao on learning and relearning a field](https://terrytao.wordpress.com/career-advice/learn-and-relearn-your-field/), [MathSciNet information](https://mathscinet.ams.org/mathscinet/help/about.html), and [Google Scholar search help](https://scholar.google.com/intl/en/scholar/help.html). These inform purposeful tool learning, classification/citation search, terminology expansion, and backward/forward tracing. Task acceptance and reuse rules are workspace adaptations without measured savings or success-rate claims.

## Organize deep work around the critical gap

An ordinary call or a complete mixed cycle is one execution step; several steps can belong to one mathematical task. Fix its role in the original problem, assumptions, quantifiers, and acceptance first. An easier auxiliary lemma cannot replace that acceptance. Apply auxiliary outputs to the original dependency chain and check parameter consistency, endpoints, constants, and circularity. Record remaining obligations.

Deep work has no minimum duration and need not succeed. A serious unsuccessful task can close with a full failure derivation, precise obstacle, and tested alternative. Continuous-search commitments still apply. Exhausted context, time, or calls mean a saved continuation, not task completion. Report steps, self-reported mathematical acceptance, and independent certification separately.

Ordinary V2 and task-enabled mixed runs retain tasks across calls. Repeated self-reports trigger mechanism review without becoming independently reviewed stagnation. Explain the scope excluded by evidence, why a new mechanism may bypass the obstacle, and a decisive test. Renaming a route is insufficient. Independent review retains its authorization requirements.

## Choose methods for the mathematical task

| Obstacle | Approach | Deliverable |
|---|---|---|
| Missing proof mechanism | Compare representations, symmetric models, and applicable variational/comparison methods; pursue one deeply | Concrete assertion, derivation, failure conditions |
| Possibly overstrong lemma | Fix hypotheses and test extreme, degenerate, and symmetric examples | Candidate satisfying all hypotheses, or unexcluded scope |
| Parametric construction or constant optimization | Fix a checker, generate a small batch, retain improvements | Feasibility checks, raw candidates, errors, reproduction command |
| Needed external theorem | In connected mode, read the source and match hypotheses | Exact statement, location, differences, explicit GAP for unchecked parts |
| Complete candidate | Freeze affected certified use, audit stepwise, obtain authorized independent review | Located findings with evidence |

Riemannian computations should test plausibility and mechanisms; universal conclusions still require continuous arguments. Current research uses natural-language proofs, adversarial examples, and authorized independent stepwise review. Do not introduce Lean or require formalization. Historical formalized labels retain only their original evidence meaning.

## Models and resources

The source workflow recorded official model guidance on 2026-09-14: GPT-6 Astra for difficult research/code work, with Terra/Luna for other cost profiles. Actual availability depends on the tools and account. See the [model documentation](https://learn.chatgpt.com/docs/models) before changing settings.

Use an available strong reasoning model for difficult derivations and critical audits; prefer local scripts for organization, formatting, and mechanical checks. Decide on smaller models from measured savings and rework, not branding or confidence.

Built-in phase defaults and runner.toml overrides differ. The synchronized research setting is medium; first decisions and triggered strategy reviews are high; audit is high; critical-audit is xhigh; stuck-escalation is high. This is a local policy, not an official capability ceiling. Check current documentation and local compatibility before changing models or effort.

For an upgrade comparison, use the same packets on a few representative tasks: a known geometric lemma, a proof with hidden assumptions, an exactly checkable construction, and a theorem-applicability check. Record model, effort, usage, time, errors, and researcher review time. Do not retain only the best run or claim savings/better proofs without such comparisons. Added-cost runs require applicable authorization.

## Adapt research-system ideas to individual work

The recorded examples are [OpenAI First Proof](https://openai.com/index/first-proof-submissions/) and [DeepMind Aletheia](https://deepmind.google/blog/accelerating-mathematical-and-scientific-discovery-with-gemini-deep-think/): complete checkable proofs and feedback, or generation, checking, and revision. The workspace uses candidate, stepwise error search, repair, and recheck while distinguishing self-review from independent certification.

[AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) suggests a fixed evaluator with a small candidate search where the objective can be reliably computed. A model's score cannot replace mathematical correctness.

Large organizations' systems, internal models, and compute are not personal-subscription capabilities. Adapt variant tracking and reuse of useful intermediate results without copying large parallel deployments or upgrading evidence from publicity.

Keep rules concise and load material on demand, as discussed in the recorded [prompting and skills guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra). Preserve evidence requirements; omit repeated surveys and mechanical whole-process instructions from ordinary round packets.
