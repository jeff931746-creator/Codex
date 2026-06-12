const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const coinsEl = document.getElementById("coins");
const enemyHudEl = document.getElementById("enemyHud");
const timerEl = document.getElementById("timer");
const overlay = document.getElementById("overlay");
const resultKicker = document.getElementById("resultKicker");
const resultTitle = document.getElementById("resultTitle");
const resultCopy = document.getElementById("resultCopy");
const restartButton = document.getElementById("restartButton");
const incomeStat = document.getElementById("incomeStat");
const mineStat = document.getElementById("mineStat");
const campStat = document.getElementById("campStat");

const OWNER = { neutral: 0, player: 1, enemy: 2 };
const CONTENT = {
  empty: "empty",
  hq: "hq",
  mine: "mine",
  barracks: "barracks",
};

const CONFIG = {
  cols: 7,
  rows: 12,
  playerHq: "3,10",
  enemyHq: "3,1",
  startingCoins: 35,
  enemyStartingCoins: 35,
  hqIncome: 2.2,
  mineIncome: 1.45,
  enemyFlipDelay: 3.8,
  enemyFlipInterval: 6.4,
  hqSpawnInterval: 4.8,
  barracksSpawnInterval: 3.8,
  maxUnitsPerSide: 14,
  unit: {
    hp: 22,
    damage: 1.4,
    speed: 23,
    range: 21,
    attackInterval: 1.0,
    repathInterval: 0.38,
  },
  buildingDefense: {
    [CONTENT.hq]: { range: 74, damage: 3.2, interval: 0.75, contactDamage: 1.2 },
    [CONTENT.barracks]: { range: 54, damage: 1.8, interval: 1.0, contactDamage: 0.7 },
    [CONTENT.mine]: { range: 42, damage: 1.0, interval: 1.3, contactDamage: 0.4 },
  },
};

const COLORS = {
  player: "#86d95d",
  playerDark: "#2c8b4d",
  playerDim: "#527849",
  enemy: "#e34d63",
  enemyDark: "#9a2d44",
  enemyDim: "#81414c",
  hiddenPlayer: "#6fb452",
  hiddenEnemy: "#b64d5c",
  neutral: "#6f8757",
  water: "#43b7d7",
  gold: "#ffd166",
  ink: "#172126",
};

const CONTENT_LABEL = {
  [CONTENT.empty]: "",
  [CONTENT.hq]: "HQ",
  [CONTENT.mine]: "MINE",
  [CONTENT.barracks]: "BAR",
};

const state = {
  cells: [],
  cellMap: new Map(),
  units: [],
  particles: [],
  connected: {
    [OWNER.player]: new Set(),
    [OWNER.enemy]: new Set(),
  },
  hex: 25,
  originY: 76,
  coins: CONFIG.startingCoins,
  enemyCoins: CONFIG.enemyStartingCoins,
  elapsed: 0,
  lastTime: 0,
  gameOver: false,
  enemyFlipClock: CONFIG.enemyFlipDelay,
  hqSpawnClock: {
    [OWNER.player]: 1.0,
    [OWNER.enemy]: 1.0,
  },
  tileClicks: 0,
  enemyFlips: 0,
  firstUnitTime: null,
  notice: "",
  noticeTime: 0,
};

function key(c, r) {
  return `${c},${r}`;
}

function cellAt(c, r) {
  return state.cellMap.get(key(c, r));
}

function hqKey(owner) {
  return owner === OWNER.player ? CONFIG.playerHq : CONFIG.enemyHq;
}

function hqCell(owner) {
  return state.cellMap.get(hqKey(owner));
}

function otherOwner(owner) {
  return owner === OWNER.player ? OWNER.enemy : OWNER.player;
}

function ownerName(owner) {
  return owner === OWNER.player ? "player" : "enemy";
}

function ownerColor(owner, dim = false) {
  if (owner === OWNER.player) return dim ? COLORS.playerDim : COLORS.player;
  if (owner === OWNER.enemy) return dim ? COLORS.enemyDim : COLORS.enemy;
  return COLORS.neutral;
}

function ownerDark(owner) {
  return owner === OWNER.player ? COLORS.playerDark : COLORS.enemyDark;
}

function isWater(c, r) {
  return new Set([
    key(5, 4),
    key(6, 4),
    key(4, 5),
    key(5, 5),
    key(6, 5),
    key(4, 6),
    key(5, 6),
    key(6, 6),
    key(5, 7),
  ]).has(key(c, r));
}

function trimmedCell(c, r) {
  return (r === 0 || r === CONFIG.rows - 1) && (c < 1 || c > 5);
}

function initialOwner(c, r) {
  if (r <= 5) return OWNER.enemy;
  if (r >= 6) return OWNER.player;
  return OWNER.neutral;
}

function initialRevealedKeys(owner) {
  const player = [
    "3,10",
    "2,10",
    "4,10",
    "3,9",
    "2,9",
    "4,9",
    "3,8",
    "3,7",
    "3,6",
  ];
  const enemy = [
    "3,1",
    "2,1",
    "4,1",
    "3,2",
    "2,2",
    "4,2",
    "3,3",
    "3,4",
    "3,5",
  ];
  return new Set(owner === OWNER.player ? player : enemy);
}

