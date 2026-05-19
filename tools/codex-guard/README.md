# Codex Guard

This directory contains small safeguards for Codex-only workflow checks.

`check-paths.sh` rejects write targets under Claude-owned paths and deprecated local knowledge paths.

Claude-owned paths:

- `.claude/` inside this workspace
- `/Users/mt/.claude/`
- any target path containing a `.claude` path segment

Deprecated local paths:

- `/Users/mt/Documents/Codex/research/`

Use `workspace/tmp/` for drafts, `workspace/projects/` for project work, and `archive/` for reusable materials.

Use it before Codex-controlled commands that may create, edit, move, delete, format, or sync files. Claude does not need to use this guard and remains free to own its `.claude` files.

Examples:

```bash
bash /Users/mt/Documents/Codex/tools/codex-guard/check-paths.sh AGENTS.md tools/codex-guard/check-paths.sh
bash /Users/mt/Documents/Codex/tools/codex-guard/check-paths.sh .claude/rules/workflow-chain.md
bash /Users/mt/Documents/Codex/tools/codex-guard/check-paths.sh research/资料/example.md
```

The first command exits `0`; the second and third exit non-zero.

## Hook Wrappers

`hooks/pretooluse-claude-readonly.py` is the recommended Codex `PreToolUse` hook command.

It reads the hook JSON payload from stdin and blocks write-capable tool calls that target Claude-owned paths. It is intentionally Codex-owned and does not read from or write to `.claude/hooks/`.

`hooks/claude-flow-check.py` records whether Codex has read the Claude-owned rule and memory sources for the current turn. It blocks mutating tool calls until Claude rule intake is complete, and stores temporary state in `/private/tmp/codex-claude-flow-check-state.json`.

It also guards long-term knowledge assets. Writes to these targets require explicit write authorization in the current user prompt:

- `/Users/mt/Documents/Codex/archive/方法论/`
- `/Users/mt/Documents/Codex/archive/资料/人群簇库/`
- `/Users/mt/Documents/Codex/archive/资料/买量组合库/`
- `/Users/mt/Documents/Codex/reference/部门标准/`
- Markdown files whose basename contains `标准`, `方法论`, or `总表`

Accepted authorization words include `写入`, `沉淀`, `更新`, `整理`, `修改`, `保存`, `落到`, `加到`, `改文档`, and similar destination-oriented write verbs. Discussion prompts such as `为什么...`, `怎么...`, `是否...`, or `要不要...` do not authorize writes by themselves.

Configure it in Codex:

```text
Settings -> Hooks -> PreToolUse -> Add
Command: /Users/mt/Documents/Codex/tools/codex-guard/hooks/pretooluse-claude-readonly.py
Matchers: exec_command, apply_patch, write_stdin

Settings -> Hooks -> UserPromptSubmit / PreToolUse / Stop -> Add
Command: /Users/mt/Documents/Codex/tools/codex-guard/hooks/claude-flow-check.py
```

Local smoke tests:

```bash
/Users/mt/Documents/Codex/tools/codex-guard/hooks/pretooluse-claude-readonly.py AGENTS.md
printf '{"tool_name":"exec_command","tool_input":{"cmd":"sed -i s/a/b/ .claude/rules/workflow-chain.md","workdir":"/Users/mt/Documents/Codex"}}' | /Users/mt/Documents/Codex/tools/codex-guard/hooks/pretooluse-claude-readonly.py
rm -f /private/tmp/codex-claude-flow-check-state.json
printf '{"hook_event_name":"UserPromptSubmit","prompt":"为什么这个规则不成立"}' | /Users/mt/Documents/Codex/tools/codex-guard/hooks/claude-flow-check.py
python3 - <<'PY' | /Users/mt/Documents/Codex/tools/codex-guard/hooks/claude-flow-check.py
import json
print(json.dumps({"tool_name":"apply_patch","input":"*** Begin Patch\n*** Update File: /Users/mt/Documents/Codex/archive/方法论/example.md\n@@\n+x\n*** End Patch\n"}, ensure_ascii=False))
PY
printf '{"hook_event_name":"UserPromptSubmit","prompt":"把这个规则写入方法论文档"}' | /Users/mt/Documents/Codex/tools/codex-guard/hooks/claude-flow-check.py
```
