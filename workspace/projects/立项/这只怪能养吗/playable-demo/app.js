"use strict";
/* 这只怪能养吗 — 可玩 Demo
   按 00-立项文档/系统设计 实现完整地牢体验：
   大厅 → 约束随机地图(含分叉选路) → 房间(战斗/事件/自选/Boss) → 购买/捉宠/结算 → 大厅
   战斗：自动为底+手动可选；伤害=基础×技能倍率×属性克制系数 */

// ============================================================
// 一、静态数据配置
// ============================================================
const ELEMENTS = { fire: "火", water: "水", shadow: "影", grass: "草", light: "光" };
const ELEM_COLOR = { fire: "#ef5b58", water: "#5fc8ff", shadow: "#a87dff", grass: "#7fd66a", light: "#ffd76a" };
// 克制关系：A 克制 COUNTER[A]
const COUNTER = { fire: "grass", grass: "water", water: "fire", light: "shadow", shadow: "light" };

const TEAM = [
  { id: "slime", name: "粘液法师", role: "远程 / 弹射", element: "water", color: "#52dfd0", damage: 9, fireRate: 0.7, range: 560 },
  { id: "wolf", name: "幼焰狼", role: "近战 / 灼烧", element: "fire", color: "#ef5b58", damage: 15, fireRate: 1.0, range: 320 },
  { id: "fox", name: "影狐", role: "穿透 / 合击", element: "shadow", color: "#a87dff", damage: 12, fireRate: 0.88, range: 520 },
];

const HERO_SKILLS = [
  { id: "meteor", name: "陨火", icon: "F", cd: 7, damage: 56, radius: 140, color: "#ef5b58", element: "fire", kind: "aoe",
    desc: "范围 AOE 爆发，自动砸向最密集敌群。手动卡聚怪时机收益翻倍。" },
  { id: "frost", name: "冰封", icon: "I", cd: 8, damage: 30, radius: 170, color: "#5fc8ff", element: "water", kind: "control",
    desc: "大范围低伤 + 减速，为宠物制造输出窗口。危机时手动救场。" },
];

// 肉鸽放大器池（局内临时）。割草向：质变 Build 优先，一眼看出战场两样
const AMPLIFIERS = [
  // —— 质变（改变打法）——
  { id: "pierce", type: "all", tier: 0, key: "贯穿", name: "贯穿弹", desc: "所有子弹穿透敌人，每颗多打 2 个目标。清群神器。", apply: (m) => (m.pierce += 2) },
  { id: "chain", type: "all", tier: 0, key: "连环爆", name: "连环爆", desc: "击杀时引发小范围爆炸，连锁清场。怪越密越爽。", apply: (m) => (m.chain += 1) },
  { id: "split", type: "pet", tier: 0, key: "分裂", name: "分裂射击", desc: "宠物每次攻击额外射出 2 发偏角子弹，弹幕加倍。", apply: (m) => (m.split += 2) },
  { id: "field", type: "hero", tier: 0, key: "火海", name: "陨火·火海", desc: "陨火落点残留持续燃烧地带，站上去的怪不断掉血。", apply: (m) => (m.meteorField = true) },
  // —— 数值放大 ——
  { id: "all_atk", type: "all", tier: 0, name: "锋锐", desc: "全体输出 +25%。", apply: (m) => (m.allDamage += 0.25) },
  { id: "wolf_rate", type: "pet", tier: 0, name: "烈焰连击", desc: "宠物攻速 +40%，弹幕更密。", apply: (m) => { m.rate.wolf += 0.4; m.rate.slime += 0.4; m.rate.fox += 0.4; } },
  { id: "hero_cd", type: "hero", tier: 0, name: "主角爆发", desc: "主角技能冷却 -35%。", apply: (m) => (m.heroCd -= 0.35) },
  { id: "combo_gain", type: "combo", tier: 0, name: "合击蓄能", desc: "合击蓄力速度 +60%。", apply: (m) => (m.comboGain += 0.6) },
  { id: "lifesteal", type: "all", tier: 0, name: "汲取", desc: "全体输出 +12%，击杀回 4 点队伍生命。", apply: (m) => { m.allDamage += 0.12; m.lifesteal += 4; } },
  // —— 扩展层（养成解锁）——
  { id: "pierce2", type: "all", tier: 1, key: "贯穿", name: "无尽贯穿", desc: "子弹再多穿透 4 个目标，全体输出 +20%。", apply: (m) => { m.pierce += 4; m.allDamage += 0.2; } },
  { id: "chain2", type: "all", tier: 1, key: "连环爆", name: "殉爆", desc: "连环爆威力翻倍、范围更大，克制命中额外 +30%。", apply: (m) => { m.chain += 2; m.counterBoost += 0.3; } },
  { id: "combo_pow", type: "combo", tier: 1, name: "合击狂热", desc: "合击伤害 +80%，释放后全场减速。", apply: (m) => (m.comboPow += 0.8) },
];

// 野生宠物刷新（含属性、稀有度、物种基础捕获率）
const WILD_PETS = [
  { id: "slime_w", name: "蓝粘怪", element: "water", rarity: "common", base: 0.65, color: "#5fc8ff" },
  { id: "bat", name: "暗影蝠", element: "shadow", rarity: "common", base: 0.6, color: "#8e7bd6" },
  { id: "leaf", name: "草叶兔", element: "grass", rarity: "common", base: 0.62, color: "#7fd66a" },
  { id: "fire_wolf", name: "炎狼崽", element: "fire", rarity: "rare", base: 0.42, color: "#ef5b58" },
  { id: "ice_deer", name: "冰角鹿", element: "water", rarity: "rare", base: 0.4, color: "#7bd7ff" },
  { id: "shadow_fox", name: "幻尾狐", element: "shadow", rarity: "epic", base: 0.26, color: "#c89bff" },
  { id: "sun_bird", name: "曦光雀", element: "light", rarity: "epic", base: 0.24, color: "#ffd76a" },
];

const BALLS = [
  { id: "basic", name: "基础球", mult: 1, color: "#cfd8e6" },
  { id: "great", name: "高级球", mult: 2, color: "#5fc8ff" },
];
const ITEMS = [
  { id: "para", name: "麻痹药", state: "para", runs: 3 },
  { id: "sleep", name: "催眠药", state: "sleep", runs: 3 },
];
const STATE_MULT = { none: 1, para: 1.5, sleep: 2.5 };
const STATE_FLEE = { none: 1, para: 0.1, sleep: 0 };

const RECIPE = { battle: 6, elite: 1, event: 2, choice: 1, boss: 1 };
const ROOM_META = {
  battle: { icon: "⚔️", name: "战斗房" },
  elite: { icon: "💀", name: "精英房" },
  event: { icon: "❓", name: "随机事件房" },
  choice: { icon: "🎁", name: "自选节点" },
  boss: { icon: "🏆", name: "Boss 房" },
};

// ============================================================
// 二、跨局元状态（内存持久）
// ============================================================
const meta = {
  caught: new Set(),
  seen: new Set(),
  materials: 0,
  poolTier: 0, // 养成层级：0=基础, 1=扩展
  heroSkillId: "meteor",
  clears: 0,
};

let run = null; // 当前地牢局
let state = null; // 当前战斗运行时
let cap = null; // 当前捉宠场景

const $ = (id) => document.getElementById(id);
const canvas = $("gameCanvas");
const ctx = canvas.getContext("2d");
const capCanvas = $("captureCanvas");
const capCtx = capCanvas.getContext("2d");

// ============================================================
// 三、屏幕切换
// ============================================================
const SCREENS = ["lobbyScreen", "mapScreen", "roomScreen", "captureScreen"];
function showScreen(id) {
  SCREENS.forEach((s) => $(s).classList.toggle("hidden", s !== id));
}

// ============================================================
// 四、大厅
// ============================================================
function renderLobby() {
  showScreen("lobbyScreen");
  const starter = TEAM[1];
  $("lobbyTeam").innerHTML = `
    <div class="team-row">
      <div class="team-portrait" style="border-radius:50%;background:radial-gradient(circle at 35% 28%, #fff, ${starter.color} 45%, #10141c)"></div>
      <div><div class="team-name">${starter.name}</div><div class="team-role">开局唯一宠物 · ${starter.role}</div></div>
      <span class="elem-chip" style="background:${ELEM_COLOR[starter.element]}33;color:${ELEM_COLOR[starter.element]}">${ELEMENTS[starter.element]}</span>
    </div>`;

  $("lobbySkills").innerHTML = HERO_SKILLS.map((s) => `
    <div class="skill-pick ${s.id === meta.heroSkillId ? "on" : ""}" data-skill="${s.id}">
      <div class="team-portrait" style="border-radius:9px;display:grid;place-items:center;background:${s.color}22;color:${s.color};font-weight:900;font-size:20px">${s.icon}</div>
      <div><div class="team-name">${s.name}</div><div class="team-role">${s.desc}</div></div>
      <span class="elem-chip" style="background:${s.color}22;color:${s.color}">选用</span>
    </div>`).join("");
  document.querySelectorAll(".skill-pick").forEach((el) =>
    el.addEventListener("click", () => { meta.heroSkillId = el.dataset.skill; renderLobby(); }));

  $("dexCaught").textContent = meta.caught.size;
  $("dexSeen").textContent = meta.seen.size;
  $("matCount").textContent = meta.materials;
  $("poolNote").textContent = meta.poolTier >= 1 ? "当前放大器池：基础 + 扩展（已养成）" : "当前放大器池：基础（攒材料可升级）";
  $("trainBtn").disabled = meta.materials < 5 || meta.poolTier >= 1;
  $("trainBtn").textContent = meta.poolTier >= 1 ? "已解锁扩展放大器池" : "用 5 材料升级队伍（解锁扩展放大器）";
}

$("trainBtn").addEventListener("click", () => {
  if (meta.materials >= 5 && meta.poolTier < 1) { meta.materials -= 5; meta.poolTier = 1; renderLobby(); }
});
$("enterDungeonBtn").addEventListener("click", startRun);

// ============================================================
// 五、地牢地图：约束随机生成 + 分叉
// ============================================================
function shuffle(a) { const r = a.slice(); for (let i = r.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [r[i], r[j]] = [r[j], r[i]]; } return r; }

