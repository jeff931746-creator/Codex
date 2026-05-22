---
# === 身份 ===
work_id: WORK-ANI-00811
work_name: 魔法学园MA
work_name_alt: []
media_type: ANI
year_first: 2008
year_range: [2008, 2008]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 现代魔法学园
cultural_paradigm: 魔法学院+搞笑日常
narrative_core: 校园闹剧与魔法冒险

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Auto]
rel_object: virtual
t_can_carry: [T3, T1]
core_emotion_note: ""
core_conflict: 魔法学园中，主角与个性迥异的少女们展开搞笑日常与冒险

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 奇幻
theme_secondary: [校园, 喜剧, 魔法, 日常喜剧]
visual_tags: [校园, 教室, 魔法阵, 搞笑荒诞, 古风装扮]


# === 评分(v0 已有)===
acquisition_score: 2

# === 素材与玩法 ===
material_hooks: [魔法少女角色, 学园制服, 搞笑表情包, 魔法战斗场面]
existing_games: []
recommended_playstyles: []
risk_notes: [受众窄, 付费浅]

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
