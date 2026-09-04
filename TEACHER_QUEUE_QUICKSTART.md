# 导师重要猜想轮询：一页操作说明

本说明适用于 macOS 或 Linux。所有命令都在解压后的工作区根目录执行。

## 第一次配置

把下面这句话直接发给工作区里的 AI：

> 请先读取 AGENTS.md、SETUP_AI_PROMPT.md 和 TEACHER_QUEUE_QUICKSTART.md。只配置研究环境，不要开始研究。先运行 ./setup.sh --check，把检查结果告诉我；任何联网安装都先征得我的同意。

导师本人完成 Codex 登录。配置完成后运行：

```bash
./queue.sh check
```

从旧版框架升级、已经存在研究项目时，再运行：

```bash
./queue.sh state-init
./queue.sh state-audit
```

这只补建下一回合使用的短状态入口，不覆盖证明、进度或验证台账。

## 加入一道猜想

也可以直接对 AI 说：

> 请把下面这道猜想加入重要猜想队列。保持原文，不要自行改变数学含义；先建立条目并让我检查，不要立即启动队列。题目如下：……

若手工操作：

```bash
./queue.sh add hadwiger "Hadwiger conjecture"
```

然后填写：

```text
problems/important-conjectures/items/hadwiger/problem.md
```

把同目录 `config.toml` 中的 `ready = false` 改为 `ready = true`。

新建题目默认使用 `search_contract = "affirmative-proof"`：长跑在搜索调度上假定完整
肯定证明存在，不因几轮失败停止，但这不会提高证据等级；默认的
`stagnation_rounds_before_blocked = 0` 表示不因停滞自动终止。若目标本来就是构造反例，改成
`search_contract = "counterexample"`。希望先做不受文献路线影响的原创搜索时，把
`problems/important-conjectures/runner.toml` 中的 `web_search` 设为 `false`；完成若干
离线回合并保存方法族快照后，再改回 `true` 做联网核查。

## 开始长时间轮询

最简单的 AI 指令：

> 请先运行 ./queue.sh check。如果检查通过，就运行 ./queue.sh start，在后台开始重要猜想轮询。不要启动 Rethlas。最后只告诉我是否启动成功，以及怎样查看和停止。

手工命令：

```bash
./queue.sh check
./queue.sh start
```

`start` 使用 tmux，关闭终端或关闭 AI 对话后仍可继续。macOS 可用 Homebrew 安装 tmux；Linux 用系统包管理器安装。

## 日常只记这三个命令

```bash
./queue.sh status   # 看状态
./queue.sh watch    # 看实时输出；Ctrl-b 后按 d 退出查看
./queue.sh stop     # 当前研究回合结束后安全停止
```

也可以分别对 AI 说：

> 请检查重要猜想队列状态，只总结各题进度和需要我处理的事项，不要改变状态。

> 请安全停止重要猜想队列，不要强杀正在写文件的 Codex 回合。

## 不安装 tmux 时

可以运行：

```bash
./queue.sh once
```

它只推进一个 Codex 回合，适合试用。也可以运行 `./queue.sh run` 前台持续轮询，但终端必须一直打开；关闭终端、断开 SSH 或退出进程就会停止。因此真正的夜间或多日轮询仍推荐 tmux。

tmux 不能让电脑在睡眠或关机时继续计算。Mac 合盖休眠后任务会暂停；重新开机后运行 `./queue.sh start`，队列会从磁盘记录继续。

## 必须由导师处理的状态

- `needs-human-review`：只暂停这一题；阅读该项目的 `progress.md` 和 `verification-ledger.md`。
- `needs-human-input`：题目有实质歧义，需要导师回答。
- `needs-escalation-approval`：Codex 建议升级到 Rethlas，但尚未运行；是否批准由导师决定。
- `solved-awaiting-human-verification`：出现完整候选证明或决定性反例，整个队列冻结，等待导师严格复核。

Rethlas 永远不会由普通轮询自动启动。

## 空间占用

```bash
./queue.sh hygiene report
```

该命令只报告，不清理。LaTeX 中间文件和旧队列日志的治理命令默认也只是 dry run；只有导师
明确要求并加入 `--apply` 才执行。项目环境不会被自动删除。
