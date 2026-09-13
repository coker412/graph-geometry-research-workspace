---
name: math-paper-study-guide
description: Create or revise detailed Chinese study editions of mathematical research papers and proof drafts, with staged reading, prerequisite refreshers, expanded calculations, learning checkpoints, and proof reconstruction. Use for learning-facing companion notes or internal Chinese proof guides; do not use for submission manuscripts, ordinary translations, or evidence upgrades.
---

# Mathematical Paper Study Guide

Turn a mathematically stable source into a Chinese document that a reader can learn, recalculate, and eventually reconstruct without the source. Keep this deliverable separate from the submission manuscript: a study edition may be longer and more pedagogical, but it must remain faithful to the source mathematics.

## Apply local policy and choose the source of truth

Read applicable repository instructions first. Identify:

- the exact paper, proof draft, or frozen snapshot being explained;
- its evidence level and unresolved gaps;
- the intended reader and the amount of background they have;
- whether the task is explanation-only or also includes mathematical auditing;
- which theorem, equation, and citation labels should remain aligned with the source.

Do not silently complete gaps, alter hypotheses, or promote a proof draft to an established result. New pedagogical derivations inherit the source's evidence level at most; if they have not been independently checked, say so in one concise status box outside the mathematical narrative.

If the formal paper is also being edited, use the `math-paper-writing` skill for that work, stabilize the paper first, and derive the study edition from the resulting snapshot.

## Read the archived method

For a new study edition or a structural rewrite, read [chinese-study-edition-method.md](references/chinese-study-edition-method.md). It records a reusable architecture for staged reading and proof reconstruction. Use [main-study-zh-template.tex](assets/main-study-zh-template.tex) when a project does not already have a compatible LaTeX structure.

## Build the study edition

1. Reduce the proof to a one-sentence mechanism and a dependency chain. Keep separate accounts for logically distinct tasks such as positivity versus growth, or existence versus regularity.
2. Open with the precise question, the exact result, the source/version status, and a two- or three-pass reading plan. Tell readers what they may skip on the first pass.
3. Organize the mathematical body in the same dependency order as the source. Preserve decisive assumptions, quantifiers, dimensions, labels, and the distinction between pointwise and integrated claims.
4. Begin each major module with a short `prerequisite` block containing only the background needed immediately. Explain every object's type, ambient space, parameters, and role before using it.
5. Present the faithful theorem-and-proof spine in ordinary prose and theorem environments. Put expanded algebra, sign checks, scaling checks, endpoint regularity, and other local derivations in separate `calculation` blocks.
6. End each major module with a `checkpoint` that asks the reader to reproduce the actual logical bottleneck, not merely recall terminology.
7. Finish with a proof-reconstruction list: exact target, construction stages, decisive estimates, closure steps, and where the technically longest verifications live.

Prefer explanation by mathematical function: why an object is introduced, which error it controls, and where it is used next. Expand the steps at which a sign, exponent, endpoint condition, norm, or quantifier can change the conclusion. Do not paraphrase every routine line.

## Keep each proof's main thread visible

A proof may be locally detailed and still be unreadable if its target disappears. For every substantial proof:

- begin by naming the exact quantity, assertion, or contradiction being established;
- give persistent notation to objects that connect several stages, such as a candidate family, error term, or selected subsequence;
- keep the main implication or equation chain together before entering a long regularity, approximation, or sign justification;
- when a technical detour ends, state the precise earlier formula it validates and resume from that formula;
- after every construction stage, say what has now been obtained and identify the later step that consumes it;
- at closure, explicitly combine the earlier outputs on the same object, with the relevant quantifiers visible.

Apply a continuity test before delivery: read only the first and last paragraph of each proof stage and the displayed equations joining them. A reader should be able to recover the proof's target, the current input and output, and why the next stage follows. If the protagonist of the statement (for example, a sum such as \(\sigma\), a candidate family, or the target functional) disappears from the proof, rewrite the spine before adding more local detail.

Factor a long proof when that makes the dependency order visible. Use an independent lemma when a technical passage has a clear hypothesis-to-conclusion interface, is called later, or would otherwise interrupt the main argument for a substantial length. Put a self-contained but secondary approximation, regularity, or boundary justification in an appendix when the main text only needs its precise statement; cite the appendix at the point of use. Keep a short one-use calculation in the current proof. Do not split merely to create more numbered results, and do not use a result before its proof without explicitly presenting it as an earlier lemma or a clearly signposted postponed proof.

## Keep the voices distinct

- **Source mathematics:** faithful statement, construction, and proof spine.
- **Prerequisite:** standard background needed at that point.
- **Calculation supplement:** a local derivation added for learning or verification.
- **Checkpoint:** a concrete task the reader should be able to perform unaided.

Do not mix audit history, agent verdicts, hashes, or defensive publication language into the exposition. Put only a short source-and-status note at the front; keep detailed evidence records in project ledgers.

## Validate the result

Check the study edition against the source theorem by theorem and equation by equation. In particular verify:

- hypotheses, dimensions, quantifiers, limits, and base-point dependence;
- definitions and notation at first appearance;
- every expanded calculation, including signs, scaling powers, boundary terms, and norms;
- that first-pass summaries do not overstate the detailed proof;
- that checkpoints and the reconstruction list cover every essential dependency;
- that source changes have not made the study edition stale.
- that long technical passages have been factored into lemmas or appendices when they obscure the main proof, while short local calculations have not been over-fragmented.

Build every affected LaTeX entry point using the repository command and scan logs for errors, undefined or duplicate references, bibliography warnings, package warnings, and overfull or underfull boxes. A successful build checks typesetting only, not mathematical correctness.
