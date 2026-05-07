# Agent Delegation Policy

This document defines the detailed ownership split between the main agent and subagents.

Use it together with:

- [`plan-and-hook-model.md`](/Users/mt/Documents/Codex/tools/codex-skills-repo/references/plan-and-hook-model.md)
- [`task-flow-matrix.md`](/Users/mt/Documents/Codex/tools/codex-skills-repo/references/task-flow-matrix.md)

## Core Principle

The main agent owns task control.

Subagents own bounded work only.

In short:

- main agent controls `plan`, flow, gates, and final delivery
- subagents perform scoped analysis, execution, verification, or review

## Hard Ownership Rules

### Main Agent Owns

- task-level formal `plan`
- task classification
- current gate and next gate decisions
- whether a gate is complete
- whether the task must `rewind`, `compact`, `clear`, or re-`plan`
- user-facing approval requests
- final integrated answer
- final decision to switch from one flow type to another

### Subagent Owns

- a bounded scoped question
- a bounded scoped write or read task
- evidence gathering
- isolated review or verification
- isolated comparison, extraction, normalization, or scoring
- a local subtask summary

### Subagent Must Not Own

- the task-level formal `plan`
- gate transition approval
- the final declaration that the whole task is complete
- scope changes for the parent task
- direct replacement of the main agent's user-facing conclusion

Subagents may propose a local sub-plan, but it is only advisory until the main agent adopts it.

## Mandatory Delegation Triggers

The main agent should delegate when any of the following is true:

- three or more files need to be read without editing
- two or more templates, samples, or competing structures need comparison
- the step will generate long intermediate reasoning that the main thread does not need to keep
- the step is verification, review, scoring, or consistency checking
- the step can be parallelized into independent bounded questions
- the step is repetitive extraction, collection, normalization, or schema mapping
- the main thread already has enough context to synthesize, but not enough room to also keep all exploration detail
- the current gate is one where evidence, inspection, or cross-checking is the main work

## Main Agent Should Usually Stay Local When

- presenting the formal `plan`
- asking for user approval
- deciding task type
- deciding whether a gate is complete
- synthesizing already-collected evidence into a final answer
- closing the current flow and opening a new flow
- making a small local fix whose context cost is trivial

## Gate-Level Delegation Guidance

### `analysis`

Recommended owner by gate:

1. `intake` -> main agent
2. `plan` -> main agent
3. `evidence` -> subagent preferred; mandatory if the step is read-heavy or multi-source
4. `synthesis` -> main agent
5. `review` -> subagent preferred
6. `delivery` -> main agent

### `doc-change`

Recommended owner by gate:

1. `intake` -> main agent
2. `plan` -> main agent
3. `target-inspection` -> subagent preferred; mandatory if many files or standards must be inspected
4. `edit` -> main agent by default, or worker subagent if the write scope is clearly bounded
5. `self-review` -> subagent preferred
6. `validation` -> subagent or local deterministic checks
7. `delivery` -> main agent

### `implementation`

Recommended owner by gate:

1. `intake` -> main agent
2. `plan` -> main agent
3. `context-inspection` -> subagent preferred
4. `implementation` -> main agent or worker subagent with clear ownership
5. `validation` -> subagent or local deterministic checks
6. `review` -> subagent preferred
7. `delivery` -> main agent

### `review`

Recommended owner by gate:

1. `intake` -> main agent
2. `plan` -> main agent
3. `target-inspection` -> subagent preferred
4. `findings` -> reviewer subagent preferred
5. `cross-check` -> subagent or main agent, depending on conflict complexity
6. `delivery` -> main agent

### `collection`

Recommended owner by gate:

1. `intake` -> main agent
2. `plan` -> main agent
3. `schema-check` -> main agent
4. `collection` -> subagent preferred
5. `normalization` -> subagent preferred
6. `validation` -> subagent preferred
7. `delivery` -> main agent

## Context Budget Rules

The main thread should keep only:

- task type
- current gate
- completed gates
- next gate
- approved plan
- confirmed conclusions
- user-visible risks and options

The main thread should avoid keeping:

- long exploratory notes
- raw file-by-file reading logs
- repeated speculative branches
- large comparison tables unless the final answer truly needs them
- verbose subagent work process

If a step would create that kind of noise, delegate it.

## Subagent Output Contract

Every subagent task should specify:

- the exact question
- the relevant files or scope
- the task type
- the current gate
- the desired output format
- the maximum summary length, unless structured output is better

Preferred return formats:

- summary <= 300 tokens
- bullet findings
- compact table
- structured JSON when post-processing matters

The subagent should return conclusions, not a full diary of its process.

## Formal Plan Rule

The task-level formal `plan` must come from the main agent.

This means:

- the main agent may consult subagents before writing the plan
- the main agent may include subagent findings in the plan
- the user should approve the main agent's plan, not a subagent's raw output

If a subagent proposes a better route, the main agent should restate it as the official plan before execution continues.

## Gate Transition Rule

Only the main agent can declare:

- `current gate complete`
- `move to next gate`
- `task type changed`
- `re-enter plan`

A subagent can report that its scoped work is complete, but that is not the same as approving the parent task's next gate.

## Conflict And Retry Handling

If a subagent result is insufficient:

1. keep the parent task in the same gate
2. either re-delegate with a narrower question or resolve locally
3. do not advance the gate until the missing requirement is satisfied

If multiple subagents disagree:

1. do not let either result become the final answer directly
2. the main agent compares the evidence
3. if needed, run a focused follow-up delegation
4. the main agent then publishes the integrated result

## Recommended Short Rule

Use this wording when you need the policy in one paragraph:

`Main agent owns the formal plan, task type, gate transitions, and final delivery. Subagents handle bounded heavy work such as evidence gathering, comparison, review, and verification. Delegate when analysis would create noise or context bloat; keep synthesis, approval, and final gate decisions in the main agent.`
