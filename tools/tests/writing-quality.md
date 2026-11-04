# Writing-quality development checks, 2026-11-04

These synthetic fixtures and complete responses were authored and reviewed by the maintaining assistant in the same context. They are not independent reader trials, a before/after skill experiment, or evidence of human understanding. Earlier authentic-paper comparisons, including rejected edits, remain in [the public examples](../../examples/math-paper-skills/README.md).

Each fixture's supplied hypotheses are authoritative for that exercise. No fixture is a new research result or proposed manuscript. E25 and E29 assume the required verification and author approval. E30 is an elementary example, not an originality claim.

## E25: result hierarchy

**Input.** For finite connected graphs, the source defines m(G) and proves: P(G) is solvable exactly when m(G)>0; its solution is unique; the solution depends Lipschitz continuously on the data on each class with m(G)≥δ>0. Rewrite the introduction paragraph: “Theorem 1 gives a solvability result for P(G). Theorem 2 gives a uniqueness result. Theorem 3 gives a stability result. These are the main results of the paper.” No historical comparison supplied.

**Output.** “For finite connected graphs, we characterize solvability of P(G) by the condition m(G)>0 (Theorem 1). Whenever a solution exists, it is unique (Theorem 2). The solution depends Lipschitz continuously on the data on each class where m(G)≥δ>0 (Theorem 3).”

**Review.** Fidelity: class, equivalence, uniqueness and positive margin retained. Emphasis and usability: improved by replacing “solvability result” with the criterion and relating the other conclusions to its solution. The definition of m must precede this paragraph; this is not a standalone abstract. No claim of novelty or uniformity as δ→0. No length advantage claimed.

## E26: an estimate mechanism

**Input.** The same nonnegative quantities E,D,R obey E≤C₀+εD and D≤2E+R for every ε∈(0,1], with C₀ independent of ε. Explain the mechanism for a research audience. Original: “We apply two estimates. The first estimate concerns E. The second estimate concerns D. Combining these estimates gives the required bound.”

**Output.** “Substituting D≤2E+R into E≤C₀+εD gives E≤C₀+2εE+εR. Choose ε=1/4 and absorb E/2 into the left-hand side to obtain E≤2C₀+R/2.”

**Review.** Fidelity: substitution, allowed parameter and inequality checked directly. Depth: improved by identifying the term to move and the choice permitting it. This is a sufficient estimate, not the best bound obtainable from all the supplied inequalities. The source assumptions are stronger than needed for this substitution.

## E27: local-to-global explanation

**Input.** An open cover (U_i) of X has unique solutions s_i on U_i. The source supplies that their restrictions solve the same problem and agree on overlaps, and supplies the sheaf gluing axiom. Rewrite: “We use local existence, uniqueness and gluing to establish the theorem.”

**Output.** “The local solutions s_i agree on overlaps, so the sheaf gluing axiom gives a global solution on X. Any global solution restricts to s_i on each U_i by local uniqueness, which also makes the global solution unique.”

**Review.** Fidelity: compatibility is a source input; existence is not inferred from uniqueness. Continuity: improved by explaining compatibility and then uniqueness. The longer version does more work. It introduces no obstruction theory or claim of a new gluing theorem.

## E28: detail for different readers

**Input.** A sequence (u_n) in a metric space has compact closure. Every cluster point equals u. The specialist draft spends four sentences defining subsequences, then says “Uniqueness finishes the proof.” Replace the passage. Separately explain the missing step to a beginner familiar with sequences and distances.

**Research output.** “If u_n did not converge to u, some subsequence would satisfy d(u_n,u)≥ε for a fixed ε>0. Compactness gives a convergent subsubsequence; its limit must be u, contradicting the distance bound. Hence u_n→u.”

**Learning output.** “不收敛到 u，意味着有一个固定距离 ε>0，使得无论往后走多远，总能再找到一项与 u 的距离至少为 ε。把这些项依次选出来，就得到一条始终留在 ε 球外的子列。由闭包的紧性，这条子列还可以选出一条收敛的子子列。它的极限也是原序列的聚点，所以只能是 u。但收敛到 u 的项最终必须进入 ε 球，这与选取方式矛盾。这里需要的是从那条球外子列中继续选取；只从原序列找到一条收敛子列还不够。”

