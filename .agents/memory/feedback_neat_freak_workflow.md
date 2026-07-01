---
name: feedback-neat-freak-workflow
description: delivery should include a bounded alignment check and change summary
metadata:
  node_type: memory
  type: feedback
---

# Delivery Alignment Check

Use this before final delivery on non-trivial tasks.
The point is a bounded cleanup pass, not broad repository reorganization.

## Check

- Confirm what files, rules, memory entries, scripts, or generated artifacts actually changed.
- Check whether related docs, rules, memory, and final summary disagree.
- Note temporary artifacts or stale statements instead of leaving them silent.
- Tell the user what changed, what did not change, and any remaining cleanup choices.

## Archive

Full original feedback, including the older runtime-specific wording, was archived at:

`archived/feedback_neat_freak_workflow_full_2026-07-01.md`
