# 探索与路线诊断

按核心机制维护方法族登记：表示、不变量、子目标、来源/暴露范围、证伪测试、障碍与重开条件。至少三个不同方向用于初始发散或重新规划，不要求每轮重新发现问题。一个主路线深入至完整候选、严格反例或精确缺口。

同一障碍失败两次不重复原推导，改表示、弱化目标、找反例或准备升级申请。记录失败位置与类型 gap/counterexample/circular/too-strong/definition-mismatch/reference-mismatch/missing-tool、暂时或结构性、影响范围、中间结果。只有新机制/不变量/构造/假设/工具能直接攻击原 gap 才重开，改名或增加 Agent 不算。

局部修复继续；关键结论失效只回退依赖分支，降为 blocked/partial-result/GAP 并记精确记录。所有已知路线阻塞仍按搜索承诺完成再发散。候选主结果转 proof-audit；反例另读 counterexample-audit。
