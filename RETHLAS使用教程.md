# Rethlas 数学证明 Agent 使用教程

本教程面向第一次使用命令行和数学 agent 的用户。日常工作只需要在
`__WORKSPACE_ROOT__` 中进行；`__RETHLAS_ROOT__`
作为后台运行引擎。

## 一、它能做什么

Rethlas 包含两个 Codex agent：

1. **Generation agent（生成 agent）**：读取一个 Markdown 数学问题，搜索相关资料，
   尝试例子和反例，拆分子目标，生成证明草稿。
2. **Verification agent（验证 agent）**：逐步检查完整证明，返回
   `correct` 或 `wrong`，并列出错误、缺口和修复建议。

生成 agent 只有在验证 agent 判定没有错误、没有缺口后，才会生成
`blueprint_verified.md`。没有这个文件，不能把结果当作已验证证明。

## 二、我们采用的文件位置

每个研究项目使用以下结构：

```text
projects/<项目名>/rethlas/
├── problems/
│   ├── <问题名>.md
│   └── <问题名>.refs/       # 可选参考资料
├── results/
│   └── <问题名>/
│       ├── blueprint.md
│       └── blueprint_verified.md
└── runs/
    └── <问题名>/
        ├── memory/
        ├── logs/
        ├── downloads/
        └── run-info.txt
```

- `problems/` 是我们维护的正式输入。
- `results/` 是容易阅读的证明草稿和已验证证明。
- `runs/` 是排错和追踪研究过程所需的详细记录。
- 运行脚本会临时把输入复制到 Rethlas，并在运行结束时把产物复制回来。

不要直接把日常研究材料只放在 Rethlas 仓库中，否则两个仓库会难以同步。

## 三、第一次使用前的检查

打开终端，执行：

```bash
cd __WORKSPACE_ROOT__
codex --version
```

如果能看到类似 `codex-cli 0.141.0`，说明 Codex CLI 已安装。还需要确认 Codex
已经登录：

```bash
codex login
```

当前机器已经有：

- conda 环境 `graphlab`
- Zola
- `pdftotext`
- Rethlas 自带的 Python 虚拟环境

如果换到另一台机器，请按照
`__RETHLAS_ROOT__/README.md` 安装 Codex 和两个 agent 的 Python 依赖。

## 四、创建一个问题

以下示例使用项目 `example-project`，问题名为 `example-problem`。

### 第 1 步：创建目录和问题模板

```bash
cd __WORKSPACE_ROOT__
./tools/rethlas/init_project.sh example-project example-problem
```

脚本会创建：

```text
projects/example-project/rethlas/problems/example-problem.md
projects/example-project/rethlas/problems/example-problem.refs/
```

### 第 2 步：填写问题

编辑：

```text
projects/example-project/rethlas/problems/example-problem.md
```

至少要写清楚：

1. 完整问题陈述；
2. 每个符号和非标准定义；
3. 图的类别，例如有限、简单、连通、加权；
4. 所有假设；
5. 要证明或反驳的完整结论。

问题陈述越精确，agent 误解问题的概率越低。不要只粘贴一条脱离上下文的公式。

### 第 3 步：加入参考资料（可选）

把只供该问题使用的资料放入：

```text
projects/example-project/rethlas/problems/example-problem.refs/
```

支持：

- `.md`
- `.tex`
- `.txt`
- `.pdf`

优先使用 Markdown、TeX 或纯文本。PDF 会由 `pdftotext` 自动提取文本，但复杂公式、
双栏排版和扫描版 PDF 可能提取不准确。私有笔记也可以放在这里；不要放 API 密钥。

## 五、启动验证服务

每次运行生成 agent 前，需要让验证服务在另一个终端持续运行。

推荐直接使用工作区启动脚本。它会解析 Codex CLI 的真实绝对路径，并同时检查
服务存活状态和 `CODEX_BIN` 配置：

```bash
cd __WORKSPACE_ROOT__
./tools/rethlas/start_verifier_tmux.sh
```

若脚本发现旧服务的 `/health` 虽然可访问，但内部没有可执行的
`CODEX_BIN`，先确认没有 generation 正在提交验证，再执行：

```bash
RESTART_STALE=1 ./tools/rethlas/start_verifier_tmux.sh
```

手工启动时也必须设置绝对路径，不能依赖可能随 VS Code 扩展升级而过期的
`PATH`：

```bash
cd __RETHLAS_ROOT__/agents/verification
source .venv/bin/activate
CODEX_BIN="$(command -v codex)" \
  uvicorn api.server:app --host 127.0.0.1 --port 8091
```

在另一个终端检查服务：

```bash
curl http://127.0.0.1:8091/health
```

正常结果是：

```json
{"status":"ok"}
```

停止服务时，在终端 A 按 `Ctrl+C`。

## 六、运行一个问题

打开“终端 B”：

```bash
cd __WORKSPACE_ROOT__
MAX_ITERATIONS=10 ./tools/rethlas/run_problem.sh example-project example-problem
```

参数含义：

- `example-project`：`projects/` 下的项目目录名；
- `example-problem`：问题文件名，不包含 `.md`；
- `MAX_ITERATIONS=10`：最多让同一个 Codex 会话继续 10 轮。

运行可能持续较长时间，也会使用模型额度。困难研究问题没有固定完成时间。

脚本退出时，即使没有证明成功，也会把已有产物同步回 `graph-geometry`。

## 七、怎么看结果

先检查：

```bash
ls projects/example-project/rethlas/results/example-problem
```

