import { MATCH_DURATION, W, jokerPool } from "../config.js";
import { shuffle } from "../utils.js";
import { hideOverlay, renderChoiceGrid, showOverlay, updateHud as syncHud, updateJokerRack as syncJokerRack } from "../ui.js";

const rarityOrder = {
  common: 0,
  uncommon: 1,
  rare: 2,
  legendary: 3,
};

export const jokerMethods = {
  triggerChoice(reason) {
    if (this.jokerCards.length >= this.jokerSlots) {
      this.xp = 0;
      this.xpNeed = Math.round(this.xpNeed * 1.25 + 1);
      this.spawnText(W / 2, 86, "牌组已满", "#ffd166");
      return;
    }

    const available = shuffle(
      jokerPool.filter((upgrade) => !this.upgradesTaken.has(upgrade.id) && upgrade.condition(this)),
    );

    if (available.length === 0) {
      this.xp = 0;
      this.xpNeed = Math.round(this.xpNeed * 1.25 + 1);
      return;
    }

    this.state = "choice";
    this.pendingChoices = this.pickChoiceSet(available, 3).map((choice) => this.decorateChoice(choice));
    this.nextChoiceReason = reason;
    this.nextChoiceSubtitle = reason.includes("路口") || reason.includes("广场") || reason.includes("安全区")
      ? "路段抽牌"
      : "战斗抽牌";

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
    showOverlay(this.ui.upgradeOverlay);
    this.ui.upgradeEyebrow.textContent = "抽小丑牌";
    this.ui.upgradeTitle.textContent = "从牌堆里挑出一条更像样的成长路线";
    this.ui.upgradeSubtitle.textContent = `${this.nextChoiceSubtitle} · 当前更容易成型的方向会被优先推到眼前。`;
    this.ui.mode.textContent = "抽牌中";
  },

  rerollChoices() {
    if (this.state !== "choice" || this.rerollCharges <= 0) return;
    this.rerollCharges -= 1;
    const exclude = new Set(this.pendingChoices.map((choice) => choice.id));
    const available = shuffle(
      jokerPool.filter((upgrade) => !this.upgradesTaken.has(upgrade.id) && upgrade.condition(this) && !exclude.has(upgrade.id)),
    );
    this.pendingChoices = this.pickChoiceSet(available, 3).map((choice) => this.decorateChoice(choice));
    this.renderUpgradeChoices();
    this.spawnText(W / 2, 88, "重抽", "#7df0c0");
    this.updateHud();
  },

  skipChoice() {
    if (this.state !== "choice") return;
    this.pendingChoices = [];
    this.xp = 0;
    this.xpNeed = Math.round(this.xpNeed * 1.12 + 1);
    this.escort.hp = Math.min(this.escort.maxHp, this.escort.hp + 18);
    this.rerollCharges = Math.min(3, this.rerollCharges + 1);
    this.state = "playing";
    hideOverlay(this.ui.upgradeOverlay);
    this.spawnText(W / 2, 90, "跳过并修整", "#ffd166");
    this.updateHud();
  },

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
      this.upgradesTaken.add(id);
      const card = this.createJokerCard(selected);
      this.jokerCards.push(card);
      this.spawnText(W / 2, 90, selected.title, "#7df0c0");
      this.rebuildLoadout();
    }

    this.pendingChoices = [];
    this.xp = 0;
    this.xpNeed = Math.round(this.xpNeed * 1.18 + 1);
    this.state = "playing";
    hideOverlay(this.ui.upgradeOverlay);
    this.updateJokerRack();
    this.updateHud();
  },

  renderUpgradeChoices() {
    renderChoiceGrid(this.ui, this.pendingChoices);
  },

  updateHud() {
    syncHud(this.ui, this);
    syncJokerRack(this.ui, this);
    if (this.ui.rerollButton) {
      this.ui.rerollButton.textContent = this.rerollCharges > 0 ? `重抽 ${this.rerollCharges} 次` : "重抽已空";
    }
    if (this.ui.skipButton) {
      this.ui.skipButton.textContent = "跳过并修整";
    }
  },

  getModeText() {
    if (this.state === "start") return "等待开始";
    if (this.state === "playing") return "护送中";
    if (this.state === "choice") return "抽牌中";
    if (this.state === "pause") return "暂停";
    if (this.state === "win") return "胜利";
    if (this.state === "lose") return "失败";
    return "等待开始";
  },

  getGoalText() {
    if (this.finalHold && this.bossSpawned && !this.bossKilled) return "守住安全区前线";
    if (this.finalHold && this.bossKilled) return "等待结算";
    return `护送到 ${this.route[Math.min(this.segmentIndex + 1, this.route.length - 1)].label}`;
  },

  getBuildSummary() {
    const parts = [];
    if (this.jokerCards.length > 0) parts.push(`小丑牌 ${this.jokerCards.length}/${this.jokerSlots}`);
    if (this.jokerCards.some((card) => card.level > 1)) {
      const totalLevel = this.jokerCards.reduce((sum, card) => sum + card.level, 0);
      parts.push(`总等级 ${totalLevel}`);
    }
    if (this.escort.maxHp > this.baseEscort.maxHp) parts.push(`车体 ${this.escort.maxHp}`);
    if (this.escort.speed > this.baseEscort.speed) parts.push(`推进 ${Math.round((this.escort.speed / this.baseEscort.speed) * 100)}%`);
    if (this.hero.damageBonus > 0) parts.push(`伤害 +${this.hero.damageBonus}`);
    if (this.hero.fireRateMult < 1) parts.push(`连射 ${Math.round((1 / this.hero.fireRateMult) * 100)}%`);
    if (this.hero.bulletsPerShot > 1) parts.push(`散射 x${this.hero.bulletsPerShot}`);
    if (this.hero.pierce > 0) parts.push(`穿透 ${this.hero.pierce}`);
    if (this.hero.range > this.baseHero.range) parts.push(`索敌 +${this.hero.range - this.baseHero.range}`);
    if (this.escort.checkpointHeal > this.baseEscort.checkpointHeal) parts.push(`检查点修理 +${this.escort.checkpointHeal - this.baseEscort.checkpointHeal}`);
    if (this.hero.chainBurst) parts.push("连锁爆发");
    if (this.hero.panicBlast) parts.push("紧急爆破");
    if (this.rerollCharges > 0) parts.push(`重抽 ${this.rerollCharges}`);
    return parts.length ? parts.join(" / ") : "基础护送";
  },

  updateJokerRack() {
    syncJokerRack(this.ui, this);
  },

  emitJokerEvent(type, payload = {}) {
    const baseGain = {
      fire: 1,
      hit: 1,
      kill: 2,
      checkpoint: 2,
      wave_start: 1,
      escort_damage: 2,
      boss_kill: 4,
    }[type] || 0;

    if (baseGain <= 0) return;

    for (const card of this.jokerCards) {
      if (card.level >= card.maxLevel) continue;
      const match = this.getCardEventWeight(card, type, payload);
      if (match <= 0) continue;
      this.gainJokerXp(card, baseGain * match);
    }
  },

  gainJokerXp(card, amount) {
    const rarityMult = {
      common: 1,
      uncommon: 1.15,
      rare: 1.3,
      legendary: 1.55,
    }[card.rarity] || 1;

    card.xp += amount * rarityMult;
    while (card.level < card.maxLevel && card.xp >= card.xpNeed) {
      card.xp -= card.xpNeed;
      card.level += 1;
      card.xpNeed = this.getCardXpNeed(card);
      this.spawnText(W / 2, 82, `${card.title} Lv.${card.level}`, "#ffd166");
      this.rebuildLoadout();
    }
  },

  rebuildLoadout() {
    if (!this.baseHero || !this.baseEscort) return;

    this.hero = { ...this.baseHero };
    this.escort = { ...this.baseEscort };
    this.hero.chainBurst = false;
    this.hero.panicBlast = false;
    this.hero.fissionKillsNeeded = 0;
    this.hero.fissionKillCounter = 0;
    this.hero.fissionCharged = false;
    this.hero.fissionShotBonus = 0;
    this.hero.chainBurstRadius = 84;
    this.hero.chainBurstDamage = 8;
    this.hero.panicBlastThreshold = 0.4;
    this.dupChoiceBonus = 0;
    this.rerollCharges = this.rerollCharges ?? 1;

    for (const card of this.jokerCards) {
      card.xpNeed = this.getCardXpNeed(card);
      card.apply(this, card);
    }

    this.applySynergiesFromCards();
    this.syncDeckStats();
  },

  applySynergiesFromCards() {
    const counts = new Map();
    for (const card of this.jokerCards) {
      counts.set(card.tag, (counts.get(card.tag) || 0) + 1);
    }

    if ((counts.get("攻击") || 0) >= 2) {
      this.hero.damageBonus += 4;
    }

    if ((counts.get("防守") || 0) >= 2) {
      this.escort.maxHp += 25;
      this.escort.hp = Math.min(this.escort.maxHp, this.escort.hp + 25);
    }

    if ((counts.get("节奏") || 0) >= 2) {
      this.hero.fireRateMult *= 0.9;
    }

    if ((counts.get("弹幕") || 0) >= 2) {
      this.hero.bulletsPerShot += 1;
      this.hero.spread += 0.12;
    }

    if ((counts.get("爆发") || 0) >= 2) {
      this.hero.pierce += 1;
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
  },

  syncDeckStats() {
    this.ui.buildText.textContent = this.getBuildSummary();
    this.ui.buildPill.textContent = this.getBuildSummary();
  },

  decorateChoice(choice) {
    return {
      ...choice,
      rarity: choice.rarity || "common",
      level: 1,
    };
  },

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
  },

  getCardXpNeed(card) {
    const base = {
      common: 3,
      uncommon: 4,
      rare: 5,
      legendary: 6,
    }[card.rarity || "common"] || 3;
    return base + Math.max(0, card.level - 1);
  },

  getCardEventWeight(card, type, payload) {
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
  },

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
  },

  getChoiceWeight(choice) {
    const progress = this.elapsed / MATCH_DURATION;
    const rarity = choice.rarity || "common";
    let weight = {
      common: 6,
      uncommon: 3,
      rare: 1.2,
      legendary: 0.35,
    }[rarity] || 1;

    if (progress > 0.35) {
      weight *= {
        common: 0.95,
        uncommon: 1.05,
        rare: 1.15,
        legendary: 1.25,
      }[rarity] || 1;
    }

    if (progress > 0.65) {
      weight *= {
        common: 0.8,
        uncommon: 1,
        rare: 1.25,
        legendary: 1.8,
      }[rarity] || 1;
    }

    const focusTag = this.getDominantTag();
    if (focusTag && choice.tag === focusTag) {
      weight *= 1.25;
    }

    if (this.escort.hp < this.escort.maxHp * 0.65 && choice.tag === "防守") {
      weight *= 1.2;
    }

    if (this.hero.bulletsPerShot >= 2 && choice.tag === "弹幕") {
      weight *= 1.2;
    }

    return weight;
  },

  getDominantTag() {
    if (this.jokerCards.length === 0) return "";
    const counts = new Map();
    for (const card of this.jokerCards) {
      counts.set(card.tag, (counts.get(card.tag) || 0) + 1);
    }
    let bestTag = "";
    let best = 0;
    for (const [tag, count] of counts.entries()) {
      if (count > best) {
        best = count;
        bestTag = tag;
      }
    }
    return bestTag;
  },

  getPreferredUpgradeTarget(tag) {
    const candidates = this.jokerCards.filter((card) => card.tag === tag && card.level < card.maxLevel);
    candidates.sort((a, b) => {
      if (rarityOrder[b.rarity] !== rarityOrder[a.rarity]) {
        return rarityOrder[b.rarity] - rarityOrder[a.rarity];
      }
      return b.level - a.level;
    });
    return candidates[0] || null;
  },

  applyJokerSynergies() {
    this.rebuildLoadout();
  },
};
