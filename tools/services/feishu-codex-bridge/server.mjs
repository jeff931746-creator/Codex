import http from "node:http";
import { spawnSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import fs from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, URL } from "node:url";

const scriptFile = fileURLToPath(import.meta.url);
const scriptDir = dirname(scriptFile);
const defaultPort = Number(process.env.PORT || 3000);

const config = {
  port: defaultPort,
  host: process.env.HOST || "127.0.0.1",
  feishuAppId: process.env.FEISHU_APP_ID || "",
  feishuAppSecret: process.env.FEISHU_APP_SECRET || "",
  feishuUserAuthAppId:
    process.env.FEISHU_USER_AUTH_APP_ID ||
    process.env.FEISHU_APP_ID ||
    "",
  feishuUserAuthAppSecret:
    process.env.FEISHU_USER_AUTH_APP_SECRET ||
    process.env.FEISHU_APP_SECRET ||
    "",
  feishuVerificationToken: process.env.FEISHU_VERIFICATION_TOKEN || "",
  feishuEventMode: (process.env.FEISHU_EVENT_MODE || "webhook").toLowerCase(),
  feishuReadAccessMode: (process.env.FEISHU_READ_ACCESS_MODE || "tenant").toLowerCase(),
  feishuReplyMode: (process.env.FEISHU_REPLY_MODE || "reply").toLowerCase(),
  feishuBackend: (process.env.FEISHU_BACKEND || "codex").toLowerCase(),
  feishuSessionMapRaw: process.env.FEISHU_SESSION_MAP || "",
  feishuDigestEnabled: String(process.env.FEISHU_DIGEST_ENABLED || "").toLowerCase() !== "0",
  feishuDigestHour: Number(process.env.FEISHU_DIGEST_HOUR || 9),
  feishuDigestMinute: Number(process.env.FEISHU_DIGEST_MINUTE || 0),
  feishuDigestPrefix: process.env.FEISHU_DIGEST_PREFIX || "【自动纪要】",
  feishuDigestMaxMessages: Number(process.env.FEISHU_DIGEST_MAX_MESSAGES || 120),
  feishuDigestTargetChatId: process.env.FEISHU_DIGEST_TARGET_CHAT_ID || "",
  feishuCrossChatMaxChats: Number(process.env.FEISHU_CROSS_CHAT_MAX_CHATS || 30),
  feishuCrossChatMaxMessagesPerChat: Number(process.env.FEISHU_CROSS_CHAT_MAX_MESSAGES_PER_CHAT || 25),
  feishuCrossChatMaxTotalMessages: Number(process.env.FEISHU_CROSS_CHAT_MAX_TOTAL_MESSAGES || 240),
  feishuCrossChatConcurrency: Number(process.env.FEISHU_CROSS_CHAT_CONCURRENCY || 6),
  feishuRunIndicator: String(process.env.FEISHU_RUN_INDICATOR || "").toLowerCase() !== "0",
  feishuRunIndicatorEmojiType: process.env.FEISHU_RUN_INDICATOR_EMOJI_TYPE || "SMILE",
  feishuBotOpenId: process.env.FEISHU_BOT_OPEN_ID || "",
  feishuOwnerOpenId: process.env.FEISHU_OWNER_OPEN_ID || "",
  codexPython: process.env.CODEX_PYTHON_BIN || process.env.PYTHON_BIN || "python3",
  codexBridgeScript:
    process.env.CODEX_DESKTOP_BRIDGE_SCRIPT ||
    "/Users/mt/Documents/Codex/tools/codex-desktop-bridge/codex_desktop_bridge.py",
  codexSessionTarget: process.env.CODEX_SESSION_TARGET || "",
  codexWorkdir:
    process.env.CODEX_BRIDGE_WORKDIR || "/Users/mt/Documents/Codex",
  openaiApiKey: process.env.OPENAI_API_KEY || "",
  openaiModel: process.env.OPENAI_MODEL || "gpt-5-mini",
  siliconflowApiKey: process.env.SILICONFLOW_API_KEY || "",
  siliconflowModel:
    process.env.SILICONFLOW_MODEL || "deepseek-ai/DeepSeek-V3",
  siliconflowBaseUrl:
    process.env.SILICONFLOW_BASE_URL || "https://api.siliconflow.cn/v1",
  anthropicApiKey: process.env.ANTHROPIC_API_KEY || "",
  anthropicModel:
    process.env.ANTHROPIC_MODEL || "claude-3-5-haiku-latest",
  botName: process.env.BOT_NAME || "助手",
  feishuStateFile:
    process.env.FEISHU_STATE_FILE || join(scriptDir, ".state", "chat-state.json"),
  feishuUserTokenFile:
    process.env.FEISHU_USER_TOKEN_FILE || join(scriptDir, ".state", "user-access-token.json"),
  feishuUserAuthRedirectUri:
    process.env.FEISHU_USER_AUTH_REDIRECT_URI ||
    `http://127.0.0.1:${defaultPort}/feishu/auth/callback`,
  feishuUserAuthScope:
    String(
      process.env.FEISHU_USER_AUTH_SCOPE ||
        "im:chat:readonly im:message:readonly im:message.group_msg:get_as_user"
    ).trim(),
  systemPrompt:
    process.env.SYSTEM_PROMPT ||
    "你是一个中文优先、简洁、可靠的助手。优先直接回答；除非用户明确要求，否则不要给出过长步骤。"
};

function resolveBackend() {
  if (config.feishuBackend === "auto") {
    if (config.codexSessionTarget) {
      return "codex";
    }
    if (config.siliconflowApiKey) {
      return "siliconflow";
    }
    if (config.anthropicApiKey) {
      return "anthropic";
    }
    return "openai";
  }
  return config.feishuBackend;
}

const activeBackend = resolveBackend();
const activeModel =
  activeBackend === "anthropic"
    ? config.anthropicModel
    : activeBackend === "siliconflow"
      ? config.siliconflowModel
      : activeBackend === "codex"
        ? config.codexSessionTarget || "(selected Codex session)"
        : config.openaiModel;

function logAnthropicUsage(usage, context = {}) {
  if (!usage || typeof usage !== "object") {
    return;
  }

  const inputTokens = Number(usage.input_tokens ?? 0);
  const outputTokens = Number(usage.output_tokens ?? 0);
  const cacheCreationTokens = Number(usage.cache_creation_input_tokens ?? 0);
  const cacheReadTokens = Number(usage.cache_read_input_tokens ?? 0);
  const payload = {
    backend: "anthropic",
    model: context.model || config.anthropicModel,
    inputTokens,
    outputTokens,
    totalTokens: inputTokens + outputTokens,
    cacheCreationInputTokens: cacheCreationTokens,
    cacheReadInputTokens: cacheReadTokens
  };

  if (context.label) {
    payload.label = context.label;
  }

  console.log("[usage] anthropic", payload);
}

function parseSessionMap(raw) {
  if (!raw.trim()) {
    return {};
  }

  try {
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      throw new Error("FEISHU_SESSION_MAP must be a JSON object.");
    }
    return Object.fromEntries(
      Object.entries(parsed)
        .map(([key, value]) => [String(key).trim(), String(value).trim()])
        .filter(([key, value]) => key && value)
    );
  } catch (error) {
    throw new Error(
      `Invalid FEISHU_SESSION_MAP: ${error instanceof Error ? error.message : String(error)}`
    );
  }
}

let sessionMap;
try {
  sessionMap = parseSessionMap(config.feishuSessionMapRaw);
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}

if (
  !config.feishuAppId ||
  !config.feishuAppSecret ||
  (activeBackend === "openai" && !config.openaiApiKey) ||
  (activeBackend === "siliconflow" && !config.siliconflowApiKey) ||
  (activeBackend === "anthropic" && !config.anthropicApiKey) ||
  (activeBackend === "codex" && !existsSync(config.codexBridgeScript))
) {
  console.error(
    "Missing required env vars. Need FEISHU_APP_ID, FEISHU_APP_SECRET, and the settings required by the selected backend."
  );
  process.exit(1);
}

if (!["codex", "auto", "openai", "anthropic", "siliconflow"].includes(config.feishuBackend)) {
  console.error("FEISHU_BACKEND must be one of: codex, auto, openai, anthropic, siliconflow.");
  process.exit(1);
}

if (!["tenant", "user"].includes(config.feishuReadAccessMode)) {
  console.error("FEISHU_READ_ACCESS_MODE must be one of: tenant, user.");
  process.exit(1);
}

if (!["reply", "summary_only"].includes(config.feishuReplyMode)) {
  console.error("FEISHU_REPLY_MODE must be one of: reply, summary_only.");
  process.exit(1);
}

if (!["webhook", "long_connection", "auto"].includes(config.feishuEventMode)) {
  console.error("FEISHU_EVENT_MODE must be one of: webhook, long_connection, auto.");
  process.exit(1);
}

if (
  Number.isNaN(config.feishuDigestHour) ||
  config.feishuDigestHour < 0 ||
  config.feishuDigestHour > 23 ||
  Number.isNaN(config.feishuDigestMinute) ||
  config.feishuDigestMinute < 0 ||
  config.feishuDigestMinute > 59
) {
  console.error("FEISHU_DIGEST_HOUR must be 0-23 and FEISHU_DIGEST_MINUTE must be 0-59.");
  process.exit(1);
}

if (config.feishuDigestEnabled && !String(config.feishuDigestTargetChatId || "").trim()) {
  console.warn("FEISHU_DIGEST_TARGET_CHAT_ID is empty; digests will not be sent until it is configured.");
}

const processedEvents = new Map();
const chatStates = new Map();
let feishuTenantTokenCache = {
  token: "",
  expiresAt: 0
};
let feishuAppTokenCache = {
  token: "",
  expiresAt: 0
};
let feishuUserAuthAppTokenCache = {
  token: "",
  expiresAt: 0
};
let feishuUserTokenCache = {
  accessToken: "",
  expiresAt: 0,
  refreshToken: "",
  refreshExpiresAt: 0,
  openId: "",
  userId: "",
  name: "",
  tenantKey: "",
  sid: ""
};
let feishuOauthState = {
  value: "",
  expiresAt: 0
};
let feishuWsClient = null;
const feishuIngressState = {
  requestedMode: config.feishuEventMode,
  activeMode: "webhook",
  lastEventAt: 0,
  lastEventId: "",
  lastEventType: "",
  lastEventSource: "",
  lastError: "",
  wsStartedAt: 0
};

function normalizePersistedMessage(record) {
  if (!record || typeof record !== "object") {
    return null;
  }

  const at = Number(record.at || 0);
  const text = String(record.text || "").trim();
  if (!text) {
    return null;
  }

  return {
    at: Number.isFinite(at) && at > 0 ? at : Date.now(),
    sender: String(record.sender || "").trim(),
    text,
    eventId: String(record.eventId || "").trim(),
    messageId: String(record.messageId || "").trim()
  };
}

