#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
mode="check"
with_rethlas=true

usage() {
  cat <<'EOF'
Usage:
  ./setup.sh --check
  ./setup.sh --bootstrap [--without-rethlas]

--check             Local configuration and health checks, without downloads (default)
--bootstrap         Authorized environment bootstrap; also installs external Rethlas by default
--without-rethlas   Bootstrap the Codex queue without Rethlas
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check)
      mode="check"
      ;;
    --bootstrap)
      mode="bootstrap"
      ;;
    --without-rethlas)
      with_rethlas=false
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown argument $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [[ "$mode" == "check" ]] && [[ "$with_rethlas" == false ]]; then
  echo "Error: --without-rethlas requires --bootstrap." >&2
  exit 2
fi

discover_conda_root() {
  if [[ -n "${CONDA_ROOT:-}" ]]; then
    printf '%s\n' "$CONDA_ROOT"
    return
  fi
  if command -v conda >/dev/null 2>&1; then
    conda info --base 2>/dev/null || true
    return
  fi
  printf '%s\n' ""
}

conda_root="$(discover_conda_root)"
setup_python="${PYTHON_BIN:-}"
if [[ -z "$setup_python" ]] && command -v python3 >/dev/null 2>&1; then
  setup_python="$(command -v python3)"
fi
if [[ -z "$setup_python" ]] && [[ -n "$conda_root" ]] && [[ -x "$conda_root/bin/python" ]]; then
  setup_python="$conda_root/bin/python"
fi
if [[ -z "$setup_python" ]]; then
  echo "Error: Python 3 is required. Install it or Miniforge, then rerun this script." >&2
  exit 1
fi
rethlas_root="${RETHLAS_ROOT:-$(cd "$WORKSPACE_ROOT/.." && pwd -P)/Rethlas}"
rethlas_root="$("$setup_python" - "$rethlas_root" <<'PY'
from pathlib import Path
import sys

print(Path(sys.argv[1]).expanduser().resolve(strict=False))
PY
)"

case "$rethlas_root/" in
  "$WORKSPACE_ROOT/"*)
    echo "Error: RETHLAS_ROOT must be outside the workspace:$rethlas_root" >&2
    exit 1
    ;;
esac

if [[ -f "$WORKSPACE_ROOT/MANIFEST.sha256" ]] && \
   grep -q '__WORKSPACE_ROOT__' "$WORKSPACE_ROOT/AGENTS.md"; then
  setup_verification_mode="--distribution"
  if [[ -e "$WORKSPACE_ROOT/.git" ]]; then
    setup_verification_mode="--public-source"
  fi
  PYTHON_BIN="$setup_python" \
    "$WORKSPACE_ROOT/tools/verify_teacher_framework.sh" "$setup_verification_mode"
fi

PYTHON_BIN="$setup_python" CONDA_ROOT="$conda_root" RETHLAS_ROOT="$rethlas_root" \
  "$WORKSPACE_ROOT/tools/configure_teacher_workspace.sh"
PYTHON_BIN="$setup_python" "$WORKSPACE_ROOT/tools/verify_teacher_framework.sh"

if [[ "$mode" == "bootstrap" ]]; then
  if [[ -z "$conda_root" ]] || [[ ! -x "$conda_root/bin/conda" ]]; then
    echo "Error: bootstrap requires Conda/Miniforge. Install it and set CONDA_ROOT." >&2
    exit 1
  fi

  if ! "$conda_root/bin/conda" run -n graphlab python --version >/dev/null 2>&1; then
    "$conda_root/bin/conda" create -n graphlab python=3.11 -y
  fi

  if [[ "$with_rethlas" == true ]]; then
    if [[ ! -d "$rethlas_root" ]]; then
      if ! command -v git >/dev/null 2>&1; then
        echo "Error: installing Rethlas requires git." >&2
        exit 1
      fi
      git clone https://github.com/frenzymath/Rethlas.git "$rethlas_root"
    fi
    if [[ ! -f "$rethlas_root/agents/verification/api/requirements.txt" ]] || \
       [[ ! -f "$rethlas_root/agents/generation/mcp/requirements.txt" ]]; then
      echo "Error: RETHLAS_ROOT does not have the expected Rethlas layout:$rethlas_root" >&2
      exit 1
    fi

    if ! "$conda_root/bin/conda" run -n rethlas-verification python --version >/dev/null 2>&1; then
      "$conda_root/bin/conda" create -n rethlas-verification python=3.11 pip -y
    fi
    "$conda_root/bin/conda" run -n rethlas-verification \
      pip install -r "$rethlas_root/agents/verification/api/requirements.txt"

    if ! "$conda_root/bin/conda" run -n rethlas-generation python --version >/dev/null 2>&1; then
      "$conda_root/bin/conda" create -n rethlas-generation python=3.11 pip -y
    fi
    "$conda_root/bin/conda" run -n rethlas-generation \
      pip install -r "$rethlas_root/agents/generation/mcp/requirements.txt"
  fi
