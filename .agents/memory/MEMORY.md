# Memory Index

This index is a routing map for project memory in `/Users/mt/Documents/Codex-codex-work`.
Open linked files only when the current task matches them.

Current operating rules live in `PROJECT.md`, `.agents/AI-ONBOARDING.md`, `.agents/AI-ENTRYPOINTS.md`, and `.agents/rules/`.
Memory explains history, preferences, and task state; it does not override active rules.

## Always-Relevant Preferences

- [设计能力与思维模式](user_design_capability.md) - 用户按系统管线推进，不要把上游框架建设误判为回避决策。
- [先理解系统再给建议](feedback_system_vs_linear_thinking.md) - 给建议前先判断用户当前动作处在其系统逻辑的哪一段。
- [分析文档写作风格要求](feedback_writing_style.md) - 禁用互联网黑话，直接写机制与因果。
- [禁止借喻性术语](feedback_writing_no_borrowed_jargon.md) - 不用其他学科借来的比喻词。
- [分析先拆概念再核事实](feedback_challenge_framing_before_facts.md) - 外部论述先检验概念框架，再核事实。

## Current Task State

- [FF 当前工作交接](FF-当前工作交接.md) - 继续 FF/指尖战记/7日强社交功能链路时先读。
- [FF 军团优化1.0模块拆分交接](FF-军团优化1.0-模块拆分交接.md) - 继续军团优化 1.0、模块拆分、UE 界面线稿时先读；后续按一个界面一个界面给用户审核，不直接写入飞书文档。
- [战略库与信息收集体系](task_战略库与信息收集体系.md) - 信息收集体系、战略库、竞品库、来源、同步脚本相关任务。
- [梦幻西游战斗数据库](task_梦幻西游战斗数据库.md) - 行动权差兑换率、梦幻西游手游战斗数据、飞书 Base 相关任务。

## High-Use Review And Design Rules

- [GDD 只写设计层不写技术实现](feedback_gdd_no_tech_implementation.md) - 写或审 GDD 时只评功能行为、玩家可见响应、功能级契约。
- [评审评质量不评存在性](feedback_review_quality_not_existence.md) - 评审结论不能只看“有没有”，需判断质量与全局协调性。
- [游戏分析方法论短卡](feedback_game_analysis_methodology.md) - 系统拆解、独立玩法判断、新方向推导的检查点。
- [双约束推理短卡](methodology_dual_constraint_reasoning.md) - 推演候选必须同时验证结构合法性与体验闭环。
- [验证 LLM 打标质量必须用语义判分](feedback_llm_validation_semantic.md) - LLM 输出同义不同字时不要用字面匹配误判质量。

## Workflow And Tooling References

- [文件归属判断调查规范](feedback_file_placement_investigation.md) - 移动文件前先调查文件性质、创建背景和候选目录。
- [API Key 加载快速参考](reference_api_key_loading.md) - 本地脚本加载 LLM key 时按需读取；运行前仍需验证当前路径。
- [Skill 结构与打包规范](feedback_skill_structure.md) - 创建、评估、测试、打包 skill 时按需读取。
- [Git 提交备注偏好](feedback_git_commit_message.md) - commit message 用中文，并覆盖 staged 主要变化。
- [依赖侧修复优先](feedback_dependency_side_fix.md) - 环境/依赖类故障先查依赖侧。
- [严谨关口别抄近路](feedback_cut_corners_at_rigor_gates.md) - 严谨关口不要用记忆代核实、全局配置代安全验证、过早下无解结论。
- [lark-cli profile 快速参考](reference_lark_cli_profiles.md) - 需要选择本机 lark-cli profile 时按需读取；认证和 bot 状态必须现场验证。

## Historical Or On-Demand Only

No root-level historical-only memory files remain after the current cleanup passes.
Historical archived memory files were deleted on 2026-07-01 after review. Active project memory is the root-level index plus the linked root-level memory files.

The `archived/` directory is kept only as an empty future holding area.

## Hygiene

- Keep this file as a compact routing index, not a full memory catalog.
- Completed task states should move out of the startup index; moving files into `archived/` is a separate cleanup step.
- Historical entries may contain old workspace paths or runtime-specific details. Treat those as historical evidence unless the current task verifies them.
