#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
verification_mode="workspace"

if [[ $# -gt 1 ]] || { [[ $# -eq 1 ]] && \
  [[ "$1" != "--distribution" ]] && [[ "$1" != "--public-source" ]]; }; then
  echo "用法：./tools/verify_teacher_framework.sh [--distribution|--public-source]" >&2
  exit 2
fi
if [[ $# -eq 1 ]] && [[ "$1" == "--distribution" ]]; then
  verification_mode="distribution"
elif [[ $# -eq 1 ]] && [[ "$1" == "--public-source" ]]; then
  verification_mode="public-source"
fi

required_files=(
  "AGENTS.md"
  "LICENSE"
  "agents/instructions/research-workflow.md"
  "agents/instructions/queue-and-escalation.md"
  "agents/instructions/paper-writing.md"
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
  "templates/blind-research-packet.md"
  "templates/project_template/CURRENT_STATE.md"
  "tools/conjecture_queue.py"
  "tools/conjecture_queue.sh"
  "tools/workspace_hygiene.py"
  "tools/project_state.py"
  "tools/update_manifest.py"
  "tools/tests/test_conjecture_queue.py"
  "tools/tests/test_workspace_hygiene.py"
  "tools/tests/test_project_state.py"
  "tools/tests/test_update_manifest.py"
  "tools/configure_teacher_workspace.sh"
  "tools/export_teacher_framework.sh"
  "tools/verify_teacher_framework.sh"
  "examples/tree-edge-count/README.md"
  "examples/tree-edge-count/problem.md"
  "examples/tree-edge-count/CURRENT_STATE.md"
  "examples/tree-edge-count/ideas.md"
  "examples/tree-edge-count/progress.md"
  "examples/tree-edge-count/research-tree.md"
  "examples/tree-edge-count/proof-map.md"
  "examples/tree-edge-count/verification-ledger.md"
  "examples/tree-edge-count/notes/proof.md"
)

failed=false
if [[ "$verification_mode" == "public-source" ]] && \
   [[ ! -f "$WORKSPACE_ROOT/.github/workflows/ci.yml" ]]; then
  echo "公开源码缺少：.github/workflows/ci.yml" >&2
  failed=true
fi
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
  if [[ "$verification_mode" == "distribution" ]] && [[ -e "$WORKSPACE_ROOT/$forbidden" ]]; then
    echo "分发包不应包含：$forbidden" >&2
    failed=true
  fi
done

if [[ "$verification_mode" != "workspace" ]]; then
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
    -not -path "$WORKSPACE_ROOT/.git/*" \
    -not -path "$WORKSPACE_ROOT/exports/*" \
    \( -name '.env' -o -name '*.env' -o -name '*.pem' -o -name '*.key' \
       -o -name '*.p12' -o -name '*.pfx' -o -name '*.pdf' -o -name '*.zip' \
       -o -name '*.7z' -o -name '*.jsonl' -o -iname '*credential*' \
       -o -iname '*secret*' -o -iname '*token*' \) -print
)

secret_pattern='(OPENAI_API_KEY|ANTHROPIC_API_KEY|DANUS_CODEX_API_KEY|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY)[[:space:]]*[=:]'
if command -v rg >/dev/null 2>&1; then
  if rg -n -I "$secret_pattern" "$WORKSPACE_ROOT" \
      -g '!.git/**' -g '!exports/**' \
      -g '!tools/verify_teacher_framework.sh' >/dev/null; then
    echo "发现疑似密钥赋值；请运行 rg 手工检查。" >&2
    failed=true
  fi
else
  if grep -R -I -E "$secret_pattern" "$WORKSPACE_ROOT" \
      --exclude-dir='.git' --exclude-dir='exports' \
      --exclude='verify_teacher_framework.sh' >/dev/null; then
    echo "发现疑似密钥赋值；请运行 grep 手工检查。" >&2
    failed=true
  fi
fi

if [[ "$verification_mode" != "workspace" ]] && [[ -f "$WORKSPACE_ROOT/MANIFEST.sha256" ]]; then
  if ! "$PYTHON_BIN" "$WORKSPACE_ROOT/tools/update_manifest.py" check; then
    echo "MANIFEST.sha256 校验失败。" >&2
    failed=true
  fi
fi

if [[ "$failed" == true ]]; then
  echo "框架检查失败。" >&2
  exit 1
fi

echo "框架检查通过。"
if [[ "$verification_mode" == "distribution" ]]; then
  echo "数据目录为空，未发现禁止目录、文件类型或常见密钥赋值。"
elif [[ "$verification_mode" == "public-source" ]]; then
  echo "公开源码边界通过：研究数据目录为空，清单与源码一致。"
fi
