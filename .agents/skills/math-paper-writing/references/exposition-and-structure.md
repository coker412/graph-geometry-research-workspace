# Exposition and structure

These are decision principles, not a universal house style. Adapt them to the paper, audience, field, and target venue. Their source basis and known tensions are recorded in [sources.md](sources.md).

## What a writing improvement must accomplish

Use the following dimensions to compose a first draft and to diagnose a revision, with mathematical fidelity checked against the source results throughout. Assess exposition for the intended reader separately from the novelty or importance of the result; these are not a universal score:

| Dimension | Evidence to look for in the text |
| --- | --- |
| Purpose and emphasis | The problem and mathematical payoff are identifiable; central results have appropriate prominence and context. |
| Organization and continuity | Statements, explanations, and proof phases appear in a usable order; transitions carry an actual mathematical relation. |
| Explanatory depth | Difficult choices and decisive steps receive enough explanation; standard material does not bury them. |
| Precision and usability | Notation is manageable, hypotheses and references are findable, and a reader can check or apply the result. |
| Prose and economy | Sentences have clear subjects and relations, paragraphs develop their point, and length serves the reader. |

These dimensions can conflict. A longer explanation may resolve a genuine obstacle; a shorter version may obscure it. For revisions, name the benefit and cost with locations in both texts; preserve the original when the alternative only sounds different. For first drafts, check whether the artifact actually explains the problem, develops the argument, and supplies its promised content. Word counts, readability formulas, compliance checklists, and model preferences do not establish reader understanding. For structured maintenance tests, see [evaluation-suite.md](evaluation-suite.md).

## From results to a first draft

Build the paper around the mathematical work the reader needs to understand. Use the available results and proofs to make these editorial choices while drafting:

- **Select the focus.** Decide which result answers the paper's main question, how other results contribute, and what mathematical significance the sources actually support. Give the draft a specific title and a coherent purpose; avoid narrating the research chronology.
- **Design the route.** Supply enough setup to understand the main statement, then arrange proof ingredients in a useful reading order. Design notation where none is fixed. Choose examples, diagrams, and lemma boundaries for a concrete explanatory role.
- **Explain the ideas as they enter.** When an auxiliary object, estimate or construction first appears, show what it accomplishes. Write out the decisive link in the proof rather than leaving a list of techniques to expand later.
- **Test the architecture in prose.** For substantial work, sketch the key statements and their dependencies, then write the hardest connection before polishing routine material. If that passage reveals a missing input, an awkward detour or an unsuitable lemma boundary, revise the structure and continue. Do not freeze every heading in advance or pause for approval at each ordinary drafting step.
- **Allocate detail and write connected prose.** Develop unfamiliar or consequential steps; keep routine work proportionate to the audience. Each paragraph should advance the current mathematical question, and each technical detour should return to it.
- **Complete the requested artifact.** Write the body, including the supplied proof work, and derive the abstract and introduction from the stable argument. A structural prototype helps when needed, but is an intermediate step. Use an existing style profile selectively from the outset when requested, rather than relying on a final cosmetic pass.

Keep source-supported claims and their status intact throughout. Missing mathematics remains an identified gap; missing exposition is work to complete in the draft. Review the draft for its mathematical content and its effectiveness as a paper, without requiring an earlier prose version to compare against.

## Start with a reader and a central message

Choose a concrete target reader. Estimate what that reader already knows, what must be defined, which examples are familiar, and where the first genuine difficulty occurs.

State the paper's central mathematical contribution in one accurate paragraph before designing the full narrative. If there are too many unrelated messages, narrow the paper or make their relationship explicit.

When turning research notes into an English paper, organize around the strongest supported results and their proof method, not the latest research steps. State the principal theorems and their relationship early; develop the lemmas that prove them, and explain a limitation when it affects the result or its interpretation. An internal draft still needs this paper structure. Keep a concise evidence qualification, but move task numbers, audit history, failed attempts and source-file inventories outside the paper. A counterexample belongs in the narrative when it establishes a stated mathematical limitation. If a project-specific argument is central to a main theorem, include its proof rather than treating the project's own note as an unexplained black box.