function normalizePersistedChatState(state) {
  const messages = Array.isArray(state?.messages)
    ? state.messages.map(normalizePersistedMessage).filter(Boolean)
    : [];
  const lastDigestIndex = Math.min(
    messages.length,
    Math.max(0, Number(state?.lastDigestIndex || 0))
  );

  return {
    messages,
    lastDigestIndex,
    lastDigestAt: Math.max(0, Number(state?.lastDigestAt || 0)),
    lastSeenAt: Math.max(0, Number(state?.lastSeenAt || 0)),
    lastSender: String(state?.lastSender || "").trim(),
    lastText: String(state?.lastText || "").trim()
  };
}

function persistChatStates() {
  const payload = {
    updatedAt: new Date().toISOString(),
    chats: Object.fromEntries(
      Array.from(chatStates.entries()).map(([chatId, state]) => [
        chatId,
        normalizePersistedChatState(state)
      ])
    )
  };

  const stateDir = dirname(config.feishuStateFile);
  mkdirSync(stateDir, { recursive: true });
  const tempFile = `${config.feishuStateFile}.tmp`;
  writeFileSync(tempFile, JSON.stringify(payload, null, 2), "utf8");
  renameSync(tempFile, config.feishuStateFile);
}

function loadPersistedChatStates() {
  if (!existsSync(config.feishuStateFile)) {
    return;
  }

  try {
    const raw = readFileSync(config.feishuStateFile, "utf8");
    if (!raw.trim()) {
      return;
    }
    const parsed = JSON.parse(raw);
    const chats = parsed?.chats;
    if (!chats || typeof chats !== "object" || Array.isArray(chats)) {
      return;
    }

    for (const [chatId, state] of Object.entries(chats)) {
      const normalizedChatId = String(chatId || "").trim();
      if (!normalizedChatId) {
        continue;
      }
      chatStates.set(normalizedChatId, normalizePersistedChatState(state));
    }
  } catch (error) {
    console.warn(
      `[feishu] failed to load persisted chat state from ${config.feishuStateFile}: ${
        error instanceof Error ? error.message : String(error)
      }`
    );
  }
}

loadPersistedChatStates();

function normalizePersistedUserTokenState(state) {
  return {
    accessToken: String(state?.accessToken || "").trim(),
    expiresAt: Math.max(0, Number(state?.expiresAt || 0)),
    refreshToken: String(state?.refreshToken || "").trim(),
    refreshExpiresAt: Math.max(0, Number(state?.refreshExpiresAt || 0)),
    openId: String(state?.openId || "").trim(),
    userId: String(state?.userId || "").trim(),
    name: String(state?.name || "").trim(),
    tenantKey: String(state?.tenantKey || "").trim(),
    sid: String(state?.sid || "").trim()
  };
}

function persistUserTokenState() {
  const payload = {
    updatedAt: new Date().toISOString(),
    auth: normalizePersistedUserTokenState(feishuUserTokenCache)
  };
  const stateDir = dirname(config.feishuUserTokenFile);
  mkdirSync(stateDir, { recursive: true });
  const tempFile = `${config.feishuUserTokenFile}.tmp`;
  writeFileSync(tempFile, JSON.stringify(payload, null, 2), "utf8");
  renameSync(tempFile, config.feishuUserTokenFile);
}

function loadPersistedUserTokenState() {
  if (!existsSync(config.feishuUserTokenFile)) {
    return;
  }

  try {
    const raw = readFileSync(config.feishuUserTokenFile, "utf8");
    if (!raw.trim()) {
      return;
    }
    const parsed = JSON.parse(raw);
    feishuUserTokenCache = normalizePersistedUserTokenState(parsed?.auth || {});
  } catch (error) {
    console.warn(
      `[feishu] failed to load user token state from ${config.feishuUserTokenFile}: ${
        error instanceof Error ? error.message : String(error)
      }`
    );
  }
}

loadPersistedUserTokenState();

