#!/usr/bin/env bash
set -u

usage() {
  printf 'Usage: %s <path> [...]\n' "$0" >&2
}

has_claude_segment() {
  case "$1" in
    .claude|.claude/*|*/.claude|*/.claude/*) return 0 ;;
    *) return 1 ;;
  esac
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

is_protected_path() {
  local raw="$1"
  local absolute

  if has_claude_segment "$raw"; then
    return 0
  fi

  absolute=$(to_absolute_path "$raw")
  case "$absolute" in
    /Users/mt/.claude|/Users/mt/.claude/*) return 0 ;;
    /Users/mt/Documents/Codex/.claude|/Users/mt/Documents/Codex/.claude/*) return 0 ;;
    *) return 1 ;;
  esac
}

if [ "$#" -eq 0 ]; then
  usage
  exit 64
fi

blocked=0
for path in "$@"; do
  if is_protected_path "$path"; then
    printf 'Blocked Codex write target: %s\n' "$path" >&2
    blocked=1
  fi
done

if [ "$blocked" -ne 0 ]; then
  printf 'Codex must treat .claude paths as read-only. Ask the user or use a Codex-owned file instead.\n' >&2
  exit 1
fi

printf 'Codex guard passed: %s path(s) are outside Claude-owned locations.\n' "$#"
