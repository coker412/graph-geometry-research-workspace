# LaTeX and bilingual writing

Read this reference for `.tex` or `.bib` edits, build verification, or synchronized English and Chinese versions.

## Preserve the project before normalizing it

Inspect the existing document structure, class, packages, macros, theorem environments, bibliography system, build command, and applicable repository instructions. Do not replace a journal template or reorganize the project merely to match a preferred layout.

When editing:

- preserve commands, labels, citation keys, and file boundaries unless their change is requested;
- keep theorem-like environments and numbering consistent;
- update every reference to a renamed symbol, label, figure, or theorem;
- avoid defining a new macro when an established project macro already expresses the same object;
- keep publication prose free of internal agent logs, verification chatter, and development history.

## Theorem and proof source

Use semantic LaTeX environments rather than visual formatting. Keep formal statements concise enough to parse, but do not shorten them by dropping assumptions. Put motivation before a theorem environment and discussion of scope after it.

If prose-only revision is requested, treat math delimiters, equations, macros, and theorem labels as protected. A wording change inside a formal statement is mathematical work and requires the integrity audit even when no formula changes.

## Bibliography

Determine whether the project uses BibTeX, biblatex, or another system before editing. Verify bibliography metadata against an authoritative record. Keep citation keys stable unless renaming is in scope and all uses can be updated.

Printed bibliographies contain bibliographic identification, not the research audit trail. Keep consulted/downloaded-source notes, verification claims, reviewer records, hashes, task IDs, and explanations such as “theorem numbering follows” in project notes outside the manuscript. Do not put these into printable `note` or `addendum` fields, or relocate them into footnotes, citation brackets, or a manuscript appendix. This also applies to the bibliography of an internal review edition.

Keep citations short: normally a reference and, when useful, a theorem, section, or page locator. If an actually needed number is tied to a different source version, preserve an unambiguous minimal locator (for example, `Thm. 1.4, arXiv v1`) and the corresponding identifier in the bibliography. Do not assume numbering agrees across versions, add long version explanations, or append arXiv versions indiscriminately. Preserve publication metadata and necessary preprint identifiers; DOI/URL display follows the selected venue or style and should not be duplicated manually in notes merely to force links to print.

Check the rendered bibliography as well as its source: custom `thebibliography` blocks and printable metadata may bypass the intended style. Preserve removed provenance in project notes. A required evidence qualification is separate from an audit narrative; keep it concise and keep its detailed review record outside the paper. Do not remove mathematical hypotheses, source attribution, or author-approved AI-use disclosures as if they were audit clutter.

Every citation should have a clear job. A proof-bearing citation must appear at or near the invocation and identify the usable result. A contextual citation may support history or comparison but cannot silently carry a proof step.

Do not add a bibliography entry that has not been checked, and do not infer that a source supports a claim from its title or abstract alone.

## Build and log checks

Use the repository's documented build command. If none exists, infer the engine and bibliography workflow from the source before choosing a command. Rebuild every affected output after changing source, bibliography, figures, or included files.

A zero exit code is necessary but not sufficient. Inspect the log for at least:

- TeX errors;
- undefined citations or references;
- duplicate or multiply defined labels;
- bibliography warnings;
- relevant package warnings;
- overfull and underfull boxes;
- missing files, fonts, or figures.

Report warnings that remain and explain whether they affect correctness, readability, or portability. Compilation checks typesetting and cross-references; it does not verify mathematical claims.

## English source and Chinese versions

If the user explicitly requests only one language edition, that scope overrides automatic bilingual synchronization: isolate shared inputs as needed, leave other editions and PDFs unchanged, and report any existing divergence without claiming synchronization.

When a project designates one language as the mathematical source of truth, edit that version first. Stabilize its definitions, hypotheses, proofs, citations, and labels before translating or synchronizing other versions.

For English-to-Chinese synchronization, compare meaning rather than environment counts. Check each formal result for:

- the same hypotheses and quantifiers;
- the same conclusion and exceptional cases;
- the same formulas, labels, and citation roles;
- the same evidence qualification;
- the same distinction between proved results, heuristics, and open questions.

Chinese may use natural word order and short explanatory glosses, but it must not add a mathematical assumption or silently strengthen a conclusion. An internal Chinese review version may contain reader guidance or an audit checklist if it reuses, rather than forks, the formal mathematics.

## Terminology and typography

Use terminology standard in the relevant mathematical literature. Do not translate a technical term solely by ordinary-language similarity. Keep an explicit glossary for terms that recur across language versions or disciplines.

Protect conventional mathematical typography during language edits, including:

- hyphenated or en-dash names represented in LaTeX, such as `Faber--Krahn`;
- minus signs and ranges inside mathematics;
- author names, theorem names, and citation keys;
- deliberate distinctions such as map versus function, immersion versus embedding, or necessary versus sufficient.

After synchronization, build every affected version and repeat the semantic comparison if the source version changes again.
