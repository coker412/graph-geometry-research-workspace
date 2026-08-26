#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

usage() {
  cat <<'EOF'
用法：
  ./tools/rethlas/init_project.sh <项目名> [问题名]

示例：
  ./tools/rethlas/init_project.sh example-project example-problem

这会创建：
  projects/example-project/rethlas/problems/example-problem.md
  projects/example-project/rethlas/problems/example-problem.refs/
  projects/example-project/rethlas/results/
  projects/example-project/rethlas/runs/
EOF
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage >&2
  exit 2
fi

project_name="$1"
problem_name="${2:-my_problem}"

if [[ ! "$project_name" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "错误：项目名只能包含字母、数字、点、下划线和连字符。" >&2
  exit 2
fi

if [[ ! "$problem_name" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "错误：问题名只能包含字母、数字、点、下划线和连字符。" >&2
  exit 2
fi

project_dir="$WORKSPACE_ROOT/projects/$project_name"
rethlas_dir="$project_dir/rethlas"
problem_file="$rethlas_dir/problems/$problem_name.md"
reference_dir="$rethlas_dir/problems/$problem_name.refs"

mkdir -p "$reference_dir" "$rethlas_dir/results" "$rethlas_dir/runs"

if [[ ! -f "$problem_file" ]]; then
  cp "$WORKSPACE_ROOT/templates/rethlas-problem.md" "$problem_file"
  echo "已创建问题模板：$problem_file"
else
  echo "问题文件已存在，未覆盖：$problem_file"
fi

echo "参考资料目录：$reference_dir"
echo "下一步：编辑问题文件，然后运行"
echo "  ./tools/rethlas/run_problem.sh $project_name $problem_name"
