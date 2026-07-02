# Runtime Adapter Notes

This folder holds examples for wiring AI runtimes to the shared project contract.

## Required Entry

Every runtime should be configured to read one of these project entries before task work:

1. `AGENTS.md`
2. `.agents/AI-ONBOARDING.md`
3. `.agents/AI-ENTRYPOINTS.md`
4. A runtime-specific thin pointer such as `CODEX.md` or `CLAUDE.md`

The runtime-specific pointer must remain thin. It should redirect to `.agents/AI-ONBOARDING.md` and `.agents/AI-ENTRYPOINTS.md` instead of copying or redefining workflow logic.

## Required Enforcement

If the runtime supports hook or policy wiring, configure it to use `.agents/hooks.json` or an adapter in this folder.

If the runtime does not support hooks, put the same requirements in the runtime's system prompt, project prompt, or startup checklist:

- work only in `/Users/mt/Documents/Codex-codex-work` unless the user explicitly names another target;
- read `.agents/AI-ONBOARDING.md` before non-trivial work;
- read `.agents/AI-ENTRYPOINTS.md` for the current concrete source list and paths;
- use `.agents/memory/` for project memory;
- do not write project rules, memory, checkpoints, task state, or handoff notes to runtime-private directories;
- run `tools/workspace-guard/check-paths.sh` before file-changing shell commands when target paths are known.
- when context usage exceeds the high-water mark during a task, set `workspace/tmp/agent-checkpoints/<runtime>/context-pressure.json` to `pending-next-task`; before starting the next task, produce a continuation handoff and only then resume risky work.

Hook support gives physical blocking. Without hook support, the onboarding contract is still mandatory, but enforcement is procedural.
