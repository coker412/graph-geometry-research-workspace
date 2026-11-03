# 六组精选改写：把信息写紧凑，把依赖说清楚

从两轮十六组实际试写中选出六组。前三组压缩任务说明、常数依赖和结果分工，后三组处理固定对象、两次极限与调和延拓。选择依据是信息保留、指代和证明组织；长度是辅助记录。十六组并非随机样本，这六组由同一助手选择和复查，不能据此推断平均效果或某个模块的独立贡献。

**对比方式：** “原文完整中译”逐句覆盖选定连续片段，不用缩略概述作为基线；英文短引用于定位，原文全文通过固定 PDF 查看。“英文改写”是实际输出，下方附对应中文。每例单独说明保留的条件与允许的局部变化。数学记号、相邻公式和原文引用编号沿用来源。

| 例子 | 英文原文 → 改写词数 | 主要修改 |
| --- | --- | --- |
| 1 | 68 → 46 | 合并任务说明，分清存在性与一致估计的来源 |
| 2 | 31 → 18 | 直接给出常数依赖顺序 |
| 3 | 42 → 30 | 交代外部存在性与本文曲率估计的分工 |
| 4 | 38 → 23 | 同一条流及固定参数只交代一次 |
| 5 | 35 → 20 | 直接说明两次极限分别做什么 |
| 6 | 106 → 78 | 按逼近、收敛、取迹安排证明 |

词数按合并换行后的英文粗计，数学排版与连字符会影响分词；比较范围是选定片段，不是整篇论文。第 2 例只改段首三句，第 4 例改两句，第 5 例改一句。上下文中必要的公式和条件保持原样。

## 如何复现

向 math-paper-writing 提供所链接 PDF 的指定片段及相邻上下文，要求：在保留条件、对象、量词、依赖、引用与证明状态的前提下，改善该例指出的具体问题；保留已经清楚的句子，输出英文和中文对照。不得用新结论、补充解释或删除技术机制制造改善。这里没有新做 DNA 蒸馏或完整作者风格复刻；去防御性判断只在重复否定影响表达时使用。

## 1．把章节说明压缩成实际工作与依赖

来源：[Calderón 问题的单边界片局部数据稿](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Smooth-Anisotropic-Uniqueness-in-the-Calderon-Problem-from-One-Boundary-Patch-September-24-2026/paper.pdf)，PDF 第 19 页，第 4 节开头完整四句。定位首句：

> We now apply the product continuation criterion near a point where an isometry is already known on one side.

**原文完整中译：**

我们现在在一个点附近应用乘积延拓判据，该点的一侧已知存在等距映射。本节的目的是构造一族作用在调和函数上的泛函，它们由小球面表示。它们的存在性将由这些球面的几何得到。球面收缩时所需的泛函一致界，将由下一节的估计得到。

**英文改写：**

We apply the product continuation criterion near a point where an isometry is known on one side, constructing a family of functionals on harmonic functions. They are represented on small spheres, whose geometry gives existence. The next section bounds these functionals uniformly as the spheres shrink.

**改写中译：**

我们在一侧已知存在等距映射的点附近应用乘积延拓判据，构造一族作用在调和函数上的泛函。这些泛函由小球面表示，其存在性来自球面的几何。下一节证明球面收缩时这些泛函的一致界。

**取舍：** 合并“现在应用……”与“本节目的是……”，把最后一句的主语改成真正提供估计的下一节。保留单侧等距、乘积延拓判据、泛函族、调和函数、小球面表示、几何提供存在性、下一节提供收缩过程中的一致界。没有把存在性与一致估计归给同一项输入。

## 2．让选择顺序本身承担提醒作用

来源：[负曲率 Kähler 三维复流形稿](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-negatively-pinched-Kahler-threefold-without-bounded-holomorphic-coordinates-September-25-2026/paper.pdf)，PDF 第 16 页首段前三句，止于 Q₀ 的选择。定位：

> We emphasize the order of the choices.

**原文完整中译：**

我们强调这些选择的顺序。归一化修正常数 $C_2$ 只依赖固定的局部片数据。它确定 $K_*$；后者再确定 $C_1$；最后选择 $Q_0$。

**英文改写：**

The fixed patch data alone determine the normalized correction constant $C_2$, then $K_*$, then $C_1$; choose $Q_0$ last.

**改写中译：**

仅由固定的局部片数据确定归一化修正常数 $C_2$，再依次确定 $K_*$、$C_1$；最后选择 $Q_0$。

**取舍：** 删除“我们强调”这句通知，依赖顺序直接呈现在正文中。保留 only/alone、常数名称、三个先后依赖及 Q₀ 最后选择。原段后面关于 $W_j$、逐阶段正比较、对数微分和概率归一化的三句不改，不把它们当作可删除的重复话。

## 3．直接说明外部结果与本文证明各做什么

来源：[有界标量曲率与有限时刻曲率爆破的 Ricci 流稿](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-closed-Ricci-flow-with-bounded-scalar-curvature-and-finite-time-curvature-blowup-September-24-2026/paper.pdf)，PDF 第 5 页 Remark 2.2 全文，去掉 remark 标题。定位：

> Proposition 2.1 is the external existence input to this paper.

**原文完整中译：**

命题 2.1 是本文的外部存在性输入。我们不从外部引入标量曲率上界、帽尺度下的全曲率界，也不引入向某个特定完备帽度量的收敛。建立这些曲率界的估计将在下文给出。

**英文改写：**

Proposition 2.1 supplies the external existence input. We prove the scalar-curvature upper bound and full-curvature bound at the cap scale below, without assuming convergence to a particular complete cap metric.

