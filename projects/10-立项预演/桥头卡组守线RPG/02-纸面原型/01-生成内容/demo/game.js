const canvas = document.getElementById("battleCanvas");
const ctx = canvas.getContext("2d");

const LANES = [330, 430, 530, 630];
const GATE_Y = 498;

const SKILLS = {
  blast: {
    name: "爆燃弹",
    school: "爆燃",
    role: "范围清群",
    color: "#c75b32",
    cooldown: 3.2,
    cost: 16,
    pickTarget: () => densestPoint() || closestEnemy() || { x: 480, y: 250 },
    fire(game, target) {
      areaDamage(target.x, target.y, game.mods.blastRadius, game.mods.blastDamage, "blast");
      game.zones.push({ type: "burn", x: target.x, y: target.y, r: game.mods.blastRadius * 0.88, ttl: game.mods.burnDuration, tick: 0 });
      addFloat(target.x, target.y, "爆燃", this.color);
      game.shake = 8;
    },
  },
  frost: {
    name: "霜裂弹",
    school: "霜裂",
    role: "控场增伤",
    color: "#3c91a3",
    cooldown: 5.4,
    cost: 13,
    pickTarget: () => closestEnemy() || { x: 480, y: 270 },
    fire(game, target) {
      game.enemies.forEach((enemy) => {
        if (distance(enemy, target) <= game.mods.frostRadius) {
          enemy.slow = Math.max(enemy.slow, game.mods.frostSlow);
          enemy.vulnerable = Math.max(enemy.vulnerable, game.mods.vulnerableTime);
          if (Math.random() < game.mods.freezeChance) enemy.frozen = Math.max(enemy.frozen, 1.15);
        }
      });
      areaDamage(target.x, target.y, game.mods.frostRadius, 2, "frost");
      addFloat(target.x, target.y, "霜裂", this.color);
    },
  },
  beam: {
    name: "聚能射线",
    school: "射线",
    role: "Boss单线",
    color: "#7c5bd6",
    cooldown: 7.2,
    cost: 22,
    pickTarget: () => ({ x: laneOfPriority(), y: 300 }),
    fire(game, target) {
      game.beams.push({ x: target.x, ttl: game.mods.beamDuration, tick: 0, width: game.mods.beamWidth, damage: game.mods.beamDamage });
      addFloat(target.x, 310, "射线", this.color);
    },
  },
  electron: {
    name: "跃迁电子",
    school: "电子",
    role: "弹射触发",
    color: "#2d8f6f",
    cooldown: 4.1,
    cost: 12,
    pickTarget: () => closestEnemy(),
    fire(game, target) {
      let current = target;
      const hit = new Set();
      for (let i = 0; i < game.mods.electronJumps; i += 1) {
        if (!current) break;
        hit.add(current.id);
        damageEnemy(current, game.mods.electronDamage, "electron");
        current.stun = Math.max(current.stun, game.mods.electronStun);
        const next = nearestEnemy(current, (enemy) => !hit.has(enemy.id), game.mods.electronRange);
        if (next) game.links.push({ x1: current.x, y1: current.y, x2: next.x, y2: next.y, ttl: 0.18 });
        current = next;
      }
      addFloat(480, 300, "跃迁", this.color);
    },
  },
};

