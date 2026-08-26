#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
distribution_mode=false

if [[ $# -gt 1 ]] || { [[ $# -eq 1 ]] && [[ "$1" != "--distribution" ]]; }; then
  echo "用法：./tools/verify_teacher_framework.sh [--distribution]" >&2
  exit 2
fi
if [[ $# -eq 1 ]]; then
  distribution_mode=true
fi

required_files=(
  "AGENTS.md"
  "README.md"
  "TEACHER_FRAMEWORK_HANDOFF.md"
  "TEACHER_SETUP_README.md"
  "RETHLAS使用教程.md"
  "SETUP_AI_PROMPT.md"
  "TEACHER_QUEUE_QUICKSTART.md"
  "setup.sh"
  "queue.sh"
  ".gitignore"
  "problems/readme.md"
  "problems/important-conjectures/README.md"
  "problems/important-conjectures/runner.toml"
  "templates/important-conjecture/problem.md"
  "templates/important-conjecture/config.toml"
  "tools/conjecture_queue.py"
  "tools/conjecture_queue.sh"
  "tools/configure_teacher_workspace.sh"
  "tools/export_teacher_framework.sh"
  "tools/verify_teacher_framework.sh"
)

failed=false
for relative in "${required_files[@]}"; do
  if [[ ! -f "$WORKSPACE_ROOT/$relative" ]]; then
    echo "缺少：$relative" >&2
    failed=true
  fi
done

required_dirs=(projects archive index library shared agents environments)
for relative in "${required_dirs[@]}"; do
  if [[ ! -d "$WORKSPACE_ROOT/$relative" ]]; then
    echo "缺少目录：$relative/" >&2
    failed=true
  fi
done

for forbidden in .git .codex .claude .agents .vscode; do
  if [[ "$distribution_mode" == true ]] && [[ -e "$WORKSPACE_ROOT/$forbidden" ]]; then
    echo "分发包不应包含：$forbidden" >&2
    failed=true
  fi
done

if [[ "$distribution_mode" == true ]]; then
  for data_dir in projects archive shared index library environments; do
    while IFS= read -r path; do
      if [[ "$(basename "$path")" != ".gitkeep" ]]; then
        echo "分发包数据目录中发现文件：${path#"$WORKSPACE_ROOT/"}" >&2
        failed=true
      fi
    done < <(find "$WORKSPACE_ROOT/$data_dir" -type f -print)
  done
fi

while IFS= read -r path; do
  echo "发现禁止的文件类型或秘密文件名：${path#"$WORKSPACE_ROOT/"}" >&2
  failed=true
done < <(
  find "$WORKSPACE_ROOT" -type f \
    \( -name '.env' -o -name '*.env' -o -name '*.pem' -o -name '*.key' \
       -o -name '*.p12' -o -name '*.pfx' -o -name '*.pdf' -o -name '*.zip' \
       -o -name '*.7z' -o -name '*.jsonl' -o -iname '*credential*' \
       -o -iname '*secret*' -o -iname '*token*' \) -print
)

secret_pattern='(OPENAI_API_KEY|ANTHROPIC_API_KEY|DANUS_CODEX_API_KEY|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY)[[:space:]]*[=:]'
if command -v rg >/dev/null 2>&1; then
  if rg -n -I "$secret_pattern" "$WORKSPACE_ROOT" \
      -g '!tools/verify_teacher_framework.sh' >/dev/null; then
    echo "发现疑似密钥赋值；请运行 rg 手工检查。" >&2
    failed=true
  fi
else
  if grep -R -I -E "$secret_pattern" "$WORKSPACE_ROOT" \
      --exclude='verify_teacher_framework.sh' >/dev/null; then
    echo "发现疑似密钥赋值；请运行 grep 手工检查。" >&2
    failed=true
  fi
fi

if [[ "$distribution_mode" == true ]]; then
  source_identity_pattern='(/home/cheng|ricciflow0602|intersecting-subset-ramsey0624|P2cut|P2_cut)'
  identity_matches="$(cd "$WORKSPACE_ROOT" && \
      grep -R -I -l -E "$source_identity_pattern" . \
        --exclude='verify_teacher_framework.sh' || true)"
  if [[ -n "$identity_matches" ]]; then
    echo "发现原工作区路径或项目标识；分发包未完全匿名化。" >&2
    (cd "$WORKSPACE_ROOT" && \
      grep -R -I -n -E "$source_identity_pattern" . \
        --exclude='verify_teacher_framework.sh') >&2 || true
    failed=true
  fi
fi

if [[ "$distribution_mode" == true ]] && [[ -f "$WORKSPACE_ROOT/MANIFEST.sha256" ]]; then
  if ! "$PYTHON_BIN" - "$WORKSPACE_ROOT" <<'PY'
from hashlib import sha256
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
for raw_line in (root / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
    digest, name = raw_line.split(maxsplit=1)
    relative = name.lstrip("* ")
    path = (root / relative).resolve()
    if root not in path.parents or not path.is_file():
        raise SystemExit(1)
    if sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit(1)
PY
  then
    echo "MANIFEST.sha256 校验失败。" >&2
    failed=true
  fi
fi

if [[ "$failed" == true ]]; then
  echo "框架检查失败。" >&2
  exit 1
fi

echo "框架检查通过。"
if [[ "$distribution_mode" == true ]]; then
  echo "数据目录为空，未发现禁止目录、文件类型或常见密钥赋值。"
fi
