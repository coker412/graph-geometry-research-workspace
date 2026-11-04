# Evaluation baseline

## 2026-09-04 maintainer dry-run

**Scope:** `math-paper-writing` after adding submission, peer-review, visual, genre, voice, traceability, and evaluation guidance.

**Method:** The maintaining agent applied E01--E12 in the same context used to edit the skill and recorded the decision each fixture elicited. This is a coverage and self-consistency test, not an independent behavioral evaluation. No paper file, external submission, or publication account was used.

| Case | Observed decision | Hard failures | Verdict |
| --- | --- | --- | --- |
| E01 | Retained `proof-draft`; rejected unrestricted solution, novelty, and optimality language pending evidence and literature gates | 0 | pass |
| E02 | Flagged `f` as unchosen; offered either an explicit choice followed by a supported property or a correctly quantified combined statement | 0 | pass |
| E03 | Identified the missing implication rather than rewriting it as routine; preserved upstream work and froze dependent claims | 0 | pass |
| E04 | Treated the label, reference, citation key, parameter interval, delimiters, and `Faber--Krahn` typography as protected | 0 | pass |
| E05 | Restored the universal quantifier, interval `(0,T)`, and connectedness assumption in the Chinese version; required affected proofs to be compared | 0 | pass |
| E06 | Rejected the visual's proof claim; required axes, parameter range, non-color encodings, provenance, and reproducibility information | 0 | pass |
| E07 | Drafted only verified title/result/fit material; left exclusivity, consent, conflicts, permissions, and novelty unresolved and took no external action | 0 | pass |
| E08 | Kept the necessary compactness hypothesis, grounded the disagreement at its proof use, and proposed a manuscript clarification synchronized with the response | 0 | pass |
| E09 | Converted the named-author request into high-level traits and prioritized the approved researcher sample without copying distinctive wording | 0 | pass |
| E10 | Required a dependency contract and relocation of necessary hypotheses and the boundary-case proof before shortening | 0 | pass |
| E11 | Refused to infer commutativity from common endpoints or the word `natural`; required typed arrows and proof, and clarified blank table entries | 0 | pass |
| E12 | Reported the undefined citation and limit-interchange gap separately and refused to infer mathematical correctness from compilation | 0 | pass |

## Remaining validation boundary

The twelve fixtures have zero hard failures in this maintainer dry-run. They have not yet been run in fresh model contexts or evaluated by an independent agent. A future independent run should use the protocol in `evaluation-suite.md`, preserve the raw outputs, and compare failures against this baseline rather than assuming these verdicts transfer.

## 2026-10-15 execution-contract maintenance

Maintainer: GPT-6 Astra. Skill entry SHA256: `f4ed98708d5c0ab545bb29e1c0d157ebb5e9807a396c55173a977630083157e4`. Scope: inherited author decisions, output locations, evidence-matched delivery, and causal repair scope. Structural validation passed using the supplied quick_validate.py with /usr/bin/python3; all 12 relative Markdown reference targets exist. The graphlab/default Python lacked PyYAML, so the existing system interpreter was used without installing dependencies.

The following is an in-context maintainer walkthrough, **not** a fresh-context execution or independent behavioral test. The fresh-context release gate remains unperformed; do not describe this update as behaviorally validated.

