#!/usr/bin/env python3
"""
人群簇 v1.0 矩阵扩大验证脚本 - 230 样本版
用 GLM-5.1 对 230 个跨媒介样本做归类验证，重点验证微信小游戏人群分布。

样本分布：
- 国内重度手游 25
- 国内女性向手游 8
- 海外手游 20
- Steam/PC 15
- 主机/独立游戏 8
- 微信小游戏（2024+2025 去重） 100
- 短剧 12
- 网文/网漫 10
- 影视/动漫 10
- 综艺/恋综 8
- 直播/视频博主 6
- 社区/资讯/工具 6
- 棋牌/边界 4

分批：5 批 × 46 样本（最后一批稍多）
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
for _parent in _THIS_FILE.parents:
    if (_parent / "archive" / "tools" / "lib").is_dir():
        sys.path.insert(0, str(_parent))
        break

from archive.tools.lib.siliconflow_client import RetryPolicy, chat_text

OUTPUT_DIR = Path("/Users/mt/Documents/Codex/archive/资料/人群簇库/_draft")
RAW_DIR = OUTPUT_DIR / "_raw"
TODAY = datetime.now().strftime("%Y-%m-%d")

MODEL = os.environ.get("SILICONFLOW_MODEL", "Pro/zai-org/GLM-5.1")

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_llm(prompt: str, max_tokens: int = 16000, retries: int = 3) -> str:
    return chat_text(
        prompt,
        model=MODEL,
        max_tokens=max_tokens,
        temperature=0.2,
        timeout=360,
        retry_policy=RetryPolicy(retries=retries, base_delay=3),
        logger=lambda msg: log(f"  {msg}"),
        return_empty_on_error=True,
    )

def call_llm_cached(prompt: str, label: str, max_tokens: int = 16000) -> str:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{TODAY}_{label}.txt"
    if raw_path.exists() and raw_path.stat().st_size > 100:
        log(f"  [{label}] 使用缓存")
        return raw_path.read_text(encoding="utf-8")
    raw = call_llm(prompt, max_tokens)
    if raw:
        raw_path.write_text(raw, encoding="utf-8")
    return raw

# ========== 230 样本清单 ==========
# 编号规则：1xx 重度手游、2xx 女性向、3xx 海外手游、4xx Steam/PC、5xx 主机/独立
#         6xx 微信小游戏 2024/2025（已去重）、7xx 短剧、8xx 网文、9xx 影视
#         A xx 综艺、B xx 直播、C xx 社区、D xx 棋牌边界
SAMPLES = [
    # === 国内重度手游 25 个 ===
    {"id": 101, "name": "三国志战略版", "type": "国内重度手游", "note": "SLG 联盟战、武将"},
    {"id": 102, "name": "率土之滨", "type": "国内重度手游", "note": "SLG 鼻祖"},
    {"id": 103, "name": "口袋奇兵", "type": "国内重度手游", "note": "SLG 合成创新出海"},
    {"id": 104, "name": "原神", "type": "国内重度手游", "note": "二次元开放世界抽卡"},
    {"id": 105, "name": "崩坏：星穹铁道", "type": "国内重度手游", "note": "二次元回合制抽卡"},
    {"id": 106, "name": "明日方舟", "type": "国内重度手游", "note": "二次元塔防抽卡"},
    {"id": 107, "name": "阴阳师", "type": "国内重度手游", "note": "二次元卡牌抽卡"},
    {"id": 108, "name": "鸣潮", "type": "国内重度手游", "note": "动作二次元抽卡"},
    {"id": 109, "name": "梦幻西游手游", "type": "国内重度手游", "note": "经典 MMO 商人玩法"},
    {"id": 110, "name": "逆水寒手游", "type": "国内重度手游", "note": "国风 MMO 长线"},
    {"id": 111, "name": "和平精英", "type": "国内重度手游", "note": "FPS 大逃杀"},
    {"id": 112, "name": "王者荣耀", "type": "国内重度手游", "note": "MOBA 国民竞技"},
    {"id": 113, "name": "永劫无间手游", "type": "国内重度手游", "note": "吃鸡冷兵器"},
    {"id": 114, "name": "蛋仔派对", "type": "国内重度手游", "note": "派对UGC社交"},
    {"id": 115, "name": "一念逍遥", "type": "国内重度手游", "note": "修仙放置"},
    {"id": 116, "name": "最强祖师", "type": "国内重度手游", "note": "修仙宗门挂机"},
    {"id": 117, "name": "三国冰河时代", "type": "国内重度手游", "note": "末日SLG 合成创新"},
    {"id": 118, "name": "全民奇迹2", "type": "国内重度手游", "note": "传奇MMO重氪老用户"},
    {"id": 119, "name": "新斗罗大陆魂师对决", "type": "国内重度手游", "note": "IP卡牌养成"},
    {"id": 120, "name": "坎公骑冠剑", "type": "国内重度手游", "note": "横版卡牌Roguelike"},
    {"id": 121, "name": "战双帕弥什", "type": "国内重度手游", "note": "动作二次元抽卡"},
    {"id": 122, "name": "鸣潮国服", "type": "国内重度手游", "note": "动作二次元"},
    {"id": 123, "name": "Whiteout Survival 无尽冬日", "type": "国内重度手游", "note": "末日SLG海外冠军"},
    {"id": 124, "name": "Last War 末日", "type": "国内重度手游", "note": "末日合并SLG出海"},
    {"id": 125, "name": "Top War 战火指挥官", "type": "国内重度手游", "note": "合成SLG老牌出海"},

    # === 国内女性向手游 8 个 ===
    {"id": 201, "name": "恋与制作人", "type": "女性向", "note": "乙女开山"},
    {"id": 202, "name": "光与夜之恋", "type": "女性向", "note": "乙女腾讯"},
    {"id": 203, "name": "未定事件簿", "type": "女性向", "note": "乙女悬疑"},
    {"id": 204, "name": "世界之外", "type": "女性向", "note": "乙女新生代"},
    {"id": 205, "name": "闪耀暖暖", "type": "女性向", "note": "换装养成"},
    {"id": 206, "name": "心动小镇", "type": "女性向", "note": "女性向治愈社交"},
    {"id": 207, "name": "无尽暖暖", "type": "女性向", "note": "3D换装"},
    {"id": 208, "name": "时光公主", "type": "女性向", "note": "换装解谜"},

    # === 海外手游 20 个 ===
    {"id": 301, "name": "Clash Royale 皇室战争", "type": "海外手游", "note": "卡牌即时对战"},
    {"id": 302, "name": "Clash of Clans 部落冲突", "type": "海外手游", "note": "SLG 元祖"},
    {"id": 303, "name": "Brawl Stars 荒野乱斗", "type": "海外手游", "note": "派对竞技"},
    {"id": 304, "name": "PUBG Mobile", "type": "海外手游", "note": "海外吃鸡"},
    {"id": 305, "name": "Genshin Impact 海外", "type": "海外手游", "note": "原神海外版"},
    {"id": 306, "name": "Honkai: Star Rail 海外", "type": "海外手游", "note": "星铁海外"},
    {"id": 307, "name": "Royal Match", "type": "海外手游", "note": "三消金主"},
    {"id": 308, "name": "Candy Crush Saga", "type": "海外手游", "note": "三消经典长青"},
    {"id": 309, "name": "Monopoly GO", "type": "海外手游", "note": "大富翁社交博彩"},
    {"id": 310, "name": "Coin Master", "type": "海外手游", "note": "抢劫好友老虎机"},
    {"id": 311, "name": "Pokémon GO", "type": "海外手游", "note": "AR位置收集"},
    {"id": 312, "name": "Roblox", "type": "海外手游", "note": "UGC沙盒平台"},
    {"id": 313, "name": "Minecraft 我的世界", "type": "海外手游", "note": "沙盒建造跨平台"},
    {"id": 314, "name": "Among Us", "type": "海外手游", "note": "狼人杀社交推理"},
    {"id": 315, "name": "Fortnite", "type": "海外手游", "note": "吃鸡UGC社交"},
    {"id": 316, "name": "Marvel Snap", "type": "海外手游", "note": "漫威卡牌竞技"},
    {"id": 317, "name": "Hero Wars", "type": "海外手游", "note": "卡牌RPG重氪"},
    {"id": 318, "name": "Project Makeover", "type": "海外手游", "note": "三消+改造剧情"},
    {"id": 319, "name": "Township", "type": "海外手游", "note": "经营建设长青"},
    {"id": 320, "name": "Gardenscapes", "type": "海外手游", "note": "三消+花园建造"},

    # === Steam/PC 15 个 ===
    {"id": 401, "name": "杀戮尖塔 Slay the Spire", "type": "Steam", "note": "牌组构筑Roguelike"},
    {"id": 402, "name": "吸血鬼幸存者", "type": "Steam", "note": "极简肉鸽"},
    {"id": 403, "name": "星露谷物语", "type": "Steam", "note": "治愈经营长留"},
    {"id": 404, "name": "Factorio 异星工厂", "type": "Steam", "note": "自动化工厂硬核"},
    {"id": 405, "name": "Stellaris 群星", "type": "Steam", "note": "P社4X宇宙"},
    {"id": 406, "name": "Cities: Skylines 城市天际线", "type": "Steam", "note": "城市建设硬核"},
    {"id": 407, "name": "Dwarf Fortress 矮人要塞", "type": "Steam", "note": "硬核模拟"},
    {"id": 408, "name": "Dota 2", "type": "Steam", "note": "MOBA硬核竞技"},
    {"id": 409, "name": "CS2 反恐精英", "type": "Steam", "note": "FPS长青"},
    {"id": 410, "name": "PUBG Steam", "type": "Steam", "note": "吃鸡端游"},
    {"id": 411, "name": "巫师3 / Witcher 3", "type": "Steam", "note": "ARPG叙事经典"},
    {"id": 412, "name": "赛博朋克2077", "type": "Steam", "note": "ARPG开放世界"},
    {"id": 413, "name": "黑神话：悟空", "type": "Steam/主机", "note": "动作ARPG国民现象"},
    {"id": 414, "name": "Balatro 小丑牌", "type": "Steam", "note": "扑克Roguelike"},
    {"id": 415, "name": "Helldivers 2 绝地潜兵2", "type": "Steam", "note": "PvE合作射击"},

    # === 主机/独立游戏 8 个 ===
    {"id": 501, "name": "动物森友会", "type": "主机", "note": "Switch治愈社交"},
    {"id": 502, "name": "塞尔达传说：王国之泪", "type": "主机", "note": "开放世界探索"},
    {"id": 503, "name": "纪念碑谷", "type": "移动/主机", "note": "艺术向解谜"},
    {"id": 504, "name": "艾尔登法环", "type": "主机/Steam", "note": "魂系硬核动作"},
    {"id": 505, "name": "GTA V / GTA 5", "type": "主机/Steam", "note": "开放世界沙盒"},
    {"id": 506, "name": "Stardew Valley 星露谷", "type": "主机", "note": "治愈经营"},
    {"id": 507, "name": "Disco Elysium 极乐迪斯科", "type": "Steam/主机", "note": "文本叙事ARPG"},
    {"id": 508, "name": "Hollow Knight 空洞骑士", "type": "Steam/主机", "note": "类银河战士独立"},

    # === 微信小游戏（2024 + 2025 去重）100 个 ===
    # 已知爆款 + 按品类假设的代表
    {"id": 601, "name": "羊了个羊", "type": "微信小游戏", "note": "2022爆款消除-长尾"},
    {"id": 602, "name": "咸鱼之王", "type": "微信小游戏", "note": "下沉放置卡牌爆款"},
    {"id": 603, "name": "寻道大千", "type": "微信小游戏", "note": "修仙放置爆款"},
    {"id": 604, "name": "向僵尸开炮", "type": "微信小游戏", "note": "射击肉鸽爆款"},
    {"id": 605, "name": "菇勇者传说", "type": "微信小游戏", "note": "Roguelike出海"},
    {"id": 606, "name": "肌肉狂魔", "type": "微信小游戏", "note": "搞怪健身解压"},
    {"id": 607, "name": "宾果消消消", "type": "微信小游戏", "note": "高ARPU三消"},
    {"id": 608, "name": "无尽冬日 小游戏版", "type": "微信小游戏", "note": "末日SLG小游戏"},
    {"id": 609, "name": "口袋奇兵 小游戏", "type": "微信小游戏", "note": "SLG小游戏版"},
    {"id": 610, "name": "三国冰河时代 小游戏", "type": "微信小游戏", "note": "SLG小游戏"},
    {"id": 611, "name": "卡皇", "type": "微信小游戏", "note": "卡牌放置"},
    {"id": 612, "name": "提灯与地下城", "type": "微信小游戏", "note": "肉鸽放置"},
    {"id": 613, "name": "三国吧兄弟", "type": "微信小游戏", "note": "三国放置"},
    {"id": 614, "name": "三国群英纪", "type": "微信小游戏", "note": "三国卡牌"},
    {"id": 615, "name": "我是大东家", "type": "微信小游戏", "note": "经营模拟"},
    {"id": 616, "name": "疯狂骑士团", "type": "微信小游戏", "note": "放置卡牌出海"},
    {"id": 617, "name": "动物餐厅", "type": "微信小游戏", "note": "治愈经营"},
    {"id": 618, "name": "我功夫特牛", "type": "微信小游戏", "note": "格斗肉鸽"},
    {"id": 619, "name": "合成大西瓜", "type": "微信小游戏", "note": "合成休闲"},
    {"id": 620, "name": "跳一跳", "type": "微信小游戏", "note": "极简休闲长尾"},
    {"id": 621, "name": "成语小秀才", "type": "微信小游戏", "note": "成语答题中老年"},
    {"id": 622, "name": "成语英雄", "type": "微信小游戏", "note": "成语解谜中老年"},
    {"id": 623, "name": "汉字找茬王", "type": "微信小游戏", "note": "找字脑洞"},
    {"id": 624, "name": "脑洞大师", "type": "微信小游戏", "note": "脑洞解谜"},
    {"id": 625, "name": "梦幻花园 小游戏", "type": "微信小游戏", "note": "三消花园"},
    {"id": 626, "name": "保卫萝卜4", "type": "微信小游戏", "note": "塔防经典续作"},
    {"id": 627, "name": "弓箭传说", "type": "微信小游戏", "note": "弓箭肉鸽出海"},
    {"id": 628, "name": "弓箭传说2", "type": "微信小游戏", "note": "弓箭肉鸽续作"},
    {"id": 629, "name": "我滴个龟龟", "type": "微信小游戏", "note": "搞怪小游戏"},
    {"id": 630, "name": "Carnival Tycoon", "type": "微信小游戏", "note": "经营模拟出海"},
    {"id": 631, "name": "全民漂移3D", "type": "微信小游戏", "note": "竞速休闲"},
    {"id": 632, "name": "全民泡泡超人", "type": "微信小游戏", "note": "射击休闲"},
    {"id": 633, "name": "梦幻商人", "type": "微信小游戏", "note": "经营放置"},
    {"id": 634, "name": "我的小家", "type": "微信小游戏", "note": "家居装修"},
    {"id": 635, "name": "城市天际线（小游戏版）", "type": "微信小游戏", "note": "城建模拟"},
    {"id": 636, "name": "动物管家", "type": "微信小游戏", "note": "宠物治愈"},
    {"id": 637, "name": "三国哈哈哈", "type": "微信小游戏", "note": "三国搞怪卡牌"},
    {"id": 638, "name": "斗罗大陆：魂师对决 小游戏", "type": "微信小游戏", "note": "IP卡牌"},
    {"id": 639, "name": "全民养成游戏", "type": "微信小游戏", "note": "放置养成"},
    {"id": 640, "name": "最强大脑挑战", "type": "微信小游戏", "note": "答题脑洞"},
    {"id": 641, "name": "麻将来了", "type": "微信小游戏", "note": "麻将"},
    {"id": 642, "name": "欢乐斗地主", "type": "微信小游戏", "note": "斗地主"},
    {"id": 643, "name": "腾讯欢乐麻将", "type": "微信小游戏", "note": "麻将"},
    {"id": 644, "name": "钓鱼大师", "type": "微信小游戏", "note": "钓鱼休闲"},
    {"id": 645, "name": "全民漂移", "type": "微信小游戏", "note": "漂移休闲"},
    {"id": 646, "name": "战火重燃", "type": "微信小游戏", "note": "SLG小游戏"},
    {"id": 647, "name": "群雄逐鹿", "type": "微信小游戏", "note": "SLG经营"},
    {"id": 648, "name": "我才是首富", "type": "微信小游戏", "note": "财富放置"},
    {"id": 649, "name": "首富之路", "type": "微信小游戏", "note": "经营放置"},
    {"id": 650, "name": "宫廷计", "type": "微信小游戏", "note": "宫斗策略"},
    {"id": 651, "name": "宫斗小游戏", "type": "微信小游戏", "note": "宫斗女频"},
    {"id": 652, "name": "我要做皇帝", "type": "微信小游戏", "note": "古代经营"},
    {"id": 653, "name": "我的修仙游戏", "type": "微信小游戏", "note": "修仙放置"},
    {"id": 654, "name": "修仙立志传", "type": "微信小游戏", "note": "修仙剧情"},
    {"id": 655, "name": "修真：我有一个法宝", "type": "微信小游戏", "note": "修仙放置"},
    {"id": 656, "name": "凡人修仙传", "type": "微信小游戏", "note": "修仙IP"},
    {"id": 657, "name": "球球大作战 小游戏", "type": "微信小游戏", "note": "io竞技"},
    {"id": 658, "name": "贪吃蛇大作战", "type": "微信小游戏", "note": "io经典"},
    {"id": 659, "name": "海岛冒险", "type": "微信小游戏", "note": "经营冒险"},
    {"id": 660, "name": "海岛纪元", "type": "微信小游戏", "note": "海岛经营"},
    {"id": 661, "name": "全民切水果", "type": "微信小游戏", "note": "极简休闲"},
    {"id": 662, "name": "保卫城堡", "type": "微信小游戏", "note": "塔防"},
    {"id": 663, "name": "保卫王国", "type": "微信小游戏", "note": "塔防"},
    {"id": 664, "name": "塔防联盟", "type": "微信小游戏", "note": "塔防联盟"},
    {"id": 665, "name": "三国塔防", "type": "微信小游戏", "note": "三国塔防"},
    {"id": 666, "name": "三国合战", "type": "微信小游戏", "note": "三国合成"},
    {"id": 667, "name": "西游记小游戏", "type": "微信小游戏", "note": "西游IP放置"},
    {"id": 668, "name": "西游之路", "type": "微信小游戏", "note": "西游冒险"},
    {"id": 669, "name": "重生宫女", "type": "微信小游戏", "note": "宫斗女频"},
    {"id": 670, "name": "重生霸总", "type": "微信小游戏", "note": "霸总女频"},
    {"id": 671, "name": "霸总追妻", "type": "微信小游戏", "note": "霸总女频剧情"},
    {"id": 672, "name": "公主驾到", "type": "微信小游戏", "note": "古风换装"},
    {"id": 673, "name": "我的甜蜜小屋", "type": "微信小游戏", "note": "家居恋爱"},
    {"id": 674, "name": "甜蜜外卖屋", "type": "微信小游戏", "note": "经营恋爱"},
    {"id": 675, "name": "美食街物语", "type": "微信小游戏", "note": "美食经营"},
    {"id": 676, "name": "梦幻餐厅", "type": "微信小游戏", "note": "餐厅经营"},
    {"id": 677, "name": "汉字大冒险", "type": "微信小游戏", "note": "汉字解谜"},
    {"id": 678, "name": "进击的汉字", "type": "微信小游戏", "note": "文字解谜"},
    {"id": 679, "name": "成语大冒险", "type": "微信小游戏", "note": "成语解谜"},
    {"id": 680, "name": "数字消消乐", "type": "微信小游戏", "note": "数字消除"},
    {"id": 681, "name": "2048", "type": "微信小游戏", "note": "数字合成经典"},
    {"id": 682, "name": "迷你世界 小游戏", "type": "微信小游戏", "note": "沙盒UGC"},
    {"id": 683, "name": "蛋仔派对 小游戏", "type": "微信小游戏", "note": "派对社交"},
    {"id": 684, "name": "原神 小游戏", "type": "微信小游戏", "note": "二次元抽卡"},
    {"id": 685, "name": "蛋仔大冒险", "type": "微信小游戏", "note": "派对UGC"},
    {"id": 686, "name": "羊羊大世界", "type": "微信小游戏", "note": "解压放置"},
    {"id": 687, "name": "猫咪派对", "type": "微信小游戏", "note": "宠物治愈"},
    {"id": 688, "name": "猫猫的世界", "type": "微信小游戏", "note": "宠物休闲"},
    {"id": 689, "name": "我的恐龙", "type": "微信小游戏", "note": "恐龙养成"},
    {"id": 690, "name": "我的农场", "type": "微信小游戏", "note": "农场经营"},
    {"id": 691, "name": "全民切割大师", "type": "微信小游戏", "note": "极简解压"},
    {"id": 692, "name": "解压神器", "type": "微信小游戏", "note": "纯解压"},
    {"id": 693, "name": "毛线工房", "type": "微信小游戏", "note": "解压创作"},
    {"id": 694, "name": "DIY小屋", "type": "微信小游戏", "note": "创作装修"},
    {"id": 695, "name": "全民桌球", "type": "微信小游戏", "note": "桌球休闲"},
    {"id": 696, "name": "台球大师", "type": "微信小游戏", "note": "桌球技巧"},
    {"id": 697, "name": "全民传奇", "type": "微信小游戏", "note": "传奇MMORPG"},
    {"id": 698, "name": "传奇盛世", "type": "微信小游戏", "note": "传奇MMO"},
    {"id": 699, "name": "热血传奇", "type": "微信小游戏", "note": "传奇MMO"},
    {"id": 700, "name": "战神之路", "type": "微信小游戏", "note": "传奇放置"},

    # === 短剧 12 个 ===
    {"id": 701, "name": "战神/兵王类短剧（《无双》《赘婿崛起》）", "type": "短剧", "note": "男频还乡团兵王"},
    {"id": 702, "name": "赘婿/上门女婿类短剧", "type": "短剧", "note": "低位逆袭打脸"},
    {"id": 703, "name": "霸总/总裁追妻类短剧", "type": "短剧", "note": "女频霸总投射"},
    {"id": 704, "name": "复仇/打脸甜宠类短剧", "type": "短剧", "note": "女主复仇"},
    {"id": 705, "name": "重生/穿越中老年短剧", "type": "短剧", "note": "中老年现实补偿"},
    {"id": 706, "name": "悬疑反转/翻车类短剧", "type": "短剧", "note": "结尾反转烧脑"},
    {"id": 707, "name": "婆媳家庭伦理短剧", "type": "短剧", "note": "家庭伦理审判"},
    {"id": 708, "name": "豪门隐婚类短剧", "type": "短剧", "note": "女频隐婚反转"},
    {"id": 709, "name": "穿越古装宫斗短剧", "type": "短剧", "note": "女频古装宫斗"},
    {"id": 710, "name": "都市恶霸校园短剧", "type": "短剧", "note": "男频校园爽文"},
    {"id": 711, "name": "战场系开局短剧", "type": "短剧", "note": "男频军旅爽剧"},
    {"id": 712, "name": "民国/谍战短剧", "type": "短剧", "note": "民国情感悬疑"},

    # === 网文/网漫 10 个 ===
    {"id": 801, "name": "斗罗大陆系列（玄幻爽文）", "type": "网文", "note": "男频玄幻长线"},
    {"id": 802, "name": "凡人修仙传（修真长篇）", "type": "网文", "note": "境界感修仙"},
    {"id": 803, "name": "晋江女频言情/古言", "type": "网文", "note": "女频情感细腻"},
    {"id": 804, "name": "番茄都市/赘婿快餐文", "type": "网文", "note": "下沉超快爽文"},
    {"id": 805, "name": "推理悬疑小说（东野圭吾类）", "type": "出版小说", "note": "推理认知向"},
    {"id": 806, "name": "克苏鲁/科幻硬核小说", "type": "出版小说", "note": "认知扩展硬核"},
    {"id": 807, "name": "起点穿越历史文", "type": "网文", "note": "穿越历史改造"},
    {"id": 808, "name": "晋江百合文", "type": "网文", "note": "女女向亲密"},
    {"id": 809, "name": "快看漫画爽番", "type": "网漫", "note": "网漫女频"},
    {"id": 810, "name": "B站漫画硬核番", "type": "网漫", "note": "男频热血"},

    # === 影视/动漫 10 个 ===
    {"id": 901, "name": "甄嬛传 / 知否", "type": "电视剧", "note": "宫斗权谋"},
    {"id": 902, "name": "进击的巨人", "type": "日漫", "note": "热血+权谋+世界观"},
    {"id": 903, "name": "孤独的美食家", "type": "日剧", "note": "日常治愈"},
    {"id": 904, "name": "权力的游戏", "type": "美剧", "note": "权谋史诗"},
    {"id": 905, "name": "黑镜 / 怪奇物语", "type": "美剧", "note": "科幻反思"},
    {"id": 906, "name": "我的恶魔/恋综类", "type": "韩剧/综艺", "note": "亲密情感"},
    {"id": 907, "name": "鬼灭之刃", "type": "日漫", "note": "热血战斗"},
    {"id": 908, "name": "咒术回战", "type": "日漫", "note": "黑暗热血"},
    {"id": 909, "name": "庆余年", "type": "国产电视剧", "note": "权谋穿越"},
    {"id": 910, "name": "繁花", "type": "国产电视剧", "note": "怀旧叙事"},

    # === 综艺/恋综 8 个 ===
    {"id": 1001, "name": "心动的信号", "type": "恋综", "note": "国内恋综"},
    {"id": 1002, "name": "种地吧", "type": "综艺", "note": "慢综艺治愈"},
    {"id": 1003, "name": "披荆斩棘的哥哥", "type": "综艺", "note": "怀旧男团"},
    {"id": 1004, "name": "脱口秀大会/喜剧大赛", "type": "综艺", "note": "脱口秀"},
    {"id": 1005, "name": "向往的生活", "type": "综艺", "note": "田园慢综艺"},
    {"id": 1006, "name": "再见爱人", "type": "综艺", "note": "婚姻观察"},
    {"id": 1007, "name": "极限挑战", "type": "综艺", "note": "团体游戏"},
    {"id": 1008, "name": "明星大侦探", "type": "综艺", "note": "推理综艺"},

    # === 直播/视频博主 6 个 ===
    {"id": 1101, "name": "户外探险/野外生存直播", "type": "直播", "note": "替代探险"},
    {"id": 1102, "name": "李子柒/田园博主", "type": "短视频", "note": "田园治愈"},
    {"id": 1103, "name": "美食博主/吃播", "type": "短视频", "note": "美食陪伴"},
    {"id": 1104, "name": "电竞主播（PDD/老一辈）", "type": "直播", "note": "电竞陪伴"},
    {"id": 1105, "name": "美妆博主（口红/穿搭）", "type": "短视频", "note": "审美表达"},
    {"id": 1106, "name": "财经科普/二级博主", "type": "短视频", "note": "财经认知"},

    # === 社区/资讯/工具 6 个 ===
    {"id": 1201, "name": "小红书穿搭/家居博主", "type": "社区", "note": "审美表达"},
    {"id": 1202, "name": "B站知识区/财经科普", "type": "社区", "note": "认知获取"},
    {"id": 1203, "name": "豆瓣小组讨论", "type": "社区", "note": "亚文化讨论"},
    {"id": 1204, "name": "知乎深度回答", "type": "社区", "note": "认知精英"},
    {"id": 1205, "name": "TapTap社区", "type": "社区", "note": "游戏深度玩家"},
    {"id": 1206, "name": "番茄/七猫小说APP", "type": "工具", "note": "免费网文"},

    # === 棋牌/边界 4 个 ===
    {"id": 1301, "name": "斗地主/欢乐麻将（线下）", "type": "棋牌", "note": "习惯型社交"},
    {"id": 1302, "name": "天天德州扑克", "type": "棋牌", "note": "竞技博弈"},
    {"id": 1303, "name": "国标麻将（硬核）", "type": "棋牌", "note": "硬核策略"},
    {"id": 1304, "name": "象棋/围棋APP", "type": "棋牌", "note": "策略对弈"},
]

# ========== 12 强簇定义（来自 v1.0） ==========
CLUSTERS_DEF = """
| 簇 ID | 主任务 | 主承接偏好 | 核心收益 | 典型代表 |
|---|---|---|---|---|
| C01 | T1 情绪调节 | P1 强刺激覆盖 | — | 爽文/割草/爆装 |
| C02 | T1 情绪调节 | P2 情感共鸣 | — | 治愈/陪伴向 |
| C03 | T1 情绪调节 | P3 低负荷转移 | — | 消除/放置/短视频 |
| C04 | T2 自我确认 | P1 强刺激覆盖 | — | PVE 逆袭/战神向 |
| C05 | T2 自我确认 | P4 系统模拟 | Y1 竞争排名 | PVP战神/榜单 |
| C06 | T2 自我确认 | P4 系统模拟 | Y3 秩序优化 | 经济流派炫耀 |
| C07 | T3 亲密连接 | P2 情感共鸣 | — | 乙女/恋爱/角色养成 |
| C08 | T4 协作归属 | P2 情感共鸣 | — | MMO团魂/公会剧情 |
| C09 | T4 协作归属 | P4 系统模拟 | Y2 协作分工 | SLG联盟/MMO公会 |
| C10 | T5 认知扩展 | P4 系统模拟 | Y4 规则解码 | 解谜/构筑/策略 |
| C11 | T6 控制感重建 | P4 系统模拟 | Y3 秩序优化 | 模拟经营/建造 |
| C12 | T6 控制感重建 | P4 系统模拟 | Y1 竞争排名 | SLG重氪霸主 |

