# Teacher Setup README — graph-geometry + Rethlas + optional Lean 4

本文档用于把本研究工作区交接给老师或老师的 AI agent。建议和根目录的 `AGENTS.md` 一起发送：

- `AGENTS.md`：研究规范、证明验证规则、目录约定、Rethlas 使用纪律。
- `TEACHER_SETUP_README.md`：如何在一台新机器上配置完整项目环境。

默认的 `./setup.sh --check` 只做本地配置和检查，不联网安装。只有老师明确许可后运行
`./setup.sh --bootstrap`，才会创建 Conda 环境并按需在工作区外安装 Rethlas。

如果交接目标只是“复现研究结构，不包含任何现有数据”，不要直接压缩整个工作区。应从工作区根目录运行：

```bash
./tools/export_teacher_framework.sh
```

脚本会在 `exports/` 中生成经过白名单筛选和敏感信息检查的 `.tar.gz`、同名 SHA-256 文件，以及包内文件清单。导师解压后的入口文档是 `README.md`。详细的包含/排除规则见 `TEACHER_FRAMEWORK_HANDOFF.md`。

无数据交接包还提供统一入口：

```bash
./setup.sh --check
```

导师也可以把 `SETUP_AI_PROMPT.md` 直接交给自己的 AI。AI 应先完成无联网检查并展示
`SETUP_REPORT.md`，取得导师对联网安装的明确许可后，才运行 `./setup.sh --bootstrap`。

**Rethlas 始终位于 graph-geometry 工作区外部。** 默认是解压目录的兄弟目录 `../Rethlas`。
`setup.sh` 会拒绝把 `RETHLAS_ROOT` 指向工作区内部。普通 Codex 队列不依赖 Rethlas；导师也可以运行
`./setup.sh --bootstrap --without-rethlas`。

## 0. 可按老师需求修改的部分

本文档里的路径和项目名是推荐示例，不是强制要求。老师可以按自己的机器、课题组目录、项目命名习惯修改：

- 工作区目录名，例如不叫 `graph-geometry` 也可以。
- 上层目录，例如不放在 `__RESEARCH_ROOT__/` 也可以。
- `AGENTS.md` 中的研究规范、证据等级、Rethlas 交接流程和目录约定。
- Codex/Rethlas 的模型名、推理强度、最大迭代次数和 tmux session 名。

需要保持一致的只有三件事：

1. 老师的 AI agent 能读到修改后的 `AGENTS.md`。
2. `tools/rethlas/*.sh` 中使用的工作区路径与实际路径一致。
3. 如果 Rethlas 不在默认位置，运行前设置 `RETHLAS_ROOT=/path/to/Rethlas`。

## 1. 总体布局

推荐目录布局如下，只是一个方便复现的例子：

```text
__RESEARCH_ROOT__/
├── graph-geometry/        # 本研究工作区
└── Rethlas/               # 外部 Rethlas 仓库，不放在 graph-geometry 里面
```

本工作区根目录：

```text
__WORKSPACE_ROOT__
```

Rethlas 默认路径：

```text
__RETHLAS_ROOT__
```

如果老师使用不同路径，需要在运行时设置：

```bash
export RETHLAS_ROOT=/path/to/Rethlas
```

下文为了简洁仍使用 `__WORKSPACE_ROOT__` 和 `__RETHLAS_ROOT__`。如果老师使用自己的目录，把命令里的这两个路径替换成实际路径即可。

## 2. graph-geometry 工作区

克隆或复制本工作区后，进入根目录：

```bash
cd __WORKSPACE_ROOT__
```

老师的 AI agent 应先读取：

```text
AGENTS.md
TEACHER_SETUP_README.md
```

总环境配置看本文件；具体项目操作建议放到各项目自己的项目级 README。当前项目的项目级交接文件是：

```text
projects/example-project/TEACHER_PROJECT_README.md
```

上面只是原工作区的项目级示例；无数据交接包不会包含该项目。老师投放自己的猜想后，
队列会在首次实际调度时创建新的 `projects/conjecture-<slug>/`。

老师日常操作可以主要在项目目录内完成：

```bash
cd __WORKSPACE_ROOT__/projects/example-project
```

重要目录：

```text
projects/                         # 每个研究项目一个子目录
projects/<project>/rethlas/        # 本项目交给 Rethlas 的问题、结果、运行记录
tools/rethlas/                     # graph-geometry 对 Rethlas 的包装脚本
templates/rethlas-problem.md       # 新 Rethlas 问题模板
```