function validSequence(arr) {
  const n = arr.length;
  if (arr[n - 1] !== "boss") return false;
  if (arr.slice(0, -1).includes("boss")) return false;
  if (!(arr[n - 2] === "choice" || arr[n - 3] === "choice")) return false; // Boss 前 2 间有自选
  for (let i = 2; i < n; i++) if (arr[i] === arr[i - 1] && arr[i] === arr[i - 2]) return false; // 连续上限 2
  const protect = Math.floor(0.4 * n);
  const ei = arr.indexOf("elite");
  if (ei >= 0 && ei < protect) return false; // 早期保护
  const evs = arr.map((t, i) => (t === "event" ? i : -1)).filter((i) => i >= 0);
  if (evs.length >= 2) { const half = Math.floor(n / 2); if (!(evs.some((i) => i < half) && evs.some((i) => i >= half))) return false; } // 事件分散
  return true;
}

function genSequence() {
  const pool = [];
  Object.entries(RECIPE).forEach(([t, n]) => { for (let i = 0; i < n; i++) pool.push(t); });
  const fixed = pool.filter((t) => t !== "boss");
  for (let attempt = 0; attempt < 600; attempt++) {
    const arr = shuffle(fixed).concat("boss");
    if (validSequence(arr)) return arr;
  }
  return ["battle", "battle", "event", "battle", "elite", "battle", "event", "battle", "choice", "battle", "boss"]; // 兜底合法序列
}

// 路线类型判定
function routeLabel(types) {
  if (types.includes("elite")) return { type: "精英线", tag: "高风险 · 高品质购买", risk: 2 };
  if (types.includes("choice")) return { type: "Build 线", tag: "确定性技能强化", risk: 1 };
  if (types.includes("event")) return { type: "事件线", tag: "不确定收益 · 遇宠机会", risk: 1 };
  return { type: "安全线", tag: "低风险 · 稳定基础收益", risk: 0 };
}

function startRun() {
  const path = genSequence();
  // 设置一个分叉点：取主线中段 2 间为安全线A，另造一条不同类型的等长岔路B
  const forkAt = 4;
  const forkLen = 2;
  const branchA = path.slice(forkAt, forkAt + forkLen);
  const aLabel = routeLabel(branchA);
  // B 取一种与 A 不同的路线类型
  const altPool = [
    { types: ["elite", "battle"], label: { type: "精英线", tag: "高风险 · 高品质购买", risk: 2 } },
    { types: ["event", "battle"], label: { type: "事件线", tag: "不确定收益 · 遇宠机会", risk: 1 } },
    { types: ["choice", "battle"], label: { type: "Build 线", tag: "确定性技能强化", risk: 1 } },
  ].filter((o) => o.label.type !== aLabel.type);
  const altB = altPool[Math.floor(Math.random() * altPool.length)];

  run = {
    path, // 已解析的房间序列（选 B 后会替换分叉段）
    fork: { at: forkAt, len: forkLen, branchA, labelA: aLabel, branchB: altB.types, labelB: altB.label, chosen: null },
    pos: -1, // 当前所在房间索引；-1 表示尚未进入第一间
    floor: meta.clears + 1,
    coins: 30,
    balls: { basic: 5, great: 1 },
    items: { para: 1, sleep: 1 },
    build: [],
    team: [{ ...TEAM[1] }], // 开局只带 1 只（幼焰狼），抓宠途中变多 → 成长感
    hp: 100, maxHp: 100, // 队伍生命跨房间保留
    mods: freshMods(),
    runCaught: 0, runSeen: 0,
  };
  goNextRoom(); // 直接进第一间，走门推进
}

function freshMods() {
  return { allDamage: 0, rate: { wolf: 0, slime: 0, fox: 0 }, dmg: { wolf: 0, slime: 0, fox: 0 },
    heroCd: 0, heroPow: 0, comboGain: 0, comboPow: 0, counterBoost: 0, lifesteal: 0, captureBoost: 0,
    pierce: 0, chain: 0, split: 0, meteorField: false };
}

// 本局战力（成长感可视化）：队伍数 × 基础 × Build 加成
function teamPower() {
  const petBase = run.team.reduce((s, p) => s + p.damage * (1 + (run.mods.dmg[p.id] || 0)) * (1 + (run.mods.rate[p.id] || 0)), 0);
  const buildMult = 1 + run.mods.allDamage + run.mods.pierce * 0.25 + run.mods.chain * 0.3 + run.mods.split * 0.15;
  return Math.round(petBase * buildMult * 4 + run.team.length * 40);
}

function renderMap() {
  const f = run.fork;
  const track = $("mapTrack");
  let html = "";
  for (let i = 0; i < run.path.length; i++) {
    if (i === f.at) {
      // 分叉段：两行
      const chosen = f.chosen;
      const rowA = f.branchA.map((t, k) => nodeHtml(t, f.at + k, chosen === "B" ? "locked" : (chosen === "A" ? statusAt(f.at + k) : "preview"))).join('<span class="map-link"></span>');
      const rowB = f.branchB.map((t, k) => nodeHtml(t, -1, chosen === "A" ? "locked" : (chosen === "B" ? statusAt(f.at + k) : "preview"))).join('<span class="map-link"></span>');
      html += '<span class="map-link"></span>';
      html += `<div class="node-col"><div class="fork-rows">
        <div class="map-node-wrap">${rowA}</div>
        <div class="map-node-wrap">${rowB}</div>
      </div></div>`;
      i += f.len - 1;
      continue;
    }
    if (i > 0) html += '<span class="map-link"></span>';
    html += `<div class="node-col">${nodeHtml(run.path[i], i, statusAt(i))}</div>`;
  }
  track.innerHTML = html;

  $("mapCoins").textContent = `金币 ${run.coins}`;
  $("mapHp").textContent = `队伍 ${Math.round((run.hp / run.maxHp) * 100)}%`;

  // 下一间提示 / 前进按钮 / 分叉
  const nextIndex = run.pos + 1;
  const fp = $("forkPanel");
  if (nextIndex === f.at && !f.chosen) {
    fp.classList.remove("hidden");
    $("advanceBtn").classList.add("hidden");
    $("nextHint").textContent = "前方分叉，选择路线";
    $("forkChoices").innerHTML = [
      forkCardHtml("A", f.labelA, f.branchA),
      forkCardHtml("B", f.labelB, f.branchB),
    ].join("");
    document.querySelectorAll(".fork-card").forEach((el) =>
      el.addEventListener("click", () => chooseFork(el.dataset.branch)));
  } else {
    fp.classList.add("hidden");
    $("advanceBtn").classList.remove("hidden");
    if (nextIndex >= run.path.length) {
      $("nextHint").textContent = "本局已结束";
      $("advanceBtn").disabled = true;
    } else {
      const t = run.path[nextIndex];
      $("advanceBtn").disabled = false;
      $("advanceBtn").textContent = run.pos < 0 ? "进入第一间" : "前进";
      $("nextHint").innerHTML = `下一间：<b>${ROOM_META[t].icon} ${ROOM_META[t].name}</b>`;
    }
  }
}

function statusAt(i) {
  if (i < run.pos) return "done";
  if (i === run.pos) return "current";
  return "next";
}
function nodeHtml(type, i, status) {
  const m = ROOM_META[type];
  const cls = ["map-node", type, status === "done" ? "done" : "", status === "current" ? "current" : "", (status === "locked" || status === "preview") ? "" : "", status === "locked" ? "locked" : ""].join(" ");
  return `<div class="${cls}">${m.icon}<small>${m.name}</small></div>`;
}
function forkCardHtml(branch, label, types) {
  const preview = types.map((t) => ROOM_META[t].icon).join(" ");
  return `<button class="fork-card" data-branch="${branch}">
    <div class="fork-type">${label.type}</div>
    <div class="fork-tag">${label.tag}</div>
    <div class="fork-preview">${preview}</div>
  </button>`;
}

function chooseFork(branch) {
  const f = run.fork;
  f.chosen = branch;
  if (branch === "B") {
    for (let k = 0; k < f.len; k++) run.path[f.at + k] = f.branchB[k];
  }
  renderMap();
}

$("advanceBtn").addEventListener("click", () => {
  run.pos += 1;
  enterRoom(run.path[run.pos]);
});
$("abandonBtn").addEventListener("click", () => {
  openModal({
    label: "确认", title: "放弃本局？", sub: "当局已获得的金币、未入仓的进度将清零，返回大厅。",
    actions: [
      { text: "继续探索", ghost: true, on: (m) => closeModal(m) },
      { text: "放弃并返回", on: (m) => { closeModal(m); meta.materials += run.runCaught * 0; endRunToLobby(false, "你放弃了本局。"); } },
    ],
  });
});

// ============================================================
// 六、实时走房间导航（走进门 → 下一间；右上角小地图）
// ============================================================
const DOOR_Y = 150;       // 门所在的墙线（玩家走到这里出门）
const COMBAT_KIND = { battle: 1, elite: 1, boss: 1 };

function buildDoors(pos) {
  if (run.path[pos] === "boss") return []; // Boss 房：清场即通关，无出口
  const nextIsFork = pos + 1 === run.fork.at && !run.fork.chosen;
  if (nextIsFork) return [
    { x: 430, w: 130, kind: "forkA", label: run.fork.labelA.type, types: run.fork.branchA, open: false },
    { x: 850, w: 130, kind: "forkB", label: run.fork.labelB.type, types: run.fork.branchB, open: false },
  ];
  return [{ x: 640, w: 150, kind: "exit", open: false }];
}

function enterRoom(type) {
  if (COMBAT_KIND[type]) startBattle(type === "battle" ? "normal" : type);
  else setupExplore(type);
}

