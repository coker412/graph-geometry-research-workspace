#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
QUEUE="$WORKSPACE_ROOT/tools/conjecture_queue.sh"

usage() {
  cat <<'EOF'
重要猜想队列（所有命令都从工作区根目录运行）

  ./queue.sh add <英文短名> "题目标题"  新建一道题
  ./queue.sh check                      启动前检查，不调用 Codex
  ./queue.sh start                      用 tmux 后台持续轮询
  ./queue.sh status                     查看队列和各题状态
  ./queue.sh watch                      进入实时终端（Ctrl-b 后按 d 退出查看）
  ./queue.sh stop                       当前 Codex 回合结束后安全停止
  ./queue.sh once                       前台只推进一个回合
  ./queue.sh run                        前台持续轮询；关闭终端会中断

日常长跑推荐 start。run 不需要 tmux，但终端必须一直保持打开。
EOF
}

command_name="${1:-help}"
case "$command_name" in
  add)
    shift
    exec "$QUEUE" add "$@"
    ;;
  check)
    "$QUEUE" doctor
    "$QUEUE" list
    exec "$QUEUE" run --dry-run
    ;;
  start|status|stop)
    exec "$QUEUE" "$command_name"
    ;;
  watch)
    exec "$QUEUE" watch
    ;;
  once)
    exec "$QUEUE" run --once
    ;;
  run)
    exec "$QUEUE" run
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    echo "错误：未知命令 $command_name" >&2
    usage >&2
    exit 2
    ;;
esac
