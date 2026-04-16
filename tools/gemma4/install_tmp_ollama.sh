#!/usr/bin/env bash

set -euo pipefail

OLLAMA_URL="${OLLAMA_URL:-https://ollama.com/download/Ollama-darwin.zip}"
ZIP_PATH="${ZIP_PATH:-/tmp/Ollama-darwin.zip}"
APP_DIR="${APP_DIR:-/tmp/Ollama.app}"
APP_PARENT="$(dirname "$APP_DIR")"

curl -L -o "$ZIP_PATH" "$OLLAMA_URL"
rm -rf "$APP_DIR"
unzip -q "$ZIP_PATH" -d "$APP_PARENT"

echo "Ollama is ready at: $APP_DIR"
