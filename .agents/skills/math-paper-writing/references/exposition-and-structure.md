# Exposition and structure

These are decision principles, not a universal house style. Adapt them to the paper, audience, field, and target venue. Their source basis and known tensions are recorded in [sources.md](sources.md).

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

A common research-paper order is:

1. problem, scope, and precise setup;
2. definitions and notation needed downstream;
3. examples, counterexamples, or preliminary results;
4. lemmas that isolate the real obstacles;
5. main proof;
6. applications, and mathematically consequential boundary cases or open questions when relevant.

This is a default, not a template to impose. Reorder when the reader benefits, but do not require the reader to use an object before learning what it is.

Write a rapid structural prototype when the architecture is unclear. Then rewrite it. Drafting discovers the structure; revision makes the structure legible.

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

Write the introduction after the mathematical body is stable enough to summarize honestly. It should let an appropriate reader identify:

- the problem and why it arises;
- the verified state of relevant literature;
- the gap addressed by the paper;
- the main result, with accurate scope;
- the central proof idea and technical obstruction;
- where the arguments are located;
- a limitation or boundary case when it materially affects the claim, its interpretation, or a verified comparison with prior work.

There is no default requirement for a limitations paragraph. Lead with the mathematical contribution, retaining the conditions needed to understand it. A specific failure of a natural extension can explain the theorem; a routine reminder that the paper does not solve every larger problem adds no information. For repetitive or apologetic framing, use the [anti-defensive diagnosis](anti-defensive-interface.md).

"Sell" the paper by making its exact contribution visible, not by adding praise. Compare with previous work only after checking the comparison. If the formal theorem is too technical for the introduction, give a useful special case or a clearly marked informal statement, then point to the precise version.

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
