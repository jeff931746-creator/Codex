---
name: Task State — 战略库与信息收集体系
description: 游戏行业信息自动化收集体系；受控词表+多维表格同步固化于 2026-06-12，cron 定时仍待办
type: project
originSessionId: current
---

# 任务状态 — 战略库与信息收集体系

## 基本信息

- **任务名**：战略库与信息收集体系
- **开始时间**：2026-06-04
- **任务类型**：knowledge-asset / implementation
- **当前状态**：Executing
- **当前门禁**：受控词表+同步固化 validation 通过 → 待 cron 定时
- **已完成门禁**：intake, plan, governance-design, target-inspection, edit, 全量测试通过, 根因修复, 全量重跑成功, 受控词表+多维表格同步(2026-06-12)
- **下一门禁**：cron 定时 → 海外媒体接入 → delivery
- **阻塞项**：无

## 多维表格同步（2026-06-12 新增）

- **目标表**：竞品库（自动化）`JQMtbtxcna9uucs6clocTMggn0f` / table `tbl2yDXmGRFFN10V`（共 2 表，用「全部竞品」表）
- **同步脚本**：`archive/tools/scripts/sync_to_bitable.py`，幂等：抓取表内→删同名→batch-create 归一化新值；非本地来源记录不动
- **身份**：写操作必须 `--as bot`（表 owner 是个人号 jeff，user 身份 Jeff-汪书丞 报 91403）
- **lark-cli 坑**：`record-upsert` 的 `match_fields` 本版本(1.0.44)不生效（"Cell value does not match any supported shape"），必须 record-id 才更新；分页用 `--offset` 不是 page_token
- **当前表内**：235 条（114 本地去重 + 121 历史保留），0 重复，主品类越界 0

## 受控词表（2026-06-12 新增，唯一真相源）

- **文件**：`archive/tools/scripts/controlled_vocab.py`
- **根因**：collector 的 category_primary/category_tags 原是 DeepSeek 自由生成，无白名单 → 主品类 33 种含同义(FPS/射击)、标签 211 种 75% 一次性 → 同步 not_found 丢数据
- **方案**：PRIMARY_CATEGORIES 封闭集(27) + PRIMARY_ALIAS 同义映射；GAMEPLAY_TAGS 推荐集(48) + TAG_ALIAS；normalize_primary/normalize_tags(strict)
- **接入**：collector prompt 注入词表(占位符 .replace)+写库前归一化兜底；sync 用 strict 收敛长尾
- **效果**：本地 116 文件主品类 100% 落受控集，标签复现项 100% 受控，strict 下仅 8/116 标签纯长尾为空

## 目标与约束

**目标**：每日自动化的游戏行业信息收集体系，覆盖公众号/海外媒体/视频来源，分流到战略库（市场情报）和竞品库（新品监控）。

**已确认约束**：
- 新品只收：海外未上线轻中度、海外已上线国内无同类、国内IAA、Steam新品、小游戏新品
- 新品排除：大厂黑名单（21家公司名单在脚本 BLACKLISTED_COMPANIES 里）、三消、超休闲、3A、已知大作
- 战略库收录：含一手数据/平台政策变化/买量策略洞察/赛道趋势/重大商业事件
- 战略库排除：纯新闻转述/大厂八卦人事/产品软文/无数据观点/PC主机3A新闻
- 竞品库按轻中重度分档 + 日期命名
- 执行方式：独立 Python 脚本 + DeepSeek API（零 Claude token）
- 数据源：wechat-article-exporter API（down.mptext.top），key 4天有效

## 已建成产物

| 产物 | 路径 | 版本 | 状态 |
|---|---|---|---|
| 通用标准 | `reference/部门标准/信息收集/信息收集标准.md` | v3 | ✅ 已 commit |
| 战略库 SCHEMA | `archive/资料/战略库/SCHEMA.md` | v2（含入库质量标准 S1-S5/E1-E5） | ✅ 已 commit |
| 竞品库 SCHEMA | `archive/资料/竞品库/SCHEMA.md` | v1（含新品收录标准 N1-N5/X1-X5、轻中重度分档） | ✅ 已 commit |
| 战略收集 Skill | `archive/skills/skills/战略收集/SKILL.md` | v1 | ✅ 已 commit |
| 来源注册表 | `archive/资料/战略库/来源注册表.md` | v2（按 new/data/ad/biz/teardown 分类） | ✅ 已 commit |
| 来源 Python 配置 | `archive/tools/scripts/source_registry.py` | 54 个公众号含 fakeid | ✅ 已 commit |
| 自动化脚本 | `archive/tools/scripts/daily_intel_collector.py` | v6（根因修复+重试+限速+截断） | ✅ 已 commit |
| 竞品库数据 | `archive/资料/竞品库/{轻度,中度,重度}/` | 240 个产品 | ✅ 质量可用 |
| 战略库数据 | `archive/资料/战略库/条目/` | 45 条 | ✅ 内容完整 |

