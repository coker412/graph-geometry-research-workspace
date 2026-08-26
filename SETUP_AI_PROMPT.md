# 给导师机器上 AI 的配置任务

你正在配置一个全新的数学研究框架。直接执行配置与检查，不要开始研究数学问题。

## 必须先读

1. `AGENTS.md`
2. `README.md`
3. `TEACHER_SETUP_README.md`
4. `RETHLAS使用教程.md`
5. `problems/important-conjectures/README.md`
6. `TEACHER_QUEUE_QUICKSTART.md`

## 配置目标

- 把当前解压目录配置成新的 graph-geometry 工作区。
- 日常 worker 只使用 Codex，不使用 Danus 或 Claude Code。
- 保持 `projects/` 等数据目录为空，直到导师投放自己的问题。
- Rethlas 必须安装在工作区外部，默认是工作区兄弟目录 `../Rethlas`；绝不能放入 graph-geometry 内部。
- 不复制其他人的 `.codex`、`.env`、token、API key、cookie、Git 历史或研究数据。
- Rethlas 是逐次人工批准的升级通道；安装完成也不得自行启动研究运行。

## 执行顺序

先运行无联网检查：

```bash
./setup.sh --check
```

读取生成的 `SETUP_REPORT.md`。如果缺少 Conda 环境或外置 Rethlas，先向导师说明即将发生的联网下载、磁盘写入位置和大致目的，并取得明确许可。获准后运行：

```bash
./setup.sh --bootstrap
```

如果导师暂时不安装 Rethlas：

```bash
./setup.sh --bootstrap --without-rethlas
```

如果机器连 Conda/Miniforge 本身都没有，先向导师取得安装系统工具的许可，按其操作系统的官方方式安装，再重跑 bootstrap。缺少 tmux 时同理。不要为了“全自动”而绕过系统权限或静默修改导师的 Shell 配置。

Codex CLI 的安装方式应按当前 OpenAI 官方文档核对，并在安装前取得导师许可。Codex 登录必须由导师本人完成；不要请求、读取、打印或迁移认证秘密。

最后重新运行：

```bash
./setup.sh --check
./tools/conjecture_queue.sh doctor
```

向导师报告：工作区路径、Conda 路径、Codex 版本与登录状态、tmux、graphlab、外置 Rethlas 路径与环境状态、未解决项。不要启动猜想队列，除非导师另外明确要求。