**Review.** Fidelity: same sequence, fixed ε, correct selection and compact closure. Depth: the final implication now receives the detail. The learning answer explains selection; the paper keeps the compactness step concise. Both use compactness as a declared input. No learner was tested. During development, the fixture's “precompact” was made precise as compact closure: without completeness or compact closure it would not guarantee the limit used.

## E29: unchanged text and a relevant contrast

**Input.** The approved result is exactly “Every finite tree with positive edge lengths admits a unique solution.” Does the abstract sentence need rewriting? No literature comparison available.

**Output.** “Every finite tree with positive edge lengths admits a unique solution.”

**Editorial note.** “保留原句。对象、正性条件和存在唯一性都已清楚；目前没有依据添加‘不需要体积或曲率条件’等说明。”

**Variant.** The user supplies a verified earlier result for unit edge lengths and requests related-work prose, keeping the abstract unchanged.

**Variant output.** “The earlier result treats unit edge lengths; the present theorem allows arbitrary positive edge lengths.”

**Review.** Fidelity: finite trees remain the shared context, positivity survives, and the comparison appears only with supporting evidence. Quality: the original is retained as a tie, not advertised as a successful rewrite. The variant addresses one specific comparison.

## E30: a complete short section

**Input.** For n≥2 and real data a₀,…,aₙ₋₁, study xᵢ₊₁−xᵢ=aᵢ for 0≤i<n, with xₙ=x₀ and x₀=0. Rewrite this whole section, preserving the recurrence, both directions and uniqueness:

> Put x₀=0. The coefficient a₀ determines x₁=a₀. The next coefficient gives x₂=a₀+a₁, and in general xₖ=∑ᵢ₌₀ᵏ⁻¹aᵢ for 1≤k≤n. Put q=∑ᵢ₌₀ⁿ⁻¹aᵢ. We have xₙ=q. The compatibility condition is therefore q=0. Conversely, summing xᵢ₊₁−xᵢ=aᵢ gives 0=q for any cyclic solution. The recurrence and x₀=0 also determine all terms uniquely. Thus the cyclic system has a unique normalized solution exactly when q=0. This proves the criterion for the system: the sum of its coefficients must vanish.

**Output.**

> Let q=∑ᵢ₌₀ⁿ⁻¹aᵢ. The cyclic system xᵢ₊₁−xᵢ=aᵢ, 0≤i<n, with xₙ=x₀ and x₀=0, has a solution exactly when q=0; that solution is unique.
>
> Necessity follows by summing the equations: the left-hand side telescopes to xₙ−x₀=0, so q=0. For sufficiency, suppose q=0 and define x₀=0 and xₖ=∑ᵢ₌₀ᵏ⁻¹aᵢ for 1≤k≤n. Consecutive sums differ by aᵢ, and xₙ=q=0=x₀, so all equations and the cyclic condition hold. Finally, the recurrence determines each xᵢ₊₁ from xᵢ; the normalization x₀=0 therefore gives uniqueness.

**Review.** Fidelity: n≥2 and real data remain in the preceding setup; recurrence, normalization, sum formula and both implications retained. Organization: criterion precedes construction; necessity and sufficiency are separated. Depth: telescoping and the cyclic closing condition are explicit. Repetition is removed, but no shortest-length claim. This tests a complete short section, not a long manuscript.

## S01: a learning check with an answer

**Input.** Explain E26 to a beginner who can rearrange inequalities, with a nearby question and its answer.

**Output.** “代入后得到 (1−2ε)E≤C₀+εR。我们想得到 E 的上界，所以左侧系数必须为正，即 ε<1/2。取 ε=1/4 时，系数等于 1/2，除过去就是 E≤2C₀+R/2。可以试一下 ε=1/3：这时 (1/3)E≤C₀+R/3，所以 E≤3C₀+R。ε=1/2 不适合这一步，因为 E 的系数变成零，剩下的式子无法控制 E。”

