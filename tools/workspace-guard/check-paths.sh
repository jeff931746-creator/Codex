#!/usr/bin/env bash
# Compatibility wrapper; the shared implementation also runs on Windows.
set -eu
script_dir="$(cd "$(dirname "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$script_dir/check_paths.py" "$@"
fi
exec python "$script_dir/check_paths.py" "$@"
