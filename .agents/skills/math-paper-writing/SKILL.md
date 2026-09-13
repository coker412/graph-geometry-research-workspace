---
name: math-paper-writing
description: Draft, revise, audit, and prepare mathematical research papers and submission materials in English or Chinese, including theorem exposition, abstracts, introductions, proofs, LaTeX, citations, figures and tables, cover letters, referee responses, and bilingual consistency. Use for paper-facing or submission-facing mathematical writing; do not use for standalone proof search or literature review unless the result will be written into a paper.
---

# Mathematical Paper Writing

Produce clear mathematical papers without changing what has actually been established. Treat mathematical meaning, evidence, and source support as constraints on the prose rather than details to repair after writing.

## Apply local policy first

Before acting, read the applicable `AGENTS.md` files and any repository writing or publication instructions they route to. Local definitions, evidence levels, directory layouts, build commands, and approval gates override this skill's defaults. Do not copy local conventions into unrelated projects.

## Establish the writing contract

Infer from the request and available files:

- the deliverable and target section;
- the genre, intended audience, language, and target venue when relevant;
- the mathematical source of truth;
- whether mathematical changes are allowed or the task is language-only;
- the status of each main claim and any publication gate;
- the files or versions that must remain synchronized;
- any researcher-approved voice sample or venue instruction that should govern the result.

Ask a question only when an unresolved choice would materially change the mathematics, publication claim, or target audience. Otherwise state a narrow assumption and proceed.

## Choose the working mode

- **Draft:** turn verified notes or results into paper prose.
- **Revise:** improve organization, explanation, notation, or language while preserving the authorized mathematics.
- **Audit:** inspect definitions, theorem statements, proofs, citations, novelty claims, and reader dependencies without silently repairing substantive gaps.
- **Deliver:** update paper files, synchronize versions, build the document, and report remaining risks.
- **Prepare submission or response:** prepare a cover letter, revision package, or point-by-point referee response without submitting it or making unsupported declarations on the author's behalf.

Modes may be combined. Do not treat a request for polishing as permission to alter a theorem or complete a missing proof.

## Preserve the mathematical invariants

- Never strengthen or weaken hypotheses, quantifiers, definitions, domains, conclusions, or evidence status without explicit authorization.
- Do not turn computational evidence, a conjecture, a conditional argument, or a proof draft into an established theorem.
- Do not invent citations, priority claims, historical context, theorem numbers, examples, or applications.
- Distinguish an informal explanation from the formal statement it explains.
- Introduce every nonstandard object before use and make its type and role clear.
- Keep notation, terminology, labels, citation keys, and cross-references stable unless changing them is in scope.
- Expose a real gap. Fluent prose is not a substitute for a proof or a checked reference.
- Keep audit records out of manuscript prose and rendered bibliographies, including internal drafts. Use concise source locators, not verification narratives; see the bibliography guidance in [latex-and-bilingual-writing.md](references/latex-and-bilingual-writing.md).
- Honor an explicit single-language scope: preserve other language editions and their outputs, and report any pre-existing synchronization gap.

For any proof-bearing edit or mathematical audit, read [mathematical-integrity.md](references/mathematical-integrity.md).

## Route to the needed guidance

- For a detailed Chinese learning edition with prerequisite blocks, expanded calculations, checkpoints, and proof reconstruction, use the separate `math-paper-study-guide` skill. Do not import that teaching structure into a submission manuscript by default.
- For titles, abstracts, introductions, section structure, examples, notation, proof narrative, or stylistic decisions, read [exposition-and-structure.md](references/exposition-and-structure.md).
- For `.tex` or `.bib` edits, build checks, translation, or bilingual synchronization, read [latex-and-bilingual-writing.md](references/latex-and-bilingual-writing.md).
- For plots, geometric figures, commutative diagrams, tables, captions, or accessibility checks, read [figures-tables-and-diagrams.md](references/figures-tables-and-diagrams.md).
- For cover letters, submission packages, revisions, or responses to editors and referees, read [submission-and-peer-review.md](references/submission-and-peer-review.md).
- For short notes, full papers, surveys, computational papers, audience changes, or a researcher-specific voice, read [voice-and-genre.md](references/voice-and-genre.md).
- When natural-language polishing should use an available Humanizer skill, read [humanizer-interface.md](references/humanizer-interface.md) and follow its protected-region protocol.
- Read [sources.md](references/sources.md) and [evaluation-suite.md](references/evaluation-suite.md) only when reviewing, maintaining, or testing this skill, or when answering questions about its source base.

Read only the references needed for the current task.

## Work from dependency to presentation

For substantial drafting, organize the paper from mathematical dependencies outward: setup and definitions, preliminary results, main argument, applications or limitations, then abstract and introduction. A rapid prototype is useful, but it is not a submission draft. Rewrite after the mathematical architecture is visible.

When editing existing material, make the smallest change that solves the writing problem. Preserve the author's defensible voice and deliberate conventions.

## Validate before handoff

Check, in proportion to the task:

1. formal statements against their source of truth;
2. hypotheses, quantifiers, notation, and object introductions;
3. proof dependencies and any omitted difficult step;
4. proof-thread continuity: the target remains visible, persistent objects keep stable names, technical detours return to the formula they justify, and the closing step combines earlier outputs on the same object;
5. proof factorization: long technical passages with a genuine interface are lemmas or appendices, dependencies are stated before use, and short calculations are not over-fragmented;
6. citations against the claims they support;
7. abstract, introduction, and conclusion against the body;
8. language-only edits for semantic drift;
9. visual claims, captions, accessibility, and reproducibility when figures or tables changed;
10. cover letters and referee responses against the manuscript, decision letter, and current venue requirements;
11. changed LaTeX and all affected versions with the repository's build procedure.

For file edits, report changed paths, checks run, unresolved mathematical or bibliographic risks, and the preserved evidence status. A successful build certifies typesetting, not mathematics.
