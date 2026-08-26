#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
mode="check"
with_rethlas=true

usage() {
  cat <<'EOF'
用法：
  ./setup.sh --check
  ./setup.sh --bootstrap [--without-rethlas]

--check             本地配置与健康检查，不联网安装（默认）
--bootstrap         明确授权创建 Conda 环境；默认还会在工作区外部克隆并安装 Rethlas
--without-rethlas   bootstrap 时只准备普通 Codex 队列，不安装 Rethlas
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
      echo "错误：未知参数 $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [[ "$mode" == "check" ]] && [[ "$with_rethlas" == false ]]; then
  echo "错误：--without-rethlas 只与 --bootstrap 一起使用。" >&2
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
  echo "错误：需要 Python 3。macOS 可先安装 Miniforge，再重新运行本脚本。" >&2
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
    echo "错误：RETHLAS_ROOT 必须位于 graph-geometry 工作区外部：$rethlas_root" >&2
    exit 1
    ;;
esac

if [[ -f "$WORKSPACE_ROOT/MANIFEST.sha256" ]] && \
   grep -q '__WORKSPACE_ROOT__' "$WORKSPACE_ROOT/AGENTS.md"; then
  PYTHON_BIN="$setup_python" \
    "$WORKSPACE_ROOT/tools/verify_teacher_framework.sh" --distribution
fi

PYTHON_BIN="$setup_python" CONDA_ROOT="$conda_root" RETHLAS_ROOT="$rethlas_root" \
  "$WORKSPACE_ROOT/tools/configure_teacher_workspace.sh"
PYTHON_BIN="$setup_python" "$WORKSPACE_ROOT/tools/verify_teacher_framework.sh"

if [[ "$mode" == "bootstrap" ]]; then
  if [[ -z "$conda_root" ]] || [[ ! -x "$conda_root/bin/conda" ]]; then
    echo "错误：bootstrap 需要 Conda/Miniforge。请先安装并设置 CONDA_ROOT。" >&2
    exit 1
  fi

  if ! "$conda_root/bin/conda" run -n graphlab python --version >/dev/null 2>&1; then
    "$conda_root/bin/conda" create -n graphlab python=3.11 -y
  fi

  if [[ "$with_rethlas" == true ]]; then
    if [[ ! -d "$rethlas_root" ]]; then
      if ! command -v git >/dev/null 2>&1; then
        echo "错误：安装 Rethlas 需要 git。" >&2
        exit 1
      fi
      git clone https://github.com/frenzymath/Rethlas.git "$rethlas_root"
    fi
    if [[ ! -f "$rethlas_root/agents/verification/api/requirements.txt" ]] || \
       [[ ! -f "$rethlas_root/agents/generation/mcp/requirements.txt" ]]; then
      echo "错误：RETHLAS_ROOT 不是预期的干净 Rethlas 布局：$rethlas_root" >&2
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

- 生成时间：$setup_timestamp
- 模式：$mode
- 工作区：$WORKSPACE_ROOT
- Conda 根目录：${conda_root:-未找到}
- graphlab：$graphlab_status
- Codex：$codex_status
- Codex 登录：$codex_login
- tmux：$tmux_status
- 外置 Rethlas：$rethlas_root
- Rethlas 布局：$rethlas_status
- rethlas-verification：$verification_env_status
- rethlas-generation：$generation_env_status
- 猜想队列 doctor：$queue_doctor_status

## 边界

- Rethlas 必须保持在工作区外部；本次路径检查已通过。
- 本脚本没有复制或打印任何认证信息。
- 本脚本没有启动 Codex 队列、Rethlas verifier 或 Rethlas generation。
- Rethlas 即使安装完成，仍须针对每次证明升级取得导师明确许可。

## 下一步

1. 如果 Codex 未安装或未登录，由导师按 OpenAI 官方文档安装并亲自登录。
2. 如果 graphlab 缺失，取得联网安装许可后运行 ./setup.sh --bootstrap --without-rethlas。
3. 如果需要 Rethlas，取得联网安装许可后运行 ./setup.sh --bootstrap。
4. 全部就绪后运行 ./tools/conjecture_queue.sh doctor；不要自动启动队列。
EOF

echo "已生成：$report"
echo "工作区：$WORKSPACE_ROOT"
echo "外置 Rethlas：$rethlas_root"
echo "Codex：$codex_status；登录：$codex_login"
echo "graphlab：$graphlab_status；tmux：$tmux_status"
echo "请把 SETUP_REPORT.md 交给导师或配置 AI 审阅。"
