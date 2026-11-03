# Applying the optional profiles

**Historical pilot record.** These examples and reserved-paper comparisons were produced from the initial three-training-paper profiles. The current profiles have twenty training works each. The old comparison papers remain excluded from those twenty, but are already known and are not fresh blind tests of the expansion. The examples below remain useful local demonstrations; their original verification scope is unchanged.

These are **targeted editorial demonstrations**, not quotations, author imitations or new research results. Each pair uses the same fixed mathematical content. The baseline passages were constructed for this exercise; they are not neutral samples of ordinary user writing. The same agent selected the rules, wrote the revisions and checked them. This demonstrates an application, not a blinded comparison, independent mathematical verification or a measured advantage over the core skill.

Use one applicable decision from the [field profiles](field-profiles.md), read its cited passages, and compare the result against the target manuscript's assumptions and conclusions. The choices below concern exposition; this exercise did not isolate the effect of anti-defensive-writing.

## Evans: give each estimate its job

Source decision: [Evans profile](profile-evans.md), E1 pp. 1–4 and E2 pp. 1–4. The transferable choice is to identify what an estimate enables; an adjoint equation is not required.

**Fixed content.** Let Ω be a bounded Lipschitz domain, let g: ℝ → ℝ be globally Lipschitz, and suppose u_j ∈ H¹₀(Ω) satisfy −Δu_j + g(u_j) = f weakly for the same f ∈ H⁻¹(Ω). Assume sup_j ‖u_j‖_{H¹₀} ≤ C. Extract a subsequence converging weakly in H¹₀ and strongly in L²; pass to the weak equation. No uniqueness or convergence of the full sequence is asserted.

**Before**

> Let Ω be a bounded Lipschitz domain and g: ℝ → ℝ globally Lipschitz. Suppose u_j ∈ H¹₀(Ω) solve −Δu_j + g(u_j) = f weakly for a fixed f ∈ H⁻¹(Ω), and sup_j ‖u_j‖_{H¹₀} ≤ C. A subsequence converges weakly in H¹₀ and strongly in L² to u. The functions g(u_j) converge strongly in L² to g(u). Passing to the limit in the weak formulation shows that u solves the same equation.

**After**

> Let Ω be a bounded Lipschitz domain and g: ℝ → ℝ globally Lipschitz. Suppose u_j ∈ H¹₀(Ω) solve −Δu_j + g(u_j) = f weakly for a fixed f ∈ H⁻¹(Ω). The bound sup_j ‖u_j‖_{H¹₀} ≤ C supplies the two convergences needed to pass to the limit: along a subsequence, u_j ⇀ u in H¹₀ controls the Laplacian term, while u_j → u in L² gives g(u_j) → g(u) in L² by the Lipschitz condition. The weak formulation therefore passes to u, which solves the same equation.

**变化：** 把两种收敛分别与线性项、非线性项对应起来。没有增添估计、唯一性或全序列收敛。若正文此前已解释这个对应关系，就保留更短的原段。

## Stanley: keep the counted object visible in the formula

Source decision: [Stanley profile](profile-stanley.md), S1 pp. 1–4 and S2 pp. 4–7. A generating function should retain its connection to the statistic being counted.

**Fixed content.** For n ≥ 0, let [n] = {1, …, n}, with [0] empty. Define F_n(q) = ∑_{A ⊆ [n]} q^{|A|}. Each element contributes 1 or q according to exclusion or inclusion; hence F_n(q) = (1 + q)ⁿ. For 0 ≤ k ≤ n, its qᵏ coefficient is the number of k-element subsets, namely binomial(n, k). Empty sum-of-elements conventions give F_0(q) = 1.

**Before**

> For n ≥ 0, write [n] = {1, …, n}, with [0] empty, and define F_n(q) = ∑_{A ⊆ [n]} q^{|A|}. We have F_n(q) = (1 + q)ⁿ and, for 0 ≤ k ≤ n, [qᵏ]F_n(q) = binomial(n, k), the number of k-element subsets. Indeed, each element contributes 1 if excluded and q if included. When n = 0 the only subset is empty, so F_0(q) = 1.

