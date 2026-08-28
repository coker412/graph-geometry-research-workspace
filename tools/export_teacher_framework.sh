#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
EXPORT_ROOT="$WORKSPACE_ROOT/exports"
timestamp="$(date +%Y%m%d-%H%M%S)"
package_name="graph-geometry-framework-$timestamp"
export_python="${PYTHON_BIN:-python3}"
if ! command -v "$export_python" >/dev/null 2>&1; then
  echo "错误：导出框架需要 Python 3。" >&2
  exit 1
fi
research_root="$(cd "$WORKSPACE_ROOT/.." && pwd -P)"
package_rethlas_root="${RETHLAS_ROOT:-$research_root/Rethlas}"
package_conda_root="${CONDA_ROOT:-}"
if [[ -z "$package_conda_root" ]] && command -v conda >/dev/null 2>&1; then
  package_conda_root="$(conda info --base 2>/dev/null || true)"
fi
if [[ -z "$package_conda_root" ]]; then
  configured_conda="$(sed -n 's|^CONDA_ROOT="${CONDA_ROOT:-\(.*\)}"$|\1|p' \
    "$WORKSPACE_ROOT/tools/conjecture_queue.sh" | head -n 1)"
  if [[ -n "$configured_conda" ]]; then
    package_conda_root="$configured_conda"
  fi
fi

mkdir -p "$EXPORT_ROOT"
stage_root="$(mktemp -d "$EXPORT_ROOT/.stage.XXXXXX")"
package_root="$stage_root/$package_name"
verification_root=""

cleanup() {
  rm -rf "$stage_root"
  if [[ -n "$verification_root" ]]; then
    rm -rf "$verification_root"
  fi
}
trap cleanup EXIT

copy_file() {
  local source="$1"
  local destination="$2"
  mkdir -p "$(dirname "$package_root/$destination")"
  install -m 0644 "$WORKSPACE_ROOT/$source" "$package_root/$destination"
}

copy_executable() {
  local source="$1"
  local destination="$2"
  mkdir -p "$(dirname "$package_root/$destination")"
  install -m 0755 "$WORKSPACE_ROOT/$source" "$package_root/$destination"
}

mkdir -p "$package_root"
copy_file "AGENTS.md" "AGENTS.md"
copy_file "agents/instructions/research-workflow.md" "agents/instructions/research-workflow.md"
copy_file "agents/instructions/queue-and-escalation.md" "agents/instructions/queue-and-escalation.md"
copy_file "agents/instructions/paper-writing.md" "agents/instructions/paper-writing.md"
copy_file ".gitignore" ".gitignore"
copy_file "TEACHER_FRAMEWORK_HANDOFF.md" "README.md"
copy_file "TEACHER_FRAMEWORK_HANDOFF.md" "TEACHER_FRAMEWORK_HANDOFF.md"
copy_file "TEACHER_SETUP_README.md" "TEACHER_SETUP_README.md"
copy_file "RETHLAS使用教程.md" "RETHLAS使用教程.md"
copy_file "SETUP_AI_PROMPT.md" "SETUP_AI_PROMPT.md"
copy_file "TEACHER_QUEUE_QUICKSTART.md" "TEACHER_QUEUE_QUICKSTART.md"
copy_executable "setup.sh" "setup.sh"
copy_executable "queue.sh" "queue.sh"
copy_file "problems/readme.md" "problems/readme.md"
copy_file "problems/important-conjectures/README.md" "problems/important-conjectures/README.md"
copy_file "problems/important-conjectures/runner.toml" "problems/important-conjectures/runner.toml"
copy_file "templates/important-conjecture/problem.md" "templates/important-conjecture/problem.md"
copy_file "templates/important-conjecture/config.toml" "templates/important-conjecture/config.toml"
copy_file "templates/blind-research-packet.md" "templates/blind-research-packet.md"
copy_file "templates/project_template/ideas.md" "templates/project_template/ideas.md"
copy_file "templates/research-visualization.md" "templates/research-visualization.md"
copy_file "templates/rethlas-problem.md" "templates/rethlas-problem.md"
copy_executable "tools/conjecture_queue.py" "tools/conjecture_queue.py"
copy_executable "tools/conjecture_queue.sh" "tools/conjecture_queue.sh"
copy_file "tools/tests/test_conjecture_queue.py" "tools/tests/test_conjecture_queue.py"
copy_executable "tools/configure_teacher_workspace.sh" "tools/configure_teacher_workspace.sh"
copy_executable "tools/verify_teacher_framework.sh" "tools/verify_teacher_framework.sh"
copy_executable "tools/export_teacher_framework.sh" "tools/export_teacher_framework.sh"

