#!/usr/bin/env bash
set -euo pipefail

hook_dir="$(cd "$(dirname "$0")" && pwd)"
input=$(cat)

result=$(echo "$input" | python3 "$hook_dir/warn-dangerous.py" 2>/dev/null || true)

if [[ "$result" == DANGER:* ]]; then
  summary="${result#DANGER:}"
  echo "⛔ 危险操作被拦截：${summary}" >&2
  echo "如需执行，请在消息中明确说明这是你的意图（如：'我确认要执行这个操作'）。" >&2
  exit 2
fi

exit 0
