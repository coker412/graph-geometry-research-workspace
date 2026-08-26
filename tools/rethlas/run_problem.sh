#!/usr/bin/env bash
set -uo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RETHLAS_ROOT="${RETHLAS_ROOT:-__RETHLAS_ROOT__}"
CONDA_ROOT="${CONDA_ROOT:-__CONDA_ROOT__}"
GENERATION_ENV="${GENERATION_ENV:-rethlas-generation}"
MODEL="${MODEL:-gpt-5.6-sol}"
REASONING_EFFORT="${REASONING_EFFORT:-xhigh}"

usage() {
  cat <<'EOF'
用法：
  ./tools/rethlas/run_problem.sh <项目名> <问题名>

示例：
  MAX_ITERATIONS=10 ./tools/rethlas/run_problem.sh example-project example-problem

可选环境变量：
  RETHLAS_ROOT       Rethlas 仓库路径
  MAX_ITERATIONS     最大迭代次数，默认 10
  MODEL              生成模型，默认 gpt-5.6-sol
  REASONING_EFFORT   推理强度，默认 xhigh
EOF
}

if [[ $# -ne 2 ]]; then
  usage >&2
  exit 2
fi

project_name="$1"
problem_name="$2"

if [[ ! "$project_name" =~ ^[A-Za-z0-9._-]+$ ]] ||
   [[ ! "$problem_name" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "错误：项目名和问题名只能包含字母、数字、点、下划线和连字符。" >&2
  exit 2
fi

generation_dir="$RETHLAS_ROOT/agents/generation"
runner="$generation_dir/tests/run_example.sh"
source_problem="$WORKSPACE_ROOT/projects/$project_name/rethlas/problems/$problem_name.md"
source_refs="$WORKSPACE_ROOT/projects/$project_name/rethlas/problems/$problem_name.refs"

problem_id="graph-geometry/$project_name/$problem_name"
rethlas_problem="$generation_dir/data/$problem_id.md"
rethlas_refs="$generation_dir/data/$problem_id.refs"

local_root="$WORKSPACE_ROOT/projects/$project_name/rethlas"
local_result="$local_root/results/$problem_name"
local_run="$local_root/runs/$problem_name"

if [[ ! -x "$runner" ]]; then
  echo "错误：找不到可执行的 Rethlas runner：$runner" >&2
  exit 1
fi

if [[ ! -f "$source_problem" ]]; then
  echo "错误：找不到问题文件：$source_problem" >&2
  echo "请先运行：./tools/rethlas/init_project.sh $project_name $problem_name" >&2
  exit 1
fi

if [[ -f "$generation_dir/results/$problem_id/blueprint_verified.md" ]]; then
  echo "错误：这个问题已经存在已验证结果，Rethlas 会直接停止而不会重新求解。" >&2
  echo "已有结果：$generation_dir/results/$problem_id/blueprint_verified.md" >&2
  echo "如果问题内容已改变，请使用新问题名，例如 ${problem_name}_v2。" >&2
  exit 1
fi

mkdir -p "$(dirname "$rethlas_problem")" "$local_result" "$local_run"
cp "$source_problem" "$rethlas_problem"

rm -rf "$rethlas_refs"
if [[ -d "$source_refs" ]]; then
  mkdir -p "$rethlas_refs"
  cp -a "$source_refs/." "$rethlas_refs/"
fi

sync_back() {
  local source
  local destination

  source="$generation_dir/results/$problem_id"
  if [[ -d "$source" ]]; then
    mkdir -p "$local_result"
    cp -a "$source/." "$local_result/"
  fi

  for artifact in memory logs downloads; do
    source="$generation_dir/$artifact/$problem_id"
    destination="$local_run/$artifact"
    if [[ -d "$source" ]]; then
      mkdir -p "$destination"
      cp -a "$source/." "$destination/"
    fi
  done

  {
    echo "problem_id=$problem_id"
    echo "source_problem=$source_problem"
    echo "rethlas_root=$RETHLAS_ROOT"
    echo "synced_at=$(date '+%Y-%m-%dT%H:%M:%S%z')"
  } > "$local_run/run-info.txt"

  echo
  echo "Rethlas 产物已同步回："
  echo "  证明结果：$local_result"
  echo "  运行记录：$local_run"
}

trap sync_back EXIT

echo "问题：$source_problem"
echo "Rethlas problem_id：$problem_id"
echo "结果将同步到：$local_result"
echo

if [[ -f "$CONDA_ROOT/etc/profile.d/conda.sh" ]]; then
  # shellcheck disable=SC1091
  source "$CONDA_ROOT/etc/profile.d/conda.sh"
  conda activate "$GENERATION_ENV"
else
  echo "错误：找不到 Conda：$CONDA_ROOT" >&2
  echo "请确认 Miniforge 安装位置，或设置 CONDA_ROOT。" >&2
  exit 1
fi

cd "$generation_dir"
MODEL="$MODEL" REASONING_EFFORT="$REASONING_EFFORT" \
  PROBLEM_FILE="data/$problem_id.md" "$runner"