文件含义：

- `blueprint.md`：当前证明草稿，可能有错误或缺口；
- `blueprint_verified.md`：验证 agent 判定通过的完整证明。

严格标准是：

```text
存在 blueprint_verified.md 才表示 Rethlas 的自动验证流程通过。
```

即使自动验证通过，人类仍应按本工作区 `AGENTS.md` 的证明验证清单复核，尤其检查：

1. 隐含假设；
2. 定义是否一致；
3. 外部定理是否真的适用；
4. 是否存在循环论证；
5. 是否能构造反例。

如果没有通过，查看：

```text
projects/example-project/rethlas/runs/example-problem/memory/verification_reports.jsonl
projects/example-project/rethlas/runs/example-problem/logs/
projects/example-project/rethlas/runs/example-problem/memory/failed_paths.jsonl
```

其中：

- `verification_reports.jsonl` 保存验证结论和修复建议；
- `logs/` 保存每轮 Codex 的完整输出；
- `failed_paths.jsonl` 保存失败路线和具体障碍。

## 八、常见操作

### 增加迭代次数

```bash
MAX_ITERATIONS=20 ./tools/rethlas/run_problem.sh example-project example-problem
```

脚本会创建新的 Codex 会话，但会保留并继续使用同一问题的 memory 和已有草稿。

### 使用不同模型

```bash
MODEL=gpt-5.6-sol REASONING_EFFORT=xhigh \
  ./tools/rethlas/run_problem.sh example-project example-problem
```

模型名必须是当前 Codex 账户实际可用的模型。通常不需要手动指定，优先使用 Rethlas
包装脚本的默认值。目前 generation 与 verifier 的默认配置均为
`gpt-5.6-sol`、`xhigh`；困难证明可另行比较 `max`，但不要未经评测全局启用。

### 修改未完成的问题后重新运行

直接编辑 `projects/<项目名>/rethlas/problems/<问题名>.md`，然后再次执行
`run_problem.sh`。脚本会把新版问题复制给 Rethlas。

如果已经存在 `blueprint_verified.md`，或者问题的数学含义发生了重大变化，必须使用一个
新问题名，避免旧证明和旧 memory 被误用于新问题，例如从 `example-problem` 改为
`example-problem_v2`。

### 中途停止

在运行终端按 `Ctrl+C`。退出钩子仍会尽力同步已经产生的结果和日志。

## 九、常见错误

### `verification service not reachable`

原因：验证服务没有启动，或端口不是 `8091`。

处理：按照第五节启动服务，并用 `/health` 检查。

### `Problem file not found`

原因：项目名、问题名拼错，或还没有创建模板。

处理：

```bash
./tools/rethlas/init_project.sh <项目名> <问题名>
```

### `codex: command not found`

安装 Codex CLI：

```bash
npm install -g @openai/codex
```

然后运行 `codex login`。

### `/health` 正常，但 `/verify` 返回 HTTP 500

若 traceback 包含

```text
PermissionError: [Errno 13] Permission denied: 'codex'
```

说明 Uvicorn 本身还活着，但它继承的 `PATH` 中没有可执行的 Codex CLI。
`/health` 只检查 Web 服务存活，不会启动验证子进程，因此不能单独证明 verifier
可用。使用下面的命令重启并固定真实路径：

```bash
cd __WORKSPACE_ROOT__
RESTART_STALE=1 ./tools/rethlas/start_verifier_tmux.sh
```

### 达到最大轮数但没有 `blueprint_verified.md`

这不等于程序故障。通常表示：

- 证明仍有缺口；
- 问题本身可能是开放问题；
- 输入缺少定义或假设；
- 某条路线被反例否定；
- 需要更多参考文献或人工数学判断。

先读验证报告和失败路线，再决定是修改问题、补充资料、增加迭代，还是换研究方向。

### PDF 没有被正确读取

检查：

```bash
pdftotext -v
```

扫描版 PDF 需要 OCR；Rethlas 当前只自动调用 `pdftotext`，不自动做 OCR。

## 十、直接使用原始 Rethlas（高级）

本工作区的包装脚本已经覆盖日常使用。若需要调试原始仓库，可直接运行：

```bash
cd __RETHLAS_ROOT__/agents/generation
PROBLEM_FILE=data/example.md MAX_ITERATIONS=10 ./tests/run_example.sh
```

原始输出位于：

```text
__RETHLAS_ROOT__/agents/generation/results/
__RETHLAS_ROOT__/agents/generation/memory/
__RETHLAS_ROOT__/agents/generation/logs/
```

验证 agent 的原始运行记录位于：

```text
__RETHLAS_ROOT__/agents/verification/results/
__RETHLAS_ROOT__/agents/verification/memory/
```

日常研究不建议直接维护这些路径中的题目；使用本教程的包装脚本可以保证正式输入和最终
产物都回到 `graph-geometry`。

## 十一、推荐工作流程

1. 在项目的 `rethlas/problems/` 中写清问题。
2. 把相关论文和笔记放入对应 `.refs/`。
3. 启动验证服务。
4. 用 `run_problem.sh` 运行。
5. 检查 `blueprint.md`、验证报告和失败路线。
6. 若出现新证明，立即停止下游论文修改，按 `AGENTS.md` 逐项人工验证。
7. 人工确认后，再把可靠结果整理到项目的 `notes/`、`progress.md` 和论文中。

Rethlas 是证明搜索和严格检查的辅助工具，不是“自动保证定理正确”的替代品。
