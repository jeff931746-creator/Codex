# Plan And Hook Model

This document defines a lightweight control model for how the workspace should move from mandatory plan review into execution, delegation, and state-control actions.

It is meant to complement the existing session protocol in [`/Users/mt/Documents/Codex/CLAUDE.md`](/Users/mt/Documents/Codex/CLAUDE.md) and the agent-role guidance in [`/Users/mt/Documents/Codex/archive/skills/docs/agent-skill-topology.md`](/Users/mt/Documents/Codex/tools/codex-skills-repo/docs/agent-skill-topology.md).

## Why This Exists

The current workspace already has strong routing for `subagent`, `compact`, `clear`, and `rewind`, but it does not yet have a single place that explains:

- why the main agent should delegate bounded work
- how subagent work should stay out of the main context
- why every task must present a plan before execution
- what a `hook` means in this system

This file fills that gap without introducing a heavy framework.

It works together with the task flow matrix in [`task-flow-matrix.md`](/Users/mt/Documents/Codex/.claude/rules/task-flow-matrix.md).

For detailed main-agent vs subagent rules, see [`agent-delegation-policy.md`](/Users/mt/Documents/Codex/.claude/rules/agent-delegation-policy.md).

## Core Definitions

### Main Agent

The main agent owns:

- understanding the user request
- decomposing the task
- deciding whether to continue locally or delegate
- enforcing the plan review gate before execution
- integrating results and presenting the final answer

The main agent should not dump every intermediate exploration step into the shared context.
The main agent also owns the only formal channel for user approval.

### Subagent

A subagent is an execution boundary for bounded work.

Use a subagent when:

- the task needs to read many files without editing them
- the task produces a lot of intermediate output
- the task is review, verification, or document drafting
- the work can be isolated and reported back as a short conclusion

The contract is:

- the main agent sends a precise question
- the subagent works in isolated context
- the subagent returns only the conclusion, not the whole process

This keeps the main thread usable and reduces context pollution.
Subagents can support the plan, but they do not own the task-level formal plan.

### Plan

`plan` is the mandatory first step for every new task.

Its job is to prevent the system from jumping straight into execution and to force an explicit agreement on the approach before work begins.

For every new task, the agent should:

1. summarize the intended approach
2. name the files, systems, or behaviors likely to change
3. surface non-obvious tradeoffs or risks
4. wait for user approval before executing

Small and reversible tasks still need `plan`, but the plan can be extremely short.

### Task Flow

Every task must also be assigned a flow type before execution begins.

The default shared flow types are:

- `analysis`
- `doc-change`
- `implementation`
- `review`
- `collection`

The flow type determines which mandatory gates must be completed in order.

### Hook

A `hook` is a condition-action trigger:

`if condition -> perform action`

In this workspace, hooks are best understood as control logic, not as a separate platform runtime.

Examples:

- if context usage becomes high, trigger `compact`
- if the task becomes noisy, trigger `subagent`
- if the goal drifts, trigger `rewind`
- if the task affects shared assets, trigger `plan` and review gates

## Default Operating Model

Use the following sequence:

1. Understand the request.
2. Present `plan`.
3. Choose the task flow.
4. Wait for approval.
5. Execute gate by gate within the approved plan and chosen flow.
6. Delegate bounded work to subagents when it improves context isolation.
7. Let hooks enforce compaction, delegation, rewind, or review behavior when trigger conditions are met.

This gives the system a clear bias:

- do not skip the alignment step
- do not skip task classification
- do not skip unfinished gates
- keep trivial-task plans short
- do not overfill the main context with exploratory noise
- do not execute broad changes without an approval gate

## Runtime Consistency

This model is runtime-agnostic.

If the request is being handled through a Claude-oriented entrypoint, the same process still applies:

- Claude calls should follow the same `plan -> continue / rewind / compact / clear / subagent` routing model.
- Claude-specific entry files should not skip the mandatory `plan` gate just because the runtime is different.
- Claude-specific entry files should not skip task classification or mandatory stage gates.
- Claude should use the same subagent isolation standard: send bounded work out, keep process noise out of the main context, and bring back concise conclusions only.
- Claude runtime mappings may change exposure and wiring, but they should not change the control semantics unless an explicit override is documented.

## When To Use `plan`

`plan` is always required for a new task.

The difference is only how long the `plan` needs to be:

- use a short `plan` when the task is tiny, reversible, and obvious
- use a fuller `plan` when the task is multi-step, high-impact, shared-asset, or hard to undo

If the task direction changes materially after approval, the agent should stop and re-enter `plan`.

## Mandatory Stage Gates

Every flow is gate-based.

Rules:

- the next gate cannot begin until the current gate is complete
- if the current gate is blocked, stay in that gate and resolve the blockage, `rewind`, or re-`plan`
- subagents do not weaken gate discipline; they inherit a scoped flow and current gate
- task state should always show `task type`, `current gate`, `completed gates`, and `next gate`

## When To Trigger `subagent`

Prefer `subagent` when:

- reading three or more files without editing is likely
- the task produces long intermediate analysis
- the main thread only needs a short answer or decision
- verification, scoring, or drafting can be done in parallel

Subagents should be assigned with:

- a precise question
- the relevant file paths
- an output constraint such as a short summary or structured result

They should also be assigned a scoped `task type` and `current gate`.

## Recommended Hook Table

| Condition | Action |
|---|---|
| New task or material scope change | `plan` |
| Task not yet classified | classify task flow |
| Current gate not complete | stay in gate |
| Same task, context usage above 60% | `compact` |
| Context usage above 80% or too many failed branches | `clear` |
| Repeated failure on the same problem | `rewind` |
| Goal drift into a new task | `rewind` |
| Read-heavy, noisy, or verification-only work | `subagent` |
| Shared-asset change after editing | local validation + Git review before rollout |

## Boundaries And Non-Goals

- A hook is not the same thing as a skill.
- A hook is not the same thing as a runtime profile.
- `profiles/` should continue to describe runtime exposure and mapping, not control policy.
- Runtime-specific mappings such as Claude should preserve the shared routing semantics unless a documented override says otherwise.
- Do not create a new agent for every workflow just because a hook exists.
- Do not turn trivial-task plans into long essays; the rule is mandatory planning, not mandatory verbosity.
- Do not treat gate transitions as implicit; they should be explicit and inspectable.
- Do not let subagents take over main-agent responsibilities such as formal plan submission, gate transition approval, or final delivery ownership.

## Recommended Wording

Use the following short-form language when describing the model:

- `Agent defines ownership and execution boundary.`
- `Main agent delegates bounded work to subagents.`
- `Subagents run in isolated context and return only concise conclusions.`
- `Plan is the mandatory approval gate: draft first, review first, execute after approval.`
- `Hooks are condition-action triggers that enforce routing, approval, compaction, and safety behavior.`
