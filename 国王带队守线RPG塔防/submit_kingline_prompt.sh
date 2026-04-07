#!/bin/zsh

set -euo pipefail

PROMPT_FILE="/Users/mt/Documents/Codex/国王带队守线RPG塔防/玩法概念图Prompts.md"
HANDOFF_SCRIPT="/Users/mt/Documents/Codex/gemini_web_handoff.sh"

usage() {
  cat <<'EOF'
Usage:
  submit_kingline_prompt.sh <1-6> [--submit] [--print]

Examples:
  submit_kingline_prompt.sh 1 --submit
  submit_kingline_prompt.sh 3 --print
EOF
}

[[ $# -ge 1 ]] || { usage >&2; exit 1; }

index="$1"
shift || true

auto_submit="false"
print_only="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --submit)
      auto_submit="true"
      shift
      ;;
    --print)
      print_only="true"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

case "$index" in
  1) section="## 图1：最后防线建立" ;;
  2) section="## 图2：前场打野抢高价值目标" ;;
  3) section="## 图3：三选一成长后队伍明显变强" ;;
  4) section="## 图4：神器让 Build 发生跃迁" ;;
  5) section="## 图5：Build成型后回防顶住Boss" ;;
  6) section="## 图6：王国绝境反转与胜利定格" ;;
  *) echo "Image index must be between 1 and 6." >&2; exit 1 ;;
esac

prompt_text="$(
  awk -v marker="$section" '
    $0 == marker { in_section=1; next }
    in_section && /^## / { exit }
    in_section { print }
  ' "$PROMPT_FILE" | awk '
    /^```text$/ { capture=1; next }
    /^```$/ && capture { exit }
    capture { print }
  '
)"

if [[ -z "${prompt_text//[[:space:]]/}" ]]; then
  echo "Failed to extract prompt for section: $section" >&2
  exit 1
fi

if [[ "$print_only" == "true" ]]; then
  printf '%s\n' "$prompt_text"
  exit 0
fi

if [[ "$auto_submit" == "true" ]]; then
  printf '%s' "$prompt_text" | zsh "$HANDOFF_SCRIPT" --submit
else
  printf '%s' "$prompt_text" | zsh "$HANDOFF_SCRIPT"
fi