function seededContent(cell, owner) {
  const playerSeeds = {
    "1,9": CONTENT.barracks,
    "2,8": CONTENT.empty,
    "4,8": CONTENT.mine,
    "5,9": CONTENT.empty,
    "2,7": CONTENT.mine,
    "4,7": CONTENT.barracks,
    "3,6": CONTENT.empty,
    "2,6": CONTENT.empty,
    "4,6": CONTENT.mine,
  };
  const enemySeeds = {
    "1,2": CONTENT.barracks,
    "2,3": CONTENT.empty,
    "4,3": CONTENT.mine,
    "5,2": CONTENT.empty,
    "2,4": CONTENT.mine,
    "4,4": CONTENT.barracks,
    "3,5": CONTENT.empty,
    "2,5": CONTENT.empty,
    "4,5": CONTENT.mine,
  };
  const seeded = owner === OWNER.player ? playerSeeds[cell.key] : enemySeeds[cell.key];
  if (seeded) return seeded;

  const value = hashCell(cell.key, owner);
  if (value % 7 === 0) return CONTENT.barracks;
  if (value % 5 === 0) return CONTENT.mine;
  return CONTENT.empty;
}

function hashCell(cellKey, owner) {
  let hash = owner * 37;
  for (let i = 0; i < cellKey.length; i += 1) {
    hash = (hash * 31 + cellKey.charCodeAt(i)) % 9973;
  }
  return hash;
}

function distanceToHq(cell, owner) {
  const [hc, hr] = hqKey(owner).split(",").map(Number);
  return Math.abs(cell.c - hc) + Math.abs(cell.r - hr);
}

function costForCell(cell, owner) {
  const content = seededContent(cell, owner);
  const contentBonus = content === CONTENT.barracks ? 10 : content === CONTENT.mine ? 5 : 0;
  const frontBonus = owner === OWNER.player ? Math.max(0, 9 - cell.r) * 2 : Math.max(0, cell.r - 2) * 2;
  return Math.min(65, 8 + distanceToHq(cell, owner) * 3 + contentBonus + frontBonus);
}

function pixelFromCell(c, r) {
  const size = state.hex;
  const rowWidth = (CONFIG.cols - 1) * size * 1.62 + size * 1.85;
  const rowOffset = r % 2 ? size * 0.81 : 0;
  return {
    x: (canvas.width - rowWidth) / 2 + c * size * 1.62 + rowOffset + size * 0.92,
    y: state.originY + r * size * 1.35,
  };
}

function pointToCell(x, y) {
  let best = null;
  let bestDist = Infinity;
  for (const cell of state.cells) {
    const p = pixelFromCell(cell.c, cell.r);
    const dist = Math.hypot(x - p.x, y - p.y);
    if (dist < bestDist) {
      best = cell;
      bestDist = dist;
    }
  }
  return bestDist <= state.hex * 0.96 ? best : null;
}

function neighbors(cell) {
  const even = cell.r % 2 === 0;
  const dirs = even
    ? [[-1, 0], [1, 0], [0, -1], [-1, -1], [0, 1], [-1, 1]]
    : [[-1, 0], [1, 0], [1, -1], [0, -1], [1, 1], [0, 1]];
  return dirs.map(([dc, dr]) => cellAt(cell.c + dc, cell.r + dr)).filter(Boolean);
}

function makeCell(c, r) {
  const water = isWater(c, r);
  const owner = water ? OWNER.neutral : initialOwner(c, r);
  return {
    c,
    r,
    key: key(c, r),
    water,
    owner,
    revealed: false,
    candidateFor: OWNER.neutral,
    cost: 0,
    content: CONTENT.empty,
    hp: 0,
    maxHp: 0,
    spawnClock: CONFIG.barracksSpawnInterval,
    defenseClock: 0,
    pulse: 0,
  };
}

function buildMap() {
  state.cells = [];
  state.cellMap = new Map();
  state.hex = Math.min(canvas.width / 10.8, canvas.height / 19.5);
  state.originY = 76;

  const playerRevealed = initialRevealedKeys(OWNER.player);
  const enemyRevealed = initialRevealedKeys(OWNER.enemy);

  for (let r = 0; r < CONFIG.rows; r += 1) {
    for (let c = 0; c < CONFIG.cols; c += 1) {
      if (trimmedCell(c, r)) continue;
      const cell = makeCell(c, r);
      if (cell.water) {
        state.cells.push(cell);
        state.cellMap.set(cell.key, cell);
        continue;
      }

      if (cell.key === CONFIG.playerHq || cell.key === CONFIG.enemyHq) {
        cell.revealed = true;
        cell.owner = cell.key === CONFIG.playerHq ? OWNER.player : OWNER.enemy;
        cell.content = CONTENT.hq;
        cell.maxHp = 360;
        cell.hp = cell.maxHp;
      } else if (playerRevealed.has(cell.key)) {
        cell.revealed = true;
        cell.owner = OWNER.player;
        cell.content = CONTENT.empty;
      } else if (enemyRevealed.has(cell.key)) {
        cell.revealed = true;
        cell.owner = OWNER.enemy;
        cell.content = CONTENT.empty;
      }

      state.cells.push(cell);
      state.cellMap.set(cell.key, cell);
    }
  }
  refreshConnectivityAndCandidates();
}

function resetGame() {
  state.units = [];
  state.particles = [];
  state.coins = CONFIG.startingCoins;
  state.enemyCoins = CONFIG.enemyStartingCoins;
  state.elapsed = 0;
  state.lastTime = performance.now();
  state.gameOver = false;
  state.enemyFlipClock = CONFIG.enemyFlipDelay;
  state.hqSpawnClock[OWNER.player] = 1.0;
  state.hqSpawnClock[OWNER.enemy] = 1.0;
  state.tileClicks = 0;
  state.enemyFlips = 0;
  state.firstUnitTime = null;
  state.notice = "";
  state.noticeTime = 0;
  overlay.classList.add("hidden");
  buildMap();
  updateUi();
}