// 非战斗房：走到中央发光节点触发事件 / 自选
function setupExplore(type) {
  state = {
    sub: type, kind: type, status: "explore", cleared: false, triggered: false,
    time: 0, wave: 1, maxWave: 1,
    hero: { x: 640, y: 600, face: 1, moving: false },
    hp: run.hp, maxHp: run.maxHp, shield: 0,
    pets: run.team.map((p, i) => ({ ...p, x: 590 + i * 50, y: 640 - i * 30, cooldown: 0 })),
    killStreak: 0, streakTimer: 0, totalKills: 0, fields: [],
    skills: [], combo: 0,
    enemies: [], projectiles: [], particles: [], damageNumbers: [], shockwaves: [], shake: 0,
    dust: [], mods: run.mods,
    doors: buildDoors(run.pos),
    interactable: { x: 640, y: 360, kind: type },
  };
  $("roomTitle").textContent = ROOM_META[type].name;
  $("roomSub").textContent = type === "choice" ? "走到礼盒处领取免费强化" : "走到 ? 处触发事件";
  renderBattleStaticUi();
  setLog(type === "choice" ? "走到中央礼盒领取免费 3 选 1。" : "走到中央 ? 触发随机事件。");
  showScreen("roomScreen");
}

// 房间目标完成 → 开门放行（替代原来的回地图）
function roomCleared() {
  if (!state) return;
  state.cleared = true;
  state.doors.forEach((d) => (d.open = true));
  state.status = state.kind && COMBAT_KIND[state.kind] ? "cleared" : "exploreDone";
  setLog("出口已开，走到门口进入下一间。");
  showScreen("roomScreen");
}

function goNextRoom(branch) {
  if (branch) chooseFork(branch);
  run.pos += 1;
  if (run.pos >= run.path.length) { endRunToLobby(true); return; }
  enterRoom(run.path[run.pos]);
}

// 每帧：触发节点 / 走门
function updateRoomNav(dt) {
  if (!state) return;
  if (!state.cleared) {
    if (!COMBAT_KIND[state.kind] && !state.triggered && state.interactable) {
      const d = Math.hypot(state.hero.x - state.interactable.x, state.hero.y - state.interactable.y);
      if (d < 48) { state.triggered = true; triggerRoom(state.kind); }
    }
    return;
  }
  for (const door of state.doors) {
    if (!door.open) continue;
    if (state.hero.y <= DOOR_Y + 16 && Math.abs(state.hero.x - door.x) < door.w / 2) {
      const branch = door.kind === "forkA" ? "A" : door.kind === "forkB" ? "B" : null;
      goNextRoom(branch);
      return;
    }
  }
}

function triggerRoom(kind) {
  if (kind === "choice") startChoiceNode();
  else if (kind === "event") enterEvent();
}

// ============================================================
// 七、战斗系统（自动为底 + 手动可选）
// ============================================================
const HERO_SPEED = 240;
const BOUNDS = { minX: 90, maxX: 1190, minY: 150, maxY: 640 };
const input = { joyX: 0, joyY: 0, keys: new Set() };
let auto = true;
let last = performance.now();

function startBattle(sub) {
  const skill = HERO_SKILLS.find((s) => s.id === meta.heroSkillId);
  state = {
    sub,
    status: "battle",
    time: 0,
    wave: 1,
    maxWave: sub === "boss" ? 2 : sub === "elite" ? 2 : 2,
    kind: sub === "normal" ? "battle" : sub, cleared: false, triggered: false,
    doors: buildDoors(run.pos), interactable: null,
    hero: { x: 640, y: 600, face: 1, moving: false },
    hp: run.hp, maxHp: run.maxHp, shield: 0,
    pets: run.team.map((p, i) => ({ ...p, x: 590 + i * 50, y: 640 - i * 30, cooldown: 0 })),
    killStreak: 0, streakTimer: 0, totalKills: 0, fields: [],
    skills: [
      { ...skill, cooldown: 0 },
      { id: "combo", name: "合击", icon: "X", cd: 0, color: "#a87dff", element: "shadow", kind: "combo" },
    ],
    combo: 0,
    enemies: [], projectiles: [], particles: [], damageNumbers: [], shockwaves: [], shake: 0,
    dust: makeDust(),
    mods: run.mods,
  };
  spawnWave();
  $("roomTitle").textContent = ROOM_META[run.path[run.pos]].name;
  $("roomSub").textContent = sub === "boss" ? "Boss 战 · 清空即通关" : "清空所有波次";
  $("autoToggle").classList.toggle("on", auto);
  $("autoToggle").textContent = `自动战斗：${auto ? "开" : "关"}`;
  renderBattleStaticUi();
  setLog(sub === "boss" ? "Boss 出现！自动战斗接管，可手动卡技能时机。" : "拖摇杆 / WASD 走位；宠物自动攻击，技能可手动放。");
  showScreen("roomScreen");
}

function spawnWave() {
  const sub = state.sub;
  const floor = run.floor;
  const room = run.pos; // 越往后房间越多怪 → 成长感
  const isBoss = sub === "boss";
  const isElite = sub === "elite";
  const elems = ["fire", "water", "grass", "shadow", "light"];
  const mk = (i, type) => {
    const hp = type === "boss" ? 700 + floor * 60 : type === "elite" ? 150 + floor * 14 : 18 + floor * 4 + room * 3;
    // 成群从右侧 + 上下边缘涌入，包夹主角
    const side = i % 3;
    let x = 760 + Math.random() * 320, y = 230 + Math.random() * 360;
    if (type === "minion") { if (side === 1) { y = 170 + Math.random() * 40; x = 300 + Math.random() * 760; } else if (side === 2) { y = 590 + Math.random() * 40; x = 300 + Math.random() * 760; } }
    return {
      id: crypto.randomUUID(), type,
      element: type === "boss" ? "shadow" : elems[Math.floor(Math.random() * elems.length)],
      x, y, hp, maxHp: hp,
      speed: type === "boss" ? 18 : type === "elite" ? 32 : 66 + Math.random() * 34,
      radius: type === "boss" ? 60 : type === "elite" ? 36 : 16 + Math.random() * 4,
      dmg: type === "boss" ? 15 : type === "elite" ? 9 : 6,
      attackTimer: Math.random() * 0.3, slow: 0, hitFlash: 0, bob: Math.random() * 6.28, face: -1,
    };
  };
  if (isBoss) {
    state.enemies = [mk(0, "boss")];
    for (let i = 1; i <= 8 + room; i++) state.enemies.push(mk(i, "minion")); // Boss 带小怪
  } else if (isElite) {
    state.enemies = [mk(0, "elite"), mk(1, "elite")];
    for (let i = 2; i <= 12 + room; i++) state.enemies.push(mk(i, "minion"));
  } else {
    const count = 8 + room * 2 + state.wave * 2; // 前期约10只，越深越多
    state.enemies = Array.from({ length: count }, (_, i) => mk(i, "minion"));
  }
}

function renderBattleStaticUi() {
  $("petList").innerHTML = state.pets.map((p) => `
    <div class="pet-card">
      <div class="pet-avatar" style="color:${p.color};background:radial-gradient(circle at 35% 26%, #fff8c9, ${p.color} 45%, #111827 82%)"></div>
      <div><div class="pet-name">${p.name}</div><div class="pet-role">${ELEMENTS[p.element]} · ${p.role}</div></div>
    </div>`).join("");
  $("skillRow").innerHTML = state.skills.map((s) => `
    <button class="skill-button" data-skill="${s.id}" type="button" title="${s.name}">
      <span class="skill-icon" style="color:${s.color}">${s.icon}</span>
      <span class="skill-name">${s.name}</span>
      <span class="cooldown hidden"></span>
    </button>`).join("");
  document.querySelectorAll(".skill-button").forEach((b) => b.addEventListener("click", () => useSkill(b.dataset.skill)));
}

function setLog(t) { $("floatLog").textContent = t; }

$("autoToggle").addEventListener("click", () => {
  auto = !auto;
  $("autoToggle").classList.toggle("on", auto);
  $("autoToggle").textContent = `自动战斗：${auto ? "开" : "关"}`;
});

$("roomAbandon").addEventListener("click", () => {
  openModal({ label: "确认", title: "放弃本局？", sub: "当局奖励清零，返回大厅（图鉴与材料保留）。",
    actions: [
      { text: "继续", ghost: true, on: (m) => closeModal(m) },
      { text: "放弃返回", on: (m) => { closeModal(m); endRunToLobby(false, "你放弃了本局。"); } },
    ] });
});

function updateBattleUi() {
  $("waveLabel").textContent = !COMBAT_KIND[state.kind] ? "探索中" : state.sub === "boss" ? `Boss · 第${state.wave}/${state.maxWave}波` : `波次 ${state.wave}/${state.maxWave}`;
  $("coinLabel").textContent = `金币 ${run.coins}`;
  $("roomSub").textContent = `战力 ${teamPower()} · 宠物 ${run.team.length} · 击杀 ${state.totalKills}`;
  $("hpText").textContent = `${Math.ceil(state.hp)}/${state.maxHp}${state.shield ? ` +${Math.ceil(state.shield)}` : ""}`;
  $("hpBar").style.width = `${Math.max(0, state.hp / state.maxHp) * 100}%`;
  $("comboText").textContent = `${Math.floor(state.combo)}%`;
  $("comboBar").style.width = `${Math.min(100, state.combo)}%`;
  document.querySelectorAll(".skill-button").forEach((b) => {
    const s = state.skills.find((x) => x.id === b.dataset.skill);
    const cd = b.querySelector(".cooldown");
    const ready = s.id === "combo" ? state.combo >= 100 : s.cooldown <= 0;
    b.classList.toggle("ready", ready);
    cd.classList.toggle("hidden", ready);
    cd.textContent = s.id === "combo" ? "" : Math.ceil(s.cooldown);
  });
}

function useSkill(id) {
  if (!state || state.status !== "battle") return;
  const s = state.skills.find((x) => x.id === id);
  if (id === "combo") {
    if (state.combo < 100) return;
    const x = state.hero.x + 360, y = state.hero.y - 10;
    blast(x, y, 230, 90 * (1 + state.mods.comboPow), "#a87dff", "shadow");
    state.enemies.forEach((e) => (e.slow = 2.6));
    state.combo = 0;
    setLog("影狐合击命中，全场压制！");
    return;
  }
  if (s.cooldown > 0) return;
  if (s.kind === "control") {
    const t = nearestEnemy(state.hero.x + 200, state.hero.y, 900) || state.enemies[0];
    if (t) { blast(t.x, t.y, s.radius, s.damage * (1 + state.mods.heroPow), s.color, s.element); state.enemies.forEach((e) => (e.slow = Math.max(e.slow, 2.2))); }
    setLog("冰封展开，敌群减速。");
  } else {
    const t = nearestEnemy(state.hero.x, state.hero.y, 900);
    if (t) {
      blast(t.x, t.y, s.radius, s.damage * (1 + state.mods.heroPow), s.color, s.element);
      if (state.mods.meteorField) state.fields.push({ x: t.x, y: t.y, r: s.radius, life: 3.5, tick: 0.3, dps: 22 + run.floor * 3 });
      setLog("陨火砸向最密集的敌群！");
    }
  }
  s.cooldown = s.cd * (1 + state.mods.heroCd);
}

