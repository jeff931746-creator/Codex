---
# === 身份 ===
work_id: WORK-ANI-00212
work_name: Gungrave
work_name_alt: []
media_type: ANI
year_first: 2003
year_range: [2003, 2003]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 现代都市黑帮地下世界
cultural_paradigm: 枪械战斗+改造人体系
narrative_core: 复仇与背叛的兄弟情仇

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: real
t_can_carry: [T4, T2]
core_emotion_note: ""
core_conflict: 兄弟因黑帮权力反目，改造人复仇与背叛交织

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 犯罪
theme_secondary: [黑帮, 友情, 科幻]
visual_tags: [都市夜景, 枪林弹雨, 改造人, 黑色西装, 爆炸场面]


# === 评分(v0 已有)===
acquisition_score: 3

# === 素材与玩法 ===
material_hooks: [枪械战斗场面, 改造人变身, 黑帮火并, 兄弟对峙]
existing_games: [Gungrave（PS2）, Gungrave VR]
recommended_playstyles: []
risk_notes: [版权成本中等, 红海竞争]

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
