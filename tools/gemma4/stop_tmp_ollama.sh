#!/usr/bin/env bash

set -euo pipefail

pkill -f '/tmp/Ollama.app/Contents/Resources/ollama serve' || true