当前重点项目示例：

```text
projects/example-project/
```

该项目中 Rethlas 相关材料位于：

```text
projects/example-project/rethlas/problems/
projects/example-project/rethlas/results/
projects/example-project/rethlas/runs/
```

## 3. Python 环境

本工作区普通实验默认使用 conda 环境：

```bash
conda create -n graphlab python=3.11 -y
conda activate graphlab
```

然后按具体项目的 `README.md` 或脚本报错安装所需依赖。例如 SAT 实验通常可能需要 `python-sat` 等包。

不要把 API key 或私密配置写入跟踪文件；不要修改 `.env` 文件。

## 4. 参考资料放在哪里

建议有固定规则，但老师可以按自己的项目习惯调整。总规则如下；具体项目可以在自己的 `TEACHER_PROJECT_README.md` 里再细化：

```text
projects/<项目名>/references.md                 # 本项目文献索引和阅读记录
projects/<项目名>/notes/                         # 本项目证明草稿、阅读笔记、计算说明
projects/<项目名>/rethlas/problems/<问题名>.refs/ # 某个 Rethlas 问题专用参考资料
shared/references/                               # 多个项目共享的总文献库
```

如果老师给的是“整个项目都要用”的论文、讲义、笔记或链接，优先放到：

```text
projects/<项目名>/references.md
projects/<项目名>/notes/
```

如果老师给的是“只给 Rethlas 解某个具体问题用”的材料，放到对应问题的 `.refs/` 目录：

```text
projects/<项目名>/rethlas/problems/<问题名>.refs/
```

Rethlas 会把这个目录同步到外部仓库的 generation agent，并在运行时优先读取。参考资料格式优先级：

```text
Markdown / LaTeX / txt  >  PDF
```

PDF 也可以放，但机器上最好安装 `pdftotext`，Rethlas 运行脚本会把 PDF 抽取成文本再读。

如果老师临时把参考资料发给 AI agent，而没有指定位置，建议 agent 先判断用途：

- 项目长期文献：保存到 `projects/<项目名>/references.md`，必要时把原文或摘录放到 `projects/<项目名>/notes/`。
- Rethlas 单题上下文：保存到 `projects/<项目名>/rethlas/problems/<问题名>.refs/`。
- 多项目共用资料：保存到 `shared/references/`，并在项目的 `references.md` 里加链接。

不建议把大量参考资料散放在工作区根目录。若老师另有目录习惯，可以在修改后的 `AGENTS.md` 中写明，并让 AI agent 按老师的新规则执行。

## 5. 安装 Codex CLI

这里的“推理证明 AI”主要不是一个需要下载到本地的模型权重，而是两层工具：

```text
Codex CLI        # 调用 OpenAI 模型执行推理、写证明、续跑 session
Rethlas          # proof-generation 和 proof-verification 的 agent 框架
```

Rethlas 依赖 Codex CLI。老师机器上需要先有 Node/npm，然后安装 Codex CLI：

```bash
npm install -g @openai/codex
codex --version
```

首次使用时按 Codex CLI 的登录流程完成认证。认证文件不应提交到本仓库。

如果老师使用的 AI 平台或模型配置不同，需要在 Rethlas 的 `.codex/config.toml` 或运行脚本环境变量中调整模型名。当前外部 Rethlas 仓库中相关位置通常是：

```text
__RETHLAS_ROOT__/agents/generation/.codex/config.toml
__RETHLAS_ROOT__/agents/verification/.codex/config.toml
__RETHLAS_ROOT__/agents/generation/tests/run_example.sh
```

常用运行环境变量：

```bash
MODEL=<model-name>
REASONING_EFFORT=xhigh
MAX_ITERATIONS=6
```

### 5.1 重要猜想 Codex 长跑队列

老师没有 Claude Code 也可以使用本工作区的新队列；日常 worker 只有 Codex。完整说明见：

```text
problems/important-conjectures/README.md
```

最短流程：

```bash
./tools/conjecture_queue.sh add <slug> "猜想标题"
# 填写 problems/important-conjectures/items/<slug>/problem.md
# 在同目录 config.toml 中选择 search_contract，并设置 ready = true
./tools/conjecture_queue.sh doctor
./tools/conjecture_queue.sh run --dry-run
./tools/conjecture_queue.sh start
```

查看和安全停止：