At each transition, ask:

- What does the reader know at this point?
- What question or obstruction is now active?
- Why is the next object, lemma, or section appearing here?
- What should the reader retain after this paragraph?

## Organize around mathematical dependencies

Organize at three connected scales. These are drafting decisions, not three mandatory outlines or a quota of headings:

| Scale | Decisions to make |
| --- | --- |
| Whole paper | What question connects the results? Where should the reader meet the main statements, necessary setup, proof mechanisms and consequences? What belongs in the main text or an appendix? |
| Section and proof | What does this part establish, which inputs does it need, and where is its output used? How do construction, estimates, choices and closure fit together? Which technical detour earns a separate lemma? |
| Paragraph and calculation | What is the immediate goal? Why introduce this object or choose this parameter now? What justifies the next displayed relation, and how does it advance the proof? |

Logical dependence and reading order are different. A theorem may be stated before the lemmas proving it, provided its objects are already introduced; the proof must still receive the inputs it uses. When several premises are jointly necessary, retain that conjunction. A dependency diagram helps with branching, but a short argument needs no graph.

Connect the scales: a calculation supplies a proof step, a proof step closes a module, and the module advances a stated result. A list of section titles or lemma numbers does not show these connections. Choose the route for the actual contribution: a classification may start from its invariant, a construction from the object it builds, and an estimate from the quantity it controls. Keep related material together and avoid forcing unrelated results into one slogan.

For a substantial first draft, move from a compact structural prototype to the difficult connections, then complete the body and revisit the global arrangement. New local difficulties can require changes at the larger scales. A clear short argument can be composed directly; the aim is an effective paper, not a separate architecture document.

## Title and abstract

The title should identify the main object, problem, result, or method without promotional language or unsupported priority claims.

An abstract should stand alone and answer:

- What problem is studied, and in what setting?
- What is the main result at its actual evidence level?
- What scope or qualification must accompany the result for this standalone statement to be accurate?

State an established result directly at its supported strength. A precise object class, parameter range or hypothesis often supplies the required scope by itself. Do not append a generic disclaimer or a list of extensions the paper never aimed to prove.

Mention a method only when needed to identify the contribution or requested by the author. An explicit request for a short setting-and-results abstract takes precedence over a generic problem-method-results pattern; do not add a stock proof-method sentence or reopen an accepted abstract during unrelated edits.

Do not put proof details, undefined notation, or claims absent from the body into the abstract. Prefer a precise modest result to a broad slogan. State the contribution and each necessary qualification once; do not pad an approximate word target by restating the same hypothesis or by commenting on the wording (for example, that the abstract “retains an explicit hypothesis”). If the available content supports a shorter abstract, keep it shorter and put any editing explanation outside the manuscript.

## Introduction

Treat the introduction as a substantial piece of mathematical exposition. In whole-paper drafting, write it after the body has stable main statements and a developed proof structure. Decide the question, contribution and reader's route during initial planning; those decisions need not be written as an introduction. Then compose the introduction from the actual results and argument, and check it against the body. If the user requests only an introduction or explicitly wants an early draft, work from the available source material and identify any unresolved dependencies rather than requiring an entire manuscript first.

**Compose from concrete anchors.** Locate the main statement and scope, the proof passage carrying the central idea, and the closest verified literature relevant to the comparison. Choose a route that explains the question, what the result changes, and how the argument achieves it. Write connected prose; a bibliography tour followed by a list of theorems is not enough. Keep anchors in the existing working context or review notes, not a mandatory new file. If comparison evidence is missing, draft the supported mathematics and report the missing comparison separately; do not invent a gap.

Give the main result appropriate prominence. If its formal version requires too much setup, introduce a useful special case or a clearly marked informal statement and point to the precise version. Explain significance through what can now be classified, constructed, estimated or deduced. Explain the mechanism by a causal connection in the proof, not a list of method names. An obstruction belongs here when it explains an actual choice or innovation.

