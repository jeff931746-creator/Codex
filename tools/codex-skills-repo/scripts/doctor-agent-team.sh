#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_SKILLS_DIR="${1:-$HOME/.codex/skills}"
has_error=0

check_dir() {
  local dir="$1"
  if [[ -d "$REPO_ROOT/$dir" ]]; then
    echo "ok: $dir/"
  else
    echo "missing: $dir/"
    has_error=1
  fi
}

echo "== repo layout =="
check_dir "rules"
check_dir "skills"
check_dir "references"
check_dir "profiles"
check_dir "overrides"
check_dir "scripts"

echo
echo "== runtime links =="
for skill_dir in "$REPO_ROOT"/skills/*; do
  [[ -d "$skill_dir" ]] || continue
  skill_name="$(basename "$skill_dir")"
  runtime_path="$RUNTIME_SKILLS_DIR/$skill_name"

  if [[ ! -L "$runtime_path" ]]; then
    echo "missing-link: $runtime_path"
    has_error=1
    continue
  fi

  current_target="$(readlink "$runtime_path")"
  if [[ "$current_target" != "$skill_dir" ]]; then
    echo "wrong-link: $runtime_path -> $current_target"
    has_error=1
    continue
  fi

  if [[ ! -e "$runtime_path" ]]; then
    echo "broken-link: $runtime_path"
    has_error=1
    continue
  fi

  echo "ok: $runtime_path"
done

echo
echo "== skill structure =="
"$REPO_ROOT/scripts/audit-skills.sh" || has_error=1

exit "$has_error"
