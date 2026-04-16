(function () {
  const canvas = document.getElementById("game-canvas");
  const ctx = canvas.getContext("2d");

  const ui = {
    baseHp: document.getElementById("base-hp"),
    timer: document.getElementById("timer"),
    wave: document.getElementById("wave"),
    score: document.getElementById("score"),
    zombiesLeft: document.getElementById("zombies-left"),
    ballsLeft: document.getElementById("balls-left"),
    reload: document.getElementById("reload"),
    mode: document.getElementById("mode"),
    buildText: document.getElementById("build-text"),
    buildPill: document.getElementById("build-pill"),
    hintText: document.getElementById("hint-text"),
    aimText: document.getElementById("aim-text"),
    goalPill: document.getElementById("goal-pill"),
    startOverlay: document.getElementById("start-overlay"),
    pauseOverlay: document.getElementById("pause-overlay"),
    upgradeOverlay: document.getElementById("upgrade-overlay"),
    resultOverlay: document.getElementById("result-overlay"),
    choiceGrid: document.getElementById("choice-grid"),
    jokerRack: document.getElementById("joker-rack"),
    resultTag: document.getElementById("result-tag"),
    resultTitle: document.getElementById("result-title"),
    resultSummary: document.getElementById("result-summary"),
    startButton: document.getElementById("start-button"),
    restartButton: document.getElementById("restart-button"),
    rerollButton: document.getElementById("reroll-button"),
    skipButton: document.getElementById("skip-button"),
    upgradeEyebrow: document.getElementById("upgrade-eyebrow"),
    upgradeTitle: document.getElementById("upgrade-title"),
    upgradeSubtitle: document.getElementById("upgrade-subtitle"),
    joystick: document.getElementById("mobile-joystick"),
    joystickThumb: document.getElementById("mobile-joystick-thumb"),
  };

  const BASE_W = 1280;
  const BASE_H = 720;
  const W = 1600;
  const H = 900;
  const SCALE_X = W / BASE_W;
  const SCALE_Y = H / BASE_H;
  const MATCH_DURATION = 480;
  const ROAD_LEFT = Math.round(332 * SCALE_X);
  const ROAD_RIGHT = Math.round(948 * SCALE_X);
  const CENTER_X = (ROAD_LEFT + ROAD_RIGHT) / 2;
  const EDGE_PADDING = 30;

  const GAME_TUNING = {
    waves: {
      totalMonsterWaves: 1000,
      openingWaveCount: 4,
    },
    route: {
      checkpointStopBaseDuration: 10,
      checkpointStopStepDuration: 5,
      latePressure: {
        startSegmentIndex: 3,
        pressureBonusScale: 0.28,
        perSegmentBonus: 0.24,
        checkpointBonus: 0.16,
        finalHoldBonus: 0.22,
        intervalMultiplier: 0.74,
        trickleExtraCount: 2,
        surgeExtraCount: 3,
        ambushExtraCount: 2,
        extraEliteChanceBonus: 0.34,
        checkpointChoiceStartSegment: 3,
        checkpointChoiceGain: 1,
      },
      checkpointThreat: {
        trickleIntervalMultiplier: 0.7,
        surgeIntervalMultiplier: 0.58,
        ambushIntervalMultiplier: 0.62,
        extraEliteChance: 0.62,
        bossUnlockProgress: 0.55,
        bossChance: 0.16,
      },
    },
    combat: {
      baseFireRate: 0.734,
      heroMaxEscortDistance: 220,
    },
    spawn: {
      trickleStartRange: [1.8, 2.8],
      surgeStartRange: [20, 28],
      ambushStartRange: [26, 36],
      trickleResetRange: [1.8, 2.8],
      tricklePressureScale: 1.2,
      trickleMinInterval: 0.65,
      surgeResetRange: [22, 30],
      surgePressureScale: 5.4,
      surgeMinInterval: 8.5,
      ambushResetRange: [28, 38],
      ambushPressureScale: 6.5,
      ambushMinInterval: 10.5,
      trickleBaseCount: 2,
      tricklePressureCountScale: 2.4,
      trickleBonusChanceBase: 0.35,
      trickleBonusChanceScale: 0.35,
      surgeBaseCount: 2,
      surgePressureCountScale: 4.5,
      surgeRandomBonusCount: 2,
      surgeEliteChanceBase: 0.45,
      surgeEliteChanceScale: 0.36,
      surgeEliteUnlockPressure: 0.18,
      ambushBaseCount: 1,
      ambushPressureCountScale: 4,
      ambushRandomBonusCount: 2,
    },
    roguelike: {
      killChoiceThresholds: [4, 8, 16, 32, 64, 128, 256, 512],
    },
  };

  function scalePoint(point) {
    return {
      ...point,
      x: Math.round(point.x * SCALE_X),
      y: Math.round(point.y * SCALE_Y),
    };
  }

  const ROUTE = [
    { x: 640, y: 640, label: "出发" },
    { x: 560, y: 560, label: "外环路口" },
    { x: 720, y: 480, label: "加油站" },
    { x: 520, y: 390, label: "商场广场" },
    { x: 760, y: 300, label: "医院街口" },
    { x: 500, y: 210, label: "地铁口" },
    { x: 640, y: 140, label: "安全区" },
  ].map(scalePoint);

  const SPAWN_GATES = [
    { x: -24, y: 120 },
    { x: 1304, y: 150 },
    { x: -24, y: 540 },
    { x: 1304, y: 520 },
    { x: 220, y: -24 },
    { x: 1060, y: -24 },
    { x: 250, y: 744 },
    { x: 1030, y: 744 },
  ].map(scalePoint);

  const zombieDefs = {
    walker: { label: "普通丧尸", color: "#8fe17b", radius: 15, hp: 24, speed: 30, damage: 6, score: 40, xp: 1 },
    runner: { label: "冲锋丧尸", color: "#b1ff92", radius: 13, hp: 16, speed: 44, damage: 4, score: 55, xp: 1 },
    brute: { label: "重型丧尸", color: "#ff8f8d", radius: 24, hp: 42, speed: 20, damage: 12, score: 120, xp: 2 },
    spitter: { label: "喷吐丧尸", color: "#7db5ff", radius: 18, hp: 28, speed: 24, damage: 8, score: 90, xp: 2 },
    elite: { label: "精英尸群", color: "#ffcf6e", radius: 22, hp: 70, speed: 26, damage: 10, score: 220, xp: 3 },
    boss: { label: "尸潮 Boss", color: "#ff6575", radius: 36, hp: 220, speed: 16, damage: 18, score: 900, xp: 8 },
  };

  const jokerPool = [
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
      title: "重弹小丑",
      rarity: "uncommon",
      tag: "攻击",
      description: "子弹命中即消失，但单发伤害更高。等级越高，伤害与索敌范围继续提升。",
      maxLevel: 3,
      condition: () => true,
      apply: (game, card) => {
        const level = card.level;
        game.hero.damageBonus += 4 + (level - 1) * 4;
        game.hero.range += Math.max(0, level - 1) * 18;
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
      id: "checkpoint_fortress",
      title: "堡垒小丑",
      rarity: "rare",
      tag: "防守",
      description: "驻点停留时，护送车会周期性释放防守脉冲，击退近身尸潮并小幅修车。",
      maxLevel: 3,
      condition: () => true,
      apply: (game, card) => {
        const level = card.level;
        game.escort.checkpointPulseDamage = 10 + (level - 1) * 6;
        game.escort.checkpointPulseRadius = 126 + (level - 1) * 18;
        game.escort.checkpointPulseInterval = Math.max(1.4, 2.8 - (level - 1) * 0.35);
        game.escort.checkpointPulseHeal = 2 + (level - 1) * 2;
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
      id: "executioner_joker",
      title: "处刑小丑",
      rarity: "uncommon",
      tag: "攻击",
      description: "对精英与 Boss 造成更高伤害。等级越高，后半局处理高威胁单位更快。",
      maxLevel: 3,
      condition: () => true,
      apply: (game, card) => {
        const level = card.level;
        game.hero.eliteDamageMult += 0.24 + (level - 1) * 0.16;
      },
    },
    {
      id: "overdrive_joker",
      title: "狂热小丑",
      rarity: "rare",
      tag: "节奏",
      description: "每打出数次射击后，进入短暂过载连射。等级越高，过载更频繁、持续更久。",
      maxLevel: 3,
      condition: () => true,
      apply: (game, card) => {
        const level = card.level;
        game.hero.overdriveEveryShots = Math.max(3, 6 - (level - 1));
        game.hero.overdriveBurstShots = 2 + level;
        game.hero.overdriveFireMult = Math.max(0.48, 0.68 - (level - 1) * 0.08);
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
      id: "bounty_joker",
      title: "赏金小丑",
      rarity: "rare",
      tag: "节奏",
      description: "每击杀数只精英或 Boss，就额外获得一次抽牌与一次重抽，后半局更容易滚起雪球。",
      maxLevel: 3,
      condition: () => true,
      apply: (game, card) => {
        const level = card.level;
        game.hero.bountyNeed = Math.max(1, 3 - (level - 1));
      },
    },
    {
      id: "shrapnel_joker",
      title: "破片小丑",
      rarity: "rare",
      tag: "爆发",
      description: "命中精英或 Boss 时触发破片爆裂，对周围尸群造成额外伤害。",
      maxLevel: 3,
      condition: () => true,
      apply: (game, card) => {
        const level = card.level;
        game.hero.impactBurst = true;
        game.hero.impactBurstRadius = 72 + (level - 1) * 18;
        game.hero.impactBurstDamage = 8 + (level - 1) * 5;
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

  const rarityOrder = {
    common: 0,
    uncommon: 1,
    rare: 2,
    legendary: 3,
  };

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function rand(min, max) {
    return Math.random() * (max - min) + min;
  }

  function distance(x1, y1, x2, y2) {
    return Math.hypot(x1 - x2, y1 - y2);
  }

  function formatTime(totalSeconds) {
    const safeSeconds = Math.max(0, Math.ceil(totalSeconds));
    const minutes = String(Math.floor(safeSeconds / 60)).padStart(2, "0");
    const seconds = String(safeSeconds % 60).padStart(2, "0");
    return `${minutes}:${seconds}`;
  }

  function shuffle(items) {
    const next = [...items];
    for (let i = next.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [next[i], next[j]] = [next[j], next[i]];
    }
    return next;
  }

  function roundRect(context, x, y, width, height, radius, fill, stroke) {
    context.beginPath();
    context.moveTo(x + radius, y);
    context.lineTo(x + width - radius, y);
    context.quadraticCurveTo(x + width, y, x + width, y + radius);
    context.lineTo(x + width, y + height - radius);
    context.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    context.lineTo(x + radius, y + height);
    context.quadraticCurveTo(x, y + height, x, y + height - radius);
    context.lineTo(x, y + radius);
    context.quadraticCurveTo(x, y, x + radius, y);
    context.closePath();
    if (fill) context.fill();
    if (stroke) context.stroke();
  }

  function showOverlay(element) {
    element.classList.remove("hidden");
  }

  function hideOverlay(element) {
    element.classList.add("hidden");
  }

  function reportRuntimeError(error) {
    const message = error && error.message ? error.message : String(error);
    ui.hintText.textContent = `运行异常：${message}`;
    ui.mode.textContent = "运行异常";
    showOverlay(ui.resultOverlay);
    ui.resultTag.textContent = "运行异常";
    ui.resultTitle.textContent = "Demo 已暂停";
    ui.resultSummary.textContent = `脚本报错：${message}`;
  }

  function clearDirectionalKeys() {
    for (const key of ["w", "a", "s", "d"]) {
      game.keys.delete(key);
    }
    if (game.moveStick) {
      game.moveStick.active = false;
      game.moveStick.pointerId = null;
      game.moveStick.x = 0;
      game.moveStick.y = 0;
    }
    if (ui.joystick) {
      ui.joystick.classList.remove("is-active");
    }
    if (ui.joystickThumb) {
      ui.joystickThumb.style.transform = "translate3d(0px, 0px, 0px)";
    }
  }

  function renderChoiceGrid(choices) {
    ui.choiceGrid.innerHTML = choices
      .map(
        (choice) => `
          <button class="choice-card" data-upgrade="${choice.id}" data-rarity="${choice.rarity || "common"}">
            <span class="choice-badge">${choice.tag || "通用"}</span>
            <span class="choice-level">Lv.${choice.level || 1}</span>
            <p>${choice.title}</p>
            <small>${choice.description}</small>
          </button>
        `,
      )
      .join("");
  }

  function updateJokerRack(game) {
    const occupied = game.jokerCards.slice(0, game.jokerSlots).map((card, index) => `
      <div class="joker-card" data-rarity="${card.rarity || "common"}">
        <strong>${index + 1}. ${card.title} <span class="joker-level">Lv.${card.level || 1}</span></strong>
        <small>${card.rarity || "common"} · ${card.tag} · ${card.description}</small>
        <small>经验 ${Math.floor(card.xp || 0)} / ${card.xpNeed || 0}</small>
      </div>
    `);

    const emptyCount = Math.max(0, game.jokerSlots - occupied.length);
    const emptySlots = Array.from({ length: emptyCount }, (_, index) => `
      <div class="joker-card joker-card--empty">
        <strong>空槽 ${occupied.length + index + 1}</strong>
        <small>等待抽牌</small>
      </div>
    `);

    const html = [...occupied, ...emptySlots].join("");
    if (html !== game.lastJokerRackHtml) {
      game.lastJokerRackHtml = html;
      ui.jokerRack.innerHTML = html;
    }
  }

  function updateHud(game) {
    ui.baseHp.textContent = `${Math.max(0, Math.ceil(game.escort.hp))} / ${game.escort.maxHp}`;
    ui.timer.textContent = formatTime(game.timer);
    ui.wave.textContent = `${Math.min(game.currentWave, GAME_TUNING.waves.totalMonsterWaves)} / ${GAME_TUNING.waves.totalMonsterWaves}`;
    ui.score.textContent = `${game.kills}`;
    ui.zombiesLeft.textContent = `${game.zombies.length}`;
    ui.ballsLeft.textContent = `${game.bullets.length}`;
    ui.reload.textContent = game.hero.fireCd > 0 ? `${game.hero.fireCd.toFixed(1)}s` : "Ready";
    ui.mode.textContent = game.getModeText();
    ui.buildText.textContent = game.getBuildSummary();
    ui.buildPill.textContent = game.getBuildSummary();
    ui.aimText.textContent = game.state === "start" ? "待开始" : `主角 ${Math.round(game.hero.x)}, ${Math.round(game.hero.y)}`;
    ui.goalPill.textContent = game.getGoalText();
    if (ui.rerollButton) {
      ui.rerollButton.textContent = game.rerollCharges > 0 ? `重抽 ${game.rerollCharges} 次` : "重抽已空";
    }
    updateJokerRack(game);
  }

  function renderGame(game) {
    ctx.clearRect(0, 0, W, H);
    drawBackground();
    drawRoad();
    drawSpawnZones();
    drawRoute(game);
    drawBullets(game);
    drawZombies(game);
    drawEscort(game);
    drawHero(game);
    drawParticles(game);
    drawTexts(game);
    drawTopBanner(game);
    drawBottomGuide();
  }

  function drawBackground() {
    const bg = ctx.createLinearGradient(0, 0, 0, H);
    bg.addColorStop(0, "#0f1521");
    bg.addColorStop(1, "#080b13");
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);

    const haze = ctx.createRadialGradient(W * 0.5, H * 0.2, 30, W * 0.5, H * 0.2, 460);
    haze.addColorStop(0, "rgba(125, 240, 192, 0.08)");
    haze.addColorStop(1, "rgba(125, 240, 192, 0)");
    ctx.fillStyle = haze;
    ctx.fillRect(0, 0, W, H);
  }

  function drawRoad() {
    ctx.save();
    ctx.fillStyle = "#121721";
    ctx.fillRect(ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, H);
    const strip = ctx.createLinearGradient(ROAD_LEFT, 0, ROAD_RIGHT, 0);
    strip.addColorStop(0, "rgba(255,255,255,0.02)");
    strip.addColorStop(0.5, "rgba(125,240,192,0.03)");
    strip.addColorStop(1, "rgba(255,255,255,0.02)");
    ctx.fillStyle = strip;
    ctx.fillRect(ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, H);
    ctx.strokeStyle = "rgba(255,255,255,0.07)";
    ctx.lineWidth = 1;
    for (let y = 0; y < H; y += 42) {
      ctx.beginPath();
      ctx.moveTo(ROAD_LEFT, y);
      ctx.lineTo(ROAD_RIGHT, y);
      ctx.stroke();
    }
    ctx.fillStyle = "rgba(255,255,255,0.06)";
    for (let y = 40; y < H; y += 92) {
      ctx.fillRect(CENTER_X - 3, y, 6, 42);
    }
    ctx.restore();
  }

  function drawSpawnZones() {
    ctx.save();
    ctx.fillStyle = "rgba(255, 101, 117, 0.06)";
    ctx.fillRect(0, 0, ROAD_LEFT, H);
    ctx.fillRect(ROAD_RIGHT, 0, W - ROAD_RIGHT, H);
    ctx.fillStyle = "rgba(255, 101, 117, 0.11)";
    ctx.fillRect(0, 0, W, 86);
    ctx.fillRect(0, H - 86, W, 86);
    ctx.fillStyle = "rgba(255,255,255,0.03)";
    for (let i = 0; i < 14; i += 1) {
      const x = i % 2 === 0 ? rand(16, ROAD_LEFT - 28) : rand(ROAD_RIGHT + 8, W - 16);
      const y = rand(10, H - 10);
      ctx.fillRect(x, y, rand(8, 30), rand(18, 64));
    }
    ctx.restore();
  }

  function drawRoute(game) {
    ctx.save();
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = "rgba(125, 240, 192, 0.16)";
    ctx.lineWidth = 42;
    ctx.beginPath();
    ctx.moveTo(game.route[0].x, game.route[0].y);
    for (let i = 1; i < game.route.length; i += 1) {
      ctx.lineTo(game.route[i].x, game.route[i].y);
    }
    ctx.stroke();
    ctx.setLineDash([14, 12]);
    ctx.strokeStyle = "rgba(125, 240, 192, 0.55)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(game.route[0].x, game.route[0].y);
    for (let i = 1; i < game.route.length; i += 1) {
      ctx.lineTo(game.route[i].x, game.route[i].y);
    }
    ctx.stroke();
    ctx.setLineDash([]);
    for (let i = 0; i < game.route.length; i += 1) {
      const point = game.route[i];
      ctx.fillStyle = i <= game.segmentIndex ? "#7df0c0" : "#ffd166";
      ctx.beginPath();
      ctx.arc(point.x, point.y, i === game.route.length - 1 ? 14 : 10, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "rgba(255,255,255,0.18)";
      ctx.font = "12px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(point.label, point.x, point.y - 18);
    }
    ctx.restore();
  }

  function drawEscort(game) {
    const target = game.route[Math.min(game.segmentIndex + 1, game.route.length - 1)];
    const angle = Math.atan2(target.y - game.escort.y, target.x - game.escort.x);
    ctx.save();
    ctx.translate(game.escort.x, game.escort.y);
    ctx.rotate(angle);
    const glow = ctx.createRadialGradient(0, 0, 4, 0, 0, 66);
    glow.addColorStop(0, "rgba(125,240,192,0.42)");
    glow.addColorStop(1, "rgba(125,240,192,0)");
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(0, 0, 60, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#1a2333";
    roundRect(ctx, -18, -30, 36, 60, 10, true, false);
    ctx.fillStyle = "#7df0c0";
    roundRect(ctx, -16, -26, 32, 52, 9, true, false);
    ctx.fillStyle = "#0c1018";
    roundRect(ctx, -10, -18, 20, 20, 6, true, false);
    ctx.fillStyle = "#ff6575";
    ctx.fillRect(-14, 24, 10, 4);
    ctx.fillRect(4, 24, 10, 4);
    ctx.restore();
    drawHealthBar(game.escort.x, game.escort.y - 40, 74, game.escort.hp / game.escort.maxHp, "#7df0c0");
  }

  function drawHero(game) {
    const aimPoint = game.getAimPoint();
    const angle = Math.atan2(aimPoint.y - game.hero.y, aimPoint.x - game.hero.x);
    ctx.save();
    ctx.strokeStyle = "rgba(255, 209, 102, 0.22)";
    ctx.fillStyle = "rgba(255, 209, 102, 0.05)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(game.hero.x, game.hero.y, game.hero.range, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    const glow = ctx.createRadialGradient(game.hero.x, game.hero.y, 2, game.hero.x, game.hero.y, 52);
    glow.addColorStop(0, "rgba(255, 209, 102, 0.4)");
    glow.addColorStop(1, "rgba(255, 209, 102, 0)");
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(game.hero.x, game.hero.y, 44, 0, Math.PI * 2);
    ctx.fill();
    ctx.translate(game.hero.x, game.hero.y);
    ctx.rotate(angle);
    ctx.fillStyle = "#ffd166";
    ctx.beginPath();
    ctx.arc(0, 0, game.hero.r, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#241605";
    ctx.fillRect(3, -3, 18, 6);
    ctx.strokeStyle = "rgba(255,255,255,0.28)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(10, 0);
    ctx.lineTo(26, 0);
    ctx.stroke();
    ctx.restore();
    drawHealthBar(game.hero.x, game.hero.y - 22, 42, game.hero.hp / game.hero.maxHp, "#ffd166");
  }

  function drawZombies(game) {
    for (const zombie of game.zombies) {
      ctx.save();
      ctx.translate(zombie.x, zombie.y);
      const glow = ctx.createRadialGradient(0, 0, 2, 0, 0, zombie.r * 2.8);
      glow.addColorStop(0, zombie.color);
      glow.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(0, 0, zombie.r * 2.2, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = zombie.hitFlash > 0 ? "#ffffff" : zombie.color;
      ctx.beginPath();
      ctx.arc(0, 0, zombie.r, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "rgba(0, 0, 0, 0.24)";
      ctx.beginPath();
      ctx.arc(-zombie.r * 0.25, -zombie.r * 0.15, zombie.r * 0.12, 0, Math.PI * 2);
      ctx.arc(zombie.r * 0.25, -zombie.r * 0.15, zombie.r * 0.12, 0, Math.PI * 2);
      ctx.fill();
      if (zombie.kind === "boss") {
        ctx.strokeStyle = "#ffe38d";
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(0, 0, zombie.r + 8, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.restore();
      drawHealthBar(zombie.x, zombie.y - zombie.r - 12, zombie.kind === "boss" ? 88 : 44, zombie.hp / zombie.maxHp, zombie.color);
    }
  }

  function drawBullets(game) {
    for (const bullet of game.bullets) {
      ctx.save();
      const glow = ctx.createRadialGradient(bullet.x, bullet.y, 1, bullet.x, bullet.y, 16);
      glow.addColorStop(0, "#ffcf6e");
      glow.addColorStop(1, "rgba(255, 207, 110, 0)");
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(bullet.x, bullet.y, 10, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#ffcf6e";
      ctx.beginPath();
      ctx.arc(bullet.x, bullet.y, bullet.r, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
  }

  function drawParticles(game) {
    for (const particle of game.particles) {
      ctx.globalAlpha = clamp(particle.life / 0.55, 0, 1);
      ctx.fillStyle = particle.color;
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function drawTexts(game) {
    ctx.textAlign = "center";
    ctx.font = "14px sans-serif";
    for (const text of game.texts) {
      ctx.globalAlpha = clamp(text.life / 0.9, 0, 1);
      ctx.fillStyle = text.color;
      ctx.fillText(text.text, text.x, text.y);
    }
    ctx.globalAlpha = 1;
  }

  function drawTopBanner(game) {
    ctx.save();
    ctx.fillStyle = "rgba(255,255,255,0.08)";
    ctx.font = "14px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText("护送目标自动前进，使用 WASD 手动走位清障，主角会自动锁敌并以直线弹道开火", 18, 24);
    ctx.fillStyle = "rgba(255,255,255,0.72)";
    ctx.fillText(`当前 Build：${game.getBuildSummary()}`, 18, 46);
    if (game.checkpointPauseRemaining > 0 && game.currentCheckpointName) {
      ctx.fillStyle = "rgba(125, 240, 192, 0.95)";
      ctx.font = "18px sans-serif";
      ctx.fillText(`驻守 ${game.currentCheckpointName} · 剩余 ${Math.ceil(game.checkpointPauseRemaining)}s`, W / 2 - 120, 28);
    } else if (game.currentCheckpointName) {
      ctx.fillStyle = "rgba(255,255,255,0.62)";
      ctx.font = "16px sans-serif";
      ctx.fillText(`当前驻点：${game.currentCheckpointName}`, W / 2 - 72, 28);
    }
    if (game.finalHold && game.bossSpawned) {
      ctx.fillStyle = "rgba(255, 101, 117, 0.95)";
      ctx.font = "18px sans-serif";
      ctx.fillText("安全区前最终决战", W / 2 - 84, 28);
    }
    ctx.restore();
  }

  function drawBottomGuide() {
    ctx.save();
    ctx.strokeStyle = "rgba(255,255,255,0.08)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(24, H - 26);
    ctx.lineTo(W - 24, H - 26);
    ctx.stroke();
    ctx.fillStyle = "rgba(255,255,255,0.18)";
    ctx.font = "12px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText("路段目标", 30, H - 38);
    ctx.restore();
  }

  function drawHealthBar(x, y, width, ratio, color) {
    ctx.fillStyle = "rgba(8, 10, 17, 0.88)";
    ctx.fillRect(x - width / 2, y, width, 6);
    ctx.fillStyle = color;
    ctx.fillRect(x - width / 2, y, width * clamp(ratio, 0, 1), 6);
  }

  class Game {
    constructor() {
      this.boundLoop = (time) => this.loop(time);
      this.lastTime = 0;
      this.nextId = 1;
      this.pointer = { x: W / 2, y: H / 2, active: false };
      this.moveStick = { active: false, pointerId: null, x: 0, y: 0 };
      this.keys = new Set();
      this.reset();
    }

    reset() {
      this.state = "start";
      this.elapsed = 0;
      this.timer = MATCH_DURATION;
      this.segmentIndex = 0;
      this.currentWave = 0;
      this.currentCheckpointName = ROUTE[0].label;
      this.checkpointPauseRemaining = 0;
      this.score = 0;
      this.kills = 0;
      this.xp = 0;
      this.xpNeed = 5;
      this.upgradeCharge = 0;
      this.nextChoiceKillIndex = 0;
      this.nextChoiceKillTarget = GAME_TUNING.roguelike.killChoiceThresholds[0];
      this.jokerSlots = 8;
      this.bossSpawned = false;
      this.bossKilled = false;
      this.finalHold = false;
      this.nextChoiceReason = "";
      this.nextChoiceSubtitle = "";
      this.choiceReasonQueue = [];
      this.checkpointPulseCd = 0;
      this.spawnTimers = {
        trickle: rand(...GAME_TUNING.spawn.trickleStartRange),
        surge: rand(...GAME_TUNING.spawn.surgeStartRange),
        ambush: rand(...GAME_TUNING.spawn.ambushStartRange),
      };
      this.zombies = [];
      this.bullets = [];
      this.particles = [];
      this.texts = [];
      this.jokerCards = [];
      this.lastJokerRackHtml = "";
      this.upgradesTaken = new Set();
      this.pendingChoices = [];
      this.rerollCharges = 1;
      this.route = ROUTE.map((point) => ({ ...point }));
      this.baseEscort = {
        x: this.route[0].x,
        y: this.route[0].y,
        r: 24,
        hp: 160,
        maxHp: 160,
        speed: 8,
        checkpointHeal: 12,
        checkpointPulseDamage: 0,
        checkpointPulseRadius: 0,
        checkpointPulseInterval: 0,
        checkpointPulseHeal: 0,
      };
      this.baseHero = {
        x: this.route[0].x + 88 * SCALE_X,
        y: this.route[0].y + 24 * SCALE_Y,
        r: 14,
        hp: 100,
        maxHp: 100,
        speed: 250,
        damage: 14,
        damageBonus: 0,
        fireRate: GAME_TUNING.combat.baseFireRate,
        fireRateMult: 1,
        fireCd: 0,
        bulletsPerShot: 1,
        spread: 0,
        bulletSpeed: 620,
        range: 320,
        autoAimRange: 140,
        chainBurst: false,
        eliteDamageMult: 1,
        overdriveEveryShots: 0,
        overdriveCounter: 0,
        overdriveBurstShots: 0,
        overdriveShotsRemaining: 0,
        overdriveFireMult: 1,
        bountyNeed: 0,
        bountyCounter: 0,
        impactBurst: false,
        impactBurstRadius: 0,
        impactBurstDamage: 0,
        panicBlast: false,
      };
      this.hero = { ...this.baseHero };
      this.escort = { ...this.baseEscort };
      this.rebuildLoadout();
      this.showStartState();
      this.renderUpgradeChoices();
      updateHud(this);
    }

    start() {
      showOverlay(ui.startOverlay);
      hideOverlay(ui.pauseOverlay);
      hideOverlay(ui.upgradeOverlay);
      hideOverlay(ui.resultOverlay);
      updateHud(this);
      requestAnimationFrame(this.boundLoop);
    }

    beginRun() {
      this.reset();
      this.state = "playing";
      hideOverlay(ui.startOverlay);
      hideOverlay(ui.pauseOverlay);
      hideOverlay(ui.upgradeOverlay);
      hideOverlay(ui.resultOverlay);
      this.spawnOpeningWave();
      updateHud(this);
    }

    loop(time) {
      const dt = Math.min(((time - this.lastTime) || 0) / 1000, 0.033);
      this.lastTime = time;
      try {
        if (this.state === "playing") {
          this.update(dt);
        }
        renderGame(this);
      } catch (error) {
        console.error(error);
        this.state = "error";
        reportRuntimeError(error);
      }
      requestAnimationFrame(this.boundLoop);
    }

    update(dt) {
      this.elapsed += dt;
      this.timer = Math.max(0, MATCH_DURATION - this.elapsed);
      this.handleRouteProgress(dt);
      if (this.state !== "playing") {
        updateHud(this);
        return;
      }
      this.handleSpawnTimers(dt);
      this.updateHero(dt);
      this.updateAutoFire();
      this.updateBullets(dt);
      this.updateZombies(dt);
      this.updateCheckpointPulse(dt);
      this.updateParticles(dt);
      this.updateTexts(dt);
      if (this.upgradeCharge > 0 && this.pendingChoices.length === 0 && this.state === "playing") {
        this.upgradeCharge -= 1;
        this.triggerChoice(this.choiceReasonQueue.shift() || `击杀达到 ${this.kills}`);
      }
      if (this.escort.hp <= 0 || this.hero.hp <= 0) {
        this.finish(false, this.escort.hp <= 0 ? "护送目标被尸潮拖垮了。" : "主角被尸潮压制倒下了。");
        return;
      }
      if (this.timer <= 0) {
        if (this.finalHold && this.bossKilled) {
          this.finish(true, "车队抵达安全区，最后的尸潮也被清空。");
        } else {
          this.finish(false, "时间到了，但车队还没能完成突围。");
        }
        return;
      }
      if (this.finalHold && this.bossSpawned && this.bossKilled && this.escort.hp > 0) {
        this.finish(true, "车队护送成功，安全区已经打开。");
        return;
      }
      this.updateHintText();
      updateHud(this);
    }

    handleRouteProgress(dt) {
      if (this.state !== "playing") return;
      if (this.finalHold || this.segmentIndex >= this.route.length - 1) return;
      if (this.checkpointPauseRemaining > 0) {
        this.checkpointPauseRemaining = Math.max(0, this.checkpointPauseRemaining - dt);
        return;
      }
      const target = this.route[this.segmentIndex + 1];
      const dx = target.x - this.escort.x;
      const dy = target.y - this.escort.y;
      const dist = Math.hypot(dx, dy) || 1;
      const step = Math.min(dist, this.escort.speed * dt);
      this.escort.x += (dx / dist) * step;
      this.escort.y += (dy / dist) * step;
      if (dist <= 7) {
        this.escort.x = target.x;
        this.escort.y = target.y;
        if (this.segmentIndex + 1 >= this.route.length - 1) {
          this.currentCheckpointName = target.label;
          this.checkpointPauseRemaining = 0;
          this.finalHold = true;
          if (!this.bossSpawned) this.spawnBoss();
          this.spawnText(target.x, target.y - 46, "安全区前最后一战", "#ffcf6e");
          return;
        }
        this.segmentIndex += 1;
        this.currentCheckpointName = target.label;
        this.checkpointPauseRemaining = this.getCheckpointStopDuration();
        this.escort.hp = Math.min(this.escort.maxHp, this.escort.hp + this.escort.checkpointHeal);
        this.score += 120;
        if (this.segmentIndex >= GAME_TUNING.route.latePressure.checkpointChoiceStartSegment) {
          this.upgradeCharge += GAME_TUNING.route.latePressure.checkpointChoiceGain;
          this.choiceReasonQueue.push(`抵达 ${target.label}`);
          this.spawnText(target.x, target.y - 66, "后半局补给 · 获得抽牌", "#ffd166");
        }
        this.spawnText(target.x, target.y - 44, `抵达 ${target.label} · 驻守 ${this.getCheckpointStopDuration()}s`, "#7df0c0");
        this.emitJokerEvent("checkpoint", { segmentIndex: this.segmentIndex, label: target.label });
      }
    }

    handleSpawnTimers(dt) {
      if (this.currentWave >= GAME_TUNING.waves.totalMonsterWaves) return;
      const pressure = this.getSpawnPressure();
      const lateRouteIntensity = this.getLateRouteIntensity();
      const checkpointDefense = this.isCheckpointDefenseActive();
      const checkpointThreat = GAME_TUNING.route.checkpointThreat;
      const lateIntervalMultiplier = 1 - lateRouteIntensity * (1 - GAME_TUNING.route.latePressure.intervalMultiplier);
      const trickleIntervalMultiplier = checkpointDefense ? checkpointThreat.trickleIntervalMultiplier : 1;
      const surgeIntervalMultiplier = checkpointDefense ? checkpointThreat.surgeIntervalMultiplier : 1;
      const ambushIntervalMultiplier = checkpointDefense ? checkpointThreat.ambushIntervalMultiplier : 1;
      this.spawnTimers.trickle -= dt;
      if (this.spawnTimers.trickle <= 0) {
        this.spawnTricklePack();
        this.spawnTimers.trickle = Math.max(
          GAME_TUNING.spawn.trickleMinInterval,
          (rand(...GAME_TUNING.spawn.trickleResetRange) - pressure * GAME_TUNING.spawn.tricklePressureScale) *
            trickleIntervalMultiplier *
            lateIntervalMultiplier,
        );
      }
      this.spawnTimers.surge -= dt;
      if (this.spawnTimers.surge <= 0) {
        this.spawnSurge();
        this.spawnTimers.surge = Math.max(
          GAME_TUNING.spawn.surgeMinInterval,
          (rand(...GAME_TUNING.spawn.surgeResetRange) - pressure * GAME_TUNING.spawn.surgePressureScale) *
            surgeIntervalMultiplier *
            lateIntervalMultiplier,
        );
      }
      this.spawnTimers.ambush -= dt;
      if (this.spawnTimers.ambush <= 0) {
        this.spawnAmbush();
        this.spawnTimers.ambush = Math.max(
          GAME_TUNING.spawn.ambushMinInterval,
          (rand(...GAME_TUNING.spawn.ambushResetRange) - pressure * GAME_TUNING.spawn.ambushPressureScale) *
            ambushIntervalMultiplier *
            lateIntervalMultiplier,
        );
      }
    }

    spawnOpeningWave() {
      if (!this.registerWave("opening")) return;
      this.spawnPack(GAME_TUNING.waves.openingWaveCount, this.pickGateSet());
      this.spawnText(W / 2, 78, "护送开始", "#ffd166");
      this.emitJokerEvent("wave_start", { kind: "opening" });
    }

    registerWave(kind) {
      if (this.currentWave >= GAME_TUNING.waves.totalMonsterWaves) {
        if (kind !== "limit") {
          this.spawnText(W / 2, 86, `${GAME_TUNING.waves.totalMonsterWaves} 波尸潮已全部出完`, "#ffd166");
        }
        return false;
      }
      this.currentWave += 1;
      return true;
    }

    spawnPack(count, gates, forceKind = null) {
      for (let i = 0; i < count; i += 1) {
        const kind = forceKind || this.pickZombieKind();
        this.spawnZombie(kind, gates[i % gates.length]);
      }
    }

    pickGateSet() {
      if (this.segmentIndex <= 0) return [SPAWN_GATES[0], SPAWN_GATES[1], SPAWN_GATES[2], SPAWN_GATES[3]];
      if (this.segmentIndex === 1) return [SPAWN_GATES[0], SPAWN_GATES[1], SPAWN_GATES[4], SPAWN_GATES[5]];
      if (this.segmentIndex === 2) return [SPAWN_GATES[0], SPAWN_GATES[1], SPAWN_GATES[2], SPAWN_GATES[3], SPAWN_GATES[4], SPAWN_GATES[5]];
      return [...SPAWN_GATES];
    }

    pickZombieKind() {
      const progress = this.elapsed / MATCH_DURATION;
      const roll = Math.random();
      if (this.bossSpawned && roll < 0.15) return "elite";
      if (this.segmentIndex >= 3 && progress >= 0.45) {
        if (roll < 0.2) return "walker";
        if (roll < 0.38) return "runner";
        if (roll < 0.6) return "spitter";
        if (roll < 0.82) return "brute";
        return "elite";
      }
      if (progress < 0.28) return roll < 0.7 ? "walker" : "runner";
      if (progress < 0.6) {
        if (roll < 0.45) return "walker";
        if (roll < 0.72) return "runner";
        if (roll < 0.9) return "spitter";
        if (roll < 0.98) return "brute";
        return "elite";
      }
      if (roll < 0.35) return "walker";
      if (roll < 0.58) return "runner";
      if (roll < 0.78) return "spitter";
      if (roll < 0.9) return "brute";
      return "elite";
    }

    spawnTricklePack() {
      if (!this.registerWave("trickle")) return;
      const pressure = this.getSpawnPressure();
      const lateRouteIntensity = this.getLateRouteIntensity();
      const count =
        GAME_TUNING.spawn.trickleBaseCount +
        Math.floor(pressure * GAME_TUNING.spawn.tricklePressureCountScale) +
        Math.floor(lateRouteIntensity * GAME_TUNING.route.latePressure.trickleExtraCount) +
        (Math.random() < GAME_TUNING.spawn.trickleBonusChanceBase + pressure * GAME_TUNING.spawn.trickleBonusChanceScale ? 1 : 0);
      const gates = this.pickGateSet();
      this.spawnPack(count, gates);
      this.spawnCheckpointThreat(gates, 0.35);
      this.emitJokerEvent("wave_start", { kind: "trickle" });
    }

    spawnSurge() {
      if (!this.registerWave("surge")) return;
      const pressure = this.getSpawnPressure();
      const lateRouteIntensity = this.getLateRouteIntensity();
      const gates = this.pickGateSet();
      const count =
        GAME_TUNING.spawn.surgeBaseCount +
        Math.floor(pressure * GAME_TUNING.spawn.surgePressureCountScale) +
        Math.floor(lateRouteIntensity * GAME_TUNING.route.latePressure.surgeExtraCount) +
        Math.floor(Math.random() * GAME_TUNING.spawn.surgeRandomBonusCount);
      this.spawnPack(count, gates);
      if (
        pressure > GAME_TUNING.spawn.surgeEliteUnlockPressure &&
        Math.random() <
          GAME_TUNING.spawn.surgeEliteChanceBase +
            pressure * GAME_TUNING.spawn.surgeEliteChanceScale +
            lateRouteIntensity * GAME_TUNING.route.latePressure.extraEliteChanceBonus
      ) {
        this.spawnZombie("elite", gates[Math.floor(Math.random() * gates.length)]);
      }
      if (lateRouteIntensity > 0.5) {
        this.spawnZombie("elite", gates[Math.floor(Math.random() * gates.length)]);
      }
      this.spawnCheckpointThreat(gates, 1);
      this.spawnText(W / 2, 88, "尸潮加压", "#ff8f8d");
      this.emitJokerEvent("wave_start", { kind: "surge" });
    }

    spawnAmbush() {
      if (!this.registerWave("ambush")) return;
      const pressure = this.getSpawnPressure();
      const lateRouteIntensity = this.getLateRouteIntensity();
      const count =
        GAME_TUNING.spawn.ambushBaseCount +
        Math.floor(pressure * GAME_TUNING.spawn.ambushPressureCountScale) +
        Math.floor(lateRouteIntensity * GAME_TUNING.route.latePressure.ambushExtraCount) +
        Math.floor(Math.random() * GAME_TUNING.spawn.ambushRandomBonusCount);
      const gates = this.pickGateSet();
      this.spawnPack(count, gates);
      if (lateRouteIntensity > 0.35) {
        this.spawnZombie("elite", gates[Math.floor(Math.random() * gates.length)]);
      }
      this.spawnCheckpointThreat(gates, 0.8);
      this.spawnText(rand(160, W - 160), 98, "侧翼围堵", "#ff6575");
      this.emitJokerEvent("wave_start", { kind: "ambush" });
    }

    spawnBoss() {
      this.registerWave("boss");
      this.bossSpawned = true;
      this.spawnZombie("boss", SPAWN_GATES[4], { finalBoss: true });
      this.spawnZombie("elite", SPAWN_GATES[1]);
      this.spawnZombie("elite", SPAWN_GATES[3]);
      this.spawnZombie("brute", SPAWN_GATES[0]);
      this.spawnText(W / 2, 102, "Boss 入场", "#ff6575");
      this.emitJokerEvent("wave_start", { kind: "boss" });
    }

    spawnCheckpointThreat(gates, intensity) {
      if (!this.isCheckpointDefenseActive()) return;
      const checkpointThreat = GAME_TUNING.route.checkpointThreat;
      const lateRouteIntensity = this.getLateRouteIntensity();
      const gate = gates[Math.floor(Math.random() * gates.length)];
      if (Math.random() < (checkpointThreat.extraEliteChance + lateRouteIntensity * GAME_TUNING.route.latePressure.extraEliteChanceBonus) * intensity) {
        this.spawnZombie("elite", gate, { checkpointThreat: true });
      }
      if (lateRouteIntensity > 0.7) {
        this.spawnZombie("elite", gates[Math.floor(Math.random() * gates.length)], { checkpointThreat: true });
      }
      if (
        this.getSpawnPressure() >= checkpointThreat.bossUnlockProgress &&
        !this.finalHold &&
        Math.random() < checkpointThreat.bossChance * intensity
      ) {
        this.spawnZombie("boss", gate, { checkpointThreat: true, finalBoss: false });
        this.spawnText(gate.x, clamp(gate.y, 88, H - 88), "驻点 Boss 突袭", "#ff6575");
      }
    }

    spawnZombie(kind, gate, options = {}) {
      const def = zombieDefs[kind];
      this.zombies.push({
        id: this.nextId += 1,
        kind,
        x: clamp(gate.x + rand(-26, 26), 18, W - 18),
        y: clamp(gate.y + rand(-18, 18), 18, H - 18),
        r: def.radius,
        hp: def.hp,
        maxHp: def.hp,
        speed: def.speed * 1.3 * rand(0.92, 1.06),
        damage: def.damage,
        score: def.score,
        xp: def.xp,
        color: def.color,
        wobbleSeed: Math.random() * 999,
        wobbleRange: rand(8, 20),
        hitFlash: 0,
        checkpointThreat: Boolean(options.checkpointThreat),
        finalBoss: Boolean(options.finalBoss),
        alive: true,
      });
    }

    getSpawnPressure() {
      return clamp(this.elapsed / MATCH_DURATION + this.getLateRouteIntensity() * GAME_TUNING.route.latePressure.pressureBonusScale, 0, 1.45);
    }

    getLateRouteIntensity() {
      const latePressure = GAME_TUNING.route.latePressure;
      if (this.segmentIndex < latePressure.startSegmentIndex && !this.finalHold) return 0;
      let intensity = 0.42 + Math.max(0, this.segmentIndex - latePressure.startSegmentIndex) * latePressure.perSegmentBonus;
      if (this.isCheckpointDefenseActive()) intensity += latePressure.checkpointBonus;
      if (this.finalHold) intensity += latePressure.finalHoldBonus;
      return clamp(intensity, 0, 1.2);
    }

    isCheckpointDefenseActive() {
      return this.checkpointPauseRemaining > 0 && !this.finalHold;
    }

    updateHero(dt) {
      let keyX = 0;
      let keyY = 0;
      if (this.keys.has("a") || this.keys.has("arrowleft")) keyX -= 1;
      if (this.keys.has("d") || this.keys.has("arrowright")) keyX += 1;
      if (this.keys.has("w") || this.keys.has("arrowup")) keyY -= 1;
      if (this.keys.has("s") || this.keys.has("arrowdown")) keyY += 1;
      let moveX = keyX + this.moveStick.x;
      let moveY = keyY + this.moveStick.y;
      if (moveX !== 0 || moveY !== 0) {
        const len = Math.hypot(moveX, moveY) || 1;
        this.hero.x += (moveX / len) * this.hero.speed * dt;
        this.hero.y += (moveY / len) * this.hero.speed * dt;
      }
      this.hero.x = clamp(this.hero.x, EDGE_PADDING, W - EDGE_PADDING);
      this.hero.y = clamp(this.hero.y, EDGE_PADDING, H - EDGE_PADDING);
      const leashDx = this.hero.x - this.escort.x;
      const leashDy = this.hero.y - this.escort.y;
      const leashDistance = Math.hypot(leashDx, leashDy) || 1;
      if (leashDistance > GAME_TUNING.combat.heroMaxEscortDistance) {
        const leashRatio = GAME_TUNING.combat.heroMaxEscortDistance / leashDistance;
        this.hero.x = this.escort.x + leashDx * leashRatio;
        this.hero.y = this.escort.y + leashDy * leashRatio;
      }
      this.hero.fireCd = Math.max(0, this.hero.fireCd - dt);
      if (this.hero.hp < this.hero.maxHp) this.hero.hp = Math.min(this.hero.maxHp, this.hero.hp + dt * 0.8);
      if (this.escort.checkpointHeal > 0 && this.finalHold) this.escort.hp = Math.min(this.escort.maxHp, this.escort.hp + dt * 0.35);
    }

    updateAutoFire() {
      if (this.state !== "playing" || this.hero.fireCd > 0) return;
      const target = this.findTarget();
      if (!target) return;
      const aimPoint = this.getInterceptAimPoint(target);
      const angle = Math.atan2(aimPoint.y - this.hero.y, aimPoint.x - this.hero.x);
      let bullets = this.hero.bulletsPerShot;
      if (this.hero.fissionCharged) {
        bullets += this.hero.fissionShotBonus || 2;
        this.hero.fissionCharged = false;
      }
      const damage = this.hero.damage + this.hero.damageBonus;
      for (let i = 0; i < bullets; i += 1) {
        const offset = (i - (bullets - 1) / 2) * this.hero.spread;
        const launch = angle + offset;
        this.bullets.push({
          x: this.hero.x + Math.cos(launch) * 18,
          y: this.hero.y + Math.sin(launch) * 18,
          vx: Math.cos(launch) * this.hero.bulletSpeed,
          vy: Math.sin(launch) * this.hero.bulletSpeed,
          speed: this.hero.bulletSpeed,
          r: 4,
          damage,
          alive: true,
        });
      }
      const overdriveActive = this.hero.overdriveShotsRemaining > 0;
      this.hero.fireCd = this.hero.fireRate * this.hero.fireRateMult * (overdriveActive ? this.hero.overdriveFireMult || 1 : 1);
      if (this.hero.overdriveEveryShots > 0) {
        this.hero.overdriveCounter = (this.hero.overdriveCounter || 0) + 1;
        if (this.hero.overdriveCounter >= this.hero.overdriveEveryShots) {
          this.hero.overdriveCounter = 0;
          this.hero.overdriveShotsRemaining = this.hero.overdriveBurstShots || 0;
          this.spawnText(this.hero.x, this.hero.y - 32, "过载连射", "#ffcf6e");
        }
      }
      if (overdriveActive) {
        this.hero.overdriveShotsRemaining = Math.max(0, this.hero.overdriveShotsRemaining - 1);
      }
      this.spawnText(this.hero.x, this.hero.y - 18, "开火", "#ffd166");
      this.spawnBurst(this.hero.x, this.hero.y, 10, "#ffad5a");
      this.emitJokerEvent("fire");
    }

    findTarget() {
      return this.findPriorityTarget(this.hero.x, this.hero.y, this.hero.range + this.hero.autoAimRange);
    }

    findPriorityTarget(originX, originY, maxRange) {
      let best = null;
      let bestScore = -Infinity;
      for (const zombie of this.zombies) {
        if (!zombie.alive) continue;
        const heroDist = distance(originX, originY, zombie.x, zombie.y);
        if (heroDist > maxRange) continue;
        const escortDist = distance(this.escort.x, this.escort.y, zombie.x, zombie.y);
        const threat = clamp(1 - escortDist / 280, 0, 1) * 2.2;
        const proximity = clamp(1 - heroDist / maxRange, 0, 1) * 1.5;
        const weight = { walker: 0.2, runner: 0.45, spitter: 0.55, brute: 0.8, elite: 1.1, boss: 1.8 }[zombie.kind] || 0.2;
        const score = threat + proximity + weight;
        if (score > bestScore) {
          best = zombie;
          bestScore = score;
        }
      }
      return best;
    }

    getAimPoint() {
      const target = this.findTarget();
      if (target) return this.getInterceptAimPoint(target);
      return { x: this.escort.x, y: this.escort.y };
    }

    getInterceptAimPoint(target) {
      const velocity = this.getZombieVelocityHint(target);
      const dx = target.x - this.hero.x;
      const dy = target.y - this.hero.y;
      const distanceToTarget = Math.hypot(dx, dy);
      const travelTime = distanceToTarget / Math.max(this.hero.bulletSpeed, 1);
      return {
        x: target.x + velocity.vx * travelTime,
        y: target.y + velocity.vy * travelTime,
      };
    }

    getZombieVelocityHint(zombie) {
      const sway = Math.sin(this.elapsed * 0.9 + zombie.wobbleSeed) * zombie.wobbleRange;
      const escortDist = distance(zombie.x, zombie.y, this.escort.x, this.escort.y);
      const heroDist = distance(zombie.x, zombie.y, this.hero.x, this.hero.y);
      let targetX = this.escort.x;
      let targetY = this.escort.y;
      if (heroDist < escortDist * 0.8) {
        targetX = this.hero.x;
        targetY = this.hero.y;
      }
      const dx = targetX + sway - zombie.x;
      const dy = targetY - zombie.y;
      const len = Math.hypot(dx, dy) || 1;
      const speed = zombie.speed * (zombie.kind === "runner" ? 1.1 : 1);
      return {
        vx: (dx / len) * speed,
        vy: (dy / len) * speed,
      };
    }

    updateBullets(dt) {
      for (const bullet of this.bullets) {
        if (!bullet.alive) continue;
        bullet.x += bullet.vx * dt;
        bullet.y += bullet.vy * dt;
        if (bullet.x < -30 || bullet.x > W + 30 || bullet.y < -30 || bullet.y > H + 30) {
          bullet.alive = false;
          continue;
        }
        let hitZombie = null;
        for (const zombie of this.zombies) {
          if (zombie.alive && distance(bullet.x, bullet.y, zombie.x, zombie.y) <= bullet.r + zombie.r) {
            hitZombie = zombie;
            break;
          }
        }
        if (!hitZombie) continue;
        const heavyTarget = hitZombie.kind === "elite" || hitZombie.kind === "boss";
        const appliedDamage = Math.round(bullet.damage * (heavyTarget ? this.hero.eliteDamageMult || 1 : 1));
        hitZombie.hp -= appliedDamage;
        hitZombie.hitFlash = 0.1;
        bullet.alive = false;
        this.spawnBurst(bullet.x, bullet.y, 8, hitZombie.color);
        this.spawnText(hitZombie.x, hitZombie.y - hitZombie.r - 10, `-${appliedDamage}`, hitZombie.color);
        if (this.hero.impactBurst && heavyTarget) {
          this.spawnBurst(hitZombie.x, hitZombie.y, 12, "#ffd166");
          for (const other of this.zombies) {
            if (other === hitZombie || !other.alive) continue;
            if (distance(hitZombie.x, hitZombie.y, other.x, other.y) > (this.hero.impactBurstRadius || 72)) continue;
            other.hp -= this.hero.impactBurstDamage || 8;
            other.hitFlash = 0.08;
            this.spawnText(other.x, other.y - other.r - 8, `-${this.hero.impactBurstDamage || 8}`, "#ffd166");
            if (other.hp <= 0) this.killZombie(other);
          }
        }
        this.emitJokerEvent("hit", { zombie: hitZombie, bullet });
        if (hitZombie.hp <= 0) this.killZombie(hitZombie);
      }
      this.bullets = this.bullets.filter((bullet) => bullet.alive);
    }

    updateCheckpointPulse(dt) {
      if (this.escort.checkpointPulseDamage <= 0) return;
      this.checkpointPulseCd = Math.max(0, this.checkpointPulseCd - dt);
      if (!this.isCheckpointDefenseActive() || this.checkpointPulseCd > 0) return;
      this.checkpointPulseCd = this.escort.checkpointPulseInterval || 2.4;
      const impacted = this.zombies.filter(
        (zombie) => zombie.alive && distance(this.escort.x, this.escort.y, zombie.x, zombie.y) <= (this.escort.checkpointPulseRadius || 120),
      );
      if (impacted.length === 0) return;
      this.spawnBurst(this.escort.x, this.escort.y, 18, "#7df0c0");
      for (const zombie of impacted) {
        zombie.hp -= this.escort.checkpointPulseDamage;
        zombie.hitFlash = 0.12;
        this.spawnText(zombie.x, zombie.y - zombie.r - 8, `-${this.escort.checkpointPulseDamage}`, "#7df0c0");
        if (zombie.hp <= 0) this.killZombie(zombie);
      }
      if (this.escort.checkpointPulseHeal > 0) {
        this.escort.hp = Math.min(this.escort.maxHp, this.escort.hp + this.escort.checkpointPulseHeal);
      }
    }

    updateZombies(dt) {
      for (const zombie of this.zombies) {
        if (!zombie.alive) continue;
        zombie.hitFlash = Math.max(0, zombie.hitFlash - dt);
        const sway = Math.sin(this.elapsed * 0.9 + zombie.wobbleSeed) * zombie.wobbleRange;
        const escortDist = distance(zombie.x, zombie.y, this.escort.x, this.escort.y);
        const heroDist = distance(zombie.x, zombie.y, this.hero.x, this.hero.y);
        let targetX = this.escort.x;
        let targetY = this.escort.y;
        if (heroDist < escortDist * 0.8) {
          targetX = this.hero.x;
          targetY = this.hero.y;
        }
        const dx = targetX + sway - zombie.x;
        const dy = targetY - zombie.y;
        const len = Math.hypot(dx, dy) || 1;
        const speed = zombie.speed * (zombie.kind === "runner" ? 1.1 : 1);
        zombie.x += (dx / len) * speed * dt;
        zombie.y += (dy / len) * speed * dt;
        if (heroDist < zombie.r + this.hero.r + 4) {
          this.hero.hp -= zombie.damage * dt * 0.7;
          this.spawnText(this.hero.x, this.hero.y - 20, `-${Math.ceil(zombie.damage * dt * 0.7)}`, "#ff6575");
        }
        if (escortDist < zombie.r + this.escort.r + 6) {
          this.escort.hp -= zombie.damage * dt * 1.25;
          this.spawnText(this.escort.x, this.escort.y - 26, `-${Math.ceil(zombie.damage * dt * 1.25)}`, "#ff6575");
          this.emitJokerEvent("escort_damage", { zombie });
        }
        if (zombie.y > H + 70 || zombie.x < -70 || zombie.x > W + 70) zombie.alive = false;
      }
      this.zombies = this.zombies.filter((zombie) => zombie.alive);
    }

    killZombie(zombie) {
      if (!zombie.alive) return;
      zombie.alive = false;
      this.kills += 1;
      this.score += zombie.score;
      this.xp += zombie.xp;
      let awardedCharge = 0;
      while (this.kills >= this.nextChoiceKillTarget) {
        this.upgradeCharge += 1;
        awardedCharge += 1;
        this.choiceReasonQueue.push(`击杀达到 ${this.kills}`);
        this.advanceChoiceKillTarget();
      }
      if (awardedCharge > 0) {
        this.spawnText(W / 2, 86, `击杀达标，获得 ${awardedCharge} 次抽牌`, "#7df0c0");
      }
      this.emitJokerEvent(zombie.kind === "boss" ? "boss_kill" : "kill", { zombie });
      if (this.hero.chainBurst) {
        for (const other of this.zombies) {
          if (other === zombie || !other.alive) continue;
          if (distance(zombie.x, zombie.y, other.x, other.y) <= (this.hero.chainBurstRadius || 84)) {
            const damage = this.hero.chainBurstDamage || 8;
            other.hp -= damage;
            this.spawnText(other.x, other.y - other.r - 8, `-${damage}`, "#7df0c0");
            if (other.hp <= 0) other.alive = false;
          }
        }
      }
      if (this.hero.panicBlast && this.escort.hp < this.escort.maxHp * (this.hero.panicBlastThreshold || 0.4)) {
        this.hero.panicBlast = false;
        this.spawnBurst(this.escort.x, this.escort.y, 26, "#ffd166");
        for (const other of this.zombies) {
          if (other.alive && distance(this.escort.x, this.escort.y, other.x, other.y) <= 130) {
            other.hp -= 18;
            this.spawnText(other.x, other.y - other.r - 8, "-18", "#ffd166");
            if (other.hp <= 0) other.alive = false;
          }
        }
      }
      if ((zombie.kind === "elite" || zombie.kind === "boss") && this.hero.bountyNeed > 0) {
        this.hero.bountyCounter = (this.hero.bountyCounter || 0) + 1;
        if (this.hero.bountyCounter >= this.hero.bountyNeed) {
          this.hero.bountyCounter = 0;
          this.upgradeCharge += 1;
          this.choiceReasonQueue.push("赏金兑现");
          this.rerollCharges = Math.min(4, this.rerollCharges + 1);
          this.spawnText(W / 2, 68, "赏金兑现 · 获得抽牌与重抽", "#ffd166");
        }
      }
      if (zombie.kind === "boss" && zombie.finalBoss) {
        this.bossKilled = true;
        this.spawnText(W / 2, 112, "Boss 被击穿", "#ffd166");
      } else if (zombie.kind === "boss") {
        this.spawnText(zombie.x, zombie.y - zombie.r - 18, "驻点 Boss 清除", "#ffd166");
      }
      this.spawnBurst(zombie.x, zombie.y, zombie.kind === "boss" ? 30 : 14, zombie.color);
      this.spawnText(zombie.x, zombie.y - zombie.r - 10, `+${zombie.score}`, "#7df0c0");
      this.zombies = this.zombies.filter((item) => item.alive);
      if (this.hero.fissionKillsNeeded > 0) {
        this.hero.fissionKillCounter = (this.hero.fissionKillCounter || 0) + 1;
        if (this.hero.fissionKillCounter >= this.hero.fissionKillsNeeded) {
          this.hero.fissionKillCounter = 0;
          this.hero.fissionCharged = true;
          this.spawnText(this.hero.x, this.hero.y - 30, "裂变已蓄能", "#ffcf6e");
        }
      }
    }

    triggerChoice(reason) {
      if (this.jokerCards.length >= this.jokerSlots) {
        this.upgradeCharge = 0;
        this.spawnText(W / 2, 86, "牌组已满", "#ffd166");
        return;
      }
      const available = shuffle(jokerPool.filter((upgrade) => !this.upgradesTaken.has(upgrade.id) && upgrade.condition(this)));
      if (available.length === 0) {
        this.upgradeCharge = 0;
        return;
      }
      this.state = "choice";
      this.pendingChoices = this.pickChoiceSet(available, 3).map((choice) => this.decorateChoice(choice));
      this.nextChoiceReason = reason;
      this.nextChoiceSubtitle = reason.includes("路口") || reason.includes("广场") || reason.includes("安全区") ? "路段抽牌" : "战斗抽牌";
      const focusTag = this.getDominantTag();
      if (this.dupChoiceBonus > 0 && focusTag) {
        const focusPool = available.filter((choice) => choice.tag === focusTag);
        if (focusPool.length > 0) {
          const focus = this.decorateChoice(focusPool[0]);
          focus.isMirror = true;
          focus.id = `mirror_${focus.id}_${this.nextId}`;
          focus.title = `镜像回响 · ${focus.title}`;
          focus.description = `强化你当前最成型的 ${focusTag} 路线，直接让一张同类牌 +1 级。`;
          focus.rarity = "legendary";
          this.pendingChoices.push(focus);
        }
      }
      this.renderUpgradeChoices();
      showOverlay(ui.upgradeOverlay);
      ui.upgradeEyebrow.textContent = "抽小丑牌";
      ui.upgradeTitle.textContent = "从牌堆里挑出一条更像样的成长路线";
      ui.upgradeSubtitle.textContent = `${this.nextChoiceSubtitle} · 击杀越快，抽牌节奏就越快。`;
      ui.mode.textContent = "抽牌中";
    }

    rerollChoices() {
      if (this.state !== "choice" || this.rerollCharges <= 0) return;
      this.rerollCharges -= 1;
      const exclude = new Set(this.pendingChoices.map((choice) => choice.id));
      const available = shuffle(jokerPool.filter((upgrade) => !this.upgradesTaken.has(upgrade.id) && upgrade.condition(this) && !exclude.has(upgrade.id)));
      this.pendingChoices = this.pickChoiceSet(available, 3).map((choice) => this.decorateChoice(choice));
      this.renderUpgradeChoices();
      this.spawnText(W / 2, 88, "重抽", "#7df0c0");
      updateHud(this);
    }

    skipChoice() {
      if (this.state !== "choice") return;
      this.pendingChoices = [];
      this.escort.hp = Math.min(this.escort.maxHp, this.escort.hp + 18);
      this.rerollCharges = Math.min(3, this.rerollCharges + 1);
      this.state = "playing";
      hideOverlay(ui.upgradeOverlay);
      this.spawnText(W / 2, 90, "跳过并修整", "#ffd166");
      updateHud(this);
    }

    chooseUpgrade(id) {
      if (this.state !== "choice") return;
      const selected = this.pendingChoices.find((choice) => choice.id === id);
      if (!selected) return;
      if (selected.isMirror) {
        const target = this.getPreferredUpgradeTarget(selected.tag);
        if (target) {
          target.level = Math.min(target.maxLevel, target.level + 1);
          target.xp = 0;
          target.xpNeed = this.getCardXpNeed(target);
          this.spawnText(W / 2, 90, `${target.title} +1 级`, "#7df0c0");
          this.rebuildLoadout();
        }
      } else {
        this.upgradesTaken.add(selected.id);
        this.jokerCards.push(this.createJokerCard(selected));
        this.spawnText(W / 2, 90, selected.title, "#7df0c0");
        this.rebuildLoadout();
      }
      this.pendingChoices = [];
      this.state = "playing";
      hideOverlay(ui.upgradeOverlay);
      updateHud(this);
    }

    renderUpgradeChoices() {
      renderChoiceGrid(this.pendingChoices);
    }

    rebuildLoadout() {
      const heroSnapshot = this.hero
        ? {
            x: this.hero.x,
            y: this.hero.y,
            hp: this.hero.hp,
            fireCd: this.hero.fireCd,
          }
        : null;
      const escortSnapshot = this.escort
        ? {
            x: this.escort.x,
            y: this.escort.y,
            hp: this.escort.hp,
          }
        : null;

      this.hero = { ...this.baseHero };
      this.escort = { ...this.baseEscort };

      if (heroSnapshot) {
        this.hero.x = heroSnapshot.x;
        this.hero.y = heroSnapshot.y;
        this.hero.hp = Math.min(this.hero.maxHp, heroSnapshot.hp);
        this.hero.fireCd = heroSnapshot.fireCd;
      }

      if (escortSnapshot) {
        this.escort.x = escortSnapshot.x;
        this.escort.y = escortSnapshot.y;
        this.escort.hp = Math.min(this.escort.maxHp, escortSnapshot.hp);
      }

      this.hero.chainBurstRadius = 84;
      this.hero.chainBurstDamage = 8;
      this.hero.eliteDamageMult = 1;
      this.hero.overdriveEveryShots = 0;
      this.hero.overdriveCounter = 0;
      this.hero.overdriveBurstShots = 0;
      this.hero.overdriveShotsRemaining = 0;
      this.hero.overdriveFireMult = 1;
      this.hero.bountyNeed = 0;
      this.hero.bountyCounter = 0;
      this.hero.impactBurst = false;
      this.hero.impactBurstRadius = 0;
      this.hero.impactBurstDamage = 0;
      this.hero.panicBlastThreshold = 0.4;
      this.hero.fissionKillsNeeded = 0;
      this.hero.fissionKillCounter = 0;
      this.hero.fissionCharged = false;
      this.hero.fissionShotBonus = 0;
      this.escort.checkpointPulseDamage = 0;
      this.escort.checkpointPulseRadius = 0;
      this.escort.checkpointPulseInterval = 0;
      this.escort.checkpointPulseHeal = 0;
      this.dupChoiceBonus = 0;
      for (const card of this.jokerCards) {
        card.xpNeed = this.getCardXpNeed(card);
        card.apply(this, card);
      }
      this.applySynergiesFromCards();
    }

    applySynergiesFromCards() {
      const counts = new Map();
      for (const card of this.jokerCards) {
        counts.set(card.tag, (counts.get(card.tag) || 0) + 1);
      }
      if ((counts.get("攻击") || 0) >= 2) this.hero.damageBonus += 4;
      if ((counts.get("防守") || 0) >= 2) {
        this.escort.maxHp += 25;
        this.escort.hp = Math.min(this.escort.maxHp, this.escort.hp + 25);
      }
      if ((counts.get("节奏") || 0) >= 2) this.hero.fireRateMult *= 0.9;
      if ((counts.get("弹幕") || 0) >= 2) {
        this.hero.bulletsPerShot += 1;
        this.hero.spread += 0.12;
      }
      if ((counts.get("爆发") || 0) >= 2) this.hero.damageBonus += 5;
      if ((counts.get("防守") || 0) >= 3 && this.segmentIndex >= GAME_TUNING.route.latePressure.startSegmentIndex) {
        this.escort.checkpointPulseDamage += 6;
        this.escort.checkpointPulseRadius += 12;
      }
      if (this.jokerCards.length >= 4) {
        this.hero.range += 50;
        this.escort.checkpointHeal += 10;
      }
      if (this.jokerCards.length >= 6) {
        this.hero.damageBonus += 3;
        this.hero.fireRateMult *= 0.95;
      }
      if (this.jokerCards.some((card) => card.id === "mirror_joker")) {
        this.dupChoiceBonus = 1;
      }
    }

    emitJokerEvent(type, payload) {
      const baseGain = { fire: 1, hit: 1, kill: 2, checkpoint: 2, wave_start: 1, escort_damage: 2, boss_kill: 4 }[type] || 0;
      if (baseGain <= 0) return;
      for (const card of this.jokerCards) {
        if (card.level >= card.maxLevel) continue;
        const match = this.getCardEventWeight(card, type, payload);
        if (match <= 0) continue;
        this.gainJokerXp(card, baseGain * match);
      }
    }

    gainJokerXp(card, amount) {
      const rarityMult = { common: 1, uncommon: 1.15, rare: 1.3, legendary: 1.55 }[card.rarity] || 1;
      card.xp += amount * rarityMult;
      while (card.level < card.maxLevel && card.xp >= card.xpNeed) {
        card.xp -= card.xpNeed;
        card.level += 1;
        card.xpNeed = this.getCardXpNeed(card);
        this.spawnText(W / 2, 82, `${card.title} Lv.${card.level}`, "#ffd166");
        this.rebuildLoadout();
      }
    }

    decorateChoice(choice) {
      return { ...choice, rarity: choice.rarity || "common", level: 1 };
    }

    createJokerCard(choice) {
      return {
        id: choice.id,
        title: choice.title,
        rarity: choice.rarity || "common",
        tag: choice.tag || "通用",
        description: choice.description,
        level: 1,
        xp: 0,
        xpNeed: this.getCardXpNeed(choice),
        maxLevel: choice.maxLevel || 3,
        apply: choice.apply,
      };
    }

    getCardXpNeed(card) {
      const base = { common: 3, uncommon: 4, rare: 5, legendary: 6 }[card.rarity || "common"] || 3;
      return base + Math.max(0, (card.level || 1) - 1);
    }

    advanceChoiceKillTarget() {
      this.nextChoiceKillIndex += 1;
      const configuredThreshold = GAME_TUNING.roguelike.killChoiceThresholds[this.nextChoiceKillIndex];
      if (configuredThreshold) {
        this.nextChoiceKillTarget = configuredThreshold;
        return;
      }
      this.nextChoiceKillTarget *= 2;
    }

    getCheckpointStopDuration() {
      return (
        GAME_TUNING.route.checkpointStopBaseDuration +
        Math.max(0, this.segmentIndex - 1) * GAME_TUNING.route.checkpointStopStepDuration
      );
    }

    getCardEventWeight(card, type) {
      const tag = card.tag;
      if (type === "fire" && (tag === "节奏" || tag === "弹幕")) return 1;
      if (type === "hit" && (tag === "弹幕" || tag === "攻击")) return 1;
      if (type === "kill" && (tag === "攻击" || tag === "爆发")) return 1;
      if (type === "checkpoint" && (tag === "防守" || tag === "节奏")) return 1.35;
      if (type === "wave_start" && (tag === "节奏" || tag === "攻击")) return 0.8;
      if (type === "escort_damage" && (tag === "防守" || tag === "爆发")) return 1.3;
      if (type === "boss_kill") return 1.5;
      if (card.id === "fission_joker" && type === "kill") return 1.4;
      if (card.id === "mirror_joker" && type === "checkpoint") return 1;
      return 0.35;
    }

    pickChoiceSet(choices, count) {
      const pool = [...choices];
      const picked = [];
      while (picked.length < count && pool.length > 0) {
        const totalWeight = pool.reduce((sum, choice) => sum + this.getChoiceWeight(choice), 0);
        let roll = Math.random() * totalWeight;
        let index = 0;
        for (; index < pool.length; index += 1) {
          roll -= this.getChoiceWeight(pool[index]);
          if (roll <= 0) break;
        }
        picked.push(pool.splice(Math.min(index, pool.length - 1), 1)[0]);
      }
      return picked;
    }

    getChoiceWeight(choice) {
      const progress = this.elapsed / MATCH_DURATION;
      const rarity = choice.rarity || "common";
      let weight = { common: 6, uncommon: 3, rare: 1.2, legendary: 0.35 }[rarity] || 1;
      if (progress > 0.35) weight *= { common: 0.95, uncommon: 1.05, rare: 1.15, legendary: 1.25 }[rarity] || 1;
      if (progress > 0.65) weight *= { common: 0.8, uncommon: 1, rare: 1.25, legendary: 1.8 }[rarity] || 1;
      if (this.segmentIndex >= GAME_TUNING.route.latePressure.startSegmentIndex) {
        weight *= { common: 0.82, uncommon: 1.08, rare: 1.35, legendary: 1.95 }[rarity] || 1;
      }
      const focusTag = this.getDominantTag();
      if (focusTag && choice.tag === focusTag) weight *= 1.25;
      if (this.escort.hp < this.escort.maxHp * 0.65 && choice.tag === "防守") weight *= 1.2;
      if (this.hero.bulletsPerShot >= 2 && choice.tag === "弹幕") weight *= 1.2;
      return weight;
    }

    getDominantTag() {
      if (this.jokerCards.length === 0) return "";
      const counts = new Map();
      for (const card of this.jokerCards) counts.set(card.tag, (counts.get(card.tag) || 0) + 1);
      let bestTag = "";
      let best = 0;
      for (const [tag, count] of counts.entries()) {
        if (count > best) {
          best = count;
          bestTag = tag;
        }
      }
      return bestTag;
    }

    getPreferredUpgradeTarget(tag) {
      const candidates = this.jokerCards.filter((card) => card.tag === tag && card.level < card.maxLevel);
      candidates.sort((a, b) => {
        if (rarityOrder[b.rarity] !== rarityOrder[a.rarity]) return rarityOrder[b.rarity] - rarityOrder[a.rarity];
        return b.level - a.level;
      });
      return candidates[0] || null;
    }

    getModeText() {
      if (this.state === "start") return "等待开始";
      if (this.checkpointPauseRemaining > 0) return "驻点停留";
      if (this.state === "playing") return "护送中";
      if (this.state === "choice") return "抽牌中";
      if (this.state === "pause") return "暂停";
      if (this.state === "win") return "胜利";
      if (this.state === "lose") return "失败";
      return "等待开始";
    }

    getGoalText() {
      if (this.checkpointPauseRemaining > 0 && this.currentCheckpointName) {
        return `驻守 ${this.currentCheckpointName} ${Math.ceil(this.checkpointPauseRemaining)}s`;
      }
      if (this.finalHold && this.bossSpawned && !this.bossKilled) return "守住安全区前线";
      if (this.finalHold && this.bossKilled) return "等待结算";
      return `护送到 ${this.route[Math.min(this.segmentIndex + 1, this.route.length - 1)].label}`;
    }

    getBuildSummary() {
      const parts = [];
      if (this.jokerCards.length > 0) parts.push(`小丑牌 ${this.jokerCards.length}/${this.jokerSlots}`);
      if (this.jokerCards.some((card) => card.level > 1)) parts.push(`总等级 ${this.jokerCards.reduce((sum, card) => sum + card.level, 0)}`);
      if (this.escort.maxHp > this.baseEscort.maxHp) parts.push(`车体 ${this.escort.maxHp}`);
      if (this.escort.speed > this.baseEscort.speed) parts.push(`推进 ${Math.round((this.escort.speed / this.baseEscort.speed) * 100)}%`);
      if (this.hero.damageBonus > 0) parts.push(`伤害 +${this.hero.damageBonus}`);
      if (this.hero.fireRateMult < 1) parts.push(`连射 ${Math.round((1 / this.hero.fireRateMult) * 100)}%`);
      if (this.hero.bulletsPerShot > 1) parts.push(`散射 x${this.hero.bulletsPerShot}`);
      if (this.hero.eliteDamageMult > 1) parts.push(`处刑 ${Math.round(this.hero.eliteDamageMult * 100)}%`);
      if (this.hero.range > this.baseHero.range) parts.push(`索敌 +${this.hero.range - this.baseHero.range}`);
      if (this.escort.checkpointHeal > this.baseEscort.checkpointHeal) parts.push(`检查点修理 +${this.escort.checkpointHeal - this.baseEscort.checkpointHeal}`);
      if (this.hero.overdriveEveryShots > 0) parts.push("过载连射");
      if (this.hero.bountyNeed > 0) parts.push(`赏金 ${this.hero.bountyNeed} 精英`);
      if (this.hero.impactBurst) parts.push("破片爆裂");
      if (this.escort.checkpointPulseDamage > 0) parts.push("驻点脉冲");
      if (this.hero.chainBurst) parts.push("连锁爆发");
      if (this.hero.panicBlast) parts.push("紧急爆破");
      if (this.rerollCharges > 0) parts.push(`重抽 ${this.rerollCharges}`);
      if (this.upgradeCharge > 0) parts.push(`待抽牌 ${this.upgradeCharge}`);
      parts.push(`下次抽牌 ${this.nextChoiceKillTarget} 杀`);
      return parts.length ? parts.join(" / ") : "基础护送";
    }

    spawnBurst(x, y, count, color) {
      for (let i = 0; i < count; i += 1) {
        const angle = rand(0, Math.PI * 2);
        const speed = rand(50, 220);
        this.particles.push({
          x,
          y,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed,
          life: rand(0.2, 0.55),
          color,
          size: rand(1.4, 3.3),
        });
      }
    }

    spawnText(x, y, text, color) {
      this.texts.push({ x, y, text, color, life: 0.9 });
    }

    updateParticles(dt) {
      for (const particle of this.particles) {
        particle.x += particle.vx * dt;
        particle.y += particle.vy * dt;
        particle.vx *= 0.97;
        particle.vy *= 0.97;
        particle.life -= dt;
      }
      this.particles = this.particles.filter((particle) => particle.life > 0);
    }

    updateTexts(dt) {
      for (const text of this.texts) {
        text.y -= 26 * dt;
        text.life -= dt;
      }
      this.texts = this.texts.filter((text) => text.life > 0);
    }

    updateHintText() {
      let hint = "护送目标会沿路线自动推进，使用 WASD 手动走位，火力会自动锁敌并直线射击。";
      if (this.checkpointPauseRemaining > 0 && this.currentCheckpointName) {
        hint = `车队正在 ${this.currentCheckpointName} 驻守补给，停留 ${Math.ceil(this.checkpointPauseRemaining)} 秒后继续推进。`;
      } else if (this.segmentIndex === 0) hint = "开局先用 WASD 保持站位，角色活动范围会被限制在护送车周围。";
      else if (this.segmentIndex === 1) hint = "中段围堵更密，继续把小丑牌组往一个方向凑成型。";
      else if (this.segmentIndex === 2) hint = "广场和医院街口都在收网，看看牌组能不能顶住后半局。";
      else if (this.segmentIndex >= 3 && !this.finalHold) hint = "第三节点后尸潮会明显提压，精英和驻点抽牌都会变多，尽快把牌组成型。";
      else if (this.finalHold && !this.bossKilled) hint = "安全区前最后一战，先打掉 Boss 再让车队进门。";
      else if (this.finalHold && this.bossKilled) hint = "安全区已经打开，稳住最后几秒就能过关。";
      ui.hintText.textContent = hint;
    }

    togglePause() {
      if (this.state !== "playing" && this.state !== "pause") return;
      if (this.state === "pause") {
        this.state = "playing";
        hideOverlay(ui.pauseOverlay);
      } else {
        this.state = "pause";
        showOverlay(ui.pauseOverlay);
      }
      updateHud(this);
    }

    finish(victory, summary) {
      this.state = victory ? "win" : "lose";
      hideOverlay(ui.pauseOverlay);
      hideOverlay(ui.upgradeOverlay);
      showOverlay(ui.resultOverlay);
      ui.resultTag.textContent = victory ? "突围成功" : "突围失败";
      ui.resultTitle.textContent = victory ? "车队冲出围城" : "车队没能撑到终点";
      ui.resultSummary.textContent = `${summary} 当前小丑牌：${Math.min(this.jokerCards.length, this.jokerSlots)}/${this.jokerSlots}。`;
      ui.mode.textContent = victory ? "胜利" : "失败";
    }

    showStartState() {
      hideOverlay(ui.pauseOverlay);
      hideOverlay(ui.upgradeOverlay);
      hideOverlay(ui.resultOverlay);
      showOverlay(ui.startOverlay);
    }

    render() {
      renderGame(this);
    }
  }

  const game = new Game();
  window.__game = game;
  window.__launchGame = function (button) {
    const startButton = button || document.getElementById("start-button");
    const restartButton = document.getElementById("restart-button");
    try {
      if (startButton) {
        startButton.disabled = false;
        startButton.textContent = startButton.id === "restart-button" ? "再来一局" : "开始试玩";
      }
      if (restartButton && restartButton !== startButton) {
        restartButton.disabled = false;
        restartButton.textContent = "再来一局";
      }
      game.beginRun();
    } catch (error) {
      if (startButton) {
        startButton.disabled = false;
        startButton.textContent = startButton.id === "restart-button" ? "再来一局" : "开始试玩";
      }
      if (restartButton && restartButton !== startButton) {
        restartButton.disabled = false;
        restartButton.textContent = "再来一局";
      }
      const overlay = document.getElementById("start-overlay");
      const card = overlay && overlay.querySelector(".overlay-card");
      if (overlay && card) {
        overlay.classList.remove("hidden");
        const title = card.querySelector("h2");
        const note = card.querySelector("p");
        if (title) title.textContent = "开始试玩失败";
        if (note) note.textContent = error && error.message ? error.message : String(error);
      }
      throw error;
    }
  };

  window.addEventListener("keydown", (event) => {
    const key = event.key.toLowerCase();
    if (key === "p") {
      game.togglePause();
      event.preventDefault();
      return;
    }
    if (key === "r") {
      game.beginRun();
      event.preventDefault();
      return;
    }
    if (["a", "arrowleft", "d", "arrowright", "w", "arrowup", "s", "arrowdown"].includes(key)) {
      game.keys.add(key);
    }
  });

  window.addEventListener("keyup", (event) => {
    game.keys.delete(event.key.toLowerCase());
  });

  window.addEventListener("blur", () => {
    game.keys.clear();
    clearDirectionalKeys();
  });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      game.keys.clear();
      clearDirectionalKeys();
    }
  });

  canvas.addEventListener("pointermove", (event) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    game.pointer.x = (event.clientX - rect.left) * scaleX;
    game.pointer.y = (event.clientY - rect.top) * scaleY;
    game.pointer.active = true;
    updateHud(game);
  });

  canvas.addEventListener("pointerdown", (event) => {
    if (game.state === "start") {
      window.__launchGame();
      return;
    }
    event.preventDefault();
  });

  ui.choiceGrid.addEventListener("click", (event) => {
    const card = event.target.closest("[data-upgrade]");
    if (!card) return;
    game.chooseUpgrade(card.dataset.upgrade);
  });

  if (ui.rerollButton) {
    ui.rerollButton.addEventListener("click", () => game.rerollChoices());
  }

  if (ui.skipButton) {
    ui.skipButton.addEventListener("click", () => game.skipChoice());
  }

  function updateJoystickFromEvent(event) {
    if (!ui.joystick) return;
    const rect = ui.joystick.getBoundingClientRect();
    const radius = rect.width * 0.5;
    const thumbRadius = rect.width * 0.2;
    const centerX = rect.left + rect.width * 0.5;
    const centerY = rect.top + rect.height * 0.5;
    const dx = event.clientX - centerX;
    const dy = event.clientY - centerY;
    const distanceToCenter = Math.hypot(dx, dy) || 1;
    const maxDistance = Math.max(12, radius - thumbRadius);
    const clampedDistance = Math.min(distanceToCenter, maxDistance);
    const normalizedX = (dx / distanceToCenter) * (clampedDistance / maxDistance);
    const normalizedY = (dy / distanceToCenter) * (clampedDistance / maxDistance);

    game.moveStick.x = normalizedX;
    game.moveStick.y = normalizedY;
    if (ui.joystickThumb) {
      ui.joystickThumb.style.transform = `translate3d(${normalizedX * maxDistance}px, ${normalizedY * maxDistance}px, 0px)`;
    }
  }

  function releaseJoystick() {
    clearDirectionalKeys();
  }

  if (ui.joystick) {
    ui.joystick.addEventListener("pointerdown", (event) => {
      event.preventDefault();
      game.moveStick.active = true;
      game.moveStick.pointerId = event.pointerId;
      ui.joystick.classList.add("is-active");
      ui.joystick.setPointerCapture(event.pointerId);
      updateJoystickFromEvent(event);
    });

    ui.joystick.addEventListener("pointermove", (event) => {
      if (!game.moveStick.active || game.moveStick.pointerId !== event.pointerId) return;
      event.preventDefault();
      updateJoystickFromEvent(event);
    });

    const endJoystick = (event) => {
      if (!game.moveStick.active) return;
      if (event && game.moveStick.pointerId !== null && event.pointerId !== game.moveStick.pointerId) return;
      if (event) event.preventDefault();
      releaseJoystick();
    };

    ui.joystick.addEventListener("pointerup", endJoystick);
    ui.joystick.addEventListener("pointercancel", endJoystick);
    ui.joystick.addEventListener("lostpointercapture", endJoystick);
  }

  game.start();
}());
