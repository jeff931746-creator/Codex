#!/usr/bin/env bash

set -euo pipefail

OLLAMA_BIN="${OLLAMA_BIN:-/tmp/Ollama.app/Contents/Resources/ollama}"
OLLAMA_HOME_DIR="${OLLAMA_HOME_DIR:-/tmp/ollama-home}"
export HOME="$OLLAMA_HOME_DIR"
export OLLAMA_MODELS="${OLLAMA_MODELS:-/tmp/ollama-models}"
MODEL="${1:-gemma4:e2b}"

if [[ ! -x "$OLLAMA_BIN" ]]; then
  echo "Ollama binary not found at: $OLLAMA_BIN" >&2
  exit 1
fi

mkdir -p "$HOME" "$OLLAMA_MODELS"

exec "$OLLAMA_BIN" pull "$MODEL"