const OPERATIONS = {
  supply: {
    name: "补给",
    tag: "资源",
    text: "立即获得30能量。",
    play(game) {
      game.energy = Math.min(game.maxEnergy, game.energy + 30);
      log("补给：能量+30。", true);
    },
  },
  expand: {
    name: "扩容",
    tag: "经济",
    text: "能量上限+15，回复速度+1。",
    play(game) {
      game.maxEnergy += 15;
      game.energyRegen += 1;
      log("扩容：能量上限和回复提高。", true);
    },
  },
  overloadBlast: {
    name: "爆燃过载",
    tag: "过载",
    text: "8秒内爆燃弹冷却加快，但自动释放额外耗能。",
    play(game) {
      game.overloads.blast = Math.max(game.overloads.blast, 8);
      log("爆燃弹进入过载。", true);
    },
  },
  overloadElectron: {
    name: "电子过载",
    tag: "过载",
    text: "8秒内跃迁电子冷却加快。",
    play(game) {
      game.overloads.electron = Math.max(game.overloads.electron, 8);
      log("跃迁电子进入过载。", true);
    },
  },
  calibrateBeam: {
    name: "射线校准",
    tag: "校准",
    text: "下一次聚能射线优先锁Boss，伤害+50%。",
    play(game) {
      game.nextBoost.beam += 0.5;
      game.targetMode = "boss";
      log("射线校准：下一次射线增强并锁Boss。", true);
    },
  },
  calibrateFrost: {
    name: "霜裂校准",
    tag: "校准",
    text: "下一次霜裂弹范围+35%，冻结概率提高。",
    play(game) {
      game.nextBoost.frost += 0.35;
      log("霜裂校准：下一发控场增强。", true);
    },
  },
  focusDense: {
    name: "密集锁定",
    tag: "目标",
    text: "10秒内自动技能优先攻击怪物密集区。",
    play(game) {
      game.targetMode = "dense";
      game.targetModeTtl = 10;
      log("目标策略：优先密集区。", true);
    },
  },
  focusGate: {
    name: "压线锁定",
    tag: "目标",
    text: "10秒内自动技能优先攻击最靠近城门的怪物。",
    play(game) {
      game.targetMode = "gate";
      game.targetModeTtl = 10;
      log("目标策略：优先压线怪。", true);
    },
  },
  recycle: {
    name: "回收",
    tag: "Cash Out",
    text: "获得15能量，并刷新全部运营牌。",
    play(game) {
      game.energy = Math.min(game.maxEnergy, game.energy + 15);
      drawOperationHand(true);
      log("回收：获得能量并刷新运营牌。", true);
    },
  },
};

const UPGRADES = [
  { name: "热浪扩散", text: "爆燃范围+22%，燃烧持续+1秒。", apply: (g) => { g.mods.blastRadius *= 1.22; g.mods.burnDuration += 1; } },
  { name: "深冻", text: "霜裂范围+18%，冻结概率提高。", apply: (g) => { g.mods.frostRadius *= 1.18; g.mods.freezeChance += 0.22; } },
  { name: "扩束镜片", text: "射线宽度+40%，持续时间+0.8秒。", apply: (g) => { g.mods.beamWidth *= 1.4; g.mods.beamDuration += 0.8; } },
  { name: "超导链路", text: "电子弹射次数+2，弹射距离+35。", apply: (g) => { g.mods.electronJumps += 2; g.mods.electronRange += 35; } },
  { name: "能量中枢", text: "能量回复+1.5，自动技能最低保留能量-8。", apply: (g) => { g.energyRegen += 1.5; g.reserveEnergy = Math.max(0, g.reserveEnergy - 8); } },
];

const ENEMY_TYPES = {
  grunt: { name: "小怪", hp: 12, speed: 44, atk: 2, radius: 15, color: "#823b35" },
  runner: { name: "跑者", hp: 8, speed: 78, atk: 1, radius: 13, color: "#a34e3d" },
  brute: { name: "重甲", hp: 26, speed: 28, atk: 4, radius: 21, color: "#62312e" },
  thrower: { name: "投石", hp: 16, speed: 34, atk: 1, radius: 16, color: "#875d32", ranged: true },
  boss: { name: "冲城巨怪", hp: 180, speed: 18, atk: 8, radius: 34, color: "#bf3a30", boss: true },
};

const els = {
  skillBar: document.getElementById("skillBar"),
  schoolList: document.getElementById("schoolList"),
  schoolHint: document.getElementById("schoolHint"),
  logList: document.getElementById("logList"),
  gateLabel: document.getElementById("gateLabel"),
  gateBar: document.getElementById("gateBar"),
  energyValue: document.getElementById("energyValue"),
  killValue: document.getElementById("killValue"),
  bossValue: document.getElementById("bossValue"),
  upgradeValue: document.getElementById("upgradeValue"),
  waveLabel: document.getElementById("waveLabel"),
  timeLabel: document.getElementById("timeLabel"),
  statusLabel: document.getElementById("statusLabel"),
  upgradeModal: document.getElementById("upgradeModal"),
  upgradeChoices: document.getElementById("upgradeChoices"),
  resultModal: document.getElementById("resultModal"),
  resultTitle: document.getElementById("resultTitle"),
  resultBody: document.getElementById("resultBody"),
};