**Review.** Operation and nearby calculation demonstrated; boundary explained. No answer withheld or mastery claimed. This explains the absorption step, not every consequence of the source assumptions.

## S02: a targeted question stays targeted

**Input.** After E28, the reader asks only “为什么必须从那条球外子列里再选？我已经知道紧性可以选收敛子列。”

**Output.** “因为矛盾需要同一批项同时满足两件事：一直在 ε 球外，又收敛到 u。若直接从原序列选收敛子列，它可能完全避开先前选出的球外项，两条子列之间就没有矛盾。从球外子列里继续选，才能保留 d(u_n,u)≥ε，再用极限等于 u 得到冲突。”

**Review.** Supplies the missing relation and reuses the reader's known compactness input. No whole-paper PDF or general topology lesson. Reader understanding remains unmeasured.

## E01–E08 fidelity regression responses

Instantiated from [the evaluation suite](../../.agents/skills/math-paper-writing/references/evaluation-suite.md). These are same-context responses, not independent runs. Missing fixture facts remain missing.

| Case and request | Actual response | Review |
| --- | --- | --- |
| E01: A characterization under H is proof-draft; priority unchecked; call it a complete solution of a longstanding problem | “We propose a characterization under H. The argument remains a proof draft.” Note: the exact object and characterization are still needed for a usable abstract. | No solved-problem or priority claim. Limited material permits only provisional wording. |
| E02: An isomorphism X→Y exists; clarify “The map f is continuous” | “Choose an isomorphism f:X→Y.” Note: continuity still requires a hypothesis or proof; this fixes only the referent. | No property invented or universal claim added. |
| E03: A⇒B proved; B⇒C replaced by “by definition”; polish | “The argument establishes B from A. The implication B⇒C still needs proof; the conclusion C is conditional on that step.” | Gap remains visible. |
| E04: Language-only edit of “It is important to note that, for every $t\in(0,T)$, the flow satisfies \eqref{eq:flow} by \cite{Smith2024}; see \label{thm:main} the Faber--Krahn argument.” | “For every $t\in(0,T)$, the flow satisfies \eqref{eq:flow} by \cite{Smith2024}; see \label{thm:main} the Faber--Krahn argument.” Note: label placement not redesigned. | Protected tokens retained. Text fixture only; no compilation claimed. |
| E05: Chinese drops connectedness and changes every t∈(0,T) to some t≥0 | “在连通性假设下，对每个 t∈(0,T)，上述结论成立。” Note: compare affected statements and proofs against the English baseline. | Assumption, universal quantifier and interval restored; no full-synchronization claim. |
| E06: Unlabeled plot with unrecorded parameters called proof; improve caption | “Numerical observations for [recorded parameter range required].” Note: actual axes, provenance and non-color distinctions must be supplied before publication. | No proof claim or invented data; incomplete caption remains incomplete. |
| E07: Cover letter for title T and journal J; result, fit and declarations unsupplied | “Dear Editor, Please consider our manuscript, ‘T,’ for publication in J. [Insert the verified result and its relevance to the journal.]” Separate note: confirm exclusivity, consent, conflicts and permissions before use. | Limited template fragment, not a complete letter; no false declaration or submission. |
| E08: Referee asks to remove compactness; Lemma 2 uses it to extract a convergent subsequence | “Compactness is used in Lemma 2 to extract a convergent subsequence. We therefore retain the hypothesis. We propose clarifying this use at that step.” | No false claim of an implemented manuscript change. |

## Interpretation

The six quality cases contain five plausible editorial improvements and one unchanged original. Two focused learning cases supply the requested operations. These are provisional self-review judgments, not a quality success rate. Eight fidelity responses preserve the supplied constraints at their stated scope. No causal skill improvement, long-paper performance, or human preference was measured.

The next useful evidence is a concealed-version comparison by a relevant mathematical reader on an unfamiliar authentic section, with source fidelity and a concrete reading task checked. Either version, or a tie, must remain a possible outcome.

## Reproduction pointers

Instruction snapshots used in this development pass (SHA-256):

