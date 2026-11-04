# Sources and synthesis notes

This reference records the source base for the skill. It is not a substitute for the original works, and the principles below are paraphrases rather than a house style copied from any author.

## Source method

Prefer first-party or institutionally hosted texts. Extract decisions that improve mathematical exposition, record their scope, and retain tensions between authors. Do not turn a respected mathematician's preference into an absolute rule without a correctness or publication reason.

These sources guide writing behavior; they are not citations to insert into an ordinary research paper unless the paper itself discusses mathematical writing.

For maintenance, record the inspected locus, the decision it supports, and the skill section that implements it. An inspected locus is evidence of targeted reading, not a claim that every page of a source has been exhaustively studied. Publication policies are time-sensitive and must be rechecked for the actual venue.

## Paul R. Halmos

**Work:** Paul R. Halmos, "How to Write Mathematics," *L'Enseignement Mathématique* 16 (1970), 123--152. DOI: [10.5169/seals-43857](https://doi.org/10.5169/seals-43857). An accessible teaching copy is hosted by [Rutgers Mathematics](https://sites.math.rutgers.edu/~ceu11/Courses/halmos.pdf).

**Inspected locus:** Sections 2--6 on audience, organization, and rewriting; Sections 9--16 on honesty, prose, logic, notation, and symbols; closing remarks on adapting a model to one's own subject and personality.

**Principles used here:** write to a defined audience; organize around a coherent subject; use central examples and counterexamples; design notation early; rewrite rather than merely patch; keep prose unobtrusive; disclose the real status of an assertion; and never let "obvious" hide a false or unchecked step.

**Scope note:** Halmos presents personal practice and explicitly rejects the idea of a complete recipe. His advice supports judgment, not uniform formatting.

## Donald E. Knuth, Tracy Larrabee, and Paul M. Roberts

