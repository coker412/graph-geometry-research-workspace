# Mathematical paper writing rules

This file covers manuscripts, abstracts, introductions, LaTeX, mathematical English, and research writing for public readers. Read root `AGENTS.md` first.

## Evidence required before writing

An unqualified main result in a submission manuscript's abstract, main theorem, or conclusion requires all of the following:

- `human-verified` or `formalized` evidence;
- Closed proof-map dependencies;
- Checked original sources for essential literature and theorems;
- Reproducible computational material;
- Explicit researcher authorization.

With explicit permission, an internal draft may contain `agent-verified` results, but use a consistent red macro or environment stating:

> agent-verified, not human-verified

Identify the verifier/review record. Editing, formatting, and restructuring cannot raise evidence levels.

## Humanizer

When available, prefer the humanizer skill for README files, project descriptions, public prose, English polishing, abstract/introduction/conclusion review, and removal of inflated or formulaic language.

Change expression only. Preserve mathematical meaning, hypotheses, quantifiers, definitions, formulas, and symbols. Invent no facts, citations, theorems, authors, dates, or history. Do not turn conjectural, experimental, conditional, or proof-draft statements into proved claims, or remove necessary qualifications. Recheck mathematics, citations, and levels afterward. The same boundaries apply if polishing manually without the skill.

## Files and builds

Keep manuscripts in `projects/<project>/paper/`. The researcher's preference recorded on 2026-09-15 is a simple single-main-file structure:

```text
paper/
├── main.tex
├── figures/          # Create only when needed.
└── references.bib
```

The location rule applies from the first write:

- New, uploaded, or received active/candidate TeX, Bib, included manuscript files, and build outputs go directly under the owning project's `paper/`, never temporarily at the project root.
- Teacher-supplied editable sources and frozen manuscript baselines belong in `paper/teacher-sources/`; internal manuscript variants use clearly named subdirectories of `paper/`.
- Source literature, notes, reports, talks, posters, and explicitly identified study editions may remain in their designated directories when they are not the active manuscript.
- Before and after paper work, run `python tools/workspace_hygiene.py paper-layout`. Legacy exceptions are frozen, not permission for new exceptions. Correct new location violations before continuing the text.

Put the body, proofs, acknowledgments, and appendices in `main.tex` by default. Do not fragment sections for agent assignments or internal administration. Organize sections around the mathematics, not each short paragraph or proof step. Preserve theorem environments and semantic cross-references.

Use a few included files only for a long manuscript or actual reuse, explaining the maintenance benefit. Keep existing paths until authorized to reorganize that manuscript; do not bulk-edit frozen manuscripts or proof snapshots.

Use `\begin{proof} ... \end{proof}` and keep BibTeX entries in `references.bib`. Public manuscripts use `\date{}` unless the researcher explicitly requests a visible date.

Build in `paper/`:

```bash
latexmk -g -xelatex main.tex
```

Rebuild every affected version after any TeX, Bib, figure, or included-file change, including English, formal Chinese, internal Chinese review, and overviews that consume the changed material. Inspect logs for TeX errors, undefined references/citations, duplicate labels, BibTeX/package warnings, and overfull/underfull boxes. A zero exit code alone is insufficient.

Prefer AMS formatting, including:

```latex
\usepackage{amssymb,amsmath,amsfonts,amsthm}
```

Use amsthm for consistent theorem, lemma, proposition, remark, example, conjecture, and problem numbering and style.

## arXiv sources and submission checks

The researcher selected these guides on 2026-09-15 as arXiv-linked reading. Apply relevant advice as a delivery standard rather than relying on what a server merely accepts:

