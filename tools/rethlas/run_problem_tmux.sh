#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

usage() {
  cat <<'EOF'
用法：
  ./tools/rethlas/run_problem_tmux.sh <项目名> <问题名> [session名]

示例：
  ./tools/rethlas/run_problem_tmux.sh example-project example-problem

这会在 tmux 里启动 Rethlas。你可以用下面命令查看：
  tmux attach -t <session名>

退出查看但不中断运行：
  按 Ctrl-b，然后按 d
EOF
}

if [[ $# -lt 2 || $# -gt 3 ]]; then
  usage >&2
  exit 2
fi

project_name="$1"
problem_name="$2"
session_name="${3:-rethlas_${project_name}_${problem_name}}"
session_name="${session_name//[^A-Za-z0-9_.-]/_}"
max_iterations="${MAX_ITERATIONS:-6}"

if ! [[ "$max_iterations" =~ ^[0-9]+$ ]] || [[ "$max_iterations" -le 0 ]]; then
  echo "错误：MAX_ITERATIONS 必须是正整数：$max_iterations" >&2
  exit 2
fi

if ! command -v tmux >/dev/null 2>&1; then
  echo "错误：找不到 tmux。" >&2
  exit 1
fi

if tmux has-session -t "$session_name" 2>/dev/null; then
  echo "tmux session 已存在：$session_name"
  echo "查看：tmux attach -t $session_name"
  exit 0
fi

cmd="cd '$WORKSPACE_ROOT' && MAX_ITERATIONS='$max_iterations' ./tools/rethlas/run_problem.sh '$project_name' '$problem_name'; echo; echo '[Rethlas finished] press Ctrl-b then d to detach, or exit to close'; exec bash"

tmux new-session -d -s "$session_name" "$cmd"

echo "已启动 tmux session：$session_name"
echo "查看实时输出：tmux attach -t $session_name"
echo "后台 detach：Ctrl-b 然后 d"
