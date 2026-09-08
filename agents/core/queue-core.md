# 队列回合

只读正式题目快照，只修改指定项目。普通回合单 researcher；多智能体须研究者明确要求。mixed-isolated 只在配置明确选择时运行，两支后汇合，通常三次调用。

queued/pushing 自动轮转；其他状态等人工处理。needs-human-review 只暂停当前题。完整主问题候选证明或决定性反例经过十项认证后才进入 solved-awaiting-human-verification，全局冻结，仍不是人类确认。审计不完整先 needs-human-review。题意歧义用 needs-human-input；申请 Rethlas 用 needs-escalation-approval，不能运行。

affirmative-proof 路线耗尽后必须按题目 stagnation_rounds_before_blocked 再发散；0 表示不因停滞自动 blocked，正整数要达到连续无新机制门槛并保存停滞证书。新机制重置计数。V2 writer 不判断证书真实性，需停滞裁决时提交 needs-human-review。

本轮包给出的进展评估规则继续适用：先封存 PLAN，结束封存 RESULT，独立 REVIEW 缺失则未知，不伪造失败或数学进展。重复障碍需换机制；状态维护不能代替研究。

V2 回合只写 notes/code/lean 等研究产物和指定目录的 ROUND_RESULT.json、进展评估材料；不直接修改共享台账、CURRENT_STATE 或 .conjecture-status。runner 校验后写入。兼容回合由根 Agent 追加 progress、登记实质结果、重写短状态；只在结构变化时改 proof-map/ideas/research-tree，禁止向 README 追加回合日志。
