---
# === 身份 ===
work_id: WORK-ANI-00255
work_name: 黑执事 II
work_name_alt: []
media_type: ANI
year_first: 2010
year_range: [2010, 2010]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 19世纪英国维多利亚时代
cultural_paradigm: 恶魔契约+哥特暗黑
narrative_core: 契约复仇+悬疑

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: virtual
t_can_carry: [T3, T2]
core_emotion_note: ""
core_conflict: 恶魔执事与少爷的契约羁绊，交织复仇与背叛的哥特悬疑

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 悬疑
theme_secondary: [犯罪, 历史, 奇幻]
visual_tags: [古堡, 维多利亚风, 黑色西装, 哥特暗黑, 契约纹章]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [恶魔执事优雅战斗, 维多利亚哥特庄园, 契约纹章与眼瞳, 血色玫瑰与黑礼服, 少爷的复仇眼神]
existing_games: []
recommended_playstyles: []
risk_notes: [版权成本高, 受众窄]

# === 元数据 ===
source: deepseek-v4-flash + v0-migrate + tags
source_run_id: 2026-05-18-tags-enrich
evidence_level: B
review_status: auto
last_updated: 2026-05-18
---

## 迁移备注

本样本由 v0 markdown 表格迁移而来,LLM 阶段尚未补 SDT 三需求 / T 任务态 / core_conflict / material_hooks 重判。
迁移完成后 evidence_level = C,LLM 增量打标后升至 B。