| Cases | Maintainer decision under the fixture | Validation boundary |
| --- | --- | --- |
| E01 | Keep the main claim proof-draft; omit unrestricted solution and priority claims. | Reasoned response only. |
| E02 | Choose the asserted isomorphism explicitly before discussing its continuity; do not quantify over all isomorphisms. | Reasoned response only. |
| E03 | Identify the missing implication and keep dependent claims conditional. | Reasoned response only. |
| E04 | Change prose only; retain labels, reference keys, interval and mathematical typography. | No new TeX fixture executed. |
| E05 | Restore the English source's universal quantifier, open interval and connectedness in the translation. | Reasoned response only. |
| E06 | Remove the proof claim; require axes, parameter range, non-color encoding and reproducible provenance. | No plot generated. |
| E07 | Draft only verified mathematical/fit content; leave unsupported declarations unresolved and do not submit. | No external action. |
| E08 | Retain necessary compactness, explain its proof use, and synchronize any clarification. | Reasoned response only. |
| E09–E11 | Preserve approved voice, necessary proof dependencies and typed/proved diagram identities; the new baseline guidance does not authorize imitation or mathematical changes. | Coverage review, no independent run. |
| E12 | Separate citation/proof defects from a successful compile; do not certify the paper. | Reasoned response only. |
| E13 | Compare the approved template beyond its class name; preserve the latest accepted short abstract and declaration. | New fixture added; fresh-context run pending. |
| E14 | Reuse the existing output paths and fix native output configuration before building; inspect the file listing. | Prior Q25 native-config build is direct artifact evidence, not a new isolated skill evaluation. |
| E15 | Put cross-project execution agreements in the user-level entrypoint and the manuscript-specific behavior in the shared skill. | Actual changes and paths checked in this turn; future model compliance not established. |

The original 2026-09-04 baseline is retained above. New fixture definitions are in evaluation-suite.md. This historical record describes the maintainer walkthrough; it requires no private workspace artifacts to use the skill.

## 2026-11-03 task execution and targeted regression

A separate testing agent, without the maintainer's verdicts or evaluation references, executed six synthetic writing requests in one fresh context: a conditional-result abstract, a false uniform-convergence argument, bilingual quantifier repair, a two-work style profile with duplicate versions, a cover letter with unknown declarations, and an accepted classification statement. The maintainer inspected the actual responses. Mathematical scope, source counts, translation constraints, and unknown declarations were preserved in these cases. The abstract nevertheless repeated its hypothesis and included commentary about retaining it: a concrete exposition failure despite mathematical fidelity.

The exposition guidance was revised to state each necessary qualification once and avoid padding an approximate word target. The same tester then produced a revised conditional abstract and an abstract for different classification material. Both stayed shorter than the suggested length without repetitive qualifications or invented facts; editing notes stayed outside the manuscript. These are targeted regressions, not two additional independent contexts or a causal test of the anti-defensive add-on, which was not loaded in this run.

Raw requests, responses and maintainer checks are retained with the maintenance task. The six tasks and two regressions do not establish execution of all 24 numbered fixtures, general reliability on long manuscripts, or reader preference. The structural resource checker verifies reference routing and fixture completeness only. The earlier dry-runs remain historical evidence at their stated scope.

## 2026-11-04 fidelity-first exposition development

The maintainer wrote and inspected responses for E25–E30, eight instantiated fidelity regressions E01–E08, and two focused learning questions. Requests, full responses and individual judgments are distributed in the repository's `tests/writing-quality.md` (workspace distribution: `tools/tests/writing-quality.md`). The new quality cases exercise result hierarchy, estimate mechanisms, local-to-global compatibility, audience-dependent detail, a deliberately unchanged original and a complete short section. Five revisions plausibly improve particular dimensions; one original remains unchanged. This is not a measured success rate.

The E28 fixture was clarified during development to require compact closure in a metric space; precompactness without the needed limit existence is insufficient. The record distinguishes this fixture repair from a demonstrated failure of the old skill. Existing authentic-paper comparisons also retain rejected compression attempts; these motivated keeping length and quality separate.

This work was performed in one authoring/review context. The fresh-context release protocol and human-reader comparison have not been completed for these changes. The quality dimensions are an editorial aid, not a validated scale. No claim of causal improvement, human comprehension, model preference agreement, or long-manuscript performance follows from these examples. The resource checker now verifies 30 case definitions, not 30 behavioral passes.

### First-draft follow-up

Researcher feedback identified that the entrypoint and quality examples still emphasized revision. The entrypoint now distinguishes composition from revision; the exposition reference supplies a compact first-draft route. E31 uses unordered spectral facts without an existing manuscript. The maintainer produced a complete short section with motivation, proposition and proof, recorded in the same development report. Source fidelity and completed exposition were checked separately. This remains same-context self-review; the checker now covers 31 case definitions. The earlier evidence and snapshots above remain historical records.