function json(res, status, body) {
  res.writeHead(status, { "content-type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(body));
}

function text(res, status, body) {
  res.writeHead(status, { "content-type": "text/plain; charset=utf-8" });
  res.end(body);
}

function hasValidUserAccessToken(now = Date.now()) {
  return Boolean(
    feishuUserTokenCache.accessToken &&
      feishuUserTokenCache.expiresAt > now + 60_000
  );
}

function getUserTokenVersion(accessToken = feishuUserTokenCache.accessToken) {
  const token = String(accessToken || "").trim();
  if (!token) {
    return "missing";
  }
  if (token.startsWith("eyJ")) {
    return "jwt";
  }
  if (token.startsWith("u-")) {
    return "opaque";
  }
  return "unknown";
}

function hasRefreshableUserToken(now = Date.now()) {
  return Boolean(
    feishuUserTokenCache.refreshToken &&
      feishuUserTokenCache.refreshExpiresAt > now + 60_000
  );
}

function hasDedicatedUserAuthApp() {
  return Boolean(
    config.feishuUserAuthAppId &&
      config.feishuUserAuthAppSecret &&
      (
        config.feishuUserAuthAppId !== config.feishuAppId ||
        config.feishuUserAuthAppSecret !== config.feishuAppSecret
      )
  );
}

function buildLocalAuthStartUrl() {
  return `http://${config.host}:${config.port}/feishu/auth/start?redirect=1`;
}

function buildFeishuUserAuthUrl(stateValue) {
  const url = new URL("https://accounts.feishu.cn/open-apis/authen/v1/authorize");
  url.searchParams.set("client_id", config.feishuUserAuthAppId);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("redirect_uri", config.feishuUserAuthRedirectUri);
  url.searchParams.set("state", stateValue);
  if (config.feishuUserAuthScope) {
    url.searchParams.set("scope", config.feishuUserAuthScope);
  }
  return url.toString();
}

function startFeishuUserOauth() {
  const stateValue = randomUUID();
  feishuOauthState = {
    value: stateValue,
    expiresAt: Date.now() + 10 * 60 * 1000
  };
  return {
    state: stateValue,
    authorizeUrl: buildFeishuUserAuthUrl(stateValue),
    expiresAt: feishuOauthState.expiresAt
  };
}

function buildUserAuthRequiredMessage(reason = "") {
  const auth = startFeishuUserOauth();
  const lines = [];
  if (reason) {
    lines.push(reason);
  } else {
    lines.push("当前 bridge 已切到 user_access_token 读取模式，但还没有完成个人授权。");
  }
  lines.push("先打开下面这个授权地址完成一次飞书登录，再重新发起总结：");
  lines.push(auth.authorizeUrl);
  return lines.join("\n");
}

function buildLegacyUserAuthBlockedMessage(reason = "") {
  const lines = [];
  if (reason) {
    lines.push(reason);
  } else {
    lines.push("当前保存的 user_access_token 还是飞书历史版本（通常以 u- 开头），新接口无法读取群历史。");
  }

  if (hasDedicatedUserAuthApp()) {
    lines.push("当前 bridge 已配置独立的用户授权应用，请重新走一次新版授权：");
    lines.push(buildLocalAuthStartUrl());
    return lines.join("\n");
  }

  lines.push("当前 bridge 仍在用“机器人应用”做个人授权，这个应用签发出来的还是历史版 token，所以继续重授权也只会重复进入同一个循环。");
  lines.push("要继续读取你个人可见的群，请单独准备一个支持新版终端用户授权的 Web 应用，并填入：");
  lines.push("FEISHU_USER_AUTH_APP_ID");
  lines.push("FEISHU_USER_AUTH_APP_SECRET");
  lines.push("如果你只是想先恢复可用，把 FEISHU_READ_ACCESS_MODE 改回 tenant。");
  return lines.join("\n");
}

function isUserAuthRequiredMessage(message) {
  const text = String(message || "");
  return (
    text.includes("user_access_token 读取模式") ||
    text.includes("请用新版授权地址重新授权一次") ||
    text.includes("/feishu/auth/start?redirect=1") ||
    text.includes("FEISHU_USER_AUTH_APP_ID") ||
    text.includes("FEISHU_READ_ACCESS_MODE 改回 tenant")
  );
}

async function handleAdComboCommand(userText, chatId) {
  const text = userText.trim();

  if (text.startsWith("补充 ")) {
    return await handleSupplementCommand(text);
  }

  if (text.startsWith("评估 ")) {
    return await handleEvaluateCommand(text);
  }

  return { handled: false };
}

async function handleSupplementCommand(text) {
  const match = text.match(/^补充\s+(.+?)\s+(.+)$/);
  if (!match) {
    return {
      handled: true,
      reply: "格式错误。正确格式：补充 [组合名] [数据]\n例如：补充 末日生存×像素复古 目标受众25-35岁男性，付费意愿中等"
    };
  }

  const [, comboName, supplementData] = match;
  const stateFile = process.env.AD_COMBO_STATE_FILE || "/tmp/ad_combo_candidates.json";

  try {
    let state;
    try {
      const content = await fs.promises.readFile(stateFile, "utf-8");
      state = JSON.parse(content);
    } catch {
      state = {
        last_run: null,
        candidates: { themes: [], art_styles: [], combos: [] },
        evaluated: { combos: [] }
      };
    }

    let found = false;
    for (const combo of state.candidates.combos) {
      const key = `${combo.theme}×${combo.art_style}`;
      if (key === comboName || combo.theme === comboName || combo.art_style === comboName) {
        combo.user_notes = supplementData;
        combo.status = "user_reviewed";
        found = true;
        break;
      }
    }

    if (!found) {
      return {
        handled: true,
        reply: `未找到组合"${comboName}"。请检查组合名称是否正确。`
      };
    }

    await fs.promises.writeFile(stateFile, JSON.stringify(state, null, 2), "utf-8");

    return {
      handled: true,
      reply: `✅ 已记录补充数据\n组合：${comboName}\n数据：${supplementData}\n\n状态已更新为"用户已审核"。如需触发完整评估，请回复：评估 ${comboName}`
    };
  } catch (error) {
    console.error("[ad-combo] supplement failed", error);
    return {
      handled: true,
      reply: `补充数据失败：${error instanceof Error ? error.message : String(error)}`
    };
  }
}

async function handleEvaluateCommand(text) {
  const match = text.match(/^评估\s+(.+)$/);
  if (!match) {
    return {
      handled: true,
      reply: "格式错误。正确格式：评估 [组合名]\n例如：评估 末日生存×像素复古"
    };
  }

  const [, comboName] = match;

  return {
    handled: true,
    reply: `📋 评估请求已收到：${comboName}\n\n⚠️ 完整评估需要在 Codex 会话中执行"买量组合评估"Skill。\n\n请在 Codex 中运行：\n/买量组合评估 ${comboName}\n\n或者手动触发评估流程。`
  };
}

function getWsReconnectInfo() {
  if (!feishuWsClient || typeof feishuWsClient.getReconnectInfo !== "function") {
    return {
      lastConnectTime: 0,
      nextConnectTime: 0
    };
  }
  try {
    const info = feishuWsClient.getReconnectInfo();
    return {
      lastConnectTime: Number(info?.lastConnectTime || 0),
      nextConnectTime: Number(info?.nextConnectTime || 0)
    };
  } catch {
    return {
      lastConnectTime: 0,
      nextConnectTime: 0
    };
  }
}

function getFeishuUserAuthStatus() {
  const now = Date.now();
  return {
    mode: config.feishuReadAccessMode,
    appId: config.feishuUserAuthAppId || null,
    hasDedicatedUserAuthApp: hasDedicatedUserAuthApp(),
    redirectUri: config.feishuUserAuthRedirectUri,
    scope: config.feishuUserAuthScope || null,
    tokenFile: config.feishuUserTokenFile,
    authorized: hasValidUserAccessToken(now) || hasRefreshableUserToken(now),
    tokenVersion: getUserTokenVersion(),
    accessTokenExpiresAt: feishuUserTokenCache.expiresAt || null,
    refreshTokenExpiresAt: feishuUserTokenCache.refreshExpiresAt || null,
    pendingStateExpiresAt:
      feishuOauthState.value && feishuOauthState.expiresAt > now
        ? feishuOauthState.expiresAt
        : null,
    user:
      feishuUserTokenCache.openId || feishuUserTokenCache.name
        ? {
            openId: feishuUserTokenCache.openId || null,
            userId: feishuUserTokenCache.userId || null,
            name: feishuUserTokenCache.name || null,
            tenantKey: feishuUserTokenCache.tenantKey || null
          }
        : null
  };
}

function markFeishuEventSeen(payload, source) {
  feishuIngressState.lastEventAt = Date.now();
  feishuIngressState.lastEventId = String(payload?.header?.event_id || payload?.event_id || "").trim();
  feishuIngressState.lastEventType = String(payload?.header?.event_type || payload?.type || "").trim();
  feishuIngressState.lastEventSource = String(source || "").trim();
  feishuIngressState.lastError = "";
}

function pruneProcessedEvents() {
  const now = Date.now();
  for (const [key, expiresAt] of processedEvents.entries()) {
    if (expiresAt <= now) {
      processedEvents.delete(key);
    }
  }
}

function getChatState(chatId) {
  if (!chatStates.has(chatId)) {
    chatStates.set(chatId, {
      messages: [],
      lastDigestIndex: 0,
      lastDigestAt: 0,
      lastSeenAt: 0,
      lastSender: "",
      lastText: ""
    });
  }
  return chatStates.get(chatId);
}

function pruneChatState(state) {
  const maxMessages = Math.max(20, config.feishuDigestMaxMessages);
  if (state.messages.length > maxMessages * 3) {
    const keep = maxMessages * 2;
    const removed = state.messages.length - keep;
    state.messages = state.messages.slice(-keep);
    state.lastDigestIndex = Math.max(0, state.lastDigestIndex - removed);
  }
}

function recordChatMessage({ chatId, sender, text, eventId, messageId }) {
  const state = getChatState(chatId);
  state.messages.push({
    at: Date.now(),
    sender,
    text,
    eventId,
    messageId
  });
  state.lastSeenAt = Date.now();
  state.lastSender = sender;
  state.lastText = text;
  pruneChatState(state);
  persistChatStates();
  return state;
}

async function addMessageReaction(messageId) {
  const emojiType = String(config.feishuRunIndicatorEmojiType || "").trim();
  if (!config.feishuRunIndicator || !emojiType || !messageId) {
    return;
  }

  const tenantToken = await getTenantAccessToken();
  const response = await fetch(
    `https://open.feishu.cn/open-apis/im/v1/messages/${encodeURIComponent(messageId)}/reactions`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${tenantToken}`,
        "content-type": "application/json; charset=utf-8"
      },
      body: JSON.stringify({
        reaction_type: {
          emoji_type: emojiType
        }
      })
    }
  );

  const responseText = await response.text();
  let responseBody = responseText;
  if (responseText) {
    try {
      responseBody = JSON.parse(responseText);
    } catch {
      responseBody = responseText;
    }
  }

  if (!response.ok) {
    throw new Error(
      `Add reaction failed: HTTP ${response.status} ${typeof responseBody === "string" ? responseBody : JSON.stringify(responseBody)}`
    );
  }

  const data =
    typeof responseBody === "string"
      ? responseBody
        ? JSON.parse(responseBody)
        : {}
      : responseBody;
  if (data.code !== 0) {
    throw new Error(`Add reaction failed: ${JSON.stringify(data)}`);
  }
  console.log("[feishu] reaction added");
}

function formatChatMessages(messages) {
  return messages
    .map((item) => {
      const at = new Date(item.at).toISOString();
      const sender = item.sender ? ` sender=${item.sender}` : "";
      return `[${at}]${sender} ${item.text}`;
    })
    .join("\n");
}

function getSummaryTimeRangeLabel(messageText, now = new Date()) {
  const text = String(messageText || "").trim();
  const end = new Date(now);
  const start = new Date(now);
  let label = "今天";

  if (text.includes("昨天")) {
    start.setDate(start.getDate() - 1);
    start.setHours(0, 0, 0, 0);
    end.setTime(start.getTime());
    end.setHours(23, 59, 59, 999);
    label = "昨天";
  } else {
    start.setHours(0, 0, 0, 0);
  }

  return {
    label,
    startTime: start.getTime(),
    endTime: end.getTime()
  };
}

function isCrossChatSummaryRequest(messageText) {
  const text = String(messageText || "").trim();
  if (!text) {
    return false;
  }

  const mentionsAll = ["所有", "全部", "各群", "全群"].some((keyword) => text.includes(keyword));
  const mentionsGroup = ["群聊", "群消息", "群记录", "聊天记录", "群"].some((keyword) => text.includes(keyword));
  const mentionsUnread = ["未读", "没读", "未总结", "新消息"].some((keyword) => text.includes(keyword));
  return Boolean((mentionsAll && mentionsGroup) || (mentionsUnread && mentionsGroup) || text.includes("跨群"));
}

function buildDigestPrompt(chatId, messages) {
  const transcript = formatChatMessages(messages);
  return [
    "请把下面这个飞书群聊片段整理成一份适合发到专属群的四分类纪要，风格偏团队晨报/周报，优先帮助推进工作。",
    "要求：",
    "- 只输出中文",
    "- 不要解释你的思路",
    "- 结构固定为：",
    "  1. 重要工作内容",
    "  2. 日常工作进度",
    "  3. 讨论/闲聊",
    "  4. 摸鱼",
    "- 先判断重要性，再决定放进哪个分类；同一条信息不要重复出现在多个分类",
    "- 每类最多 5 条，每条尽量一句话；如果某类内容很多，只保留最关键的前几条",
    "- 重要工作内容：只放会影响交付、审批、决策、排期、依赖、风险的内容；优先写负责人、动作、截止时间、阻塞点；没有明确执行价值就不要放进去",
    "- 日常工作进度：只放 routine 进展、阶段状态、已完成/进行中/待开始；优先写当前状态、下一步、是否卡住",
    "- 讨论/闲聊：只放与工作相关但未形成动作的讨论；只保留能解释背景或结论的句子，不要保留对话过程",
    "- 摸鱼：只放明显与工作无关的内容；必须极短，尽量像一句旁白，不要扩写，不要总结成大段",
    "- 如果某一类没有内容，直接写“无”",
    "- 不要引入新的分类，不要加额外说明，不要写前言或总结性废话",
    "- 尽量提炼人名、日期、截止时间、群名、决策和动作",
    "- 压缩重复内容，避免把同一件事写进多个分类",
    "- 输出时保持四个标题原样，不要改名",
    `群聊ID: ${chatId}`,
    "消息记录：",
    "```",
    transcript,
    "```"
  ].join("\n");
}

function buildHistorySummaryPrompt({ chatId, messages, rangeLabel, partialReason = "" }) {
  const transcript = formatChatMessages(messages);
  const scopeLine = partialReason
    ? `注意：下面不是完整群历史，只是 bridge 当前能拿到的部分消息。原因：${partialReason}`
    : "注意：下面是通过飞书消息历史接口读取到的群原始消息，请直接基于这些原文总结，不要再说“缺少原始消息”。";
  return [
    "请把下面这个飞书群聊记录整理成一份四分类纪要，输出直接适合回到群里。",
    "要求：",
    "- 只输出中文",
    "- 不要解释过程",
    "- 结构固定为：",
    "  1. 重要工作内容",
    "  2. 日常工作进度",
    "  3. 讨论/闲聊",
    "  4. 摸鱼",
    "- 每类最多 5 条，每条尽量一句话；没有内容就写“无”",
    "- 优先提炼负责人、动作、时间点、阻塞和结论",
    "- 压缩重复表达，不要把同一件事拆成多条",
    "- 重要工作内容：只放影响交付、审批、决策、排期、依赖、风险的内容",
    "- 日常工作进度：只放 routine 进展、阶段状态、下一步和是否卡住",
    "- 讨论/闲聊：只放与工作相关但尚未沉淀为动作的讨论",
    "- 摸鱼：只放明显与工作无关的内容，必须极短",
    scopeLine,
    `群聊ID: ${chatId}`,
    `时间范围: ${rangeLabel}`,
    "消息记录：",
    "```",
    transcript,
    "```"
  ].join("\n");
}

function buildCrossChatSummaryPrompt({
  groups,
  rangeLabel,
  noteLines = [],
  truncated = false,
  totalMessages = 0
}) {
  const noteBlock = noteLines.length
    ? [`补充说明：`, ...noteLines.map((line) => `- ${line}`)].join("\n")
    : "";
  const transcript = groups
    .map((group) =>
      [
        `群聊: ${group.name}`,
        `chat_id: ${group.chatId}`,
        `消息数: ${group.messages.length}`,
        "```",
        formatChatMessages(group.messages),
        "```"
      ].join("\n")
    )
    .join("\n\n");

  return [
    "请把下面多个飞书群的消息整理成一份跨群汇总纪要，输出直接适合回到飞书里。",
    "要求：",
    "- 只输出中文",
    "- 不要解释过程",
    "- 结构固定为：",
    "  1. 重要工作内容",
    "  2. 日常工作进度",
    "  3. 讨论/闲聊",
    "  4. 摸鱼",
    "- 每类最多 8 条，每条尽量一句话；没有内容就写“无”",
    "- 每条前面尽量带上群名，例如 `[产品群] xxx`",
    "- 优先提炼负责人、动作、时间点、阻塞和结论",
    "- 重要工作内容：只放影响交付、审批、决策、排期、依赖、风险的内容",
    "- 日常工作进度：只放 routine 进展、阶段状态、下一步和是否卡住",
    "- 讨论/闲聊：只放与工作相关但未沉淀为动作的讨论",
    "- 摸鱼：只放明显与工作无关的内容，必须极短",
    truncated
      ? `注意：这次输入为了控制长度做了裁剪，当前纳入 ${groups.length} 个群、${totalMessages} 条消息。`
      : `注意：当前纳入 ${groups.length} 个群、${totalMessages} 条消息。`,
    noteBlock,
    `时间范围: ${rangeLabel}`,
    "群消息记录：",
    transcript
  ]
    .filter(Boolean)
    .join("\n");
}

function classifyReplyIntent(messageText, replyInput = {}) {
  const text = String(messageText || "").trim();
  const hasDocLinks = Array.isArray(replyInput.docLinks) && replyInput.docLinks.length > 0;
  if (hasDocLinks) {
    return "document_review";
  }

  const summaryKeywords = [
    "总结",
    "纪要",
    "整理",
    "提炼",
    "复盘",
    "概括",
    "归纳",
    "帮我总结",
    "帮我整理",
    "帮我提炼"
  ];
  if (summaryKeywords.some((keyword) => text.includes(keyword))) {
    return "summary";
  }

  const reviewKeywords = [
    "帮我看",
    "帮我审",
    "审一下",
    "review",
    "评审",
    "反馈",
    "建议",
    "修改意见"
  ];
  if (reviewKeywords.some((keyword) => text.toLowerCase().includes(keyword.toLowerCase()))) {
    return "document_review";
  }

  return "chat";
}

function buildReplyPrompt({ intent, originalText, replyInput }) {
  const text = String(originalText || "").trim();

  if (intent === "document_review") {
    const docBlocks = Array.isArray(replyInput.docLinks) && replyInput.docLinks.length
      ? replyInput.docLinks
          .map((doc, index) => {
            const content = doc.content || "";
            return [
              `文档 ${index + 1}`,
              `链接: ${doc.url}`,
              `document_id: ${doc.documentId}`,
              "正文:",
              content
            ].join("\n");
          })
          .join("\n\n")
      : "";

    return [
      "你正在帮用户审阅飞书文档。",
      "要求：",
      "- 先给结论，再给问题和建议",
      "- 如果文档有明显优点，也要指出",
      "- 不要套固定四段模板，不要假装已读到你没有看到的内容",
      "- 如果信息不足，直接说明缺口",
      "- 语气像熟练同事，简洁自然",
      "用户原话：",
      text,
      docBlocks ? "文档正文：" : "",
      docBlocks
    ].filter(Boolean).join("\n");
  }

  if (intent === "summary") {
    return [
      "请把下面内容整理成一份简洁、结构化的工作总结。",
      "要求：",
      "- 用中文输出",
      "- 尽量简短，但要保留结论、待办、风险、时间点",
      "- 如果内容比较杂，优先提炼对推进工作最有价值的信息",
      "- 可以使用小标题，但不要写长篇说明",
      "原始内容：",
      text
    ].join("\n");
  }

  return [
    "你在和用户进行正常聊天或工作沟通。",
    "要求：",
    "- 直接自然地回答，不要强制固定模板",
    "- 保持简洁，像一个靠谱同事",
    "- 如果信息不足，先问最关键的一点",
    "- 不要把每次回复都写成同一种格式",
    "用户消息：",
    text
  ].join("\n");
}

function extractMessagesSinceDigest(state) {
  return state.messages.slice(state.lastDigestIndex).slice(-config.feishuDigestMaxMessages);
}

async function generateChatDigest(chatId, state) {
  const messages = extractMessagesSinceDigest(state);
  if (!messages.length) {
    return "";
  }
  const digestPrompt = buildDigestPrompt(chatId, messages);
  return askBackend(digestPrompt);
}

async function sendChatDigest(chatId, state) {
  const messages = extractMessagesSinceDigest(state);
  if (!messages.length) {
    return { kind: "empty" };
  }

  const targetChatId = String(config.feishuDigestTargetChatId || "").trim();
  if (!targetChatId) {
    throw new Error("FEISHU_DIGEST_TARGET_CHAT_ID is required when digest is enabled.");
  }

  const digest = await generateChatDigest(chatId, state);
  const sourceLabel = targetChatId === chatId ? "" : `\n来源群：${chatId}`;
  const body = `${config.feishuDigestPrefix}${sourceLabel}\n${digest}`.trim();
  await sendFeishuMessage(targetChatId, body);
  state.lastDigestIndex = state.messages.length;
  state.lastDigestAt = Date.now();
  persistChatStates();
  return { kind: "sent", count: messages.length, targetChatId };
}

async function runDigestCycle() {
  if (!config.feishuDigestEnabled) {
    return [];
  }

  const results = [];
  for (const [chatId, state] of chatStates.entries()) {
    try {
      const result = await sendChatDigest(chatId, state);
      if (result.kind === "sent") {
        results.push({ chatId, ...result });
      }
    } catch (error) {
      results.push({
        chatId,
        kind: "error",
        error: error instanceof Error ? error.message : String(error)
      });
      console.error("[digest] failed", chatId, error);
    }
  }
  return results;
}

let digestTimer = null;
function nextDigestRunTime(now = new Date()) {
  const target = new Date(now);
  target.setSeconds(0, 0);
  target.setHours(config.feishuDigestHour, config.feishuDigestMinute, 0, 0);
  if (target <= now) {
    target.setDate(target.getDate() + 1);
  }
  return target;
}

function scheduleNextDigestRun() {
  if (!config.feishuDigestEnabled) {
    return;
  }

  const target = nextDigestRunTime();
  const delay = Math.max(1000, target.getTime() - Date.now());
  digestTimer = setTimeout(() => {
    void runDigestCycle().catch((error) => {
      console.error("[digest] cycle failed", error);
    });
    scheduleNextDigestRun();
  }, delay);
  if (typeof digestTimer.unref === "function") {
    digestTimer.unref();
  }
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) {
    chunks.push(chunk);
  }
  const raw = Buffer.concat(chunks).toString("utf8").trim();
  if (!raw) {
    return {};
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    throw new Error(`Request body is not valid JSON: ${raw.slice(0, 200)}`);
  }
}

function extractMessageText(messageContent) {
  try {
    const parsed = JSON.parse(messageContent);
    if (parsed.text) {
      return normalizeMentionMarkup(String(parsed.text).trim());
    }
  } catch {
    return normalizeMentionMarkup(String(messageContent || "").trim());
  }
  return "";
}

function normalizeMentionMarkup(text) {
  return String(text || "").replace(/<at\s+user_id="[^"]+">([^<]*)<\/at>/g, "@$1").trim();
}

function extractUrls(text) {
  const matches = String(text || "").match(/https?:\/\/[^\s<>"'`]+/gi) || [];
  return [...new Set(matches.map((item) => item.replace(/[),.;!?】]+$/g, "")))];
}

async function mapWithConcurrency(items, limit, mapper) {
  const list = Array.isArray(items) ? items : [];
  if (!list.length) {
    return [];
  }

  const concurrency = Math.max(1, Math.min(Number(limit || 1), list.length));
  const results = new Array(list.length);
  let nextIndex = 0;

  async function worker() {
    while (true) {
      const currentIndex = nextIndex;
      nextIndex += 1;
      if (currentIndex >= list.length) {
        return;
      }
      results[currentIndex] = await mapper(list[currentIndex], currentIndex);
    }
  }

  await Promise.all(Array.from({ length: concurrency }, () => worker()));
  return results;
}

function parseFeishuDocUrl(rawUrl) {
  let url;
  try {
    url = new URL(rawUrl);
  } catch {
    return null;
  }

  const host = url.hostname.toLowerCase();
  if (
    !host.endsWith("feishu.cn") &&
    !host.endsWith("larkoffice.com") &&
    !host.endsWith("larksuite.com")
  ) {
    return null;
  }

  const pathname = url.pathname.replace(/\/+$/, "");
  const docxMatch = pathname.match(/^\/docx\/([A-Za-z0-9]+)/);
  if (docxMatch) {
    return {
      kind: "docx",
      documentId: docxMatch[1],
      url: rawUrl
    };
  }

  const wikiMatch = pathname.match(/^\/wiki\/([A-Za-z0-9]+)/);
  if (wikiMatch) {
    return {
      kind: "wiki",
      wikiId: wikiMatch[1],
      url: rawUrl
    };
  }

  return null;
}

function isBotMentioned(payload) {
  const message = payload?.event?.message || {};
  const mentions = Array.isArray(message.mentions) ? message.mentions : [];
  const botOpenId = String(config.feishuBotOpenId || "").trim();
  const botName = String(config.botName || "").trim();

  for (const mention of mentions) {
    if (!mention || typeof mention !== "object") {
      continue;
    }
    const mentionId = String(mention.id || "").trim();
    const mentionName = String(mention.name || "").trim();
    if (botOpenId && mentionId === botOpenId) {
      return true;
    }
    if (!botOpenId && botName && mentionName === botName) {
      return true;
    }
  }

  const content = normalizeMentionMarkup(extractMessageText(message.content));
  return Boolean(botName && content.includes(`@${botName}`));
}

function isOwnerMessage(payload) {
  const ownerOpenId = String(config.feishuOwnerOpenId || "").trim();
  if (!ownerOpenId) {
    return false;
  }
  const senderOpenId = String(payload?.event?.sender?.sender_id?.open_id || "").trim();
  return senderOpenId === ownerOpenId;
}

async function fetchFeishuDocPlainText(documentId) {
  const tenantToken = await getTenantAccessToken();
  const response = await fetch(
    `https://open.feishu.cn/open-apis/docx/v1/documents/${encodeURIComponent(documentId)}/raw_content`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${tenantToken}`,
        "content-type": "application/json; charset=utf-8"
      }
    }
  );

  const responseText = await response.text();
  let responseBody = responseText;
  if (responseText) {
    try {
      responseBody = JSON.parse(responseText);
    } catch {
      responseBody = responseText;
    }
  }

  if (!response.ok) {
    throw new Error(
      `Fetch doc content failed: HTTP ${response.status} ${typeof responseBody === "string" ? responseBody : JSON.stringify(responseBody)}`
    );
  }

  const data =
    typeof responseBody === "string"
      ? responseBody
        ? JSON.parse(responseBody)
        : {}
      : responseBody;
  if (data.code !== 0) {
    throw new Error(`Fetch doc content failed: ${JSON.stringify(data)}`);
  }

  return String(data?.data?.content || "").trim();
}

function extractHistoryMessageText(item) {
  const msgType = String(item?.msg_type || "").trim() || "message";
  const bodyContent = String(item?.body?.content || "").trim();
  if (!bodyContent) {
    return `[${msgType}]`;
  }

  if (bodyContent.startsWith("text:")) {
    return normalizeMentionMarkup(bodyContent.slice("text:".length).trim());
  }

  try {
    const parsed = JSON.parse(bodyContent);
    if (parsed && typeof parsed === "object" && typeof parsed.text === "string" && parsed.text.trim()) {
      return normalizeMentionMarkup(parsed.text.trim());
    }
  } catch {
    // Keep the raw fallback below.
  }

  return `[${msgType}] ${normalizeMentionMarkup(bodyContent)}`.trim();
}

function normalizeHistoryMessage(item) {
  if (!item || typeof item !== "object" || item.deleted) {
    return null;
  }

  const senderType = String(item?.sender?.sender_type || "").trim();
  if (senderType === "app") {
    return null;
  }

  const text = extractHistoryMessageText(item);
  if (!text) {
    return null;
  }

  const at = Number(item?.create_time || 0);
  return {
    at: Number.isFinite(at) && at > 0 ? at : Date.now(),
    sender: String(item?.sender?.id || "").trim(),
    text,
    eventId: "",
    messageId: String(item?.message_id || "").trim()
  };
}

function parseFeishuApiResponse(responseText) {
  if (!responseText) {
    return {};
  }
  try {
    return JSON.parse(responseText);
  } catch {
    return responseText;
  }
}

function describeFeishuHistoryError(errorBody) {
  const payload =
    typeof errorBody === "string"
      ? errorBody
      : JSON.stringify(errorBody);
  const code = Number(errorBody?.code || 0);
  const message = String(errorBody?.msg || "").trim();
  if (code === 99991695) {
    return buildLegacyUserAuthBlockedMessage(
      "当前保存的 user_access_token 还是飞书历史版本，暂时读不了群历史。"
    );
  }
  if (code === 230027) {
    if (message.includes("im:message.group_msg:get_as_user")) {
      return "当前个人授权还缺少用户身份权限 `im:message.group_msg:get_as_user`，所以虽然能看到群列表，但还读不到群历史消息。请在飞书后台的 user_access_token 权限里开通“获取群组中所有消息（用户身份）”后重新授权。";
    }
    return "飞书应用缺少“获取群组中所有消息”权限，当前拿不到这个群的完整历史消息。请在权限管理里补上后重新发布应用。";
  }
  if (code === 230002) {
    return "机器人当前不在这个群里，无法读取群历史。";
  }
  if (code === 230006) {
    return "飞书应用的机器人能力没有生效，无法读取群历史。";
  }
  return `读取飞书群历史失败：${payload}`;
}

function describeFeishuListChatsError(errorBody) {
  const payload =
    typeof errorBody === "string"
      ? errorBody
      : JSON.stringify(errorBody);
  const code = Number(errorBody?.code || 0);
  const message = String(errorBody?.msg || "").trim();

  if (code === 232025 || message.includes("Bot ability is not activated")) {
    return "当前独立用户授权应用还没启用“机器人”能力，所以虽然个人授权已经成功，飞书仍不允许列出会话列表。请在这个新网页应用里添加并启用“机器人”能力，发布最新版本后再试。";
  }
  if (code === 230027) {
    if (message.includes("im:chat:readonly")) {
      return "当前个人授权还缺少用户身份权限 `im:chat:readonly`，所以还拿不到你个人可见的群列表。请在飞书后台补上后重新授权。";
    }
    return "飞书应用缺少读取群列表的权限，当前还拿不到你个人可见的群。请在权限管理里补上后重新发布应用。";
  }
  if (code === 230006) {
    return "飞书应用的机器人能力没有生效，当前还列不出可见群列表。请确认机器人能力已启用并发布最新版本。";
  }
  return `读取飞书群列表失败：${payload}`;
}

async function requestFeishuChatHistory({
  chatId,
  containerIdType,
  startTime,
  endTime,
  excludeMessageId = "",
  useTimeWindow = true
}) {
  const accessToken = await getReadAccessToken();
  const messages = [];
  let pageToken = "";
  const maxMessages = 500;
  const pageSize = 50;

  while (messages.length < maxMessages) {
    const url = new URL("https://open.feishu.cn/open-apis/im/v1/messages");
    url.searchParams.set("container_id_type", containerIdType);
    url.searchParams.set("container_id", chatId);
    if (useTimeWindow) {
      url.searchParams.set("start_time", String(startTime));
      url.searchParams.set("end_time", String(endTime));
    }
    url.searchParams.set("page_size", String(Math.min(pageSize, maxMessages - messages.length)));
    if (pageToken) {
      url.searchParams.set("page_token", pageToken);
    }

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "content-type": "application/json; charset=utf-8"
      }
    });

    const responseText = await response.text();
    const data = parseFeishuApiResponse(responseText);
    if (!response.ok) {
      throw new Error(
        `Fetch chat history failed: HTTP ${response.status} ${typeof data === "string" ? data : JSON.stringify(data)}`
      );
    }
    if (typeof data !== "object" || data.code !== 0) {
      throw new Error(describeFeishuHistoryError(data));
    }

    const items = Array.isArray(data?.data?.items) ? data.data.items : [];
    for (const item of items) {
      const message = normalizeHistoryMessage(item);
      if (!message) {
        continue;
      }
      if (excludeMessageId && message.messageId === excludeMessageId) {
        continue;
      }
      if (message.text.startsWith(config.feishuDigestPrefix)) {
        continue;
      }
      messages.push(message);
      if (messages.length >= maxMessages) {
        break;
      }
    }

    if (!data?.data?.has_more || !data?.data?.page_token) {
      break;
    }
    pageToken = String(data.data.page_token || "").trim();
    if (!pageToken) {
      break;
    }
  }

  return messages.sort((left, right) => left.at - right.at);
}

async function fetchFeishuChatHistory({ chatId, startTime, endTime, excludeMessageId = "" }) {
  const attempts = [
    { containerIdType: "chat", useTimeWindow: true },
    { containerIdType: "chat", useTimeWindow: false }
  ];
  let lastError = null;

  for (const attempt of attempts) {
    try {
      const result = await requestFeishuChatHistory({
        chatId,
        startTime,
        endTime,
        excludeMessageId,
        ...attempt
      });
      const filtered = attempt.useTimeWindow
        ? result
        : result.filter((item) => item.at >= startTime && item.at <= endTime);

      console.log("[feishu] history fetch", {
        chatId,
        containerIdType: attempt.containerIdType,
        useTimeWindow: attempt.useTimeWindow,
        count: filtered.length
      });
      return filtered;
    } catch (error) {
      lastError = error;
      const message = error instanceof Error ? error.message : String(error);
      console.warn("[feishu] history fetch failed", {
        chatId,
        containerIdType: attempt.containerIdType,
        useTimeWindow: attempt.useTimeWindow,
        error: message
      });

      if (
        message.includes("获取群组中所有消息") ||
        message.includes("机器人当前不在这个群里") ||
        message.includes("机器人能力没有生效")
      ) {
        throw error;
      }
    }
  }

  if (lastError) {
    throw lastError;
  }
  return [];
}

function extractCachedSummaryMessages(chatId, excludeMessageId = "") {
  const state = getChatState(chatId);
  return state.messages
    .filter((item) => item && item.text && !item.text.startsWith(config.feishuDigestPrefix))
    .filter((item) => !excludeMessageId || item.messageId !== excludeMessageId)
    .slice(-Math.max(config.feishuDigestMaxMessages, 50));
}

async function listFeishuVisibleChats() {
  const accessToken = await getReadAccessToken();
  const chats = [];
  let pageToken = "";
  const maxChats = Math.max(1, config.feishuCrossChatMaxChats);
  const pageSize = 50;

  while (chats.length < maxChats) {
    const url = new URL("https://open.feishu.cn/open-apis/im/v1/chats");
    url.searchParams.set("page_size", String(Math.min(pageSize, maxChats - chats.length)));
    url.searchParams.set("user_id_type", "open_id");
    if (pageToken) {
      url.searchParams.set("page_token", pageToken);
    }

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "content-type": "application/json; charset=utf-8"
      }
    });

    const responseText = await response.text();
    const data = parseFeishuApiResponse(responseText);
    if (!response.ok) {
      throw new Error(describeFeishuListChatsError(data));
    }
    if (typeof data !== "object" || data.code !== 0) {
      throw new Error(describeFeishuListChatsError(data));
    }

    const items = Array.isArray(data?.data?.items) ? data.data.items : [];
    for (const item of items) {
      const chatId = String(item?.chat_id || "").trim();
      if (!chatId) {
        continue;
      }
      chats.push({
        chatId,
        name: String(item?.name || "").trim() || chatId,
        description: String(item?.description || "").trim()
      });
      if (chats.length >= maxChats) {
        break;
      }
    }

    if (!data?.data?.has_more || !data?.data?.page_token) {
      break;
    }
    pageToken = String(data.data.page_token || "").trim();
    if (!pageToken) {
      break;
    }
  }

  return chats;
}

function getUnreadStartTimeForChat(chatId, defaultStartTime) {
  const state = chatStates.get(chatId);
  const lastDigestAt = Number(state?.lastDigestAt || 0);
  if (!lastDigestAt) {
    return defaultStartTime;
  }
  return Math.max(defaultStartTime, lastDigestAt + 1);
}

function trimCrossChatGroups(groups) {
  const maxGroups = Math.max(1, config.feishuCrossChatMaxChats);
  const maxPerChat = Math.max(1, config.feishuCrossChatMaxMessagesPerChat);
  const maxTotal = Math.max(maxPerChat, config.feishuCrossChatMaxTotalMessages);
  const sorted = [...groups].sort((left, right) => Number(right.lastMessageAt || 0) - Number(left.lastMessageAt || 0));

  const selected = [];
  let totalMessages = 0;
  let truncated = false;

  for (const group of sorted) {
    if (selected.length >= maxGroups || totalMessages >= maxTotal) {
      truncated = true;
      break;
    }

    const clippedMessages = group.messages.slice(-maxPerChat);
    if (clippedMessages.length < group.messages.length) {
      truncated = true;
    }

    const remaining = maxTotal - totalMessages;
    if (remaining <= 0) {
      truncated = true;
      break;
    }

    const finalMessages = clippedMessages.slice(-remaining);
    if (finalMessages.length < clippedMessages.length) {
      truncated = true;
    }
    if (!finalMessages.length) {
      truncated = true;
      break;
    }

    selected.push({
      ...group,
      messages: finalMessages,
      lastMessageAt: finalMessages[finalMessages.length - 1]?.at || group.lastMessageAt
    });
    totalMessages += finalMessages.length;
  }

  if (selected.length < groups.length) {
    truncated = true;
  }

  return {
    groups: selected,
    truncated,
    totalMessages
  };
}

function describeCrossChatScope() {
  return config.feishuReadAccessMode === "user" ? "你个人可见的所有群" : "机器人可见的所有群";
}

function describeCrossChatUnreadScope() {
  return config.feishuReadAccessMode === "user"
    ? "今天你个人可见的群里没有读到可用于总结的未纪要消息。"
    : "今天机器人可见的群里没有读到可用于总结的未纪要消息。";
}

async function buildCrossChatSummaryReply({ chatId, messageId, originalText, sessionTarget }) {
  const { label, startTime, endTime } = getSummaryTimeRangeLabel(originalText);
  const rangeLabel = `${label} ${new Date(startTime).toLocaleString()} - ${new Date(endTime).toLocaleString()}`;
  const startedAt = Date.now();
  let visibleChats;
  try {
    visibleChats = await listFeishuVisibleChats();
  } catch (error) {
    return error instanceof Error ? error.message : String(error);
  }
  console.log("[feishu] cross-chat visible chats", {
    count: visibleChats.length,
    chats: visibleChats.slice(0, 10).map((item) => ({
      chatId: item.chatId,
      name: item.name
    }))
  });
  const groups = [];
  const errors = [];
  const fetchResults = await mapWithConcurrency(
    visibleChats,
    Math.max(1, config.feishuCrossChatConcurrency),
    async (chat) => {
      try {
        const unreadStartTime = getUnreadStartTimeForChat(chat.chatId, startTime);
        const messages = await fetchFeishuChatHistory({
          chatId: chat.chatId,
          startTime: unreadStartTime,
          endTime,
          excludeMessageId: chat.chatId === chatId ? messageId : ""
        });

        if (!messages.length) {
          return null;
        }

        return {
          kind: "group",
          value: {
            chatId: chat.chatId,
            name: chat.name,
            messages,
            lastMessageAt: messages[messages.length - 1]?.at || 0
          }
        };
      } catch (error) {
        return {
          kind: "error",
          value: {
            chatId: chat.chatId,
            name: chat.name,
            error: error instanceof Error ? error.message : String(error)
          }
        };
      }
    }
  );

  for (const item of fetchResults) {
    if (!item) {
      continue;
    }
    if (item.kind === "group") {
      groups.push(item.value);
      continue;
    }
    if (item.kind === "error") {
      errors.push(item.value);
    }
  }

  console.log("[feishu] cross-chat fetch complete", {
    scannedCount: visibleChats.length,
    matchedCount: groups.length,
    errorCount: errors.length,
    concurrency: Math.max(1, config.feishuCrossChatConcurrency),
    durationMs: Date.now() - startedAt
  });

  if (!groups.length) {
    if (errors.length) {
      const preview = errors
        .slice(0, 3)
        .map((item) => `${item.name}: ${item.error}`)
        .join("；");
      return `我尝试扫描${describeCrossChatScope()}，但没有成功读到可用于汇总的消息。${preview ? ` 已知问题：${preview}` : ""}`;
    }
    return describeCrossChatUnreadScope();
  }

  const trimmed = trimCrossChatGroups(groups);
  console.log("[feishu] cross-chat matched groups", {
    count: groups.length,
    selectedCount: trimmed.groups.length,
    groups: trimmed.groups.map((item) => ({
      chatId: item.chatId,
      name: item.name,
      messageCount: item.messages.length
    }))
  });
  const noteLines = [
    "“未读”按 bridge 的近似口径处理：优先取各群上次纪要之后的新消息；从未纪要过的群则取今天消息。"
  ];
  if (errors.length) {
    noteLines.push(
      `有 ${errors.length} 个群读取失败，例如：${errors
        .slice(0, 3)
        .map((item) => item.name)
        .join("、")}`
    );
  }

  const prompt = buildCrossChatSummaryPrompt({
    groups: trimmed.groups,
    rangeLabel,
    noteLines,
    truncated: trimmed.truncated,
    totalMessages: trimmed.totalMessages
  });
  return askBackend(prompt, { sessionTarget });
}

async function buildSummaryReply({ chatId, messageId, originalText, sessionTarget }) {
  if (isCrossChatSummaryRequest(originalText)) {
    return buildCrossChatSummaryReply({
      chatId,
      messageId,
      originalText,
      sessionTarget
    });
  }

  const { label, startTime, endTime } = getSummaryTimeRangeLabel(originalText);
  const rangeLabel = `${label} ${new Date(startTime).toLocaleString()} - ${new Date(endTime).toLocaleString()}`;
  let messages = [];
  let partialReason = "";

  try {
    messages = await fetchFeishuChatHistory({
      chatId,
      startTime,
      endTime,
      excludeMessageId: messageId
    });
  } catch (error) {
    partialReason = error instanceof Error ? error.message : String(error);
    if (isUserAuthRequiredMessage(partialReason)) {
      return partialReason;
    }
    messages = extractCachedSummaryMessages(chatId, messageId);
  }

  if (!messages.length) {
    if (partialReason) {
      return `我尝试读取这个群${label}的完整消息历史，但失败了：${partialReason}`;
    }
    return `${label}这个群里没有读到可用于总结的消息。`;
  }

  const prompt = buildHistorySummaryPrompt({
    chatId,
    messages,
    rangeLabel,
    partialReason
  });
  return askBackend(prompt, { sessionTarget });
}

async function buildReplyInputFromMessage(messageText) {
  const urls = extractUrls(messageText);
  const docLinks = urls
    .map((url) => parseFeishuDocUrl(url))
    .filter((item) => item && item.kind === "docx");

  if (!docLinks.length) {
    return {
      text: messageText,
      docLinks: []
    };
  }

  const docs = [];
  for (const docLink of docLinks) {
    try {
      const content = await fetchFeishuDocPlainText(docLink.documentId);
      if (!content) {
        continue;
      }
      docs.push({
        url: docLink.url,
        documentId: docLink.documentId,
        content
      });
    } catch (error) {
      return {
        text: "",
        docLinks,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }

  if (!docs.length) {
    return {
      text: "",
      docLinks,
      error: "未能读取到文档正文"
    };
  }

  const docBlocks = docs
    .map(
      (doc, index) =>
        [
          `文档 ${index + 1}`,
          `链接: ${doc.url}`,
          `document_id: ${doc.documentId}`,
          "正文:",
          doc.content
        ].join("\n")
    )
    .join("\n\n");

  return {
    text: [
      "请先阅读下面的飞书文档正文，再给出审阅意见。",
      "如果文档里有结论、待办、风险、改动建议，请直接提炼出来；如果信息不足，请明确指出缺口。",
      "原消息：",
      messageText,
      "文档内容：",
      docBlocks
    ].join("\n"),
    docLinks: docs
  };
}

async function getTenantAccessToken() {
  const now = Date.now();
  if (feishuTenantTokenCache.token && feishuTenantTokenCache.expiresAt > now + 60_000) {
    return feishuTenantTokenCache.token;
  }

  const response = await fetch(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        app_id: config.feishuAppId,
        app_secret: config.feishuAppSecret
      })
    }
  );

  if (!response.ok) {
    throw new Error(`Feishu auth failed: HTTP ${response.status}`);
  }

  const data = await response.json();
  if (data.code !== 0 || !data.tenant_access_token) {
    throw new Error(`Feishu auth failed: ${JSON.stringify(data)}`);
  }

  feishuTenantTokenCache = {
    token: data.tenant_access_token,
    expiresAt: now + Number(data.expire || 7200) * 1000
  };

  return feishuTenantTokenCache.token;
}

async function getAppAccessToken() {
  const now = Date.now();
  if (feishuAppTokenCache.token && feishuAppTokenCache.expiresAt > now + 60_000) {
    return feishuAppTokenCache.token;
  }

  const response = await fetch(
    "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal",
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        app_id: config.feishuAppId,
        app_secret: config.feishuAppSecret
      })
    }
  );

  if (!response.ok) {
    throw new Error(`Feishu app auth failed: HTTP ${response.status}`);
  }

  const data = await response.json();
  const appAccessToken = String(data.app_access_token || "").trim();
  if (data.code !== 0 || !appAccessToken) {
    throw new Error(`Feishu app auth failed: ${JSON.stringify(data)}`);
  }

  feishuAppTokenCache = {
    token: appAccessToken,
    expiresAt: now + Number(data.expire || 7200) * 1000
  };

  return feishuAppTokenCache.token;
}

async function getUserAuthAppAccessToken() {
  const now = Date.now();
  if (
    feishuUserAuthAppTokenCache.token &&
    feishuUserAuthAppTokenCache.expiresAt > now + 60_000
  ) {
    return feishuUserAuthAppTokenCache.token;
  }

  const response = await fetch(
    "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal",
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        app_id: config.feishuUserAuthAppId,
        app_secret: config.feishuUserAuthAppSecret
      })
    }
  );

  if (!response.ok) {
    throw new Error(`Feishu user auth app token failed: HTTP ${response.status}`);
  }

  const data = await response.json();
  const appAccessToken = String(data.app_access_token || "").trim();
  if (data.code !== 0 || !appAccessToken) {
    throw new Error(`Feishu user auth app token failed: ${JSON.stringify(data)}`);
  }

  feishuUserAuthAppTokenCache = {
    token: appAccessToken,
    expiresAt: now + Number(data.expire || 7200) * 1000
  };

  return feishuUserAuthAppTokenCache.token;
}

async function fetchFeishuUserInfo(accessToken) {
  const response = await fetch("https://open.feishu.cn/open-apis/authen/v1/user_info", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });

  const responseText = await response.text();
  const data = parseFeishuApiResponse(responseText);
  if (!response.ok) {
    throw new Error(
      `Feishu user info failed: HTTP ${response.status} ${
        typeof data === "string" ? data : JSON.stringify(data)
      }`
    );
  }
  if (typeof data !== "object" || data.code !== 0 || !data?.data) {
    throw new Error(`Feishu user info failed: ${typeof data === "string" ? data : JSON.stringify(data)}`);
  }
  return data.data;
}

async function exchangeUserAccessToken(code) {
  const appAccessToken = await getUserAuthAppAccessToken();
  const response = await fetch("https://open.feishu.cn/open-apis/authen/v1/oidc/access_token", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${appAccessToken}`,
      "content-type": "application/json; charset=utf-8"
    },
    body: JSON.stringify({
      grant_type: "authorization_code",
      code
    })
  });

  const responseText = await response.text();
  const data = parseFeishuApiResponse(responseText);
  if (!response.ok) {
    throw new Error(
      `Feishu user auth failed: HTTP ${response.status} ${
        typeof data === "string" ? data : JSON.stringify(data)
      }`
    );
  }
  if (typeof data !== "object" || data.code !== 0 || !data?.data?.access_token) {
    throw new Error(`Feishu user auth failed: ${typeof data === "string" ? data : JSON.stringify(data)}`);
  }

  let userInfo = {};
  try {
    userInfo = await fetchFeishuUserInfo(data.data.access_token);
  } catch (error) {
    console.warn("[feishu] user info lookup after auth failed", error);
  }

  const now = Date.now();
  feishuUserTokenCache = normalizePersistedUserTokenState({
    accessToken: data.data.access_token,
    expiresAt: now + Number(data.data.expires_in || 7200) * 1000,
    refreshToken: data.data.refresh_token,
    refreshExpiresAt: now + Number(data.data.refresh_expires_in || 0) * 1000,
    openId: userInfo.open_id || data.data.open_id,
    userId: userInfo.user_id || data.data.user_id,
    name: userInfo.name || userInfo.en_name || data.data.name || data.data.en_name || "",
    tenantKey: userInfo.tenant_key || data.data.tenant_key,
    sid: data.data.sid
  });
  persistUserTokenState();
  return feishuUserTokenCache.accessToken;
}

