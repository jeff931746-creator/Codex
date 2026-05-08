import { clamp, rand } from "../utils.js";

export const effectMethods = {
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
  },

  spawnText(x, y, text, color) {
    this.texts.push({ x, y, text, color, life: 0.9 });
  },

  updateParticles(dt) {
    for (const particle of this.particles) {
      particle.x += particle.vx * dt;
      particle.y += particle.vy * dt;
      particle.vx *= 0.97;
      particle.vy *= 0.97;
      particle.life -= dt;
    }
    this.particles = this.particles.filter((particle) => particle.life > 0);
  },

  updateTexts(dt) {
    for (const text of this.texts) {
      text.y -= 26 * dt;
      text.life -= dt;
    }
    this.texts = this.texts.filter((text) => text.life > 0);
  },
};