【作用域 boundary 判据】
- 满足感来自"我个体更强/更稀有" → 自我确认（C04/C05/C06）
- 满足感来自"我让一套系统/组织/世界按我规则运转" → 控制感重建（C11/C12）
- 主簇判断优先级：付费动机 > 留存动机 > 点击动机
- 副簇允许 0-2 个，超过 2 个标"产品定位模糊"
"""

def build_prompt_batch(samples_batch, batch_idx, total_batches):
    samples_str = "\n".join(
        f"{s['id']}. 【{s['type']}】《{s['name']}》— {s['note']}"
        for s in samples_batch
    )
    return f"""你是资深用户研究专家。请用以下"12 强簇候选 (v1.0)"对样本做归类验证。
这是第 {batch_idx}/{total_batches} 批，共 {len(samples_batch)} 个样本。

# 12 强簇定义

{CLUSTERS_DEF}

# 一级任务（6 个，互斥）

1. 情绪调节：处理焦虑、压抑、疲惫、无聊
2. 自我确认：确认我是谁、我有价值、我没掉队
3. 亲密连接：获得情感连接、被看见、被需要
4. 协作归属：在群体中有位置、有任务、被依赖
5. 认知扩展：理解世界、解码规则、满足好奇
6. 控制感重建：在不可控生活中建立可控小世界

