# Tools

This folder holds reusable utilities and local tool repos.

This folder and its children follow the root [`CLAUDE.md`](/Users/mt/Documents/Codex/CLAUDE.md) session protocol.

## Current Entries

- `codex-desktop-bridge/`: desktop bridge helpers used by this workspace
- `codex-skills-repo/`: skill source repository and catalog
- `feishu-codex-bridge/`: Feishu integration tooling
- `gemini-breakdown-worker/`: breakdown worker and prompts
- `gemma4/`: model-related helper scripts and notes

## Tool Directory Template

Reusable tool folders should stay small and purpose-built. Prefer this structure when adding or reorganizing a tool:

```text
tool-name/
  README.md
  scripts/
  config/
  docs/
  tests/
  tmp/
```

- `README.md`: what the tool is for, how to run it, and what it depends on.
- `scripts/`: executable or reusable scripts.
- `config/`: checked-in sample or non-secret configuration only.
- `docs/`: design notes and operating notes.
- `tests/`: repeatable checks and fixtures.
- `tmp/`: local scratch output, ignored or disposable.

Do not vendor runtimes, SDKs, package manager globals, downloaded installers, or binary bundles here unless the user explicitly approves them as workflow-critical.

`codex-skills-repo/skills/` follows the stricter skill package rules: each skill must have `SKILL.md`; optional runtime scripts go in `scripts/`; references go in `references/`; evaluation and test outputs stay in `evals/` and `tests/`; packaged `.skill` files must exclude `evals/` and `tests/`.
