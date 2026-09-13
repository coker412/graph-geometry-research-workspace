# Mathematical integrity

Use this reference whenever drafting or editing material that states, explains, or depends on mathematical claims.

## Authority and evidence

Identify the source of truth before writing: a researcher-approved statement, a proof file, a verification record, a formalization, or a cited theorem. Preserve the repository's evidence vocabulary. If none exists, describe uncertainty plainly rather than inventing a certification scheme.

Language editing, compilation, additional citations, and repeated model review do not raise a claim's evidence status. Do not present a claim without qualification in an abstract or conclusion merely because it appears as a theorem in a draft.

For each main claim, maintain a compact ledger, explicitly or mentally:

| Field | Question |
| --- | --- |
| Statement | What is asserted exactly? |
| Objects | What are their types, spaces, measures, or domains? |
| Hypotheses | Which assumptions are global, local, inherited, or newly added? |
| Quantifiers | What is universal, existential, unique, uniform, or asymptotic? |
| Conclusion | What strength and parameter range are proved? |
| Support | Which proof, computation, formalization, or citation supports it? |
| Status | What evidence label does the project assign? |

After a prose edit, compare the edited claim with this ledger.

## Definition and normalization audit

Before applying an external result or writing a proof, check the definitions and normalizations that affect it. Typical fault lines include:

- weighted, unweighted, combinatorial, metric, or measured objects;
- sign and normalization of operators;
- domains, codomains, boundary conditions, and regularity classes;
- finite, connected, complete, locally finite, compact, or orientable assumptions;
- time parameters, measures, distances, and scaling conventions;
- whether a named condition means existence, uniqueness, constancy, or an equivalence.

Similar names and formulas do not establish compatibility.

## First-appearance gate

Introduce a nonstandard object before using it in a theorem. The introduction should normally give:

- its type and ambient space;
- its defining data or characterization;
- the range of its parameters;
- the convention or normalization in force;
- why it is needed in the argument.

For a map, name the domain and codomain. For an operator, state its action and sign convention. For a measure, state the base space. For a process, state the clock or generator when relevant. Local proof objects such as cutoffs, exceptional sets, index families, and auxiliary constants follow the same rule.

## Formal statement audit

Check theorem, proposition, lemma, definition, conjecture, and problem environments for:

1. bound variables and unambiguous referents;
2. existence versus a chosen object;
3. `some` versus `every`, and necessary versus sufficient conditions;
4. hidden dependence of constants or thresholds;
5. the exact parameter interval and exceptional cases;
6. all assumptions actually used by the conclusion;
7. agreement between displayed formulas and surrounding prose;
8. words such as `sharp`, `optimal`, `classification`, `counterexample`, and `if and only if` that require full support.

Do not refer to "the map" after proving only that a set of maps is nonempty. Either define or choose the map first, or state the property with the correct quantifier.

## Proof audit and exposition

Separate proof correctness from proof presentation. When checking correctness, reconstruct each implication and inspect:

- unstated assumptions and circular dependencies;
- division by a possibly zero quantity;
- sign errors, boundary cases, and empty cases;
- unjustified limit, sum, derivative, or integral interchange;
- existence of every constructed object;
- compatibility with every external theorem invoked;
- whether a claimed general result was proved only in a special case.

When presenting a correct proof:

- state the strategy before technical detail when it helps orientation;
- identify the difficult step rather than hiding it behind "standard" or "by definition";
- use a lemma when it creates a meaningful interface, isolates a genuine obstruction, or will be reused;
- do not fragment a continuous argument into ceremonial lemmas;
- explain where a hypothesis enters when that is not evident;
- distinguish intuition and heuristic motivation from formal inference.

If a gap is found, preserve the strongest valid part, locate the exact failure, and state its effect on downstream claims. Do not silently fill the gap with plausible text.

## Citations and originality

Distinguish two citation roles:

- **proof-bearing:** an external result supplies a logical step;
- **contextual:** a source supplies history, motivation, comparison, or terminology.

For a proof-bearing citation, inspect the original theorem and its surrounding definitions. Record the assumptions, normalization, theorem identifier, and the reason the present objects satisfy its hypotheses. A citation in the introduction does not support an invocation in a proof unless the interface is made clear.

Verify authors, title, venue or archive identifier, year, and stable identifier before adding bibliography data. Do not claim novelty, openness, priority, or improvement from search snippets, abstracts, or absence of a result in a small search.

## Public-claim gate

Before writing an unrestricted main result into a title, abstract, introduction summary, or conclusion, confirm the repository's required evidence and approval gates. If a result is provisional, keep its status visible in the appropriate internal draft and do not let polishing remove that qualification.