function isConnectedTile(cell, owner) {
  return cell && !cell.water && cell.revealed && cell.owner === owner;
}

function connectedSet(owner) {
  const root = hqCell(owner);
  const visited = new Set();
  if (!isConnectedTile(root, owner)) return visited;

  const queue = [root];
  visited.add(root.key);
  while (queue.length) {
    const cell = queue.shift();
    for (const next of neighbors(cell)) {
      if (visited.has(next.key) || !isConnectedTile(next, owner)) continue;
      visited.add(next.key);
      queue.push(next);
    }
  }
  return visited;
}

function closerOwnerForCandidate(cell, currentOwner, incomingOwner) {
  const currentDistance = distanceToHq(cell, currentOwner);
  const incomingDistance = distanceToHq(cell, incomingOwner);
  if (incomingDistance === currentDistance) return cell.owner || currentOwner;
  return incomingDistance < currentDistance ? incomingOwner : currentOwner;
}

function assignCandidate(cell, owner) {
  if (cell.water || cell.revealed) return;
  if (cell.candidateFor === OWNER.neutral) {
    cell.candidateFor = owner;
  } else if (cell.candidateFor !== owner) {
    cell.candidateFor = closerOwnerForCandidate(cell, cell.candidateFor, owner);
  }
  cell.cost = costForCell(cell, cell.candidateFor);
}

function refreshConnectivityAndCandidates() {
  for (const cell of state.cells) {
    cell.candidateFor = OWNER.neutral;
    cell.cost = 0;
  }

  state.connected[OWNER.player] = connectedSet(OWNER.player);
  state.connected[OWNER.enemy] = connectedSet(OWNER.enemy);

  for (const owner of [OWNER.player, OWNER.enemy]) {
    for (const cellKey of state.connected[owner]) {
      const cell = state.cellMap.get(cellKey);
      for (const next of neighbors(cell)) assignCandidate(next, owner);
    }
  }
}

function revealedCells(owner = null) {
  return state.cells.filter((cell) => cell.revealed && !cell.water && (owner === null || cell.owner === owner));
}

function candidateCells(owner) {
  return state.cells.filter((cell) => !cell.revealed && !cell.water && cell.candidateFor === owner);
}

function buildingCells(owner, content = null) {
  return state.cells.filter((cell) => (
    cell.revealed
    && !cell.water
    && cell.owner === owner
    && [CONTENT.hq, CONTENT.mine, CONTENT.barracks].includes(cell.content)
    && (!content || cell.content === content)
  ));
}

function sideUnitCount(owner) {
  return state.units.filter((unit) => unit.owner === owner).length;
}

function incomePerSecond(owner) {
  const hq = hqCell(owner);
  const hqIncome = hq && hq.hp > 0 && hq.owner === owner ? CONFIG.hqIncome : 0;
  return hqIncome + buildingCells(owner, CONTENT.mine).length * CONFIG.mineIncome;
}

function wallet(owner) {
  return owner === OWNER.player ? state.coins : state.enemyCoins;
}

function spendCoins(owner, amount) {
  if (owner === OWNER.player) state.coins -= amount;
  else state.enemyCoins -= amount;
}

function addCoins(owner, amount) {
  if (owner === OWNER.player) state.coins += amount;
  else state.enemyCoins += amount;
}

function revealCandidate(cell, owner) {
  if (!cell || cell.water || cell.revealed || state.gameOver) return false;
  if (cell.candidateFor !== owner) {
    if (owner === OWNER.player) flashNotice("Not connected");
    return false;
  }
  if (wallet(owner) < cell.cost) {
    if (owner === OWNER.player) flashNotice("Need coins");
    return false;
  }

  spendCoins(owner, cell.cost);
  const content = seededContent(cell, owner);
  cell.revealed = true;
  cell.owner = owner;
  cell.content = content;
  cell.candidateFor = OWNER.neutral;
  cell.pulse = 0.75;
  if (content === CONTENT.mine) {
    cell.maxHp = 36;
    cell.hp = cell.maxHp;
    cell.defenseClock = 0.35;
  } else if (content === CONTENT.barracks) {
    cell.maxHp = 48;
    cell.hp = cell.maxHp;
    cell.spawnClock = 1.0;
    cell.defenseClock = 0.2;
  } else {
    cell.maxHp = 0;
    cell.hp = 0;
  }

  if (owner === OWNER.player) state.tileClicks += 1;
  else state.enemyFlips += 1;

  const p = pixelFromCell(cell.c, cell.r);
  const label = content === CONTENT.empty ? "OPEN" : CONTENT_LABEL[content];
  floatingText(p.x, p.y - 20, label, owner === OWNER.player ? "#fff4a7" : "#ffd3dd");
  burst(p.x, p.y, owner === OWNER.player ? "#fff5a4" : "#ff9aac", 10);
  refreshConnectivityAndCandidates();
  return true;
}

function autoRevealEnemy(dt) {
  state.enemyFlipClock -= dt;
  if (state.enemyFlipClock > 0) return;

  const affordable = candidateCells(OWNER.enemy)
    .filter((cell) => state.enemyCoins >= cell.cost)
    .sort((a, b) => enemyCandidateScore(b) - enemyCandidateScore(a));

  if (affordable.length) revealCandidate(affordable[0], OWNER.enemy);
  state.enemyFlipClock = affordable.length ? CONFIG.enemyFlipInterval : 1.0;
}