async function refreshUserAccessToken() {
  if (!feishuUserTokenCache.refreshToken) {
    throw new Error(buildUserAuthRequiredMessage());
  }

  const appAccessToken = await getUserAuthAppAccessToken();
  const response = await fetch("https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${appAccessToken}`,
      "content-type": "application/json; charset=utf-8"
    },
    body: JSON.stringify({
      grant_type: "refresh_token",
      refresh_token: feishuUserTokenCache.refreshToken
    })
  });

  const responseText = await response.text();
  const data = parseFeishuApiResponse(responseText);
  if (!response.ok) {
    throw new Error(
      `Feishu user refresh failed: HTTP ${response.status} ${
        typeof data === "string" ? data : JSON.stringify(data)
      }`
    );
  }
  if (typeof data !== "object" || data.code !== 0 || !data?.data?.access_token) {
    throw new Error(`Feishu user refresh failed: ${typeof data === "string" ? data : JSON.stringify(data)}`);
  }

  let userInfo = {};
  try {
    userInfo = await fetchFeishuUserInfo(data.data.access_token);
  } catch (error) {
    console.warn("[feishu] user info lookup after refresh failed", error);
  }

  const now = Date.now();
  const refreshExpiresAt =
    Number(data.data.refresh_expires_in || 0) > 0
      ? now + Number(data.data.refresh_expires_in) * 1000
      : feishuUserTokenCache.refreshExpiresAt;
  feishuUserTokenCache = normalizePersistedUserTokenState({
    accessToken: data.data.access_token,
    expiresAt: now + Number(data.data.expires_in || 7200) * 1000,
    refreshToken: data.data.refresh_token || feishuUserTokenCache.refreshToken,
    refreshExpiresAt,
    openId: userInfo.open_id || data.data.open_id || feishuUserTokenCache.openId,
    userId: userInfo.user_id || data.data.user_id || feishuUserTokenCache.userId,
    name: userInfo.name || userInfo.en_name || data.data.name || data.data.en_name || feishuUserTokenCache.name,
    tenantKey: userInfo.tenant_key || data.data.tenant_key || feishuUserTokenCache.tenantKey,
    sid: data.data.sid || feishuUserTokenCache.sid
  });
  persistUserTokenState();
  return feishuUserTokenCache.accessToken;
}

