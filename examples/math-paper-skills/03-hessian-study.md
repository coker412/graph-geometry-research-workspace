# 样例三：为什么这个 Hessian 正定？

**来源：** OpenAI，*A Smooth Nonquadratic Entire Affine Maximal Graph in Dimension Ten*，[固定版本 PDF](https://github.com/openai/math/blob/4eaee87548250b2682affda7d05d947c05554bae/preprints/Smooth-Nonquadratic-Affine-Maximal-Graph-in-Dimension-Ten-October-5-2026/affine-maximal-dimension-ten.pdf)，第 2 页 Proposition 2.1 的局部计算，式 (4)–(5)。本页只讲这个恒等式及其正定性，不证明整篇论文。

## 可复现任务

```text
使用 math-paper-study-guide，解释命题2.1中 u=sqrt(F²+t²) 的 Hessian 为什么正定。
假设我只熟悉多元微积分和线性代数。展开求导、平方配方和严格正定的判断，
再算一个二维例子。保留 F>0 和 D²F>0，说明逐点正定与一致下界的区别。
这是局部 Markdown 学习示例，不需要整篇论文学习 PDF。
```

## 先确定要证明什么

设 $\Omega\subset\mathbb R^m$ 为开集，$F:\Omega\to(0,\infty)$ 二阶连续可微，并且 $H=D_x^2F$ 在每点正定。令

$$
u(x,t)=\sqrt{F(x)^2+t^2},\qquad (x,t)\in\Omega\times\mathbb R.
$$

我们要检查：任取非零方向 $v=(\xi,\tau)\in\mathbb R^m\times\mathbb R$，是否都有 $v^TD^2u\,v>0$。这是整个 Hessian 的正定性；仅检查各坐标方向的二阶导数为正还不够。

## 从偏导算到平方配方

用 $F_i=\partial_iF$、$F_{ij}=\partial_i\partial_jF$ 表示导数。链式法则给出

$$
u_i=\frac{FF_i}{u},\qquad u_t=\frac{t}{u}.
$$

再次求导，并用 $u^2-F^2=t^2$ 化简：

$$
u_{ij}=\frac FuF_{ij}+\frac{t^2}{u^3}F_iF_j,
\qquad u_{it}=-\frac{Ft}{u^3}F_i,
\qquad u_{tt}=\frac{F^2}{u^3}.
$$

例如第一式先得到 $(F_iF_j+FF_{ij})/u-F^2F_iF_j/u^3$；合并两个含 $F_iF_j$ 的项才得到上式。

令 $a=\nabla F\cdot\xi$。把这些分量代入二次型，得到

$$
\begin{aligned}
v^TD^2u\,v
&=\frac Fu\xi^TH\xi+\frac{t^2a^2-2Fta\tau+F^2\tau^2}{u^3}\\
&=\frac Fu\xi^TH\xi+\frac{F^2}{u^3}
\left(\tau-\frac tF\nabla F\cdot\xi\right)^2.
\end{aligned}
$$

这就是来源式 (4) 作用在具体方向上的含义。混合项没有消失，而是被吸收进第二个平方。

## 为什么是严格正定

由于 $F>0$、$u>0$，两个系数都为正。

- 若 $\xi\ne0$，$H>0$ 使第一项严格为正，第二项非负。
- 若 $\xi=0$，非零方向要求 $\tau\ne0$，于是第二项为 $F^2\tau^2/u^3>0$。

两种情况覆盖所有非零方向。关键是两项的零方向没有非零交集；不需要每一项单独在所有方向上都严格为正。

## 实际算一次

取 $m=1$、$F(x)=1+x^2$，于是 $F''=2>0$。在 $(x,t)=(1,2)$ 处，$F=2$、$F'=2$、$u=2\sqrt2$，上面的公式给出

$$
D^2u=\frac1{4\sqrt2}
\begin{pmatrix}12&-2\\-2&1\end{pmatrix},
\qquad
v^TD^2u\,v=\sqrt2\,\xi^2+\frac{(\tau-2\xi)^2}{4\sqrt2}.
$$

取 $v=(1,2)$ 时平方项为零，第一项仍为 $\sqrt2$；取 $v=(0,1)$ 时第一项为零，平方项为 $1/(4\sqrt2)$。矩阵的首个顺序主子式为正，行列式为 $1/4>0$，也与二维正定性判据一致。

这个 $F$ 只用于演示 Hessian 计算。没有在这里构造满足来源径向系统的 $P$，因此不能说这个二维例子已经解了仿射极大方程。

## 两个容易混淆的地方

**严格凸性不能丢。** 若改取常数 $F=1$，则 $u$ 与 $x$ 无关，所有纯 $x$ 方向的二次型都为零；Hessian 只有半正定性。

**逐点正定不保证全局统一下界。** 对刚才的 $F=1+x^2$，沿 $x=0$ 有

$$
u_{tt}(0,t)=(1+t^2)^{-3/2}\longrightarrow0\quad(|t|\to\infty).
$$

因此不存在对所有点都成立的常数 $c>0$，使 $D^2u\ge cI$。这个条件差别有实质内容，不能作为“防御性语言”删掉。

**核验范围：** 这里是已有局部公式的教学复现（同一助手推导和自查，尚非独立验证）。[检查脚本](check_examples.py)另作精确有限样本核对；它不验证来源主定理，也不证明读者已经掌握。[返回样例首页](README.md)。