const game = {
  gate: 100,
  maxGate: 100,
  energy: 70,
  maxEnergy: 110,
  energyRegen: 8,
  reserveEnergy: 12,
  kills: 0,
  operationPlays: 0,
  elapsed: 0,
  wave: 1,
  nextUpgradeAt: 32,
  spawnTimer: 0,
  bossSpawned: false,
  enemies: [],
  zones: [],
  beams: [],
  links: [],
  floats: [],
  logs: [],
  skillCooldowns: {},
  operationDeck: [],
  operationHand: [],
  mods: {},
  overloads: {},
  nextBoost: {},
  targetMode: "gate",
  targetModeTtl: 0,
  paused: false,
  gameOver: false,
  shake: 0,
  lastTime: 0,
};

function defaultMods() {
  return {
    blastRadius: 86,
    blastDamage: 13,
    burnDuration: 3.4,
    frostRadius: 92,
    frostSlow: 3.5,
    freezeChance: 0.18,
    vulnerableTime: 3.5,
    vulnerableBonus: 0.35,
    beamDuration: 2.6,
    beamWidth: 34,
    beamDamage: 7,
    bossBeamBonus: 3,
    electronJumps: 5,
    electronDamage: 7,
    electronRange: 125,
    electronStun: 0.18,
  };
}

function resetGame() {
  Object.assign(game, {
    gate: 100,
    maxGate: 100,
    energy: 70,
    maxEnergy: 110,
    energyRegen: 8,
    reserveEnergy: 12,
    kills: 0,
    operationPlays: 0,
    elapsed: 0,
    wave: 1,
    nextUpgradeAt: 32,
    spawnTimer: 0,
    bossSpawned: false,
    enemies: [],
    zones: [],
    beams: [],
    links: [],
    floats: [],
    logs: [],
    skillCooldowns: {},
    operationDeck: shuffle(Object.keys(OPERATIONS)),
    operationHand: [],
    mods: defaultMods(),
    overloads: { blast: 0, frost: 0, beam: 0, electron: 0 },
    nextBoost: { blast: 0, frost: 0, beam: 0, electron: 0 },
    targetMode: "gate",
    targetModeTtl: 0,
    paused: false,
    gameOver: false,
    shake: 0,
    lastTime: performance.now(),
  });
  els.resultModal.classList.add("hidden");
  els.upgradeModal.classList.add("hidden");
  drawOperationHand(true);
  log("新版：四技能自动释放，玩家用运营卡调资源和策略。", true);
  spawnEnemy("grunt");
  spawnEnemy("grunt");
  renderStaticPanels();
  renderAll();
}

function update(now) {
  const dt = Math.min(0.05, (now - game.lastTime) / 1000 || 0);
  game.lastTime = now;
  if (!game.paused && !game.gameOver) tick(dt);
  drawBattle();
  requestAnimationFrame(update);
}

function tick(dt) {
  game.elapsed += dt;
  game.energy = Math.min(game.maxEnergy, game.energy + dt * game.energyRegen);
  game.spawnTimer -= dt;
  game.targetModeTtl = Math.max(0, game.targetModeTtl - dt);
  if (game.targetModeTtl <= 0 && game.targetMode !== "gate") game.targetMode = "gate";
  Object.keys(SKILLS).forEach((key) => {
    const over = game.overloads[key] > 0;
    game.overloads[key] = Math.max(0, game.overloads[key] - dt);
    const rate = over ? 1.8 : 1;
    game.skillCooldowns[key] = Math.max(0, (game.skillCooldowns[key] || 0) - dt * rate);
  });

  if (game.elapsed > 35) game.wave = 2;
  if (game.elapsed > 70) game.wave = 3;
  if (game.elapsed > 100) game.wave = 4;
  if (game.spawnTimer <= 0) {
    spawnByWave();
    game.spawnTimer = spawnInterval();
  }

  autoFireSkills();
  updateZones(dt);
  updateBeams(dt);
  updateEnemies(dt);
  updateEffects(dt);
  cleanupEnemies();
  maybeUpgrade();
  maybeWin();
  renderHud();
  renderAutoSkillPanel();
}

