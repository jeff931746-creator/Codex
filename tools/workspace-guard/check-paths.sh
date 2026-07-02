#!/usr/bin/env bash
set -u

WORKSPACE_ROOT="/Users/mt/Documents/Codex-codex-work"
TMP_ROOT="/private/tmp"
SESSION_TMP_ROOT="/private/var/folders/wy/ljz0r5_s13lf1jlpv88cn7h00000gn/T"

usage() {
  printf 'Usage: %s <path> [...]\n' "$0" >&2
}

to_absolute_path() {
  local target="$1"
  local dir base

  case "$target" in
    /*) printf '%s\n' "$target" ;;
    *)
      dir=$(dirname "$target")
      base=$(basename "$target")
      if [ -d "$dir" ]; then
        (cd "$dir" && printf '%s/%s\n' "$(pwd -P)" "$base")
      else
        printf '%s/%s\n' "$(pwd -P)" "$target"
      fi
      ;;
  esac
}

is_allowed_path() {
  local absolute="$1"

  case "$absolute" in
    "$WORKSPACE_ROOT"|"$WORKSPACE_ROOT"/*) return 0 ;;
    "$TMP_ROOT"|"$TMP_ROOT"/*) return 0 ;;
    "$SESSION_TMP_ROOT"|"$SESSION_TMP_ROOT"/*) return 0 ;;
    *) return 1 ;;
  esac
}

if [ "$#" -eq 0 ]; then
  usage
  exit 64
fi

blocked=0
for path in "$@"; do
  absolute=$(to_absolute_path "$path")
  if ! is_allowed_path "$absolute"; then
    printf 'Blocked write target outside independent workspace: %s -> %s\n' "$path" "$absolute" >&2
    blocked=1
  fi
done

if [ "$blocked" -ne 0 ]; then
  printf 'Workspace guard failed. Use /Users/mt/Documents/Codex-codex-work or an allowed temp directory, unless the user explicitly requested external work.\n' >&2
  exit 1
fi

printf 'Workspace guard passed: %s path(s) are inside allowed local roots.\n' "$#"
