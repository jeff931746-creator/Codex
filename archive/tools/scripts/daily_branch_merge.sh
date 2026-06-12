#!/bin/bash
# 每日自动合并无冲突分支 + 清理已合并 worktree/分支
# cron: 0 23 * * * /Users/mt/Documents/Codex/archive/tools/scripts/daily_branch_merge.sh
set -o pipefail

REPO="/Users/mt/Documents/Codex"
LOG_DIR="$REPO/archive/tools/scripts/_logs"
LOG_FILE="$LOG_DIR/branch_merge_$(date +%Y-%m-%d).log"
PUSH_MARKER="$LOG_DIR/.pending_push"

export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

mkdir -p "$LOG_DIR"

log() { echo "[$(date +%H:%M:%S)] $1" | tee -a "$LOG_FILE"; }

notify() {
    osascript -e "display notification \"$2\" with title \"$1\"" 2>/dev/null
}

cd "$REPO" || { log "FATAL: 无法进入 $REPO"; exit 1; }

current_branch=$(git symbolic-ref --short HEAD 2>/dev/null)
if [ "$current_branch" != "main" ]; then
    log "SKIP: 当前分支是 $current_branch，不是 main，跳过"
    exit 0
fi

log "=== 开始每日分支合并 ==="

# 暂存未提交改动
stashed=false
if ! git diff --quiet || ! git diff --cached --quiet; then
    git stash push -m "daily-merge-auto-stash-$(date +%Y%m%d)" --include-untracked 2>>"$LOG_FILE"
    stashed=true
    log "已暂存未提交改动"
fi

git fetch origin 2>>"$LOG_FILE"

# 收集活跃 worktree 分支名（用换行分隔的字符串代替关联数组）
active_wt_branches=""
while IFS= read -r line; do
    branch=$(echo "$line" | awk '{print $3}' | tr -d '[]')
    [ -n "$branch" ] && active_wt_branches="$active_wt_branches|$branch"
done < <(git worktree list | tail -n +2)

merged_count=0
conflict_count=0
skipped_count=0
merged_list=""
conflict_list=""

while IFS= read -r branch; do
    branch=$(echo "$branch" | sed 's/^[* +]*//')
    [ -z "$branch" ] && continue

    # 跳过有活跃 worktree 的分支
    if echo "$active_wt_branches" | grep -qF "$branch"; then
        skipped_count=$((skipped_count + 1))
        log "SKIP: $branch — 有活跃 worktree"
        continue
    fi

    # merge --no-commit 做干跑检测
    if git merge --no-commit --no-ff "$branch" >>"$LOG_FILE" 2>&1; then
        git commit --no-edit >>"$LOG_FILE" 2>&1
        merged_count=$((merged_count + 1))
        merged_list="$merged_list $branch"
        log "MERGED: $branch"
    else
        git merge --abort 2>/dev/null
        conflict_count=$((conflict_count + 1))
        conflict_list="$conflict_list $branch"
        log "CONFLICT: $branch — 跳过"
    fi
done < <(git branch --no-merged main | grep 'claude/')

# 清理已合并的 worktree
cleaned_wt=0
while IFS= read -r line; do
    wt_path=$(echo "$line" | awk '{print $1}')
    wt_branch=$(echo "$line" | awk '{print $3}' | tr -d '[]')

    [ "$wt_path" = "$REPO" ] && continue

    if git branch --merged main 2>/dev/null | grep -qF "$wt_branch"; then
        git worktree remove "$wt_path" --force 2>>"$LOG_FILE" && cleaned_wt=$((cleaned_wt + 1))
        log "REMOVED worktree: $(basename "$wt_path")"
    fi
done < <(git worktree list | tail -n +2)

# 清理已合并的分支
cleaned_br=0
while IFS= read -r branch; do
    branch=$(echo "$branch" | sed 's/^[* +]*//')
    [ -z "$branch" ] && continue
    git branch -D "$branch" >>"$LOG_FILE" 2>&1 && cleaned_br=$((cleaned_br + 1))
done < <(git branch --merged main | grep 'claude/')

# 恢复暂存
if [ "$stashed" = true ]; then
    git stash pop >>"$LOG_FILE" 2>&1 || log "WARN: stash pop 有冲突，需手动处理"
fi

# 汇总
ahead=$(git rev-list origin/main..main --count 2>/dev/null || echo 0)
summary="合并 ${merged_count} 个分支，清理 ${cleaned_wt} 个 worktree + ${cleaned_br} 个分支"

if [ "$conflict_count" -gt 0 ]; then
    summary="$summary，${conflict_count} 个有冲突待处理"
fi

log "=== 完成：$summary ==="
log "=== 待 push: $ahead 个 commit ==="

# 通知 + push 审批
if [ "$ahead" -gt 0 ]; then
    cat > "$PUSH_MARKER" <<EOF
date: $(date +%Y-%m-%d)
commits_ahead: $ahead
merged:$merged_list
conflicts:$conflict_list
EOF

    notify "Codex Git 待审批" "$summary | $ahead 个 commit 待 push"
    log "已发送 push 审批通知"
elif [ "$merged_count" -gt 0 ] || [ "$cleaned_wt" -gt 0 ] || [ "$cleaned_br" -gt 0 ]; then
    notify "Codex Git 清理完成" "$summary"
fi

log "=== 结束 ==="