**Read back the delivered prose.** After drafting, try to recover from the introduction alone: the question; the result and its scope; its mathematical payoff or verified relation to earlier work; and the decisive idea. Point to the sentences supplying the answers. Do not fill missing links from your knowledge of the body. Then cross-check those answers against the source anchors, including constants, quantifiers and the attribution of methods. This same-context exercise detects omissions and mismatches; it is not a test with an unfamiliar reader.

**Repair the diagnosed problem and repeat the affected check.** If the result is buried, move it; if a connection is missing, write that connection; if background obscures the question, shorten or relocate it. When the body changes, revisit the affected introduction claims. Deliver the prose, with a brief review note stating any unresolved substantive issue. Do not substitute a compliance checklist for the introduction or claim that following this process guarantees good writing.

Scale the introduction to the paper and audience. There is no fixed paragraph count or mandatory roadmap, novelty slogan, obstacle, or limitations paragraph. Give navigation when it helps locate a substantial argument. A specific failure of a natural extension can illuminate the theorem; a list of assumptions the paper does not need usually adds nothing unless a verified comparison makes it informative. Avoid invented history and applications. For repetitive or apologetic framing, use the [anti-defensive diagnosis](anti-defensive-interface.md).

## Transfer arguments and informal overviews

### Explain a transfer at the point where the old argument changes

When extending an established result to a new setting, identify the relevant earlier theorem, the property its proof uses that is unavailable here, and the replacement actually established in this paper. State what survives unchanged and where assumptions or constants change. Do not invent a failed step if the contribution is a new application rather than a new proof mechanism.

For a cross-field method, give the necessary correspondence between objects and explain how the imported conclusion returns to the original problem. A useful explanation names the estimate, compactness principle or construction that does the work; merely naming another field does not. Preserve the target manuscript's notation and introduce new language only when it earns its place.

### Make the simplifications in a proof overview explicit

If a sketch suppresses error terms, replaces an object by a model, or temporarily ignores a boundary case, say which simplification is being made and point to the formal statement that restores it. If no such statement is available, preserve the gap. A heuristic should explain the mechanism without being mistaken for the proof. A result for a modified equation or larger class must remain distinct from a result for the original problem.

These are optional exposition tools supported by the [corpus models](author-models.md), not requirements to lengthen every introduction or accepted abstract.

## Examples and abstraction

Use an example before an abstract definition when the reader otherwise lacks a mental model for the definition. Use counterexamples to explain why an assumption, formulation, or hoped-for strengthening is necessary.

Do not make "examples first" automatic. A short standard definition may be clearer first for specialists. Whichever order is chosen, signal it and connect the example to the exact feature it is meant to illuminate.

Examples should do mathematical work: motivate a definition, test a boundary, expose a failed implication, or preview a mechanism. Remove decorative examples with no downstream role.

## Theorems, lemmas, and proofs

State a theorem before proving it, with enough local context to understand its hypotheses and conclusion. A formal statement should not depend on an ambiguous pronoun or an object chosen only inside a previous proof.

Use lemmas to factor a proof when they create clear interfaces or isolate distinct ideas. Avoid both extremes: a monolithic proof with hidden structure and a parade of trivial lemmas that obscures the main argument.

Before a difficult proof, explain the strategy and name the obstacle. During the proof, keep the current goal visible at genuine changes of phase. After a key lemma, state how it advances the main theorem when the connection is not immediate.

A proof overview should reveal a decisive relationship, not only name techniques or list sections. For an estimate this may be the term that absorbs an error; for a gluing argument it may be the compatibility supplied on overlaps. Use the mechanism actually in the source. Allocate detail by the reader's difficulty: expand the unfamiliar choice or implication, and keep routine steps concise without hiding dependencies. A research paper and a beginner's learning edition need different amounts of expansion.

Write calculations in the direction a reader can follow. If a computation is long and unavoidable, explain its inputs, intended output, and internal checkpoints. Never use a proof-ending symbol to conceal a missing argument.