function enemyCandidateScore(cell) {
  const content = seededContent(cell, OWNER.enemy);
  const contentScore = content === CONTENT.barracks ? 45 : content === CONTENT.mine ? 38 : 16;
  const towardPlayer = 20 - distanceToHq(cell, OWNER.player);
  const cheap = 40 - cell.cost;
  const hasBarracks = buildingCells(OWNER.enemy, CONTENT.barracks).length > 0;
  const hasMines = buildingCells(OWNER.enemy, CONTENT.mine).length > 0;
  const needBonus = (!hasBarracks && content === CONTENT.barracks ? 30 : 0)
    + (!hasMines && content === CONTENT.mine ? 20 : 0);
  return contentScore + towardPlayer + cheap * 0.3 + needBonus;
}

function updateEconomy(dt) {
  addCoins(OWNER.player, incomePerSecond(OWNER.player) * dt);
  addCoins(OWNER.enemy, incomePerSecond(OWNER.enemy) * dt);

  for (const cell of state.cells) cell.pulse = Math.max(0, cell.pulse - dt);
  state.noticeTime = Math.max(0, state.noticeTime - dt);

  autoRevealEnemy(dt);
}

function spawnUnit(owner, sourceCell) {
  if (sideUnitCount(owner) >= CONFIG.maxUnitsPerSide || !sourceCell) return;
  const p = pixelFromCell(sourceCell.c, sourceCell.r);
  state.units.push({
    owner,
    x: p.x + (Math.random() - 0.5) * 9,
    y: p.y + (Math.random() - 0.5) * 9,
    c: sourceCell.c,
    r: sourceCell.r,
    hp: CONFIG.unit.hp,
    maxHp: CONFIG.unit.hp,
    age: 0,
    nearPlayerHqTime: 0,
    attackClock: 0,
    repathClock: 0,
    path: [],
  });
  if (state.firstUnitTime === null) state.firstUnitTime = state.elapsed;
}

function updateSpawning(dt) {
  for (const owner of [OWNER.player, OWNER.enemy]) {
    const hq = hqCell(owner);
    state.hqSpawnClock[owner] -= dt;
    if (hq && hq.owner === owner && hq.hp > 0 && state.hqSpawnClock[owner] <= 0) {
      spawnUnit(owner, hq);
      state.hqSpawnClock[owner] += CONFIG.hqSpawnInterval;
    }

    for (const barracks of buildingCells(owner, CONTENT.barracks)) {
      barracks.spawnClock -= dt;
      if (barracks.spawnClock <= 0) {
        spawnUnit(owner, barracks);
        barracks.spawnClock += CONFIG.barracksSpawnInterval;
      }
    }
  }
}

function nearestEnemyUnitInRange(unit) {
  let target = null;
  let best = Infinity;
  for (const other of state.units) {
    if (other.owner === unit.owner) continue;
    const d = Math.hypot(unit.x - other.x, unit.y - other.y);
    if (d < best) {
      best = d;
      target = other;
    }
  }
  return best <= CONFIG.unit.range ? target : null;
}

function nearbyEnemyBuilding(unit) {
  const enemy = otherOwner(unit.owner);
  const current = cellAt(unit.c, unit.r);
  const candidates = [current, ...neighbors(current || {})]
    .filter((cell) => cell && cell.owner === enemy && [CONTENT.hq, CONTENT.mine, CONTENT.barracks].includes(cell.content));

  let best = null;
  let bestDist = Infinity;
  for (const cell of candidates) {
    const p = pixelFromCell(cell.c, cell.r);
    const d = Math.hypot(unit.x - p.x, unit.y - p.y);
    if (d < bestDist) {
      best = cell;
      bestDist = d;
    }
  }
  return bestDist <= state.hex * 1.18 ? best : null;
}

function attackUnit(attacker, defender) {
  if (attacker.attackClock > 0) return;
  defender.hp -= CONFIG.unit.damage;
  attacker.attackClock = CONFIG.unit.attackInterval;
  burst(defender.x, defender.y, attacker.owner === OWNER.player ? "#f2ffc8" : "#ffd1dc", 3);
}

function attackBuilding(attacker, building) {
  if (attacker.attackClock > 0) return;
  building.hp -= CONFIG.unit.damage;
  const defense = CONFIG.buildingDefense[building.content];
  if (defense && building.hp > 0) attacker.hp -= defense.contactDamage;
  attacker.attackClock = CONFIG.unit.attackInterval;
  const p = pixelFromCell(building.c, building.r);
  burst(p.x, p.y, attacker.owner === OWNER.player ? "#f2ffc8" : "#ffd1dc", 4);

  if (building.hp > 0) return;
  if (building.content === CONTENT.hq) {
    endGame(attacker.owner === OWNER.player);
    return;
  }

  building.owner = attacker.owner;
  building.hp = building.maxHp;
  building.defenseClock = 0.4;
  building.pulse = 0.8;
  refreshConnectivityAndCandidates();
  floatingText(p.x, p.y - 18, "TAKE", attacker.owner === OWNER.player ? "#f5ffc6" : "#ffd1dc");
}

