# 图几何与几何分析研究工作台

每次回答以 **Hi, mathematician!** 开头。
工作区为 `__WORKSPACE_ROOT__`，用于离散几何、几何分析与数学研究管理。

## 不可变边界

- 公开问题也必须实际尝试证明或构造反例，不能用综述或公开状态代替推进。
- 区分探索与认证。探索可在明确标为 conditional/GAP 的引理上推进；完整候选解、决定性反例、高风险共同依赖和证据升级必须进入认证，冻结受影响的依赖分支。
- 实质结论必须有证据等级和直接证据：`conjecture`、`experimental`、`partial-result`、`proof-draft`、`agent-verified`、`human-verified`、`formalized`。计算不是证明，自检不能成为独立验证，模型强度与状态整理不能提高等级。
- `agent-verified` 需要 verifier 或独立 Agent 审查；`human-verified` 需要研究者逐步接受；`formalized` 需要形式系统检查。论文主结果无保留写入摘要和结论须达到后两级，并取得研究者授权。
- Rethlas 与网页端 Pro 必须逐次明确批准。可准备问题包，不能自行启动或提交。外部写入、公开发布、额外费用和扩大权限前核对已有授权，没有授权时先询问。
- 不写机密、不修改 `.env`、不覆盖已有改动、不用破坏性命令清理。修改前后检查 Git diff；没有 Git 时保存快照并检查文件差异。除非明确要求，不提交或推送。

## 按阶段读取

只读当前任务所需模块，已包含在 RESEARCH_PACKET 中的正文不重复读取。开始相关工作前完成读取，并在首次实质进度更新列出路径：

- 数学任务：`agents/core/research-core.md`，再按阶段读取下面的协议。
- 探索、路线诊断：`agents/protocols/explore.md`。
- 候选证明、严格审核、证据升级：`agents/protocols/proof-audit.md`。
- 决定性反例：再读 `agents/protocols/counterexample-audit.md`。
- 文献核查：`agents/protocols/literature-check.md`。
- 计算实验：`agents/protocols/computation.md`。
- 队列回合：`agents/core/queue-core.md`；操作调度器时另读 `problems/important-conjectures/README.md`。
- Rethlas/网页端升级：`agents/protocols/escalation.md`。
- 论文、LaTeX、面向公开读者的研究文字：`agents/instructions/paper-writing.md`；润色优先使用 humanizer，不改变数学内容。
- 研究者明确要求多智能体时：`agents/protocols/multi-agent.md`。不因工具可用自行增加并行 Agent。

旧入口 `agents/instructions/research-workflow.md` 和 `queue-and-escalation.md` 提供索引。更近的 AGENTS.md 继续适用。

## 长期记忆与目录

`CURRENT_STATE.md` 是恢复的唯一短入口，只保存问题边界、证据等级、可用结果 ID、活动 gap/路线、下一动作和证据指针，不存证明正文。目标 6 KiB，超过 8 KiB 提醒；V2 新写入硬限 12 KiB/300 行，旧摘要暂保留 32 KiB/300 行兼容上限，禁止为满足大小静默截断证据。

先读状态，再按稳定 ID 和 `file#L起-L止` 或带 SHA256 的片段读取证据。禁止为了了解上下文完整重读增长中的历史台账。摘要不能覆盖 ledger 或直接证据；首次迁移只核对当前状态段、最近完整回合与被引用证据，未读历史按未知处理。

产物位于 `projects/<项目名>/`：短状态 `CURRENT_STATE.md`，追加历史 `progress.md`，证据 `verification-ledger.md`，依赖 `proof-map.md`，路线 `ideas.md`/`research-tree.md`，稳定说明 `README.md`。证明草稿放 `notes/`，实验放 `code/`，形式化放 `lean/`，Rethlas 放 `rethlas/`，论文源码只放 `paper/`。开放问题放 `problems/`，通用定义与例子放 `library/`，跨项目材料放 `shared/`。

只有对应结构变化才更新路线/依赖文件。README 不追加回合日志。V2 researcher 写证明与 ROUND_RESULT.json，由 runner 整理共享状态；手工与兼容回合由根 Agent 统一收尾。

## 环境与交付

Python 使用 Conda `graphlab`；LaTeX 在对应 `paper/` 运行 `latexmk -xelatex main.tex` 并遵守论文模块的完整检查；Lean 使用项目 `lean-toolchain`。长进程优先 tmux，告知会话及查看/退出方法。

多步骤任务写明目标、假设、产物和验收标准。完成时报告文件路径、检查、缺口、证据等级及下一动作。问题有实质歧义、要求但无法核实新颖性、主要路线满足搜索承诺后仍结构性阻塞、候选结果需要人类确认、准备写论文主结果或改变项目目标时，保存具体材料再询问研究者。
