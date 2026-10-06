#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
QUEUE="$WORKSPACE_ROOT/tools/conjecture_queue.sh"

usage() {
  cat <<'EOF'
Conjecture queue (run from the workspace root)

  ./queue.sh add <slug> "Title"         Add a problem
  ./queue.sh check                      Check without calling Codex
  ./queue.sh start                      Start fair rotation in tmux
  ./queue.sh start --slug NAME          Start a dedicated problem runner
  ./queue.sh status                     Show queue and problem states
  ./queue.sh list                       List registered problems
  ./queue.sh doctor [--slug NAME]        Read-only health check
  ./queue.sh set-status NAME STATUS     Apply a researcher-directed status
  ./queue.sh packet --slug NAME         Preview packet size and evidence
  ./queue.sh usage [--slug NAME]         Show recorded token usage
  ./queue.sh progress [--slug NAME]      Show assessments and route advice
  ./queue.sh state-init [--slug NAME]    Add missing recovery state
  ./queue.sh state-audit [--slug NAME]   Check state structure and size
  ./queue.sh hygiene report             Report generated files and disk use
  ./queue.sh watch [--slug NAME]         View tmux; detach with Ctrl-b, then d
  ./queue.sh stop [--slug NAME]          Stop safely after the current round
  ./queue.sh stop --all                 Safely stop all runners
  ./queue.sh once                       Run one foreground round
  ./queue.sh run                        Poll in the foreground

Use start for long runs. Foreground run does not need tmux but requires an open terminal.
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
  start|status|stop|state-init|state-audit|progress|packet|usage|doctor|list|set-status)
    shift
    exec "$QUEUE" "$command_name" "$@"
    ;;
  watch)
    shift
    exec "$QUEUE" watch "$@"
    ;;
  once)
    shift
    exec "$QUEUE" run --once "$@"
    ;;
  run)
    shift
    exec "$QUEUE" run "$@"
    ;;
  hygiene)
    shift
    exec "$WORKSPACE_ROOT/tools/workspace_hygiene.py" "$@"
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    echo "Error: unknown command $command_name" >&2
    usage >&2
    exit 2
    ;;
esac