function autoFireSkills() {
  Object.entries(SKILLS).forEach(([key, skill]) => {
    const extraCost = game.overloads[key] > 0 ? 4 : 0;
    if ((game.skillCooldowns[key] || 0) > 0) return;
    if (game.energy < skill.cost + extraCost + game.reserveEnergy) return;
    const target = pickSkillTarget(key);
    if (!target || game.enemies.length === 0) return;
    game.energy -= skill.cost + extraCost;
    const boost = game.nextBoost[key] || 0;
    game.activeBoost = boost;
    skill.fire(game, target);
    game.activeBoost = 0;
    game.nextBoost[key] = 0;
    game.skillCooldowns[key] = skill.cooldown;
    log(`自动释放${skill.name}。`);
  });
}

function pickSkillTarget(key) {
  if (key === "beam" && game.targetMode === "boss") {
    const boss = game.enemies.find((enemy) => enemy.boss);
    if (boss) return { x: boss.x, y: boss.y };
  }
  if (game.targetMode === "dense") return densestPoint() || closestEnemy();
  if (game.targetMode === "gate") return closestEnemy();
  return SKILLS[key].pickTarget();
}

function spawnInterval() {
  if (game.wave === 1) return 1.7;
  if (game.wave === 2) return 1.25;
  if (game.wave === 3) return 0.9;
  return 2.4;
}

function spawnByWave() {
  if (game.wave === 1) {
    spawnEnemy(Math.random() < 0.25 ? "runner" : "grunt");
  } else if (game.wave === 2) {
    spawnEnemy(Math.random() < 0.3 ? "brute" : Math.random() < 0.48 ? "runner" : "grunt");
  } else if (game.wave === 3) {
    spawnEnemy(Math.random() < 0.24 ? "thrower" : Math.random() < 0.45 ? "brute" : "runner");
  } else if (!game.bossSpawned) {
    spawnEnemy("boss");
    game.bossSpawned = true;
    log("Boss冲城巨怪出现。可用射线校准锁定。", true);
  } else {
    spawnEnemy(Math.random() < 0.7 ? "grunt" : "runner");
  }
}

function spawnEnemy(typeKey) {
  const type = ENEMY_TYPES[typeKey];
  const x = LANES[Math.floor(Math.random() * LANES.length)] + (Math.random() - 0.5) * 26;
  game.enemies.push({
    ...type,
    id: `${typeKey}-${Date.now()}-${Math.random()}`,
    typeKey,
    maxHp: type.hp,
    x,
    y: 50 + Math.random() * 18,
    slow: 0,
    frozen: 0,
    stun: 0,
    vulnerable: 0,
    rangedTimer: 1.2,
  });
}

function playOperation(index) {
  if (game.paused || game.gameOver) return;
  const id = game.operationHand[index];
  const op = OPERATIONS[id];
  op.play(game);
  game.operationPlays += 1;
  if (id !== "recycle") {
    game.operationHand.splice(index, 1, drawOperation());
  }
  renderAll();
}

function drawOperationHand(reset = false) {
  if (reset) game.operationHand = [];
  while (game.operationHand.length < 4) game.operationHand.push(drawOperation());
  renderOperations();
}

function drawOperation() {
  if (game.operationDeck.length === 0) game.operationDeck = shuffle(Object.keys(OPERATIONS));
  return game.operationDeck.shift();
}

function updateZones(dt) {
  game.zones.forEach((zone) => {
    zone.ttl -= dt;
    zone.tick -= dt;
    if (zone.tick <= 0) {
      zone.tick = 0.35;
      game.enemies.forEach((enemy) => {
        if (distance(enemy, zone) <= zone.r) damageEnemy(enemy, 2.2, "blast");
      });
    }
  });
  game.zones = game.zones.filter((zone) => zone.ttl > 0);
}

function updateBeams(dt) {
  game.beams.forEach((beam) => {
    beam.ttl -= dt;
    beam.tick -= dt;
    if (beam.tick <= 0) {
      beam.tick = 0.16;
      game.enemies.forEach((enemy) => {
        if (Math.abs(enemy.x - beam.x) <= beam.width) {
          damageEnemy(enemy, beam.damage + (enemy.boss ? game.mods.bossBeamBonus : 0), "beam");
        }
      });
    }
  });
  game.beams = game.beams.filter((beam) => beam.ttl > 0);
}

