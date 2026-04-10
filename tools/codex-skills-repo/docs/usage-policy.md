# Usage Policy

This document defines the default team rules for using the shared agent-team repository.

## Core Principles

1. Shared assets live in the central repository and are versioned with Git.
2. Runtime directories are projection layers, not edit targets.
3. Keep entry-layer context short; move long material into `references/`.
4. Prefer selective routing over global injection.
5. Project-specific behavior should not be promoted to global defaults too early.

## Source Of Truth

- Shared `rules/`, `skills/`, `references/`, `profiles/`, and `overrides/` are maintained in this repository.
- Runtime directories such as `~/.codex/skills`, `.cursor/`, or `.claude/` are generated, linked, or mapped from here.
- Team members must not manually copy shared content into business repositories unless a project explicitly adopts a local override.

## Daily Usage Rules

1. Reuse shared assets first.
2. Only add project-local assets when the need is genuinely project-specific.
3. Do not paste large standards into global prompt entry files.
4. When a long explanation is required, store it in `references/` and link to it from the entry asset.
5. Do not edit runtime symlink targets through the runtime path; edit the repository path directly.

## Runtime Constraints

1. `~/.codex/skills` is a runtime surface only.
2. Shared skill directories in runtime should be symlinks or mapped projections from this repo.
3. Broken runtime links must be fixed before further editing or rollout.
4. Runtime directories must not become alternate sources of truth.

## Contribution Constraints

1. No direct copy-paste distribution of shared assets across projects.
2. No Git submodule embedding of the central agent-team repository into business repositories by default.
3. No long-form policy text in `rules/`.
4. No project-secret, customer-secret, or environment-secret content in shared global assets.
5. No editor-specific duplication when the content itself is editor-agnostic.

## Role Expectations

### Contributors

- Use existing shared rules and skills before creating new ones.
- Raise a proposal when shared behavior is missing or repeatedly reimplemented.
- Keep project-specific experiments in project-local space until reuse is proven.

### Project Owners

- Decide whether a need belongs in `overrides/` or should be upstreamed to shared assets.
- Prevent one project's special case from silently becoming a team-wide default.

### Maintainers

- Keep shared assets minimal, discoverable, and validated.
- Reject changes that add unnecessary global context or duplicate existing assets.
- Ensure runtime mappings remain healthy after structural changes.
