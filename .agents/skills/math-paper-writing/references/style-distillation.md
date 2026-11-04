# Distilling mathematical writing choices

Use this mode when asked to learn, compare, or update writing methods from selected papers, including the researcher's own writing. For ordinary polishing, the voice reference is enough. This mode is self-contained: no separately installed distillation skill, fixed workspace, particular connector or paid service is required.

Mathematical distillation directly invokes `writing-dna-skill`; it does not need to go through a separate mathematical controller. First read and use the bundled original [Writing DNA skill](../assets/writing-dna-skill/SKILL.md), then apply the mathematical specializations in this reference. The original entry has one documented link back to this mathematical adaptation; do not reload an entry or reference already read for this task. Its English workflow, Chinese/English templates and referenced cleanup skill are included unchanged, with [pinned version and file hashes](../assets/writing-dna-skill/UPSTREAM.json) and [MIT license](../assets/writing-dna-skill/LICENSE). Resolve upstream relative paths from that bundled skill directory. No separate installation or network access is needed to load the workflow.

For mathematical work, the user’s decisions and this adaptation govern conflicts: retain exact mathematical scope and notation; treat the upstream similarity-score goal as an aspiration, not a measured result; allow explicitly chosen small-sample/local modes; and use cleanup only when needed, without compulsory successive passes. Choose templates by artifact language, translate their genre fields to mathematical uses, and fill them with evidence rather than copying their placeholders. The mathematical specialization below preserves the original twenty-work standard while adding an explicitly chosen small-sample mode, guards against coauthor/genre confounding, and treats a profile as defeasible editorial guidance rather than identity imitation.

## Resolve what is being learned

Use the request and existing files to identify the target author or collection, desired period/genre, approved inclusions and exclusions, language, intended manuscript, and output location. Check complete current author lists before reading excluded collaborations; search snippets can omit authors. Record source versions and distinguish first submission, revision and publication dates. Preserve the selected version with a digest when a local copy is available.

Separate three products:

- **General craft:** choices useful across papers, subject to mathematical and editorial constraints.
- **Optional profile:** choices supported by this author/corpus, genre and period.
- **Researcher's preferences:** explicit choices that may differ from observed habits.

Do not turn every profile trait into a shared default. Keep personal corpora and profiles in the existing project or an explicitly chosen private location. A request to analyze private drafts does not authorize bundling them with a distributable skill. Public-source bibliography, original paraphrases and licensed workflow instructions can form a portable example; retain required notices when adapting another skill.

## Use twenty works for the standard study

The standard author-profile workflow uses **at least twenty complete, distinct works** and all five synthesis documents below. Public demonstration packs follow this standard. A requested count is an acceptance requirement, not a suggestion. Limited samples do not authorize shortening an otherwise feasible standard study.

We also support **small-sample profiles from three or more works** when the user chooses that mode or supplies a limited personal corpus. Label the result provisional and identify the narrower coverage. A passage or one or two papers can support local analysis, but not a completed reusable author profile. If collecting twenty relevant works is blocked, report the actual shortfall and available alternatives; do not silently substitute a small-sample deliverable.

These are operational tiers, not statistically validated sample-size cutoffs:

| Independent works available | Useful product | Claim limit |
| --- | --- | --- |
| No text | Stated preference profile or source-search result | No inferred author style |
| A passage or 1–2 papers | Local passage analysis | Not a completed reusable author profile |
| 3–5 papers | Tentative profile with recurring observations and exceptions | Separate shared-topic/coauthor effects |
| 6–19 papers | Broader, stratified profile; check an unused paper when feasible | Untested traits remain provisional |
| 20 or more papers | Broad corpus study across relevant types/periods | Count alone does not establish representativeness or reliability |

Twenty is the standard workflow's minimum, not a statistically validated reliability threshold. The smaller tiers describe the explicitly chosen small-sample mode; they do not relax a standard study or a requested count. Duplicate versions, translated copies, sections and excerpts are not independent works. Count papers, versions, sections and words separately. A long paper supplies many observations but remains one work; related sequels are correlated evidence. Do not pad a personal corpus with other authors and then call it the researcher's own voice.

With few papers, inspect contrasting sections: abstract, problem framing, formal statement, difficult proof transition and ending. These expand *section coverage*, not the number of independent samples. A survey, lecture note, referee response or thesis chapter can supplement the profile if its genre is recorded; it cannot silently substitute for a research paper.

For the researcher's own writing, distinguish original draft, collaborator/teacher edit and author-approved final. A revision pair can reveal preferred choices better than a word-frequency table. Mark unknown sentence authorship as unknown. Explicit preferences can be recorded without demanding twenty examples, but label them as preferences rather than corpus findings. Keep defects the researcher wants to change out of the desired profile.

## Collect and inspect evidence

