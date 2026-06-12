#!/bin/bash
# 审批并执行 push —— 查看待推送内容，确认后 push
set -uo pipefail

REPO="/Users/mt/Documents/Codex"
PUSH_MARKER="$REPO/archive/tools/scripts/_logs/.pending_push"

cd "$REPO" || exit 1

ahead=$(git rev-list origin/main..main --count 2>/dev/null || echo 0)

if [ "$ahead" -eq 0 ]; then
    echo "没有待 push 的 commit。"
    [ -f "$PUSH_MARKER" ] && rm "$PUSH_MARKER"
    exit 0
fi

echo "=== 待 push: $ahead 个 commit ==="
echo
git log origin/main..main --oneline
echo
echo "---"

if [ -f "$PUSH_MARKER" ]; then
    echo "自动合并摘要:"
    cat "$PUSH_MARKER"
    echo "---"
fi

read -rp "确认 push 到 origin/main? [y/N] " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    git push origin main
    [ -f "$PUSH_MARKER" ] && rm "$PUSH_MARKER"
    echo "已 push。"
else
    echo "已取消。待 push 的 commit 保留在本地。"
fi
