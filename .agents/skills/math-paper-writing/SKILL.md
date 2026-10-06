---
name: math-paper-writing
description: Draft, revise, audit, or prepare mathematical manuscripts and submission materials. Use for paper-facing work, not standalone proof search or learning editions.
---

# Mathematical Paper Writing

Produce clear mathematical papers while preserving the established mathematics and the author's defensible voice.

## Scope and mathematical boundaries

Follow applicable repository instructions for evidence, publication, paths, and builds; do not reread instructions already loaded. Infer the deliverable, audience, language, authoritative source, allowed mathematical changes, and affected versions from the request and files. Ask only when an unresolved choice materially changes the mathematics, publication claim, or audience; otherwise proceed with a narrow stated assumption.

- Preserve hypotheses, quantifiers, definitions, domains, conclusions, and evidence status unless their change is explicitly authorized. Polishing does not authorize proof completion.
- Do not invent citations, priority, examples, applications, or author declarations. Expose gaps and keep informal explanations distinct from formal claims.
- Introduce nonstandard objects before use. Preserve notation, labels, citation keys, cross-references, and deliberate conventions unless changes are in scope.
- For an existing or collaborative manuscript, treat the authoritative author's notation as locked. Before drafting, make a local notation map for every object touched and reuse the exact established symbol in the corresponding part of the paper. A familiar alternative symbol is not a reason to rename an object. If the argument genuinely needs a new object, first check that no existing symbol already serves it, apply the necessity gate below, and state its relation to the established notation at first use. Before handoff, inspect the baseline diff and search the added text for aliases, renamed spaces, and symbols that occur only once; remove any that are not mathematically necessary.
- Apply a necessity gate before adding any definition, symbol, named construction, lemma, remark, or side conclusion. Add it when it is needed for correctness, prevents a real ambiguity, materially simplifies the argument, is reused downstream, or the author explicitly requests a more conceptual framework. Prefer direct expressions for one-use objects. A stronger identification or corollary may be added when it materially sharpens the paper's main message, supports later arguments, or has author-requested conceptual value; otherwise do not add it by default. Whether or not it is inserted into the manuscript, always report a newly established stronger conclusion to the author, together with its value and added expository cost. If removing an entity leaves the proof, later text, and intended contribution unchanged, omit it.
- Keep detailed audit records outside manuscript prose and rendered bibliographies, including internal drafts; retain required concise evidence qualifications.
- Honor single-language requests; synchronize versions only within the authorized scope and report pre-existing divergence.
- Preparing submission materials does not authorize submission.

## Load guidance for the actual edit

Read only applicable references, once. Combine routes when an edit crosses their boundaries.

| Task | Required guidance |
| --- | --- |
| Drafting mathematical claims, proof-bearing edits, or mathematical audit, including wording changes to formal statements | [mathematical-integrity.md](references/mathematical-integrity.md) |
| Titles, abstracts, introductions, structure, notation, or proof exposition | [exposition-and-structure.md](references/exposition-and-structure.md) |
| `.tex`/`.bib`, builds, translation, or bilingual synchronization | [latex-and-bilingual-writing.md](references/latex-and-bilingual-writing.md) |
| Figures, diagrams, tables, or captions | [figures-tables-and-diagrams.md](references/figures-tables-and-diagrams.md) |
| Cover letters, submission packages, or referee responses | [submission-and-peer-review.md](references/submission-and-peer-review.md) |
| Genre, audience changes, or researcher-specific voice | [voice-and-genre.md](references/voice-and-genre.md) |
| Natural-language polishing with an available Humanizer skill | [humanizer-interface.md](references/humanizer-interface.md) |
| Detailed Chinese learning edition | Use the separate `math-paper-study-guide` skill; do not impose its teaching structure on a manuscript |

For substantial drafting, organize from mathematical dependencies outward and write the abstract and introduction once the body is stable. For existing text, make the smallest change that solves the requested writing problem. Proof exposition must keep the target and persistent objects visible, return from technical detours, and factor long arguments at meaningful interfaces; the exposition reference gives the checks.

## Delivery and maintenance

Before handoff, apply the relevant [delivery checks](references/delivery-checks.md). Report changed paths, checks, unresolved mathematical or bibliographic risks, and preserved evidence status. A successful build checks typesetting, not mathematics.

Only for skill maintenance, evaluation, or questions about its sources, read [sources.md](references/sources.md) and [evaluation-suite.md](references/evaluation-suite.md).
