import { H, MATCH_DURATION, SPAWN_GATES, W, zombieDefs } from "../config.js";
import { rand } from "../utils.js";

export const spawnMethods = {
  spawnOpeningWave() {
    this.spawnPack(3, this.pickGateSet());
    this.spawnText(W / 2, 78, "护送开始", "#ffd166");
    if (typeof this.emitJokerEvent === "function") {
      this.emitJokerEvent("wave_start", { kind: "opening" });
    }
  },

  spawnPack(count, gates, forceKind = null) {
    for (let i = 0; i < count; i += 1) {
      const kind = forceKind || this.pickZombieKind();
      const gate = gates[i % gates.length];
      this.spawnZombie(kind, gate);
    }
  },

  pickGateSet() {
    if (this.segmentIndex <= 0) {
      return [SPAWN_GATES[0], SPAWN_GATES[1], SPAWN_GATES[2], SPAWN_GATES[3]];
    }
    if (this.segmentIndex === 1) {
      return [SPAWN_GATES[0], SPAWN_GATES[1], SPAWN_GATES[4], SPAWN_GATES[5]];
    }
    if (this.segmentIndex === 2) {
      return [SPAWN_GATES[0], SPAWN_GATES[1], SPAWN_GATES[2], SPAWN_GATES[3], SPAWN_GATES[4], SPAWN_GATES[5]];
    }
    return [...SPAWN_GATES];
  },

  pickZombieKind() {
    const progress = this.elapsed / MATCH_DURATION;
    const roll = Math.random();
    if (this.bossSpawned && roll < 0.15) return "elite";
    if (progress < 0.28) {
      return roll < 0.7 ? "walker" : "runner";
    }
    if (progress < 0.6) {
      if (roll < 0.45) return "walker";
      if (roll < 0.72) return "runner";
      if (roll < 0.9) return "spitter";
      return "brute";
    }
    if (roll < 0.35) return "walker";
    if (roll < 0.58) return "runner";
    if (roll < 0.78) return "spitter";
    if (roll < 0.94) return "brute";
    return "elite";
  },

  spawnTricklePack() {
    const gates = this.pickGateSet();
    const count = 1 + Math.floor(Math.random() * 2);
    this.spawnPack(count, gates);
  },

  spawnSurge() {
    const gates = this.pickGateSet();
    const count = 3 + Math.floor(Math.random() * 3);
    this.spawnPack(count, gates);
    if (Math.random() < 0.5) {
      this.spawnZombie("elite", gates[Math.floor(Math.random() * gates.length)]);
    }
    this.spawnText(W / 2, 88, "尸潮加压", "#ff8f8d");
    if (typeof this.emitJokerEvent === "function") {
      this.emitJokerEvent("wave_start", { kind: "surge" });
    }
  },

  spawnAmbush() {
    const gates = this.pickGateSet();
    const count = 2 + Math.floor(Math.random() * 3);
    this.spawnPack(count, gates);
    this.spawnText(rand(160, W - 160), 98, "侧翼围堵", "#ff6575");
    if (typeof this.emitJokerEvent === "function") {
      this.emitJokerEvent("wave_start", { kind: "ambush" });
    }
  },

  spawnBoss() {
    this.bossSpawned = true;
    this.spawnZombie("boss", SPAWN_GATES[4]);
    this.spawnZombie("elite", SPAWN_GATES[1]);
    this.spawnZombie("elite", SPAWN_GATES[3]);
    this.spawnZombie("brute", SPAWN_GATES[0]);
    this.spawnText(W / 2, 102, "Boss 入场", "#ff6575");
    if (typeof this.emitJokerEvent === "function") {
      this.emitJokerEvent("wave_start", { kind: "boss" });
    }
  },

  spawnZombie(kind, gate) {
    const def = zombieDefs[kind];
    const x = Math.max(18, Math.min(W - 18, gate.x + rand(-26, 26)));
    const y = Math.max(18, Math.min(H - 18, gate.y + rand(-18, 18)));
    this.zombies.push({
      id: this.nextId += 1,
      kind,
      label: def.label,
      x,
      y,
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
      alive: true,
      slow: 0,
    });
  },
};
