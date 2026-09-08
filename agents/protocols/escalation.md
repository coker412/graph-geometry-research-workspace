# 推理升级

Rethlas、网页端 Pro 逐次明确授权；模型较强不改变证据要求。Codex 同一精确 gap 两次无法关闭时，先检索已有项目正文、当前状态指向的历史/ledger/proof map 和 Rethlas 结果，确认现有材料未包含论证。

准备无歧义交接稿：正式陈述、定义归一化、已核验结果、最小 gap、必要失败路线、目标、成本和验证要求。必须包含：

> 直接尝试证明或构造反例；不得以问题可能公开为理由停止；得到候选结果后严格检查。

只准备材料并请求本次运行许可；批准 Rethlas 后读取 RETHLAS使用教程.md。网页端 Pro 同样须批准后提交。结果回流独立审查，登记原始响应与哈希，更新实际受影响的 progress/ledger/proof-map/research-tree，不能凭模型强度认证。

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
