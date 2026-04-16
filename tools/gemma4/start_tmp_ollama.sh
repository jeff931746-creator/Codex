#!/usr/bin/env bash

set -euo pipefail

OLLAMA_BIN="${OLLAMA_BIN:-/tmp/Ollama.app/Contents/Resources/ollama}"
OLLAMA_HOME_DIR="${OLLAMA_HOME_DIR:-/tmp/ollama-home}"
export HOME="$OLLAMA_HOME_DIR"
export OLLAMA_MODELS="${OLLAMA_MODELS:-/tmp/ollama-models}"

if [[ ! -x "$OLLAMA_BIN" ]]; then
  echo "Ollama binary not found at: $OLLAMA_BIN" >&2
  echo "Download or unpack Ollama.app to /tmp first." >&2
  exit 1
fi

mkdir -p "$HOME" "$OLLAMA_MODELS"

exec "$OLLAMA_BIN" serve
