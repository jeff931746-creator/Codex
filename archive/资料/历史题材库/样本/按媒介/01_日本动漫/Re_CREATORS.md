---
# === 身份 ===
work_id: WORK-ANI-00303
work_name: "Re:CREATORS"
work_name_alt: []
media_type: ANI
year_first: 2017
year_range: [2017, 2017]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 现代东京+异世界穿越
cultural_paradigm: 造物主与角色混战
narrative_core: 穿越互斗与元叙事

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: [N-Rel]
rel_object: mixed
t_can_carry: [T5, T2]
core_emotion_note: ""
core_conflict: 被创造的角色反抗造物主，争夺现实世界主导权

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 奇幻
theme_secondary: [异世界穿越, 都市, 悬疑, 冒险]
visual_tags: [都市夜景, 异世界穿越, 魔法阵, 武器对决, 机甲]


# === 评分(v0 已有)===
acquisition_score: 3

# === 素材与玩法 ===
material_hooks: [角色穿越东京, 造物主与角色对峙, 异世界战斗场面, 角色能力碰撞]
existing_games: []
recommended_playstyles: []
risk_notes: [红海, 版权成本高]

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
