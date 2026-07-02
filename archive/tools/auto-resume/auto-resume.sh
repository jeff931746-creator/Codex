#!/usr/bin/env bash
# auto-resume —— 额度受限时无人值守续接任务
# 用法:
#   auto-resume.sh start   <任务名> [间隔分钟，默认30] [最大次数，默认48]   # memory 任务模式，读 task_<任务名>.md
#   auto-resume.sh session <标签> <session_id> <工作目录> [间隔] [最大次数]  # 会话续接模式，接 claude 对话历史
#   auto-resume.sh stop    <标签>
#   auto-resume.sh run     <标签>      # 由 cron 调用，一般不手动跑
#   auto-resume.sh status  <标签>
#   auto-resume.sh list
#
# 停止条件（任一触发即注销 cron）：
#   1) claude 在回复最后单独输出一行 TASK_COMPLETE
#   2) 累计调用次数达到 <最大次数>
#   3) 手动 stop
set -euo pipefail

# cron 的 PATH 极简，补上 node 和 claude 所在目录，否则会静默失败
export PATH="/opt/homebrew/bin:/Users/mt/.local/npm/bin:$PATH"
CLAUDE=/Users/mt/.local/npm/bin/claude
PROJECT=/Users/mt/Documents/Codex
SELF="$PROJECT/archive/tools/auto-resume/auto-resume.sh"
BASE="$PROJECT/archive/tools/auto-resume"
LOGS="$BASE/_logs"
STATE="$BASE/_state"
PROMPTS="$BASE/prompts"

notify() { osascript -e "display notification \"$2\" with title \"auto-resume: $1\"" 2>/dev/null || true; }
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOGS/$TASK.log"; }

build_prompt() {
  if [[ -f "$PROMPTS/$TASK.txt" ]]; then
    cat "$PROMPTS/$TASK.txt"
  elif [[ -n "${SESSION_ID:-}" ]]; then
    # 会话续接模式：接的是这个对话已交代、未干完的活
    cat <<EOF
继续本对话里已经交代但还没做完的任务，向前推进。
只做你能确定、可验证的部分；遇到需要我来判断或拍板的地方，不要擅自决定，
说明卡在哪、需要什么决策，然后停下。
如果本对话已交代的任务全部做完、没有剩余工作，在回复最后单独输出一行：TASK_COMPLETE
EOF
  else
    cat <<EOF
运行 session-resume $TASK 恢复任务状态。
按恢复的状态向前推进任务，完成当前一个 gate 后停下，不要一次跑完整个任务。
推进前先确认本步是机械/可验证的工作；若下一步需要人来判断或拍板，不要擅自决定，
在回复里说明卡在哪、需要什么决策，然后停下。
如果整个任务已全部完成、没有任何剩余工作，在回复的最后单独输出一行：TASK_COMPLETE
EOF
  fi
}

cmd_run() {
  mkdir -p "$LOGS" "$STATE"
  local cnt_file="$STATE/$TASK.count" max_file="$STATE/$TASK.max"
  local cnt max
  cnt=$(cat "$cnt_file" 2>/dev/null || echo 0)
  max=$(cat "$max_file" 2>/dev/null || echo 48)
  cnt=$((cnt + 1))
  echo "$cnt" > "$cnt_file"

  # 会话续接模式：存在 .session 则用 claude --resume 接对话历史；否则用 session-resume 读 memory
  SESSION_ID=$(cat "$STATE/$TASK.session" 2>/dev/null || echo "")
  local cwd
  cwd=$(cat "$STATE/$TASK.cwd" 2>/dev/null || echo "$PROJECT")

  log "第 $cnt/$max 次尝试 …"
  local out rc=0
  if [[ -n "$SESSION_ID" ]]; then
    out=$(cd "$cwd" && "$CLAUDE" --resume "$SESSION_ID" -p "$(build_prompt)" 2>&1) || rc=$?
  else
    out=$(cd "$PROJECT" && "$CLAUDE" -p "$(build_prompt)" 2>&1) || rc=$?
  fi

  echo "$out" >> "$LOGS/$TASK.log"
  if [[ $rc -ne 0 ]]; then
    log "claude 退出码 $rc（可能被限流或出错），本次不推进，等待下次。"
    if [[ $cnt -ge $max ]]; then
      log "已达最大次数 $max，自动停止。"
      notify "$TASK" "达到最大次数 $max，已停止，请来查看"
      cmd_stop
    fi
    exit 0
  fi

  if echo "$out" | grep -q '^TASK_COMPLETE$'; then
    log "检测到 TASK_COMPLETE，任务完成，注销 cron。"
    notify "$TASK" "任务已完成 ✓"
    cmd_stop
    exit 0
  fi

  log "本次推进完成（未结束）。"
  if [[ $cnt -ge $max ]]; then
    log "已达最大次数 $max，自动停止。"
    notify "$TASK" "达到最大次数 $max，已停止，请来查看"
    cmd_stop
  fi
}