### Keep the proof thread continuous

Local correctness does not by itself make a proof readable. In a proof with several stages, name the target quantity, contradiction, or persistent family near the beginning and keep that object visible through the argument. Give stable notation to an object that is constructed in one stage, selected in another, and used at closure.

Keep the main implication or equation chain together whenever possible. A long approximation, regularity, sign, or boundary justification may follow the main chain if the paper clearly says which formula is being justified; after the detour, explicitly return to that formula. If an auxiliary lemma is proved first, state its exact substitution into the main proof rather than expecting the reader to infer the connection.

At the end of a multi-stage proof, identify the earlier outputs being combined and verify that their quantifiers concern the same object. Typical failures are combining “every candidate” with an unstated candidate, selecting a subsequence twice, changing a parameter after an object depends on it, or proving estimates on two different domains.

Use a compression test during revision: read only the proof's opening, phase transitions, displayed connecting formulas, and closing paragraph. Those pieces should still reveal the target and the complete causal route. If the main object from the theorem statement disappears, repair the proof spine before polishing individual paragraphs.

### Factor technical arguments at genuine interfaces

Turn a technical passage into a lemma when it has a precise input-output statement, will be invoked later, or would substantially interrupt the proof that uses it. State and prove that lemma before the main invocation. If its proof is self-contained but secondary to the paper's conceptual mechanism, place the proof in an appendix and give an explicit forward pointer with the lemma statement. The reader should never have to guess whether a formula being used is assumed, previously proved, or scheduled for proof much later.

Keep a short calculation or one-use substitution inside the proof. More lemmas do not automatically mean more clarity: avoid a sequence of ceremonial results whose statements are harder to follow than the continuous argument. During final review, ask whether each extracted lemma creates a reusable or conceptually meaningful interface, and whether every long detour left in the main proof is genuinely part of its central mechanism.

## Notation and mathematical sentences

Design notation before it proliferates. Prefer a small, consistent alphabet over nested subscripts and ad hoc renaming. Do not use the same symbol for different objects in one live context.

- Define variables at first appearance.
- Do not begin a sentence with a bare symbol when a noun can identify the object.
- Connect neighboring formulas with words that state their logical relation.
- Use prose for logical verbs instead of forcing punctuation or symbols to carry them.
- Punctuate displayed mathematics as part of the sentence.
- Remove symbols that add no information.
- Preserve deliberate repetition when synonym changes would blur a technical distinction.

Read prose once while mentally replacing substantial formulas with placeholders. The sentences should still reveal the argument's direction.

## Natural mathematical prose

Prefer accurate, direct sentences. Vary sentence length and structure enough to avoid mechanical rhythm, but keep parallel structure for parallel mathematics. Repeat the mathematical noun when a pronoun could refer to several objects.

When a paragraph feels disconnected, inspect the mathematical subject and purpose of each sentence. Connect established information to the next new point, and separate genuinely different jobs when needed. A transition word cannot replace a missing implication. Retain a natural sentence rhythm rather than compressing several readable steps into one dense sentence.

Avoid:

- vague authority such as "it is well known" without an appropriate source or proof;
- promotional adjectives and unsupported statements of importance;
- formulaic opening and closing paragraphs;
- strings of participial phrases that imply consequences not established;
- excessive signposting that announces rather than explains;
- synonym cycling for fixed mathematical terms.

The author's voice may be present in motivation and informal remarks, but formal claims must remain distinguishable from opinion or heuristic explanation.

## Revision passes

For a substantial paper, separate at least these concerns:

1. **Mathematics:** reconstruct definitions, claims, and proofs.
2. **Reader:** follow first appearances, motivation, and dependency order.
3. **Sources:** check theorem interfaces, history, and originality claims.
4. **Language:** improve cadence, precision, and paragraph function without semantic drift.
5. **Production:** check versions, references, figures, and builds.

Do not report that a paper is finished when only the language or typesetting pass has succeeded.