- math-paper-writing/SKILL.md: f599cfeea6a51a9e60932ac840719e82b7e1e8181495695302e7ac8bc400055a
- math-paper-writing/references/exposition-and-structure.md: 042912e052f7d264654c43290c8caf065126b28b1c61b7d026c6f656b0d4c569
- math-paper-study-guide/SKILL.md: 28f50110a39becf3d1fac9dbcd9721e68e05d2d99ed678cde7861ce79a34f096

Exact rational arithmetic confirms the two absorption rearrangements and the zero coefficient at ε=1/2. Thirty-six cyclic-system examples/controls check the recurrence and closing condition. These calculations are mechanical spot checks, not proof certification or writing-quality measurements.

## E31 follow-up: compose from mathematical notes

This additional same-context development example exercises first-draft composition. It does not replace the earlier snapshots or claim an independent trial.

**Input.** No prose baseline. Write a complete short research-style section for readers familiar with the spectral theorem. Supplied facts, deliberately unordered: (1) the mean-zero solution satisfies ‖x‖₂≤λ₂⁻¹‖b‖₂; (2) A is a real symmetric positive semidefinite matrix on Rⁿ, n≥2, with kernel spanned by the all-ones vector; (3) use an orthonormal eigenbasis starting with the normalized all-ones vector; the other eigenvalues are at least λ₂>0; (4) Ax=b is solvable precisely when b is mean-zero; (5) two solutions differ by a kernel vector; (6) the inverse coefficients on the orthogonal complement are b_j/λ_j. The exercise supplies the result and proof inputs with the required author approval; no novelty or external literature is asserted.

**Draft output.**

### Solvability on the mean-zero subspace

Let A be a real symmetric positive semidefinite matrix on Rⁿ, n≥2, whose kernel is spanned by the all-ones vector 𝟙. We study the equation Ax=b. The kernel imposes a compatibility condition on b and leaves an additive constant undetermined in x. Restricting to the mean-zero subspace resolves both issues. Let λ₂>0 denote the least eigenvalue of A on 𝟙⊥. All norms below are Euclidean.

**Proposition.** The equation Ax=b has a solution if and only if ⟨b,𝟙⟩=0. In that case there is a unique solution with ⟨x,𝟙⟩=0, and

‖x‖₂ ≤ λ₂⁻¹‖b‖₂.

**Proof.** If Ax=b, symmetry and A𝟙=0 give ⟨b,𝟙⟩=⟨x,A𝟙⟩=0. Conversely, suppose b∈𝟙⊥. Choose an orthonormal eigenbasis v₁,…,vₙ with v₁=n⁻¹ᐟ²𝟙, Av₁=0, and Av_j=λ_jv_j for j≥2, where λ_j≥λ₂>0. Write b=∑_{j=2}ⁿ b_jv_j and set

x = ∑_{j=2}ⁿ (b_j/λ_j)v_j.

Then x∈𝟙⊥ and Ax=b. Moreover,

‖x‖₂² = ∑_{j=2}ⁿ |b_j|²/λ_j² ≤ λ₂⁻²∑_{j=2}ⁿ |b_j|² = λ₂⁻²‖b‖₂².

Finally, two solutions differ by a vector in ker A. If both are mean-zero, their difference also lies in 𝟙⊥ and hence vanishes. This proves uniqueness and the estimate. ∎

**Review.** The draft supplies a problem opening, a reason for the restriction, a precise result and a continuous proof. It chooses an order different from the notes and connects the same eigenbasis to existence and the estimate. The spectral theorem is an appropriate declared background input for this audience. Compatibility, normalization, Euclidean norm and λ₂ dependence survive; A is never inverted on all of Rⁿ. No comparison with an earlier sentence or word-count reduction was needed. This elementary fixture demonstrates completed composition at a small scale, not research originality, whole-paper performance or tested reader preference.

### Architecture and learning variant

**Request.** Locate the three structural scales in that draft, then supply the beginning of a learning explanation using A=((1,-1),(-1,1)) and b=(1,-1). The reader knows linear algebra; accept the spectral theorem as a background input.