function counterMult(atkElem, defElem) {
  if (COUNTER[atkElem] === defElem) return 1.5 + state.mods.counterBoost;
  return 1;
}

function blast(x, y, radius, damage, color, element, minor) {
  state.enemies.forEach((e) => {
    if (Math.hypot(e.x - x, e.y - y) < radius + e.radius) {
      const mult = counterMult(element, e.element);
      const dmg = Math.round(damage * (1 + state.mods.allDamage) * mult);
      e.hp -= dmg; e.hitFlash = 1;
      if (!minor || mult > 1) addDamageNumber(e.x, e.y - e.radius, dmg, mult > 1);
      if (mult > 1) addParticles(e.x, e.y, ELEM_COLOR[element], 8);
    }
  });
  state.shockwaves.push({ x, y, r: 8, max: radius, color, life: minor ? 0.28 : 0.45 });
  addParticles(x, y, color, minor ? 8 : 38);
  if (!minor) state.shake = Math.min(14, state.shake + 9);
}

function updateBattle(dt) {
  if (state.status !== "battle") return;
  state.time += dt;
  state.skills.forEach((s) => (s.cooldown = Math.max(0, s.cooldown - dt)));
  state.streakTimer = Math.max(0, state.streakTimer - dt);
  if (state.streakTimer <= 0) state.killStreak = 0;
  moveHero(dt); movePets(dt); updateEnemies(dt); heroSweep(dt); updatePetAttacks(dt);
  updateProjectiles(dt); updateFields(dt); updateParticles(dt); updateDamageNumbers(dt); updateShockwaves(dt);

  const dead = [];
  state.enemies = state.enemies.filter((e) => {
    if (e.hp > 0) return true;
    dead.push(e);
    run.coins += e.type === "boss" ? 80 : e.type === "elite" ? 18 : 2;
    state.combo = Math.min(100, state.combo + (e.type === "minion" ? 4 : 12) * (1 + state.mods.comboGain));
    state.hp = Math.min(state.maxHp, state.hp + state.mods.lifesteal);
    state.killStreak += 1; state.totalKills += 1; state.streakTimer = 2;
    addParticles(e.x, e.y, ELEM_COLOR[e.element], e.type === "boss" ? 60 : 12);
    if (e.type !== "minion") state.shake = Math.min(16, state.shake + (e.type === "boss" ? 16 : 5));
    return false;
  });
  // 连环爆：击杀引发小范围爆炸，连锁清场
  if (state.mods.chain > 0) dead.forEach((e) => {
    if (e.type === "minion") blast(e.x, e.y, 70 + state.mods.chain * 18, 10 + state.mods.chain * 8, "#ffb04d", e.element, true);
  });

  if (state.hp <= 0) { battleLose(); return; }
  if (state.enemies.length === 0) {
    if (state.wave < state.maxWave) { state.wave += 1; spawnWave(); setLog(`第 ${state.wave} 波来袭！`); state.shake = Math.min(16, state.shake + 6); }
    else battleWin();
  }
}

// 主角近身横扫：割草核心，移动到怪群里挥剑清场
function heroSweep(dt) {
  state.heroSwing = (state.heroSwing || 0) - dt;
  if (state.heroSwing > 0) return;
  const R = 82, hx = state.hero.x, hy = state.hero.y;
  let hit = 0;
  state.enemies.forEach((e) => {
    if (e.type === "minion" && Math.hypot(e.x - hx, e.y - hy) < R + e.radius) {
      const dmg = Math.round((15 + run.floor * 2) * (1 + state.mods.allDamage));
      e.hp -= dmg; e.hitFlash = 1; hit++;
      addDamageNumber(e.x, e.y - e.radius, dmg, false);
    }
  });
  if (hit) { state.shockwaves.push({ x: hx, y: hy, r: 20, max: R, color: "#ffe6aa", life: 0.3 }); state.swingFx = 0.18; }
  state.heroSwing = 0.45;
}

function updateFields(dt) {
  state.fields = (state.fields || []).filter((f) => {
    f.life -= dt; f.tick -= dt;
    if (f.tick <= 0) {
      f.tick = 0.3;
      state.enemies.forEach((e) => { if (Math.hypot(e.x - f.x, e.y - f.y) < f.r + e.radius) { const dmg = Math.round(f.dps * 0.3); e.hp -= dmg; e.hitFlash = Math.max(e.hitFlash, 0.4); if (Math.random() < 0.4) addDamageNumber(e.x, e.y - e.radius, dmg, false); } });
    }
    return f.life > 0;
  });
}

function moveHero(dt) {
  let dx = input.joyX, dy = input.joyY;
  if (input.keys.has("up")) dy -= 1; if (input.keys.has("down")) dy += 1;
  if (input.keys.has("left")) dx -= 1; if (input.keys.has("right")) dx += 1;
  const mag = Math.hypot(dx, dy);
  if (mag < 0.05) { state.hero.moving = false; return; }
  const sc = Math.min(1, mag);
  state.hero.x = Math.max(BOUNDS.minX, Math.min(BOUNDS.maxX, state.hero.x + (dx / mag) * HERO_SPEED * sc * dt));
  state.hero.y = Math.max(BOUNDS.minY, Math.min(BOUNDS.maxY, state.hero.y + (dy / mag) * HERO_SPEED * sc * dt));
  state.hero.face = dx < -0.05 ? -1 : dx > 0.05 ? 1 : state.hero.face;
  state.hero.moving = true;
}

function movePets(dt) {
  state.pets.forEach((p, i) => {
    const tx = state.hero.x - 88 + i * 64, ty = state.hero.y + 70 - i * 34;
    p.x += (tx - p.x) * Math.min(1, dt * 4.2);
    p.y += (ty - p.y) * Math.min(1, dt * 4.2);
  });
}

function updateEnemies(dt) {
  state.enemies.forEach((e) => {
    const sm = e.slow > 0 ? 0.42 : 1;
    e.slow = Math.max(0, e.slow - dt); e.hitFlash = Math.max(0, e.hitFlash - dt * 4); e.bob += dt * 6;
    e.face = state.hero.x < e.x ? -1 : 1;
    const dx = state.hero.x - e.x, dy = state.hero.y - e.y, d = Math.max(1, Math.hypot(dx, dy));
    if (d > e.radius + 40) { e.x += (dx / d) * e.speed * sm * dt; e.y += (dy / d) * e.speed * sm * dt; }
    else { e.attackTimer -= dt; if (e.attackTimer <= 0) { damageHero(e.dmg); e.attackTimer = e.type === "boss" ? 1.0 : e.type === "elite" ? 1.2 : 1.1; } }
  });
}

function spawnShot(p, t, angOff) {
  state.projectiles.push({
    x: p.x, y: p.y, targetId: t.id, element: p.element, color: p.color,
    speed: p.id === "wolf" ? 760 : 580, radius: p.id === "wolf" ? 8 : 7,
    damage: p.damage * (1 + state.mods.allDamage + (state.mods.dmg[p.id] || 0)),
    pierceLeft: state.mods.pierce, hit: new Set(), drift: angOff || 0,
  });
}
function updatePetAttacks(dt) {
  state.pets.forEach((p) => {
    p.cooldown -= dt;
    const rate = p.fireRate / (1 + (state.mods.rate[p.id] || 0));
    if (p.cooldown > 0) return;
    const t = nearestEnemy(p.x, p.y, p.range);
    if (!t) return;
    spawnShot(p, t, 0);
    for (let k = 0; k < state.mods.split; k++) { const others = state.enemies.filter((e) => e.id !== t.id); const t2 = others[Math.floor(Math.random() * others.length)] || t; spawnShot(p, t2, (k % 2 ? 1 : -1) * (0.25 + k * 0.1)); }
    p.cooldown = rate;
  });
}

function updateProjectiles(dt) {
  state.projectiles = state.projectiles.filter((s) => {
    let t = state.enemies.find((e) => e.id === s.targetId);
    if (!t || s.hit.has(t.id)) { t = nearestEnemy(s.x, s.y, 9999, s.hit); if (!t) return false; s.targetId = t.id; }
    const dx = t.x - s.x, dy = t.y - s.y, d = Math.max(1, Math.hypot(dx, dy)), step = s.speed * dt;
    if (d <= step + t.radius) {
      const mult = counterMult(s.element, t.element);
      const dmg = Math.round(s.damage * mult);
      t.hp -= dmg; t.hitFlash = Math.max(t.hitFlash, 0.7); s.hit.add(t.id);
      addDamageNumber(t.x + (Math.random() - 0.5) * 20, t.y - t.radius * 0.6, dmg, mult > 1);
      state.combo = Math.min(100, state.combo + 1.2 * (1 + state.mods.comboGain));
      addParticles(t.x, t.y, mult > 1 ? ELEM_COLOR[s.element] : s.color, mult > 1 ? 8 : 4);
      if (s.pierceLeft > 0) { s.pierceLeft -= 1; const nx = nearestEnemy(s.x, s.y, 9999, s.hit); if (nx) { s.targetId = nx.id; return true; } }
      return false;
    }
    s.tx = t.x; s.ty = t.y; s.x += (dx / d) * step; s.y += (dy / d) * step;
    return true;
  });
}

