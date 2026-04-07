const modes = {
  concept: {
    label: "概念出图",
    title: "概念出图模式已启用",
    body: "当前默认流程是 Codex 先写概念，再把 Gemini 图像 prompt 自动准备好。",
  },
  auto: {
    label: "自动分发",
    title: "自动分发已启用",
    body: "系统会先判断这次是否需要豆包补前期发散，还是直接由 Codex 进入概念出图链路。",
  },
  execute: {
    label: "执行优先",
    title: "执行优先模式已启用",
    body: "当前会压缩前置讨论，直接让 Codex 生成概念包和 Gemini 图像 prompt。",
  },
};

const sampleTask = {
  task: "帮我做一个中世纪卡通塔防主视觉概念图。",
  context: "受众是轻度塔防玩家，参考 Clash 风格的明亮卡通感，希望有木质箭塔、石墙关卡、哥布林敌人和晨光氛围。",
  output: "KV 主视觉、可延展成商店图标和宣传海报的画面方向",
};

const taskInput = document.getElementById("task-input");
const contextInput = document.getElementById("context-input");
const outputInput = document.getElementById("output-input");
const routeBadge = document.getElementById("route-badge");
const routeTitle = document.getElementById("route-title");
const routeSummary = document.getElementById("route-summary");
const tags = document.getElementById("tags");
const timeline = document.getElementById("timeline");
const deliverables = document.getElementById("deliverables");
const strategyTitle = document.getElementById("strategy-title");
const strategyBody = document.getElementById("strategy-body");
const doubaoSummary = document.getElementById("doubao-summary");
const geminiSummary = document.getElementById("gemini-summary");
const codexSummary = document.getElementById("codex-summary");
const doubaoPrompt = document.getElementById("doubao-prompt");
const geminiPrompt = document.getElementById("gemini-prompt");
const codexPrompt = document.getElementById("codex-prompt");
const conceptPackage = document.getElementById("concept-package");
const handoffBadge = document.getElementById("handoff-badge");
const handoffSummary = document.getElementById("handoff-summary");
const geminiHandoff = document.getElementById("gemini-handoff");
const automationCommand = document.getElementById("automation-command");

let activeMode = "concept";
let lastPlanText = "";

function inferIntent(task, context, output) {
  const combined = `${task} ${context} ${output}`.toLowerCase();
  const brainstormWords = ["创意", "命名", "风格探索", "方向", "世界观", "包装"];
  const conceptWords = ["主视觉", "概念图", "kv", "海报", "角色", "场景", "图标", "出图"];

  let route = "concept";
  const needsBrainstorm = brainstormWords.some((word) => combined.includes(word));
  const hasImageTarget = conceptWords.some((word) => combined.includes(word));

  if (activeMode === "execute") return "execute";
  if (activeMode === "concept") return "concept";
  if (needsBrainstorm && !hasImageTarget) return "auto";
  return "concept";
}

function renderTags(items) {
  tags.innerHTML = items.map((item) => `<span class="tag">${item}</span>`).join("");
}

function renderTimeline(items) {
  timeline.innerHTML = items
    .map(
      (item) => `
        <article class="timeline-item">
          <h4>${item.title}</h4>
          <p>${item.body}</p>
        </article>
      `,
    )
    .join("");
}

function renderDeliverables(items) {
  deliverables.innerHTML = items
    .map(
      (item) => `
        <article class="deliverable-card">
          <h4>${item.title}</h4>
          <p>${item.body}</p>
        </article>
      `,
    )
    .join("");
}

function renderConceptPackage(pkg) {
  conceptPackage.innerHTML = `
    <article class="concept-item">
      <h4>概念标题</h4>
      <p>${pkg.title}</p>
    </article>
    <article class="concept-item">
      <h4>风格方向</h4>
      <p>${pkg.style}</p>
    </article>
    <article class="concept-item">
      <h4>主体与场景</h4>
      <p>${pkg.subject}</p>
    </article>
    <article class="concept-item">
      <h4>构图</h4>
      <p>${pkg.composition}</p>
    </article>
    <article class="concept-item">
      <h4>色彩氛围</h4>
      <p>${pkg.palette}</p>
    </article>
    <article class="concept-item">
      <h4>限制项</h4>
      <p>${pkg.constraints}</p>
    </article>
  `;
}

