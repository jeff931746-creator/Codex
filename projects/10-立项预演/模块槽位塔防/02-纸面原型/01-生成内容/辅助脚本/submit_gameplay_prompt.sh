#!/bin/zsh

set -euo pipefail

PROMPT_FILE="/Users/mt/Documents/Codex/模块槽位塔防/模块槽位塔防_玩法图Prompts.md"
HANDOFF_SCRIPT="/Users/mt/Documents/Codex/gemini_web_handoff.sh"

usage() {
  cat <<'EOF'
Usage:
  submit_gameplay_prompt.sh <1-6> [--submit] [--print]

Examples:
  submit_gameplay_prompt.sh 1
  submit_gameplay_prompt.sh 3 --submit
  submit_gameplay_prompt.sh 2 --print

What it does:
  - extracts the selected image prompt from the prompt pack
  - sends it to Gemini web via gemini_web_handoff.sh

Notes:
  - add --submit to automatically send after pasting
  - without --submit, the prompt is pasted only
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
  1) section="## 图1：基础防线" ;;
  2) section="## 图2：掉落模块" ;;
  3) section="## 图3：安装第一个模块" ;;
  4) section="## 图4：第二模块触发联动" ;;
  5) section="## 图5：Build 成型" ;;
  6) section="## 图6：Boss 波检验" ;;
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