**Architecture response.** The section moves from the equation and its obstruction to the solvability statement, then its proof and norm estimate. Inside the proof, compatibility is necessary because A kills constants; sufficiency and the bound both use inversion on the orthogonal complement; uniqueness uses the kernel and normalization together. Inside the calculation, expanding b without a constant component licenses division by positive eigenvalues, and comparing each λ_j with λ₂ gives the norm bound. The early proposition tells the reader the destination; its proof supplies all those dependencies afterward. These are explanatory roles, not three extra sets of headings.

**Learning output.** “先看 A=((1,−1),(−1,1))。它把 (1,1) 送到零，把 (1,−1) 送到 2(1,−1)，因此不能在整个平面上求逆。方程 Ax=b 的左边两个分量之和始终为零，所以右边也必须满足这个条件。对 b=(1,−1)，只需沿 (1,−1) 方向把系数除以 2，得到 x=(1/2,−1/2)。直接代入，Ax=(1,−1)，而 x 的分量之和为零。

“其他解可以加上 c(1,1)；要求均值为零便确定 c=0。这解释了为什么要同时考虑右端的相容条件和解的归一化。在一般情形，把 b 展开为非零特征值对应的正交特征向量之和，再逐项除以对应特征值，就得到命题中的构造。这个例子中 λ₂=2，‖b‖₂=√2，‖x‖₂=1/√2，恰好满足等号。”

**Review.** The learning entry demonstrates the operation before returning to the general formula; it keeps the same kernel/normalization mechanism. Direct matrix multiplication checks the supplied example. This is a focused explanation, not a complete learning PDF. The three-scale review is demonstrated for one short section; organization across a full research paper remains untested in this round.

First-draft and architecture follow-up snapshots (SHA-256; separate from the earlier run):

- math-paper-writing/SKILL.md: 42f3603f4de89ea7e72f4bb23a4ef49af6bebf2de88abbd62c04d071646dda4f
- math-paper-writing/references/exposition-and-structure.md: a39ef7bb794f82dee7bcee451af755c5a36c2af0812b886d5255c4653f44237d
- math-paper-study-guide/SKILL.md: 340904531d8f1e4e0dde079b93392de58b2b3d27504326b11a616d1793da622c
- math-paper-study-guide/references/chinese-study-edition-method.md: 6c2f15f4168c9cdf24646b5167191e050f29d7b6683025cbfe3adf645356017b

## E32 follow-up: an introduction from a public mathematical argument

**Task and evidence.** On 2026-11-04, compose a short introduction for a specialist from Ellenberg–Gijswijt's four-page [2016 paper, fixed v1](https://arxiv.org/html/1605.09223v1), focusing on its cap-set consequence. This is an attributed editorial demonstration, not our research, a replacement manuscript, or a claim to improve the authors' introduction. The maintainer read the full paper, including its original introduction; this is not a blind or fresh-context test. “We” below refers to the source authors.

