#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "错误：找不到 $PYTHON_BIN；请先安装 Python 3。" >&2
  exit 1
fi

conda_root="${CONDA_ROOT:-}"
if [[ -z "$conda_root" ]] && command -v conda >/dev/null 2>&1; then
  conda_root="$(conda info --base 2>/dev/null || true)"
fi
if [[ -z "$conda_root" ]]; then
  conda_root="__CONDA_ROOT__"
fi

rethlas_root="${RETHLAS_ROOT:-}"
if [[ -z "$rethlas_root" ]]; then
  rethlas_root="$(cd "$WORKSPACE_ROOT/.." && pwd -P)/Rethlas"
fi

"$PYTHON_BIN" - "$WORKSPACE_ROOT" "$conda_root" "$rethlas_root" <<'PY'
from pathlib import Path
import sys

workspace_root = sys.argv[1]
conda_root = sys.argv[2]
rethlas_root = sys.argv[3]
root = Path(workspace_root)

replacements = {
    "__WORKSPACE_ROOT__": workspace_root,
    "__RESEARCH_ROOT__": str(root.parent),
    "__CONDA_ROOT__": conda_root,
    "__RETHLAS_ROOT__": rethlas_root,
}

suffixes = {".md", ".sh", ".py", ".toml"}
runtime_files = {
    "setup.sh",
    "tools/configure_teacher_workspace.sh",
    "tools/export_teacher_framework.sh",
    "tools/verify_teacher_framework.sh",
}
for path in root.rglob("*"):
    if not path.is_file() or path.suffix not in suffixes:
        continue
    if path.relative_to(root).as_posix() in runtime_files:
        continue
    content = path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        content = content.replace(old, new)
    path.write_text(content, encoding="utf-8")
PY

echo "工作区路径：$WORKSPACE_ROOT"
if [[ "$conda_root" == "__CONDA_ROOT__" ]]; then
  echo "警告：未识别 Conda 根目录；请安装 Conda 后设置 CONDA_ROOT 再运行本脚本。" >&2
else
  echo "Conda 路径：$conda_root"
fi
echo "Rethlas 路径：$rethlas_root（可选；未安装不影响 Codex 队列）"
echo "下一步：./tools/verify_teacher_framework.sh"
