---
# === 身份 ===
work_id: WORK-LIT-00401
work_name: The Shadow of the Wind
work_name_alt: []
media_type: LIT
year_first: 2001
year_range: [2001, 2003]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: 1940年代巴塞罗那
cultural_paradigm: 书籍谜团+哥特悬疑
narrative_core: 少年探寻作家失踪之谜

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: N-Auto
n_others: [N-Rel]
rel_object: mixed
t_can_carry: [T5, T3]
core_emotion_note: 自主探索与关系感交织，主角在解谜中建立与逝去作家及同伴的情感纽带
core_conflict: 少年追寻神秘作家失踪真相，揭开家族与城市的黑暗秘密

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: 悬疑
theme_secondary: [身份谜团, 家庭秘密, 历史, 都市]
visual_tags: [古堡, 废墟, 老街巷, 阴暗图书馆, 雨中墓地]


# === 评分(v0 已有)===
acquisition_score: 3

# === 素材与玩法 ===
material_hooks: [哥特式巴塞罗那街景, 焚书场景, 神秘作家肖像, 阴暗图书馆, 雨中墓地]
existing_games: []
recommended_playstyles: []
risk_notes: [受众窄, 版权成本中等]

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