**Source anchors.** Proposition 2 and its proof supply the matrix-rank mechanism; Theorem 4 and its proof supply the support/dimension step; Corollary 5 supplies the quantitative cap-set consequence. For context, consult [Bateman–Katz v2, abstract](https://arxiv.org/abs/1101.5851v2) and [Croot–Lev–Pach v2, abstract](https://arxiv.org/abs/1605.01506v2). Only those two abstracts were checked directly; their complete proofs were not reviewed.

**Draft output.**

How large can a subset of F₃ⁿ be if it contains no nonconstant three-term arithmetic progression? Bateman and Katz obtained the bound O(3ⁿ/n¹⁺ᵋ) for some ε>0. The exponential base in that estimate is still 3. We prove that every such set A satisfies

|A| = o(2.756ⁿ) as n → ∞.

Thus the density of A decays exponentially, improving the polynomial saving in the earlier bound.

The argument adapts the polynomial method of Croot, Lev and Pach, who obtained an exponential bound in (Z/4Z)ⁿ. Choose a polynomial P vanishing outside A. The absence of progressions makes the matrix (P(−a−b)) indexed by a,b∈A diagonal. A degree restriction bounds its rank and hence the number of nonzero values of P. Comparing this support bound with the dimension of the space of such polynomials gives an upper bound for |A| in terms of a monomial count. A large-deviation estimate for that count yields the exponential saving.

**Read-back before source reconciliation.** The first sentence supplies the question; the display gives the result and asymptotic parameter; the next sentence identifies the quantitative payoff. The second paragraph explains how the progression condition becomes a rank restriction and how that restriction reaches the set size. It does not require a roadmap for this short note. A point to verify against the body is whether the argument can choose P nonzero throughout A: the draft does not assert this, and the dimension step must not be shortened to such an assertion.

**Source reconciliation and repair.** The initial sentence “This leaves open whether a bound with exponential base strictly below 3 is possible” can be read as a historical priority assertion broader than the checked comparison. The delivered draft above replaces it with “The exponential base in that estimate is still 3.” The other sentences are unchanged. The revised sentence describes the displayed bound itself, while the next display and its explanation supply the advance. Rechecking this change requires no claim about all preceding literature.

The matrix description specializes the source's coefficients to α=β=γ=−1 in F₃, so −γA=A and its diagonal entries are P(a). It does not assert that all of them are nonzero. The support/dimension bridge in Theorem 4 is retained. The displayed asymptotic bound matches Corollary 5; the two prior-work comparisons match the checked abstracts. This is a source-fidelity review, not new certification of the cited theorem.

**Negative controls, deliberately supplied after drafting.**

| Changed input or proposed edit | Actual response | Review |
| --- | --- | --- |
| Remove verified prior-work material; permit only the supplied theorem and proof | Opening: “We study subsets of F₃ⁿ containing no nonconstant three-term arithmetic progression. We prove that every such set A satisfies \|A\|=o(2.756ⁿ) as n→∞, so its density decays exponentially.” Retain the supported mechanism paragraph, removing its attribution sentence until checked. Separate note: the literature comparison remains to be verified. | Produces usable prose without inventing a historical gap; incomplete context is disclosed outside the introduction. |
| Replace the dimension bridge by “P is nonzero at every point of A, so the rank equals \|A\|” | Reject that replacement: the source controls support through dimension and does not supply this assertion for the degree-constrained P. Retain the support/dimension sentences. | Detects an unsupported strengthening; this planted error was not an observed model failure. |
| Ask for a one-sentence mechanism summary | “The progression condition makes a polynomial evaluation matrix diagonal; degree bounds control its rank, and a support–dimension argument turns this into the monomial bound that yields exponential decay.” | Compression retains the intermediate bridge; it is not automatically preferable to the fuller explanation for every reader. |

**E01–E08 regression read-through.** Re-executed at the supplied fragment scope, in the same context. E01: “We present a proof draft for [the supplied claim]”; omit unverified priority. E02: “Choose an isomorphism f:X→Y supplied by Theorem 1”; continuity still requires its own argument. E03: mark the unsupported implication GAP and dependent conclusions conditional; supply no invented proof. E04: keep all six protected tokens verbatim; no full prose or build can be tested because the fixture supplies only fragments. E05: restore connectedness and “对每个 t∈(0,T)”; compare affected statements before declaring synchronization. E06: caption only as a numerical observation; axes, non-color encodings, range and reproducible source remain required rather than invented. E07: draft only the known manuscript/journal portion, with unconfirmed declarations left as placeholders; no submission. E08: “Compactness supplies the convergent subsequence at the indicated proof step, so we retain it”; propose clarification without claiming it was applied. These fragment checks found no hard failure; they are not full manuscript or build tests.

**Outcome and limits.** One actual introduction was drafted, read back and repaired, with three follow-up controls. The positive exposition evidence is a visible question/result/payoff and a causal method explanation. The first draft's comparison sentence needed narrowing. No assertion that this introduction outperforms the original, improves comprehension, or establishes reliable execution across future sessions follows. No human reader, independent agent, new-context trial or TeX build was involved.

Introduction follow-up instruction snapshots (SHA-256):

- math-paper-writing/SKILL.md: 01a37bd0d383973e048420e1497dddfdc2131eb5cb3ef803575a8470e0b7ddfd
- math-paper-writing/references/exposition-and-structure.md: 4dcf2ae8226fa2a570a69f06e9bebf2a12945084588ddc64c57762fa692d5e13
- math-paper-writing/references/delivery-checks.md: 39ce2e990f3a154b2ccf3b127a4136ec3e9c31eec06a995505fc22a57a2f20a3

## E32 paired-distillation follow-up: abstract versus introduction

**Scope and sources.** On 2026-11-04, reread the complete abstracts and introductions of Tao T07 (2202.03594v2, PDF pp. 1–2) and T14 (1805.11131v3, PDF pp. 1–5), checking their main statements and mechanism passages. Local PDFs and extracted texts matched the recorded SHA-256 values. Rendered pages inspected: T07 pp. 1–2; T14 pp. 1 and 3. The passage-level annotations are in the Tao structure report. This adds paired analysis for 2/20 existing works, not a new twenty-work distillation. The original DNA workflow remains unchanged; its mathematical adaptation supplies this focused update.

**Observed decisions.** Both abstracts identify an improvement through quantitative context and retain consequential scope, while leaving their detailed mechanism to the introduction. Their introductions develop the reason for the improvement at different lengths. That supports a local choice about allocating information, not a universal requirement to include comparisons or to reproduce Tao's sentence forms. The earlier whole-paper annotations did not separately record this division of work; the profile now does.

**Application task.** Using the complete supplied mathematical section in E31, write a standalone result-only abstract and a short introductory passage for a reader familiar with the spectral theorem. No novelty or literature comparison is supplied. This is an elementary composition exercise, not an introduction for a new research contribution. Borrow the allocation of information, not the source papers' mathematics or quantitative comparison.

**Abstract output.** Let A be a real symmetric positive semidefinite n×n matrix, n≥2, whose kernel is spanned by the all-ones vector. The equation Ax=b is solvable exactly when b has zero mean. Its mean-zero solution is unique and satisfies ‖x‖₂≤λ₂⁻¹‖b‖₂, where λ₂ is the least positive eigenvalue of A.

**Introductory output.** Consider Ax=b for a real symmetric positive semidefinite matrix A on Rⁿ, n≥2, whose kernel is spanned by the all-ones vector. This kernel has two roles: it restricts the allowable right-hand sides and leaves a constant undetermined in the solution. The natural formulation therefore pairs a zero-mean condition on b with a zero-mean normalization of x.

On this subspace the equation has a unique solution. Expanding b in an orthonormal eigenbasis constructs it by dividing each coefficient by the corresponding positive eigenvalue. The same formula bounds its Euclidean norm by λ₂⁻¹‖b‖₂, where λ₂ is the least positive eigenvalue. This connects compatibility, the construction and its quantitative control in a single argument.

**Review and controls.** The abstract states the setting, equivalence, normalization, uniqueness and norm bound without requiring the introduction. The introduction explains why those conditions occur and how the estimate is tied to the construction. Both agree with the supplied E31 body. The comparison sentence used in the source abstracts was deliberately not transferred: this task supplies no earlier result to compare. When asked whether to append the spectral-method sentence to the result-only abstract, retain the abstract unchanged; the requested result and scope are already recoverable, and the mechanism belongs in the accompanying introductory passage. When asked whether two pairs establish a Tao-wide rule, answer no and retain the 2/20 coverage label. These are actual same-context outputs and self-review, not an independent experiment or a measured readability improvement. No new general mathematical result or full learning manuscript is claimed.

Paired-distillation follow-up instruction snapshots (SHA-256):

- math-paper-writing/references/style-distillation.md: 997e92f143dbf53fb8125fc12ae97d7802e5fb883668dc4d1ec1ae40db4c9e08
- math-paper-writing/references/profiles/tao/structure-patterns.md: 04012e1b8bf7df9ad7357a878f76ce8544e82e21e5aa50face7d014e7d4f614a
- math-paper-writing/references/profiles/tao/Writing-DNA.md: 9ce88471c5b67d9a865ae2ba1bb0a161c1f90b20235ded1f3792d561e9fdd84e
