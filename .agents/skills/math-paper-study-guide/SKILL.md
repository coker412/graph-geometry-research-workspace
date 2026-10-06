---
name: math-paper-study-guide
description: Create or revise Chinese mathematical study editions with prerequisites, expanded calculations, and proof-reconstruction checkpoints. Not for ordinary translation or submission manuscripts.
---

# Mathematical Paper Study Guide

Produce a Chinese companion that lets the reader understand, recalculate, and reconstruct a mathematically stable source. Keep it separate from the submission manuscript and faithful to the source mathematics.

## Source and boundaries

Follow applicable repository instructions without rereading those already loaded. Identify the exact source or frozen version, its evidence level and gaps, the reader's background, whether auditing is requested, and the theorem, equation, and citation labels to preserve.

- Do not silently fill gaps, change assumptions or quantifiers, or promote evidence. Added pedagogical derivations inherit at most the source's level; unreviewed additions must be identified in a concise front status note.
- Keep source mathematics, prerequisite explanations, calculation supplements, and learning checkpoints distinguishable. Detailed audit records belong outside the narrative.
- If the formal manuscript is also in scope, use `math-paper-writing` for that work, stabilize it first, then derive the study edition. A source change requires checking affected companion material again.

## Deliverable scope and reading design

A request for a Chinese study edition does not request a separate Chinese paper translation. Work directly from the stable source; produce other manuscript versions only when the user requests them. Reusing a translation that already exists is optional, never a prerequisite or a reason to preserve its reading order.

When the user names a previous successful edition, inspect its final learning text at the actual difficult passages before choosing the structure. Extract how it teaches, not its page count or environment names. Preserve mathematical statements and traceability while arranging explanations where the reader needs them: prerequisites before first use and decisive derivations beside the step they explain. Do not default to a complete formal section followed by a detached supplement.

## Read only the needed method

For a new edition or structural rewrite, read [chinese-study-edition-method.md](references/chinese-study-edition-method.md). It contains the staged reading design, module structure, proof continuity and factorization guidance, and completion checklist. Use the [LaTeX template](assets/main-study-zh-template.tex) only when no compatible project structure exists.

For a local revision, read the corresponding section of that method: proof continuity/factorization for proof restructuring, calculation granularity for expanded derivations, or source synchronization for source changes. Preserve the existing edition's architecture unless a structural change is requested.

The edition must retain a precise problem and source-status note, a mechanism and dependency chain, staged reading guidance, prerequisites needed at each major module, expanded decisive calculations, checkpoints on actual bottlenecks, and a final proof-reconstruction list. Explain why each object is introduced and where its output is used. Keep the target and persistent objects visible; connect technical detours back to the main proof. Avoid repeating routine calculations or splitting short arguments into ceremonial lemmas.

## Validate and deliver

Compare changed material and affected dependencies against the source theorem by theorem and equation by equation: hypotheses, dimensions, quantifiers, limits, base-point dependence, definitions, signs, scaling, boundary terms, and norms. First-pass summaries must not overstate the detailed proof; checkpoints and reconstruction must cover essential dependencies. Apply the method's completion checklist when delivering a full edition.

Check teaching quality separately from mathematical correctness: follow one difficult proof from the intended reader's starting knowledge, identify where each prerequisite is supplied, and reconstruct the decisive chain without a later supplement. A theorem audit or a complete checklist does not establish this.

Build every affected LaTeX entry point with the repository command and inspect errors, undefined/duplicate references, bibliography and package warnings, and overfull/underfull boxes. Report changed files, source/version status, checks, and remaining gaps. Compilation does not verify the mathematics.
