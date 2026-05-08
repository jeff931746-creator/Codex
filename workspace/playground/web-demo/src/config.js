export const W = 1280;
export const H = 720;
export const MATCH_DURATION = 480;
export const ROAD_LEFT = 332;
export const ROAD_RIGHT = 948;
export const CENTER_X = (ROAD_LEFT + ROAD_RIGHT) / 2;
export const HERO_LEASH = 240;

export const ROUTE = [
  { x: 640, y: 640, label: "出发" },
  { x: 560, y: 560, label: "外环路口" },
  { x: 720, y: 480, label: "加油站" },
  { x: 520, y: 390, label: "商场广场" },
  { x: 760, y: 300, label: "医院街口" },
  { x: 500, y: 210, label: "地铁口" },
  { x: 640, y: 140, label: "安全区" },
];

export const SPAWN_GATES = [
  { x: -24, y: 120 },
  { x: 1304, y: 150 },
  { x: -24, y: 540 },
  { x: 1304, y: 520 },
  { x: 220, y: -24 },
  { x: 1060, y: -24 },
  { x: 250, y: 744 },
  { x: 1030, y: 744 },
];

export const zombieDefs = {
  walker: {
    label: "普通丧尸",
    color: "#8fe17b",
    radius: 15,
    hp: 24,
    speed: 30,
    damage: 6,
    score: 40,
    xp: 1,
  },
  runner: {
    label: "冲锋丧尸",
    color: "#b1ff92",
    radius: 13,
    hp: 16,
    speed: 44,
    damage: 4,
    score: 55,
    xp: 1,
  },
  brute: {
    label: "重型丧尸",
    color: "#ff8f8d",
    radius: 24,
    hp: 42,
    speed: 20,
    damage: 12,
    score: 120,
    xp: 2,
  },
  spitter: {
    label: "喷吐丧尸",
    color: "#7db5ff",
    radius: 18,
    hp: 28,
    speed: 24,
    damage: 8,
    score: 90,
    xp: 2,
  },
  elite: {
    label: "精英尸群",
    color: "#ffcf6e",
    radius: 22,
    hp: 70,
    speed: 26,
    damage: 10,
    score: 220,
    xp: 3,
  },
  boss: {
    label: "尸潮 Boss",
    color: "#ff6575",
    radius: 36,
    hp: 220,
    speed: 16,
    damage: 18,
    score: 900,
    xp: 8,
  },
};

