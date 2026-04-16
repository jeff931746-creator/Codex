import { H, W } from "./config.js";
import { renderGame } from "./render.js";
import { ui } from "./ui.js";
import { stateMethods } from "./modules/state.js";
import { spawnMethods } from "./modules/spawn.js";
import { combatMethods } from "./modules/combat.js";
import { effectMethods } from "./modules/effects.js";
import { jokerMethods } from "./modules/joker.js";

export class Game {
  constructor(ctx) {
    this.ctx = ctx;
    this.boundLoop = (time) => this.loop(time);
    this.lastTime = 0;
    this.nextId = 1;
    this.pointer = { x: W / 2, y: H / 2, active: false };
    this.keys = new Set();
    this.upgradesTaken = new Set();
    this.pendingChoices = [];
    this.ui = ui;
    this.reset();
  }

  render() {
    renderGame(this, this.ctx);
  }
}

Object.assign(Game.prototype, stateMethods, spawnMethods, combatMethods, effectMethods, jokerMethods);
