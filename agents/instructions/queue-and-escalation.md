# 重要猜想队列与推理升级

本文件适用于重要猜想长跑、Rethlas 和网页端 Pro 升级。先读根目录 `AGENTS.md`，并根据任务继续读取：

- 队列操作：`problems/important-conjectures/README.md`
- Rethlas 操作：`RETHLAS使用教程.md`

## 队列的职责

重点问题位于 `problems/important-conjectures/items/`，由 `tools/conjecture_queue.sh` 调度。每次 Codex 调用只推进一个有边界的研究回合，长期状态必须写入 `projects/conjecture-<slug>/`，不能只留在聊天上下文。

研究者负责：

- 填写 `problem.md` 和参考资料；
- 设置 `ready = true`、优先级和回合限制；
- 处理所有需要人工判断的状态；
- 复核候选证明或反例。

Agent 只能读取题目输入快照并修改对应项目，不能改写研究者维护的原题。

## 每轮要求

第一次实际调度某题时，自动创建标准项目结构。每个实质数学推进必须在 `verification-ledger.md` 中登记：

- 命题或观察；
- 证据等级；
- 反例测试；
- 证据文件；
- 依赖和影响范围。

中间步骤做局部检查。完整主猜想候选解、决定性反例、关键高风险引理和证据等级升级必须进入认证模式并完成十项检查。

调度器按优先级公平轮转。单题卡住不能阻塞其他可运行题目，除非触发全局冻结。

## 状态规则

只有以下状态自动继续：

- `queued`
- `pushing`

以下状态需要研究者处理：

- `paused`
- `needs-human-review`
- `needs-human-input`
- `needs-escalation-approval`
- `blocked`
- `attempt-limit`
- `runtime-error`
- `solved-awaiting-human-verification`
- `completed`

`needs-human-review` 只暂停当前题。`solved-awaiting-human-verification` 触发整个队列冻结。

只有满足以下条件之一，并完成十项认证，才可以设置 `solved-awaiting-human-verification`：

1. 已有完整主猜想候选证明；
2. 已有严格核验、足以彻底否定主猜想的反例。

此状态不等于问题已经由人类确认。不得自动升级为 `human-verified`。

题目存在实质歧义时设置 `needs-human-input`。需要 Rethlas 时只能准备问题包并设置 `needs-escalation-approval`，不能自动启动。

## 推理升级顺序

当前采用以下工作顺序：

```text
Codex 工作区 Agent < Rethlas < 网页端 Pro
```

这只是决定何时申请升级的经验顺序，不代表较强模型的输出可以免于验证。

### 第一级：Codex

Codex 先完成：

- 问题陈述和定义审计；
- 文献与归一化核查；
- 最小例子和反例测试；
- 至少三个攻击方向；
- 初步证明搜索；
- 把卡点压缩成最小且无歧义的命题。

### 第二级：Rethlas

如果 Codex 在一个精确定义的证明缺口上两次无法可靠关闭，或该问题适合多路线搜索和 verifier 检查，可以申请 Rethlas。

申请前必须：

1. 搜索项目正文、`notes/`、`progress.md`、proof map 和已有 Rethlas 结果；
2. 说明真正未解决的缺口；
3. 说明已有材料是否已经包含所需论证；
4. 给出预计运行目标和成本；
5. 取得研究者对本次运行的明确许可。

未经许可，只能准备问题草稿。

### 第三级：网页端 Pro

Rethlas 仍不能关闭缺口，或问题需要更强全局推理时，准备一个可直接复制的完整问题包。问题包包括：

- 正式陈述；
- 必要定义与归一化；
- 已知结果；
- 精确 gap；
- 期望输出；
- 验证要求；
- 仅在确有帮助时列出失败路线。

提示词必须要求模型直接证明或构造反例，不得把公开状态当作停止理由。未经研究者明确批准，不得自行提交网页端 Pro。

### 结果回流

研究者带回 Pro 输出后，Codex 必须独立审查，并同步到：

- `progress.md`
- `research-tree.md`
- `proof-map.md`
- `verification-ledger.md`

必要时可再次申请 Rethlas 做独立验证。所有模型输出最高先标为 `proof-draft` 或 `agent-verified`。

## Rethlas 交接前提

只有同时满足以下条件才可以交给 Rethlas：

- 问题陈述完整且无歧义；
- 定义与归一化已经审计；
- 已知结果与待证内容已经分开；
- 参考资料已经整理；
- 精确缺口已经写清；
- 研究者已批准本次运行。

标准流程：

1. 用 `tools/rethlas/init_project.sh` 建立问题。
2. 把正式问题和 `.refs/` 资料放入项目的 `rethlas/problems/`。
3. 报告问题文件、精确缺口和运行目标。
4. 获得许可后启动 verification service。
5. 运行 `tools/rethlas/run_problem.sh` 或 tmux 包装脚本。
6. `blueprint.md` 最高标为 `proof-draft`。
7. `blueprint_verified.md` 最高标为 `agent-verified`。
8. 同步 verifier 报告、失败路线和新引理。
9. 研究者独立复核后，才可升级为 `human-verified`。

Rethlas 找到候选证明时，只冻结依赖该证明的分支。可以继续做不依赖它的实验、反例搜索、文献核查和其他路线。

## Rethlas 的 tmux 运行

Rethlas 长任务使用 tmux，不让当前 Agent 持续轮询。

先启动或检查 verifier：

```bash
./tools/rethlas/start_verifier_tmux.sh
curl -sf http://127.0.0.1:8091/health
```

脚本必须确认服务进程配置了真实可执行的绝对 `CODEX_BIN`。若旧服务配置无效，并且确认没有 generation 正在提交验证，可运行：

```bash
RESTART_STALE=1 ./tools/rethlas/start_verifier_tmux.sh
```

verifier 可访问后再启动 generation：

```bash
MAX_ITERATIONS=6 ./tools/rethlas/run_problem_tmux.sh <项目名> <问题名> <session名>
```

启动后告诉研究者：

```text
generation session名 = <session名>
verifier session名 = rethlas_verifier
查看 generation = tmux attach -t <session名>
查看 verifier = tmux attach -t rethlas_verifier
退出查看但不中断运行 = Ctrl-b，然后 d
```

未指定 session 名时使用可读、稳定的名字。不要每隔几十秒轮询。只有研究者询问状态，或任务结束需要分析结果时，才读取日志和结果目录。

## 普通猜想队列的 tmux 运行

常用入口：

```bash
./queue.sh check
./queue.sh start
./queue.sh status
./queue.sh watch
./queue.sh stop
```

`start` 在 tmux 中后台运行。`stop` 应让当前研究回合安全结束，不能在写文件时强杀进程。电脑休眠或关机会暂停或停止计算；重新启动后从磁盘状态继续。

## 全局冻结与人工处理

出现 `solved-awaiting-human-verification` 时：

1. 整个队列立即退出；
2. 不转去研究其他猜想；
3. 保留候选证明、反例、十项审查和全部证据；
4. 等待研究者逐步复核；
5. 未经明确处理，不恢复队列。

需要研究者判断时，只报告精确问题、当前证据和可选动作。不要把“请确认”写成模糊的流程占位。
