import { CENTER_X, H, ROAD_LEFT, ROAD_RIGHT, W } from "./config.js";
import { clamp, roundRect } from "./utils.js";

export function renderGame(game, ctx) {
  ctx.clearRect(0, 0, W, H);
  drawBackground(ctx);
  drawRoad(ctx);
  drawSpawnZones(ctx);
  drawRoute(game, ctx);
  drawBullets(game, ctx);
  drawZombies(game, ctx);
  drawEscort(game, ctx);
  drawHero(game, ctx);
  drawParticles(game, ctx);
  drawTexts(game, ctx);
  drawTopBanner(game, ctx);
  drawBottomGuide(ctx);
}

function drawBackground(ctx) {
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

function drawRoad(ctx) {
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

function drawSpawnZones(ctx) {
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

function drawRoute(game, ctx) {
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

function drawEscort(game, ctx) {
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

  drawHealthBar(ctx, game.escort.x, game.escort.y - 40, 74, game.escort.hp / game.escort.maxHp, "#7df0c0");
}

function drawHero(game, ctx) {
  ctx.save();
  const target = game.findTarget();
  const angle = Math.atan2(target.y - game.hero.y, target.x - game.hero.x);
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

  drawHealthBar(ctx, game.hero.x, game.hero.y - 22, 42, game.hero.hp / game.hero.maxHp, "#ffd166");
}

function drawZombies(game, ctx) {
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
    drawHealthBar(ctx, zombie.x, zombie.y - zombie.r - 12, zombie.kind === "boss" ? 88 : 44, zombie.hp / zombie.maxHp, zombie.color);
  }
}

function drawBullets(game, ctx) {
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

function drawParticles(game, ctx) {
  for (const particle of game.particles) {
    ctx.globalAlpha = clamp(particle.life / 0.55, 0, 1);
    ctx.fillStyle = particle.color;
    ctx.beginPath();
    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}

function drawTexts(game, ctx) {
  ctx.textAlign = "center";
  ctx.font = "14px sans-serif";
  for (const text of game.texts) {
    ctx.globalAlpha = clamp(text.life / 0.9, 0, 1);
    ctx.fillStyle = text.color;
    ctx.fillText(text.text, text.x, text.y);
  }
  ctx.globalAlpha = 1;
}

function drawTopBanner(game, ctx) {
  ctx.save();
  ctx.fillStyle = "rgba(255,255,255,0.08)";
  ctx.font = "14px sans-serif";
  ctx.textAlign = "left";
  ctx.fillText("护送目标自动前进，鼠标 / WASD 控制主角走位清障，主角会自动射击", 18, 24);
  ctx.fillStyle = "rgba(255,255,255,0.72)";
  ctx.fillText(`当前 Build：${game.getBuildSummary()}`, 18, 46);
  if (game.finalHold && game.bossSpawned) {
    ctx.fillStyle = "rgba(255, 101, 117, 0.95)";
    ctx.font = "18px sans-serif";
    ctx.fillText("安全区前最终决战", W / 2 - 84, 28);
  }
  ctx.restore();
}

function drawBottomGuide(ctx) {
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

function drawHealthBar(ctx, x, y, width, ratio, color) {
  ctx.fillStyle = "rgba(8, 10, 17, 0.88)";
  ctx.fillRect(x - width / 2, y, width, 6);
  ctx.fillStyle = color;
  ctx.fillRect(x - width / 2, y, width * clamp(ratio, 0, 1), 6);
}

function rand(min, max) {
  return Math.random() * (max - min) + min;
}