function updateEnemies(dt) {
  game.enemies.forEach((enemy) => {
    enemy.slow = Math.max(0, enemy.slow - dt);
    enemy.frozen = Math.max(0, enemy.frozen - dt);
    enemy.stun = Math.max(0, enemy.stun - dt);
    enemy.vulnerable = Math.max(0, enemy.vulnerable - dt);
    if (enemy.ranged && enemy.y > 250) {
      enemy.rangedTimer -= dt;
      if (enemy.rangedTimer <= 0) {
        enemy.rangedTimer = 1.45;
        damageGate(enemy.atk, "投石怪远程攻击");
      }
    }
    if (enemy.frozen > 0 || enemy.stun > 0) return;
    enemy.y += enemy.speed * (enemy.slow > 0 ? 0.45 : 1) * dt;
    if (enemy.y >= GATE_Y) {
      damageGate(enemy.atk, `${enemy.name}冲击城门`);
      enemy.dead = true;
    }
  });
}

function updateEffects(dt) {
  game.floats.forEach((float) => {
    float.ttl -= dt;
    float.y -= 26 * dt;
  });
  game.floats = game.floats.filter((float) => float.ttl > 0);
  game.links.forEach((link) => {
    link.ttl -= dt;
  });
  game.links = game.links.filter((link) => link.ttl > 0);
  game.shake = Math.max(0, game.shake - 0.6);
}

function cleanupEnemies() {
  let killed = 0;
  game.enemies = game.enemies.filter((enemy) => {
    if (enemy.hp <= 0 || enemy.dead) {
      if (enemy.hp <= 0) killed += 1;
      return false;
    }
    return true;
  });
  if (killed > 0) {
    game.kills += killed;
    game.energy = Math.min(game.maxEnergy, game.energy + killed * 3);
  }
}

function damageEnemy(enemy, amount, school) {
  if (!enemy || amount <= 0) return;
  let final = amount * (1 + (game.activeBoost || 0));
  if (enemy.vulnerable > 0) final *= 1 + game.mods.vulnerableBonus;
  enemy.hp -= final;
  addFloat(enemy.x, enemy.y - enemy.radius, `-${Math.ceil(final)}`, schoolColor(school));
}

function areaDamage(x, y, radius, damage, school) {
  game.enemies.forEach((enemy) => {
    if (distance(enemy, { x, y }) <= radius) damageEnemy(enemy, damage, school);
  });
}

function damageGate(amount, source) {
  game.gate -= amount;
  log(`${source}，城门-${amount}。`, true);
  if (game.gate <= 0) endGame(false);
}

function maybeUpgrade() {
  if (game.elapsed < game.nextUpgradeAt || game.paused || game.gameOver) return;
  game.nextUpgradeAt += 34;
  game.paused = true;
  const picks = shuffle(UPGRADES).slice(0, 3);
  els.upgradeChoices.innerHTML = "";
  picks.forEach((upgrade) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "upgrade";
    button.innerHTML = `<strong>${upgrade.name}</strong><span>${upgrade.text}</span>`;
    button.addEventListener("click", () => {
      upgrade.apply(game);
      game.paused = false;
      game.lastTime = performance.now();
      els.upgradeModal.classList.add("hidden");
      log(`获得强化：${upgrade.name}。`, true);
      renderAll();
    });
    els.upgradeChoices.appendChild(button);
  });
  els.upgradeModal.classList.remove("hidden");
}

function maybeWin() {
  if (game.elapsed > 132 && game.bossSpawned && game.enemies.every((enemy) => !enemy.boss)) endGame(true);
}

function endGame(win) {
  if (game.gameOver) return;
  game.gameOver = true;
  els.resultTitle.textContent = win ? "守住桥头" : "城门失守";
  els.resultBody.textContent = win
    ? "自动技能与运营卡跑通了。观察你是否在运营能量、过载与目标策略。"
    : "输出没压住怪潮。尝试用补给/扩容支撑自动技能，或用目标锁定处理压线。";
  els.resultModal.classList.remove("hidden");
}

function renderStaticPanels() {
  els.schoolList.innerHTML = Object.entries(SKILLS).map(([key, skill]) => `
    <div class="chain-step" style="box-shadow: inset 4px 0 0 ${skill.color}">
      <span>${skill.school}</span>
      <b id="auto-${key}">待机</b>
    </div>
  `).join("");
  renderOperations();
}

