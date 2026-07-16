# Independent Review Checkpoint Schema

Strict `knowledge-asset` changes require a completed independent inspection checkpoint before delivery. The reviewer reports findings but does not approve or reject the change; unresolved findings require an explicit user decision.

Checkpoint path:

`workspace/tmp/agent-checkpoints/<runtime>/independent-review.json`

The matching reviewed scope is stored at:

`workspace/tmp/agent-checkpoints/<runtime>/independent-review-scope.json`

Required fields:

| Field | Required value |
|---|---|
| `flow_intensity` | `strict` |
| `task_type` | `knowledge-asset` |
| `result` | `reviewed` |
| `reviewer_role` | contains `independent` |
| `reviewer_runtime` | non-empty and different from `main_runtime` |
| `main_runtime` | runtime that authored/integrates the change |
| `scope_paths` | reviewed long-term asset paths; directories cover descendants |
| `required_plan_fields.similar_assets_scanned` | non-empty |
| `required_plan_fields.rules_read` | non-empty |
| `required_plan_fields.automation_entrypoints_checked` | non-empty |
| `required_plan_fields.source_of_truth` | non-empty |
| `reviewed_diff_hash` | current diff hash for the reviewed scope |
| `findings` | list of findings; may be empty |
| `user_message_excerpt` | required when `findings` is not empty; this excerpt is the user decision and must match a user-authored runtime message |
| `expires_at` | future timestamp |

The checkpoint proves an independent inspection happened for the current scoped diff. Any later edit inside the reviewed scope changes the hash and invalidates the checkpoint. It does not grant the reviewer decision authority and does not replace user approval.
