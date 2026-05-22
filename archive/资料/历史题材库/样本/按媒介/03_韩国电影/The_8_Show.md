---
# === 身份 ===
work_id: WORK-MVK-00064
work_name: The 8 Show
work_name_alt: []
media_type: MVK
year_first: 2024
year_range: [2024, 2024]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 封闭游戏空间
cultural_paradigm: 生存竞争+心理博弈
narrative_core: 残酷竞争+人性考验

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: real
t_can_carry: [T4, T5]
core_emotion_note: ""
core_conflict: 8人争夺奖金，在封闭空间中互相算计与背叛

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 悬疑
theme_secondary: [求生, 心理悬疑, 智斗]
visual_tags: [封闭空间, 数字计时器, 玩家对峙, 奖金跳动, 淘汰瞬间]


# === 评分(v0 已有)===
acquisition_score: 3

# === 素材与玩法 ===
material_hooks: [封闭楼层空间, 数字计时器, 玩家对峙表情, 奖金数字跳动, 淘汰瞬间]
existing_games: []
recommended_playstyles: []
risk_notes: [红海, 竞争激烈]

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
