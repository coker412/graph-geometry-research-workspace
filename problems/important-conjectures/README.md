# 重要猜想 Codex 长跑队列

这套队列让老师只负责投放和排序重要猜想，由 Codex 在 tmux 后台逐题轮转研究。它不依赖 Danus 或 Claude Code；Rethlas 只作为老师明确批准后的升级通道。

## 工作方式

```text
老师填写题目
    ↓ ready = true
Codex 回合 1：定义审计、最小例子、路线生成
    ↓ 把状态写入项目文件
轮到下一道猜想
    ↓ 下一轮回来继续当前最小缺口
完整证明主猜想 / 严格反例彻底否定主猜想
    ↓ 十项审查通过后自动全局冻结并退出队列
老师审查并决定完成、恢复或批准 Rethlas 升级
```

每个 Codex 调用只做一个有边界的研究回合。长期记忆不依赖聊天上下文，而是写入：

```text
projects/conjecture-<slug>/
├── README.md
├── references.md
├── ideas.md
├── progress.md
├── verification-ledger.md
├── research-tree.md
├── proof-map.md
├── notes/
├── code/
├── lean/
├── rethlas/
├── input-snapshots/
├── CURRENT_INPUT.md
└── .conjecture-status
```

题目原文始终保留在 `problems/important-conjectures/items/<slug>/`。Runner 会建立不可变输入快照，不会让研究 Agent 改写老师的原题。

第一次真正调度某题时，runner 会自动创建这个完整项目骨架。以后每个回合都必须追加 `progress.md`，并在 `verification-ledger.md` 逐条登记新增数学陈述、证据等级、十项检查、反例测试、审查结论和证据文件。

## 老师的最短操作流程

所有命令都在工作区根目录执行。

### 1. 新建题目

```bash
./tools/conjecture_queue.sh add hadwiger-conjecture "Hadwiger conjecture"
```

然后填写：

```text
problems/important-conjectures/items/hadwiger-conjecture/problem.md
```

参考论文、讲义或已有笔记可放入：

```text
problems/important-conjectures/items/hadwiger-conjecture/references/
```

最后编辑同目录的 `config.toml`，把 `ready = false` 改成 `ready = true`。

### 2. 启动前检查

```bash
./tools/conjecture_queue.sh doctor
./tools/conjecture_queue.sh list
./tools/conjecture_queue.sh run --dry-run
```

`--dry-run` 会显示下一题、项目路径和 Codex 命令，但不会消耗模型额度。

### 3. 后台长跑

```bash
./tools/conjecture_queue.sh start
```

查看实时输出：

```bash
./queue.sh watch
```

退出查看但不中断运行：按 `Ctrl-b`，然后按 `d`。

查看总状态：

```bash
./tools/conjecture_queue.sh status
```

安全停止：

```bash
./tools/conjecture_queue.sh stop
```

安全停止不会强杀正在写文件的 Codex；当前研究回合结束后，runner 才退出。

## 调度规则

- `priority` 数字越大越先运行。
- 每一轮中，每道可运行题最多获得一个 Codex 回合；然后调度器转到下一题，避免难题独占机器。
- 一轮结束后重新扫描目录，因此老师可以在 runner 运行时继续添加题目或调整优先级。
- `max_attempts = 0` 表示不限制该题的累计回合数；早期试运行建议先设为 `3` 或 `5`。
- `runner.toml` 的 `max_wall_hours` 控制一次后台启动的总时长。默认 24 小时；设为 `0` 才是持续运行直到人工停止。
- 单回合默认 90 分钟超时。连续三次 CLI 或超时故障会冻结为 `runtime-error`，防止无休止消耗额度。

## 状态机

| 状态 | 是否自动继续 | 含义 |
|---|---:|---|
| `queued` | 是 | 等待第一次运行 |
| `pushing` | 是 | 有明确的下一研究动作 |
| `paused` | 否 | 老师暂时暂停 |
| `needs-human-review` | 否 | 重要中间结果或审计问题需要老师判断；只暂停当前题，其他题继续 |
| `solved-awaiting-human-verification` | 否 | 主猜想有完整候选证明或严格反例；触发全局解答冻结 |
| `needs-human-input` | 否 | 题目存在实质歧义或缺少老师决定 |
| `needs-escalation-approval` | 否 | Codex 已压缩出精确缺口并申请 Rethlas；尚未获准运行 |
| `blocked` | 否 | 主要路线均结构性阻塞 |
| `attempt-limit` | 否 | 达到该题 `max_attempts` |
| `runtime-error` | 否 | 连续运行故障达到上限 |
| `completed` | 否 | 老师确认不再继续队列研究 |

