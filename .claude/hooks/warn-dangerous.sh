#!/usr/bin/env bash
# Hook 2: 危险命令拦截
# 触发：PreToolUse / Bash 工具
# 作用：拦截高风险操作，要求用户明确确认

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
input=$(cat)

result=$(echo "$input" | python3 "$HOOK_DIR/warn-dangerous.py" 2>/dev/null || true)

if [[ "$result" == DANGER:* ]]; then
  summary="${result#DANGER:}"
  echo "⛔ 危险操作被拦截：${summary}" >&2
  echo "如需执行，请在消息中明确说明这是你的意图（如：'我确认要执行这个操作'）。" >&2
  exit 2
fi

exit 0
