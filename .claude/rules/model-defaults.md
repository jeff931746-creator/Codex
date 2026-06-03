# Model Defaults

子 agent 模型选型与推理配置，适用于所有 agent() 委派调用。

## 模型选型

| 场景 | 默认行为 | 说明 |
|---|---|---|
| 一般子 agent 委派 | 继承主 agent 模型（当前 sonnet-4-6） | 不传 model 参数；不要主动降级 |
| 快速信息提取 / 格式归一 / 简单校验 | `haiku` | 速度/成本优先，质量要求低时才用 |
| 超长推理链 / 高置信度判断 | `opus` | 仅在明确需要时指定，不默认使用 |

LLM API 任务（DeepSeek / SiliconFlow）的模型选型见 `.claude/rules/api-client-architecture.md`。

## 推理要求

- 多步推理任务（机制拆解、GDD 审核、证据链评估）：不要在 prompt 里限制思考步骤
- 结构化输出任务：要求子 agent 返回 JSON（schema 约束），不要解析自由文本
- 文档审核类任务：prompt 里必须提供标准文件路径，不让子 agent 自定义评审维度

## Sub-agent Prompt 最低要求

每次委派必须包含：
1. 精确问题（不预埋方向和结论）
2. 相关文件路径
3. 任务类型 + 当前 gate
4. 输出格式约束（≤300 tokens 摘要 / bullet findings / JSON）

套娃检查（委派前强制）：「我对这个问题有结论了吗？」
- 有结论 → 本地完成，不委派
- 无结论 → 开放问题给子 agent，prompt 里不预埋方向