function updateParticles(dt) { state.particles = state.particles.filter((p) => { p.life -= dt; p.x += p.vx * dt; p.y += p.vy * dt; return p.life > 0; }); }
function updateDamageNumbers(dt) { state.damageNumbers = state.damageNumbers.filter((d) => { d.life -= dt; d.x += d.vx * dt; d.y += d.vy * dt; d.vy += 70 * dt; return d.life > 0; }); }
function updateShockwaves(dt) { state.shockwaves = state.shockwaves.filter((s) => { s.life -= dt; s.r += (s.max - s.r) * Math.min(1, dt * 7); return s.life > 0; }); }

function damageHero(a) { const b = Math.min(state.shield, a); state.shield -= b; state.hp -= a - b; addParticles(state.hero.x, state.hero.y, b ? "#52dfd0" : "#ef5b58", 8); }
function nearestEnemy(x, y, range, exclude) { let best = null, bd = range; state.enemies.forEach((e) => { if (exclude && exclude.has(e.id)) return; const d = Math.hypot(e.x - x, e.y - y); if (d < bd) { best = e; bd = d; } }); return best; }
function makeDust() { return Array.from({ length: 46 }, () => ({ x: Math.random() * 1280, y: Math.random() * 720, r: 0.6 + Math.random() * 1.8, vx: -8 - Math.random() * 14, vy: -4 + Math.random() * 8, a: 0.04 + Math.random() * 0.1 })); }
function addDamageNumber(x, y, v, crit) { state.damageNumbers.push({ x, y, value: v, crit, life: crit ? 0.95 : 0.7, maxLife: crit ? 0.95 : 0.7, vy: crit ? -90 : -64, vx: (Math.random() - 0.5) * 26 }); }
function addParticles(x, y, color, n) { for (let i = 0; i < n; i++) { const a = Math.random() * 6.28, sp = 30 + Math.random() * 150; state.particles.push({ x, y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, color, life: 0.35 + Math.random() * 0.45, maxLife: 0.8, radius: 2 + Math.random() * 4 }); } }

function battleWin() {
  state.status = "won";
  run.hp = state.hp; // 生命带回地图
  if (state.sub === "boss") { endRunToLobby(true); return; }
  const isElite = state.sub === "elite";
  openShop(isElite ? 4 : 3, isElite);
}
function battleLose() { state.status = "lost"; endRunToLobby(false, "全队宠物倒下，保留死亡前已获得的奖励。"); }

// ============================================================
// 八、购买界面（战斗房奖励，花币）
// ============================================================
function ampPool() { return AMPLIFIERS.filter((a) => a.tier <= meta.poolTier); }
function priceFor(a, elite) { const base = a.tier >= 1 ? 28 : 18; return (elite ? base + 8 : base) + (a.type === "hero" || a.type === "combo" ? 4 : 0); }

function openShop(count, elite) {
  const picks = shuffle(ampPool()).slice(0, count);
  openModal({
    label: elite ? "精英购买 · 高品质池" : "战斗购买",
    title: "用金币购买放大器",
    sub: `当前金币 ${run.coins}。放大器是局内临时强化，出地牢后消失。可只买需要的，或直接跳过。`,
    grid: picks.map((a) => {
      const price = priceFor(a, elite);
      const afford = run.coins >= price;
      return {
        tag: ampTag(a.type), tagText: ampTagText(a.type),
        title: a.name, desc: a.desc, price: `${price} 金币`, disabled: !afford,
        on: (m) => { run.coins -= price; applyAmp(a); closeModal(m); roomCleared(); },
      };
    }),
    actions: [{ text: "跳过购买", ghost: true, on: (m) => { closeModal(m); roomCleared(); } }],
  });
}
function applyAmp(a) { a.apply(run.mods); run.build.push(a.name); }
function ampTag(t) { return { all: "amp-all", pet: "amp-pet", hero: "amp-hero", combo: "amp-combo" }[t]; }
function ampTagText(t) { return { all: "全体放大器", pet: "宠物专属", hero: "主角技能", combo: "合击放大器" }[t]; }

// ============================================================
// 九、自选节点（免费 3 选 1 技能，不花币）
// ============================================================
function startChoiceNode() {
  const picks = shuffle(ampPool()).slice(0, 3);
  openModal({
    label: "🎁 自选节点", title: "免费 3 选 1 强化", sub: "自选节点不消耗货币，从可用放大器中挑一个。",
    grid: picks.map((a) => ({
      tag: ampTag(a.type), tagText: ampTagText(a.type), title: a.name, desc: a.desc, price: "免费",
      on: (m) => { applyAmp(a); closeModal(m); roomCleared(); },
    })),
  });
}

// ============================================================
// 十、随机事件房（按权重抽事件类型）
// ============================================================
function enterEvent() {
  // 权重：遇宠最高
  const roll = Math.random();
  if (roll < 0.55) startEncounter();
  else if (roll < 0.8) openRiskEvent();
  else openGainEvent();
}

function openGainEvent() {
  const gains = [
    { t: "回复", run: () => { run.hp = Math.min(run.maxHp, run.hp + 30); }, desc: "泉水回复队伍 30 点生命。" },
    { t: "材料", run: () => { meta.materials += 3; }, desc: "拾获 3 个养成材料。" },
    { t: "金币", run: () => { run.coins += 24; }, desc: "发现宝箱，金币 +24。" },
    { t: "补给", run: () => { run.balls.great += 1; }, desc: "获得 1 个高级捕捉球。" },
  ];
  const g = gains[Math.floor(Math.random() * gains.length)];
  openModal({
    label: "❓ 随机事件 · 即时增益", title: "低风险补给", sub: g.desc,
    actions: [{ text: "收下并前进", on: (m) => { g.run(); closeModal(m); roomCleared(); } }],
  });
}

function openRiskEvent() {
  openModal({
    label: "❓ 随机事件 · 风险抉择", title: "古老祭坛", sub: "祭坛索取代价，给予回报。选择其一，或不献祭离开。",
    grid: [
      { tag: "amp-hero", tagText: "献祭生命", title: "以血换力", desc: "失去 18 点队伍生命，全体输出本局 +15%。",
        on: (m) => { run.hp = Math.max(1, run.hp - 18); run.mods.allDamage += 0.15; run.build.push("祭坛·以血换力"); closeModal(m); roomCleared(); } },
      { tag: "amp-combo", tagText: "赌博", title: "命运硬币", desc: "50% 金币 +40，50% 金币 -20。",
        on: (m) => { run.coins += Math.random() < 0.5 ? 40 : -20; if (run.coins < 0) run.coins = 0; closeModal(m); roomCleared(); } },
    ],
    actions: [{ text: "不献祭，离开", ghost: true, on: (m) => { closeModal(m); roomCleared(); } }],
  });
}

// ============================================================
// 十一、捉宠场景（回合制：攻击/投球/道具/放弃）
// ============================================================
function rarityName(r) { return { common: "普通", rare: "稀有", epic: "史诗" }[r]; }
function makePetFromWild(w) {
  const dmg = w.rarity === "epic" ? 18 : w.rarity === "rare" ? 14 : 11;
  const look = w.element === "water" ? "slime" : w.element === "fire" ? "wolf" : "fox";
  return { id: look, name: w.name, role: ELEMENTS[w.element] + " · 捕获", element: w.element, color: w.color, damage: dmg, fireRate: 0.85, range: 500 };
}
function startEncounter() {
  const wild = WILD_PETS[Math.floor(Math.random() * WILD_PETS.length)];
  meta.seen.add(wild.id);
  cap = {
    wild, maxHp: 100, hp: 100, st: "none", stTurns: 0,
    fleeBase: wild.rarity === "epic" ? 0.34 : wild.rarity === "rare" ? 0.26 : 0.18,
    log: "出现一只野生宠物。满血时逃跑率高——先削血再投球。",
    over: false, t: 0,
  };
  $("capName").textContent = wild.name;
  $("capRarity").textContent = rarityName(wild.rarity);
  $("capRarity").className = `rarity ${wild.rarity}`;
  $("ballCount").textContent = run.balls.basic + run.balls.great;
  $("captureBack").classList.add("hidden");
  $("itemTray").classList.add("hidden");
  renderCapture();
  showScreen("captureScreen");
}

function hpCoef() { return (3 * cap.maxHp - 2 * cap.hp) / (3 * cap.maxHp); }
function captureRate(ballMult) { return Math.min(0.97, cap.wild.base * hpCoef() * ballMult * STATE_MULT[cap.st]); }
function fleeChance() { const hpMod = cap.hp / cap.maxHp > 0.5 ? 1.5 : cap.hp / cap.maxHp < 0.3 ? 0.3 : 1; return cap.fleeBase * hpMod * STATE_FLEE[cap.st]; }

function renderCapture() {
  $("capHpBar").style.width = `${(cap.hp / cap.maxHp) * 100}%`;
  $("capHpText").textContent = `${Math.max(0, Math.ceil(cap.hp))}/${cap.maxHp}`;
  $("capLog").textContent = cap.log;
  const rate = Math.round(captureRate(1) * 100);
  const flee = fleeChance();
  $("capRateLine").innerHTML = `基础球成功率：<b>${rate}%</b>　逃跑概率：${flee > 0.28 ? "高" : flee > 0.12 ? "中" : flee > 0 ? "低" : "无（已控制）"}`;
  $("capState").classList.toggle("hidden", cap.st === "none");
  $("capState").textContent = cap.st === "para" ? "麻痹" : cap.st === "sleep" ? "睡眠" : "";
  const ballN = run.balls.basic + run.balls.great;
  $("ballCount").textContent = ballN;
  document.querySelector('#capActions button[data-act="ball"]').disabled = ballN <= 0 || cap.over;
  document.querySelectorAll("#capActions button").forEach((b) => { if (b.dataset.act !== "ball") b.disabled = cap.over; });
}

function capPetAttack() {
  // 玩家用出战队伍削血（取最高伤害宠物一次普攻量级）
  const dmg = 18 + Math.floor(Math.random() * 10);
  cap.hp -= dmg;
  cap.log = `队伍出手，削减 ${dmg} 点生命。`;
  if (cap.hp <= 0) { cap.hp = 0; cap.log = `${cap.wild.name} 被打倒了——捉宠失败。`; return capFail(); }
  capEnemyPhase();
}

