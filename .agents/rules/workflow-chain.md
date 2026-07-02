# Workflow Chain Rules

Workflow layer architecture and capability lookup protocol for any AI agent working in `/Users/mt/Documents/Codex-codex-work`.

Detailed reference material lives in `.agents/references/workflow-chain-reference.md`. Use it when creating new projects, moving between workflow phases, or checking stage-specific process details.

## Layer Architecture

```text
reference/    rule layer - stable standards and templates; do not edit without permission
archive/      accumulation layer - approved methods, knowledge, and tools
workspace/    execution layer - task outputs and project work products
.agents/      agent-neutral operating layer - active project rules and shared hook logic
```

Knowledge promotion is one-way and requires approval:

`workspace/` -> `archive/经验/` -> `archive/方法论/` -> `reference/`

## Capability Lookup Protocol

Before work that needs a specialized capability, such as design documents, code, art requirements, reviews, or structured methodology:

1. Check `reference/部门标准/{能力}/`.
2. If a standard exists, follow it and do not invent unconfirmed additions.
3. If no standard exists, stop and tell the user:
   `需要 [X] 能力的标准，当前 reference/部门标准/{能力}/ 下暂无，是否建立？`
4. Do not create capability documents without a standard or explicit user approval.

Current known capability domains:

| Capability | Path |
|---|---|
| Project initiation | `reference/部门标准/立项/` |
| Design | `reference/部门标准/策划/` |
| Development | `reference/部门标准/开发/` |
| Art | `reference/部门标准/美术/` |

## Framework Accumulation

When the main conversation reaches consensus on any of the following, stop before continuing and decide whether to accumulate it:

- new conceptual framework
- first-principles inference result
- reusable criterion or method
- definition formed after repeated user correction
- new hierarchy or interface rule

| Type | Location |
|---|---|
| Standard, rule, field definition | `reference/部门标准/` |
| Methodology, inference process, criteria set | `archive/方法论/` |

Do not do the work first and backfill the framework later when the framework is needed as a prerequisite.

## Lark/Feishu Access Fallback

When accessing Lark/Feishu resources:

1. Use available MCP/app tools when present.
2. If MCP/app tools are unavailable, time out, or error, switch to the relevant `lark-*` skill or `lark-cli` command.
3. Do not report `无法访问飞书` only because MCP is disconnected; local `lark-cli` may still be usable.