## 架构

```
信息收集标准 v3（通用）
  ├── 文章级路径 → value_score 筛选 → 战略库（买量/市场/赛道/政策）
  └── 产品级路径 → 大厂硬过滤 + 新品标准 → 竞品库（轻度/中度/重度）

信息类型：new(新品) / data(数据榜单) / ad(买量市场) / biz(行业动态) / teardown(不采集)
每篇文章由 DeepSeek 判断类型 → 分流处理 → 写入对应库

自动化：独立脚本 + DeepSeek + 系统 cron（零 Claude token）
数据源：wechat-article-exporter API（公众号后台搜索接口）+ url-md（全文读取）
```

## 已修复的 Bug

**战略库条目全空问题（已修复）**：
- 症状：120 篇条目有标题和URL，但 core_thesis/tags/key_points/正文全为空
- **真正根因**：`write_strategy_entry` 第一行 `strategy = analysis if analysis.get("type") == "strategy"` 取到了包装 dict 而非实际 strategy 数据，导致 .get() 全返回默认值
- 修复：改为 `strategy = analysis.get("strategy") or analysis`
- 之前误判为 DeepSeek 限流，实际是代码层的字典层级错误
- 修复后全量跑：45 条战略库条目，内容完整，0 空壳

## 关键技术结论

| 结论 | 依据 |
|---|---|
| 微信公众号文章列表获取：wechat-article-exporter 是唯一免费方案 | 微信官方API无跨号接口；搜狗停更；RSSHub微信路由全挂；Wechat2RSS需150元/年 |
| WX_API_KEY 已入桥接 .env | 2026-06-12 起 `WX_API_KEY` 写入 `~/Library/Application Support/FeishuCodexBridge/bridge/.env`，不再外部传入；key 仍约 4 天有效需续期 |
| 数据质量分层（116 竞品实测） | 强(97-100%)：核心玩法/主品类/标签/地区/平台；中(47-78%)：发行商/开发商/上线状态/变现；弱(<20%)：上线日期11%/美术18%/对标18%/榜单3.4%。弱字段是来源决定（新游推荐号不写榜单数据），非脚本 bug |
| 战略库质量 > 竞品库 | 战略库 76 条 core_thesis 100%、value_score 全≥3（LLM 强项=论点提取）；竞品库元数据弱（文章无 release_date/榜单/美术） |
| 微信 API 的 size 参数不可靠 | 请求 5 篇可能返回 20+，必须在代码层截断 |
| DeepSeek JSON 输出有截断风险 | 含大量产品的文章（如 SLG 复盘）JSON 超 2000 token 会被截断，需重试 |
| 54 源全量跑约 50 分钟 | 270 篇 × (fetch + DeepSeek + sleep) |

## 下一步

1. **设 cron 定时任务**（每日自动跑）
2. **海外媒体接入**（url-md 抓 GamesIndustry/PocketGamer/GameBeat）
3. **YouTube/B站标题采集**
4. **持续调优**：扩充黑名单、根据 user_rating 反馈迭代
5. **WX API key 续期机制**（4天到期提醒）

## 会话续接指引

**续接后第一个动作：**
检查 cron 是否已设置。如未设，配置系统 cron 或 launchd 定期运行脚本。

**运行前必须确认：**
- [ ] wechat-article-exporter API key 是否过期（4天有效，到期去 down.mptext.top 重新扫码）
- [ ] DeepSeek API key 是否可用（`source "$HOME/Library/Application Support/FeishuCodexBridge/bridge/.env"` 后检查 `echo $DEEPSEEK_API_KEY`）