```bash
./tools/conjecture_queue.sh status
tmux attach -t important_conjectures
./tools/conjecture_queue.sh stop
```

Runner 每次调用一个有边界的 `codex exec` 研究回合，把长期状态写入
`projects/conjecture-<slug>/`，并在 `verification-ledger.md` 逐条记录推进与严格审查，然后公平
轮转到下一题。`needs-human-review` 只暂停当前题；只有完整解决主猜想的候选证明或严格反例才进入
`solved-awaiting-human-verification`，使整个队列退出并等待老师复核。Rethlas 仍然是逐次人工
批准的升级通道，不会被队列自动启动。

新条目默认 `search_contract = "affirmative-proof"`，用于防止肯定证明搜索过早终止；
同时默认 `stagnation_rounds_before_blocked = 0`，不因停滞自动停止。反例型任务应改成
`counterexample`。`runner.toml` 的 `web_search = false` 用于离线原创
阶段，`true` 用于联网文献核查。两阶段结果的来源和路线暴露必须分别记录。

## 6. 安装外部 Rethlas

Rethlas 框架本身需要从 GitHub 克隆。若老师已有自己的 fork，可以替换成自己的仓库地址。

在 `__RESEARCH_ROOT__` 下克隆 Rethlas：

```bash
cd __RESEARCH_ROOT__
git clone https://github.com/frenzymath/Rethlas.git
cd Rethlas
```

Rethlas 的两个核心部分：

```text
agents/verification/      # verifier HTTP service
agents/generation/        # generation agent
```

### 6.1 配置 verification agent

```bash
cd __RETHLAS_ROOT__/agents/verification
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

也可以用 `uv`：

```bash
cd __RETHLAS_ROOT__/agents/verification
uv venv
uv pip install -r requirements.txt
```

### 6.2 配置 generation agent

```bash
cd __RETHLAS_ROOT__/agents/generation
python3 -m venv .venv
source .venv/bin/activate
pip install -r mcp/requirements.txt
```

如果运行含 PDF 参考资料的问题，建议安装 `pdftotext`。Ubuntu/Debian：

```bash
sudo apt-get install poppler-utils
```

## 7. 启动 Rethlas verifier

Rethlas 长跑任务建议用 tmux。先启动 verifier：

```bash
tmux new-session -d -s rethlas_verifier \
  'cd __RETHLAS_ROOT__/agents/verification && .venv/bin/uvicorn api.server:app --host 0.0.0.0 --port 8091'
```

确认 verifier 可访问：

```bash
curl -sf http://127.0.0.1:8091/health
```

查看 verifier 实时终端：

```bash
tmux attach -t rethlas_verifier
```

退出查看但不中断运行：按 `Ctrl-b`，然后按 `d`。

## 8. 用 graph-geometry 包装脚本运行 Rethlas

所有命令从工作区根目录运行：

```bash
cd __WORKSPACE_ROOT__
```

### 8.1 新建一个 Rethlas 问题

```bash
./tools/rethlas/init_project.sh <项目名> <问题名>
```

例：

```bash
./tools/rethlas/init_project.sh example-project new_problem_name
```

这会创建：

```text
projects/<项目名>/rethlas/problems/<问题名>.md
projects/<项目名>/rethlas/problems/<问题名>.refs/
projects/<项目名>/rethlas/results/
projects/<项目名>/rethlas/runs/
```

把正式问题写入 `<问题名>.md`，把参考材料放进 `<问题名>.refs/`。参考材料优先用 Markdown、LaTeX、纯文本；PDF 可以放入，但需要 `pdftotext`。

### 8.2 后台运行 Rethlas

确认 `http://127.0.0.1:8091/health` 正常后：

```bash
MAX_ITERATIONS=6 ./tools/rethlas/run_problem_tmux.sh <项目名> <问题名> <session名>
```

例：

```bash
MAX_ITERATIONS=6 ./tools/rethlas/run_problem_tmux.sh example-project divisible_blowup_embedding rethlas_divisible_blowup
```

查看 generation：

```bash
tmux attach -t rethlas_divisible_blowup
```

查看 verifier：

```bash
tmux attach -t rethlas_verifier
```

退出查看但不中断运行：按 `Ctrl-b`，然后按 `d`。

### 8.3 运行结果同步位置

包装脚本会把 Rethlas 外部仓库里的产物同步回本项目：

```text
projects/<项目名>/rethlas/results/<问题名>/
projects/<项目名>/rethlas/runs/<问题名>/
```