**Work:** Donald E. Knuth, Tracy Larrabee, and Paul M. Roberts, *Mathematical Writing*, MAA Notes 14, Mathematical Association of America, 1989. The [official Stanford page](https://cs.stanford.edu/~knuth/klr.html) describes the course and provides the source text.

**Inspected locus:** Lectures 5--6 on mathematical sentences and notation, 15--17 on refereeing, and 18--19 on illustrations and tables, using the [MAA-hosted text](https://maa.org/wp-content/uploads/2024/10/NTE14-1.pdf).

**Principles used here:** keep the reader's current knowledge in view; make theorem statements locally intelligible; define variables on first use; connect formulas with prose; motivate upcoming objects; keep notation consistent; avoid excessive indices; read sentences for rhythm; and revise from feedback.

**Scope note:** The volume records a course with several contributors. Not every comment is a single-author command, so this skill uses recurring principles rather than attributing every detail to Knuth alone.

## Jean-Pierre Serre

**Work:** Jean-Pierre Serre, "How to Write Mathematics Badly," public lecture at Harvard, November 2003. The lecture is listed by the [Collège de France](https://www.college-de-france.fr/fr/chaire/jean-pierre-serre-algebre-et-geometrie-chaire-statutaire/biography); an [ETH-hosted transcript](https://metaphor.ethz.ch/x/2025/hs/401-3005-00L/texts/serre_how_to_write_mathematics_badly_transcript.pdf) is available.

**Inspected locus:** Transcript sections "On Theorems," "On References," "On Proofs," "On Grammar," "On Abbreviations," "On Commas," "On Verbs," and the discussion of naturally defined maps and commutative diagrams.

**Principles used here:** do not hide the hard part behind "by definition" or an empty proof marker; distinguish existence from the choice of a particular object; make quantifier scope explicit; do not force symbols or commas to serve as logical verbs; and check that naturally defined maps are actually the same maps required downstream.

**Scope note:** The available document is a transcript of a humorous lecture. The skill extracts the logical failure modes, not its jokes or personal mannerisms.

## Terence Tao

**Work:** Terence Tao, ["On writing"](https://terrytao.wordpress.com/advice-on-writing-papers/), a collection of advice on research papers and exposition.

**Inspected locus:** The indexed guidance on accurately presenting and "selling" results, organization, motivation, notation, level of detail, lemma granularity, rapid prototypes, professional voice, proofreading, and final drafts. Follow the linked article for a principle before extending it beyond the summary on this index page.

**Principles used here:** make the main contribution visible in the title, abstract, and introduction; describe results accurately; compare with prior work only with adequate support; organize and motivate the paper; choose notation and detail for the reader; use a rapid prototype; and submit a checked final draft rather than a first draft.

**Scope note:** "Selling" a paper means explaining its exact merit and context. It does not license promotional prose or unsupported novelty claims.

## Timothy Gowers

**Work:** Timothy Gowers, ["My favourite pedagogical principle: examples first!"](https://gowers.wordpress.com/2007/10/19/my-favourite-pedagogical-principle-examples-first/), 2007.

**Inspected locus:** The main post, especially the closing qualification that examples should come first only after a conscious audience-dependent decision.

**Principles used here:** place a well-chosen example before an abstract definition when it gives the reader a mental model to which the formal properties can attach. Examples should shape the explanation, not merely decorate it afterward.

**Scope note:** Examples first is conditional. Specialists may prefer a concise standard definition first, and Gowers himself describes making a conscious choice rather than imposing a fixed order.

## Keith Conrad

**Work:** Keith Conrad, ["Advice on Mathematical Writing"](https://kconrad.math.uconn.edu/blurbs/proofs/writingtips.pdf), University of Connecticut handout.

**Inspected locus:** Sections 1--7 on notation, equations and expressions, punctuation, reasoning words, grammar, types of results, and definitions.

**Principles used here:** audit concrete sentences with before-and-after counterexamples; define notation and logical standing at first use; do not make symbols carry grammatical relations; punctuate displays as sentences; state the direction of an argument; and keep theorem statements distinct from proof strategy.

**Scope note:** The handout often uses elementary examples for teaching. The diagnostics transfer to research prose, but its examples and preferred formulations are not mandatory templates.

## Nicholas J. Higham

**Work:** Nicholas J. Higham, *Handbook of Writing for the Mathematical Sciences*, 3rd ed., SIAM, 2020, ISBN 978-1-611976-09-0. The [author's book page](https://nhigham.com/handbook-of-writing-for-the-mathematical-sciences/) links the table of contents, preface, bibliography, and supporting articles; the [third-edition note](https://nhigham.com/2020/02/11/handbook-of-writing-for-the-mathematical-sciences-third-edition/) records the expanded workflow, LaTeX, table, English-usage, publishing, and reviewing coverage.

**Inspected locus:** Author-hosted overview and third-edition change record; supporting article ["Better LaTeX Tables with Booktabs"](https://nhigham.com/2019/11/19/better-latex-tables-with-booktabs/). The full book remains the authority for details not present in those materials.

**Principles used here:** treat workflow and production as parts of writing; revise iteratively; distinguish genres; design tables for comparison rather than decoration; account for modern LaTeX, bibliography, version, and publishing practices; and include review and publication stages in the writing lifecycle.

**Scope note:** Specific package choices and publishing mechanics can age or conflict with a journal template. Recheck the venue instead of freezing them as universal rules.

## Corpus distillation and mathematical adaptation

**Workflow:** [writing-dna-skill](https://github.com/larashero3-dotcom/writing-dna-skill), inspected 2026-11-02: `SKILL.md`, English workflow and the five English author-corpus templates. Its six layers distinguish language, structure, topic framing, source strategy, reasoning perspective and visuals. The upstream runtime is [bundled locally](../assets/writing-dna-skill/SKILL.md), including both template languages and its referenced cleanup skill; [version and hashes](../assets/writing-dna-skill/UPSTREAM.json) identify the inspected commit and the single local math-routing addition to its entrypoint. [style-distillation.md](style-distillation.md) calls it and specifies the mathematical adaptations; the upstream [MIT notice](../licenses/writing-dna-MIT.txt) is included.

**Adaptation boundary:** the upstream broad-corpus workflow asks for at least twenty complete articles, scripted statistics, individual annotations, five to ten visually sampled articles, and five synthesis documents. The mathematical mode keeps those evidence layers for a broad study while allowing smaller samples with narrower claims. Its numerical sampling tiers are workflow choices, not empirically established reliability thresholds. Formula extraction, collaborator attribution and journal layout need separate treatment. No automated imitation score is asserted.

**Paper evidence:** the complete [Tao profile](profile-tao.md) now distributes all five synthesis reports and twenty source records; [author-models.md](author-models.md) records inspected loci and limits for twenty selected Tao papers: eighteen research papers/notes and two surveys. The originating study annotated their structures and visually sampled five works. Selected close reading supports editorial decisions, not exhaustive proof verification. This Tao study had no held-out or independent fidelity test.

**Optional field demonstrations (expanded 2026-11-03):** [field-profiles.md](field-profiles.md) routes Milnor, Evans, Stanley and Mumford profiles. Each now uses twenty distinct complete training works and five synthesis documents: eighty training works and twenty reports in total. Four additional papers were reserved for the earlier three-paper pilot and are excluded from training counts. They have since been read, so they are not fresh blind tests of the expansion. Each work has authors, date/version information, an architecture and inspected loci; each author has five works with complete visual surveying. OCR-aware language diagnostics remain approximate and include no POS-based or punctuation-style claims. The [application record](profile-applications.md) preserves the earlier same-agent checks and constructed revision pairs. Source links and annotations travel with the profiles; downloaded papers, private profiles and maintainer paths do not. The corpus includes explicitly labeled expository research, a survey and published correspondence; the field index states their scope.

**Reason for the cross-field comparator:** Ben Green's [Oxford account of the 2025 I. Martin Isaacs Prize](https://www.maths.ox.ac.uk/node/69941) credits Tao for learning how to structure arguments. This is specific first-party testimony about exposition, not a claim that all mathematicians agree or that a writing prize was awarded to Tao for these twenty papers. Domain relevance and demonstrated decisions matter more than reputation.

| ID | Decision | Direct evidence | Implementation |
| --- | --- | --- | --- |
| W16 | Supply a cross-field dictionary and the route back | Tao: Heisenberg embedding pp. 3–5; adelic multipliers pp. 1–2, 9; regularity reformulation pp. 9–10 | Exposition → transfer arguments |
| W17 | Declare what a heuristic suppresses and where rigor is restored | Tao: Collatz heuristic and following proposition; Kneser p. 4; high-dimensional wave systems pp. 3–4 | Exposition → informal overviews |
| W18 | Scale profile claims to independent evidence and explicit preferences | Six-layer upstream workflow plus the researcher's explicit request for small-corpus and self-writing support | Distillation → sampling, attribution and maintenance; evaluation E16–E21 |

These additions refine W05/W14 and existing proof-thread guidance. Fixed abstract lengths, mandatory method sentences, copied stylistic signatures, mathematical verification claims and publisher typography were deliberately not promoted.

## Direct mathematical writing and correction evidence

**Source:** [Kiterlin/anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing/blob/main/skill/anti-defensive-writing/SKILL.md), inspected 2026-11-02: Core Rule, Preserve Necessary Precision, Rewrite Procedure, Writing Principles, and the additional rules on unfavorable results, review comments and example use. The [MIT notice](../licenses/anti-defensive-MIT.txt) is retained with the [mathematical calling interface](anti-defensive-interface.md). At the researcher’s request, the original skill is now called directly; the interface only specifies mathematical integration, loading and semantic checks.

**Decision W19:** state the supported contribution directly, classify qualifications by their informational function, and replace redundant negative framing with the exact positive scope. Implemented at the drafting entrypoint, abstract/introduction guidance and anti-defensive interface. The mathematical adaptation keeps essential conditions in standalone claims and preserves informative counterexamples; it does not import a mandatory experimental-paper structure or generic Limitations section.

**Decision W20:** maintain symmetry between preventing overclaiming and preventing unwarranted weakening of established results. Keep verification history in internal records and required status notices at their prescribed locations. Implemented in mathematical integrity, delivery checks and E22–E24. These are writing decisions; the underlying evidence/approval gates are unchanged.

A maintainer review identified an unconditional limitations prompt and an asymmetry between preventing overclaiming and stating supported contributions directly. E22–E24 exercise the revised choices. Whether any one instruction caused a manuscript's defensive prose requires behavioral evidence. Revision pairs are supported as correction evidence; only actual researcher acceptance establishes a personal preference.

## Current publication guidance (venue policies)

These are institutional policies and practical guidance, not models of an individual mathematician's voice.

- The American Physical Society's ["Responding to Referee Reports"](https://journals.aps.org/authors/responding-to-referee-reports) supports careful reading of the decision letter, complete point-by-point responses, respectful disagreement, explicit change locations, and clarification when a request is ambiguous.
- SIAM's [Information for Journal Authors](https://epubs.siam.org/journal-authors) confirms that requirements such as a cover letter, exclusivity, related-work disclosure, permissions, and embedded figures are venue-level submission facts rather than prose conventions.
- SIAM's [illustration guidance](https://epubs.siam.org/siims/instructions-for-authors) gives a concrete production check for figure citation, reduction, line weight, grayscale, and color-blind readability.

**Inspection date:** 2026-09-04. Recheck the applicable journal's current instructions before preparing a real submission.

## Decision traceability

### 2026-11-04 exposition-quality maintenance

The quality dimensions in `exposition-and-structure.md` are a working synthesis for editing, not a validated scale or a claimed consensus ranking. Mathematical fidelity remains a prerequisite. The source principles already present were made actionable through original/revised comparisons in E25–E30; the borrowed projects below were inspected, not installed or executed.

Additional targeted reading:

- First-draft architecture follow-up: Halmos, *How to Write Mathematics*, Section 5, distinguishes organization and interconnections from their linear presentation. Tao, [Organise the paper](https://terrytao.wordpress.com/advice-on-writing-papers/organise-the-paper/), discusses milestones, grouping, placement of technical material and dependency diagrams; [Write a rapid prototype first](https://terrytao.wordpress.com/advice-on-writing-papers/write-a-rapid-prototype-first/), main procedure, moves from a skeleton through precise statements and key arguments to routine completion. The three-scale drafting guidance is our operational synthesis, not terminology or a rigid recipe attributed to these authors. The learning skill applies the distinction to prerequisite teaching as well as proof structure.
- Tao, [Motivate the paper](https://terrytao.wordpress.com/advice-on-writing-papers/motivate-the-paper/), main post: connect local work to its purpose and use a simpler case where useful. [Give appropriate amounts of detail](https://terrytao.wordpress.com/advice-on-writing-papers/give-appropriate-amounts-of-detail/), main post: distribute detail by importance and reader familiarity. [Don't overoptimise](https://terrytao.wordpress.com/advice-on-writing-papers/dont-overoptimise/), discussion of brevity: compression can make exposition worse. Implemented in proof overviews, detail allocation, and retaining clear originals.
- Igor Pak, [How to Write a Clear Math Paper](https://www.math.ucla.edu/~pak/papers/how-to-write1.pdf), Sections 1.1–1.3: clarity concerns how readers encounter and use a paper, not phrasing alone. His deliberately false introductory statement is a cautionary example, not a mathematical input. This supports treating clarity and correctness separately.

Comparable projects inspected at pinned versions:

| Project and inspected locus | Useful comparison and adaptation boundary |
| --- | --- |
| [Orchestra ml-paper-writing](https://github.com/orchestra-research/ai-research-skills/blob/773a52944ba4747a18bd4ae9ade53fff041adcbc/20-ml-paper-writing/ml-paper-writing/SKILL.md), Narrative Principle | Connect claims, support and significance. Adapt to theorem relationships; do not impose empirical-paper sections, fixed abstract formulas or routine approval pauses. |
| [slark-prime ml-paper-writing](https://github.com/slark-prime/ml-paper-writing/blob/9146d4023e0e632396725e796fcc3a40637e80ef/SKILL.md), mission and organization | Give supported contributions appropriate prominence and choose representations for their purpose. Do not adopt acceptance/marketing as the objective, fixed module counts or its additional planning objects. |
| [Lorena Barba's sciwrite](https://github.com/labarba/sciwrite/blob/347306c514619fa2806e96c8e0aa1c2db162e76f/skills/sciwrite/SKILL.md), Pass 3 and Reporting findings | Prioritize consequential paragraph problems and contextual before/after comparisons. Do not impose sentence-length thresholds or Nature abstract conventions on mathematics. |
| [K-Dense scientific-writing](https://github.com/K-Dense-AI/claude-scientific-skills/blob/a25cf9ec00e2745d03f8704acf6f6919694ccd9a/skills/scientific-writing/SKILL.md), evidence binding and bundled tools | Useful separation of evidence checks and prose. Our existing mathematical checks already cover the relevant need; no additional registries or clinical-reporting workflow imported. |

No upstream code or instruction text from these four projects was bundled. Their existence, popularity, or design does not demonstrate better writing outcomes. The comparison informed scoped editorial choices, not a competitive performance claim.

The identifiers below are maintenance handles. They map source-derived decisions to their operational implementation; they are not citations for a research paper.

| ID | Decision | Main source basis | Implemented in |
| --- | --- | --- | --- |
| W01 | Define the reader and central message | Halmos Sections 3--5; Tao writing index | `exposition-and-structure.md` → "Start with a reader and a central message" |
| W02 | Organize by logical and reader dependencies, then rewrite | Halmos Sections 5--6; Tao rapid prototype; Higham workflow | `SKILL.md` → "Work from dependency to presentation"; `exposition-and-structure.md` → "Organize around mathematical dependencies" |
| W03 | Make notation and formulas grammatical | Halmos Sections 14--16; Knuth Lectures 5--6; Conrad Sections 1--4 | `exposition-and-structure.md` → "Notation and mathematical sentences" |
| W04 | Preserve quantifiers and distinguish existence from choice | Serre "On Grammar"; Conrad Section 1 | `mathematical-integrity.md` → "Formal statement audit" |
| W05 | Expose the hard proof step | Halmos Section 10; Serre "On Proofs" | `mathematical-integrity.md` → "Proof audit and exposition" |
| W06 | Make the exact contribution visible without hype | Tao writing index; Halmos Sections 3 and 10 | `exposition-and-structure.md` → "Title and abstract" and "Introduction" |
| W07 | Use examples before abstraction only when they build the needed model | Gowers main post | `exposition-and-structure.md` → "Examples and abstraction" |
| W08 | Use concrete counterexamples when auditing prose | Conrad Sections 1--7; Knuth manuscript examples | `evaluation-suite.md` → E02--E04 |
| W09 | Treat visuals and tables as mathematical exposition | Knuth Lectures 18--19; Higham table guidance | `figures-tables-and-diagrams.md` |
| W10 | Treat writing as a workflow extending through publication | Higham third-edition record; Knuth Lectures 15--17 | `submission-and-peer-review.md`; `latex-and-bilingual-writing.md` |
| W11 | Answer referee reports completely, precisely, and respectfully | APS response guidance; Knuth Lectures 15--17 | `submission-and-peer-review.md` → "Decision letter and response ledger" and "Point-by-point response" |
| W12 | Check current venue declarations instead of inventing defaults | SIAM author guidance | `submission-and-peer-review.md` → "Establish the submission contract" |
| W13 | Make visual encoding legible without color alone | SIAM illustration guidance | `figures-tables-and-diagrams.md` → "Figures and plots" and "Captions and accessibility" |
| W14 | Learn decisions from models without copying a voice | Halmos closing remarks; Tao on one's own voice | `voice-and-genre.md` → "Preserve or learn the researcher's voice" and "Learning from other mathematicians" |

## Resolved tensions

### Lemma granularity

Tao notes that smaller pieces can improve readability, while Halmos records the opposite danger of tedious over-fragmentation. This skill uses a functional test: create a lemma when it isolates a real idea, forms a useful interface, or is reused; otherwise keep the proof continuous.

### Examples versus definitions

Gowers favors examples before abstraction when they supply a mental model. Formal definitions still need a clear, findable statement. Choose the order by reader need and signal the transition.

### Visibility versus hype

Tao asks authors to make a contribution prominent. Halmos and Knuth warn against self-praise and vague importance claims. The synthesis is to state the exact contribution, comparison, and obstruction prominently while removing unsupported evaluation.

### Prose versus compression

Serre and Knuth object to symbol-heavy writing that makes readers reconstruct grammar. Mathematical notation remains essential, but prose should state the logical relation between formulas and identify the acting objects.

## Maintenance rule

When adding a source, read the original text far enough to establish context, record a stable link, inspected locus, limitations, decision ID, and implementation target. Add only principles that change concrete writing decisions. Do not accumulate quotations, prestige lists, or generic advice. Recheck time-sensitive publication policies at the point of use and update the inspection date when their role in the skill changes.