function renderOperations() {
  els.skillBar.innerHTML = "";
  game.operationHand.forEach((id, index) => {
    const op = OPERATIONS[id];
    const el = document.createElement("article");
    el.className = "card operation";
    el.innerHTML = `
      <div>
        <span class="tag">${op.tag}</span>
        <h3>${op.name}</h3>
        <p>${op.text}</p>
        <p class="cooldown-text">点击打出，打出后补一张。</p>
      </div>
      <div class="card-actions single">
        <button type="button">打出</button>
      </div>
    `;
    el.querySelector("button").addEventListener("click", () => playOperation(index));
    els.skillBar.appendChild(el);
  });
}

function renderAll() {
  renderHud();
  renderAutoSkillPanel();
  renderOperationsState();
  renderLog();
  drawBattle();
}

function renderHud() {
  els.gateLabel.textContent = `${Math.max(0, Math.ceil(game.gate))} / ${game.maxGate}`;
  els.gateBar.style.width = `${Math.max(0, game.gate / game.maxGate) * 100}%`;
  els.energyValue.textContent = `${Math.floor(game.energy)} / ${game.maxEnergy}`;
  els.killValue.textContent = game.kills;
  els.bossValue.textContent = game.bossSpawned ? (game.enemies.some((enemy) => enemy.boss) ? "交战中" : "已击破") : "未出现";
  els.upgradeValue.textContent = game.operationPlays;
  els.waveLabel.textContent = game.wave === 4 ? "Boss波" : `波次 ${game.wave}`;
  els.timeLabel.textContent = formatTime(game.elapsed);
  els.statusLabel.textContent = game.paused ? "选择强化" : `目标:${targetLabel()}`;
}

function renderAutoSkillPanel() {
  Object.entries(SKILLS).forEach(([key, skill]) => {
    const el = document.getElementById(`auto-${key}`);
    if (!el) return;
    const cd = game.skillCooldowns[key] || 0;
    const over = game.overloads[key] > 0;
    el.textContent = cd > 0 ? `${cd.toFixed(1)}s` : game.energy >= skill.cost + game.reserveEnergy ? (over ? "过载" : "就绪") : "缺能";
  });
}

function renderOperationsState() {
  [...els.skillBar.querySelectorAll(".card")].forEach((el) => {
    const button = el.querySelector("button");
    if (button) button.disabled = game.paused || game.gameOver;
  });
}

function renderLog() {
  els.logList.innerHTML = game.logs.map((entry) => `<div class="log-item ${entry.hot ? "hot" : ""}">${entry.text}</div>`).join("");
}