老师可手动改变状态：

```bash
./tools/conjecture_queue.sh set-status hadwiger-conjecture paused
./tools/conjecture_queue.sh set-status hadwiger-conjecture pushing
./tools/conjecture_queue.sh set-status hadwiger-conjecture completed
```

`needs-human-review` 只暂停当前题，runner 会继续轮询其他猜想。老师阅读该题的 `progress.md`、候选证明或反例文件及 `proof-map.md` 后，可用 `set-status` 明确设为 `pushing`、`paused`、`blocked` 或 `completed`。

只有 `solved-awaiting-human-verification` 会冻结整个 runner：它表示 Codex 声称已经完整证明主猜想，或用严格核验的反例彻底否定主猜想，并已在同一回合完成十项检查。单个 Codex 回合自检通过仍最多是 `proof-draft`；老师仍须逐步复核，恢复或完成都不会自动把证据等级升级为 `human-verified`。

## 配置文件

全局配置位于 `runner.toml`：

- `model = ""`：使用 Codex CLI 当前默认模型；老师也可填写账户实际可用的 GPT/Codex 模型。
- `reasoning_effort = "xhigh"`：研究回合的推理强度。
- `attempt_timeout_minutes`：单回合最长时间，`0` 表示不限制。
- `max_wall_hours`：一次 `start` 的总运行时间，`0` 表示持续运行。
- `idle_seconds`：没有可运行题目时的重扫间隔。
- `web_search`：是否允许 Codex 使用内置网页搜索做文献核查。
- `max_consecutive_runtime_failures`：连续运行故障冻结阈值。
- `codex_path`：只有 `codex` 不在 `PATH` 时才需要填写绝对路径。

每题配置位于 `items/<slug>/config.toml`：

- `ready`：老师是否已确认题目可以运行。
- `enabled`：是否参与调度；与研究状态分开。
- `project_path`：可选；复用 `projects/` 下已有项目的工作区相对路径。留空时自动使用
  `projects/conjecture-<slug>/`。首次调度只补齐缺失骨架，不覆盖已有研究文件。
- `priority`：调度优先级。
- `max_attempts`：该题允许的累计 Codex 回合数。

## 证明安全与升级边界

队列提示词强制继承根目录 `AGENTS.md`：

- 公开问题也必须实际尝试证明或寻找反例，不能只写综述。
- 计算结果只能标为 `experimental`。
- 每条新数学推进必须先停止该回合的其他动作，执行与其强度相称的十项验证，再允许后续回合使用；最高先标为 `proof-draft`。
- 中间引理、部分结果或潜在新现象不冻结整个队列。它们经审查后可以继续 `pushing`；确需老师判断时设置 `needs-human-review`，只暂停当前题。
- 只有完整解决主猜想的候选证明，或严格反例彻底推翻主猜想，才设置 `solved-awaiting-human-verification` 并冻结整个队列。
- Codex 无权自动启动 Rethlas。它只能准备 Rethlas 问题稿并设置 `needs-escalation-approval`；老师明确批准某一次运行后，才按 `AGENTS.md` 的 Rethlas 流程执行。
- 队列不会调用网页端 Pro，不会自行宣称猜想已解决，也不会把结果升级为 `human-verified`。

## 日志与恢复

调度日志位于：

```text
agents/important-conjectures/history.jsonl
agents/important-conjectures/logs/<slug>/
```

每个 Codex 回合都有完整 JSONL 事件日志和最终答复。累计回合数、最近错误和最近日志路径保存在各项目的 `.queue-runtime.json`。

机器重启后直接再次运行 `./tools/conjecture_queue.sh start`。Runner 会从项目文件和状态继续，不依赖旧聊天会话。

## 当前限制

- 这是公平轮转队列，不是多 Agent 并行系统；同一时刻只运行一个 Codex 回合，更容易控制费用和文件冲突。
- LLM 自检不是形式证明。任何 `needs-human-review` 或 `solved-awaiting-human-verification` 结果仍需老师逐步复核；必要时再升级到 Rethlas 或 Lean。
- `stop` 是回合边界停止。如果必须立即终止，应由操作者进入 tmux 后发送中断，并检查项目文件是否留下半写状态。
