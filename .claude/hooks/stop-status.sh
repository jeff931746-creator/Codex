#!/usr/bin/env bash
# Hook 3: Stop 时工作区状态播报
# 触发：Stop 事件（Claude 每次响应结束）
# 作用：有未提交改动时提醒，工作区干净时静默

set -euo pipefail

# 找到项目根目录
PROJECT_DIR="/Users/mt/Documents/Codex"

# 获取 git status（只看修改/新增/删除，不看 untracked 的 worktree 目录）
status=$(git -C "$PROJECT_DIR" status --short 2>/dev/null | grep -v '^\?' | grep -v 'worktrees/' || true)
untracked=$(git -C "$PROJECT_DIR" status --short 2>/dev/null | grep '^?' | grep -v 'worktrees/' | grep -v '.claude/worktrees' || true)

changed_count=0
untracked_count=0
[[ -n "$status" ]] && changed_count=$(echo "$status" | grep -c . || true)
[[ -n "$untracked" ]] && untracked_count=$(echo "$untracked" | grep -c . || true)
total=$((changed_count + untracked_count))

if [[ $total -gt 0 ]]; then
  echo "⚠️  工作区有 ${total} 个未提交文件。任务完成后记得 neat-freak + commit。"
fi

exit 0
