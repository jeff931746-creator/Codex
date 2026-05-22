---
# === 身份 ===
work_id: WORK-ANI-00422
work_name: 黑执事 Book of Circus
work_name_alt: []
media_type: ANI
year_first: 2014
year_range: [2014, 2015]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 19世纪英国维多利亚时代
cultural_paradigm: 恶魔契约+贵族暗黑美学
narrative_core: 复仇悬疑+主仆羁绊

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: mixed
t_can_carry: [T3, T5]
core_emotion_note: ""
core_conflict: 贵族少爷与恶魔执事在复仇中揭露马戏团黑暗秘密

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 悬疑
theme_secondary: [犯罪, 历史, 恐怖]
visual_tags: [维多利亚风, 古堡, 马戏团, 哥特氛围]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [恶魔执事优雅, 马戏团诡异, 维多利亚哥特, 少爷复仇眼神]
existing_games: [黑执事 幽灵与管家]
recommended_playstyles: []
risk_notes: [受众偏女性, 题材较冷]

# === 元数据 ===
source: deepseek-v4-flash + v0-migrate + tags
source_run_id: 2026-05-18-tags-enrich
evidence_level: B
review_status: auto
last_updated: 2026-05-18
# v0_duplicate_count: 3
---

## 迁移备注

本样本由 v0 markdown 表格迁移而来,LLM 阶段尚未补 SDT 三需求 / T 任务态 / core_conflict / material_hooks 重判。
迁移完成后 evidence_level = C,LLM 增量打标后升至 B。
