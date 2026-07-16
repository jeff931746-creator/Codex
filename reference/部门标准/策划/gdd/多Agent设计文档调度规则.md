# 多 Agent 设计文档调度规则

## 这份规则处理什么

本文件定义多 Agent GDD 写作的状态、上下文、返回、checkpoint 和恢复语义。阶段顺序见 `多Agent设计文档工作流.md`；所有策划选择必须遵守 `../策划决策权规则.md`。

## 路由与证据读取边界

主 Agent 在确认是否进入 GDD 写作流程时，只装配用户原始请求、目标与参考路径清单、工作区规则、执行入口、工作流、调度规则和可用能力。

业务证据由 G1 首次解释。主 Agent 在 G1 前不得提炼目的、手段、边界、对象、结构、独立功能或方案方向。已越界形成的解释不得作为工作流证据。

## 状态字典

状态 S 至少包含：

- confirmed_facts / unknown_facts
- candidate_design_purposes / candidate_means_frameworks
- candidate_design_objects / candidate_delivery_objects / candidate_structure_bases
- user_confirmations（U1-U5）
- confirmed_design_purpose / confirmed_exploration_boundary
- confirmed_means_framework / confirmed_design_object / confirmed_delivery_boundary / confirmed_structure_basis
- confirmed_features / confirmed_rules / confirmed_states / confirmed_ue
- direction_validation_pending_items / formal_gdd_blockers
- model_optimization_outputs / diff_check_reports / independent_review_reports
- stage_outputs / suggested_return_options / stage_snapshots / return_counters

`confirmed_*` 字段只能由对应用户确认生成，不能由 Agent 推荐、检查结论或 checkpoint 自行生成。

## 用户确认记录

U1-U5 的记录必须包含：

- confirmation_stage
- confirmed_object
- user_message_excerpt
- source=`user`
- target_artifact_hash 或对应输入版本
- recorded_at

Agent 不得根据沉默、上下文推断、历史选择或“继续分析”生成确认。用户一次合并确认多个节点时，仍需分别记录。

## 阶段快照与返回

进入 G1-G6、C4 或独立审核前记录状态快照。

Agent 发现问题时只记录：发现位置、证据、影响、可选返回阶段、各选项后果和推荐项。未获得用户决定前不得回滚或使后续产物失效。

用户决定返回后：

1. 回滚到用户指定阶段进入前的快照。
2. 追加用户决定和 Agent 报告。
3. 标记该阶段之后受影响的产物为待重做。
4. 从用户指定阶段继续。

## 上下文装配

每次调用 Agent 时，只装配当前阶段所需的已确认事实、未覆盖事实、用户确认结论、当前任务、当前原则、角色卡、禁止事项和输出要求。

用户确认节点不调用 Agent 代替决策。主 Agent 只把上一阶段材料整理为：候选、证据、影响、风险、推荐和待用户决定项。

## 模型文本优化与差异检查

DeepSeek 等模型只能作为 G5 后的文本优化工具并产出候选稿：

1. 只使用统一 LLM 入口。
2. 输入只包含 G5 草稿、U1-U3 确认结论、资料覆盖范围、待确认项、写作原则和优化提示词。
3. 不补玩法、奖励、数值、系统能力或项目事实。
4. 写入新文件或候选槽位，不覆盖用户确认版本。
5. 标记为候选稿，直到 U4 明确选择。

Agent 对候选稿只检查新增事实、信息丢失、结构污染、技术越界和规则归位，并把差异交给用户。Agent 不得自行选择 G5 原稿或优化稿。

## 同一问题重复出现时

问题重复按 `(发现阶段 -> 建议返回阶段 -> reason_hash)` 记录。相同问题第三次出现时，Agent 必须停止自动执行，向用户提供：

- 继续补资料。
- 降级为方向验证稿。
- 保留风险继续。
- 停止方向。

Agent 可以推荐，但只能由用户选择。

## 分段落盘

- U1 后：G1/G2 材料和用户确认的目的、循环、缺口、边界。
- U2 后：用户选择的手段、对象、交付边界和结构依据。
- U3 后：用户确认的功能、规则、状态和 UE 方向。
- G5-D 后：原稿、候选稿、模型输入摘要、提示词版本和差异报告。
- U4 后：用户确认的待检查正文版本。
- G6 后：与正文分离的交付状态检查报告。
- gdd-review 后：与正文分离的独立审核报告。
- U5 后：用户最终处理决定。

推荐位置：`workspace/tmp/agent-checkpoints/gdd-write/<doc-id>/`。

## 方向验证稿与正式 GDD

- G6 只报告交付状态，不决定是否通过。
- 正式 GDD 分支在 G6 后调用非生产者 `gdd-review`，审核只报告问题与建议。
- 方向验证稿和正式 GDD 都必须由 U5 决定是否交付、带风险接受、返回修改或停止。
- Agent 自检、G6、独立审核和外部模型均不能输出具有最终效力的“通过”。
- 用户决定带风险交付时，必须保留未关闭问题和影响说明，不得伪装为无风险通过。

## 交付前检查

- 工作流、调度规则和策划决策权规则已读。
- G1/G2/G3/G4/G5/C4/G6 有真实 Agent 证据；正式 GDD 另有独立审核证据。
- U1-U5 有明确用户确认记录。
- 正文与对应用户确认版本一致。
- 模型候选稿未覆盖用户确认版本。
- G6 和独立审核报告与正文分离。
- 未关闭问题、风险和用户处理决定已记录。
- Agent 没有替用户选择、打回、接受风险或宣布交付。
