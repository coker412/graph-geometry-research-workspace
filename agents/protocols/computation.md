# Reproducible experiments

Choose an experiment to answer a mathematical question relevant to route selection or an active proof obligation. Before a substantial search, identify the claim it tests, what a hit or no hit would establish, and the bounded resource limit in the existing note/plan. A small falsification check or symbolic check need not create a separate planning artifact. Explicitly authorized computational construction/search remains valid research.

After a batch, interpret the result before expanding parameters, precision or mesh size. Continue when it tests a new mechanism, resolves a relevant uncertainty or pursues an explicit computational target; repeated no-hits or numerical closeness alone do not justify expansion. For an unresolved general implication, derive the required quantifiers and error/transfer conditions in text. Do not substitute more samples for them, or ban experiments that could discriminate between credible routes.

A vague request for stricter or machine checking does not change the existing no-Lean workflow. First inspect the current proof for applicable exact arithmetic, symbolic identities or finite checks and explain their coverage; do not make clarification about formalization a prerequisite for these authorized checks. Ask only when a material unresolved scope or tool choice actually blocks the next step.

Use graphlab. Test actual claims on admissible minimal/symmetric examples: paths, cycles, stars, trees, small weighted graphs; for Riemannian problems, standard spaces, product/conformal/warped families satisfying completeness, regularity and other hypotheses. Record commands, versions, parameters, seeds, precision, errors and boundaries. Attack fragile lemmas with counterexamples; finding none is not proof.

Save code/output in project code/ or notes/ and register evidence. Numerical observations are experimental. After code changes run risk-appropriate syntax/unit checks and reproduce real inputs. Exact enumeration establishes only its covered range, not an infinite class.

For candidate-generation/evaluation searches, fix the evaluator, feasibility constraints, objective and resource limits first. Search code must not change the evaluator or lower thresholds. Check feasibility before scoring; retain best candidates and evaluator versions, then check unused parameters/precisions to avoid sample overfitting.

For discretized continuous geometry, distinguish geometric, discretization and floating-point errors. Mesh refinement/high-precision stability remain experimental. Rational reconstruction, symbolic conversion or interval estimates still require error control and a justification connecting finite computation to the original claim; assign levels through certification.
