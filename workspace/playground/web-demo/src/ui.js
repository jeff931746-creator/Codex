import { formatTime } from "./utils.js";

export const ui = {
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
};

export function showOverlay(element) {
  element.classList.remove("hidden");
}

export function hideOverlay(element) {
  element.classList.add("hidden");
}

export function renderChoiceGrid(uiRef, choices) {
  uiRef.choiceGrid.innerHTML = choices
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

export function updateHud(uiRef, game) {
  uiRef.baseHp.textContent = `${Math.max(0, Math.ceil(game.escort.hp))} / ${game.escort.maxHp}`;
  uiRef.timer.textContent = formatTime(game.timer);
  uiRef.wave.textContent = `${Math.min(game.segmentIndex + 1, game.route.length - 1)} / ${game.route.length - 1}`;
  uiRef.score.textContent = `${game.kills}`;
  uiRef.zombiesLeft.textContent = `${game.zombies.length}`;
  uiRef.ballsLeft.textContent = `${game.bullets.length}`;
  uiRef.reload.textContent = game.hero.fireCd > 0 ? `${game.hero.fireCd.toFixed(1)}s` : "Ready";
  uiRef.mode.textContent = game.getModeText();
  uiRef.buildText.textContent = game.getBuildSummary();
  uiRef.buildPill.textContent = game.getBuildSummary();
  uiRef.aimText.textContent = game.state === "start"
    ? "待开始"
    : `主角 ${Math.round(game.hero.x)}, ${Math.round(game.hero.y)}`;
  uiRef.goalPill.textContent = game.getGoalText();
}

export function updateJokerRack(uiRef, game) {
  if (!uiRef.jokerRack) return;

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
  if (html === game.lastJokerRackHtml) return;
  game.lastJokerRackHtml = html;
  uiRef.jokerRack.innerHTML = html;
}
