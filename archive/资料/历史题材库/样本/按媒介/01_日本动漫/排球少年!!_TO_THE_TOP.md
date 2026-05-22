---
# === 身份 ===
work_id: WORK-ANI-00180
work_name: 排球少年!! TO THE TOP
work_name_alt: []
media_type: ANI
year_first: 2020
year_range: [2020, 2020]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 现代日本高中排球部
cultural_paradigm: 体育竞技+团队协作
narrative_core: 成长逆袭+热血竞技

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: [N-Rel]
rel_object: mixed
t_can_carry: [T2, T4]
core_emotion_note: ""
core_conflict: 乌野高中排球部从弱队逆袭全国大赛，对抗强敌与自我突破

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 体育竞技
theme_secondary: [篮球, 校园, 友情]
visual_tags: [校园, 操场, 青春热血, 赛场高空俯视]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [扣杀瞬间特写, 飞身救球慢镜, 团队击掌庆祝, 赛场高空俯视]
existing_games: [排球少年!! 飞翔吧！]
recommended_playstyles: []
risk_notes: [红海, 版权成本高]

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
