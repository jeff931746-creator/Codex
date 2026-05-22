---
# === 身份 ===
work_id: WORK-ANI-00037
work_name: 精灵宝可梦XY
work_name_alt: []
media_type: ANI
year_first: 2014
year_range: [2014, 2014]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 奇幻世界卡洛斯地区
cultural_paradigm: 精灵收集+对战进化
narrative_core: 冒险成长+友情羁绊

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: [N-Rel]
rel_object: virtual
t_can_carry: [T2, T3]
core_emotion_note: ""
core_conflict: 训练师与精灵共同成长，挑战道馆与邪恶组织

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 冒险
theme_secondary: [友情, 奇幻, 校园]
visual_tags: [奇幻瑰丽, 精灵进化特效, 华丽对战场景, Mega进化变身]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [精灵进化特效, 华丽对战场景, 道馆徽章收集, Mega进化变身]
existing_games: [宝可梦XY, 宝可梦GO]
recommended_playstyles: []
risk_notes: [版权成本极高, 红海]

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
