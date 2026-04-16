import { MATCH_DURATION, ROUTE, W } from "../config.js";
import { rand } from "../utils.js";
import { hideOverlay, showOverlay } from "../ui.js";

export const stateMethods = {
  reset() {
    this.state = "start";
    this.elapsed = 0;
    this.timer = MATCH_DURATION;
    this.segmentIndex = 0;
    this.score = 0;
    this.kills = 0;
    this.xp = 0;
    this.xpNeed = 5;
    this.jokerSlots = 8;
    this.bossSpawned = false;
    this.bossKilled = false;
    this.finalHold = false;
    this.nextChoiceReason = "";
    this.nextChoiceSubtitle = "";
    this.spawnTimers = {
      trickle: rand(0.75, 1.4),
      surge: rand(13, 20),
      ambush: rand(16, 24),
    };
    this.zombies = [];
    this.bullets = [];
    this.particles = [];
    this.texts = [];
    this.jokerCards = [];
    this.jokerSynergyFlags = new Set();
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
    };
    this.baseHero = {
      x: this.route[0].x + 88,
      y: this.route[0].y + 24,
      r: 14,
      hp: 100,
      maxHp: 100,
      speed: 250,
      damage: 14,
      damageBonus: 0,
      fireRate: 0.22,
      fireRateMult: 1,
      fireCd: 0,
      bulletsPerShot: 1,
      spread: 0,
      bulletSpeed: 620,
      pierce: 0,
      range: 320,
      chainBurst: false,
      panicBlast: false,
    };
    this.escort = { ...this.baseEscort };
    this.hero = { ...this.baseHero };
    this.serveHint = "车队会沿路线自动前进，主角会自动射击。";
    this.showStartState();
    this.renderUpgradeChoices();
    if (typeof this.rebuildLoadout === "function") {
      this.rebuildLoadout();
    }
    this.updateJokerRack();
    this.updateHud();
  },

  start() {
    showOverlay(this.ui.startOverlay);
    hideOverlay(this.ui.pauseOverlay);
    hideOverlay(this.ui.upgradeOverlay);
    hideOverlay(this.ui.resultOverlay);
    this.updateHud();
    requestAnimationFrame(this.boundLoop);
  },

  beginRun() {
    this.reset();
    this.state = "playing";
    hideOverlay(this.ui.startOverlay);
    hideOverlay(this.ui.pauseOverlay);
    hideOverlay(this.ui.upgradeOverlay);
    hideOverlay(this.ui.resultOverlay);
    this.spawnOpeningWave();
    this.updateHud();
  },

  loop(time) {
    const dt = Math.min(((time - this.lastTime) || 0) / 1000, 0.033);
    this.lastTime = time;

    if (this.state === "playing") {
      this.update(dt);
    }

    this.render();
    requestAnimationFrame(this.boundLoop);
  },

  update(dt) {
    this.elapsed += dt;
    this.timer = Math.max(0, MATCH_DURATION - this.elapsed);

    this.handleRouteProgress(dt);
    if (this.state !== "playing") {
      this.updateHud();
      return;
    }
    this.handleSpawnTimers(dt);
    this.updateHero(dt);
    this.updateAutoFire(dt);
    this.updateBullets(dt);
    this.updateZombies(dt);
    this.updateParticles(dt);
    this.updateTexts(dt);

    if (this.xp >= this.xpNeed && this.pendingChoices.length === 0) {
      this.triggerChoice("战斗间隙升级");
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
    this.updateHud();
  },

  handleRouteProgress(dt) {
    if (this.finalHold) return;
    if (this.segmentIndex >= this.route.length - 1) return;

    const target = this.route[this.segmentIndex + 1];
    const dx = target.x - this.escort.x;
    const dy = target.y - this.escort.y;
    const dist = Math.hypot(dx, dy) || 1;
    const speed = this.escort.speed;
    const step = Math.min(dist, speed * dt);

    this.escort.x += (dx / dist) * step;
    this.escort.y += (dy / dist) * step;

    if (dist <= 7) {
      this.escort.x = target.x;
      this.escort.y = target.y;

      if (this.segmentIndex + 1 >= this.route.length - 1) {
        this.finalHold = true;
        if (!this.bossSpawned) {
          this.spawnBoss();
        }
        this.spawnText(target.x, target.y - 46, "安全区前最后一战", "#ffcf6e");
        return;
      }

      this.segmentIndex += 1;
      this.escort.hp = Math.min(this.escort.maxHp, this.escort.hp + this.escort.checkpointHeal);
      this.score += 120;
      this.spawnText(target.x, target.y - 44, `抵达 ${target.label}`, "#7df0c0");
      if (typeof this.emitJokerEvent === "function") {
        this.emitJokerEvent("checkpoint", { segmentIndex: this.segmentIndex, label: target.label });
      }
      this.triggerChoice(`抵达 ${target.label}`);
    }
  },

  handleSpawnTimers(dt) {
    this.spawnTimers.trickle -= dt;
    if (this.spawnTimers.trickle <= 0) {
      this.spawnTricklePack();
      const tempo = Math.max(0.72, 1 - this.elapsed / 900);
      this.spawnTimers.trickle = rand(0.95, 1.9) * tempo;
      if (typeof this.emitJokerEvent === "function") {
        this.emitJokerEvent("wave_start", { kind: "trickle" });
      }
    }

    this.spawnTimers.surge -= dt;
    if (this.spawnTimers.surge <= 0) {
      this.spawnSurge();
      this.spawnTimers.surge = rand(15, 22) * Math.max(0.8, 1 - this.elapsed / 1200);
      if (typeof this.emitJokerEvent === "function") {
        this.emitJokerEvent("wave_start", { kind: "surge" });
      }
    }

    this.spawnTimers.ambush -= dt;
    if (this.spawnTimers.ambush <= 0) {
      this.spawnAmbush();
      this.spawnTimers.ambush = rand(20, 30) * Math.max(0.82, 1 - this.elapsed / 1300);
      if (typeof this.emitJokerEvent === "function") {
        this.emitJokerEvent("wave_start", { kind: "ambush" });
      }
    }
  },

  updateHintText() {
    let hint = "护送目标会沿路线自动推进，鼠标或 WASD 控制主角清障。";
    if (this.segmentIndex === 0) {
      hint = "先稳住外环路口，抽到的第一张小丑牌会决定这局的开头方向。";
    } else if (this.segmentIndex === 1) {
      hint = "中段围堵更密，继续把小丑牌组往一个方向凑成型。";
    } else if (this.segmentIndex === 2) {
      hint = "广场和医院街口都在收网，看看牌组能不能顶住后半局。";
    } else if (this.finalHold && !this.bossKilled) {
      hint = "安全区前最后一战，先打掉 Boss 再让车队进门。";
    } else if (this.finalHold && this.bossKilled) {
      hint = "安全区已经打开，稳住最后几秒就能过关。";
    }
    this.ui.hintText.textContent = hint;
  },

  finish(victory, summary) {
    this.state = victory ? "win" : "lose";
    hideOverlay(this.ui.pauseOverlay);
    hideOverlay(this.ui.upgradeOverlay);
    showOverlay(this.ui.resultOverlay);
    this.ui.resultTag.textContent = victory ? "突围成功" : "突围失败";
    this.ui.resultTitle.textContent = victory ? "车队冲出围城" : "车队没能撑到终点";
    this.ui.resultSummary.textContent = `${summary} 当前小丑牌：${Math.min(this.jokerCards.length, this.jokerSlots)}/${this.jokerSlots}。`;
    this.ui.mode.textContent = victory ? "胜利" : "失败";
  },

  togglePause() {
    if (this.state !== "playing" && this.state !== "pause") return;
    if (this.state === "pause") {
      this.state = "playing";
      hideOverlay(this.ui.pauseOverlay);
    } else {
      this.state = "pause";
      showOverlay(this.ui.pauseOverlay);
    }
    this.updateHud();
  },

  showStartState() {
    hideOverlay(this.ui.pauseOverlay);
    hideOverlay(this.ui.upgradeOverlay);
    hideOverlay(this.ui.resultOverlay);
    showOverlay(this.ui.startOverlay);
  },
};

function rand(min, max) {
  return Math.random() * (max - min) + min;
}
