# Codex Guard

This directory contains small safeguards for Codex-only workflow checks.

`check-paths.sh` rejects write targets under Claude-owned paths:

- `.claude/` inside this workspace
- `/Users/mt/.claude/`
- any target path containing a `.claude` path segment

Use it before Codex-controlled commands that may create, edit, move, delete, format, or sync files. Claude does not need to use this guard and remains free to own its `.claude` files.

Examples:

```bash
bash /Users/mt/Documents/Codex/tools/codex-guard/check-paths.sh AGENTS.md tools/codex-guard/check-paths.sh
bash /Users/mt/Documents/Codex/tools/codex-guard/check-paths.sh .claude/rules/workflow-chain.md
```

The first command exits `0`; the second exits non-zero.
