#!/usr/bin/env bash
set -eu
exec zsh "$(cd "$(dirname "$0")" && pwd)/scripts/gemini_web_handoff.sh" "$@"