function enemyUnitsInBuildingRange(building, range) {
  const p = pixelFromCell(building.c, building.r);
  const targets = [];
  for (const unit of state.units) {
    if (unit.owner === building.owner || unit.hp <= 0) continue;
    const d = Math.hypot(unit.x - p.x, unit.y - p.y);
    if (d <= range) targets.push({ unit, distance: d });
  }
  targets.sort((a, b) => b.unit.nearPlayerHqTime - a.unit.nearPlayerHqTime || a.distance - b.distance);
  return targets.map((target) => target.unit);
}

function updateBuildingDefense(dt) {
  for (const building of buildingCells(OWNER.player).concat(buildingCells(OWNER.enemy))) {
    const defense = CONFIG.buildingDefense[building.content];
    if (!defense || building.hp <= 0) continue;
    building.defenseClock = Math.max(0, building.defenseClock - dt);
    if (building.defenseClock > 0) continue;

    const targets = enemyUnitsInBuildingRange(building, defense.range);
    if (!targets.length) continue;
    for (const target of targets) target.hp -= defense.damage;
    building.defenseClock = defense.interval;
    const p = pixelFromCell(building.c, building.r);
    const primary = targets[0];
    burst(primary.x, primary.y, building.owner === OWNER.player ? "#f2ffc8" : "#ffd1dc", 5);
    floatingText((p.x + primary.x) / 2, (p.y + primary.y) / 2 - 8, "HIT", building.owner === OWNER.player ? "#f5ffc6" : "#ffd1dc");
  }
}

function passable(cell) {
  return cell && !cell.water && cell.revealed;
}

function findPath(startCell, targetKeys) {
  if (!passable(startCell) || !targetKeys.size) return [];
  const queue = [startCell];
  const visited = new Set([startCell.key]);
  const previous = new Map();
  let found = null;

  while (queue.length) {
    const current = queue.shift();
    if (targetKeys.has(current.key) && current.key !== startCell.key) {
      found = current;
      break;
    }
    for (const next of neighbors(current)) {
      if (!passable(next) || visited.has(next.key)) continue;
      visited.add(next.key);
      previous.set(next.key, current.key);
      queue.push(next);
    }
  }

  if (!found) return [];
  const path = [];
  let cursor = found.key;
  while (cursor && cursor !== startCell.key) {
    const cell = state.cellMap.get(cursor);
    if (cell) path.unshift(cell);
    cursor = previous.get(cursor);
  }
  return path;
}

function fallbackFrontierPath(startCell, owner) {
  const enemy = otherOwner(owner);
  const hq = hqCell(enemy);
  if (!hq) return [];

  const queue = [startCell];
  const visited = new Set([startCell.key]);
  const previous = new Map();
  let best = startCell;
  let bestScore = distanceToHq(startCell, enemy);

  while (queue.length) {
    const current = queue.shift();
    const score = distanceToHq(current, enemy);
    if (score < bestScore) {
      best = current;
      bestScore = score;
    }
    for (const next of neighbors(current)) {
      if (!passable(next) || visited.has(next.key)) continue;
      visited.add(next.key);
      previous.set(next.key, current.key);
      queue.push(next);
    }
  }

  if (best.key === startCell.key) return [];
  const path = [];
  let cursor = best.key;
  while (cursor && cursor !== startCell.key) {
    const cell = state.cellMap.get(cursor);
    if (cell) path.unshift(cell);
    cursor = previous.get(cursor);
  }
  return path;
}

function recalcPath(unit) {
  const start = cellAt(unit.c, unit.r);
  if (!start) {
    unit.path = [];
    return;
  }

  const enemy = otherOwner(unit.owner);
  const targetKeys = new Set();
  for (const other of state.units) {
    if (other.owner !== unit.owner) targetKeys.add(key(other.c, other.r));
  }
  for (const building of buildingCells(enemy)) targetKeys.add(building.key);

  unit.path = findPath(start, targetKeys);
  if (!unit.path.length) unit.path = fallbackFrontierPath(start, unit.owner);
}

function capturePassage(unit, cell) {
  if (!cell || cell.water || !cell.revealed || cell.owner === unit.owner) return;
  if ([CONTENT.hq, CONTENT.mine, CONTENT.barracks].includes(cell.content)) return;
  cell.owner = unit.owner;
  cell.pulse = 0.36;
  refreshConnectivityAndCandidates();
}

function advanceUnit(unit, dt) {
  const enemyUnit = nearestEnemyUnitInRange(unit);
  if (enemyUnit) {
    attackUnit(unit, enemyUnit);
    return;
  }

  const enemyBuilding = nearbyEnemyBuilding(unit);
  if (enemyBuilding) {
    attackBuilding(unit, enemyBuilding);
    return;
  }

  unit.repathClock -= dt;
  if (unit.repathClock <= 0 || !unit.path.length) {
    recalcPath(unit);
    unit.repathClock = CONFIG.unit.repathInterval;
  }

  const target = unit.path[0];
  if (!target) return;
  const p = pixelFromCell(target.c, target.r);
  const dx = p.x - unit.x;
  const dy = p.y - unit.y;
  const dist = Math.hypot(dx, dy);
  const step = CONFIG.unit.speed * dt;
  if (dist <= step) {
    unit.x = p.x;
    unit.y = p.y;
    unit.c = target.c;
    unit.r = target.r;
    capturePassage(unit, target);
    unit.path.shift();
  } else if (dist > 0) {
    unit.x += (dx / dist) * step;
    unit.y += (dy / dist) * step;
  }
}

function isEnemyNearPlayerHq(unit) {
  if (!unit || unit.owner !== OWNER.enemy) return false;
  const hq = hqCell(OWNER.player);
  if (!hq) return false;
  const p = pixelFromCell(hq.c, hq.r);
  return Math.hypot(unit.x - p.x, unit.y - p.y) <= 68;
}