function drawBattle() {
  const shakeX = game.shake > 0 ? (Math.random() - 0.5) * game.shake : 0;
  const shakeY = game.shake > 0 ? (Math.random() - 0.5) * game.shake : 0;
  ctx.save();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.translate(shakeX, shakeY);
  ctx.fillStyle = "#b7dce9";
  ctx.fillRect(-20, -20, canvas.width + 40, canvas.height + 40);
  ctx.fillStyle = "#8fc8d8";
  for (let i = 0; i < 7; i += 1) {
    ctx.beginPath();
    ctx.ellipse(130 + i * 130, 95 + (i % 3) * 145, 62, 17, 0, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.fillStyle = "#b9a278";
  ctx.fillRect(270, 58, 420, 410);
  ctx.strokeStyle = "#8b7550";
  ctx.lineWidth = 4;
  ctx.strokeRect(270, 58, 420, 410);
  [110, 205, 300, 395].forEach((y, index) => {
    ctx.strokeStyle = "rgba(60, 48, 36, 0.28)";
    ctx.beginPath();
    ctx.moveTo(270, y);
    ctx.lineTo(690, y);
    ctx.stroke();
    ctx.fillStyle = "#3d3327";
    ctx.font = "16px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText(["怪潮入口", "远端", "中桥", "桥头"][index], 705, y + 5);
  });
  LANES.forEach((x) => {
    ctx.strokeStyle = "rgba(60, 48, 36, 0.22)";
    ctx.beginPath();
    ctx.moveTo(x, 58);
    ctx.lineTo(x, 468);
    ctx.stroke();
  });
  game.zones.forEach((zone) => {
    ctx.fillStyle = "rgba(199, 91, 50, 0.26)";
    ctx.beginPath();
    ctx.arc(zone.x, zone.y, zone.r, 0, Math.PI * 2);
    ctx.fill();
  });
  game.beams.forEach((beam) => {
    const gradient = ctx.createLinearGradient(beam.x, 470, beam.x, 50);
    gradient.addColorStop(0, "rgba(124, 91, 214, 0.8)");
    gradient.addColorStop(1, "rgba(124, 91, 214, 0.08)");
    ctx.fillStyle = gradient;
    ctx.fillRect(beam.x - beam.width, 58, beam.width * 2, 410);
  });
  game.links.forEach((link) => {
    ctx.strokeStyle = `rgba(45, 143, 111, ${Math.max(0, link.ttl / 0.18)})`;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(link.x1, link.y1);
    ctx.lineTo(link.x2, link.y2);
    ctx.stroke();
  });
  ctx.fillStyle = "#5c6370";
  ctx.fillRect(245, 470, 470, 56);
  ctx.fillStyle = "#39414d";
  ctx.fillRect(380, 438, 200, 42);
  ctx.fillStyle = "#f2c94c";
  ctx.fillRect(445, 470, 70, 55);
  ctx.fillStyle = "#fff";
  ctx.font = "17px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("城门 / 防线", 480, 500);
  game.enemies.forEach((enemy) => {
    ctx.fillStyle = enemy.frozen > 0 ? "#3c91a3" : enemy.color;
    ctx.beginPath();
    ctx.arc(enemy.x, enemy.y, enemy.radius, 0, Math.PI * 2);
    ctx.fill();
    if (enemy.vulnerable > 0) {
      ctx.strokeStyle = "#e8f2ff";
      ctx.lineWidth = 4;
      ctx.stroke();
    }
    ctx.fillStyle = "#fff";
    ctx.font = enemy.boss ? "13px sans-serif" : "11px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(enemy.boss ? "Boss" : enemy.name.slice(0, 2), enemy.x, enemy.y - 1);
    ctx.fillText(`${Math.max(0, Math.ceil(enemy.hp))}`, enemy.x, enemy.y + 13);
  });
  game.floats.forEach((float) => {
    ctx.globalAlpha = Math.max(0, float.ttl);
    ctx.fillStyle = float.color;
    ctx.font = "bold 18px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(float.text, float.x, float.y);
    ctx.globalAlpha = 1;
  });
  ctx.restore();
}

function densestPoint() {
  if (game.enemies.length === 0) return null;
  return [...game.enemies].sort((a, b) => neighborCount(b, 105) - neighborCount(a, 105))[0];
}

function neighborCount(enemy, radius) {
  return game.enemies.filter((other) => distance(enemy, other) <= radius).length;
}

function closestEnemy() {
  return [...game.enemies].sort((a, b) => b.y - a.y)[0];
}

function laneOfPriority() {
  const boss = game.enemies.find((enemy) => enemy.boss);
  if (boss) return boss.x;
  const target = game.targetMode === "dense" ? densestPoint() : closestEnemy();
  return target ? target.x : 480;
}

function nearestEnemy(origin, predicate = () => true, range = 120) {
  return game.enemies.filter((enemy) => enemy !== origin && predicate(enemy) && distance(enemy, origin) <= range)
    .sort((a, b) => distance(a, origin) - distance(b, origin))[0];
}

function distance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function addFloat(x, y, text, color) {
  game.floats.push({ x, y, text, color, ttl: 1 });
}

function schoolColor(school) {
  if (school === "blast") return "#c75b32";
  if (school === "frost") return "#3c91a3";
  if (school === "beam") return "#7c5bd6";
  if (school === "electron") return "#2d8f6f";
  return "#1f2933";
}

function targetLabel() {
  if (game.targetMode === "dense") return "密集";
  if (game.targetMode === "boss") return "Boss";
  return "压线";
}

function log(text, hot = false) {
  game.logs.unshift({ text, hot });
  game.logs = game.logs.slice(0, 36);
  renderLog();
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60).toString().padStart(2, "0");
  const s = Math.floor(seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

function shuffle(items) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

document.getElementById("restartBtn").addEventListener("click", resetGame);
document.getElementById("resultRestartBtn").addEventListener("click", resetGame);

resetGame();
requestAnimationFrame(update);
