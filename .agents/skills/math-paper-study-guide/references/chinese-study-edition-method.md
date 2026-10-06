# Method for a Chinese mathematical study edition

## Origin and scope

This method was developed from an internal scalar-curvature study edition. The recorded entry-point SHA-256 is `c127be33068ee0ce812d154a7a4236a3795dc502bb130808349269806d777bc2`; its modules were study-guide, introduction, slices, path, clock, ambient, completion, and reconstruction. The private manuscript is not part of the public framework.

This records teaching and exposition choices, not the source paper's mathematics. Identify each new paper's own dependencies, difficult steps, and evidence status instead of copying module names or counts.

## Core design

Preserve a mathematical core that can be compared with the source, supply prerequisites/calculations where readers actually need them, and enable eventual reconstruction without the text. Sentence-by-sentence translation and pasted review records are insufficient.

```text
Precise problem and main result
        ↓
One-sentence mechanism and proof dependencies
        ↓
Prerequisites → proof module → decisive calculation → checkpoint
        ↑                                             |
        └──────── repeat for essential modules ────────┘
        ↓
Proof-reconstruction list and mastery criteria
```

## Front matter

### Source and status

Use a short status box naming the source/frozen version, its evidence level, and any new teaching calculations. Keep it concise rather than defensive.

### Mechanism in one sentence

Explain the causal chain: what is constructed, how pieces connect, which positive term controls which error, and how the target follows. Do not merely repeat the abstract.

### Staged reading

- First pass: objects, target quantity, mechanism, module inputs/outputs; long calculations may be skipped.
- Second pass: recompute decisive identities/inequalities and identify how each error is absorbed.
- Third pass: close the text and reconstruct definitions, dependencies, and estimates.

Give testable completion criteria for each pass. Vague requests to read carefully or understand deeply are insufficient.

### Key quantities

List only persistent quantities with distinct roles. Give their type, definition, and proof function. Introduce one-use notation locally.

## Proof modules

The following are teaching functions, not five blocks to concatenate. Supply prerequisites before first use and decisive calculations beside the steps they explain. Short checks can close a section. Do not make readers finish a compressed proof before receiving the knowledge needed to understand it.

1. State the module's inputs, obstacle, and output in a paragraph.
2. Review only definitions, formulas, and intuition immediately needed; identify details that can be skipped on the first pass.
3. Preserve exact statements/dependencies while reorganizing the learning narrative. Match source mathematics and citations, not necessarily paragraph order.
4. Expand error-prone calculations: second derivatives/chain rules, curvature signs/index raising, scaling/volume factors, boundary terms/endpoint parity/smooth extension, block-matrix positivity/mixed terms, and the distinctions between limits, limsups, subsequences, and all sufficiently large parameters.
5. Ask why the module works, which step drives it, and where its output is used.

Give decisive constructions and estimates full treatment; combine easy connecting passages.

### Proof continuity

Start a long proof with its target quantity, proposition, or contradiction. Keep stable notation for persistent objects. Present the main equality/implication chain before a long technical verification, then explicitly connect that verification to the formula it establishes.

For stepwise constructions, identify the prior input, output quantifiers, later use on the same object, and whether final outputs concern the same box, subsequence, parameters, or candidate family. A sequence of disconnected local achievements is insufficient.

Check the central object throughout: if it disappears for a long stretch or an auxiliary construction never reconnects to the goal, repair the exposition. Reading step openings, endings, and connecting formulas should reconstruct the causal chain.

### Lemmas and appendices

A long technical passage with a clear hypothesis/conclusion interface, used later only through its conclusion, should normally become a lemma. Approximation, regularity, boundary-trace, or lengthy constant checks may move to an appendix if they are not the conceptual mechanism. State the result precisely before use and point to its full proof.

Keep short one-use algebra and direct substitutions inline. Split by meaningful mathematical interfaces and clearer causality, not page count or desired numbering.

## Auxiliary environments

`prerequisite` supplies the minimum background needed for the next page: geometric meaning, formulas, conventions, or endpoint/regularity intuition. It is not an unlimited textbook chapter.

`calculation` explains the move between two source lines: differentiation variables, identities, signs, and sufficient estimate margins. End by stating what the calculation accomplishes in the main proof.

`checkpoint` asks what the reader can reconstruct with the text closed. Test causality or a decisive calculation, not yes/no responses or irrelevant constant memorization.

## Track distinct obligations separately

The source example separately tracked nonnegative Ricci curvature and divergent scalar-curvature mass. Other papers may separate existence/regularity, local construction/global gluing, main-term lower bounds/error control, geometric/integral or topological properties, or qualitative results/optimality.

Explain which obligation each new object serves so readers understand why a formula is needed.

## Detail level

Expand steps where one error invalidates the conclusion; nontrivial arguments hidden behind direct calculation or standard reasoning; ambiguous variables, scales, endpoints, measures, or tensor types; and passages from local/subsequence results to global quantifiers.

Do not repeat identical mechanical substitutions, unrelated background, already explained standard facts, or audit/revision history.

## Source synchronization

Match theorems, formulas, assumptions, and labels wherever possible. Make added explanations identifiable, including concise markings on expansions placed directly in proofs. Keep source-comparison records; do not disguise a new proof as the source argument.

A proof-bearing source change makes the companion potentially stale. Added calculations aid understanding without raising evidence levels. If they expose a gap, return to the source and proof-audit process rather than bypassing it only in the companion.

## Completion checklist

1. Does the opening state the problem, conclusion, source version, and evidence boundary accurately?
2. Does the short mechanism describe the full chain from construction to conclusion?
3. Does each module specify inputs, obstacle, and output?
4. Is every nonstandard object typed, defined, and motivated before use?
5. Can decisive calculations be recomputed line by line, including signs, powers, norms, and boundary terms?
6. Are pointwise/integral, local/global, subsequence/full-limit, and fixed/uniform parameters distinguished?
7. Do checkpoints test the actual bottlenecks?
8. Does reconstruction cover all essential dependencies rather than summarize sections?
9. Have duplicate translations, empty encouragement, audit logs, and defensive prose been removed?
10. Are source comparison, forced LaTeX builds, and log checks complete?
11. Do long proofs retain their target objects, reconnect technical detours, and combine outputs on the same objects?
12. Are long technical steps factored through clear interfaces without fragmenting short calculations?

## Lessons from a later internal study edition

A later private study edition refined these rules; its files are optional teaching references, not required mathematical inputs for other projects.

Show the complete target chain early. For example, explain the incompatible upper/lower bounds on the same pair of boxes before the finite-tree argument that selects them. Find the new paper's own persistent objects and closed chain rather than listing module names.

Use a short example to explain an unfamiliar object's purpose only when it removes a real obstacle, and check the example's hypotheses. An affine map's translation increment can explain why subtracting a constant vector suffices.

Organize hard proofs causally, expand necessary calculations in place, and track objects and parameter dependence. Checkpoints test material already taught; they must not delegate omitted essential derivations to the reader.

Reading routes should point to exact propositions, equations, or pages, specifying which input is provisionally accepted and when to return to its proof. Three generic reading passes do not replace this route.

For teaching acceptance, read the hardest chain from the intended reader's starting knowledge. At each step ask why the quantity is introduced, how the next line follows, and where the output is used. Record and repair actual sticking points. Report this reading check separately from mathematical audit; page counts, supplement counts, and matching labels do not establish teaching quality.