# 主承接偏好（4 个）

- 强刺激覆盖：爽文、爆装、割草、搞笑、恐怖
- 情感共鸣：治愈、恋爱、剧情、陪伴
- 低负荷转移：消除、放置、美食、日常
- 系统模拟：SLG、经营、建造、解谜、策略

# 验证规则

1. 每个样本选 1 个**主簇**（C01-C12，或标"无合适簇"）
2. 如有显著副任务，标 1-2 个**副簇**
3. **冲突标记**：归类是否勉强、规则是否被打破，必须诚实标注
4. **不能拼凑**：若 12 簇都不合适，必须标"无合适簇"并说明缺什么维度
5. 棋牌/二次元抽卡/女性向悬疑古风等边界样本，按 boundary 判据归类后说明依据

# 待验证样本（{len(samples_batch)} 个）

{samples_str}

# 输出格式（JSON 数组，{len(samples_batch)} 个）

```json
[
  {{
    "id": 101,
    "name": "三国志战略版",
    "audience_desc": "核心受众一句话描述（30字内）",
    "main_task": "协作归属",
    "main_carrier": "系统模拟",
    "system_yield": "协作分工",
    "main_cluster": "C09",
    "secondary_clusters": ["C12"],
    "fit_quality": "good/marginal/poor/none",
    "conflict_note": "归类是否勉强、与哪个簇冲突、为什么（30字内，无冲突填'无'）",
    "missing_dim": "若 main_cluster=无合适簇，缺什么维度"
  }}
]
```

