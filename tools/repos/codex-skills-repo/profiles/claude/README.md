# Claude Profile

Use this profile to document or script how shared assets map into Claude-oriented runtime directories.

Typical responsibilities:

- shared skill linking
- Claude-specific prompts or agent entry files
- platform notes such as symlink vs junction behavior

Claude-facing entrypoints should preserve the shared control flow rather than invent a separate one.

That means Claude invocation should follow the same routing model defined by the shared rules and session protocol:

- `plan`
- `continue`
- `rewind`
- `compact`
- `clear`
- `subagent`

In particular:

- Claude should not bypass the mandatory `plan` gate, even for small tasks; small tasks just use shorter plans.
- Claude should classify the task into the shared flow types before execution begins.
- Claude should not advance to a later gate until the current gate is complete.
- Claude should keep formal `plan`, gate transition approval, and final delivery in the main agent.
- Claude should delegate read-heavy, noisy, or verification work through `subagent` when context isolation is the better choice.
- Claude-specific prompts and agent entry files should treat hooks as condition-action control triggers, not as a separate runtime-only behavior layer.
