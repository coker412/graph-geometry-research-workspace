#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONDA_ROOT="${CONDA_ROOT:-__CONDA_ROOT__}"

if [[ "${CONDA_DEFAULT_ENV:-}" == "graphlab" ]]; then
  exec python "$WORKSPACE_ROOT/tools/conjecture_queue.py" "$@"
fi

if [[ -x "$CONDA_ROOT/bin/conda" ]]; then
  exec "$CONDA_ROOT/bin/conda" run --no-capture-output -n graphlab \
    python "$WORKSPACE_ROOT/tools/conjecture_queue.py" "$@"
fi

echo "警告：找不到 graphlab conda 环境入口，回退到 PATH 中的 python3。" >&2
exec python3 "$WORKSPACE_ROOT/tools/conjecture_queue.py" "$@"