关键文件：

```text
blueprint.md             # proof-draft，只是候选证明
blueprint_verified.md    # agent-verified，只代表 Rethlas verifier 通过
run-info.txt             # problem_id、Rethlas 路径、同步时间
logs/                    # Codex 迭代日志
memory/                  # Rethlas 记忆和中间材料
downloads/               # 下载材料
```

注意：`blueprint_verified.md` 不能自动升级为 `human-verified`。根据 `AGENTS.md`，新证明出现后必须停止下游写作，先做独立验证并交给人类审查。

## 9. 已有结果的重复运行问题

如果外部 Rethlas 的 generation 目录下已经有：

```text
agents/generation/results/graph-geometry/<项目名>/<问题名>/blueprint_verified.md
```

包装脚本会拒绝用同名问题重跑，因为 Rethlas 会直接停止。若问题内容发生变化，请使用新问题名，例如：

```text
<问题名>_v2
```

## 10. 可选：浏览 Rethlas 结果网站

Rethlas generation agent 自带 Zola 结果网站。安装 Zola 后：

```bash
cd __RETHLAS_ROOT__/agents/generation
./site/serve.sh
```

浏览器打开：

```text
http://localhost:3264
```

## 11. 可选：Lean 4 配置

当前工作区没有统一的全局 Lean 项目。若老师后续需要 Lean 4 形式化，建议每个研究项目单独建 Lean 子项目：

```text
projects/<项目名>/lean/
├── lean-toolchain
├── lakefile.lean
├── <PackageName>/
└── <PackageName>.lean
```

### 11.1 安装 elan

```bash
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
source "$HOME/.elan/env"
lean --version
lake --version
```

### 11.2 新建 Lean 4 项目

例：

```bash
cd __WORKSPACE_ROOT__/projects/example-project
mkdir -p lean
cd lean
lake init IntersectingSubsetRamsey math
```

`lake init ... math` 会生成一个 mathlib 项目。之后先构建一次：

```bash
lake update
lake build
```

如果只需要纯 Lean 4、暂时不用 mathlib，可以用：

```bash
lake init IntersectingSubsetRamsey
lake build
```

### 11.3 Lean 使用纪律

- 不假设全局 Lean 版本；每个 Lean 项目保留自己的 `lean-toolchain`。
- 形式化尝试放在 `projects/<项目名>/lean/`。
- 自然语言证明和 Lean 形式化要互相引用文件路径。
- 只有 `lake build` 通过的结论才可标记为 `formalized`。

## 12. 交接给老师时建议附带的文件

最低限度：

```text
AGENTS.md
TEACHER_SETUP_README.md
projects/<项目名>/README.md
projects/<项目名>/progress.md
projects/<项目名>/research-tree.md
projects/<项目名>/proof-map.md
projects/<项目名>/rethlas/problems/
projects/<项目名>/rethlas/results/
projects/<项目名>/rethlas/runs/
```

若要完整复现实验，还应附带：

```text
projects/<项目名>/code/
projects/<项目名>/data/
projects/<项目名>/notes/
projects/<项目名>/references.md
```

外部 Rethlas 仓库不建议直接塞进本工作区；让老师按第 6 节单独 clone 更清晰。

如果老师准备深度接管项目，建议让老师先复制一份 `AGENTS.md` 再修改，保留原始版本作对照。尤其是证明冻结规则、证据等级、Rethlas 输出不能自动视为人类验证这些部分，最好不要删掉，只按老师自己的流程改写。

## 13. 快速健康检查

在老师机器上配置完成后，可运行：

```bash
cd __WORKSPACE_ROOT__
test -f AGENTS.md
test -x tools/rethlas/init_project.sh
test -x tools/rethlas/run_problem.sh
test -x tools/rethlas/run_problem_tmux.sh
test -d __RETHLAS_ROOT__/agents/generation
test -d __RETHLAS_ROOT__/agents/verification
codex --version
curl -sf http://127.0.0.1:8091/health
```

若上述命令都通过，说明基础配置已经可用。

## 14. 证据等级提醒

Rethlas 输出的 `blueprint_verified.md` 最高只能视为：

```text
agent-verified
```

它不是人类确认的定理。准备把结果写入摘要、主定理、结论或对外传播前，必须由人类逐步复核并明确升级为：

```text
human-verified
```

若 Lean 形式化通过 `lake build`，可标记为：

```text
formalized
```