function buildConceptPackage(task, context, output) {
  const safeTask = task.trim() || "奇幻题材主视觉概念图";
  const safeContext = context.trim() || "暂无额外材料，请使用明快、清晰、商业化的游戏概念图方向。";
  const safeOutput = output.trim() || "一张可用于概念验证的主视觉";

  return {
    title: `${safeTask.replace(/[。！!?]/g, "")} · 概念包`,
    style: "明亮商业插画、轻卡通奇幻、可用于游戏宣发的主视觉语言",
    subject: `${safeTask}。核心参考信息：${safeContext}`,
    composition: "前景放置辨识度最高的核心单位，中景展开战场层次，背景补充世界观轮廓，整体偏电影式透视。",
    palette: "暖金色晨光 + 高识别度主色块，强调可读性和商店展示效果。",
    constraints: `交付目标：${safeOutput}。避免画面过灰、信息过满、角色比例过写实。`,
  };
}

function buildPrompts(task, context, output, route, pkg) {
  const safeTask = task.trim() || "请生成一套概念出图方案";
  const safeContext = context.trim() || "暂无额外背景材料";
  const safeOutput = output.trim() || "概念图";

  return {
    doubao: `你是创意补强顾问。当前主任务是：${safeTask}\n背景：${safeContext}\n目标：${safeOutput}\n请只在需要拓展风格方向时介入，输出 3 组可供 Codex 继续写成图像 prompt 的风格关键词。`,
    gemini: `请根据 Codex 生成的概念包直接出图。\n概念标题：${pkg.title}\n风格方向：${pkg.style}\n主体与场景：${pkg.subject}\n构图：${pkg.composition}\n色彩氛围：${pkg.palette}\n限制项：${pkg.constraints}\n请生成一张高可读性的游戏主视觉概念图。`,
    codex: `请先为这个需求生成结构化概念创意包，再自动整理成 Gemini 可直接使用的图像 prompt。\n任务：${safeTask}\n背景：${safeContext}\n目标输出：${safeOutput}\n请输出：concept_title、style_direction、subject_scene、composition、palette_mood、negative_constraints、gemini_image_prompt、handoff_steps。`,
  };
}

function buildTimeline(route) {
  if (route === "auto") {
    return [
      { title: "Step 1 · 豆包", body: "先给 Codex 补 2 到 3 个创意方向，避免一上来就把图像概念写死。" },
      { title: "Step 2 · Codex", body: "把选择后的方向整理成结构化概念包，并生成标准化 Gemini 图像 prompt。" },
      { title: "Step 3 · Gemini", body: "接收 Codex 下发内容，直接生成概念图，并作为下一轮修订基础。" },
    ];
  }

  return [
    { title: "Step 1 · Codex", body: "先写概念包，明确风格、主体、构图、色彩和限制项。" },
    { title: "Step 2 · Codex -> Gemini", body: "自动把概念包压缩成 Gemini 图像 prompt，并给出下发动作说明。" },
    { title: "Step 3 · Gemini", body: "使用收到的图像 prompt 生成概念图，如需修订再回流给 Codex。 " },
  ];
}

function buildTags(task, context, output, route) {
  const items = [modes[activeMode].label, `主链路：${modes[route].label}`];
  if (task.trim()) items.push("已填写任务");
  if (context.trim()) items.push("含视觉背景");
  if (output.trim()) items.push(`目标：${output.trim()}`);
  return items.slice(0, 4);
}

function buildDeliverables(pkg) {
  return [
    {
      title: "Codex 概念包",
      body: "包含标题、风格方向、主体场景、构图、色彩和限制项，可作为内部评审输入。",
    },
    {
      title: "Gemini 图像 Prompt",
      body: "由 Codex 自动整理成适合 Gemini 接收的出图指令，减少你手工重写 prompt。",
    },
    {
      title: "自动下发说明",
      body: "页面会同时产出 handoff 文案，方便后续接 Gemini API 或浏览器自动化。",
    },
  ];
}

function buildHandoff(pkg, prompts) {
  return [
    "handoff_status: ready",
    "source_agent: Codex",
    "target_agent: Gemini",
    `concept_title: ${pkg.title}`,
    "",
    "[gemini_image_prompt]",
    prompts.gemini,
    "",
    "[handoff_steps]",
    "1. Codex 完成概念包生成。",
    "2. 系统提取 gemini_image_prompt。",
    "3. 将 prompt 发送给 Gemini 图像入口。",
    "4. Gemini 返回首轮图片，用于继续修订。",
  ].join("\n");
}

