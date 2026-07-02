#!/usr/bin/env bash
set -euo pipefail

hook_dir="$(cd "$(dirname "$0")" && pwd)"
input=$(cat)

result=$(echo "$input" | python3 "$hook_dir/check-commit-message.py" 2>/dev/null || true)

if [[ "$result" == FAIL:* ]]; then
  preview="${result#FAIL:}"
  echo "❌ commit message 必须用中文概括所有改动（当前：\"${preview}\"）" >&2
  exit 2
fi

exit 0