**After**

> For n ≥ 0, write [n] = {1, …, n}, with [0] empty. To record a subset A, assign weight q to each included element and weight 1 to each excluded element. Its weight is q^{|A|}, and the independent choices give F_n(q) := ∑_{A ⊆ [n]} q^{|A|} = (1 + q)ⁿ. Thus [qᵏ]F_n(q) counts the k-element subsets and equals binomial(n, k) for 0 ≤ k ≤ n. For n = 0, the unique empty subset has weight 1, giving F_0(q) = 1.

**变化：** 先解释乘积的每个因子代表什么，再读取系数。两段都有同样的组合解释；改动是顺序和连接，不是偷偷补进一个新证明。对熟悉这一编码的读者，原段也合适。

## Mumford: identify the distinction the example settles

Source decision: [Mumford profile](profile-mumford.md), M2 pp. 18–19. The example should separate the precise properties at issue. This elementary algebra example is newly constructed for the exercise; it is not taken from Mumford.

**Fixed content.** For a field k, set B = k[t, x]/(x² − t). As a k[t]-module, B is free with basis 1, x, so Spec B → Spec k[t] is finite flat of degree two. Its fiber at t = 0 has coordinate ring k[x]/(x²), which is nonreduced. Consequently a finite flat morphism may have a nonreduced fiber. No restriction on the characteristic is needed for these statements.

**Before**

> Let k be a field and B = k[t, x]/(x² − t). The elements 1, x form a k[t]-basis of B. Therefore Spec B → Spec k[t] is finite flat of degree two. The fiber at t = 0 has coordinate ring k[x]/(x²), which is nonreduced. This shows that a finite flat morphism may have a nonreduced fiber.

**After**

> A finite flat morphism may have a nonreduced fiber. For a field k, consider B = k[t, x]/(x² − t). The relation x² = t makes B free over k[t] with basis 1, x, so Spec B → Spec k[t] is finite flat of degree two. At t = 0, however, the fiber ring is k[x]/(x²): the class of x is nonzero and has square zero. Thus flatness here coexists with a nonreduced fiber.

**变化：** 先交代例子要区分的性质，再逐项验明。展开“非约化”的已有含义，没有宣称所有非零纤维分裂、光滑或相同。不要把这一局部选择推广成“代数几何文章都要先讲病态”。

## Milnor: expose the bridge from geometry to counting

Source decision: [Milnor profile](profile-milnor.md), G1 pp. 2–3. Here a packing argument turns geometric separation into a numerical bound.

**Fixed content.** In a metric space with a Borel measure μ, let x₁, …, x_N ∈ B(o, R), with d(x_i, x_j) ≥ δ > 0 for i ≠ j. Suppose μ(B(x_i, δ/2)) ≥ v > 0 for every i and μ(B(o, R + δ/2)) ≤ V < ∞. Balls are open. Their disjointness, containment and measure bounds give Nv ≤ V, hence N ≤ V/v.

**Before**

> Let x₁, …, x_N ∈ B(o, R) in a metric space with a Borel measure μ, and suppose d(x_i, x_j) ≥ δ > 0 for i ≠ j. Assume μ(B(x_i, δ/2)) ≥ v > 0 for every i and μ(B(o, R + δ/2)) ≤ V < ∞. All balls are open. They satisfy ∑_i μ(B(x_i, δ/2)) ≤ μ(B(o, R + δ/2)), since the small balls are pairwise disjoint and contained in the larger ball. Thus Nv ≤ V and N ≤ V/v.

**After**

