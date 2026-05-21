#!/usr/bin/env bash
# 每日 Git 状态检查
# 检测工作目录是否有超过 24 小时未提交的改动，发 macOS 通知。
# 由 launchd 每天定时调用，无需 token，零 AI 介入。

REPO="/Users/mt/Documents/Codex"
THRESHOLD_HOURS=24

cd "$REPO"

# 没有 git 仓库则退出
git rev-parse --git-dir > /dev/null 2>&1 || exit 0

# 检查是否有未提交的修改（tracked 文件）
modified=$(git status --porcelain | grep -cE '^[ MADRCU][MADRCU]' || true)

if [[ "$modified" -eq 0 ]]; then
    exit 0
fi

now=$(date +%s)
threshold=$(( THRESHOLD_HOURS * 3600 ))

# 找最老的 modified 文件的 mtime
oldest_mtime=$(git status --porcelain \
    | grep -E '^[ MADRCU][MADRCU]' \
    | awk '{print $NF}' \
    | while IFS= read -r f; do
        stat -f '%m' "$REPO/$f" 2>/dev/null || true
      done \
    | sort -n | head -1)

if [[ -n "$oldest_mtime" && $(( now - oldest_mtime )) -gt $threshold ]]; then
    osascript -e "display notification \"工作目录有 $modified 个文件超过 ${THRESHOLD_HOURS}h 未提交，请及时 commit。\" with title \"⚠️ Codex · Git 未提交\" sound name \"Basso\""
fi