async function getUserAccessToken() {
  const now = Date.now();
  if (hasValidUserAccessToken(now)) {
    return feishuUserTokenCache.accessToken;
  }
  if (hasRefreshableUserToken(now)) {
    const refreshed = await refreshUserAccessToken();
    return refreshed;
  }
  throw new Error(buildUserAuthRequiredMessage());
}

async function getReadAccessToken() {
  if (config.feishuReadAccessMode === "user") {
    return getUserAccessToken();
  }
  return getTenantAccessToken();
}

async function sendFeishuMessage(chatId, content) {
  console.log(`[feishu] replying to ${chatId}: ${content.slice(0, 200)}`);
  const tenantToken = await getTenantAccessToken();
  const response = await fetch(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${tenantToken}`,
        "content-type": "application/json; charset=utf-8"
      },
      body: JSON.stringify({
        receive_id: chatId,
        msg_type: "text",
        content: JSON.stringify({ text: content })
      })
    }
  );

  const responseText = await response.text();
  let responseBody = responseText;
  if (responseText) {
    try {
      responseBody = JSON.parse(responseText);
    } catch {
      responseBody = responseText;
    }
  }

  if (!response.ok) {
    throw new Error(
      `Send message failed: HTTP ${response.status} ${typeof responseBody === "string" ? responseBody : JSON.stringify(responseBody)}`
    );
  }

  const data =
    typeof responseBody === "string"
      ? responseBody
        ? JSON.parse(responseBody)
        : {}
      : responseBody;
  if (data.code !== 0) {
    throw new Error(`Send message failed: ${JSON.stringify(data)}`);
  }
  console.log("[feishu] reply sent");
}

async function askOpenAI(userText) {
  const response = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${config.openaiApiKey}`,
      "content-type": "application/json"
    },
    body: JSON.stringify({
      model: config.openaiModel,
      input: [
        {
          role: "system",
          content: [{ type: "input_text", text: config.systemPrompt }]
        },
        {
          role: "user",
          content: [{ type: "input_text", text: userText }]
        }
      ]
    })
  });

  if (!response.ok) {
    throw new Error(`OpenAI request failed: HTTP ${response.status}`);
  }

  const data = await response.json();
  const textOutput = data.output_text?.trim();
  if (textOutput) {
    return textOutput;
  }

  const fallback = data.output
    ?.flatMap((item) => item.content || [])
    ?.find((item) => item.type === "output_text")?.text;

  if (!fallback) {
    throw new Error(`No model output text: ${JSON.stringify(data)}`);
  }

  return String(fallback).trim();
}

