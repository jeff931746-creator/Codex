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

## Hook Wrappers

`hooks/pretooluse-claude-readonly.py` is the recommended Codex `PreToolUse` hook command.

It reads the hook JSON payload from stdin and blocks write-capable tool calls that target Claude-owned paths. It is intentionally Codex-owned and does not read from or write to `.claude/hooks/`.

Configure it in Codex:

```text
Settings -> Hooks -> PreToolUse -> Add
Command: /Users/mt/Documents/Codex/tools/codex-guard/hooks/pretooluse-claude-readonly.py
Matchers: exec_command, apply_patch, write_stdin
```

Local smoke tests:

```bash
/Users/mt/Documents/Codex/tools/codex-guard/hooks/pretooluse-claude-readonly.py AGENTS.md
printf '{"tool_name":"exec_command","tool_input":{"cmd":"sed -i s/a/b/ .claude/rules/workflow-chain.md","workdir":"/Users/mt/Documents/Codex"}}' | /Users/mt/Documents/Codex/tools/codex-guard/hooks/pretooluse-claude-readonly.py
```
