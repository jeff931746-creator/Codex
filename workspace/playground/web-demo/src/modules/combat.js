import { H, HERO_LEASH, W } from "../config.js";
import { distance } from "../utils.js";

export const combatMethods = {
  updateHero(dt) {
    let moveX = 0;
    let moveY = 0;
    if (this.keys.has("a") || this.keys.has("arrowleft")) moveX -= 1;
    if (this.keys.has("d") || this.keys.has("arrowright")) moveX += 1;
    if (this.keys.has("w") || this.keys.has("arrowup")) moveY -= 1;
    if (this.keys.has("s") || this.keys.has("arrowdown")) moveY += 1;

    if (moveX !== 0 || moveY !== 0) {
      const len = Math.hypot(moveX, moveY) || 1;
      this.hero.x += (moveX / len) * this.hero.speed * dt;
      this.hero.y += (moveY / len) * this.hero.speed * dt;
    } else {
      const target = this.pointer.active
        ? this.pointer
        : { x: this.escort.x + 82, y: this.escort.y + 30 };
      const dx = target.x - this.hero.x;
      const dy = target.y - this.hero.y;
      const dist = Math.hypot(dx, dy) || 1;
      const step = Math.min(dist, this.hero.speed * 0.6 * dt);
      this.hero.x += (dx / dist) * step;
      this.hero.y += (dy / dist) * step;
    }

    const leashDx = this.hero.x - this.escort.x;
    const leashDy = this.hero.y - this.escort.y;
    const leashDist = Math.hypot(leashDx, leashDy) || 1;
    if (leashDist > HERO_LEASH) {
      const pull = (leashDist - HERO_LEASH) * 0.18;
      this.hero.x -= (leashDx / leashDist) * pull;
      this.hero.y -= (leashDy / leashDist) * pull;
    }

    this.hero.x = Math.max(30, Math.min(W - 30, this.hero.x));
    this.hero.y = Math.max(30, Math.min(H - 30, this.hero.y));
    this.hero.fireCd = Math.max(0, this.hero.fireCd - dt);

    if (this.hero.hp < this.hero.maxHp) {
      this.hero.hp = Math.min(this.hero.maxHp, this.hero.hp + dt * 0.8);
    }

    if (this.escort.checkpointHeal > 0 && this.finalHold) {
      this.escort.hp = Math.min(this.escort.maxHp, this.escort.hp + dt * 0.35);
    }
  },

  updateAutoFire() {
    if (this.state !== "playing") return;
    if (this.hero.fireCd > 0) return;

    const target = this.findTarget();
    const angle = Math.atan2(target.y - this.hero.y, target.x - this.hero.x);
    const damage = this.hero.damage + this.hero.damageBonus;
    let bullets = this.hero.bulletsPerShot;
    const spread = this.hero.spread;

    if (this.hero.fissionCharged) {
      bullets += this.hero.fissionShotBonus || 2;
      this.hero.fissionCharged = false;
    }

    for (let i = 0; i < bullets; i += 1) {
      const offset = (i - (bullets - 1) / 2) * spread;
      const launch = angle + offset;
      this.bullets.push({
        id: this.nextId += 1,
        x: this.hero.x + Math.cos(launch) * 18,
        y: this.hero.y + Math.sin(launch) * 18,
        vx: Math.cos(launch) * this.hero.bulletSpeed,
        vy: Math.sin(launch) * this.hero.bulletSpeed,
        r: 4,
        damage,
        pierceLeft: this.hero.pierce,
        alive: true,
      });
    }

    this.hero.fireCd = this.hero.fireRate * this.hero.fireRateMult;
    this.spawnText(this.hero.x, this.hero.y - 18, "开火", "#ffd166");
    this.spawnBurst(this.hero.x, this.hero.y, 10, "#ffad5a");
    if (typeof this.emitJokerEvent === "function") {
      this.emitJokerEvent("fire");
    }
  },

  fire() {},

  findTarget() {
    let best = null;
    let bestDist = Infinity;
    for (const zombie of this.zombies) {
      if (!zombie.alive) continue;
      const d = distance(this.hero.x, this.hero.y, zombie.x, zombie.y);
      if (d < this.hero.range && d < bestDist) {
        best = zombie;
        bestDist = d;
      }
    }

    if (best) return best;
    if (this.pointer.active) return this.pointer;
    return { x: this.escort.x, y: this.escort.y };
  },

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
        if (!zombie.alive) continue;
        if (distance(bullet.x, bullet.y, zombie.x, zombie.y) <= bullet.r + zombie.r) {
          hitZombie = zombie;
          break;
        }
      }

      if (!hitZombie) continue;

      hitZombie.hp -= bullet.damage;
      hitZombie.hitFlash = 0.1;
      bullet.pierceLeft -= 1;
      this.spawnBurst(bullet.x, bullet.y, 8, hitZombie.color);
      this.spawnText(hitZombie.x, hitZombie.y - hitZombie.r - 10, `-${bullet.damage}`, hitZombie.color);
      if (typeof this.emitJokerEvent === "function") {
        this.emitJokerEvent("hit", { zombie: hitZombie, bullet });
      }

      if (hitZombie.hp <= 0) {
        this.killZombie(hitZombie);
      }

      if (bullet.pierceLeft < 0) {
        bullet.alive = false;
      }
    }

    this.bullets = this.bullets.filter((bullet) => bullet.alive);
  },

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
        if (typeof this.emitJokerEvent === "function") {
          this.emitJokerEvent("escort_damage", { zombie });
        }
      }

      if (zombie.y > H + 70 || zombie.x < -70 || zombie.x > W + 70) {
        zombie.alive = false;
      }
    }

    this.zombies = this.zombies.filter((zombie) => zombie.alive);
  },

  killZombie(zombie) {
    if (!zombie.alive) return;
    zombie.alive = false;
    this.kills += 1;
    this.score += zombie.score;
    this.xp += zombie.xp;
    if (zombie.kind === "boss" && typeof this.emitJokerEvent === "function") {
      this.emitJokerEvent("boss_kill", { zombie });
    } else if (typeof this.emitJokerEvent === "function") {
      this.emitJokerEvent("kill", { zombie });
    }

    if (this.hero.chainBurst) {
      for (const other of this.zombies) {
        if (other === zombie || !other.alive) continue;
        const radius = this.hero.chainBurstRadius || 84;
        const damage = this.hero.chainBurstDamage || 8;
        if (distance(zombie.x, zombie.y, other.x, other.y) <= radius) {
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

    if (zombie.kind === "boss") {
      this.bossKilled = true;
      this.spawnText(W / 2, 112, "Boss 被击穿", "#ffd166");
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
  },
};