- [Why Submit TeX?](https://info.arxiv.org/help/faq/whytex.html): reproducible, convertible semantic sources; remove private source comments.
- [Common Mistakes](https://info.arxiv.org/help/faq/mistakes.html): paths, filenames, styles/fonts, image formats, package conflicts, bibliography compatibility, and untested last-minute edits.
- [Trevor Campbell's guide](https://trevorcampbell.me/html/arxiv.html): clean a copy, simplify layout, combine body/appendices, include the bibliography, and check metadata/server PDF.
- [Ian Huston's checklist](https://www.ianhuston.net/2011/03/checklist-for-arxiv-submission/): rendered bibliography, publication details, mathematical punctuation, names/spelling, and removal of revisions/obsolete material.

Requirements:

1. Preserve maintainable sources and history in the working manuscript. Create a separate submission copy, normally one main.tex with a flat directory and necessary images/styles. Merge sections into one valid document; do not concatenate complete documents.
2. Include only required files. Exclude old drafts, study editions, internal reviews, version control, logs, disposable intermediates, and the generated full-paper PDF. Keep PDFs actually used as figures. Inspect the package contents.
3. Remove internal comments, obsolete commented text, TODOs, revision markup, and unused macros. Preserve TeX semantics when handling percent signs, including whitespace suppression, escaped percent signs, and verbatim content. Do not remove mathematical qualifications, attribution, or author-approved AI disclosure. Rebuild after cleanup.
4. Normally include a final `main.bbl` matching the main filename. After a clean independent build, the submission copy may omit unneeded Bib/BST files; retain them in the working source. Inspect each rendered entry and citation. Check whether a published version changes the cited conclusion before updating metadata. For biblatex, check backend and BBL-format compatibility separately.
5. Produce one PDF for the body and necessary appendices. Without venue instructions, put references before appendices. Use standard packages, portable fonts, relative paths, simple filenames without spaces, and engine-compatible images. Do not depend on absolute local paths, interactive input, or missing generation steps.
6. Unpack into a clean temporary directory and build with the submission engine until references stabilize. Scan logs and inspect the PDF page by page: punctuation, bibliography, figures, page breaks, links, title, abstract, and names. Any final edit invalidates the old build check. Workspace XeLaTeX validation does not replace target-engine compatibility testing.
7. Prepare metadata matching the final text. Remove inappropriate formatting and whitespace while preserving necessary mathematics under field rules. After authorized upload, check server file lists, logs, and PDF. If unfinished, report this explicitly; local success is not completed server acceptance.
8. Single-file structure, restrained sectioning, and compact packages are workspace preferences. Before using old claims about AutoTeX, engine support, BibTeX, or fixed compilation passes, consult the [current TeX submission instructions](https://info.arxiv.org/help/submit_tex.html) and linked TeX Live information. Do not apply obsolete patches mechanically. Preparation does not alter evidence, authorship, or publication authorization.

## Writing order

Write prerequisites, proofs, and applications first; then conclusions/open questions; then the abstract; then the introduction. Finally read the whole paper for narrative, terminology, levels, and citations. The abstract and introduction must not outrun the evidence.

## Title, abstract, and introduction

The title should identify the core object, problem, or method through useful terms, without publicity or claims beyond the body.

The abstract must stand alone: state the problem, main method, and results at their actual verified level. Omit proof details, unsupported novelty/significance claims, and theorem language for computational observations.

Write the introduction last, explaining checked history/current knowledge, setting and problem, results and evidence status, method and obstacles, and scope. Before claiming to resolve an open problem, improve a best bound, or introduce a new framework, complete the literature comparison. Remove unsupported claims rather than replacing them with vague attribution.

## Main text

Organize by mathematical dependency: setting and notation, directly checkable preliminary results, needed lemmas, main proof, applications/limitations, and precise open problems.

Open major sections with connected prose explaining purpose, idea, dependencies, and output. Explain which obstacle a key lemma addresses and how its conclusion is used next.

Keep material needed to understand and verify the main theorem. Failed routes, agent verdicts, debugging, evidence administration, and version history belong in research records. Long calculations, parameter cases, and computational certificates can become technical lemmas or appendices.

## Introduce objects before using them

At first appearance, explain each object's type, space, parameter range, definition/characterization, and role. A symbol alone is not an introduction.

- Sets: specify their elements. Maps: domain, codomain, and arguments. Operators: spaces, domain, sign, and normalization. Measures: underlying space. Stochastic processes: generator, clock, and lifetime conventions.
- Define unfamiliar terminology or give a precise short explanation. Names, abbreviations, and citations alone do not explain subordinate processes, regular symmetric Dirichlet forms, relative Faber-Krahn inequalities, Bochner derivatives, spectral projections, capacity, or recurrence.
- A formula is a definition only when its symbols are explained. Do not postpone spaces, measures, indices, or boundary conditions for pages.
- Define nonstandard objects before theorem statements that use them. Apply the same rule to local indices, cutoffs, spectral bands, level/exceptional sets, and auxiliary constants.
- Before delivery, audit first appearances in source order for type, definition, and role. Search supports but does not replace a sequential reading.

For a Chinese review edition intended for collaborators from other fields, also explain intuition and the object's place in the proof using standard Chinese, without changing mathematics or assuming internal terminology.

## Hypotheses, quantifiers, and strength

Maintain a hypothesis record from the original problem through the main theorem and lemmas. Identify whether connectedness, completeness, no boundary, dimension, regularity, finiteness, and parameter ranges come from the problem, a cited theorem, or new restrictions.

Before repairing a proof with an added assumption, check whether it narrows the original problem. If so, describe a special case or partial result. Translation, polishing, and merging must not silently add assumptions or omit qualifications.

Match every use of complete answer, counterexample, criterion, if and only if, necessary, sufficient, sharp, or optimal to the proof. For sharpness/optimality, specify parameter, object class, and comparison. In Chinese, retain a standard mathematical expression for sharpness instead of a literal everyday adjective.

Distinguish a literal answer to the original question, a strengthened version, a special model, a background theorem, and a direct corollary. Keep these classifications consistent in abstracts, introductions, theorem titles, conclusions, and project overviews.

## Submission manuscript and internal review

The English submission source is a research paper, not a verification report, teaching handout, or agent log. Its introduction should explain the original question, prior work, remaining gap, contribution, method, scope, and limits.

Keep definitions, statements, proofs, and necessary explanations in the body. Put self-audit lists, verifier dialogue, repair history, hashes, task status, and claims of finding no errors in project notes or a separate internal review.

Concentrate internal evidence warnings in one status box. Remove it from the formal public version only after the researcher approves evidence and priority checks. Essential teaching explanations belong naturally beside definitions/motivation; line-by-line review aids belong in the internal edition. Remove repeated background, unused definitions, and paragraphs whose only purpose is to say a check occurred.

## English source and Chinese editions

An explicit single-version scope, such as English only, takes precedence. Isolate shared-input effects, do not modify/rebuild other editions, and do not claim pre-existing differences are synchronized.

Otherwise, the English manuscript is the authoritative mathematical submission source:

1. Correct and check English definitions, statements, proofs, assumptions, citations, and cross-references.
2. Once stable, translate the formal Chinese edition section by section.
3. Update terminology, proof routes, and checklists in the Chinese internal review.
4. Build all affected editions and compare mathematical meaning.

The formal Chinese version must neither add nor omit assumptions, definitions, lemmas, proof steps, citations, quantifiers, exceptions, evidence limits, or scope. Preserve theorem order, formulas, labels, and citation keys where possible. Natural sentence splitting and faithful explanatory wording are allowed; strengthening, weakening, or reinterpretation is not. Internal review may add a glossary, reading guide, dependency diagram, and audit questions while reusing the formal mathematical body.

Compare each theorem's assumptions/quantifiers/conclusion, each proof's logic, and each citation's role. Counting environments is insufficient. An English proof-bearing change makes the Chinese editions unsynchronized until comparison and rebuilding finish.

## Mathematical environments

- `theorem`: main contribution.
- `lemma`: an auxiliary statement needed for a main result.
- `proposition`: a relatively direct property or intermediate result worth recording.
- `remark`: scope, meaning, differences, or limits; never conceal a gap.
- `example`: tests assumptions, boundaries, or constructions.
- `conjecture` and `problem`: unresolved questions with precise definitions, quantifiers, and background.

By default, omit descriptive bracketed titles on theorem/proposition/lemma/definition/remark environments. Explain role and context before the formal statement.

State the original objective and core conclusion first. Put regularity, uniqueness, approximation, or other auxiliary properties after the main existence/classification conclusion and explain why they matter.

## Notation and differentiation

Define symbols, abbreviations, and objects at first use. Avoid a large detached notation list at the start of an abstract/introduction. Rename only when a local ambiguity requires it.

With several variables or parameters, write the differentiation variable explicitly: `dx/ds`, `dW/d\rho`, `\partial X/\partial t`. Use ordinary derivatives for one-variable functions and partial derivatives for multivariable functions/families. Primes/dots require a unique, nearby specified variable. After notation changes, check equations, captions, references, versions, and dependencies.

## Terminology and prose

Use terminology consistent with the closest original research sources. Check uncertain near-synonyms rather than applying general English substitutions. Distinguish generating/profile curves, ordinary curves, parameter values versus dynamical time, solution orbits, plane curves, arcs, graphs, immersions, embeddings, transversality, compactness, and principal curvature.

Pronouns must have a unique referent; repeat the object's name when needed. Write precise, natural, concise English. Explain strategy before technical steps, give each paragraph a mathematical purpose, and avoid generic openings/endings, exaggerated importance, vague consensus, mechanical three-part arguments, or synonym variation at the expense of precision.

## References

Keep audit records out of the paper and rendered bibliography: read/downloaded versions, verification verdicts, agent records, hashes, and task IDs belong in project notes, not printable note/addendum fields, footnotes, body, or appendices. This also applies to an internal edition's bibliography; detailed audits stay separate.

Citations usually need the reference number and relevant theorem/section/page. If version matters for location, use the shortest necessary version identifier without audit narration. Render DOI/URL/preprint identifiers according to the target style; do not duplicate them in notes to force a link. Check the final PDF as well as BibTeX. Do not mistake mathematical qualifications, attribution, or author-approved AI disclosure for removable audit text.

Prefer standard MathSciNet BibTeX. Check arXiv author/title/year/identifier and reliable journal volume/pages/DOI metadata. Keep body citations, references.bib, and project references.md consistent. Do not cite unread sources or sources whose support is unconfirmed.

Distinguish proof-bearing citations from contextual background. At every theorem use, give a nearby citation and check original hypotheses, conclusion, notation, normalization, and theorem number. A reference only in the introduction cannot support a later proof step. State the part used and how the present objects satisfy it.

Distinguish known results, direct use, reproving, original combinations, and pending priority checks in the introduction/conclusion. A long bibliography is no substitute for theorem-level comparison. Missing key full text creates an explicit GAP; abstracts/snippets/secondary accounts cannot support strong novelty claims.

## Evidence and source snapshots

Keep evidence levels consistent across English, formal Chinese, internal review, paper README, project overview, proof map, and ledger.

A verifier certifies only the submitted snapshot. Proof-bearing changes require reassessment or re-verification of affected conclusions. Before submission, record input files, order, hashes, and formal statement; afterward preserve raw response, verdict, errors, gaps, and manifest.

A later status-only front-page update must be recorded as presentation-only/status-only, preserve the exact submitted snapshot, and confirm theorem/proof/bibliography hashes are unchanged. Polishing, rereading by the same agent, successful compilation, and more references do not raise evidence levels.

## Acknowledgments and authors

Record only real discussions, advice, help, and applicable funding. Use affiliations and a durable contact email. Do not disclose personal information that should remain private.

## Delivery checks

Before delivery, check assumptions/quantifiers/levels; claims in abstract/introduction/conclusion against the body; notation/captions/references; citation support; builds; semantic changes from polishing; accidental internal logs or unverified verdicts in public text; and visible labels for agent-verified material.

Complete four distinct reading passes before reporting a finished paper:

1. Mathematics: reconstruct definitions and proofs from the beginning, testing counterexamples, boundaries, division by zero, limit exchanges, signs, and hidden assumptions.
2. Reader experience: first-use definitions, explanations, main argument, and paragraph purpose.
3. Citations and originality: each external proof dependency and the division between prior work and this paper.
4. Versions and builds: compare all in-scope editions/state, force rebuilds, and inspect every log.

Report changed files, mathematical assumptions, checks/builds, unresolved proof or literature risks, evidence level, and the next human-review focus. Bare claims that the paper is synchronized, verified, or ready to submit are insufficient.
