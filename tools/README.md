# Tools

This folder holds reusable workflow utilities, local service bridges, model helpers, and tool source repos.

This folder and its children follow the root [`CLAUDE.md`](/Users/mt/Documents/Codex/CLAUDE.md) session protocol.

## Canonical Structure

```text
tools/
  README.md
  bin/
  scripts/
  services/
  model-tools/
  repos/
  archived/
```

- `bin/`: command shims or lightweight executable entrypoints.
- `scripts/`: standalone scripts that do not need their own project folder.
- `services/`: long-running bridges or service-style tools with state, environment files, or launchd integration.
- `model-tools/`: local model, runtime, and model smoke-test helpers.
- `repos/`: larger tool repositories, source-of-truth projects, or reusable packages.
- `archived/`: retired tools kept only for reference. Do not add active tools here.

## Current Entries

- `services/codex-desktop-bridge/`: desktop bridge helpers used by this workspace.
- `services/feishu-codex-bridge/`: Feishu integration tooling.
- `model-tools/gemma4/`: temporary Ollama and Gemma helper scripts.
- `repos/codex-skills-repo/`: skill source repository and catalog.
- `repos/breakdown-worker/`: breakdown worker and prompts.
- `scripts/daily_ad_combo_collector.py`: daily ad-combo collection helper.
- `scripts/daily_game_breakdown.py`: daily game breakdown helper.
- `scripts/claude_api.py`: Claude API helper script.
- `scripts/gemini_web_handoff.sh`: Gemini web handoff helper.
- `youtube-transcript-collector/`: YouTube channel subtitle collection and transcript aggregation helper.

## Compatibility Links

Several older workflows and docs still reference the previous root-level paths. Keep these root-level symlinks until all callers have migrated:

- `codex-desktop-bridge -> services/codex-desktop-bridge`
- `feishu-codex-bridge -> services/feishu-codex-bridge`
- `gemma4 -> model-tools/gemma4`
- `codex-skills-repo -> repos/codex-skills-repo`
- `breakdown-worker -> repos/breakdown-worker`
- `daily_ad_combo_collector.py -> scripts/daily_ad_combo_collector.py`
- `daily_game_breakdown.py -> scripts/daily_game_breakdown.py`
- `claude_api.py -> scripts/claude_api.py`
- `gemini_web_handoff.sh -> scripts/gemini_web_handoff.sh`

Prefer the canonical paths for new references. Use the compatibility links only to avoid breaking existing automation.

## Safety Rules

- Do not delete `.env`, `.state`, `node_modules/`, `cloudflared/`, launchd plists, or local runtime state unless the active tool README explicitly says it is safe.
- Do not vendor runtimes, SDKs, package manager globals, downloaded installers, or binary bundles here unless the user explicitly approves them as workflow-critical.
- Do not move service folders without checking absolute-path references in launchd, `.env`, README files, and scripts.
- Remove `.DS_Store`, `__pycache__/`, and other reproducible cache files during cleanup.

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

`repos/codex-skills-repo/skills/` follows the stricter skill package rules: each skill must have `SKILL.md`; optional runtime scripts go in `scripts/`; references go in `references/`; evaluation and test outputs stay in `evals/` and `tests/`; packaged `.skill` files must exclude `evals/` and `tests/`.
