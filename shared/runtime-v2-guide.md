# 数学研究运行时 V2

普通回合使用 `high` 推进数学，runner 负责准备上下文包与整理结构化结果。
`CURRENT_STATE + proof-map + verification-ledger + progress` 继续保存长期记忆。

## 阶段与配置

`problems/important-conjectures/runner.toml` 设置默认 `phase = "research"`。
单题 `config.toml` 可用 `phase` 覆盖；阶段不会由模型自行升级。

| phase | effort | 加载协议 |
| --- | --- | --- |
| triage | medium | explore |
| research | high | explore |
| experiment | medium | computation |
| literature | medium | literature-check |
| audit | high | proof-audit |
| critical-audit | xhigh | proof-audit |
| stuck-escalation | xhigh | explore |

普通阶段配置 xhigh 会报错。literature 必须同时明确选择 connected；切换阶段不会自行打开网络。
`model = ""` 继续使用 CLI 默认模型，记录为未解析，不能据此推算某型号的价格。
当前 CLI 为 0.153.0，仍由本机管理升级。推理档位是否受支持取决于所选模型。

`runtime_version = 2` 为普通回合的默认路径。设为 `1` 可使用兼容提示词。
`mixed-isolated` 保持已配置模式，使用兼容收尾和原有 bubblewrap 隔离；三个调用依次承担
离线探索、联网核查、汇合审计，后两者使用 medium、high。它尚未接入 V2 状态 writer。

## 上下文包

每个普通回合创建：

```text
projects/<project>/.runtime/rounds/<round-id>/
  RESEARCH_PACKET.md
  PACKET.json
  BASELINE.json
  ROUND_RESULT.json
  COMMIT.json
  APPLIED.json
  before/
  after/
```

包包含规则核心、当前阶段协议、正式题目、短状态、指定证据片段与本轮评估要求。
不自动遍历旧 progress、proof-map 或整个 notes。首轮没有片段清单时，Agent 从短状态的
精确指针选择必要材料，并在回合结果中给下一轮返回片段。引用了外部依赖时仍须按协议
加载相应文献或认证规则，包不能替代缺失的证明前提。

证据清单位于项目 `.runtime/evidence.json`，例如：

```json
{
  "evidence": [{
    "file": "notes/lemma.md",
    "start": 12,
    "end": 40,
    "sha256": "此处填写整个文件的64位SHA256",
    "purpose": "当前缺口所需的饱和估计",
    "source": "internal-offline"
  }]
}
```

路径必须在项目内，禁止 symlink 和目录逃逸。范围越界、哈希过期、离线包引入非内部
来源、片段超预算时拒绝调用模型。哈希仅检测内容变化，不能核验来源标签或数学正确性。
行号漂移需重新选片段并核对哈希，不能自动接受旧引用。

短状态目标 6 KiB，超过 8 KiB 提醒，V2 新写入最多 12 KiB/300 行。旧摘要保留
32 KiB/300 行检查上限；自动 writer 保留原问题范围、既有数学状态和证据上限。
若这些部分需要精简或纠正，应先做显式保守迁移，不能让程序猜测或截掉证明条件。

`context_budget` 控制初始包的目标、硬上限、片段数量及单片段大小。本实现没有安装
专用 tokenizer，使用 UTF-8 字节数作为保守 token 上界：默认目标 12000，硬上限 48000，
最多 8 个片段，每片段上限 12000。PACKET.json 分项记录字节数、哈希与提醒。
这些数值不是实际计费 tokens，也不限制 CLI 的系统提示、工具定义和之后的工具返回。
追加读取仍靠阶段协议约束，实际消耗以事件 usage 为准。

## 回合结果与认证

格式见 [ROUND_RESULT 协议](../agents/protocols/round-result.md)。研究 Agent 保存证明、
检查记录、计算及 JSON 字段，runner 校验后追加 progress、登记新 claim，并更新短状态
与下一轮片段清单。gap 变化只作为待证据核对的报告追加到 proof-map，程序不重写证明 DAG。
方法族结构变更仍写在研究笔记里，由显式复核更新 ideas/research-tree。

自动 writer 只接受新 ID，证据等级最高 proof-draft；既有结论的升级、降级与认证结果回流
需要显式审查和状态协调。完整候选必须带十项检查及报告的证据哈希，随后触发全局冻结。
JSON 检查通过不等于数学认证，候选仍须研究者复核。未完成认证的候选用 needs-human-review。

writer 写入前检查共享文件是否偏离开工哈希，并保存前后快照及提交日志。重复应用同一
已完成结果不会重复追加；已应用结果遭改写会拒绝。多文件写入遇中断时保留 COMMIT.json，
若没有 APPLIED.json，后续回合停止并报告待恢复。按日志逐文件核对 before/after 哈希，
确认后选择恢复或完成；程序不会自动覆盖中断后研究者的修改。备份仅用于恢复状态文件，
证明和实验产物仍保存在原目录。

## 查看与验证

```bash
./queue.sh packet --slug <slug>           # 只读大小与哈希预览
./queue.sh packet --slug <slug> --content # 输出包正文
./queue.sh run --dry-run --slug <slug>    # 命令预演，不启动模型
./queue.sh usage                         # 历史回合汇总
./queue.sh usage --slug <slug> --json
./queue.sh state-audit
conda run -n graphlab python -m unittest discover -s tools/tests -v
```

packet 预览使用当前题目源，不创建输入快照，也不含实际启动时的进展评估指令；实际包在
调用前重新编译并执行完整预算检查。未创建项目、混合模式或超限包会明确报错。

每轮 telemetry 记录请求模型、effort、phase、耗时、包大小、各信息分支 token 用量、工具
调用计数及结果类别。input、cached input、output 分开统计，缓存量是输入的子集，不再相加。
reasoning tokens 只在 CLI 上报时记录；文件读取数量没有可靠事件支持，保留 null。
历史缺失或失败调用缺失 usage 均为未知，部分分支统计标记 incomplete，不把缺失当零。
工具调用只计算事件可见的工具，不代表 shell 命令内全部操作或子 Agent 的完整用量。
进展类别是研究者自报；是否真正缩小核心缺口仍以原有独立进展评估为准。

CLI 的 JSONL usage 和配置接口已核对
[官方非交互文档](https://learn.chatgpt.com/docs/non-interactive-mode)与
[官方配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)。
本次仅验证本地实现与模拟回合，尚无真实模型回合的质量、耗时或额度节省对照。
