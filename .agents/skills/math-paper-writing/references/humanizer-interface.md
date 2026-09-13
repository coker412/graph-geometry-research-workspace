# Humanizer interface

Use this protocol when an available Humanizer skill is requested or would materially improve public-facing mathematical prose. Humanizer is optional: the mathematical writing skill must remain usable without it.

## Authority order

Apply constraints in this order:

1. the user's requested mathematical meaning and scope;
2. applicable repository and publication policy;
3. formal statements, evidence status, and checked citations;
4. this skill's mathematical integrity rules;
5. Humanizer's style preferences.

When a style preference conflicts with mathematical convention or semantic preservation, preserve the mathematics.

## Default scope

Humanizer may normally revise:

- abstract and introduction prose;
- motivation and related-work prose whose factual support is already fixed;
- section openings and transitions;
- explanatory remarks and discussion;
- conclusion prose that accurately restates established results.

Keep these regions locked by default:

- theorem, lemma, proposition, definition, conjecture, and problem statements;
- proof steps and proof-bearing computations;
- formulas and mathematical delimiters;
- bibliography records;
- evidence labels and internal verification notices.

If the user explicitly requests language revision inside a locked formal region, first record its semantic invariants and run the full post-edit audit below.

## Protected tokens and structures

Do not alter:

- LaTeX commands, environments, macros, comments, or delimiter structure;
- `\label`, `\ref`, `\eqref`, `\cite`, citation keys, and bibliography identifiers;
- symbols, indices, parameter ranges, equation numbers, and quantifiers;
- standard mathematical names and typography such as `Faber--Krahn`;
- quoted text, source titles, author names, or user-supplied terminology;
- words marking uncertainty or status, including conjectural, conditional, experimental, proof draft, and verified labels.

Humanizer's ordinary preference to remove dash characters applies only to editable prose. It must not rewrite LaTeX double hyphens, mathematical minus signs, name compounds, or numeric ranges.

## Controlled pipeline

### 1. Freeze the semantic contract

Record for the selected passage:

- each factual and mathematical claim;
- hypotheses, quantifiers, parameter ranges, and exceptions;
- defined terms and fixed terminology;
- evidence and novelty qualifications;
- citations and the claims they support;
- protected LaTeX tokens.

### 2. Invoke Humanizer in embedded mode

Ask it to return only the revised prose. Supply the target audience and, when available, a genuine author sample. Require it to preserve every item in the semantic contract and to add no fact, citation, example, or interpretation.

### 3. Re-audit the result

Compare the revision against the frozen contract. Check specifically for:

- deleted qualifiers or assumptions;
- stronger causal, novelty, optimality, or universality language;
- changed quantifiers, negations, or logical connectives;
- renamed technical objects;
- invented motivations, facts, or citations;
- changed evidence status;
- damaged LaTeX or conventional mathematical typography.

If a span fails, restore the original span or revise it under the mathematical writing rules. Do not accept a semantically unsafe sentence because it sounds more natural.

### 4. Validate in context

Read the paragraph with its neighbors and, for LaTeX, rebuild the affected document. Confirm that the author's voice is more natural without changing the paper's mathematical register.

## Style goals for mathematical prose

Humanization should remove inflated significance, vague attribution, mechanical transitions, repetitive sentence templates, and chatbot correspondence. It should not inject personality into a formal theorem or proof. In technical prose, a neutral and direct voice is often the appropriate human voice.

Preserve useful repetition, precise technical vocabulary, and conventional passive constructions when they make the mathematics clearer. A recognizable AI pattern is a reason to inspect a sentence, not permission to flatten mathematically appropriate prose.

## Handoff record

For file edits, report that Humanizer was used, identify the prose regions it touched, and state that a mathematical semantic audit followed. Humanizer use does not alter evidence status.