Prefer complete original text for a whole-paper profile. Abstract-only access supports abstract analysis only. Use available text/PDF tools; prefer editable source when supplied. Inspect mathematical notation and visual material in the rendered PDF when extraction is ambiguous. A downloaded full text is not evidence that every argument has been read or verified.

When no reusable page-labelled extraction exists, use [pdf_pages.py](../scripts/pdf_pages.py) with an explicit `--cache` path in the existing reading/build directory. The default index and `--find` locate material; `--pages 2,5-7` prints those PDF pages without truncation and `--pages all` prints the full extraction. Repeated uses verify the source hash and reuse the text. Fresh extraction requires PyMuPDF; it does not perform OCR, count independent works, remove mathematical content, or replace the required full-text reading. Use existing metadata/identifiers to distinguish versions, not file hashes alone.

For each source, retain a compact record, for example:

```json
{
  "id": "P01",
  "title": "Source title",
  "authors": ["Full author list"],
  "source": "URL or supplied path",
  "version": "Version or file hash",
  "dates": {"submitted": "known date", "revised": "known date"},
  "genre": "research paper",
  "period": "selected period",
  "authorship": "sole / collaborative / unknown passage attribution",
  "exclusion_check": "checked against the user's exclusions",
  "coverage": "full text available; selected passages closely read",
  "inspected_loci": ["PDF p. 3, paragraph before Theorem 1.2"],
  "opening": "known theorem and new setting",
  "structure": "setup → obstacle → replacement estimate → consequence",
  "ending": "final corollary",
  "notable": "exception to an otherwise repeated pattern"
}
```

Unknown fields stay unknown; do not invent dates, author contributions or quotations. Use stable page/section references or hash-bound text slices. Keep the record proportional to the corpus rather than creating empty files for every possible dimension.

## Give abstracts and introductions a dedicated paired reading

Allocate attention by editorial importance, not word count. For each work in a standard study, closely read its abstract and complete introduction as a pair, then check their selection and presentation against the main statements and relevant proof passages. This supplements the full-work reading; it does not replace it. Record actual coverage separately (abstracts, introductions, body connections), including absent abstracts or inaccessible sections. Twenty abstract/introduction pairs still count as twenty works, not forty independent samples. In small-sample mode apply the same paired reading to the available works.

Look for decisions rather than a mandatory sentence pattern:

| Part | What to distill |
| --- | --- |
| Abstract | Which result leads; which scope conditions survive compression; how significance is made concrete; whether a comparison or method earns its space; which secondary results, setup and proof details are left to the paper. |
| Introduction | How the question becomes understandable; which literature comparisons explain the contribution; where results appear and how much setup they need; how motivation, examples and the actual proof mechanism connect; how technical detail and navigation are allocated. |
| Their relationship | What is repeated to orient readers, what is expanded or deferred, and how both remain faithful to the same theorem. In particular, an omitted abstract detail is not permission to omit a necessary hypothesis or to generalize the conclusion. |

Keep compact passage-level evidence in the existing structure report or source annotations: source locations, the editorial choice and its mathematical purpose, what the other part adds, and an exception or unknown. Compare across works and genres before inferring an author tendency. Report section-specific language observations separately from pooled prose statistics; do not turn a distinguished author's long abstract, detailed introduction or unusual ordering into a universal requirement.

For new or updated profiles, give abstract decisions and introduction decisions separate, readily findable entries in the existing structure report and compact Writing-DNA document. Each needs supporting loci and use conditions, or an explicit statement that evidence is insufficient. Preserve the five-document format; no extra template pack or numerical importance weights are needed. When updating an older profile, state how many pairs were actually re-examined rather than implying that all twenty received this new analysis.

Test a borrowed decision on the intended part using supported mathematical content. Check both fidelity and a specific expository purpose: an abstract should let the reader identify the result and scope without needing the introduction; an introduction should develop context or explanation rather than simply lengthen the abstract. Include a case where a method sentence or literature comparison should be omitted. Save the actual output and review in the existing application/evaluation record. Distillation examines published parts together; whole-paper composition still follows the user's body-first, introduction-later order.

## Six layers, adapted to mathematical papers

