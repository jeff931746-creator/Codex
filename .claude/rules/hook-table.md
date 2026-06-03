# Hook Table

运行时条件—动作触发表。与 [`plan-and-hook-model.md`](plan-and-hook-model.md) 配套：前者说明控制模型原理，本文件是可操作的查找表。

| 条件 | 动作 |
|---|---|
| 新任务或任务范围实质性变化 | `plan` |
| 任务尚未分类 | 分类任务流 |
| 请求含 `标准 / 流程 / 体系 / 框架 / 方法论 / 沉淀 / 长期管理`，或"知识库/机制库/题材库"等知识资产类库 | 默认 `knowledge-asset` + `strict`；进入 `governance-design` gate |
| `knowledge-asset` plan 缺少 3 项扫描清单（现有资产 / README / 脚本） | 拒绝 plan，停在 `plan` gate |
| `doc-change` 或 `implementation` plan 缺 gate 执行序列小节 | 拒绝 plan，停在 `plan` gate |
| `doc-change` 目标是策划/系统/玩法/战斗设计文档，且 `edit` gate 前未读 `GDD写作标准.md` | 阻断 `edit` gate；先读 `reference/部门标准/策划/current/GDD写作标准.md`，再重新确认 `target-inspection` 完成 |
| `doc-change` edit 产出设计文档但 `self-review` 未交子 agent | 阻断交付；先跑子 agent 审核；子 agent 必须使用 GDD 写作标准中的 Self-Review 判据 |
| 分类在任务中途发现错误 | rewind 到 `intake`；已产出物降为 `draft` |
| 当前 gate 未完成 | 停在当前 gate |
| 同任务，上下文 >30% | `compact` |
| 上下文 >60%，或失败分支 ≥ 3 | `clear` |
| 同一问题连续失败 ≥ 3 次 | `rewind` |
| 目标偏移成新任务 | `rewind` |
| 读密集 / 产出噪声大 / 仅验证类工作 | `subagent` |
| 编辑后涉及共享资产 | 本地验证 + Git review 后再推广 |
