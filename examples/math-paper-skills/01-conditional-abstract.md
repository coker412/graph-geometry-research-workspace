# 样例一：把摘要写直接，同时保留分类前提

**来源：** OpenAI，*An L² Einstein Gap for Nonnegatively Curved Four-Manifolds*，2026-10-05。[固定版本 PDF](https://github.com/openai/math/blob/4eaee87548250b2682affda7d05d947c05554bae/preprints/An-L2-Einstein-Gap-for-Nonnegatively-Curved-Four-Manifolds-October-5-2026/einstein-gap.pdf)，第 1 页摘要、Classification Assumption 1.1，以及第 1–2 页 Theorem 1.2。

这是对来源稿件主张的编辑示例，完整证明未在此重新认证。

## 原文中需要处理的关系

摘要先写能量间隙与微分同胚结论，随后交代它使用另一篇稿件的 Einstein 分类。最后一句是：

> The conclusion concerns the smooth manifold, not an isometry of the original metric.

这一区分有数学含义。若前面已明确说结论是微分同胚分类，是否还需要再说明一次，取决于该段的读者和上下文。分类前提则必须保留，不能因为它像“限制”就删除。

## 可复现任务

```text
使用 math-paper-writing，改写指定摘要，使前提和结论更容易定位。
保留分类假设、四维、闭、单连通、非负截面曲率、尺度不变的 L² 小能量，
以及微分同胚结论和无需额外几何界的范围。先完成结构改写；
再只用 anti-defensive-writing 检查是否还有重复的范围说明。
分别显示这两步的差异，不补充证明或提高来源结果的验证等级。
```

## 核心写作输出

Assuming the stated classification of closed four-manifolds with positive Einstein metrics and nonnegative sectional curvature, we establish a universal, scale-invariant $L^2$ gap for the trace-free Ricci tensor. Every closed, connected, simply connected smooth four-manifold with nonnegative sectional curvature and sufficiently small trace-free Ricci energy is diffeomorphic, without a prescribed orientation, to $S^4$, $\mathbb{CP}^2$, or $S^2\times S^2$. No additional bounds on curvature, volume, diameter, injectivity radius, or Sobolev constants are required. This identifies the smooth manifold; it does not identify the original metric up to isometry.

## 再做局部去防御性清理

在这个版本中，删除最后一句，其余三句原样保留。原因是第二句已经准确说出了微分同胚结论；最后一句没有增加新的条件。这里没有把分类前提或“无额外几何界”删掉，它们都提供实质信息。

最终稿就是上面的前三句。中文对应如下：

在接受上述闭四维流形上正 Einstein 度量、非负截面曲率的分类结论这一前提下，我们建立无迹 Ricci 张量的普适、尺度不变的 $L^2$ 间隙。任一具有非负截面曲率、无迹 Ricci 能量充分小的闭、连通、单连通光滑四维流形，都在不指定取向的意义下微分同胚于 $S^4$、$\mathbb{CP}^2$ 或 $S^2\times S^2$。这一结论不要求额外的曲率、体积、直径、单射半径或 Sobolev 常数界。

## 数学内容核对

| 保护项 | 来源与输出的对应 |
| --- | --- |
| 分类是前提 | 第一句保留；没有把依赖其他稿件的结论改成无条件结论 |
| 几何范围 | 四维、闭、单连通、非负截面曲率全部保留；原文 closed 指紧且无边界 |
| 小量 | 保留无迹 Ricci 张量的 $L^2$ 能量及其尺度不变性；没有改成逐点小曲率 |
| 结论类型 | 微分同胚于三个标准光滑流形；没有声称原度量等距于标准度量 |
| 附加条件 | 无额外几何界的陈述保留 |

前提提前属于结构修改；删除末句属于局部去防御性修改。这个样例能展示二者的差异，不证明某个模块普遍优于另一种写法。[返回样例首页](README.md)。