for script in "$WORKSPACE_ROOT"/tools/rethlas/*.sh; do
  copy_executable "${script#"$WORKSPACE_ROOT/"}" "${script#"$WORKSPACE_ROOT/"}"
done

empty_dirs=(
  "problems/important-conjectures/items"
  "projects"
  "archive"
  "index"
  "library/definitions"
  "library/theorems"
  "library/examples"
  "library/counterexamples"
  "shared/references"
  "shared/datasets"
  "shared/papers"
  "agents/important-conjectures"
  "environments"
)
for relative in "${empty_dirs[@]}"; do
  mkdir -p "$package_root/$relative"
  : > "$package_root/$relative/.gitkeep"
done

"$export_python" - "$package_root" "$WORKSPACE_ROOT" "$research_root" \
  "$package_conda_root" "$package_rethlas_root" <<'PY'
from pathlib import Path
import sys

package_root = Path(sys.argv[1])
source_root = sys.argv[2]
research_root = sys.argv[3]
conda_root = sys.argv[4]
rethlas_root = sys.argv[5]
replacements = [
    (source_root, "__WORKSPACE_ROOT__"),
    (rethlas_root, "__RETHLAS_ROOT__"),
    (conda_root, "__CONDA_ROOT__"),
    (research_root, "__RESEARCH_ROOT__"),
]
replacements.extend([
    ("ricci" + "flow0602", "example-project"),
    ("intersecting-subset-" + "ramsey0624", "example-project"),
    ("nine_over_four_" + "breakthrough", "example-problem"),
    ("P2" + "cut", "example-problem"),
    ("P2" + "_cut", "example_problem"),
    ("某个存在性命题", "某个存在性命题"),
])
replacements = [(old, new) for old, new in replacements if old]
suffixes = {".md", ".sh", ".py", ".toml"}
for path in package_root.rglob("*"):
    if not path.is_file() or path.suffix not in suffixes:
        continue
    if path.relative_to(package_root).as_posix() == "tools/verify_teacher_framework.sh":
        continue
    content = path.read_text(encoding="utf-8")
    for old, new in replacements:
        content = content.replace(old, new)
    path.write_text(content, encoding="utf-8")
PY

"$export_python" - "$package_root" <<'PY'
from hashlib import sha256
from pathlib import Path
import sys

root = Path(sys.argv[1])
lines = []
for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
    if not path.is_file() or path.name == "MANIFEST.sha256":
        continue
    digest = sha256(path.read_bytes()).hexdigest()
    relative = path.relative_to(root).as_posix()
    lines.append(f"{digest}  ./{relative}\n")
(root / "MANIFEST.sha256").write_text("".join(lines), encoding="utf-8")
PY

PYTHON_BIN="$export_python" \
  "$package_root/tools/verify_teacher_framework.sh" --distribution

archive_path="$EXPORT_ROOT/$package_name.tar.gz"
tar -C "$stage_root" -czf "$archive_path" "$package_name"
"$export_python" - "$archive_path" "$archive_path.sha256" <<'PY'
from hashlib import sha256
from pathlib import Path
import sys

archive = Path(sys.argv[1])
checksum = Path(sys.argv[2])
digest = sha256(archive.read_bytes()).hexdigest()
checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
if sha256(archive.read_bytes()).hexdigest() != digest:
    raise SystemExit("archive checksum verification failed")
print(f"{archive.name}: OK")
PY

verification_root="$(mktemp -d "$EXPORT_ROOT/.verify.XXXXXX")"
tar -C "$verification_root" -xzf "$archive_path"
extracted_root="$verification_root/$package_name"
PYTHON_BIN="$export_python" \
  "$extracted_root/tools/verify_teacher_framework.sh" --distribution
CONDA_ROOT="$package_conda_root" \
RETHLAS_ROOT="$package_rethlas_root" \
  "$extracted_root/setup.sh" --check
PYTHON_BIN="$export_python" "$extracted_root/tools/verify_teacher_framework.sh"
"$extracted_root/tools/conjecture_queue.sh" doctor

echo "已生成：$archive_path"
echo "校验文件：$archive_path.sha256"
echo "内容清单：$package_name/MANIFEST.sha256"
echo "本包使用严格白名单，不包含 projects/archive/shared 等目录中的任何研究数据。"
echo "已完成解压、路径配置、结构检查和队列 doctor 端到端验收。"
