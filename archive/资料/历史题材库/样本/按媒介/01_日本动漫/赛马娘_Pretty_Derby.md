---
# === 身份 ===
work_id: WORK-ANI-00067
work_name: 赛马娘 Pretty Derby
work_name_alt: []
media_type: ANI
year_first: 2023
year_range: [2023, 2024]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 架空现代赛马世界
cultural_paradigm: 赛马竞技+偶像养成
narrative_core: 追逐梦想与竞技成长

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: [N-Rel]
rel_object: virtual
t_can_carry: [T2, T3]
core_emotion_note: ""
core_conflict: 赛马娘们为成为最强赛马偶像而竞逐，同时建立深厚羁绊

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 体育竞技
theme_secondary: [友情, 校园]
visual_tags: [赛道冲刺, 胜利舞台, 马耳马尾, 决胜服, 校园青春]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [赛马娘奔跑英姿, 胜利舞台演出, 马耳马尾动态, 赛道冲刺瞬间, 角色专属决胜服]
existing_games: [赛马娘 Pretty Derby（手游）]
recommended_playstyles: []
risk_notes: [版权成本高, 红海竞争]

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
