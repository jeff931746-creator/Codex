# Pocket Groove Clone Prototype

一个零依赖浏览器原型目录，用来验证 `Pocket Groove Tactics` 参考玩法。

## 当前状态

当前 demo 已按 `docs/video_reanalysis/00_纠偏结论与实现口径.md` 重写为连通翻格版本：

- 玩家点击地图上的未翻开候选地块，支付金币后翻开。
- 候选地块只从已翻开且能连回己方 HQ 的地块旁生成。
- 翻开结果包含空地、矿、兵营；HQ 和矿产金币，HQ 和兵营自动出兵。
- 敌方按同类规则自动翻地、产金币、出兵。
- 单位使用已翻开可通行地块网络寻路，不再使用硬编码单线兵轨。

## Run

直接打开 `index.html`，或在本目录启动静态服务器：

```bash
python3 -m http.server 8000
```

## Scope

- 已实现：地图地块付费翻开、基地连通校验、翻开结果为空/矿/兵营、HQ/矿产金币、敌方同规则扩张、基于连通地块网络的单位寻路与交战。
- 暂不实现：真实长线养成、联网 PvP、广告/内购、完整关卡编辑器。

这个目录是 `workspace/playground/` 下的实验原型，可按需要继续扩展或丢弃。

## Design Docs

### 视频复核纠偏

以下文档是后续实现主依据：

- `docs/video_reanalysis/00_纠偏结论与实现口径.md`

### 立项补证与纸面原型

以下文档保留为立项和失败复盘依据；其中“底部翻格按钮 / 槽位激活 / 单线兵轨”口径均不再作为实现依据：

- `docs/launch/00_纸面原型补证稿.md`
- `docs/launch/01_纸面原型规则.md`
- `docs/launch/02_模块拆解与边界.md`
- `docs/launch/03_GDD重写清单.md`

### GDD v2

以下文档按上一轮立项补证逻辑和 `reference/部门标准/策划/gdd/GDD写作标准.md` v17 重写，但包含错误口径，不再作为实现依据：

- `docs/gdd_v2/00_核心玩法总需求GDD.md`
- `docs/gdd_v2/01_底部翻格与基地连结GDD.md`
- `docs/gdd_v2/02_经济建筑与出兵节奏GDD.md`
- `docs/gdd_v2/03_战斗节奏与结算GDD.md`

### 失效 GDD v1

以下文档保留为失败稿对照，不作为实现依据：

- `docs/gdd/00_核心玩法总需求GDD.md`
- `docs/gdd/01_地图翻格系统GDD.md`
- `docs/gdd/02_经济系统GDD.md`
- `docs/gdd/03_建筑与出兵系统GDD.md`
- `docs/gdd/04_战斗推进系统GDD.md`
- `docs/gdd/05_敌方AI与结算GDD.md`

### 早期拆解草稿

- `docs/00_复刻目标与证据边界.md`
- `docs/01_功能模块总览.md`
- `docs/02_地图与地块系统.md`
- `docs/03_经济系统.md`
- `docs/04_建筑与出兵系统.md`
- `docs/05_战斗与推进系统.md`
- `docs/06_对局流程_AI与验收清单.md`