fi

report="$WORKSPACE_ROOT/SETUP_REPORT.md"
setup_timestamp="$(date '+%Y-%m-%dT%H:%M:%S%z')"
codex_status="missing"
codex_login="unknown"
if command -v codex >/dev/null 2>&1; then
  codex_status="$(codex --version 2>/dev/null | head -n 1 || true)"
  if codex login status >/dev/null 2>&1; then
    codex_login="logged-in"
  else
    codex_login="not-logged-in-or-unavailable"
  fi
fi

tmux_status="missing"
if command -v tmux >/dev/null 2>&1; then
  tmux_status="$(tmux -V)"
fi

graphlab_status="missing"
verification_env_status="not-installed"
generation_env_status="not-installed"
if [[ -n "$conda_root" ]] && [[ -x "$conda_root/bin/conda" ]]; then
  if "$conda_root/bin/conda" run -n graphlab python --version >/dev/null 2>&1; then
    graphlab_status="ready"
  fi
  if "$conda_root/bin/conda" run -n rethlas-verification python --version >/dev/null 2>&1; then
    verification_env_status="ready"
  fi
  if "$conda_root/bin/conda" run -n rethlas-generation python --version >/dev/null 2>&1; then
    generation_env_status="ready"
  fi
fi

rethlas_status="missing-optional"
if [[ -f "$rethlas_root/agents/generation/tests/run_example.sh" ]] && \
   [[ -f "$rethlas_root/agents/verification/api/server.py" ]]; then
  rethlas_status="external-layout-ready"
fi

queue_doctor_status="not-run"
if [[ "$graphlab_status" == "ready" ]] && \
   [[ "$codex_status" != "missing" ]] && \
   [[ "$tmux_status" != "missing" ]]; then
  if "$WORKSPACE_ROOT/tools/conjecture_queue.sh" doctor; then
    queue_doctor_status="passed"
  else
    queue_doctor_status="failed"
  fi
fi

cat > "$report" <<EOF
# Setup Report

- Generated at: $setup_timestamp
- Mode: $mode
- Workspace: $WORKSPACE_ROOT
- Conda root: ${conda_root:-not found}
- graphlab: $graphlab_status
- Codex: $codex_status
- Codex login: $codex_login
- tmux: $tmux_status
- External Rethlas: $rethlas_root
- Rethlas layout: $rethlas_status
- rethlas-verification: $verification_env_status
- rethlas-generation: $generation_env_status
- Queue doctor: $queue_doctor_status

## Boundaries

- Rethlas must remain outside the workspace; the path check passed.
- This script did not copy or print authentication secrets.
- This script did not start the Codex queue, Rethlas verifier, or generation.
- Every Rethlas run still requires explicit researcher authorization.

## Next steps

1. If Codex is missing or not authenticated, install it using official instructions and sign in personally.
2. If graphlab is missing, authorize installation and run ./setup.sh --bootstrap --without-rethlas.
3. If Rethlas is needed, authorize installation and run ./setup.sh --bootstrap.
4. When ready, run ./tools/conjecture_queue.sh doctor; do not start the queue automatically.
EOF

echo "Created: $report"
echo "Workspace: $WORKSPACE_ROOT"
echo "External Rethlas: $rethlas_root"
echo "Codex: $codex_status; login: $codex_login"
echo "graphlab: $graphlab_status；tmux: $tmux_status"
echo "Review SETUP_REPORT.md with the researcher or setup assistant."