function capThrow() {
  const ballType = run.balls.great > 0 ? "great" : "basic";
  if (ballType === "great") run.balls.great -= 1; else run.balls.basic -= 1;
  const ball = BALLS.find((b) => b.id === ballType);
  // 属性匹配的高级球额外加成（简单处理：高级球对稀有以上 +0）
  const rate = captureRate(ball.mult);
  if (Math.random() < rate) {
    cap.over = true;
    const repeat = meta.caught.has(cap.wild.id);
    meta.caught.add(cap.wild.id);
    run.runCaught += 1;
    const full = run.team.length >= 4;
    if (repeat || full) { meta.materials += 4; cap.log = `${repeat ? cap.wild.name + " 已在图鉴中" : "队伍已满"}——转化为 4 个养成材料！`; }
    else {
      // 新宠物加入本局队伍：越打越多 → 成长感
      run.team.push(makePetFromWild(cap.wild));
      cap.log = `捕捉成功！${cap.wild.name}（${rarityName(cap.wild.rarity)}）加入本局队伍，战力提升！`;
    }
    renderCapture();
    $("captureBack").classList.remove("hidden");
    return;
  }
  cap.log = `${ball.name}（成功率 ${Math.round(rate * 100)}%）被挣脱了。`;
  capEnemyPhase();
}

function capUseItem(id) {
  if (run.items[id] <= 0) { cap.log = "该道具已用尽。"; renderCapture(); return; }
  run.items[id] -= 1;
  const it = ITEMS.find((i) => i.id === id);
  cap.st = it.state; cap.stTurns = it.runs;
  cap.log = it.state === "para" ? "施加麻痹：逃跑率骤降，成功率 ×1.5。" : "施加催眠：不再逃跑，成功率 ×2.5。";
  $("itemTray").classList.add("hidden");
  capEnemyPhase();
}

function capEnemyPhase() {
  if (cap.over) return;
  // 反击
  state && 0; // 捉宠与主战斗隔离，这里用队伍生命承受反击
  const counter = 6 + Math.floor(Math.random() * 6);
  run.hp = Math.max(1, run.hp - counter);
  // 状态衰减
  if (cap.st !== "none") { cap.stTurns -= 1; if (cap.stTurns <= 0) cap.st = "none"; }
  // 逃跑判定
  const flee = fleeChance();
  if (Math.random() < flee) { cap.log = `${cap.wild.name} 趁机逃跑了。`; renderCapture(); return capFail(); }
  cap.log += `（宠物反击 -${counter} 队伍生命）`;
  renderCapture();
}

function capFail() {
  cap.over = true;
  renderCapture();
  $("captureBack").classList.remove("hidden");
}

$("capActions").addEventListener("click", (e) => {
  const btn = e.target.closest("button"); if (!btn || btn.disabled) return;
  const act = btn.dataset.act;
  if (act === "attack") capPetAttack();
  else if (act === "ball") capThrow();
  else if (act === "item") toggleItemTray();
  else if (act === "flee") { cap.log = "你放走了它。"; capFail(); }
});
function toggleItemTray() {
  const tray = $("itemTray");
  tray.innerHTML = ITEMS.map((i) => `<button data-item="${i.id}" ${run.items[i.id] <= 0 ? "disabled" : ""}>${i.name}（${run.items[i.id]}）</button>`).join("");
  tray.classList.toggle("hidden");
  tray.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => capUseItem(b.dataset.item)));
}
$("captureBack").addEventListener("click", () => { cap = null; roomCleared(); });

function drawCapture() {
  const c = capCtx, W = capCanvas.width, H = capCanvas.height;
  c.clearRect(0, 0, W, H);
  // 地面光圈
  const g = c.createRadialGradient(W / 2, H * 0.62, 20, W / 2, H * 0.62, 220);
  g.addColorStop(0, "rgba(120,235,220,0.12)"); g.addColorStop(1, "rgba(120,235,220,0)");
  c.fillStyle = g; c.fillRect(0, 0, W, H);
  if (!cap) return;
  const bob = Math.sin(cap.t * 3) * 6;
  const cx = W / 2, cy = H * 0.55 + bob, r = 64, col = cap.wild.color;
  c.fillStyle = "rgba(0,0,0,0.3)"; c.beginPath(); c.ellipse(cx, H * 0.74, r * 1.1, r * 0.3, 0, 0, 6.28); c.fill();
  const body = c.createRadialGradient(cx - r * 0.3, cy - r * 0.4, 4, cx, cy, r * 1.3);
  body.addColorStop(0, "#fff"); body.addColorStop(0.4, col); body.addColorStop(1, "#10141c");
  c.fillStyle = body; c.beginPath(); c.ellipse(cx, cy, r * 0.92, r, 0, 0, 6.28); c.fill();
  // 耳
  c.fillStyle = col;
  c.beginPath(); c.moveTo(cx - r * 0.5, cy - r * 0.7); c.lineTo(cx - r * 0.75, cy - r * 1.25); c.lineTo(cx - r * 0.2, cy - r * 0.85); c.fill();
  c.beginPath(); c.moveTo(cx + r * 0.5, cy - r * 0.7); c.lineTo(cx + r * 0.75, cy - r * 1.25); c.lineTo(cx + r * 0.2, cy - r * 0.85); c.fill();
  // 眼
  c.fillStyle = "#fff"; c.beginPath(); c.arc(cx - r * 0.3, cy - r * 0.1, 8, 0, 6.28); c.arc(cx + r * 0.3, cy - r * 0.1, 8, 0, 6.28); c.fill();
  c.fillStyle = "#0c0f16"; c.beginPath(); c.arc(cx - r * 0.28, cy - r * 0.08, 4, 0, 6.28); c.arc(cx + r * 0.32, cy - r * 0.08, 4, 0, 6.28); c.fill();
  // 属性光
  c.fillStyle = ELEM_COLOR[cap.wild.element]; c.globalAlpha = 0.5 + Math.sin(cap.t * 5) * 0.2;
  c.beginPath(); c.arc(cx + r * 0.7, cy - r * 0.7, 6, 0, 6.28); c.fill(); c.globalAlpha = 1;
}

// ============================================================
// 十二、结算
// ============================================================
function endRunToLobby(victory, msg) {
  if (victory) meta.clears += 1;
  const m = openModal({
    label: victory ? "通关结算" : "本局结束",
    title: victory ? "地牢通关！" : "返回大厅",
    sub: msg || "",
    custom: `<div class="big-emoji">${victory ? "🏆" : "🚪"}</div>
      <div class="result-stats">
        <div><b>${run.coins}</b><small>金币</small></div>
        <div><b>${run.runCaught}</b><small>本局捕捉</small></div>
        <div><b>${run.build.length}</b><small>放大器</small></div>
      </div>
      <p>${victory ? "第 " + run.floor + " 层已清，下次可挑战更深地牢。" : "已获得的图鉴与材料已保留。"}</p>`,
    center: true,
    actions: [{ text: "返回大厅", on: (mm) => { closeModal(mm); run = null; state = null; renderLobby(); } }],
  });
  return m;
}

// ============================================================
// 十三、通用弹窗
// ============================================================
function openModal(opt) {
  const root = $("modalRoot");
  const el = document.createElement("div");
  el.className = "modal";
  let inner = `<div class="modal-panel ${opt.center ? "result-panel" : ""}">`;
  if (opt.label) inner += `<p class="modal-label">${opt.label}</p>`;
  if (opt.title) inner += `<h2>${opt.title}</h2>`;
  if (opt.sub) inner += `<p class="modal-sub">${opt.sub}</p>`;
  if (opt.custom) inner += opt.custom;
  if (opt.grid) {
    inner += `<div class="choice-grid">` + opt.grid.map((g, i) => `
      <button class="choice-card" data-i="${i}" ${g.disabled ? "disabled" : ""}>
        ${g.tag ? `<span class="tag ${g.tag}">${g.tagText}</span>` : ""}
        <strong>${g.title}</strong><p>${g.desc}</p>
        ${g.price ? `<span class="price">${g.price}</span>` : ""}
      </button>`).join("") + `</div>`;
  }
  if (opt.actions) inner += `<div class="modal-foot">` + opt.actions.map((a, i) => `<button class="${a.ghost ? "ghost-action" : "primary-action"}" data-a="${i}">${a.text}</button>`).join("") + `</div>`;
  inner += `</div>`;
  el.innerHTML = inner;
  root.appendChild(el);
  if (opt.grid) el.querySelectorAll(".choice-card").forEach((b) => { if (!b.disabled) b.addEventListener("click", () => opt.grid[+b.dataset.i].on(el)); });
  if (opt.actions) el.querySelectorAll(".modal-foot button").forEach((b) => b.addEventListener("click", () => opt.actions[+b.dataset.a].on(el)));
  return el;
}
function closeModal(el) { el.remove(); }

// ============================================================
// 十四、战斗渲染（透视地牢 + 精灵 + 反馈）
// ============================================================
function drawBattle() {
  ctx.imageSmoothingEnabled = false;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.save();
  if (state.shake > 0.2) { const a = state.shake; ctx.translate(Math.round((Math.random() - 0.5) * a), Math.round((Math.random() - 0.5) * a)); }
  drawFloor(); drawRoomChrome(); drawFields(); drawShockwaves(); drawProjectiles(); drawActors(); drawParticles(); drawDamageNumbers(); drawVignette();
  ctx.restore();
  drawStreak(); drawMinimap();
}