function buildAutomationCommand(prompts) {
  const scriptPath = "/Users/mt/Documents/Codex/gemini_web_handoff.sh";
  return [
    "# 推荐：自动打开 Gemini、粘贴并直接提交",
    `cat <<'GEMINI_PROMPT' | zsh ${scriptPath} --submit`,
    prompts.gemini,
    "GEMINI_PROMPT",
    "",
    "# 备用：只粘贴，不自动发送",
    `cat <<'GEMINI_PROMPT' | zsh ${scriptPath}`,
    prompts.gemini,
    "GEMINI_PROMPT",
  ].join("\n");
}

function buildPlanText(task, context, output, route, pkg, prompts, handoffText) {
  return [
    `模式：${modes[activeMode].label}`,
    `主链路：${modes[route].label}`,
    `任务：${task.trim() || "未填写"}`,
    `背景材料：${context.trim() || "未填写"}`,
    `目标输出：${output.trim() || "未填写"}`,
    "",
    "[Codex Concept Package]",
    JSON.stringify(pkg, null, 2),
    "",
    "[Doubao Prompt]",
    prompts.doubao,
    "",
    "[Gemini Prompt]",
    prompts.gemini,
    "",
    "[Codex Prompt]",
    prompts.codex,
    "",
    "[Gemini Handoff]",
    handoffText,
  ].join("\n");
}

function generatePlan() {
  const task = taskInput.value;
  const context = contextInput.value;
  const output = outputInput.value;
  const route = inferIntent(task, context, output);
  const pkg = buildConceptPackage(task, context, output);
  const prompts = buildPrompts(task, context, output, route, pkg);
  const handoffText = buildHandoff(pkg, prompts);
  const automationText = buildAutomationCommand(prompts);

  routeBadge.textContent = modes[route].label;
  routeTitle.textContent =
    route === "auto" ? "这次建议先补一点创意发散" : "这次适合直接进入概念出图链路";
  routeSummary.textContent =
    route === "auto"
      ? "你的需求还带有较强的风格探索成分，最好先让豆包补几组方向，再由 Codex 写成结构化概念，最后交给 Gemini 出图。"
      : "你的需求已经足够明确，最适合让 Codex 直接生成概念包和 Gemini 图像 prompt，再进入自动下发流程。";

  renderTags(buildTags(task, context, output, route));
  renderTimeline(buildTimeline(route));
  renderDeliverables(buildDeliverables(pkg));
  renderConceptPackage(pkg);

  doubaoSummary.textContent =
    route === "auto"
      ? "这次豆包会先补 2 到 3 组风格方向，帮助 Codex 形成更有变化的概念包。"
      : "这次豆包不是主链路，只在你想额外拓展风格方案时再介入。";
  geminiSummary.textContent =
    "Gemini 在这里不负责想概念，而是接收 Codex 已经整理好的图像 prompt，直接出图。";
  codexSummary.textContent =
    "Codex 是这条链路的总控，负责生成概念 JSON、图像 prompt，以及发给 Gemini 的 handoff 内容。";

  doubaoPrompt.textContent = prompts.doubao;
  geminiPrompt.textContent = prompts.gemini;
  codexPrompt.textContent = prompts.codex;

  handoffBadge.textContent = "Ready";
  handoffSummary.textContent = "Codex 已经把概念内容整理成 Gemini 可直接接收的出图指令，下面主命令会自动打开、粘贴并提交到 Gemini。";
  geminiHandoff.textContent = handoffText;
  automationCommand.textContent = automationText;

  lastPlanText = [
    buildPlanText(task, context, output, route, pkg, prompts, handoffText),
    "",
    "[Automation Command]",
    automationText,
  ].join("\n");
}

function setMode(mode) {
  activeMode = mode;
  document.querySelectorAll(".mode-chip").forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === mode);
  });
  strategyTitle.textContent = modes[mode].title;
  strategyBody.textContent = modes[mode].body;
  generatePlan();
}

document.getElementById("mode-list").addEventListener("click", (event) => {
  const button = event.target.closest(".mode-chip");
  if (!button) return;
  setMode(button.dataset.mode);
});

document.getElementById("sample-button").addEventListener("click", () => {
  taskInput.value = sampleTask.task;
  contextInput.value = sampleTask.context;
  outputInput.value = sampleTask.output;
  generatePlan();
});

document.getElementById("run-button").addEventListener("click", () => {
  generatePlan();
});

document.getElementById("copy-button").addEventListener("click", async () => {
  if (!lastPlanText) {
    generatePlan();
  }

  try {
    await navigator.clipboard.writeText(lastPlanText);
    routeBadge.textContent = "已复制";
    window.setTimeout(() => generatePlan(), 1200);
  } catch {
    routeBadge.textContent = "复制失败";
  }
});

generatePlan();
