---
# === 身份 ===
work_id: WORK-ANI-00008
work_name: Fate/Zero
work_name_alt: []
media_type: ANI
year_first: 2011
year_range: [2011, 2012]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 架空现代都市+魔术世界
cultural_paradigm: 英灵召唤+宝具对决体系
narrative_core: 圣杯战争+权谋博弈

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: real
t_can_carry: [T4, T5]
core_emotion_note: ""
core_conflict: 七组御主与英灵争夺圣杯，背后是魔术师家族的千年阴谋

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 奇幻
theme_secondary: [政治权谋, 战争, 悬疑, 都市]
visual_tags: [黑暗压抑, 魔法阵, 武器对决, 都市夜景]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [英灵宝具对决, 圣杯战争仪式, 魔术礼装特效, 黑暗都市夜景]
existing_games: [Fate/Grand Order, Fate/Extella]
recommended_playstyles: []
risk_notes: [版权成本高, 红海竞争]

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