async function askSiliconFlow(userText) {
  const response = await fetch(
    `${config.siliconflowBaseUrl.replace(/\/$/, "")}/chat/completions`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${config.siliconflowApiKey}`,
        "content-type": "application/json"
      },
      body: JSON.stringify({
        model: config.siliconflowModel,
        messages: [
          {
            role: "system",
            content: config.systemPrompt
          },
          {
            role: "user",
            content: userText
          }
        ]
      })
    }
  );

  if (!response.ok) {
    throw new Error(`SiliconFlow request failed: HTTP ${response.status}`);
  }

  const data = await response.json();
  const choice = data.choices?.[0];
  const message = choice?.message;
  const content = message?.content;

  if (typeof content === "string" && content.trim()) {
    return content.trim();
  }

  if (Array.isArray(content)) {
    const textOutput = content
      .filter((item) => item?.type === "text" && item.text)
      .map((item) => String(item.text).trim())
      .filter(Boolean)
      .join("\n\n");
    if (textOutput) {
      return textOutput;
    }
  }

  if (typeof message?.reasoning_content === "string" && message.reasoning_content.trim()) {
    return message.reasoning_content.trim();
  }

  throw new Error(`No model output text: ${JSON.stringify(data)}`);
}

async function askAnthropic(userText) {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": config.anthropicApiKey,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json"
    },
    body: JSON.stringify({
      model: config.anthropicModel,
      max_tokens: 1024,
      system: config.systemPrompt,
      messages: [{ role: "user", content: userText }]
    })
  });

  if (!response.ok) {
    throw new Error(`Anthropic request failed: HTTP ${response.status}`);
  }

  const data = await response.json();
  logAnthropicUsage(data.usage, {
    model: data.model,
    label: "feishu-codex-bridge"
  });
  const textOutput = data.content
    ?.filter((item) => item.type === "text" && item.text)
    .map((item) => item.text.trim())
    .filter(Boolean)
    .join("\n\n");

  if (!textOutput) {
    throw new Error(`No model output text: ${JSON.stringify(data)}`);
  }

  return textOutput;
}

function askCodexBridge(userText, sessionTarget = "") {
  const args = [
    config.codexBridgeScript,
    "send"
  ];
  const target = String(sessionTarget || config.codexSessionTarget || "").trim();
  if (target) {
    args.push("--session", target);
  }
  args.push("--message", userText, "--json");

  const proc = spawnSync(config.codexPython, args, {
    cwd: config.codexWorkdir,
    encoding: "utf8",
    env: process.env,
    maxBuffer: 10 * 1024 * 1024,
    timeout: Number(process.env.CODEX_BRIDGE_TIMEOUT_MS || 120000),
    killSignal: "SIGTERM"
  });

  if (proc.error) {
    if (proc.error.code === "ETIMEDOUT") {
      throw new Error("Codex bridge timed out while waiting for a response.");
    }
    throw proc.error;
  }

  let payload = null;
  if (proc.stdout && proc.stdout.trim()) {
    try {
      payload = JSON.parse(proc.stdout);
    } catch {
      throw new Error(`Codex bridge returned invalid JSON: ${proc.stdout.trim()}`);
    }
  }

  if (proc.status !== 0) {
    const detail =
      payload?.message ||
      payload?.stderr_tail ||
      proc.stderr?.trim() ||
      proc.stdout?.trim() ||
      (proc.signal ? `Codex bridge terminated by ${proc.signal}` : "") ||
      `Codex bridge failed with exit code ${proc.status}`;
    throw new Error(detail);
  }

  const responseText = String(payload?.response || "").trim();
  if (!responseText) {
    throw new Error(`Codex bridge returned no response: ${proc.stdout?.trim() || "(empty)"}`);
  }

  return responseText;
}

function resolveFeishuSessionTarget(payload) {
  if (activeBackend !== "codex") {
    return "";
  }

  const message = payload?.event?.message || {};
  const sender = payload?.event?.sender?.sender_id?.open_id || "";
  const chatId = message?.chat_id || "";

  const candidates = [
    `chat:${chatId}`,
    `sender:${sender}`,
    chatId,
    sender
  ].map((item) => String(item).trim()).filter(Boolean);

  for (const key of candidates) {
    if (sessionMap[key]) {
      return sessionMap[key];
    }
  }

  return config.codexSessionTarget;
}

async function askBackend(userText, options = {}) {
  if (activeBackend === "anthropic") {
    return askAnthropic(userText);
  }
  if (activeBackend === "siliconflow") {
    return askSiliconFlow(userText);
  }
  if (activeBackend === "codex") {
    return askCodexBridge(userText, options.sessionTarget || "");
  }
  return askOpenAI(userText);
}

function scheduleFeishuReply(payload) {
  void (async () => {
    try {
      const message = payload.event?.message;
      const sender = payload.event?.sender?.sender_id?.open_id;
      const chatId = message?.chat_id;
      const userText = extractMessageText(message?.content);
      const sessionTarget = resolveFeishuSessionTarget(payload);
      const replyInput = await buildReplyInputFromMessage(userText);
      const intent = classifyReplyIntent(userText, replyInput);
      const prompt = buildReplyPrompt({
        intent,
        originalText: userText,
        replyInput
      });

      console.log("[feishu] processing", {
        chatId,
        sender,
        sessionTarget: sessionTarget || "(default)",
        docLinks: replyInput.docLinks?.length || 0,
        intent
      });

      if (replyInput.error && replyInput.docLinks?.length) {
        await sendFeishuMessage(
          chatId,
          "我看到了这个飞书文档链接，但现在还没读到正文。你可以把文档分享给我，或者直接把正文贴过来，我就能继续帮你审。"
        );
        return;
      }

      const reply = intent === "summary"
        ? await buildSummaryReply({
            chatId,
            messageId: message?.message_id || "",
            originalText: userText,
            sessionTarget
          })
        : await askBackend(prompt, { sessionTarget });
      await sendFeishuMessage(chatId, reply);
    } catch (error) {
      console.error("[feishu] background reply failed", error);
    }
  })();
}

async function handleFeishuEvent(payload, options = {}) {
  const source = String(options.source || "webhook").trim() || "webhook";
  const skipVerificationToken = Boolean(options.skipVerificationToken);
  console.log("[feishu] event received", {
    source,
    type: payload.type,
    eventType: payload.header?.event_type,
    eventId: payload.header?.event_id || payload.event_id || "",
  });
  if (
    !skipVerificationToken &&
    config.feishuVerificationToken &&
    payload.token &&
    payload.token !== config.feishuVerificationToken
  ) {
    throw new Error("Invalid verification token");
  }

  if (payload.type === "url_verification") {
    return { kind: "challenge", challenge: payload.challenge };
  }

  if (payload.header?.event_type !== "im.message.receive_v1") {
    return { kind: "ignored" };
  }

  markFeishuEventSeen(payload, source);

  const eventId = payload.header?.event_id || payload.event_id || "";
  if (eventId) {
    pruneProcessedEvents();
    if (processedEvents.has(eventId)) {
      return { kind: "duplicate" };
    }
    processedEvents.set(eventId, Date.now() + 10 * 60 * 1000);
  }

  const message = payload.event?.message;
  const sender = payload.event?.sender?.sender_id?.open_id;
  const chatId = message?.chat_id;
  const messageType = message?.message_type;

  if (!chatId || !sender) {
    return { kind: "ignored" };
  }

  const userText = extractMessageText(message.content);
  if (!userText) {
    console.log("[feishu] ignored empty text message");
    return { kind: "ignored" };
  }

  if (userText.startsWith(config.feishuDigestPrefix)) {
    console.log("[feishu] ignored digest message");
    return { kind: "ignored" };
  }

  recordChatMessage({
    chatId,
    sender,
    text: userText,
    eventId,
    messageId: message?.message_id || ""
  });

  const commandResult = await handleAdComboCommand(userText, chatId);
  if (commandResult.handled) {
    if (commandResult.reply) {
      void (async () => {
        try {
          await sendFeishuMessage(chatId, commandResult.reply);
        } catch (error) {
          console.error("[ad-combo] failed to send command reply", error);
        }
      })();
    }
    return { kind: "command_handled" };
  }

  const shouldShowRunIndicator = config.feishuRunIndicator && message?.message_id && isOwnerMessage(payload);
  if (shouldShowRunIndicator) {
    void (async () => {
      try {
        await addMessageReaction(message?.message_id || "");
      } catch (error) {
        console.error("[feishu] run indicator failed", error);
      }
    })();
  }

  const shouldReply = config.feishuReplyMode === "reply" || isOwnerMessage(payload) || isBotMentioned(payload);
  if (shouldReply) {
    scheduleFeishuReply(payload);
    return { kind: "queued" };
  }

  if (config.feishuRunIndicator) {
    void (async () => {
      try {
        await addMessageReaction(message?.message_id || "");
      } catch (error) {
        console.error("[feishu] run indicator failed", error);
      }
    })();
  }

  return { kind: "stored" };
}

function buildLongConnectionPayload(eventData) {
  const eventId =
    String(eventData?.header?.event_id || "").trim() ||
    String(eventData?.event_id || "").trim() ||
    String(eventData?.message?.message_id || "").trim() ||
    `ws-${Date.now()}`;

  return {
    header: {
      event_type: "im.message.receive_v1",
      event_id: eventId
    },
    event: eventData
  };
}

async function startFeishuLongConnection() {
  let Lark;
  try {
    Lark = await import("@larksuiteoapi/node-sdk");
  } catch (error) {
    feishuIngressState.lastError = `Failed to load Feishu SDK: ${
      error instanceof Error ? error.message : String(error)
    }`;
    console.error(`[feishu] ${feishuIngressState.lastError}`);
    return false;
  }

  try {
    const eventDispatcher = new Lark.EventDispatcher({}).register({
      "im.message.receive_v1": async (eventData) => {
        const payload = buildLongConnectionPayload(eventData);
        const result = await handleFeishuEvent(payload, {
          source: "long_connection",
          skipVerificationToken: true
        });
        console.log("[feishu] long-connection result", result);
      }
    });

    feishuWsClient = new Lark.WSClient({
      appId: config.feishuAppId,
      appSecret: config.feishuAppSecret,
      loggerLevel: Lark.LoggerLevel.info
    });
    await feishuWsClient.start({ eventDispatcher });

    feishuIngressState.activeMode = "long_connection";
    feishuIngressState.wsStartedAt = Date.now();
    feishuIngressState.lastError = "";
    console.log("[feishu] long connection start requested");
    return true;
  } catch (error) {
    feishuIngressState.lastError =
      error instanceof Error ? error.message : String(error);
    console.error("[feishu] failed to start long connection", error);
    return false;
  }
}

async function startFeishuIngress() {
  feishuIngressState.activeMode = "webhook";
  if (!["long_connection", "auto"].includes(config.feishuEventMode)) {
    return;
  }

  const started = await startFeishuLongConnection();
  if (!started && config.feishuEventMode === "long_connection") {
    console.warn("[feishu] long_connection mode failed to start; webhook endpoint remains available.");
  }
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);
    console.log(`[http] ${req.method} ${url.pathname}`);

    if (req.method === "GET" && url.pathname === "/health") {
        return json(res, 200, {
          ok: true,
          botName: config.botName,
          eventMode: feishuIngressState.activeMode,
          requestedEventMode: feishuIngressState.requestedMode,
          readAccessMode: config.feishuReadAccessMode,
          backend: activeBackend,
          model: activeModel,
          replyMode: config.feishuReplyMode,
          digestEnabled: config.feishuDigestEnabled,
          stateFile: config.feishuStateFile,
          userAuth: getFeishuUserAuthStatus(),
          chatCount: chatStates.size,
          lastEventAt: feishuIngressState.lastEventAt || null,
          lastEventId: feishuIngressState.lastEventId || null,
          lastEventType: feishuIngressState.lastEventType || null,
          lastEventSource: feishuIngressState.lastEventSource || null,
          longConnection: {
            startedAt: feishuIngressState.wsStartedAt || null,
            lastError: feishuIngressState.lastError || null,
            ...getWsReconnectInfo()
          },
          digestTargetChatId: config.feishuDigestTargetChatId || null,
          digestSchedule: `${String(config.feishuDigestHour).padStart(2, "0")}:${String(config.feishuDigestMinute).padStart(2, "0")}`
        });
    }

    if (req.method === "GET" && url.pathname === "/feishu/auth/status") {
      return json(res, 200, {
        ok: true,
        ...getFeishuUserAuthStatus()
      });
    }

    if (req.method === "GET" && url.pathname === "/feishu/auth/start") {
      const auth = startFeishuUserOauth();
      if (url.searchParams.get("redirect") === "1") {
        res.writeHead(302, { location: auth.authorizeUrl });
        return res.end();
      }
      return json(res, 200, {
        ok: true,
        mode: config.feishuReadAccessMode,
        redirectUri: config.feishuUserAuthRedirectUri,
        authorizeUrl: auth.authorizeUrl,
        expiresAt: auth.expiresAt
      });
    }

    if (req.method === "GET" && url.pathname === "/feishu/auth/callback") {
      const code = String(url.searchParams.get("code") || "").trim();
      const state = String(url.searchParams.get("state") || "").trim();
      const now = Date.now();

      if (!code) {
        return text(res, 400, "Missing code.");
      }

      if (
        feishuOauthState.value &&
        feishuOauthState.expiresAt > now &&
        state !== feishuOauthState.value
      ) {
        return text(res, 400, "Invalid state.");
      }

      try {
        await exchangeUserAccessToken(code);
        feishuOauthState = { value: "", expiresAt: 0 };
        return text(
          res,
          200,
          `Feishu user authorization succeeded for ${
            feishuUserTokenCache.name || feishuUserTokenCache.openId || "current user"
          }. You can return to Codex and continue.`
        );
      } catch (error) {
        return text(
          res,
          500,
          error instanceof Error ? error.message : String(error)
        );
      }
    }

    if (url.pathname === "/feishu/events" && req.method === "GET") {
      const challenge = url.searchParams.get("challenge") || "";
      return json(res, 200, {
        ok: true,
        challenge,
        message: "Feishu callback endpoint is reachable."
      });
    }

    if (req.method === "POST" && url.pathname === "/feishu/events") {
      const payload = await readBody(req);
      const result = await handleFeishuEvent(payload);
      console.log("[feishu] result", result);

      if (result.kind === "challenge") {
        return json(res, 200, { challenge: result.challenge });
      }

      return json(res, 200, { ok: true, result: result.kind });
    }

    if (req.method === "GET" && url.pathname === "/digest") {
      const chats = Array.from(chatStates.entries()).map(([chatId, state]) => ({
        chatId,
        messageCount: state.messages.length,
        pendingForDigest: Math.max(0, state.messages.length - state.lastDigestIndex),
        lastDigestAt: state.lastDigestAt || null,
        lastSeenAt: state.lastSeenAt || null,
        lastSender: state.lastSender || null,
        lastText: state.lastText || null
      }));
      return json(res, 200, {
        ok: true,
        replyMode: config.feishuReplyMode,
        digestEnabled: config.feishuDigestEnabled,
        digestTargetChatId: config.feishuDigestTargetChatId || null,
        digestSchedule: `${String(config.feishuDigestHour).padStart(2, "0")}:${String(config.feishuDigestMinute).padStart(2, "0")}`,
        chats
      });
    }

    if (req.method === "POST" && url.pathname === "/digest/run") {
      const results = await runDigestCycle();
      return json(res, 200, { ok: true, results });
    }

    if (req.method === "GET" && url.pathname === "/debug/latest-chat") {
      const chats = Array.from(chatStates.entries()).map(([chatId, state]) => ({
        chatId,
        lastSeenAt: state.lastSeenAt || null,
        lastSender: state.lastSender || null,
        lastText: state.lastText || null,
        pendingForDigest: Math.max(0, state.messages.length - state.lastDigestIndex)
      }));
      const latest = chats
        .filter((item) => item.lastSeenAt)
        .sort((a, b) => Number(b.lastSeenAt) - Number(a.lastSeenAt))[0] || null;
      return json(res, 200, {
        ok: true,
        latest,
        chats
      });
    }

    return text(res, 404, "Not Found");
  } catch (error) {
    console.error(error);
    return json(res, 500, {
      ok: false,
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

server.listen(config.port, config.host, () => {
  console.log(
    `Feishu Codex bridge listening on http://${config.host}:${config.port} using ${activeBackend}:${activeModel} eventMode=${config.feishuEventMode}`
  );
  scheduleNextDigestRun();
  void startFeishuIngress();
});