> Let x₁, …, x_N ∈ B(o, R) in a metric space with a Borel measure μ, with d(x_i, x_j) ≥ δ > 0 for i ≠ j. Suppose each open ball B(x_i, δ/2) has measure at least v > 0, while μ(B(o, R + δ/2)) ≤ V < ∞. Separation gives N disjoint open balls, and the triangle inequality places all of them inside B(o, R + δ/2). Comparing their total measure with that of the containing ball yields Nv ≤ ∑_i μ(B(x_i, δ/2)) ≤ V. Hence N ≤ V/v.

**变化：** 先把“点之间的距离”变成“不相交的球”，再做体积比较。保留开球、正半径、逐球下界及有限总体积；没有加入曲率假设或声称此界必可达到。

## Held-out checks

One paper per author was reserved before the three training papers were distilled. The four profile files were hashed before inspecting these held-out bodies; their rules were not subsequently rewritten to fit these papers. This is a **within-run held-out check by the same agent**, not independent review, a claim that the model had never encountered the texts, or a test of author recognition. Selected passages were closely read; no whole-paper proof audit was performed.

| Profile and held-out source | Inspected evidence | What it supports or limits |
| --- | --- | --- |
| Evans: Evans, Kneuss and Tran, [Partial regularity for minimizers of singular energy functionals, with application to liquid crystal models](https://arxiv.org/pdf/1312.4471v1), v1, 16 December 2013 | PDF pp. 1–3: existence baseline, excess and the announced role of its decay; pp. 26–29: regularity conclusion and liquid-crystal model dictionary | Supports identifying an estimate's job and returning to an application. Does not require an adjoint equation or an immediate elementary payoff. Joint authorship limits personal attribution |
| Stanley: [Longest Alternating Subsequences of Permutations](https://math.mit.edu/~rstan/papers/altseq.pdf), author-hosted 18-page version | PDF pp. 1–3: increasing-subsequence comparison, alternating convention, counting arrays and generating functions; pp. 15–16: three generalizations | Supports keeping object, encoding and interpretation connected. Opening with prior theory counters an obligatory example-first rule. Genuine open questions can form the ending; that is not a universal requirement |
| Mumford: [Pathologies III](https://www.dam.brown.edu/people/mumford/alg_geom/papers/1967d--Path3-JS.pdf), 11-page scan, printed pp. 94–104 | All pages visually inspected; pp. 94–95: classical formulation, cohomological reformulation and scope; pp. 97–99: second proof explains the role of characteristic zero; pp. 100–103: obstruction, lemma and counterexample | Supports reformulation with a stated purpose and tracing an assumption to its use. Crucially the counterexample is a normal surface, not asserted nonsingular; do not erase that distinction as defensive prose. A second proof earns its place by explaining the failure mechanism |
| Milnor: [Eigenvalues of the Laplace operator on certain manifolds](https://pmc.ncbi.nlm.nih.gov/articles/PMC300113/), 1964, p. 542 | Entire one-page article, including final differential-form calculation: flat torus → dual lattice → eigenvalue counts → Witt's pair of lattices → nonisometric tori with the same spectrum | Supports making the bridge explicit and checking a nearby possible distinction. No preliminary worked example or separate conclusion section is needed. The lattice construction is cited, not claimed as Milnor's new theorem |

The held-out papers support some decisions and leave others untested. In particular, they do not validate every local rule, sentence pattern or visual choice in the profiles. Historical open questions in these papers are not asserted to remain open today.

## What these checks establish

Manual comparison of the four revision pairs retained the fixed hypotheses, objects, quantifiers and conclusions. The PDE pair keeps subsequence convergence; the counting pair includes n = 0; the algebra pair makes no unsupported fiber claim; the packing pair keeps the open-ball convention and measure bounds. These are same-agent content checks. There was no independent evaluator or author preference vote.

The core skill already asks for proof interfaces, meaningful examples and precise scope. These profiles supply concrete applications of those principles. They do not justify another mandatory layer of instructions. A future user comparison should use a genuine passage, keep the core instructions fixed, vary only the selected profile decision, and ask which version helps the intended reader.
