---
# === 身份 ===
work_id: WORK-LIT-00399
work_name: The Book Thief
work_name_alt: []
media_type: LIT
year_first: 2005
year_range: [2005, 2005]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 二战德国小镇
cultural_paradigm: 文字救赎+纳粹压迫
narrative_core: 少女偷书与人性觉醒

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Auto]
rel_object: virtual
t_can_carry: [T3, T1]
core_emotion_note: N-Rel温和归属为主，N-Auto提供自由探索文字世界的副爽点
core_conflict: 少女在纳粹压迫下通过偷书与文字寻找人性温暖

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 历史
theme_secondary: [二战, 战争, 成长, 救赎, 家庭羁绊]
visual_tags: [小镇, 雪原, 地下室, 古风装扮, 战争残酷]


# === 评分(v0 已有)===
acquisition_score: 3

# === 素材与玩法 ===
material_hooks: [偷书少女, 地下室读书, 犹太逃亡者, 手写故事, 雪中送书]
existing_games: []
recommended_playstyles: []
risk_notes: [受众窄, 版权成本中等, 题材沉重]

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
