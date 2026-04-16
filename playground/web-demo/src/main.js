import { Game } from "./game.js";
import { ui } from "./ui.js";

const canvas = document.getElementById("game-canvas");
const game = new Game(canvas.getContext("2d"));
window.__game = game;
window.__launchGame = () => {
  try {
    if (!window.__game) {
      throw new Error("游戏脚本还没有加载完成");
    }
    game.beginRun();
    const startButton = document.getElementById("start-button");
    if (startButton) startButton.textContent = "开始试玩";
  } catch (error) {
    const overlay = document.getElementById("start-overlay");
    const card = overlay?.querySelector(".overlay-card");
    if (overlay && card) {
      overlay.classList.remove("hidden");
      const title = card.querySelector("h2");
      const note = card.querySelector("p");
      if (title) title.textContent = "开始试玩失败";
      if (note) note.textContent = error?.message || String(error);
    }
    console.error(error);
    const startButton = document.getElementById("start-button");
    if (startButton) startButton.textContent = "开始试玩";
  }
};

window.addEventListener("error", (event) => {
  const overlay = document.getElementById("start-overlay");
  const card = overlay?.querySelector(".overlay-card");
  if (card) {
    overlay?.classList.remove("hidden");
    card.querySelector("h2").textContent = "脚本启动时出错了";
    const note = card.querySelector("p");
    if (note) {
      note.textContent = event.error ? event.error.message : "请打开控制台查看详细错误。";
    }
  }
});

window.addEventListener("unhandledrejection", (event) => {
  const overlay = document.getElementById("start-overlay");
  const card = overlay?.querySelector(".overlay-card");
  if (card) {
    overlay?.classList.remove("hidden");
    card.querySelector("h2").textContent = "脚本启动时出错了";
    const note = card.querySelector("p");
    if (note) {
      note.textContent = event.reason?.message || String(event.reason || "未知错误");
    }
  }
});

function bindEvents() {
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

  canvas.addEventListener("pointermove", (event) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    game.pointer.x = (event.clientX - rect.left) * scaleX;
    game.pointer.y = (event.clientY - rect.top) * scaleY;
    game.pointer.active = true;
    game.updateHud();
  });

  canvas.addEventListener("pointerdown", (event) => {
    if (game.state === "start") {
      game.beginRun();
      return;
    }
    event.preventDefault();
  });

  ui.rerollButton?.addEventListener("click", () => {
    game.rerollChoices();
  });

  ui.skipButton?.addEventListener("click", () => {
    game.skipChoice();
  });

  ui.choiceGrid.addEventListener("click", (event) => {
    const card = event.target.closest("[data-upgrade]");
    if (!card) return;
    game.chooseUpgrade(card.dataset.upgrade);
  });
}

bindEvents();
game.start();
