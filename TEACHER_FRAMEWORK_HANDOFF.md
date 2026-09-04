# Graph Geometry 研究框架交接包

本压缩包只包含研究框架，不包含原作者的研究数据、项目内容、论文、PDF、运行日志、环境、Git 历史或认证信息。日常研究 Agent 使用 Codex；Rethlas 是可选且必须逐次人工批准的升级通道。

因为导师环境使用 GPT/Codex，本包有意不包含 Danus、Claude Code 或 Copilot 专用说明；对应规则已经统一写入 `AGENTS.md` 和本包的 Codex 配置说明，避免同时维护互相冲突的入口。

## 1. 包内包含什么

- `AGENTS.md`：研究纪律、证明验证、证据等级和重要猜想队列规则。
- `TEACHER_SETUP_README.md`：Codex、外置 Rethlas、可选 Lean 和工作区的完整手工配置说明。
- `RETHLAS使用教程.md`：Rethlas 问题准备、运行、结果同步和验证纪律。
- `SETUP_AI_PROMPT.md`：导师可直接交给 AI 的配置任务书。
- `TEACHER_QUEUE_QUICKSTART.md`：导师日常轮询只需照抄的一页说明。
- `setup.sh`：统一的检查与可选 bootstrap 入口。
- `queue.sh`：根目录下的极简队列入口。
- `problems/important-conjectures/`：导师投放猜想的入口和队列配置。
- `templates/`：问题、项目记录、证明图和 Rethlas 问题模板。
- `tools/conjecture_queue.*`：Codex 长跑队列。
- `CURRENT_STATE.md` 模板与 `state-audit`：用短状态入口恢复长项目，避免每轮重读全部历史。
- `tools/project_state.py`：为队列外的普通项目初始化并检查同一种短状态入口。
- `tools/workspace_hygiene.py`：默认只读地报告日志、LaTeX 中间文件和环境占用；清理必须显式 `--apply`。
- `tools/rethlas/`：可选的 Rethlas 包装脚本。
- `tools/configure_teacher_workspace.sh`：把占位路径替换为导师机器上的实际路径。
- `tools/export_teacher_framework.sh`：导师以后可再次生成同样的无数据白名单交接包。
- `tools/verify_teacher_framework.sh`：检查结构、空数据目录、清单和常见秘密模式。
- 空的 `projects/`、`archive/`、`shared/`、`library/`、`index/`、`agents/` 和 `environments/` 目录骨架。

压缩包明确不包含：

- 原作者的 `projects/`、`archive/`、`shared/`、`library/` 或 `index/` 内容；
- `.git/`、`.codex/`、`.claude/`、`.agents/`、`.vscode/`；
- Conda/TeX/Julia 环境、缓存、日志、模型会话；
- `.env`、API key、登录凭证、token、cookie；
- PDF、压缩包、数据集、实验结果和论文源文件。

## 2. 解压和校验

在 Linux 机器上，把压缩包和同名 `.sha256` 文件放在同一目录：

```bash
# Linux
sha256sum -c graph-geometry-framework-YYYYMMDD-HHMMSS.tar.gz.sha256

# macOS
shasum -a 256 -c graph-geometry-framework-YYYYMMDD-HHMMSS.tar.gz.sha256

tar -xzf graph-geometry-framework-YYYYMMDD-HHMMSS.tar.gz
cd graph-geometry-framework
```

最简单的做法是让导师机器上的 AI 先读取 `SETUP_AI_PROMPT.md`。也可以直接做本地检查：

```bash
./setup.sh --check
```

## 3. 配置导师机器路径

`setup.sh --check` 会先验证原始分发包，然后自动调用路径配置工具并生成 `SETUP_REPORT.md`。如需手工指定路径，也可以运行：

```bash
CONDA_ROOT=/导师的/miniforge3 \
RETHLAS_ROOT=/导师的/Rethlas \
./tools/configure_teacher_workspace.sh
```

如果暂时不用 Rethlas，可以省略 `RETHLAS_ROOT`。配置脚本只替换本包中的路径占位符，不安装软件、不登录账户、不写入密钥。

配置后检查：

```bash
./tools/verify_teacher_framework.sh
```

在导师明确允许联网下载和创建环境后，AI 可以运行：

```bash
./setup.sh --bootstrap
```

这会创建 `graphlab`，并把干净 Rethlas 克隆到工作区外部的兄弟目录。只需要普通 Codex 队列时使用：

```bash
./setup.sh --bootstrap --without-rethlas
```

## 4. 安装本机工具

建议准备：

- Linux、Bash、Git、tmux；
- Conda/Miniforge；
- `graphlab` Python 3.11 环境；
- Codex CLI，并由导师使用自己的账户完成登录；
- 可选：单独克隆的 Rethlas 和它自己的环境。

Codex 的安装与登录方式可能更新，应以 [OpenAI Codex 官方文档](https://developers.openai.com/codex/cli/) 为准。不要复制原作者的 Codex 配置目录或登录文件。

建立 Python 环境：

```bash
conda create -n graphlab python=3.11 -y
conda activate graphlab
```

确认基础工具：

```bash
codex --version
tmux -V
./tools/conjecture_queue.sh doctor
./tools/conjecture_queue.sh state-audit
./tools/workspace_hygiene.py report
```

## 5. 初始化导师自己的 Git 仓库

压缩包不包含原作者的 Git 历史。导师检查文件后，可以建立全新的私人仓库：

```bash
git init
git add .
git status --short
git commit -m "Initialize graph geometry research framework"
```

是否提交由导师决定。不要把 Codex 登录信息、`.env` 或后续私密数据加入 Git。

## 6. 投放第一道重要猜想

```bash
./tools/conjecture_queue.sh add first-conjecture "第一道猜想的标题"
```

导师填写：

```text
problems/important-conjectures/items/first-conjecture/problem.md
```

把同目录 `config.toml` 中的 `ready = false` 改为 `ready = true`，然后：

```bash
./tools/conjecture_queue.sh run --dry-run
./tools/conjecture_queue.sh start
```

第一次实际调度该题时，队列会创建独立的 `projects/conjecture-first-conjecture/`，并按 `AGENTS.md` 维护进度、路线图、证明依赖图和验证台账。

## 7. Rethlas 边界

Rethlas 不在本压缩包内，也不是运行 Codex 队列的前提。只有导师明确批准某个精确证明缺口后，才单独安装并调用 Rethlas。任何 Rethlas 输出最高先视为 `agent-verified`，不能自动升级为 `human-verified`。

推荐布局固定为：

```text
<某个上层目录>/
├── graph-geometry-framework/   # 本压缩包解压目录
└── Rethlas/                    # 独立克隆，绝不放入上面的工作区
```
