#!/bin/zsh

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  gemini_web_handoff.sh --file /path/to/prompt.txt [--submit]
  gemini_web_handoff.sh --text "prompt content" [--submit]
  printf '%s' "prompt content" | gemini_web_handoff.sh [--submit]

What it does:
  1. Copies the prompt to your clipboard
  2. Opens Gemini web in Google Chrome
  3. Waits for the page to load
  4. Pastes the prompt into the chat box

Notes:
  - Default behavior is paste only, without auto-submitting.
  - Add --submit if you want the script to press Return after pasting.
  - macOS may ask you to allow Terminal/Codex to control your computer.
EOF
}

prompt_text=""
auto_submit="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      [[ $# -ge 2 ]] || { echo "Missing value for --file" >&2; exit 1; }
      prompt_text="$(cat "$2")"
      shift 2
      ;;
    --text)
      [[ $# -ge 2 ]] || { echo "Missing value for --text" >&2; exit 1; }
      prompt_text="$2"
      shift 2
      ;;
    --submit)
      auto_submit="true"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$prompt_text" ]] && [[ ! -t 0 ]]; then
  prompt_text="$(cat)"
fi

if [[ -z "${prompt_text//[[:space:]]/}" ]]; then
  echo "No prompt provided." >&2
  usage >&2
  exit 1
fi

if [[ ! -d "/Applications/Google Chrome.app" ]]; then
  echo "Google Chrome.app was not found in /Applications." >&2
  exit 1
fi

printf '%s' "$prompt_text" | pbcopy
prompt_b64="$(printf '%s' "$prompt_text" | base64 | tr -d '\n')"

osascript <<EOF
tell application "Google Chrome"
  activate
  if (count of windows) = 0 then
    make new window
  end if
  set currentUrl to URL of active tab of front window
  if currentUrl does not contain "gemini.google.com/app" then
    set URL of active tab of front window to "https://gemini.google.com/app"
  end if
end tell

delay 4

tell application "Google Chrome"
  tell active tab of front window
    execute javascript "(function(){var btn=Array.from(document.querySelectorAll('button')).find(b=>((b.innerText||'').trim()==='🖼️ 制作图片')||((b.innerText||'').trim()==='制作图片')||((b.getAttribute('aria-label')||'').includes('制作图片'))); if(btn){btn.click(); return 'IMAGE_MODE';} return 'NO_IMAGE_MODE_BUTTON';})()"
  end tell
end tell

delay 0.8

tell application "Google Chrome"
  tell active tab of front window
    execute javascript "(function(){var box=document.querySelector('[role=\"textbox\"][aria-label*=\"Gemini\"]')||document.querySelector('[role=\"textbox\"]')||document.querySelector('[contenteditable=\"true\"]'); if(!box){return 'NO_BOX';} var bytes=Uint8Array.from(atob('$prompt_b64'), c => c.charCodeAt(0)); var text=new TextDecoder().decode(bytes); box.click(); box.focus(); box.innerHTML=''; box.textContent=text; box.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertText',data:text})); return 'OK';})()"
  end tell
end tell

delay 0.6

tell application "System Events"
  keystroke "v" using command down
end tell

delay 0.4
EOF

if [[ "$auto_submit" == "true" ]]; then
  send_result="$(osascript <<EOF
tell application "Google Chrome"
  tell active tab of front window
    execute javascript "(function(){var btn=Array.from(document.querySelectorAll('button')).find(b=>((b.innerText||'').trim()==='发送')||((b.getAttribute('aria-label')||'').includes('发送'))); if(btn){btn.click(); return 'OK';} return 'NO_SEND';})()"
  end tell
end tell
EOF
)"
  echo "$send_result"
  if [[ "$send_result" != "OK" ]]; then
    /usr/bin/osascript -e 'tell application "System Events" to key code 36'
  fi
  echo "Prompt pasted into Gemini web and submitted."
  exit 0
fi

echo "Prompt pasted into Gemini web."
