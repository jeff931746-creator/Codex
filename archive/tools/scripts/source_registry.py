#!/usr/bin/env python3
"""来源注册表数据（脚本读取用）。

对应 archive/资料/战略库/来源注册表.md 的机器可读版本。
修改来源时同步修改两边。
"""

# 信息类型：new=新品发现, data=数据榜单, ad=买量市场, biz=行业动态, teardown=产品拆解(不采集)

SOURCES = [
    # ── T1 核心：新品发现为主 ──
    {"name": "柠檬游戏说", "fakeid": "MzA3NTIwNjk2MA==", "types": ["new", "data"]},
    {"name": "龙虾游戏推荐", "fakeid": "MzU0MTA2MDA0Mw==", "types": ["new", "data"]},
    {"name": "GAME游意思", "fakeid": "MzIyODkwMzUzNQ==", "types": ["new"]},
    {"name": "王董的新游戏", "fakeid": "Mzg5MTcwMTI5Nw==", "types": ["new"]},
    {"name": "新游观察", "fakeid": "MzkyMzY2OTc5Mw==", "types": ["new"]},
    {"name": "急速行走的小U盘", "fakeid": "MzkzMDM4NzI4NA==", "types": ["new"]},
    {"name": "鹅说的游戏", "fakeid": "MzU1ODg1ODkxNw==", "types": ["new"]},
    {"name": "游戏吗喽说", "fakeid": "MzkyMDcyNTEyNA==", "types": ["new"]},
    {"name": "胡扯游戏", "fakeid": "Mzk1NzIzNzk1NA==", "types": ["new"]},
    {"name": "雅馨小筑小游戏评测", "fakeid": "Mzk0Mjc1NDEyMQ==", "types": ["new"]},
    {"name": "奎妮游戏推荐", "fakeid": "Mzk2NDY4MjYzMg==", "types": ["new"]},
    {"name": "Vergil的游戏杂谈", "fakeid": "MzkxMTY5ODc1NA==", "types": ["new"]},
    {"name": "无花果的游戏日记", "fakeid": "Mzk0NzIyOTIzNA==", "types": ["new"]},
    {"name": "趣游拾荒客", "fakeid": "MzUxMjYyNzkwMw==", "types": ["new"]},
    {"name": "嘅噗喔呋啼", "fakeid": "MzAwMDYxMzUwNw==", "types": ["new"]},
    {"name": "海喵研究院", "fakeid": "MzkyNTM0NTgwMg==", "types": ["new"]},
    {"name": "DennisLook", "fakeid": "MzkyNDU5ODY0OA==", "types": ["new", "teardown"]},
    {"name": "英雄游戏研究院", "fakeid": "MzkyNTcyNTYwNQ==", "types": ["new", "teardown"]},
    {"name": "产品拆解师", "fakeid": "MzkyNTI5NDg4MQ==", "types": ["new", "teardown"]},
    {"name": "游戏发展国", "fakeid": "MzAxMjc3ODcwNA==", "types": ["new", "teardown"]},
    {"name": "米粒游戏版号", "fakeid": "Mzg2MTYzMjQ4MQ==", "types": ["new"]},
    {"name": "一叶知游", "fakeid": "MzkxOTcwNDI4OQ==", "types": ["new", "teardown"]},

    # ── T1 核心：数据榜单为主 ──
    {"name": "半吊子玩家", "fakeid": "MjM5MzAxNDg0MA==", "types": ["data"]},
    {"name": "DataEye游戏观察", "fakeid": "MzA4MzE0ODIwNA==", "types": ["data", "ad"]},
    {"name": "AppMagic", "fakeid": "MzkwNzg3OTEzMA==", "types": ["data"]},
    {"name": "赛博蛋挞", "fakeid": "MzkxMzYxNzEwMg==", "types": ["data"]},
    {"name": "游戏客栈x爆款时代", "fakeid": "MzI3OTAxOTg0MA==", "types": ["data"]},
    {"name": "游戏新渠道", "fakeid": "MzkxOTY2NjU4Mw==", "types": ["data"]},
    {"name": "游戏行业商务合作指南", "fakeid": "MjM5MjY1Mjk5Ng==", "types": ["data"]},

    # ── T1 核心：买量市场为主 ──
    {"name": "白鲸出海", "fakeid": "MzYzNTkyMTI2Ng==", "types": ["ad", "biz"]},
    {"name": "独立出海联合体", "fakeid": "MzU2NTgyOTI4Ng==", "types": ["ad", "biz"]},
    {"name": "扬帆出海", "fakeid": "MjM5NzI2NzA3Mg==", "types": ["ad", "biz"]},
    {"name": "Enjoy出海开发者服务平台", "fakeid": "Mzg2NDgyODMzOQ==", "types": ["ad"]},
    {"name": "广大大出海笔记", "fakeid": "Mzg3NDU0MTA0OA==", "types": ["ad"]},
    {"name": "出海观察", "fakeid": "MzYzNDE2MDEzNA==", "types": ["ad", "biz"]},
    {"name": "诗人的游戏观察", "fakeid": "MzU0NDkwNzY0MQ==", "types": ["ad", "data"]},

    # ── T1 核心：行业动态为主 ──
    {"name": "竞核", "fakeid": "MzkwMjY0ODI1Mg==", "types": ["biz"]},
    {"name": "游戏智库", "fakeid": "MzA5NDkxMjI2Ng==", "types": ["biz"]},

    # ── 综合（多类型混合）──
    {"name": "GameLook", "fakeid": "MjM5NzQwMjI4MA==", "types": ["new", "data", "ad", "biz"]},
    {"name": "游戏葡萄", "fakeid": "MjM5OTc2ODUxMw==", "types": ["new", "data", "biz"]},
    {"name": "罗斯基", "fakeid": "MzIwOTc2MjY2MA==", "types": ["new", "data", "ad"]},
    {"name": "游戏陀螺", "fakeid": "MjM5Njc5MjgyMA==", "types": ["new", "biz"]},
    {"name": "触乐", "fakeid": "MzA4MDIxNzkyNA==", "types": ["new", "biz"]},
    {"name": "游戏那点事Gamez", "fakeid": "MjM5MDEwMTk2MA==", "types": ["new", "data", "biz"]},
    {"name": "游戏新知", "fakeid": "Mzg3MzMzNjM3OQ==", "types": ["new", "data", "biz"]},
    {"name": "游戏价值论", "fakeid": "Mzg2OTU0MTcyMg==", "types": ["new", "data"]},
    {"name": "游戏茶馆", "fakeid": "MjM5OTgzNzkyNA==", "types": ["new", "biz"]},
    {"name": "游戏研究社", "fakeid": "MzIzNzM3NzE2MA==", "types": ["new", "biz"]},
    {"name": "游戏日报", "fakeid": "MjM5NTIzNjA2MA==", "types": ["new", "data"]},
    {"name": "胡椒游戏", "fakeid": "Mzg2MjgzODk2OQ==", "types": ["new", "data"]},
    {"name": "游益", "fakeid": "MzkwMDUzMzQwMA==", "types": ["new", "biz"]},
    {"name": "妙游社", "fakeid": "MzA3NjQzMzYxMw==", "types": ["new", "biz"]},
    {"name": "游戏旅人", "fakeid": "MzU4MzgwNDEzMA==", "types": ["data", "ad"]},
    {"name": "GameRes游资网", "fakeid": "MjM5NTMxNTU0MQ==", "types": ["new"]},
]

# 总数
TOTAL_SOURCES = len(SOURCES)