// 房间内的门 + 交互节点（像素）
function drawRoomChrome() {
  // 交互节点（事件 ? / 自选礼盒）
  const it = state.interactable;
  if (it && !state.cleared) {
    const pulse = 0.6 + Math.sin(state.time * 4) * 0.4;
    ctx.fillStyle = `rgba(120,235,220,${0.18 * pulse})`; ctx.fillRect(it.x - 50, it.y - 24, 100, 48);
    if (it.kind === "choice") { ctx.fillStyle = "#caa24a"; ctx.fillRect(it.x - 18, it.y - 14, 36, 28); ctx.fillStyle = "#8a6a2e"; ctx.fillRect(it.x - 18, it.y - 2, 36, PX); ctx.fillStyle = "#ffd34d"; ctx.fillRect(it.x - PX, it.y - 22, PX * 2, PX * 2); }
    else { ctx.fillStyle = "#ffd24d"; ctx.font = "900 40px system-ui"; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText("?", it.x, it.y); }
    ctx.textAlign = "left"; ctx.textBaseline = "alphabetic";
  }
  // 门（开=发光通道，闭=横栏）
  state.doors.forEach((door) => {
    const x = door.x - door.w / 2;
    ctx.fillStyle = "#0a0710"; ctx.fillRect(x, 16, door.w, DOOR_Y - 16);
    if (door.open) {
      const g = 0.6 + Math.sin(state.time * 5) * 0.4;
      ctx.fillStyle = `rgba(120,235,220,${0.5 * g})`; ctx.fillRect(x + PX, 24, door.w - PX * 2, DOOR_Y - 24);
      ctx.fillStyle = "#9af0e6"; ctx.fillRect(x, 16, PX, DOOR_Y - 16); ctx.fillRect(x + door.w - PX, 16, PX, DOOR_Y - 16);
    } else {
      ctx.fillStyle = "#3a2d22"; for (let i = 0; i < 4; i++) ctx.fillRect(x + 6, 30 + i * 22, door.w - 12, PX * 2);
    }
    // 门牌（分叉预览 / 类型）
    if (door.types) { ctx.fillStyle = "#ffe0a0"; ctx.font = "700 18px system-ui"; ctx.textAlign = "center"; ctx.fillText(door.label + " " + door.types.map((t) => ROOM_META[t].icon).join(""), door.x, DOOR_Y + 22); ctx.textAlign = "left"; }
  });
}

// 右上角小地图：房间序列 + 分叉 + 当前位置
function drawMinimap() {
  if (!run) return;
  const X = 18, Y = 84, W = 230, cell = 18, gap = 4;
  ctx.fillStyle = "rgba(8,10,16,0.82)"; ctx.fillRect(X, Y, W, 84);
  ctx.strokeStyle = "rgba(225,206,153,0.3)"; ctx.lineWidth = 1; ctx.strokeRect(X + 0.5, Y + 0.5, W, 84);
  const f = run.fork;
  let col = 0; const baseY = Y + 42;
  const node = (type, cx, cy, status) => {
    ctx.fillStyle = status === "cur" ? "#52dfd0" : status === "done" ? "#3a4a44" : "#2a2f3a";
    ctx.fillRect(cx, cy - cell / 2, cell, cell);
    ctx.fillStyle = "#0a0a0a"; ctx.font = "12px system-ui"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText(ROOM_META[type].icon, cx + cell / 2, cy + 1);
    if (status === "cur") { ctx.strokeStyle = "#9af0e6"; ctx.lineWidth = 2; ctx.strokeRect(cx - 1, cy - cell / 2 - 1, cell + 2, cell + 2); }
  };
  for (let i = 0; i < run.path.length; i++) {
    const cx = X + 12 + col * (cell + gap);
    const st = i < run.pos ? "done" : i === run.pos ? "cur" : "next";
    if (i === f.at && f.chosen === null) {
      // 分叉两行
      node(f.branchA[0], cx, baseY - 12, "next"); node(f.branchA[1], cx + cell + gap, baseY - 12, "next");
      node(f.branchB[0], cx, baseY + 12, "next"); node(f.branchB[1], cx + cell + gap, baseY + 12, "next");
      col += f.len; i += f.len - 1; continue;
    }
    node(run.path[i], cx, baseY, st); col += 1;
  }
  ctx.textAlign = "left"; ctx.textBaseline = "alphabetic";
  ctx.fillStyle = "#b7ad9b"; ctx.font = "11px system-ui"; ctx.fillText(`第${run.floor}层 · 第 ${run.pos + 1}/${run.path.length} 间`, X + 8, Y + 78);
}

// ===== 像素美术系统 =====
const PX = 5; // 像素块边长
function hash2(x, y) { let n = (x | 0) * 374761393 + (y | 0) * 668265263; n = (n ^ (n >> 13)) * 1274126177; return ((n ^ (n >> 16)) >>> 0) / 4294967296; }
// 精灵 = 字符行数组；blit 把每个非'.'像素画成 PX×PX 方块
function blit(sprite, pal, cx, cy, scale, flip) {
  const s = scale || PX, w = sprite[0].length, h = sprite.length;
  const ox = Math.round(cx - (w * s) / 2), oy = Math.round(cy - h * s);
  for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) {
    const ch = sprite[r][flip ? w - 1 - c : c];
    if (ch === ".") continue;
    const col = pal[ch]; if (!col) continue;
    ctx.fillStyle = col; ctx.fillRect(ox + c * s, oy + r * s, s, s);
  }
}
// 角色：深发冒险者
const SP_HERO = [
  "...HHHHH...", "..HHHHHHH..", ".HHFFFFFHH.", ".HFFFFFFFH.", ".HFeFFFeFH.",
  ".HFFFFFFFH.", ".HHFFFFFHH.", "..AAAAAAA..", ".AAAAAAAAA.", ".AAAaaaAAA.",
  "..AAAAAAA..", "..LLL.LLL..", "..LLL.LLL..", "..bb...bb..",
];
const HERO_PAL = { H: "#2a2036", F: "#f1c79f", e: "#23202a", A: "#d7ad4e", a: "#9a7330", L: "#33203a", b: "#171019" };
// 通用小怪/宠物：圆身双耳双眼，B=主色 D=暗部
const SP_CRIT = [
  "..O....O..", ".OBO..OBO.", ".OBBBBBBO.", "OBBBBBBBBO", "OBwBBBBwBO",
  "OBkBBBBkBO", "ODBBBBBBDO", ".ODBBBBDO.", "..OOOOOO..",
];
function critPal(color) { return { O: "#150d14", B: color, D: shade(color, -45), w: "#ffffff", k: "#150d14" }; }

function drawFloor() {
  // 地块：暗棕石砖 + 草簇 + 碎石（仿元气骑士地牢）
  const T = 40;
  for (let ty = 0; ty * T < canvas.height; ty++) for (let tx = 0; tx * T < canvas.width; tx++) {
    const h = hash2(tx, ty);
    const base = h < 0.5 ? "#3a2b1e" : h < 0.8 ? "#42301f" : "#352619";
    ctx.fillStyle = base; ctx.fillRect(tx * T, ty * T, T, T);
    ctx.fillStyle = "rgba(0,0,0,0.25)"; ctx.fillRect(tx * T, ty * T + T - PX, T, PX); ctx.fillRect(tx * T + T - PX, ty * T, PX, T);
    ctx.fillStyle = "rgba(255,255,255,0.03)"; ctx.fillRect(tx * T, ty * T, T, PX);
    // 草簇
    if (h > 0.55) { const gx = tx * T + Math.floor(hash2(tx + 7, ty) * 6) * PX, gy = ty * T + Math.floor(hash2(tx, ty + 5) * 5 + 2) * PX; ctx.fillStyle = "#4a7a33"; ctx.fillRect(gx, gy, PX, PX); ctx.fillRect(gx + PX, gy - PX, PX, PX); ctx.fillRect(gx - PX, gy, PX, PX); }
    // 碎石
    if (h > 0.3 && h < 0.42) { const px = tx * T + Math.floor(hash2(tx + 3, ty + 9) * 6 + 1) * PX, py = ty * T + Math.floor(hash2(tx + 1, ty) * 6 + 1) * PX; ctx.fillStyle = "#5a4631"; ctx.fillRect(px, py, PX, PX); ctx.fillStyle = "#2c2114"; ctx.fillRect(px + PX, py, PX, PX); }
  }
  // 顶部墙体暗带
  ctx.fillStyle = "#1a1320"; ctx.fillRect(0, 0, canvas.width, 70);
  for (let x = 0; x < canvas.width; x += 80) { ctx.fillStyle = "#241b2c"; ctx.fillRect(x, 18, 70, 34); ctx.fillStyle = "#120c18"; ctx.fillRect(x, 50, 80, PX); }
  ctx.fillStyle = "rgba(0,0,0,0.5)"; ctx.fillRect(0, 70, canvas.width, PX * 2);
}

function shadowPx(cx, cy, w) { ctx.fillStyle = "rgba(0,0,0,0.32)"; ctx.fillRect(Math.round(cx - w / 2), Math.round(cy - PX), w, PX * 2); }

function drawFields() {
  (state.fields || []).forEach((f) => {
    const a = Math.min(1, f.life / 1.2) * 0.5;
    const g = ctx.createRadialGradient(f.x, f.y, 4, f.x, f.y, f.r);
    g.addColorStop(0, `rgba(255,150,50,${a})`); g.addColorStop(0.7, `rgba(255,90,30,${a * 0.5})`); g.addColorStop(1, "rgba(255,90,30,0)");
    ctx.save(); ctx.translate(f.x, f.y); ctx.scale(1, 0.5); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, f.r, 0, 6.28); ctx.fill(); ctx.restore();
    for (let i = 0; i < 2; i++) { const an = Math.random() * 6.28, rr2 = Math.random() * f.r; ctx.fillStyle = `rgba(255,${150 + Math.random() * 80 | 0},60,0.5)`; ctx.beginPath(); ctx.arc(f.x + Math.cos(an) * rr2, f.y + Math.sin(an) * rr2 * 0.5, 2, 0, 6.28); ctx.fill(); }
  });
}

// 连杀 / 战力 HUD（屏幕坐标，不受震动）
function drawStreak() {
  if (state.killStreak >= 4) {
    ctx.save(); ctx.textAlign = "center"; ctx.textBaseline = "middle";
    const s = Math.min(1, state.streakTimer / 2);
    ctx.globalAlpha = 0.55 + s * 0.45;
    ctx.font = "900 40px system-ui, sans-serif"; ctx.fillStyle = "#ffd24d"; ctx.strokeStyle = "rgba(0,0,0,0.8)"; ctx.lineWidth = 5;
    const txt = `连杀 ${state.killStreak}`;
    ctx.strokeText(txt, canvas.width / 2, 92); ctx.fillText(txt, canvas.width / 2, 92);
    ctx.restore(); ctx.globalAlpha = 1;
  }
}