export const jokerPool = [
  {
    id: "escort_armor",
    title: "守车小丑",
    rarity: "common",
    tag: "防守",
    description: "护送目标最大耐久 +30，并立刻修复 20 点。等级越高，检查点修复越强。",
    maxLevel: 3,
    condition: () => true,
    apply: (game, card) => {
      const level = card.level;
      game.escort.maxHp += 24 + (level - 1) * 12;
      game.escort.hp = Math.min(game.escort.maxHp, game.escort.hp + 18 + (level - 1) * 8);
      game.escort.checkpointHeal += 6 + (level - 1) * 4;
    },
  },
  {
    id: "escort_speed",
    title: "推进小丑",
    rarity: "common",
    tag: "节奏",
    description: "护送目标移动速度 +12%。等级越高，推进节奏越稳。",
    maxLevel: 3,
    condition: () => true,
    apply: (game, card) => {
      const level = card.level;
      game.escort.speed *= 1 + 0.1 + (level - 1) * 0.05;
    },
  },
  {
    id: "hero_damage",
    title: "重击小丑",
    rarity: "common",
    tag: "攻击",
    description: "主角武器伤害 +5。等级越高，击杀成长越快。",
    maxLevel: 4,
    condition: () => true,
    apply: (game, card) => {
      const level = card.level;
      game.hero.damageBonus += 4 + (level - 1) * 3;
    },
  },
  {
    id: "hero_fire",
    title: "连射小丑",
    rarity: "common",
    tag: "节奏",
    description: "开火冷却 -16%。等级越高，射击节奏越紧。",
    maxLevel: 4,
    condition: () => true,
    apply: (game, card) => {
      const level = card.level;
      game.hero.fireRateMult *= Math.max(0.72, 0.86 - (level - 1) * 0.03);
    },
  },
  {
    id: "multi_shot",
    title: "散射小丑",
    rarity: "uncommon",
    tag: "弹幕",
    description: "每次开火额外发射 1 枚子弹。等级越高，弹幕扩张越强。",
    maxLevel: 3,
    condition: (game) => game.hero.bulletsPerShot < 4,
    apply: (game, card) => {
      const level = card.level;
      game.hero.bulletsPerShot += 1 + Math.floor((level - 1) / 2);
      game.hero.spread += 0.14 + (level - 1) * 0.04;
    },
  },
  {
    id: "pierce_rounds",
    title: "穿刺小丑",
    rarity: "uncommon",
    tag: "攻击",
    description: "子弹穿透次数 +1。等级越高，穿刺后还能增伤。",
    maxLevel: 3,
    condition: () => true,
    apply: (game, card) => {
      const level = card.level;
      game.hero.pierce += level;
      game.hero.damageBonus += Math.max(0, level - 1);
    },
  },
  {
    id: "repair_drone",
    title: "修理小丑",
    rarity: "uncommon",
    tag: "防守",
    description: "每经过一个路段检查点，护送目标额外回复 18 点。等级越高，回复更稳。",
    maxLevel: 3,
    condition: () => true,
    apply: (game, card) => {
      const level = card.level;
      game.escort.checkpointHeal += 14 + level * 8;
    },
  },
  {
    id: "chain_burst",
    title: "连锁小丑",
    rarity: "rare",
    tag: "爆发",
    description: "击杀丧尸后会对附近敌人造成溅射伤害。等级越高，爆炸范围更大。",
    maxLevel: 3,
    condition: (game) => !game.hero.chainBurst,
    apply: (game, card) => {
      const level = card.level;
      game.hero.chainBurst = true;
      game.hero.chainBurstRadius = 84 + (level - 1) * 22;
      game.hero.chainBurstDamage = 8 + (level - 1) * 4;
    },
  },
  {
    id: "aim_assist",
    title: "锁敌小丑",
    rarity: "common",
    tag: "节奏",
    description: "自动索敌范围 +70，火力更容易锁住拦路怪。等级越高，优先级越高。",
    maxLevel: 3,
    condition: () => true,
    apply: (game, card) => {
      const level = card.level;
      game.hero.range += 60 + (level - 1) * 25;
    },
  },
  {
    id: "panic_blast",
    title: "绝境小丑",
    rarity: "rare",
    tag: "爆发",
    description: "当护送目标生命较低时，自动触发一次范围冲击。等级越高，触发阈值更宽。",
    maxLevel: 2,
    condition: (game) => !game.hero.panicBlast,
    apply: (game, card) => {
      const level = card.level;
      game.hero.panicBlast = true;
      game.hero.panicBlastThreshold = 0.4 + level * 0.05;
    },
  },
  {
    id: "fission_joker",
    title: "裂变小丑",
    rarity: "legendary",
    tag: "弹幕",
    description: "每 5 次击杀，下一轮射击会额外分裂两枚子弹。",
    maxLevel: 2,
    condition: () => true,
    apply: (game, card) => {
      game.hero.fissionKillsNeeded = Math.max(3, 5 - (card.level - 1));
      game.hero.fissionShotBonus = 2 + (card.level - 1);
    },
  },
  {
    id: "mirror_joker",
    title: "镜像小丑",
    rarity: "rare",
    tag: "节奏",
    description: "每次抽牌时，会有一张已拥有小丑的镜像回响。",
    maxLevel: 2,
    condition: () => true,
    apply: (game, card) => {
      game.dupChoiceBonus = 1 + (card.level - 1);
    },
  },
];
