#!/bin/zsh

set -euo pipefail

BASE_DIR="/Users/mt/Documents/Codex/模块槽位塔防"
PROMPT_SCRIPT="$BASE_DIR/submit_gameplay_prompt.sh"
HANDOFF_SCRIPT="/Users/mt/Documents/Codex/gemini_web_handoff.sh"
OUTPUT_DIR="$BASE_DIR/玩法图片输出"

image_name() {
  case "$1" in
    1) echo "图1_基础防线" ;;
    2) echo "图2_掉落模块" ;;
    3) echo "图3_安装第一个模块" ;;
    4) echo "图4_第二模块触发联动" ;;
    5) echo "图5_Build成型" ;;
    6) echo "图6_Boss波检验" ;;
    *) return 1 ;;
  esac
}

chrome_js() {
  local script="$1"
  osascript -e "tell application \"Google Chrome\" to tell active tab of front window to execute javascript \"$script\""
}

current_image_count() {
  chrome_js 'Array.from(document.images).filter(i=>i.src.includes(\"googleusercontent.com/gg/\")).length.toString()'
}

last_image_rect() {
  chrome_js '(function(){var imgs=Array.from(document.images).filter(i=>i.src.includes(\"googleusercontent.com/gg/\")); if(!imgs.length){return \"NO_IMAGE\";} var img=imgs[imgs.length-1]; img.scrollIntoView({block:\"center\"}); var r=img.getBoundingClientRect(); return [Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)].join(\",\");})()'
}

viewport_metrics() {
  chrome_js '[window.screenX,window.screenY,window.outerHeight,window.innerHeight].join(\",\")'
}

wait_for_new_image() {
  local before_count="$1"
  local tries=0
  while [[ $tries -lt 90 ]]; do
    sleep 4
    local now_count
    now_count="$(current_image_count)"
    if [[ "$now_count" =~ ^[0-9]+$ ]] && (( now_count > before_count )); then
      echo "$now_count"
      return 0
    fi
    tries=$((tries + 1))
  done
  return 1
}

save_latest_image_screenshot() {
  local output_path="$1"
  local rect metrics
  rect="$(last_image_rect)"
  metrics="$(viewport_metrics)"

  if [[ "$rect" == "NO_IMAGE" ]]; then
    echo "No image found on the page." >&2
    return 1
  fi

  local rect_left rect_top rect_width rect_height
  local screen_x screen_y outer_h inner_h
  IFS=',' read -r rect_left rect_top rect_width rect_height <<< "$rect"
  IFS=',' read -r screen_x screen_y outer_h inner_h <<< "$metrics"

  local chrome_bar_height=$(( outer_h - inner_h ))
  local abs_x=$(( screen_x + rect_left ))
  local abs_y=$(( screen_y + chrome_bar_height + rect_top ))

  screencapture -x -R"${abs_x},${abs_y},${rect_width},${rect_height}" "$output_path"
}

submit_one() {
  local index="$1"
  local name prompt folder prompt_file image_file before_count after_count

  name="$(image_name "$index")"
  folder="$OUTPUT_DIR/$name"
  mkdir -p "$folder"

  prompt="$(zsh "$PROMPT_SCRIPT" "$index" --print)"
  prompt_file="$folder/prompt.txt"
  image_file="$folder/${name}.png"
  printf '%s\n' "$prompt" > "$prompt_file"

  before_count="$(current_image_count)"
  if [[ ! "$before_count" =~ ^[0-9]+$ ]]; then
    before_count=0
  fi

  printf '%s' "$prompt" | zsh "$HANDOFF_SCRIPT" --submit
  after_count="$(wait_for_new_image "$before_count")"
  sleep 2
  save_latest_image_screenshot "$image_file"
  echo "Saved $name to $image_file (image count: $before_count -> $after_count)"
}

usage() {
  cat <<'EOF'
Usage:
  generate_and_save_gameplay_series.sh
  generate_and_save_gameplay_series.sh 1 3 5

What it does:
  - sends one gameplay prompt at a time to Gemini web
  - waits for a new generated image to appear
  - saves a cropped screenshot into the matching gameplay folder
  - then continues to the next image
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

mkdir -p "$OUTPUT_DIR"

if [[ $# -eq 0 ]]; then
  set -- 1 2 3 4 5 6
fi

for index in "$@"; do
  submit_one "$index"
done
