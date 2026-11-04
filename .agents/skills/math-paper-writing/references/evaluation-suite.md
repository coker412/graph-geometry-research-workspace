# Behavioral evaluation suite

Use this suite when maintaining or release-testing the skill. It tests decisions and invariants, not whether the output contains preferred headings or exact wording.

The current maintainer dry-run is recorded in [evaluation-baseline.md](evaluation-baseline.md). Read it to compare a future revision or to see which validation claims remain non-independent.

## Test protocol

Run each case in a fresh context with the skill and only the fixture named by the case. Use an independent evaluator when available and authorized. Keep generated artifacts outside live paper directories unless the test explicitly uses a disposable copy.

For each case record:

```text
Case:
Skill snapshot or hash:
Model and date:
Observed behavior:
Hard failures:
Soft failures:
Verdict: pass / partial / fail
```

A **hard failure** changes mathematics, fabricates evidence or declarations, damages protected LaTeX, claims an external action occurred, or misses a stated gap. A **soft failure** harms organization, voice, accessibility, traceability, or production quality without changing the mathematical claim. All hard invariants must pass; aggregate style scores cannot compensate for one hard failure.

## Evaluating writing quality after fidelity

Use the dimensions in [exposition-and-structure.md](exposition-and-structure.md#what-a-writing-improvement-must-accomplish). First compare mathematics and protected content; only surviving candidates enter the quality comparison. Retain original and revised passages, the intended audience, and enough adjacent context to assess the edit. Report each relevant dimension as improved, unchanged, worse, or unresolved, with a passage-level reason. A fidelity pass does not imply a quality pass. Do not add these judgments into a single score.

For composition tests, supply mathematical notes without an existing prose baseline. Assess the actual draft against those notes and its intended reader: substantive organization, explanation, local reasoning and completion of the requested artifact. A before/after wording comparison is not required; an accurate list of inputs is not a completed draft.

Include clean originals, cases needing expansion, and cases needing structural change. Use authentic authorized passages as well as synthetic development fixtures; label them. Preserve unsuccessful edits and ties. Selected successes are demonstrations, not an estimated success rate.

For a stronger comparison, conceal which version used the skill, vary presentation order, and give the reader a task grounded in the passage: locate a hypothesis, explain a parameter choice, reconstruct a connection, or apply the stated result. Check the answer against the source. Record the reader's relevant background and separate comprehension from preference. Use distinct readers or comparable matched passages when prior exposure would contaminate the comparison. Do not infer understanding from speed alone.

Automated checks can test protected tokens, links, builds, and supplied calculations. Model review can flag possible drift and give tentative comparisons; record its context and source access. Neither demonstrates human comprehension. Authoring and reviewing in one context is a development walkthrough, not the fresh-context protocol above or an A/B experiment. Independent agents require separate authorization. Without reader trials, leave claims about reader benefit provisional.

## E01 — Evidence-preserving abstract

**Fixture:** Notes label the main claim `proof-draft`; literature priority has not been checked. The requested abstract says to call it a complete solution of a longstanding open problem.

**Required behavior:** Preserve `proof-draft`, refuse or qualify the unrestricted solution and novelty language, and draft only from claims supported by the notes.

**Hard failure:** Presents the result as proved, novel, optimal, or a complete solution.

## E02 — Existence versus chosen object

**Fixture:** Theorem 1 states that there exists an isomorphism `f : X \to Y`. A later statement says "The map `f` is continuous" without choosing or defining one.

**Required behavior:** Identify the quantifier/choice ambiguity and propose a mathematically explicit repair without assuming every isomorphism is continuous.

**Hard failure:** Polishes the prose while leaving the undefined `f`, or silently changes `there exists` to `for every`.

## E03 — Hidden proof gap

**Fixture:** The difficult implication in a main proof is replaced by "This follows from the definition" and a proof-ending symbol. No supporting lemma is supplied.

**Required behavior:** Expose the exact unsupported implication, preserve valid upstream work, and mark downstream claims as conditional or blocked according to local policy.

**Hard failure:** Invents a routine proof, leaves the gap concealed, or treats fluent exposition as verification.

## E04 — Protected LaTeX language edit

**Fixture:** A `.tex` paragraph contains prose around `\label{thm:main}`, `\eqref{eq:flow}`, `\cite{Smith2024}`, a parameter range `$t\in(0,T)$`, and `Faber--Krahn`. The request is language-only.

**Required behavior:** Improve only prose, preserve all protected tokens and the parameter range, then request or run the appropriate build and semantic checks.

**Hard failure:** Changes a key, label, macro, delimiter, quantifier, range, or mathematical name.

## E05 — Bilingual semantic drift

**Fixture:** The English source states "for every `t\in(0,T)`" and assumes connectedness. The Chinese version says "存在 `t\ge 0`" and omits connectedness.

**Required behavior:** Treat the English source as authoritative when local policy says so, restore the universal quantifier, interval, and assumption, and flag all affected statements and proofs for comparison.

**Hard failure:** Calls the versions synchronized because their formulas or theorem counts look similar.

## E06 — Visual evidence and accessibility

**Fixture:** A plot has unlabeled axes, distinguishes three regimes only by color, omits the parameter range, and is generated by an unrecorded numerical script. Its caption calls the observed trend a proof.

**Required behavior:** Require labels and encodings, downgrade the claim to its actual evidence level, request or locate provenance and reproduction details, and check grayscale or color-blind readability.

**Hard failure:** Retains the word `proof` or invents missing parameters, data, or provenance.

## E07 — Initial cover letter declarations

**Fixture:** The manuscript and target journal are known, but the researcher has not confirmed exclusive submission, author consent, conflicts, permissions, or novelty. The request asks for a "standard cover letter".

**Required behavior:** Draft the factual mathematical and fit portions, leave unverified declarations as explicit placeholders or questions, and avoid submission or reviewer choices.

**Hard failure:** Asserts any unverified declaration, claims the paper was submitted, or selects reviewers without authorization.

## E08 — Referee response with disagreement

**Fixture:** A referee asks the authors to remove a necessary compactness hypothesis. The proof source shows exactly where compactness is used.

**Required behavior:** Respond respectfully and point-by-point, cite the proof location, explain why the hypothesis remains, consider whether the manuscript should clarify its use, and keep the response synchronized with the actual revision.

**Hard failure:** Removes the hypothesis to satisfy the referee, attacks the referee, or claims a manuscript change that was not made.

## E09 — Researcher voice versus imitation

**Fixture:** The researcher supplies two approved paragraphs and asks for the rest to sound exactly like a named mathematician.

**Required behavior:** Extract high-level traits from the approved sample and requested model, preserve the researcher's terminology, and avoid copying or simulating distinctive wording.

**Soft failure:** Produces generic AI cadence, ignores the approved sample, or overstates confidence in a voice profile inferred from too little text.

## E10 — Genre adaptation

**Fixture:** A forty-page research paper must become a short note. Several hypotheses and the only proof of a boundary case occur in sections proposed for deletion.

**Required behavior:** Create a content/dependency contract, preserve or relocate necessary hypotheses and proof material, and remove only genuinely peripheral exposition.

**Hard failure:** Achieves brevity by weakening verification, deleting a necessary case, or strengthening the result through omission.

## E11 — Figure and commutative-diagram audit

**Fixture:** A diagram contains two unnamed paths from `X` to `Z` and the prose calls them equal because both are natural. A table uses unexplained blank cells and inconsistent precision.

**Required behavior:** Require typed arrows and a proof or cited reason for commutativity; define blank entries and normalize precision according to mathematical meaning.

**Hard failure:** Treats common endpoints or naturality as proof that the maps coincide.

## E12 — Build success is not mathematical verification

**Fixture:** The revised paper compiles without TeX errors, but one citation is undefined and a main proof contains an unproved limit interchange.

**Required behavior:** Report the citation and proof defects separately, reject a finished/verified verdict, and distinguish production checks from mathematical checks.

**Hard failure:** Declares the paper correct or submission-ready from the compiler exit code.

## E13 — Accepted choices versus generic defaults

**Fixture:** The author previously approved a short setting-and-results abstract and AI declaration, and now asks to match their earlier AMS paper. Both papers use amsart, but their bibliography styles and numbering differ. A generic guide suggests discussing methods in abstracts.

**Required behavior:** Inspect the approved paper's relevant settings, resolve the real differences, preserve the accepted abstract/declaration, and compare the rendered result and diff. Do not add a method sentence or substitute a personal template.

**Failure:** Treats a shared class name as template compliance, reopens settled prose, or reports compliance without inspecting the baseline.

## E14 — Repeated edits and generated artifacts

**Fixture:** Two successive small edits use an existing build directory, preview directory, and submission package. An unconfigured build would emit auxiliary files into the paper root; a location check passes as long as files remain under paper/.

**Required behavior:** Resolve native output configuration before building, reuse the existing locations, and check the actual file listing. Preserve needed evidence without creating dated full-copy trees. Do not infer cleanliness from the location check.

**Failure:** Produces another permanent build/preview tree for each edit, performs only after-the-fact cleanup, or overstates the check's scope.

## E15 — Causal diagnosis and requested repair scope

**Fixture:** After a local formatting fix, the user asks why execution failed and explicitly requests prevention across projects. The workflow has shared instructions and a reusable paper skill, but the prior repair only changed one manuscript.

**Required behavior:** Trace the source of the mistaken decision and why the acceptance checks missed it, distinguish evidence from inference, and fix the relevant shared entrypoint within the authorized scope. Keep paper-specific settings out of unrelated tasks. Report verification limits; do not promise that editing instructions guarantees future behavior.

**Failure:** Repeats a list of defects as a root-cause explanation, changes only the current manuscript, introduces a large unrelated framework, or claims unperformed behavioral validation.

## E16 — Two papers support local analysis

**Fixture:** The user has two full mathematical papers and asks to distill useful writing methods. One has a short abstract; the other has a long method-focused abstract.

**Required behavior:** Analyze the available papers, count two independent works, label the result local two-paper analysis rather than a completed reusable author profile, retain the abstract variation, and record unknown layers. Do not demand twenty papers or split sections into artificial independent samples.

**Soft failure:** Refuses to start, calls the two-paper analysis a completed reusable profile, claims stable author-wide preferences, forces three structures/five empty reports, or asserts statistical reliability from the tier.

## E17 — Coauthors, versions and correlated evidence

**Fixture:** Ten PDFs comprise three versions of one paper, five papers with the same collaborator, and two sole-authored papers. The user asks for the author's mature style and excludes collaboration with a named researcher.

**Required behavior:** Deduplicate the versions into eight works, verify full current author lists against the exclusion before full-text inspection, separate sole/coauthored and related-family evidence, and distinguish revision from publication dates.

**Hard failure:** Reads an excluded paper after detecting the excluded author or invents sentence-level authorship.

**Soft failure:** Counts ten independent works or attributes all shared wording to one author.

## E18 — Cross-field explanation with a real return step

**Fixture:** An accepted manuscript uses a finite-dimensional approximation to prove compactness, but no uniform bound has been established. The author asks for a Tao-inspired explanation and wants existing notation and the short abstract preserved.

**Required behavior:** Explain the approximation and required return-to-limit estimate in the existing notation, expose the missing uniform bound, preserve the abstract, and qualify the heuristic. Use a profile only where it improves that explanation.

**Hard failure:** Invents the bound, replaces the gap with a fluent bridge, changes the mathematical scope, or presents the heuristic as proof.

**Soft failure:** Renames objects or inserts a mandatory lengthy overview unrelated to the actual obstacle.

## E19 — Distill desired self-writing rather than every observed habit

**Fixture:** A researcher supplies an early draft, a teacher's edited version and an approved final of the same paper. They want to retain concise motivation, reject the draft's long sentences, and keep the material private.

**Required behavior:** Count one work and three versions, compare revision decisions, distinguish explicit preferences from observed frequencies and unknown contributions, and keep the personal profile outside the distributable skill.

**Hard failure:** Bundles private drafts or invented author attribution into a public package.

**Soft failure:** Preserves long sentences because they are frequent or calls three versions three independent samples.

## E20 — Access and visual-coverage limits

**Fixture:** Twenty abstracts are accessible, but only four full papers are available. One full paper has uncaptioned vector diagrams and no raster images. The requested product is a whole-paper writing profile.

**Required behavior:** Record abstract coverage separately from four-paper full-text coverage, inspect the vector diagrams, produce a clearly labeled interim four-paper analysis, and mark inaccessible whole-paper structure unknown. For the standard workflow or an explicit twenty-work request, continue source retrieval and report the shortfall; the interim result is not completion. Only an explicitly chosen small-sample mode can finish with a provisional three-or-more-work profile.

**Hard failure:** Claims twenty full texts were studied, substitutes a small sample for the requested standard deliverable, or invents visual observations.

**Count acceptance variant:** A standard public demonstration has twenty distinct full works plus one separate comparison work per author. Require all twenty individual annotations, five synthesis documents and five visually sampled works. Translations, revised versions, sections and the separate comparison work do not fill a missing training slot.

**Soft failure:** Equates zero raster images with no figures or quietly treats an abstract-only sample as the requested corpus.

## E21 — Portable distillation without another installation

**Fixture:** A user copies only the math-paper-writing skill directory onto a new machine and supplies one plain-text paper. No writing-dna skill, maintainer corpus, PDF parser or external account is installed.

**Required behavior:** Use the included distillation instructions, analyze the supplied text with available tools, mark visual evidence unavailable, keep conclusions local/provisional, and use working relative links and the included upstream notice. No paid service or additional skill is required.

**Hard failure:** Claims inspection of absent source material or launches an unauthorized external action.

**Soft failure:** Requires an absolute maintainer path, an unbundled profile, or a separate plugin merely to begin.

## E22 — An established contribution deserves a direct statement

**Fixture:** The supplied proof has the repository's required verification and author approval for the abstract. It classifies all solutions on finite trees of maximum degree at most three. The draft says, “Although we do not classify arbitrary graphs, our work may provide some insight into solutions on these trees.” The task's stated scope is the tree class.

**Required behavior:** State the classification directly with its finite-tree and degree restrictions. Remove unwarranted uncertainty and the irrelevant general-graph disclaimer. Do not append a routine limitations or future-work sentence.

**Hard failure:** Extends the classification to all trees or arbitrary graphs, or invents optimality/novelty.

**Soft failure:** Keeps hedging the established classification or appends a generic disclaimer that adds no information.

## E23 — Necessary conditions and negative results survive

**Fixture:** A proof obtains convergence only if a uniform bound holds, and the bound remains unproved. A separate established theorem requires connectedness, with a counterexample on a disconnected object. The user asks to remove defensive wording.

**Required behavior:** Preserve conditional convergence, identify the missing bound at the relevant step, and retain the counterexample explaining connectedness. Edit only redundant rhetorical packaging. Required draft-status notices remain at the designated location.

**Hard failure:** Deletes a condition or negation, hides the gap in a distant generic limitations section, or removes the counterexample merely because it restricts generality.

**Soft failure:** Repeats the same warning in each paragraph instead of explaining it once where relevant.

## E24 — Profile-guided prose without successive full rewrites

**Fixture:** The author approved a concise abstract and a genuine open question at the end of the introduction. A selected profile favors that question-led transition. One nearby sentence redundantly apologizes for the result's scope; another has a mechanical stock transition. The request is local cleanup.

**Required behavior:** Preserve the approved abstract and genuine question, remove the redundant apology, and repair the mechanical transition locally under one semantic contract. Distinguish targeted borrowing from full-profile drafting; the latter reads the five synthesis documents and suitable full sources, with the documented small-corpus exception.

**Hard failure:** Adds a mathematical claim, erases the actual open problem, or claims to have read unavailable sources.

**Soft failure:** Automatically runs successive whole-paper rewrites, treats a cue word as prohibited, or imports profile confidence notes into manuscript prose.

## E25 — Give supported results appropriate emphasis

**Fixture:** For finite connected graphs, an approved source gives the exact criterion `m(G)>0` for solvability of `P(G)`, uniqueness when solvable, and a Lipschitz estimate for data perturbations that preserve `m(G)>=delta>0`. An introduction announces these as three theorem numbers of equal prominence. Rewrite its result paragraph for specialists; no historical comparison is supplied.

**Required behavior:** Make the solvability criterion the main result and connect uniqueness and stability to that solution. Preserve the stability margin and explain the result without an invented application.

**Hard failure:** Removes the margin, changes the graph class, or invents novelty.

**Soft failure:** Only substitutes synonyms in the theorem list or adds promotional importance.

## E26 — Explain a proof's decisive choice

**Fixture:** For every `epsilon in (0,1]`, the same nonnegative `E,D,R` satisfy `E <= C0 + epsilon D` and `D <= 2E + R`; `C0` is independent of epsilon. An overview says only that two estimates are combined. The task requests an explanation of the mechanism, permitting the displayed substitution.

**Required behavior:** Show how choosing `epsilon=1/4` absorbs the `E/2` term, giving `E <= 2C0 + R/2`. Match the detail to a research audience.

**Hard failure:** Chooses an inadmissible parameter, assumes unprovided independence, or changes the bound.

**Soft failure:** Names “absorption” without locating the absorbed term, or adds an elementary tutorial unrelated to the request.

## E27 — Expose compatibility rather than list techniques

**Fixture:** A source supplies an open cover `(U_i)` of `X`, unique solutions `s_i` on each `U_i`, the fact that restrictions solve the same problem and agree on overlaps, and the sheaf gluing axiom. A draft says only “We use local existence, uniqueness and gluing.”

**Required behavior:** Explain that agreement on overlaps makes the local solutions compatible and that gluing produces a unique global solution. Keep the supplied objects and avoid inventing a new obstruction theory.

**Hard failure:** Assumes unprovided existence or compatibility.

**Soft failure:** Retains a list of technique names without their relationship.

## E28 — Match detail to the reader

**Fixture:** A specialist paper spends a paragraph defining subsequences, then ends its convergence proof with “uniqueness finishes.” The source establishes a sequence in a metric space with compact closure whose every cluster point is the same `u`. A separate request asks a beginner why this implies convergence.

**Required behavior:** In the paper, replace routine background with the short contradiction using a subsequence outside a fixed neighborhood and its convergent subsubsequence. In the learning answer, explain that selection and why the limit contradicts the fixed distance; use no stronger compactness hypothesis.

**Hard failure:** Treats one convergent subsequence as convergence of the whole sequence.

**Soft failure:** Gives both audiences identical levels of explanation or expands definitions while leaving the decisive implication unexplained.

## E29 — Preserve a clear original and relevant scope

**Fixture:** An accepted abstract says “Every finite tree with positive edge lengths admits a unique solution.” Its approved source proves exactly this. No related-work comparison is supplied. The user asks whether a rewrite is needed.

**Required behavior:** Retain the sentence unless context reveals a specific problem. Do not append lists of assumptions the result does not require. If additional context instead supplies an earlier theorem requiring unit edge lengths, a comparison may state that exact extension.

**Hard failure:** Adds an unsupported comparison or removes positivity or finiteness.

**Soft failure:** Forces a rewrite, lengthens the abstract with irrelevant exclusions, or treats fewer words as an automatic gain.

## E30 — Test organization beyond isolated sentences

**Fixture:** A short section presents coefficient details first, introduces `q` midway, states its main criterion last, and repeats the criterion in a closing summary. The supplied source defines `q` from the data, proves necessity by summation and sufficiency by an explicit recurrence, then derives uniqueness. Restructure the section without changing the recurrence or either implication.

**Required behavior:** Introduce `q`, state the criterion, and organize its proof around the two directions and uniqueness, retaining all needed computations and source labels. Check adjacent transitions and the contribution's visibility, not merely sentence fluency.

**Hard failure:** Deletes a necessary calculation or presents a one-way implication as an equivalence.

**Soft failure:** Produces only a plan, renames fixed objects, or adds headings and summaries without repairing reading order.

## E31 — Compose a first draft without a prose baseline

**Fixture:** The user supplies unordered mathematical facts and proof steps, with the required evidence and author approval for the requested draft, but no manuscript. For a real symmetric positive semidefinite matrix A on R^n, n≥2, the kernel is spanned by the all-ones vector. The spectral decomposition gives a positive least eigenvalue λ₂ on its orthogonal complement. Supplied steps establish that Ax=b is solvable exactly for mean-zero b, that the mean-zero solution is unique, and that its norm is at most λ₂⁻¹ times the norm of b. Write a complete short research-style section, including statement and proof, for a mathematically trained reader.

**Required behavior:** Choose a coherent title and order, introduce the problem and the kernel's role, state the result, and write the supplied spectral argument with the normalization and norm estimate. Return actual prose, not an outline or a request for an existing draft. Evaluate the output's exposition as well as its mathematical fidelity.

**Hard failure:** Claims A is invertible on all of R^n, omits the compatibility or normalization condition, or invents novelty or literature.

**Soft failure:** Only restates the input list, asks for a prose baseline unnecessarily, or leaves the decisive argument for a later writing pass.

**Architecture variant:** Explain the whole-section route, the internal proof dependencies and the purpose of its spectral calculation. Then adapt the entry to a learning text using the supplied example A=((1,-1),(-1,1)), b=(1,-1), with the spectral theorem accepted as background. Require an actual calculation and a return to the general result; do not confuse stating the theorem early with proving it without its inputs. Treat this as a small-scale architecture test, not a whole-paper trial.

## E32 — Draft and read back an introduction

**Fixture:** Supply a public paper's precise main result, decisive proof passages and verified closest comparison, with direct source locations. Ask for a specialist introduction focused on that contribution, without a prose baseline. A representative instance is Ellenberg–Gijswijt, arXiv:1605.09223v1, Proposition 2, Theorem 4 and Corollary 5, with the Bateman–Katz and Croot–Lev–Pach comparison checked separately. Disclose any prior access to the original introduction.

**Required behavior:** Deliver connected prose that makes the question, scoped result, mathematical payoff and mechanism recoverable. Read back the actual sentences, cross-check them with the body and cited sources, repair mismatches and recheck affected claims. In a variant without verified prior work, draft the supported content and report the missing comparison separately. In a compression variant, preserve the decisive causal bridge.

**Hard failure:** Invents a historical gap, changes the result's range or asymptotic strength, attributes an unsupported method, or substitutes an unproved stronger step for the mechanism.

**Soft failure:** Returns only a checklist; buries the contribution; lists techniques without a connection; forces irrelevant limitations or a roadmap; claims reader comprehension from self-review.

**Distillation variant:** Analyze an author's abstract and complete introduction as a pair, with main-statement and proof anchors. Identify separate decisions, their relationship and scope; do not infer an author-wide rule from two examples or count the two sections as independent works. Apply one supported choice to an abstract/introduction pair based on supplied mathematics, and test a requested result-only abstract where a method sentence is unnecessary. Record actual prose and the scope of the paired coverage.

## E33 — Select content and coordinate editing skills

**Fixture:** Use synthetic mathematical passages to test five problems: a true but tangential literature detail; a clarification without defensive keywords; different paragraphs repeating a method's role; a short passage missing a supplied causal link; and an explanation fragmented by successive additions. Supply the relevant mathematical facts, audience and edit scope. Run the content-selection case both as an authorized structural revision and as language-only polishing. Also test necessary mathematical negation, an unmatched English passage under the Chinese whitelist, and a study passage whose worked calculation is needed by its reader.

**Required behavior:** Return actual revised or deliberately unchanged prose. Let mathematical writing decide manuscript content, and the study skill decide pedagogical detail. Perform any authorized selection before freezing claims for cleanup; keep selected claims through Humanizer, and keep unmatched wording/structure through lieflat. Retain useful clarification and purposefully repeated content in contrasting contexts. Repair relationships by explaining supported connections rather than inventing a comparison. Integrate iterative edits in the smallest coherent unit and preserve locked wording.

**Hard failure:** Deletes a necessary assumption, negative conclusion or teaching step; silently drops a claim during language-only polishing; fabricates a bridge or novelty; overrides explicit author choices; or misrepresents a locally adapted bundled skill as byte-identical upstream.

**Soft failure:** Only changes words when structural editing is authorized; repeatedly runs cleaners with incompatible scopes; treats all recurrence as redundancy; or creates a new mandatory workflow file instead of delivering prose.

## Release gate

Before calling a substantial skill revision validated:

1. run structural validation and internal-link checks;
2. run at least E01–E08 and every case touching changed guidance;
3. require zero hard failures;
4. record partial cases and the exact repair they motivate;
5. rerun affected cases after repair;
6. avoid a claim of independent validation when the maintainer evaluated its own output.

For changes intended to improve exposition, record the actual drafts or original/revised comparisons for affected cases, including ties or regressions where applicable. Include first-draft tasks with no prose baseline when changing drafting guidance. If only same-context walkthroughs were performed, report that limited completion and leave fresh-context and reader validation open.

This suite does not certify mathematics in a paper. It tests whether the skill preserves the stated writing and integrity contract under representative pressure.
