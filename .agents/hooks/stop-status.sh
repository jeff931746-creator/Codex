#!/usr/bin/env bash
set -euo pipefail

project_dir="${AGENT_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
runtime="${AGENT_RUNTIME:-agent}"

status=$(git -C "$project_dir" status --short 2>/dev/null | grep -v '^\?' | grep -v 'worktrees/' || true)
untracked=$(git -C "$project_dir" status --short 2>/dev/null | grep '^?' | grep -v 'worktrees/' || true)

changed_count=0
untracked_count=0
[[ -n "$status" ]] && changed_count=$(echo "$status" | grep -c . || true)
[[ -n "$untracked" ]] && untracked_count=$(echo "$untracked" | grep -c . || true)
total=$((changed_count + untracked_count))

if [[ $total -gt 0 ]]; then
  echo "⚠️  ${runtime} 工作区有 ${total} 个未提交文件。任务完成后记得收尾检查 + commit。"
fi

exit 0

