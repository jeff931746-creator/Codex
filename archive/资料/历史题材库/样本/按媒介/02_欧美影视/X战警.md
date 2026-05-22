---
# === 身份 ===
work_id: WORK-TVW-00032
work_name: X战警
work_name_alt: []
media_type: TVW
year_first: 2000
year_range: [2000, 2000]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 现代超能力世界
cultural_paradigm: 变种人体系+超能力对抗
narrative_core: 变种人对抗与共存

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: mixed
t_can_carry: [T4, T2]
core_emotion_note: ""
core_conflict: 变种人争取生存权利与人类恐惧对抗，内部理念分裂

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 科幻
theme_secondary: [异能学院, 未来战争, 政治权谋, 都市]
visual_tags: [都市夜景, 实验室, 爆炸场面, 武器对决, 超能力特效]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [超能力视觉特效, 变种人角色造型, X战警制服, 战斗场面爆炸]
existing_games: [X-Men系列游戏]
recommended_playstyles: []
risk_notes: [版权成本高, 红海]

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
