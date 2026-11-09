---
# === 身份 ===
work_id: WORK-ANI-00101
work_name: "Re:从零开始的异世界生活"
work_name_alt: []
media_type: ANI
year_first: 2016
year_range: [2016, 2026]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 奇幻异世界
cultural_paradigm: 魔法+死亡回归轮回
narrative_core: 死亡轮回与情感救赎

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: [N-Rel]
rel_object: mixed
t_can_carry: [T2, T5]
core_emotion_note: ""
core_conflict: 主角在死亡轮回中破解诅咒与拯救同伴

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 奇幻
theme_secondary: [异世界穿越, 黑暗奇幻, 悬疑, 友情]
visual_tags: [城堡, 森林, 魔法阵, 古风装扮, 黑暗压抑]


# === 评分(v0 已有)===
acquisition_score: 4

# === 素材与玩法 ===
material_hooks: [死亡轮回场景, 魔女气息, 角色表情特写, 城堡与森林]
existing_games: ["Re:从零开始的异世界生活 虚假的王选候补", "Re:从零开始的异世界生活 INFINITY"]
recommended_playstyles: []
risk_notes: [版权成本高, 玩法创新难]

# === 元数据 ===
source: deepseek-v4-flash + v0-migrate + tags
source_run_id: 2026-05-18-tags-enrich
evidence_level: B
review_status: auto
last_updated: 2026-05-18
# v0_duplicate_count: 9
---

## 迁移备注

本样本由 v0 markdown 表格迁移而来,LLM 阶段尚未补 SDT 三需求 / T 任务态 / core_conflict / material_hooks 重判。
迁移完成后 evidence_level = C,LLM 增量打标后升至 B。
