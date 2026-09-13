# Figures, tables, and diagrams

Read this reference when creating, editing, or auditing visual mathematical material. A visual is part of the mathematical argument: its labels, caption, data provenance, and surrounding claims must be checked with the same care as prose.

## Give every visual a mathematical job

Before adding a visual, state what relation it makes easier to see. Appropriate jobs include:

- comparing several exact quantities or regimes;
- showing a geometric construction, dependency, or limiting behavior;
- separating cases or illustrating why a hypothesis is needed;
- presenting reproducible computational evidence without promoting it to proof.

Do not add a figure because a section looks visually empty. If one sentence or a small formula communicates the relation more accurately, use it.

Introduce and cite each visual in the prose near its first use. The prose should tell the reader what to inspect and what conclusion is justified. It should not merely say that a figure or table exists.

## Mathematical and visual contract

Record, explicitly or mentally:

| Field | Check |
| --- | --- |
| Objects | What mathematical objects or data are shown? |
| Parameters | Which values, ranges, units, normalizations, and scales are used? |
| Encoding | What do position, color, line type, marker, shading, and arrows mean? |
| Claim | What may the reader infer, and what remains only illustrative? |
| Provenance | Which source, script, data, or theorem produced the visual? |
| Reproduction | Can the visual be regenerated from recorded inputs? |

Keep the plotted domain, numerical precision, exceptional cases, and normalization consistent with the surrounding statement. A schematic diagram must be identified as schematic when distances, angles, or proportions have no quantitative meaning.

## Figures and plots

- Label axes, units, parameters, curves, regions, and exceptional points that carry meaning.
- Choose bounds and aspect ratios that do not visually exaggerate or conceal behavior.
- Do not distinguish mathematical cases by color alone. Add line styles, markers, labels, or patterns, and check grayscale readability when print is possible.
- Make text, symbols, and line weights legible after reduction to the journal's column width.
- Prefer vector output for line art and diagrams when the toolchain and venue support it; use adequate-resolution raster output for image data.
- Keep notation in the visual consistent with the paper. Define any abbreviation in the caption or surrounding prose.
- Do not smooth, truncate, rescale, or omit data in a way that changes the apparent mathematical conclusion without disclosing the operation.

For computational figures, preserve the generating script, data source, parameter file, random seed when relevant, software environment, and exact output path according to local policy. The caption or nearby text should distinguish a theorem-backed curve, a numerical approximation, and a heuristic guide.

## Tables

Use a table when rows and columns support an exact comparison. Give columns unambiguous headings with units and parameter conventions. Use consistent precision and align comparable numeric entries.

Group columns by mathematical role instead of decorating the grid. Use whitespace and a small number of rules to reveal structure; do not assume that a particular LaTeX package or house style is accepted by the target venue. Explain missing, undefined, infinite, or nonconvergent entries rather than leaving ambiguous blanks.

Do not duplicate a table as a plot unless the second representation answers a different reader question.

## Commutative and dependency diagrams

- Type every object and arrow: domain, codomain, direction, and construction must be recoverable from the text.
- State which regions commute and why; drawing two paths with common endpoints does not prove that the composites agree.
- Distinguish canonical maps, chosen maps, isomorphisms known only to exist, inclusions, projections, and identifications.
- Check signs, orientations, variance, grading shifts, and arrow direction.
- If a diagram summarizes proof dependency rather than mathematics, label it as an expository dependency diagram.

## Captions and accessibility

A caption should identify the visual, define local encodings and parameters, and state the intended observation. It should not introduce an unproved conclusion or carry a hypothesis that is missing from the main text.

When the venue supports alternative text, describe the mathematical relation or trend that a reader cannot recover from the filename alone. Do not copy the caption mechanically into alt text. Follow current venue requirements for accessibility, file type, dimensions, fonts, and permissions; these requirements change over time.

## Rights and external material

Do not assume that citation alone permits reuse. Record the source and verify whether permission, a license notice, or redrawing is required. Never fabricate a permission statement or claim ownership of externally produced material.

## Validation

After editing a visual:

1. compare every label, value, and visual claim with its mathematical or computational source;
2. inspect the rendered output at publication size and in grayscale when relevant;
3. check the caption and every textual reference to the visual;
4. rebuild all affected document versions and inspect missing-file, font, bounding-box, float, and overfull warnings;
5. rerun the generating code when the underlying mathematics, parameters, or data changed.

A compelling visual is evidence only to the level justified by its source. It does not turn an experiment or schematic into a proof.