**改写中译：**

命题 2.1 提供外部存在性输入。下文证明标量曲率上界和帽尺度下的全曲率界，不预设向某个特定完备帽度量的收敛。

**取舍：** 原文先否定“外部提供曲率界”，下一句再说“本文证明曲率界”；改写直接说谁证明这些界。这一段确有具体比较对象——命题 2.1，所以保留区分的实际内容。关于完备帽度量收敛的说明也保留；没有把它误写成本文已经证明的结果。

## 4．固定同一条流，合并重复说明

来源：[固定版本 PDF](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-closed-Ricci-flow-with-bounded-scalar-curvature-and-finite-time-curvature-blowup-September-24-2026/paper.pdf)，PDF 第 15 页，式 (6.3) 后两句。

**原文完整中译：**

下文其余常数都针对同一条流选择。每当需要更晚的起始时间，我们就将已经选定的流限制到一个更晚的时间切片；我们不重复构造，也不改变其参数。

**英文改写：**

Choose all remaining constants for this fixed flow. To start later, restrict it to a later time slice, keeping its construction parameters fixed.

**改写中译：**

针对这条固定的流选择其余所有常数。需要推迟起始时间时，将它限制到更晚的时间切片，并保持构造参数不变。

**判断：** 同一条流和参数冻结都是证明所需信息，保留；“限制已选流”已经描述了实际操作，可与“不重新构造”合并。没有让后续估计作用在另一条重新选择的流上。

## 5．直接说明两个极限的分工

来源：[固定版本 PDF](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Smooth-Anisotropic-Uniqueness-in-the-Calderon-Problem-from-One-Boundary-Patch-September-24-2026/paper.pdf)，PDF 第 36 页，式 (6.10) 前第一句。

**原文完整中译：**

为清楚起见，这个证明中的两个极限有不同作用：空间缩放只使用一次，以得到一个固定的小度量差；随后收缩的族改善的是同一个度量差的界。

**英文改写：**

One spatial dilation makes the metric difference small; the subsequent shrinking family improves the bound on that same fixed difference.

**改写中译：**

一次空间缩放使度量差变小；随后收缩的族改善同一个固定度量差的界。

**判断：** 删除“为清楚起见、两个极限有不同作用”的预告，直接给出各自作用。保留一次缩放、随后收缩、同一固定差值；后面的参数顺序公式 (6.10) 和有限阶导数约定不改。

## 6．按逼近、收敛、取迹的次序组织

来源：[固定版本 PDF](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-Three-Dimensional-Counterexample-to-Integer-Degree-Harmonic-Dimension-Comparison-September-26-2026/paper.pdf)，PDF 第 24 页，式 (5.7) 后完整段落。

**原文完整中译：**

由稠密性，这些映射延拓到 $L^2(\mu)$。为清楚起见，延拓后的映射仍然是内部同一个调和函数的迹：用光滑数据在 $L^2$ 中逼近边界值，并在内球面上使用 (5.7)。局部 $L^2$ 到上确界估计，接着是内部 Schauder 估计及其对微分后光滑方程的迭代，使这些延拓在更小紧集上的每个光滑范数下都是 Cauchy 列［8，定理 8.17，第 194 页，取 $p=2$；推论 6.3，第 93–94 页］。其极限是调和的，唯一性由同一逼近得到。这也表明，从 $L^2$ 边界数据得到的限制在每个严格内部球面上都是光滑的。

**英文改写：**

Approximate each $L^2(\mu)$ boundary value by smooth data. Estimate (5.7) on inner spheres, the local $L^2$-to-sup estimate, and iterated interior Schauder estimates make the harmonic extensions Cauchy in every smooth norm on smaller compact sets [8, Theorem 8.17, p. 194, with $p=2$, and Corollary 6.3, pp. 93–94]. They converge to a harmonic function, unique by the same approximation. Thus the maps extended by density to $L^2(\mu)$ are traces of this single function, smooth on every strictly inner sphere.

**改写中译：**

用光滑数据逼近每个 $L^2(\mu)$ 边界值。内球面上的估计 (5.7)、局部 $L^2$ 到上确界估计以及迭代的内部 Schauder 估计，使调和延拓在更小紧集上的每个光滑范数下都是 Cauchy 列［8，定理 8.17，第 194 页，取 $p=2$；推论 6.3，第 93–94 页］。它们收敛到一个调和函数，唯一性由同一逼近得到。因此，由稠密性延拓到 $L^2(\mu)$ 的映射，是同一个函数的迹，并在每个严格内部球面上光滑。

**判断：** 估计编号、完整来源定位、局部区域、每个光滑范数、调和极限与唯一性均保留。将段落从“先声明迹仍相容，再解释，最后再声明光滑”重组为一次完整的构造过程。此处沿用来源关于唯一性的论证，不增加证明步骤或独立认证该结论。

## 哪些没有选

十组未入选的修改包括：削弱了局部适用范围的压缩；把三个证明步骤挤入长句；仍然罗列未假设条件；以及原文已经清楚、仅改变语态或减少几个词的版本。它们不计作成功。原有[摘要取舍](01-conditional-abstract.md)和[证明概览取舍](02-proof-overview.md)也保留，供比较何时改写未必更好。

已核对选段、上下文与 PDF 原页，未重新认证来源论文的完整主定理。本页的中文原文翻译与英文改写是本项目制作；不代表原作者认可。来源版本、页码、PDF 哈希见 [sources.json](sources.json)，保留来源的 [Apache-2.0 许可](OPENAI-MATH-LICENSE)。[返回样例首页](README.md)。