【硬约束】
- 全部样本必须有 main_cluster（C01-C12 或"无合适簇"）
- fit_quality 是 4 个枚举之一
- conflict_note 不允许写"无问题"等套话，要么"无"要么具体说明

只返回 JSON 数组，不要其他文字或代码块标记。"""

def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())

def write_report(all_results):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"validation_report_230samples_{TODAY}.md"

    cluster_count = {}
    fit_count = {"good": 0, "marginal": 0, "poor": 0, "none": 0}
    no_cluster_samples = []
    poor_samples = []
    secondary_count = 0
    conflicts = []
    type_cluster_matrix = {}  # type → cluster → count

    sample_by_id = {s["id"]: s for s in SAMPLES}

    for r in all_results:
        cluster = r.get("main_cluster", "未知")
        cluster_count[cluster] = cluster_count.get(cluster, 0) + 1

        fit = r.get("fit_quality", "unknown")
        if fit in fit_count:
            fit_count[fit] += 1
        if cluster == "无合适簇":
            no_cluster_samples.append(r)
        if fit == "poor":
            poor_samples.append(r)

        sec = r.get("secondary_clusters", [])
        if sec and len(sec) > 0:
            secondary_count += 1

        cn = r.get("conflict_note", "")
        if cn and cn != "无" and len(cn) > 3:
            conflicts.append(r)

        sample = sample_by_id.get(r["id"], {})
        s_type = sample.get("type", "未知")
        type_cluster_matrix.setdefault(s_type, {})
        type_cluster_matrix[s_type][cluster] = type_cluster_matrix[s_type].get(cluster, 0) + 1

    total = len(all_results)
    success_rate = (fit_count["good"] + fit_count["marginal"]) / total * 100 if total else 0
    secondary_rate = secondary_count / total * 100 if total else 0
    no_cluster_rate = fit_count["none"] / total * 100 if total else 0

    lines = [
        f"# 人群簇 v1.0 矩阵扩大验证报告（230 样本）",
        f"",
        f"**验证日期**：{TODAY}",
        f"**样本数**：{total}",
        f"**模型**：{MODEL}",
        f"",
        f"## 一、关键指标",
        f"",
        f"| 指标 | 数值 | 判据 |",
        f"|---|---|---|",
        f"| 归类成功率（good+marginal） | {success_rate:.1f}% | ≥85% 通过 |",
        f"| poor 质量率 | {fit_count['poor']/total*100:.1f}% | <15% 通过 |",
        f"| 无簇可归率 | {no_cluster_rate:.1f}% | <10% 通过 |",
        f"| 副簇 ≤ 2 个率 | 详见冲突清单 | <10% 超标 |",
        f"",
        f"## 二、12 簇归类分布",
        f"",
        f"| 簇 ID | 样本数 | 占比 | 状态 |",
        f"|---|---|---|---|",
    ]
    for cid in ["C01","C02","C03","C04","C05","C06","C07","C08","C09","C10","C11","C12","无合适簇"]:
        count = cluster_count.get(cid, 0)
        pct = count / total * 100 if total else 0
        status = "✅ 充足" if count >= 5 else ("⚠️ 偏少" if count > 0 else "❌ 空簇")
        if cid == "无合适簇":
            status = "⚠️ 需关注" if count > 0 else "✅ 无遗漏"
        lines.append(f"| {cid} | {count} | {pct:.1f}% | {status} |")

    lines += [
        f"",
        f"## 三、归类质量分布",
        f"",
        f"| 质量 | 样本数 |",
        f"|---|---|",
        f"| good | {fit_count['good']} |",
        f"| marginal | {fit_count['marginal']} |",
        f"| poor | {fit_count['poor']} |",
        f"| none | {fit_count['none']} |",
        f"",
        f"## 四、无合适簇样本（高优先级）",
        f"",
    ]
    if no_cluster_samples:
        for r in no_cluster_samples:
            lines.append(f"### {r['id']}. 《{r['name']}》")
            lines.append(f"- audience_desc：{r.get('audience_desc', '')}")
            lines.append(f"- missing_dim：{r.get('missing_dim', '')}")
            lines.append(f"")
    else:
        lines.append("无")
        lines.append("")

    lines += [
        f"## 五、Poor 质量样本",
        f"",
    ]
    if poor_samples:
        for r in poor_samples:
            lines.append(f"- {r['id']} 《{r['name']}》| 主簇 {r.get('main_cluster')} | {r.get('conflict_note','')}")
    else:
        lines.append("无")
    lines.append("")

    lines += [
        f"## 六、按类型归类分布（验证矩阵的覆盖度）",
        f"",
        f"| 样本类型 | 主要归簇分布 |",
        f"|---|---|",
    ]
    for s_type, cmap in sorted(type_cluster_matrix.items()):
        dist = sorted(cmap.items(), key=lambda x: -x[1])[:5]
        dist_str = "、".join(f"{c}({n})" for c, n in dist)
        lines.append(f"| {s_type} | {dist_str} |")

    lines += [
        f"",
        f"## 七、冲突清单",
        f"",
        f"共 {len(conflicts)} 个样本有冲突标注。",
        f"",
        f"| ID | 样本 | 主簇 | 副簇 | 质量 | 冲突说明 |",
        f"|---|---|---|---|---|---|",
    ]
    for r in conflicts:
        sec = "、".join(r.get("secondary_clusters", [])) or "—"
        lines.append(f"| {r['id']} | {r['name'][:20]} | {r['main_cluster']} | {sec} | {r['fit_quality']} | {r['conflict_note']} |")

    lines += [
        f"",
        f"## 八、所有 230 样本归类全表",
        f"",
        f"| ID | 类型 | 样本 | 主簇 | 副簇 | 质量 |",
        f"|---|---|---|---|---|---|",
    ]
    for r in all_results:
        sample = sample_by_id.get(r["id"], {})
        sec = "、".join(r.get("secondary_clusters", [])) or "—"
        lines.append(
            f"| {r['id']} | {sample.get('type','—')} | {r['name'][:20]} | {r['main_cluster']} | {sec} | {r['fit_quality']} |"
        )

    lines += [
        f"",
        f"## 九、自动判定",
        f"",
    ]
    if success_rate >= 85 and no_cluster_rate <= 10 and fit_count["poor"]/total*100 <= 15:
        verdict = "✅ 矩阵在 230 样本规模下仍然稳定，可保留 v1.0"
    elif success_rate >= 70:
        verdict = "⚠️ 矩阵基本可用，需补判据或处理边界样本"
    else:
        verdict = "❌ 矩阵需调整，回到 v1.1"

    lines.append(f"**结论**：{verdict}")

    # 关注点
    lines.append("")
    lines.append(f"## 十、关注点")
    lines.append("")
    empty_clusters = [c for c in ["C01","C02","C03","C04","C05","C06","C07","C08","C09","C10","C11","C12"]
                      if cluster_count.get(c, 0) < 5]
    if empty_clusters:
        lines.append(f"- 样本数 < 5 的簇：{', '.join(empty_clusters)}——观察是否需要合并或寻找更多样本")
    if cluster_count.get("无合适簇", 0) > 0:
        lines.append(f"- 关注 {cluster_count['无合适簇']} 个无合适簇样本")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log(f"  ✓ 写出报告：{report_path}")
    return report_path, success_rate, no_cluster_rate, fit_count

def main():
    log("=" * 60)
    log("人群簇 v1.0 矩阵扩大验证（230 样本）")
    log("=" * 60)
    log(f"模型：{MODEL}")
    log(f"总样本：{len(SAMPLES)}")
    log(f"输出：{OUTPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 分批：每批 46 个，共 5 批
    BATCH_SIZE = 46
    batches = [SAMPLES[i:i+BATCH_SIZE] for i in range(0, len(SAMPLES), BATCH_SIZE)]
    log(f"分 {len(batches)} 批，每批最多 {BATCH_SIZE} 个")

    all_results = []
    for i, batch in enumerate(batches, start=1):
        log(f"\n[{i}/{len(batches)}] 批次 {i}（{len(batch)} 样本）")
        prompt = build_prompt_batch(batch, i, len(batches))
        raw = call_llm_cached(prompt, f"validation_230_batch{i:02d}", max_tokens=16000)
        if not raw:
            log(f"  ❌ 批次 {i} 空响应")
            continue
        try:
            results = parse_json(raw)
            log(f"  解析 {len(results)} 个结果")
            all_results.extend(results)
        except Exception as e:
            log(f"  ❌ 批次 {i} 解析失败：{e}")
            log(f"  原始前 300：{raw[:300]}")

    log(f"\n[最终] 总解析 {len(all_results)} 个结果（期望 {len(SAMPLES)}）")
    if not all_results:
        log("❌ 无可用结果，退出")
        return

    report_path, success, no_cluster, fit_count = write_report(all_results)

    log("\n" + "=" * 60)
    log(f"✅ 验证完成！")
    log(f"   归类成功率：{success:.1f}%")
    log(f"   poor 质量数：{fit_count['poor']}")
    log(f"   无簇可归数：{fit_count['none']}")
    log(f"   报告：{report_path}")
    log("=" * 60)

if __name__ == "__main__":
    main()