function updateUnits(dt) {
  updateBuildingDefense(dt);

  for (const unit of state.units) {
    unit.age += dt;
    unit.nearPlayerHqTime = isEnemyNearPlayerHq(unit) ? unit.nearPlayerHqTime + dt : 0;
    unit.attackClock = Math.max(0, unit.attackClock - dt);
    advanceUnit(unit, dt);
  }

  state.units = state.units.filter((unit) => {
    if (unit.hp > 0) return true;
    burst(unit.x, unit.y, unit.owner === OWNER.player ? "#f2ffc8" : "#ffd1dc", 6);
    return false;
  });
}

function updateParticles(dt) {
  for (const particle of state.particles) {
    particle.x += particle.vx * dt;
    particle.y += particle.vy * dt;
    particle.life -= dt;
  }
  state.particles = state.particles.filter((particle) => particle.life > 0);
}

function flashNotice(text) {
  state.notice = text;
  state.noticeTime = 1.0;
}

function floatingText(x, y, text, color) {
  state.particles.push({ x, y, text, color, vx: 0, vy: -18, life: 0.9 });
}

function burst(x, y, color, count = 8) {
  for (let i = 0; i < count; i += 1) {
    state.particles.push({
      x,
      y,
      color,
      vx: (Math.random() - 0.5) * 60,
      vy: (Math.random() - 0.5) * 60,
      life: 0.45,
    });
  }
}

function tick(dt) {
  if (!state.gameOver) {
    state.elapsed += dt;
    updateEconomy(dt);
    updateSpawning(dt);
    updateUnits(dt);
    updateParticles(dt);
    updateUi();
  } else {
    updateParticles(dt);
  }
}

function drawRoundRect(x, y, width, height, radius) {
  const r = Math.min(radius, width / 2, height / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + width, y, x + width, y + height, r);
  ctx.arcTo(x + width, y + height, x, y + height, r);
  ctx.arcTo(x, y + height, x, y + height - r, r);
  ctx.arcTo(x, y, x + r, y, r);
  ctx.closePath();
}

function drawHexPath(x, y, size) {
  ctx.beginPath();
  for (let i = 0; i < 6; i += 1) {
    const angle = (Math.PI / 180) * (60 * i - 30);
    const px = x + Math.cos(angle) * size;
    const py = y + Math.sin(angle) * size;
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }
  ctx.closePath();
}

function drawCell(cell) {
  const p = pixelFromCell(cell.c, cell.r);
  ctx.save();
  drawHexPath(p.x, p.y, state.hex - 1);
  if (cell.water) {
    ctx.fillStyle = COLORS.water;
  } else if (cell.revealed) {
    ctx.fillStyle = ownerColor(cell.owner, false);
  } else if (cell.candidateFor !== OWNER.neutral) {
    ctx.fillStyle = cell.candidateFor === OWNER.player ? COLORS.hiddenPlayer : COLORS.hiddenEnemy;
  } else {
    ctx.fillStyle = ownerColor(cell.owner, true);
  }
  ctx.globalAlpha = cell.revealed || cell.water || cell.candidateFor !== OWNER.neutral ? 1 : 0.52;
  ctx.fill();
  ctx.globalAlpha = 1;
  ctx.strokeStyle = cell.water ? "rgba(210,245,255,0.22)" : "rgba(25,35,28,0.36)";
  ctx.lineWidth = 1.1;
  ctx.stroke();

  if (!cell.revealed && cell.candidateFor !== OWNER.neutral) {
    drawCandidateMark(cell, p.x, p.y);
  }

  if (cell.pulse > 0) {
    ctx.globalAlpha = Math.min(0.72, cell.pulse);
    ctx.strokeStyle = "#fff4a8";
    ctx.lineWidth = 3;
    drawHexPath(p.x, p.y, state.hex + cell.pulse * 5);
    ctx.stroke();
  }
  ctx.restore();
}

function drawCandidateMark(cell, x, y) {
  const canPay = wallet(cell.candidateFor) >= cell.cost;
  ctx.save();
  ctx.fillStyle = canPay ? "rgba(255,255,255,0.94)" : "rgba(236,236,229,0.6)";
  ctx.strokeStyle = cell.candidateFor === OWNER.player ? "#fff3a0" : "#ffd1dc";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(x, y - 5, 13, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = COLORS.ink;
  ctx.font = "900 12px system-ui";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("?", x, y - 5);
  ctx.fillStyle = cell.candidateFor === OWNER.player ? "#fff0a8" : "#ffd6df";
  ctx.font = "900 8px system-ui";
  ctx.fillText("FLIP", x, y + 13);
  ctx.fillStyle = COLORS.gold;
  ctx.font = "900 10px system-ui";
  ctx.fillText(String(cell.cost), x, y + 25);
  ctx.restore();
}

function drawConnections(owner) {
  const connected = state.connected[owner];
  ctx.save();
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.strokeStyle = owner === OWNER.player ? "rgba(248,255,218,0.76)" : "rgba(255,220,228,0.72)";
  ctx.lineWidth = 5;
  ctx.beginPath();
  for (const cellKey of connected) {
    const cell = state.cellMap.get(cellKey);
    const a = pixelFromCell(cell.c, cell.r);
    for (const next of neighbors(cell)) {
      if (!connected.has(next.key)) continue;
      if (cell.key > next.key) continue;
      const b = pixelFromCell(next.c, next.r);
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
    }
  }
  ctx.stroke();
  ctx.strokeStyle = "rgba(24,35,30,0.42)";
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.setLineDash([4, 5]);
  ctx.strokeStyle = owner === OWNER.player ? "rgba(255,239,139,0.78)" : "rgba(255,188,203,0.72)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  for (const candidate of candidateCells(owner)) {
    const parent = neighbors(candidate).find((cell) => connected.has(cell.key));
    if (!parent) continue;
    const a = pixelFromCell(parent.c, parent.r);
    const b = pixelFromCell(candidate.c, candidate.r);
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
  }
  ctx.stroke();
  ctx.restore();
}

