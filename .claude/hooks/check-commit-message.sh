#!/usr/bin/env bash
# Hook 1: git commit 中文检查
# 触发：PreToolUse / Bash 工具
# 作用：确保 commit message 首行包含中文字符，否则阻断

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
input=$(cat)

result=$(echo "$input" | python3 "$HOOK_DIR/check-commit-message.py" 2>/dev/null || true)

if [[ "$result" == FAIL:* ]]; then
  preview="${result#FAIL:}"
  echo "❌ commit message 必须用中文概括所有改动（当前：\"${preview}\"）" >&2
  exit 2
fi

exit 0
