#!/usr/bin/env bash
set -euo pipefail

CONDA_ROOT="${CONDA_ROOT:-__CONDA_ROOT__}"
RETHLAS_ROOT="${RETHLAS_ROOT:-__RETHLAS_ROOT__}"
SESSION_NAME="${SESSION_NAME:-rethlas_verifier}"
CODEX_MODEL="${CODEX_MODEL:-gpt-5.6-sol}"
CODEX_REASONING_EFFORT="${CODEX_REASONING_EFFORT:-xhigh}"
RESTART_STALE="${RESTART_STALE:-0}"

resolve_codex_bin() {
  local candidate=""
  local extension_candidates=()

  if [[ -n "${CODEX_BIN:-}" ]]; then
    candidate="$CODEX_BIN"
  elif command -v codex >/dev/null 2>&1; then
    candidate="$(command -v codex)"
  else
    shopt -s nullglob
    extension_candidates=(
      "$HOME"/.vscode-server/extensions/openai.chatgpt-*-linux-x64/bin/linux-x86_64/codex
    )
    shopt -u nullglob
    if [[ ${#extension_candidates[@]} -gt 0 ]]; then
      candidate="$(
        printf '%s\n' "${extension_candidates[@]}" |
          sort -V |
          tail -n 1
      )"
    fi
  fi

  if [[ -z "$candidate" || ! -f "$candidate" || ! -x "$candidate" ]]; then
    return 1
  fi

  readlink -f "$candidate"
}

running_codex_bin() {
  local pane_pid=""

  if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    return 1
  fi
  pane_pid="$(tmux list-panes -t "$SESSION_NAME" -F '#{pane_pid}' | head -n 1)"
  if ! [[ "$pane_pid" =~ ^[0-9]+$ ]] || [[ ! -r "/proc/$pane_pid/environ" ]]; then
    return 1
  fi
  tr '\0' '\n' <"/proc/$pane_pid/environ" |
    sed -n 's/^CODEX_BIN=//p' |
    head -n 1
}

if ! resolved_codex_bin="$(resolve_codex_bin)"; then
  echo "错误：找不到可执行的 Codex CLI。" >&2
  echo "请先确认 codex --version 可运行，或显式设置 CODEX_BIN=/绝对路径/codex。" >&2
  exit 1
fi

if ! "$resolved_codex_bin" --version >/dev/null 2>&1; then
  echo "错误：Codex CLI 无法执行：$resolved_codex_bin" >&2
  exit 1
fi

if curl -sf http://127.0.0.1:8091/health >/dev/null; then
  configured_codex_bin="$(running_codex_bin || true)"
  if [[ -n "$configured_codex_bin" &&
        -f "$configured_codex_bin" &&
        -x "$configured_codex_bin" ]]; then
    echo "Rethlas verifier 已在 http://127.0.0.1:8091 运行。"
    echo "Codex：$configured_codex_bin"
    exit 0
  fi

  echo "检测到 verifier 的 /health 可访问，但它没有配置可执行的 CODEX_BIN。" >&2
  if [[ "$RESTART_STALE" != "1" ]]; then
    echo "确认没有验证任务正在运行后，请执行：" >&2
    echo "  RESTART_STALE=1 ./tools/rethlas/start_verifier_tmux.sh" >&2
    exit 1
  fi
  if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "错误：端口 8091 不是由 tmux session $SESSION_NAME 管理；拒绝自动停止未知进程。" >&2
    exit 1
  fi
  tmux kill-session -t "$SESSION_NAME"
fi

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  if [[ "$RESTART_STALE" != "1" ]]; then
    echo "tmux session 已存在但健康检查未通过：$SESSION_NAME" >&2
    echo "查看日志：tmux attach -t $SESSION_NAME" >&2
    echo "确认可重启后：RESTART_STALE=1 ./tools/rethlas/start_verifier_tmux.sh" >&2
    exit 1
  fi
  tmux kill-session -t "$SESSION_NAME"
fi

cmd="source '$CONDA_ROOT/etc/profile.d/conda.sh' && conda activate rethlas-verification && cd '$RETHLAS_ROOT/agents/verification' && CODEX_BIN='$resolved_codex_bin' CODEX_MODEL='$CODEX_MODEL' CODEX_REASONING_EFFORT='$CODEX_REASONING_EFFORT' exec uvicorn api.server:app --host 127.0.0.1 --port 8091"
tmux new-session -d -s "$SESSION_NAME" "$cmd"

for _ in {1..20}; do
  if curl -sf http://127.0.0.1:8091/health >/dev/null; then
    echo "Rethlas verifier 已启动：$SESSION_NAME"
    echo "模型：$CODEX_MODEL；推理强度：$CODEX_REASONING_EFFORT"
    echo "Codex：$resolved_codex_bin"
    echo "查看：tmux attach -t $SESSION_NAME"
    exit 0
  fi
  sleep 0.25
done

echo "Rethlas verifier 启动失败；查看：tmux attach -t $SESSION_NAME" >&2
exit 1
