---
# === 身份 ===
work_id: WORK-MVK-00391
work_name: YMCA棒球队
work_name_alt: []
media_type: MVK
year_first: 2002
year_range: [2002, 2002]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 日据时期韩国
cultural_paradigm: 棒球运动+民族抗争
narrative_core: 团队成长+历史抗争

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Rel
n_others: [N-Comp]
rel_object: mixed
t_can_carry: [T4, T2]
core_emotion_note: ""
core_conflict: 日据时期韩国棒球队在殖民压迫下通过比赛争取民族尊严与团队胜利

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 体育竞技
theme_secondary: [棒球, 历史, 成长, 热血战斗]
visual_tags: [赛场, 古战场, 军装, 武器对决, 历史背景字幕]


# === 评分(v0 已有)===
acquisition_score: 3

# === 素材与玩法 ===
material_hooks: [棒球赛场对决, 日韩国旗对峙, 球员挥棒特写, 观众呐喊场面, 历史背景字幕]
existing_games: []
recommended_playstyles: []
risk_notes: [受众窄, 历史敏感]

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
