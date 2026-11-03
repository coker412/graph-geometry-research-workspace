# 样例二：辅助函数出现后，怎样把读者带回原问题

这是组织取舍示例，不作为完整替代稿。改写更集中地介绍辅助量，但省略了原概览中向量场单调性与平衡角点控制的机制；不能据此宣称全面改善。优先查看[六组精选对照](04-selected-revisions.md)。

**来源：** OpenAI，*A Smooth Nonquadratic Entire Affine Maximal Graph in Dimension Ten*，2026-10-05。[固定版本 PDF](https://github.com/openai/math/blob/4eaee87548250b2682affda7d05d947c05554bae/preprints/Smooth-Nonquadratic-Affine-Maximal-Graph-in-Dimension-Ten-October-5-2026/affine-maximal-dimension-ten.pdf)，第 2 页引言末段与 Proposition 2.1，第 3 页式 (6)。本例重组来源中的证明概览，不认证其全局论证。

## 原文定位

原段落已经明确指出障碍：

> The main obstacle is then global existence: a priori the auxiliary function P could vanish at a finite radius.

它还说明了径向约化、原点处的局部构造和不变区域。因此这里不把原稿描述成“没有解释证明思路”。改写的目标是让辅助量的作用、全局障碍和最终返回原方程连在一起。

## 可复现任务

```text
使用 math-paper-writing 改写第2页的证明概览。
局部借用 Tao 画像中“说明中间目标，并返回原问题”的方法。
只用原文给出的构造和依赖，不新增估计、结论或符号；
解释 F、P 的用途和全局存在的障碍。给英文稿与中文对应。
这是局部方法借用，不是完整 Tao 风格复刻，也不执行新的作者蒸馏。
```

## 英文改写

We seek the graph in the form $u(x,t)=\sqrt{F(x)^2+t^2}$. Introducing $P$ separates the determinant power in the affine maximal equation and reduces the construction to a radial system for $F$ and $P$. After constructing a smooth solution at the origin, the main task is to prevent $P$ from vanishing at a finite radius. A change to logarithmic derivative variables provides a bounded invariant region that controls the radial continuation. Returning through Proposition 2.1 then gives the required entire graph and pointwise positive-definite Hessian.

## 中文对应

我们寻找形如 $u(x,t)=\sqrt{F(x)^2+t^2}$ 的图像。引入 $P$ 后，仿射极大方程中的行列式幂可以分离，构造问题随之化为关于 $F$ 和 $P$ 的径向系统。在原点处构造光滑解之后，主要任务是排除 $P$ 在有限半径处降为零。改用对数导数变量，可得到一个控制径向延拓的有界不变区域。最后回到命题 2.1，便得到所需的整图像及逐点正定的 Hessian。

## 改动及其边界

| 写作选择 | 实际作用 |
| --- | --- |
| 先展示图像的构造形式 | 读者先知道最终要构造什么 |
| 在引入 $P$ 时说明其作用 | 辅助函数用于分离行列式幂，不只是另一个名称 |
| 把局部构造与全局延拓分开 | 原点附近的光滑解尚不能自动给出整空间上的解 |
| 结尾指回命题 2.1 | 解释径向系统的成果怎样回到原方程 |

“pointwise”保留；这里没有增加全局一致 Hessian 下界或仿射度量完备性。没有运行 anti-defensive 清理来制造差异：这次变化主要来自证明组织。原文更详细的向量场单调性与角点控制仍在正文中，概览不替代那部分论证。[返回样例首页](README.md)。
