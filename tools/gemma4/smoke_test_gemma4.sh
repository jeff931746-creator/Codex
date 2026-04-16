#!/usr/bin/env bash

set -euo pipefail

MODEL="${1:-gemma4:e2b}"
PROMPT="${2:-请只回复：部署成功。}"
HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"

payload="$(
  python3 - "$MODEL" "$PROMPT" <<'PY'
import json
import sys

print(json.dumps({
    "model": sys.argv[1],
    "messages": [{"role": "user", "content": sys.argv[2]}],
    "stream": False,
}, ensure_ascii=False))
PY
)"

curl -fsS "$HOST/api/chat" -d "$payload"
