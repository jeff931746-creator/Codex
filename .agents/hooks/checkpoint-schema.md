# Independent Review Checkpoint Schema

Strict `knowledge-asset` changes require a passing independent review checkpoint before delivery.

Checkpoint path:

`workspace/tmp/agent-checkpoints/<runtime>/independent-review.json`

The matching reviewed scope is stored at:

`workspace/tmp/agent-checkpoints/<runtime>/independent-review-scope.json`

Required fields:

| Field | Required value |
|---|---|
| `flow_intensity` | `strict` |
| `task_type` | `knowledge-asset` |
| `result` | `pass` |
| `reviewer_role` | contains `independent` |
| `reviewer_runtime` | non-empty and different from `main_runtime` |
| `main_runtime` | runtime that authored/integrates the change |
| `scope_paths` | reviewed long-term asset paths; directories cover descendants |
| `required_plan_fields.similar_assets_scanned` | non-empty |
| `required_plan_fields.rules_read` | non-empty |
| `required_plan_fields.automation_entrypoints_checked` | non-empty |
| `required_plan_fields.source_of_truth` | non-empty |
| `reviewed_diff_hash` | current diff hash for the reviewed scope |
| `blocking_findings` | empty list |
| `expires_at` | future timestamp |

The checkpoint proves a review gate happened for the current scoped diff. Any later edit inside the reviewed scope changes the hash and invalidates the checkpoint. It does not replace human judgment or user approval.
