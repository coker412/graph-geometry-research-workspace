---
name: math-paper-study-guide
description: Explain mathematical papers and reconstruct proofs; create self-contained study PDFs with editable source for whole-paper learning (Chinese by default), or answer focused reading questions. Not for manuscript editing, ordinary translation, or standalone proof search.
---

# Mathematical Paper Reading and Study

Help the reader understand a paper's objects, use its inputs, and reconstruct its decisive reasoning. Preserve the source mathematics and keep teaching material separate from submission manuscripts. A completed artifact does not establish reader understanding or certify the source proof.

## Choose the requested scope

Use the request and existing preferences without an intake questionnaire or preliminary quiz.

- **Focused question or passage:** explain the requested step in the conversation, including its local prerequisites and source location. Do not automatically create files, a PDF, or a new project.
- **Whole-paper learning:** by default deliver a self-contained study PDF and editable source first, unless the user asks for conversation only or another format. Complete the agreed scope, necessary prerequisites, and decisive calculations; an outline or first installment is not the requested guide.
- **New or revised study edition:** put the necessary teaching inside the requested artifact. In an authorized revision, integrate explanations at the relevant locations in the existing edition instead of making a new note or PDF for each question. Preserve its architecture unless structural change is requested.

Default to Chinese unless the user chooses another language. Default to a reader fluent in calculus and linear algebra who only vaguely recognizes advanced-course concepts; an explicit reader background overrides this. An English edition uses the same teaching standard and does not imply a specialist audience or a submission manuscript.

This skill controls teaching structure and detail. Optional author profiles or language cleaners must respect the declared reader's needs: a worked calculation, prerequisite explanation or purposeful restatement is not disposable merely because a specialist paper could be shorter. Complete teaching-content decisions before language cleanup; return substantive changes to this stage rather than letting a cleaner remove untaught steps.

## Establish the source and its boundaries

Identify the exact accessible source/version, agreed scope, source status and gaps, whether auditing is requested, and the notation and labels to preserve. Follow applicable repository instructions already in context.

- Abstract-only or excerpt-only access supports that scope. Obtain missing text before claiming whole-paper coverage; do not reconstruct an unseen proof from its title.
- Preserve assumptions, quantifiers, conclusions, and evidence status. Use the source's labels when available; otherwise describe publication/draft status and unchecked additions in plain language rather than requiring a private verification system.
- Distinguish source mathematics, prerequisite teaching, added calculations, and optional checkpoints. State unchecked additions concisely near the front; keep detailed audit history outside the teaching narrative. Never silently fill a source gap or present a pedagogical derivation as new certification.
- Preserve source notation and theorem/equation/page pointers. A proof-bearing source change requires rechecking affected companion explanations, not merely updating a date or title.
- If manuscript editing is also requested, use the available `math-paper-writing` skill for that portion. When the user wants the English paper first, stabilize its mathematical narrative before deriving the learning edition. A research-status report is not that manuscript. A study edition alone does not request an additional formal Chinese translation.

## Teach the operations that the proof needs

Start with the exact problem and result. Explain the prior inputs actually invoked, the bridge supplied by the paper, and how the proof reaches its target; do not force a fixed number of prerequisite papers.

At a difficult step, identify the current obstacle, why the auxiliary object or estimate helps, the decisive calculation, and where its output is used. Keep the same target and persistent objects visible across technical detours. Distinguish an unfamiliar object, inability to perform an operation, misleading intuition, missing motivation, and a missing implication; they need different explanations.

For an unfamiliar operation, introduce its objects and notation, work an accessible example, and connect the calculation to the paper. For example, actually diagonalize a matrix before using its fractional powers; expanding “by the spectral theorem” into a longer sentence does not teach the operation. A contrasting example can clarify a hypothesis, but do not require a quota of examples for every definition. Explain where an analogy stops and the general theorem begins.

Reconstructed motivation is one way to understand a choice, not the author's historical discovery process unless documented. Deep external theorems may remain declared inputs: explain their objects, hypotheses, conclusion, a meaningful example, and the precise application here. The paper's own decisive reasoning still needs a continuous, worked explanation.

## Make the proof navigable

Scale the structure to the task; a short argument may need only connected paragraphs. For substantial learning material in any language or requested medium, provide:

1. **Whole-edition route:** connect the exact problem and result to a small set of meaningful proof modules, each with input conditions, precise output and next use. Arrange the reader's path through them, including prerequisites needed at each point; do not copy the source's page order automatically.
2. **Module and proof structure:** explain the local target, obstacle, construction or estimate, and closing step. Show how hypotheses are met and how each output returns to the main line. Distinguish logical dependence, prerequisite knowledge and reading order; jointly needed premises remain a conjunction.
3. **Paragraphs and calculations:** teach the operation needed at the point of use, expand decisive calculations, and connect their output back to the module's goal. State objects, parameter ranges and dependencies mathematically. Group by meaningful work, not one node or heading per formula.

