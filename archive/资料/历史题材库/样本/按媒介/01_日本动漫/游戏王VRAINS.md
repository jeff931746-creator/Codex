---
# === 身份 ===
work_id: WORK-ANI-00106
work_name: 游戏王VRAINS
work_name_alt: []
media_type: ANI
year_first: 2018
year_range: [2018, 2018]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 近未来网络虚拟世界
cultural_paradigm: 卡牌决斗+数据化召唤
narrative_core: 竞技冒险+黑客对抗

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Comp
n_others: [N-Rel]
rel_object: virtual
t_can_carry: [T2, T5]
core_emotion_note: ""
core_conflict: 主角在虚拟网络世界通过卡牌决斗对抗黑客组织，拯救现实与虚拟世界

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 科幻
theme_secondary: [赛博朋克, 冒险, 犯罪]
visual_tags: [霓虹灯, 虚拟网络城市, 数据化召唤, 全息投影, 高速决斗特效]


# === 评分(v0 已有)===
acquisition_score: 3

# === 素材与玩法 ===
material_hooks: [高速决斗特效, 数据化召唤怪兽, 虚拟网络城市, 黑客入侵场景, Link召唤动画]
existing_games: [游戏王决斗链接, 游戏王大师决斗]
recommended_playstyles: []
risk_notes: [版权成本高, 红海竞争]

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
