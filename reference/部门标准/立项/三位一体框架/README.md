# 三位一体框架(版本索引)

> 最近更新:2026-05-15
> 引用规则:**永远从 `current/` 读取**。`history/` 仅作历史追溯,不允许被业务流程引用。

## 当前版本

| 标准 | 当前版本 | 状态 | 最近升级 | 文件 |
|---|---|---|---|---|
| 00-框架定义 | v1.0 | stable | 2026-05-12 | [current/00-框架定义.md](current/00-框架定义.md) |
| 01-人群簇标准 | v1.2 | stable | 2026-05-15 | [current/01-人群簇标准.md](current/01-人群簇标准.md) |
| 02-题材母题标准 | v0.3 | hypothesis | 2026-05-11 | [current/02-题材母题标准.md](current/02-题材母题标准.md) |
| 03-玩法承接标准 | v1.1 | stable | 2026-05-15 | [current/03-玩法承接标准.md](current/03-玩法承接标准.md) |
| 04-ID 与交叉引用规则 | v1.0 | stable | 2026-05-11 | [current/04-ID与交叉引用规则.md](current/04-ID与交叉引用规则.md) |
| 05-填库工作流 | v1.0 | stable | 2026-05-11 | [current/05-填库工作流.md](current/05-填库工作流.md) |
| 06-基础维度定义 | v1.0 | stable | 2026-05-15 | [current/06-基础维度定义.md](current/06-基础维度定义.md) |
| 07a-立项分析SOP | v1.0 | stable | 2026-05-15 | [current/07a-立项分析SOP.md](current/07a-立项分析SOP.md) |
| 07b-成功复盘SOP | v1.0 | stable | 2026-05-15 | [current/07b-成功复盘SOP.md](current/07b-成功复盘SOP.md) |

## 历史版本

| 标准 | 历史版本 |
|---|---|
| 01-人群簇标准 | [history/01-人群簇标准/v1.1_2026-05-13.md](history/01-人群簇标准/v1.1_2026-05-13.md) |
| 03-玩法承接标准 | [history/03-玩法承接标准/v1.0_2026-05-12.md](history/03-玩法承接标准/v1.0_2026-05-12.md) |

## 模板

立项时填库使用模板:[current/模板/](current/模板/)

## 升级流程

每次升级一份标准:
1. 把 `current/{标准名}.md` 复制为 `history/{标准名}/v{X}_{日期}.md`
2. 新版本内容直接写到 `current/{标准名}.md`(覆盖)
3. 顶部 yaml 元数据更新 version / released / supersedes
4. 本 README 索引表更新

## 引用规则(硬约束)

所有业务流程、Skill、子 agent prompt 中引用三位一体框架文档时:

- ✅ 必须用 `current/` 路径:`reference/部门标准/立项/三位一体框架/current/01-人群簇标准.md`
- ❌ 不允许:任何 history/ 路径或裸文件路径(不带 current/)
- 历史版本仅作追溯查阅,不进入执行流