function drawBuilding(cell) {
  if (!cell || cell.content === CONTENT.empty || !cell.revealed) return;
  const p = pixelFromCell(cell.c, cell.r);
  ctx.save();
  ctx.translate(p.x, p.y);

  if (cell.content === CONTENT.mine) {
    ctx.fillStyle = COLORS.gold;
    ctx.strokeStyle = ownerDark(cell.owner);
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(0, 0, 15, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = "#fff5b6";
    ctx.fillRect(-5, -7, 10, 14);
  } else {
    drawRoundRect(-18, -14, 36, 29, 6);
    ctx.fillStyle = cell.owner === OWNER.player ? "#eef6d8" : "#ffe1e8";
    ctx.strokeStyle = ownerDark(cell.owner);
    ctx.lineWidth = 3;
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = ownerDark(cell.owner);
    ctx.fillRect(-7, -1, 14, 14);
    ctx.fillStyle = COLORS.ink;
    ctx.font = "900 9px system-ui";
    ctx.textAlign = "center";
    ctx.fillText(CONTENT_LABEL[cell.content], 0, -19);
  }

  if (cell.maxHp > 0) {
    ctx.fillStyle = "rgba(0,0,0,0.35)";
    ctx.fillRect(-17, 18, 34, 4);
    ctx.fillStyle = cell.owner === OWNER.player ? "#dcff84" : "#ff91a5";
    ctx.fillRect(-17, 18, 34 * Math.max(0, cell.hp / cell.maxHp), 4);
  }
  ctx.restore();
}

function drawUnits() {
  for (const unit of state.units) {
    ctx.save();
    ctx.translate(unit.x, unit.y);
    ctx.fillStyle = unit.owner === OWNER.player ? "#f5f4dd" : "#252b31";
    ctx.strokeStyle = unit.owner === OWNER.player ? COLORS.playerDark : COLORS.enemyDark;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.arc(0, 0, 6.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = unit.owner === OWNER.player ? "#243025" : "#ffdce5";
    ctx.font = "900 8px system-ui";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("S", 0, 1);
    ctx.fillStyle = "rgba(0,0,0,0.36)";
    ctx.fillRect(-9, -13, 18, 3);
    ctx.fillStyle = unit.owner === OWNER.player ? "#dcff84" : "#ff91a5";
    ctx.fillRect(-9, -13, 18 * Math.max(0, unit.hp / unit.maxHp), 3);
    ctx.restore();
  }
}

function drawParticles() {
  for (const particle of state.particles) {
    ctx.globalAlpha = Math.max(0, Math.min(1, particle.life * 1.8));
    ctx.fillStyle = particle.color;
    if (particle.text) {
      ctx.font = "900 11px system-ui";
      ctx.textAlign = "center";
      ctx.fillText(particle.text, particle.x, particle.y);
    } else {
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, 2.8, 0, Math.PI * 2);
      ctx.fill();
    }
  }
  ctx.globalAlpha = 1;
}

function drawNotice() {
  if (state.noticeTime <= 0) return;
  ctx.fillStyle = "rgba(18,26,29,0.82)";
  drawRoundRect(142, 600, 136, 30, 8);
  ctx.fill();
  ctx.fillStyle = "#ffe2ad";
  ctx.font = "900 12px system-ui";
  ctx.textAlign = "center";
  ctx.fillText(state.notice, canvas.width / 2, 620);
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#182428";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (const cell of state.cells) drawCell(cell);
  drawConnections(OWNER.enemy);
  drawConnections(OWNER.player);
  for (const cell of state.cells) drawBuilding(cell);
  drawUnits();
  drawParticles();
  drawNotice();
}

function hqHp(owner) {
  const hq = hqCell(owner);
  return hq ? hq.hp : 0;
}

function updateUi() {
  coinsEl.textContent = `${Math.floor(state.coins)} · HQ ${Math.max(0, Math.ceil(hqHp(OWNER.player)))}`;
  enemyHudEl.textContent = `${Math.floor(state.enemyCoins)} · HQ ${Math.max(0, Math.ceil(hqHp(OWNER.enemy)))}`;

  const minutes = Math.floor(state.elapsed / 60).toString().padStart(2, "0");
  const seconds = Math.floor(state.elapsed % 60).toString().padStart(2, "0");
  timerEl.textContent = `${minutes}:${seconds}`;

  incomeStat.querySelector("small").textContent = `+${incomePerSecond(OWNER.player).toFixed(1)}/s`;
  mineStat.querySelector("small").textContent = String(buildingCells(OWNER.player, CONTENT.mine).length);
  campStat.querySelector("small").textContent = String(buildingCells(OWNER.player, CONTENT.barracks).length);

  canvas.dataset.coins = String(Math.floor(state.coins));
  canvas.dataset.enemyCoins = String(Math.floor(state.enemyCoins));
  canvas.dataset.playerCandidates = String(candidateCells(OWNER.player).length);
  canvas.dataset.enemyCandidates = String(candidateCells(OWNER.enemy).length);
  canvas.dataset.playerRevealed = String(revealedCells(OWNER.player).length);
  canvas.dataset.enemyRevealed = String(revealedCells(OWNER.enemy).length);
  canvas.dataset.hidden = String(state.cells.filter((cell) => !cell.water && !cell.revealed).length);
  canvas.dataset.playerUnits = String(sideUnitCount(OWNER.player));
  canvas.dataset.enemyUnits = String(sideUnitCount(OWNER.enemy));
  canvas.dataset.enemyNearPlayerHq = String(enemyUnitsNearPlayerHq().count);
  canvas.dataset.oldestEnemyNearPlayerHq = String(enemyUnitsNearPlayerHq().oldest);
  canvas.dataset.firstUnitTime = state.firstUnitTime === null ? "" : state.firstUnitTime.toFixed(1);
  canvas.dataset.tileClicks = String(state.tileClicks);
  canvas.dataset.enemyFlips = String(state.enemyFlips);
  canvas.dataset.pathMode = "revealed-network-bfs";
  canvas.dataset.gameOver = String(state.gameOver);
}

function step(time) {
  const dt = Math.min(0.04, (time - state.lastTime) / 1000 || 0);
  state.lastTime = time;
  tick(dt);
  draw();
}

function frameLoop(time) {
  step(time);
  requestAnimationFrame(frameLoop);
}

function endGame(won) {
  if (state.gameOver) return;
  state.gameOver = true;
  resultKicker.textContent = won ? "Victory" : "Defeat";
  resultTitle.textContent = won ? "Enemy HQ Captured" : "HQ Lost";
  resultCopy.textContent = won
    ? `Opened ${state.tileClicks} connected tiles and broke through the network.`
    : "The enemy network reached your HQ.";
  overlay.classList.remove("hidden");
}

function canvasPoint(event) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: (event.clientX - rect.left) * (canvas.width / rect.width),
    y: (event.clientY - rect.top) * (canvas.height / rect.height),
  };
}

