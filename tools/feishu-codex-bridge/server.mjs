import http from "node:http";
import { URL } from "node:url";

const config = {
  port: Number(process.env.PORT || 3000),
  feishuAppId: process.env.FEISHU_APP_ID || "",
  feishuAppSecret: process.env.FEISHU_APP_SECRET || "",
  feishuVerificationToken: process.env.FEISHU_VERIFICATION_TOKEN || "",
  modelProvider: (process.env.MODEL_PROVIDER || "auto").toLowerCase(),
  openaiApiKey: process.env.OPENAI_API_KEY || "",
  openaiModel: process.env.OPENAI_MODEL || "gpt-5-mini",
  anthropicApiKey: process.env.ANTHROPIC_API_KEY || "",
  anthropicModel:
    process.env.ANTHROPIC_MODEL || "claude-3-5-haiku-latest",
  botName: process.env.BOT_NAME || "助手",
  systemPrompt:
    process.env.SYSTEM_PROMPT ||
    "你是一个中文优先、简洁、可靠的助手。优先直接回答；除非用户明确要求，否则不要给出过长步骤。"
};

function resolveProvider() {
  if (config.modelProvider === "auto") {
    if (config.anthropicApiKey) {
      return "anthropic";
    }
    return "openai";
  }
  return config.modelProvider;
}

const activeProvider = resolveProvider();
const activeModel =
  activeProvider === "anthropic" ? config.anthropicModel : config.openaiModel;

if (
  !config.feishuAppId ||
  !config.feishuAppSecret ||
  (activeProvider === "openai" && !config.openaiApiKey) ||
  (activeProvider === "anthropic" && !config.anthropicApiKey)
) {
  console.error(
    "Missing required env vars. Need FEISHU_APP_ID, FEISHU_APP_SECRET, and the API key for the selected provider."
  );
  process.exit(1);
}

if (!["auto", "openai", "anthropic"].includes(config.modelProvider)) {
  console.error("MODEL_PROVIDER must be one of: auto, openai, anthropic.");
  process.exit(1);
}

const processedEvents = new Map();
let feishuTokenCache = {
  token: "",
  expiresAt: 0
};

function json(res, status, body) {
  res.writeHead(status, { "content-type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(body));
}

function text(res, status, body) {
  res.writeHead(status, { "content-type": "text/plain; charset=utf-8" });
  res.end(body);
}

function pruneProcessedEvents() {
  const now = Date.now();
  for (const [key, expiresAt] of processedEvents.entries()) {
    if (expiresAt <= now) {
      processedEvents.delete(key);
    }
  }
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) {
    chunks.push(chunk);
  }
  const raw = Buffer.concat(chunks).toString("utf8");
  return raw ? JSON.parse(raw) : {};
}

function extractMessageText(messageContent) {
  try {
    const parsed = JSON.parse(messageContent);
    if (parsed.text) {
      return String(parsed.text).trim();
    }
  } catch {
    return String(messageContent || "").trim();
  }
  return "";
}

async function getTenantAccessToken() {
  const now = Date.now();
  if (feishuTokenCache.token && feishuTokenCache.expiresAt > now + 60_000) {
    return feishuTokenCache.token;
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

  feishuTokenCache = {
    token: data.tenant_access_token,
    expiresAt: now + Number(data.expire || 7200) * 1000
  };

  return feishuTokenCache.token;
}

async function sendFeishuMessage(chatId, content) {
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

  if (!response.ok) {
    throw new Error(`Send message failed: HTTP ${response.status}`);
  }

  const data = await response.json();
  if (data.code !== 0) {
    throw new Error(`Send message failed: ${JSON.stringify(data)}`);
  }
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

async function askModel(userText) {
  if (activeProvider === "anthropic") {
    return askAnthropic(userText);
  }
  return askOpenAI(userText);
}

async function handleFeishuEvent(payload) {
  if (
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

  if (!chatId || !sender || messageType !== "text") {
    return { kind: "ignored" };
  }

  const userText = extractMessageText(message.content);
  if (!userText) {
    return { kind: "ignored" };
  }

  const reply = await askModel(userText);
  await sendFeishuMessage(chatId, reply);
  return { kind: "replied" };
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);

    if (req.method === "GET" && url.pathname === "/health") {
        return json(res, 200, {
          ok: true,
          botName: config.botName,
          provider: activeProvider,
          model: activeModel
        });
    }

    if (req.method === "POST" && url.pathname === "/feishu/events") {
      const payload = await readBody(req);
      const result = await handleFeishuEvent(payload);

      if (result.kind === "challenge") {
        return json(res, 200, { challenge: result.challenge });
      }

      return json(res, 200, { ok: true, result: result.kind });
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

server.listen(config.port, () => {
  console.log(
    `Feishu Codex bridge listening on http://127.0.0.1:${config.port} using ${activeProvider}:${activeModel}`
  );
});