function drawShockwaves() { state.shockwaves.forEach((s) => { const al = Math.max(0, s.life / 0.45); ctx.save(); ctx.translate(s.x, s.y); ctx.scale(1, 0.55); ctx.strokeStyle = s.color; ctx.globalAlpha = al * 0.7; ctx.lineWidth = 6 * al + 1; ctx.beginPath(); ctx.arc(0, 0, s.r, 0, 6.28); ctx.stroke(); ctx.restore(); }); ctx.globalAlpha = 1; }
function drawVignette() { const g = ctx.createRadialGradient(640, 400, 280, 640, 360, 760); g.addColorStop(0, "rgba(0,0,0,0)"); g.addColorStop(1, "rgba(0,0,0,0.55)"); ctx.fillStyle = g; ctx.fillRect(0, 0, canvas.width, canvas.height); }

function drawActors() {
  const a = [{ y: state.hero.y, d: () => drawHero(state.hero.x, state.hero.y) },
    ...state.pets.map((p) => ({ y: p.y, d: () => drawPet(p) })),
    ...state.enemies.map((e) => ({ y: e.y, d: () => drawEnemy(e) }))];
  a.sort((x, y) => x.y - y.y); a.forEach((o) => o.d());
}
function drawHero(x, y) {
  const mv = state.hero.moving; const bob = mv ? Math.round(Math.sin(state.time * 11)) * PX : 0;
  shadowPx(x, y, 12 * PX / 5 * 4);
  blit(SP_HERO, HERO_PAL, x, y + bob, PX, state.hero.face < 0);
}
function drawPet(p) {
  const bob = Math.round(Math.sin(state.time * 6 + p.x)) * PX;
  shadowPx(p.x, p.y, 9 * PX);
  blit(SP_CRIT, critPal(p.color), p.x, p.y + bob, PX);
  // 火宠尾焰 / 法师帽点缀
  if (p.id === "slime") { ctx.fillStyle = "#3a5fb0"; ctx.fillRect(Math.round(p.x - PX * 1.5), Math.round(p.y - 9 * PX - bob - PX * 2), PX * 3, PX * 2); ctx.fillStyle = "#ffd34d"; ctx.fillRect(Math.round(p.x - PX / 2), Math.round(p.y - 9 * PX - bob - PX * 3), PX, PX); }
}
function drawEnemy(e) {
  const big = e.type === "boss" ? 3.2 : e.type === "elite" ? 1.9 : 1;
  const sc = Math.round(PX * big * (e.type === "minion" ? (e.radius / 18) : 1)) || PX;
  const bob = Math.round(Math.sin(e.bob)) * (e.type === "minion" ? 0 : PX);
  shadowPx(e.x, e.y, 9 * sc);
  const col = e.type === "boss" ? "#7a4ea8" : ELEM_COLOR[e.element];
  blit(SP_CRIT, critPal(col), e.x, e.y + bob, sc, e.face < 0);
  // 角（精英/Boss）
  if (e.type !== "minion") {
    const topY = Math.round(e.y + bob - 9 * sc);
    ctx.fillStyle = e.type === "boss" ? "#1c1228" : "#d9c9a3";
    ctx.fillRect(Math.round(e.x - 3.2 * sc), topY - sc, sc, sc * 2);
    ctx.fillRect(Math.round(e.x + 2.2 * sc), topY - sc, sc, sc * 2);
    if (e.type === "boss") { const g = 0.5 + Math.sin(state.time * 5) * 0.5; ctx.fillStyle = `rgba(255,120,200,${g})`; ctx.fillRect(Math.round(e.x - 2.6 * sc), Math.round(e.y + bob - 5.5 * sc), sc, sc); ctx.fillRect(Math.round(e.x + 1.6 * sc), Math.round(e.y + bob - 5.5 * sc), sc, sc); }
  }
  if (e.hitFlash > 0.02 && Math.random() < e.hitFlash) blit(SP_CRIT, { O: "#fff", B: "#fff", D: "#fff", w: "#fff", k: "#fff" }, e.x, e.y + bob, sc, e.face < 0);
  // 血条 + 属性点（像素）
  const w = Math.max(28, 9 * sc), bx = Math.round(e.x - w / 2), by = Math.round(e.y + bob - 9 * sc - PX * 2.4);
  ctx.fillStyle = "#0c0a10"; ctx.fillRect(bx - 1, by - 1, w + 2, PX + 2);
  ctx.fillStyle = e.type === "boss" ? "#c07bff" : e.type === "elite" ? "#f0b454" : "#74dd62"; ctx.fillRect(bx, by, Math.round(w * Math.max(0, e.hp / e.maxHp)), PX);
  ctx.fillStyle = ELEM_COLOR[e.element]; ctx.fillRect(bx - PX - 2, by, PX, PX);
}
function drawProjectiles() {
  state.projectiles.forEach((s) => {
    const tx = s.tx ?? s.x, ty = s.ty ?? s.y; const dx = tx - s.x, dy = ty - s.y, len = Math.max(1, Math.hypot(dx, dy));
    const bx = -(dx / len) * PX * 2, by = -(dy / len) * PX * 2;
    ctx.fillStyle = s.color; ctx.fillRect(Math.round(s.x + bx - PX / 2), Math.round(s.y + by - PX / 2), PX, PX);
    ctx.fillRect(Math.round(s.x - PX), Math.round(s.y - PX), PX * 2, PX * 2);
    ctx.fillStyle = "#fff"; ctx.fillRect(Math.round(s.x - PX / 2), Math.round(s.y - PX / 2), PX, PX);
  });
}
function drawParticles() { state.particles.forEach((p) => { const t = Math.max(0, p.life / p.maxLife); if (t <= 0) return; ctx.globalAlpha = t; ctx.fillStyle = p.color; const s = Math.max(PX, Math.round(p.radius)); ctx.fillRect(Math.round(p.x - s / 2), Math.round(p.y - s / 2), s, s); }); ctx.globalAlpha = 1; }
function drawDamageNumbers() {
  ctx.save(); ctx.textAlign = "center"; ctx.textBaseline = "middle";
  state.damageNumbers.forEach((d) => { const t = d.life / d.maxLife; ctx.globalAlpha = Math.min(1, t * 1.6); const sz = d.crit ? 30 : 20; ctx.font = `900 ${sz}px system-ui, sans-serif`; ctx.lineWidth = 4; ctx.strokeStyle = "rgba(0,0,0,0.85)"; ctx.fillStyle = d.crit ? "#ffd24d" : "#fff0e0"; ctx.strokeText(d.value, d.x, d.y); ctx.fillText(d.value, d.x, d.y); if (d.crit) { ctx.font = "700 11px system-ui"; ctx.fillStyle = "#ff9a3c"; ctx.fillText("克制", d.x + sz * 0.9, d.y - sz * 0.4); } });
  ctx.restore(); ctx.globalAlpha = 1;
}
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
function shade(hex, amt) { const v = parseInt(hex.slice(1), 16); const r = Math.max(0, Math.min(255, (v >> 16) + amt)), g = Math.max(0, Math.min(255, ((v >> 8) & 255) + amt)), b = Math.max(0, Math.min(255, (v & 255) + amt)); return `rgb(${r},${g},${b})`; }

// ============================================================
// 十五、主循环
// ============================================================
function loop(now) {
  const dt = Math.min(0.05, (now - last) / 1000); last = now;
  if (state) {
    const fighting = COMBAT_KIND[state.kind] && !state.cleared && state.status === "battle";
    if (fighting) {
      if (auto) { const hs = state.skills[0]; if (hs && hs.cooldown <= 0) useSkill(hs.id); if (state.combo >= 100) useSkill("combo"); }
      updateBattle(dt);
    } else {
      // 探索 / 清场后：走位 + 跟随 + 特效衰减
      state.time += dt;
      moveHero(dt); movePets(dt);
      updateParticles(dt); updateDamageNumbers(dt); updateShockwaves(dt); updateFields(dt);
    }
    updateRoomNav(dt);
    state.shake = Math.max(0, state.shake - dt * 40);
    if (!$("roomScreen").classList.contains("hidden")) { updateBattleUi(); drawBattle(); }
  }
  if (cap) { cap.t += dt; if (!$("captureScreen").classList.contains("hidden")) drawCapture(); }
  requestAnimationFrame(loop);
}

// ============================================================
// 十六、输入：键盘 + 摇杆
// ============================================================
const KEY_MAP = { ArrowUp: "up", KeyW: "up", ArrowDown: "down", KeyS: "down", ArrowLeft: "left", KeyA: "left", ArrowRight: "right", KeyD: "right" };
window.addEventListener("keydown", (e) => { const d = KEY_MAP[e.code]; if (!d) return; input.keys.add(d); e.preventDefault(); });
window.addEventListener("keyup", (e) => { const d = KEY_MAP[e.code]; if (d) input.keys.delete(d); });

const joystick = $("joystick"), knob = $("joystickKnob"), JOY_R = 34;
let joyOn = false, joyId = null;
function joyStart(e) { joyOn = true; joyId = e.pointerId; joystick.classList.add("active"); joystick.setPointerCapture?.(e.pointerId); joyMove(e); }
function joyMove(e) {
  if (!joyOn || (joyId !== null && e.pointerId !== joyId)) return;
  const rc = joystick.getBoundingClientRect();
  const dx = e.clientX - (rc.left + rc.width / 2), dy = e.clientY - (rc.top + rc.height / 2);
  const dist = Math.min(Math.hypot(dx, dy), JOY_R), ang = Math.atan2(dy, dx);
  const kx = Math.cos(ang) * dist, ky = Math.sin(ang) * dist;
  knob.style.transform = `translate(${kx}px, ${ky}px)`;
  input.joyX = kx / JOY_R; input.joyY = ky / JOY_R;
}
function joyEnd(e) { if (joyId !== null && e && e.pointerId !== joyId) return; joyOn = false; joyId = null; joystick.classList.remove("active"); knob.style.transform = "translate(0,0)"; input.joyX = 0; input.joyY = 0; }
joystick.addEventListener("pointerdown", joyStart);
window.addEventListener("pointermove", joyMove);
window.addEventListener("pointerup", joyEnd);
window.addEventListener("pointercancel", joyEnd);

// ============================================================
// 启动
// ============================================================
renderLobby();
requestAnimationFrame(loop);