In a PDF, use a proof overview, navigable sections, and local derivations or clearly linked appendices. Give a compact diagram when branching matters; a short linear argument can use an implication chain. If an interactive reader is requested, preserve the same dependencies when folding modules and provide usable navigation and diagram controls. Required PDF explanations must not be deferred to a website or chat.

## Deliver, then refine from feedback

For a whole-paper or structural task, use the first-draft procedure and completion checks in [the study-edition method](references/chinese-study-edition-method.md). Work backward from the conclusion, expand the hardest dependency chain before polishing, and finish the other modules. Known teaching gaps belong in the initial PDF, not in a promised follow-up.

Include optional reconstruction questions or nearby examples only where they test a real bottleneck, with worked guidance and reference explanations in the artifact. Never withhold an explanation until the reader answers, or replace untaught reasoning with an exercise. Track demonstrated understanding separately from supplied teaching; silence, paraphrase, and finished checklists do not establish mastery.

For a useful learning check, ask for an operation the explanation has taught: choose a parameter, verify an input hypothesis, or carry out a nearby calculation. Provide its worked answer and point to the teaching that supports it. An assistant's successful calculation checks the explanation's coverage, not the human reader's understanding; do not turn it into a mastery score.

Use a topic-specific PDF filename and matching editable entry point, such as `<论文主题>-中文学习稿.pdf` or `<topic>-study-guide.pdf`, unless the user has chosen another convention. Reuse the owning directory and build location. Inspect a named successful example's difficult passages before following its teaching approach; do not copy its page count or headings.

The default cycle is **first complete PDF → reader feedback → revision**. Put paper-specific explanations back in that edition. Refine shared guidance only when feedback supports a transferable decision, consolidating existing advice rather than adding a universal rule or a separate feedback log for each question. A proposed explanation remains untested until there is relevant reader evidence.

## Read supporting guidance selectively

- For a whole-paper task, new edition, or structural rewrite, read [chinese-study-edition-method.md](references/chinese-study-edition-method.md); its teaching standard also applies to English. Use the [Chinese LaTeX template](assets/main-study-zh-template.tex) only when no compatible project structure exists.
- For a focused question or local edit, read only the corresponding method section: reader operations, proof modules, calculation granularity, source synchronization, or the specific learning obstacle. Do not turn a local question into the whole-paper workflow.
- For concept formation, proof motivation, structural understanding, or learning checks, consult the relevant section of [mathematics-education-psychology.md](references/mathematics-education-psychology.md). Its educational interpretations are design choices, not evidence of effectiveness for this reader.

## Check the result at the requested scope

For repeated file work, execute the optional [PDF page reader](scripts/pdf_pages.py) or [TeX log scanner](scripts/check_tex_log.py) with `--help`; do not load their implementations for ordinary use. Prefer existing editable source or page-labelled text. The reader caches unfiltered extracted text against the PDF SHA-256; by default it prints an index, with `--find` for locating pages and `--pages` for complete page text. An index or a few pages cannot stand in for whole-paper reading. Empty extracted pages need visual/OCR inspection. The log scanner summarizes the actual build's `.log`/`.blg` files; still check build status, freshness and rendered pages as described below.

Compare source and explanation for hypotheses, dimensions, quantifiers, definitions, signs, scaling, norms, limits, base-point dependence and boundary terms. Overview, detailed derivation and reconstruction must agree. Report suspected source gaps without disguising them as exposition or silently repairing the theorem.

For a full edition, inspect the finished PDF using only its declared reader background and external inputs. Locate a difficult chain's prerequisites, choices, calculations and return to the target at actual PDF locations. Repair connections that require remembered chat or hidden source comments. Check one joint dependency and one external input when present, and that reference answers follow from material already taught. Assess mathematical coverage and teaching accessibility separately; this is editorial self-review, not learner testing.

Use the project build command when available. Otherwise the method gives a portable XeLaTeX build; the bundled Chinese template uses ctex and Fandol. If an engine or font is missing, retain the completed editable source and report PDF delivery as pending rather than claiming a nonexistent file. After changing LaTeX, build affected entry points and inspect errors, undefined/duplicate references, bibliography/package warnings, overfull/underfull boxes and the rendered pages. Compilation checks typesetting, not mathematics.

Report the delivered scope and paths, source/version status, checks, and remaining gaps. A focused conversational explanation needs checks for that explanation, not a full-paper build.