cmd_start() {
  local interval="${1:-30}" max="${2:-48}"
  mkdir -p "$STATE"
  echo 0 > "$STATE/$TASK.count"
  echo "$max" > "$STATE/$TASK.max"
  local marker="# auto-resume:$TASK"
  local line="*/$interval * * * * $SELF run $TASK >> $LOGS/$TASK.cron.log 2>&1 $marker"
  ( crontab -l 2>/dev/null | grep -v "$marker"; echo "$line" ) | crontab -
  log "已注册 cron：每 $interval 分钟一次，最多 $max 次。"
  echo "已启动 [$TASK]：每 $interval 分钟尝试一次，上限 $max 次。"
  echo "查看进度：$SELF status $TASK"
}

cmd_session() {
  # 会话续接模式：auto-resume.sh session <标签> <session_id> <工作目录> [间隔] [最大次数]
  local sid="${1:?需要 session_id}" cwd="${2:?需要工作目录}" interval="${3:-30}" max="${4:-48}"
  mkdir -p "$STATE"
  echo 0 > "$STATE/$TASK.count"
  echo "$max" > "$STATE/$TASK.max"
  echo "$sid" > "$STATE/$TASK.session"
  echo "$cwd" > "$STATE/$TASK.cwd"
  local marker="# auto-resume:$TASK"
  local line="*/$interval * * * * $SELF run $TASK >> $LOGS/$TASK.cron.log 2>&1 $marker"
  ( crontab -l 2>/dev/null | grep -v "$marker"; echo "$line" ) | crontab -
  log "已注册会话续接 cron：session=$sid cwd=$cwd 每 $interval 分钟，最多 $max 次。"
  echo "已启动会话续接 [$TASK]：每 $interval 分钟续接一次，上限 $max 次。"
  echo "查看进度：$SELF status $TASK"
}

cmd_stop() {
  local marker="# auto-resume:$TASK"
  crontab -l 2>/dev/null | grep -v "$marker" | crontab - || true
  rm -f "$STATE/$TASK.session" "$STATE/$TASK.cwd" 2>/dev/null || true
  log "已注销 cron。"
  echo "已停止 [$TASK]。"
}

cmd_status() {
  local cnt max
  cnt=$(cat "$STATE/$TASK.count" 2>/dev/null || echo "-")
  max=$(cat "$STATE/$TASK.max" 2>/dev/null || echo "-")
  echo "任务 [$TASK]  已尝试 $cnt/$max 次"
  echo "cron: $(crontab -l 2>/dev/null | grep "# auto-resume:$TASK" || echo '未注册')"
  echo "--- 最近日志 ---"
  tail -n 20 "$LOGS/$TASK.log" 2>/dev/null || echo "(无)"
}

cmd_list() {
  echo "当前注册的 auto-resume cron："
  crontab -l 2>/dev/null | grep "# auto-resume:" || echo "(无)"
}

main() {
  local action="${1:-}"
  case "$action" in
    list) cmd_list ;;
    run|start|stop|status|session)
      TASK="${2:?需要任务名}"; shift 2
      "cmd_$action" "$@" ;;
    *) echo "用法: $0 {start|stop|run|status|list} <任务名> [间隔分钟] [最大次数]"; exit 1 ;;
  esac
}
main "$@"
