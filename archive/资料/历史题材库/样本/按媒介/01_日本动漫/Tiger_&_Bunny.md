---
# === 身份 ===
work_id: WORK-ANI-00411
work_name: "TIGER & BUNNY"
work_name_alt: []
media_type: ANI
year_first: 2011
year_range: [2011, 2011]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 架空现代都市+英雄真人秀
cultural_paradigm: 超级英雄+企业赞助体系
narrative_core: 英雄搭档与职场成长

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: mixed
t_can_carry: [T3, T4]
core_emotion_note: ""
core_conflict: 英雄在赞助商规则下搭档合作，同时对抗超级罪犯与职场竞争

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 都市
theme_secondary: [职场, 友情, 喜剧]
visual_tags: [都市夜景, 霓虹灯, 摩天楼, 英雄变身, 机甲]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [英雄变身战斗, 搭档合体技, 企业赞助标志, 城市高楼跳跃]
existing_games: ["TIGER & BUNNY（手游）"]
recommended_playstyles: []
risk_notes: [版权成本中, 受众偏窄, IP热度下降]

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