canvas.addEventListener("click", (event) => {
  const point = canvasPoint(event);
  const cell = pointToCell(point.x, point.y);
  if (!cell) return;
  if (cell.candidateFor === OWNER.player) {
    revealCandidate(cell, OWNER.player);
    updateUi();
    draw();
    return;
  }
  if (cell.candidateFor === OWNER.enemy) {
    flashNotice("Enemy tile");
  } else if (cell.revealed) {
    flashNotice(cell.content === CONTENT.empty ? "Opened" : CONTENT_LABEL[cell.content]);
  } else {
    flashNotice("Not connected");
  }
  updateUi();
  draw();
});

restartButton.addEventListener("click", resetGame);

function enemyUnitsNearPlayerHq() {
  const hq = hqCell(OWNER.player);
  if (!hq) return { count: 0, oldest: 0 };
  const p = pixelFromCell(hq.c, hq.r);
  let count = 0;
  let oldest = 0;
  for (const unit of state.units) {
    if (unit.owner !== OWNER.enemy) continue;
    const distance = Math.hypot(unit.x - p.x, unit.y - p.y);
    if (distance > 68) continue;
    count += 1;
    oldest = Math.max(oldest, unit.nearPlayerHqTime);
  }
  return { count, oldest: Number(oldest.toFixed(1)) };
}

window.__pocketGrooveDebug = () => ({
  elapsed: state.elapsed,
  coins: state.coins,
  enemyCoins: state.enemyCoins,
  playerCandidates: candidateCells(OWNER.player).length,
  enemyCandidates: candidateCells(OWNER.enemy).length,
  playerRevealed: revealedCells(OWNER.player).length,
  enemyRevealed: revealedCells(OWNER.enemy).length,
  hidden: state.cells.filter((cell) => !cell.water && !cell.revealed).length,
  playerMines: buildingCells(OWNER.player, CONTENT.mine).length,
  playerBarracks: buildingCells(OWNER.player, CONTENT.barracks).length,
  enemyMines: buildingCells(OWNER.enemy, CONTENT.mine).length,
  enemyBarracks: buildingCells(OWNER.enemy, CONTENT.barracks).length,
  playerUnits: sideUnitCount(OWNER.player),
  enemyUnits: sideUnitCount(OWNER.enemy),
  enemyNearPlayerHq: enemyUnitsNearPlayerHq().count,
  oldestEnemyNearPlayerHq: enemyUnitsNearPlayerHq().oldest,
  firstUnitTime: state.firstUnitTime,
  tileClicks: state.tileClicks,
  enemyFlips: state.enemyFlips,
  pathMode: canvas.dataset.pathMode,
  gameOver: state.gameOver,
});

window.__pocketGrooveTest = {
  clickFirstCandidate() {
    const cell = candidateCells(OWNER.player)[0];
    return revealCandidate(cell, OWNER.player);
  },
  clickCandidate(cellKey) {
    return revealCandidate(state.cellMap.get(cellKey), OWNER.player);
  },
  candidateKeys(owner = "player") {
    const targetOwner = owner === "enemy" ? OWNER.enemy : OWNER.player;
    return candidateCells(targetOwner).map((cell) => cell.key);
  },
  runSeconds(seconds) {
    for (let i = 0; i < seconds * 30; i += 1) tick(1 / 30);
    draw();
    return window.__pocketGrooveDebug();
  },
};

resetGame();
requestAnimationFrame(frameLoop);
