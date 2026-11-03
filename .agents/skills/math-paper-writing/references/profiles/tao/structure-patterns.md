# Structural patterns: the selected Tao corpus

All twenty papers have individual [source records](sources.json), summarized in the [source index below](#source-index). Four recurring architectures are useful; overlap is expected.

## A. Reduction with explicit remaining obligations

**Papers:** T01, T05, T10, T11–T12.

Precise main result → conceptual model → stronger intermediate target → staged elimination/reformulation → technical construction → explicit return through earlier implications.

T01's headings move from stabilization to mixing to Fourier decay; its closing paragraph names the earlier propositions discharged. T05 moves from the embedding problem to oscillating maps and an iterative step before perturbation theory. T11–T12 name the potential, field or constraint eliminated at each stage. Their section names communicate mathematical work rather than merely numbering lemmas.

This pattern suits a long argument with genuine interfaces. It does not require extracting every calculation as a lemma. The target manuscript's notation and necessity gate still apply.

## B. A construction that exposes the limits of a method

**Papers:** T09, T11–T13; related obstruction discussion in T06.

Original problem → properties a proposed method uses → altered system retaining those properties → counterexample within the altered class → exact limitation on that method.

T09 keeps the averaged equation distinct from Navier–Stokes. T12 explains why forcing and a large target dimension remain. T13 distinguishes high-dimensional systems from the scalar model and the unresolved dimension. The expository gain is a precise inference about a method; it is not permission to overstate the mathematical result.

## C. Improve a bound by identifying the old bottleneck

**Papers:** T02, T07, T08, T14–T16, with aspects of T03.

Known regime/bounds → uncovered regime → mechanism blocking the earlier argument → new estimate, construction or case split → proof → remaining question.

T07 identifies the perimeter/area issue before its packing algorithm. T08 organizes different root locations by the tools they require. T14 contrasts the old construction with the improved logarithmic bound and discloses that its exponent is not optimized. T16 motivates the inverse theorem with equality configurations before an error-suppressed outline.

## D. Translate between mathematical languages

**Research papers:** T04, T05, T17, T19. **Survey variants:** T18, T20.

Original question → target language and explicit correspondence → imported mechanism with hypotheses → return to the original conclusion.

T17 explains the continuous/arithmetic factors of the adelic model and a sampling comparison. T19 turns graphs into events and partitions into sigma-algebras, then recovers the graph statement. T04 uses an adapted-form criterion to make dynamical universality concrete.

T18 and T20 require separate treatment: surveys can reorder established arguments for a new audience and declare omitted details. A research paper cannot borrow those omissions while retaining a claim to prove its main result.

Most papers end after completing an argument or stating a mathematically focused question. Distinctive closing asides and jokes are not part of the reusable architecture.

## Source index

Dates are first arXiv submissions; page anchors refer to the recorded inspected version. All twenty works are sole-authored by Terence Tao. T18 and T20 are surveys; the other eighteen are research papers/notes. Related papers are distinct works but not independent evidence of author-wide habits. There was no reserved unseen test paper.

| ID | Work and inspected version | Date / genre | Architecture and inspected PDF pages |
| --- | --- | --- | --- |
| T01 | [Almost all orbits of the Collatz map attain almost bounded values](https://arxiv.org/abs/1909.03562v7); 58 pp. | 2019-09-08; research paper | Precise partial result → Syracuse model → labeled probability heuristic → first-passage stabilization → mixing → Fourier decay → closure. Inspected pp. 1, 3, 5, 6, 8, 9, 13, 16, 20, 28, 33, 36, 41, 44, 56. Heuristic is followed by a precise distribution statement; closing paragraph discharges the chain of reductions. |
| T02 | [Quantitative bounds for critically bounded solutions to the Navier-Stokes equations](https://arxiv.org/abs/1908.04958v2); 45 pp. | 2019-08-14; research paper | Critical equation → quantitative substitute → spacetime overview → basic estimates → Carleman inequalities → main estimate → applications. Inspected pp. 1, 4, 5, 6, 8, 27, 36, 41, 44. The diagram explains where separate estimates operate; triple-exponential cost is part of the contribution. |
| T03 | [An integration approach to the Toeplitz square peg problem](https://arxiv.org/abs/1611.07441v2); 53 pp. | 2016-11-22; research paper | Known regular cases → small-square obstruction → integration method → proved case → periodic/combinatorial variants → special cases and unresolved step. Inspected pp. 1, 5, 6, 11, 14, 33, 37, 42, 51. A proposed route to the general conjecture stays separate from the proved positive result. |
| T04 | [On the universality of potential well dynamics](https://arxiv.org/abs/1707.02389v3); 20 pp. | 2017-07-08; research paper | Potential-well model → embedding question → geometric criterion → examples and obstruction → proof → Turing-machine encoding. Inspected pp. 1, 8, 11, 15, 18, 20. A geometric criterion makes cross-field universality a testable mathematical interface; the counterexample is attributed to Bryant. |
| T05 | [Embedding the Heisenberg group into a bounded dimensional Euclidean space with optimal distortion](https://arxiv.org/abs/1811.09223v2); 46 pp. | 2018-11-22; research paper | Known distortion/dimension tradeoff → simultaneous improvement → informal oscillatory construction → orthogonality obstacle → iterative reductions → perturbation → closure. Inspected pp. 1, 3, 4, 5, 8, 11, 16, 23, 26, 41, 45. Imports Nash–Moser-type ideas by naming derivative loss; does not claim the borrowed theorem applies verbatim. |
| T06 | [On the universality of the incompressible Euler equation on compact manifolds, II. Non-rigidity of Euler flows](https://arxiv.org/abs/1902.06313v2); 21 pp. | 2019-02-17; research paper | Euler setting → extension notion → non-rigidity/generic obstruction → coordinate formulation → separate proofs. Inspected pp. 1, 7, 9, 12, 14, 15, 20. Degree-of-freedom heuristic is bounded by dimension; explicitly admits the argument fails in dimension two. |
| T07 | [Perfectly packing a square by squares of nearly harmonic sidelength](https://arxiv.org/abs/2202.03594v2); 11 pp. | 2022-02-08; research paper | Problem → improved range → perimeter obstruction → near-lattice remedy → recursive reduction → local packing construction. Inspected pp. 1, 2, 3, 6, 7, 10, 11. A short paper can still identify the exact invariant blocking the old algorithm. |
| T08 | [Sendov's conjecture for sufficiently high degree polynomials](https://arxiv.org/abs/2012.04125v2); 38 pp. | 2020-12-08; research paper | Conjecture → large-degree theorem → locations of the distinguished root → asymptotic conventions → regime-specific contradictions → equality discussion. Inspected pp. 1, 10, 12, 15, 17, 19, 25, 28, 37. Distinct root regimes receive distinct tools; notation explains the meaning of small parameters before use. |
| T09 | [Finite time blowup for an averaged three-dimensional Navier-Stokes equation](https://arxiv.org/abs/1402.0290v3); 77 pp. | 2014-02-03; research paper | Original problem and retained identities → modified equation theorem → informal cascade model → averaging → ODE reduction → circuit components → blowup closure. Inspected pp. 1, 5, 10, 11, 15, 16, 18, 29, 35, 48, 75. Modified-equation blowup is used to delimit a method, not advertised as solving the original Navier–Stokes problem. |
| T10 | [The Erdos discrepancy problem](https://arxiv.org/abs/1509.05363v6); 27 pp. | 2015-09-17; research paper | Result and provenance → three ingredients → Fourier reduction → multiplicative-function input → residual model → generalization. Inspected pp. 1, 7, 8, 10, 11, 12, 18, 23, 26. Credits shared/previous ingredients and singles out the new assembly; a remark tests why a tempting example does not contradict the reduction. |
| T11 | [Finite time blowup for a supercritical defocusing nonlinear wave system](https://arxiv.org/abs/1602.08059v3); 32 pp. | 2016-02-25; research paper | System and parameter range → self-similar target → eliminate potential → eliminate field → dimension reduction → constructive closure. Inspected pp. 1, 5, 6, 9, 12, 15, 22, 23, 24, 25, 31. Section names identify the unknown eliminated at each stage and the last paragraph returns to the main theorem. |
| T12 | [Finite time blowup for a supercritical defocusing nonlinear Schr\"odinger system](https://arxiv.org/abs/1612.00526v1); 55 pp. | 2016-12-02; research paper | System and forcing → limitation statement → self-similar target → eliminate variables/constraints → construction → embedding appendix. Inspected pp. 1, 5, 8, 9, 10, 15, 20, 26, 33, 35, 43, 54. Explains why forcing and a large target dimension remain; their removal is not an established consequence. |
| T13 | [Finite time blowup for high dimensional nonlinear wave systems with bounded smooth nonlinearity](https://arxiv.org/abs/1603.01908v3); 27 pp. | 2016-03-07; research paper | Known low-dimensional regularity → high-dimensional counterexample → explicitly non-rigorous scaling picture → wave profiles → construction → low-dimensional appendix. Inspected pp. 1, 3, 4, 6, 12, 13, 21, 26. Keeps scalar, system and unresolved dimension ten apart; heuristic numerology is explicitly not a proof. |
| T14 | [Commutators close to the identity](https://arxiv.org/abs/1805.11131v3); 15 pp. | 2018-05-28; research paper | Quantitative obstruction → old construction → improved bound → operator system → abstract solving lemma → open questions. Inspected pp. 1, 3, 6, 11, 13. Short note includes a comparison construction; nonoptimized exponent is disclosed rather than presented as sharp. |
| T15 | [Some remarks on the lonely runner conjecture](https://arxiv.org/abs/1701.02048v4); 31 pp. | 2017-01-09; research paper | Runner picture → Bohr-set formulation → multiple partial results → preliminaries → separate theorem proofs → short-progression case. Inspected pp. 1, 2, 8, 12, 21, 27, 30. A concrete problem is translated into a reusable language before the proof; scope remains partial. |
| T16 | [An inverse theorem for an inequality of Kneser](https://arxiv.org/abs/1711.04337v4); 30 pp. | 2017-11-12; research paper | Strengthened inequality → extremal examples → stable inverse theorem → error-suppressed sketch → formal argument → further questions. Inspected pp. 1, 2, 4, 5, 7, 8, 28, 29. Explicitly suppresses epsilon/delta only in the outline, not in the theorem; examples explain the target structure. |
| T17 | [The Ionescu--Wainger multiplier theorem and the adeles](https://arxiv.org/abs/2008.05066v2); 39 pp. | 2020-08-12; research paper | Unified group language → lattice/adelic dictionary → sampling bridge → superorthogonality → sunflower bound → theorem → major-arc construction → background appendix. Inspected pp. 1, 2, 9, 11, 13, 21, 24, 35, 36, 38. Explains what continuous and arithmetic features each factor models and proves a comparison returning to lattice norms. |
| T18 | [Perelman's proof of the Poincar\'e conjecture: a nonlinear PDE perspective](https://arxiv.org/abs/math/0610903v1); 42 pp. | 2006-10-29; survey | Perelman theorem → declared audience and omissions → nonlinear-PDE overview → scaling/local existence → monotonicity → blowup → surgery/extinction. Inspected pp. 1, 2, 4, 6, 8, 10, 12, 15, 19, 22, 24, 41. Survey deliberately rearranges chronology and declares simplifications; do not apply its omissions to research proofs. |
| T19 | [Szemer\'edi's regularity lemma revisited](https://arxiv.org/abs/math/0504472v2); 21 pp. | 2005-04-22; research paper | Graph statement → probability/information reformulation → recover graph consequence → prove stronger formulation → entropy variant. Inspected pp. 1, 9, 10, 12, 15, 20. Translation is operational: a graph becomes an event and partitions become sigma-algebras, followed by a return application. |
| T20 | [The dichotomy between structure and randomness, arithmetic progressions, and the primes](https://arxiv.org/abs/math/0512114v2); 27 pp. | 2005-12-06; survey | Structure/randomness thesis → ergodic formulation → Fourier formulation → graph regularity → primes application. Inspected pp. 1, 5, 9, 13, 16, 21, 25. One organizing distinction is instantiated across fields; this is a survey, not a template for every theorem paper. |