1. **Language.** Measure prose separately from displays, citations and bibliographies where feasible. Record extraction/filtering rules. Compare relevant genres and sections, not just pooled words. Do not infer part of speech from untagged tokens or treat Chinese character thresholds as English sentence targets. Formula-induced fragmentation, common subject nouns and journal headings are confounders. For a small or noisy corpus, report qualitative observations and unavailable statistics honestly.
2. **Structure.** Annotate each work's opening, first substantive question, theorem hierarchy, proof interfaces, transitions and ending. Group recurring architectures only when there is evidence; a one-paper corpus need not supply three templates. Record counterexamples to the proposed pattern.
3. **Question framing.** Identify how the text selects its gap: new object, weaker assumptions, sharp parameter range, improved estimate, obstruction, new proof or application. Distinguish the explanatory frame from an inferred research agenda. A selected corpus cannot establish what its author never studies.
4. **Evidence strategy.** Track the roles of cited theorems, examples, counterexamples, calculations and figures. Distinguish a borrowed theorem from an analogy and a new estimate from established machinery. Do not assess source prestige in place of checking its job in the argument.
5. **Reasoning presentation.** Infer reusable decisions about revealing obstacles, changing languages, suppressing technical detail and returning from reductions. Support each inference with inspected passages; do not diagnose private beliefs or claim mathematical correctness from elegant writing.
6. **Visual organization.** Sample 5–10 papers for a broad corpus, or all available papers when fewer than five. Open every identified figure in those papers, including vector diagrams and uncaptioned plots. Caption/raster searches alone are insufficient. Record what figures explain, and separate author choices from publisher/class layout. If visual access is unavailable, mark this layer unassessed.

For a broad study, produce `language-dna.md`, `structure-patterns.md`, `cognitive-framework.md` (layers 3–5), `visual-style-guide.md`, and a compact `Writing-DNA.md`. Use the source language unless the user chooses another artifact language. For a small study, one profile with the six layers and explicit unknowns is enough. Do not generate five empty reports merely to satisfy a format.

## Turn observations into scoped decisions

Each usable trait needs: the editorial action; source loci; independent-paper support versus related-family support; an exception or missing coverage; the relevant genre/section; and a confidence description such as **observed once**, **tentative recurrence**, or **repeated in this corpus**. These descriptions are not mathematical verification levels or statistical probabilities.

Example: “When transporting a result, name the old proof's unavailable property and the replacement estimate” is actionable. “This author is rigorous” is not. A phrase count is evidence about this extraction, not an instruction to repeat that phrase. The [Tao models](author-models.md) and optional [field profiles](field-profiles.md) illustrate scoped decisions without defining a universal house style.

Before promoting a trait, look for contrary cases and distinguish personal tendency from mathematical necessity, coauthor practice, topic and venue. If feasible, set aside a relevant paper *before* deriving the profile, then test whether the rule explains it without amendment. If all papers have already informed the profile, call a subsequent comparison an in-sample check, not an unseen test. With little material, use a short author-reviewed trial instead; approval of that preference does not prove author-wide generality.

## Apply and maintain a profile

Distinguish the requested use before drafting:

- **Full profile-guided drafting:** read all five synthesis documents, then read five complete source works closest to the new text's genre and topic. Use metadata to select them and prefer recent works among equally relevant matches. The upstream skill requires five full texts and fills shortages with the same genre on other topics. In this mathematical adaptation, if fewer than five suitable works are available, read those available and state the narrower evidence; do not pad with irrelevant texts. For a small-corpus profile, read its single consolidated document and available sources. Previously read material still present in the working context need not be mechanically reloaded.
- **Targeted borrowing of a method or local revision:** read the profile's applicable layers and the passages supporting the selected decision. This is a lighter mathematical adaptation, not completion of the upstream full-profile workflow. The portable examples in `author-models.md` support this use; they do not replace an author's five synthesis documents and raw corpus for a full-profile claim.

Translate the material into a short working selection: the relevant structure, two or three writing choices that solve this task, and the original passages that illustrate them. For an abstract or introduction, select the corresponding section-specific decisions and inspect their paired source passages; do not rely only on a whole-paper profile. Use that selection to draft; do not paste the profile's metadata, confidence annotations or warnings into manuscript prose. Preserve mathematical meaning, existing notation, accepted abstracts and venue conventions.

When comparison is requested, distinguish **already covered**, **new useful decision**, **author-specific option**, and **not supported/rejected**. Add a general rule only if it changes a concrete decision, survives the target manuscript's constraints and has traceable support. Do not merge contradictory author preferences into an accumulating checklist. Profile changes should record which new source or explicit user choice changed the inference.

Learn from corrections as well as model papers. When a draft and a revised passage are supplied, record the removed problem, the actual change, its reason, preserved mathematical content, and whether the researcher accepted it. A maintainer's proposed rewrite is not an accepted preference. Repeated accepted corrections can refine the personal profile; promotion to general guidance requires a reusable decision and contrary-case checks. Keep these compact examples in the existing profile/evaluation record rather than creating a separate framework for each edit.

Validate application on a short passage: compare hypotheses, quantifiers, objects, references and proof status before assessing explanation. Show what changed and why. Retain unresolved fidelity questions; never invent a numeric similarity score, independent reviewer verdict or author approval. Portable delivery must have working relative links and required license notices and must not depend on the maintainer's private corpus or absolute paths.
