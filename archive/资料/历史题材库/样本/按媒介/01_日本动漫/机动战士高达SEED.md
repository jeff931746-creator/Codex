---
# === 身份 ===
work_id: WORK-ANI-00017
work_name: 机动战士高达SEED
work_name_alt: []
media_type: ANI
year_first: 2002
year_range: [2002, 2002]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 宇宙纪元战争
cultural_paradigm: 机动战士+基因调整者
narrative_core: 战争史诗+成长逆袭

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: [N-Rel]
rel_object: mixed
t_can_carry: [T2, T4]
core_emotion_note: ""
core_conflict: 基因调整者与自然人的种族战争，主角在战斗中寻找自我与和平

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 战争
theme_secondary: [未来战争, 机甲, 太空, 政治权谋]
visual_tags: [机甲, 星舰内部, 太空战场, 光束军刀]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [高达机体对决, 光束军刀斩击, 战舰出击场面, 角色驾驶舱特写]
existing_games: [高达SEED（PS2）, 高达SEED（GBA）, 高达SEED（手游）]
recommended_playstyles: []
risk_notes: [版权成本极高, 红海竞争]

# === 元数据 ===
source: deepseek-v4-flash + v0-migrate + tags
source_run_id: 2026-05-18-tags-enrich
evidence_level: B
review_status: auto
last_updated: 2026-05-18
# v0_duplicate_count: 2
---

## 迁移备注

本样本由 v0 markdown 表格迁移而来,LLM 阶段尚未补 SDT 三需求 / T 任务态 / core_conflict / material_hooks 重判。
迁移完成后 evidence_level = C,LLM 增量打标后升至 B。
