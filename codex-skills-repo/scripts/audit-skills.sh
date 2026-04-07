#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_ROOT="$REPO_ROOT/skills"
has_error=0

for skill_dir in "$SKILLS_ROOT"/*; do
  [[ -d "$skill_dir" ]] || continue
  skill_name="$(basename "$skill_dir")"
  echo "== $skill_name =="

  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    echo "missing: SKILL.md"
    has_error=1
  else
    echo "ok: SKILL.md"
  fi

  if [[ ! -f "$skill_dir/agents/openai.yaml" ]]; then
    echo "warn: agents/openai.yaml"
  else
    echo "ok: agents/openai.yaml"
  fi

  if [[ -d "$skill_dir/scripts" ]]; then
    echo "info: has scripts/"
  fi

  if [[ -d "$skill_dir/references" ]]; then
    echo "info: has references/"
  fi
done

exit "$has_error"
