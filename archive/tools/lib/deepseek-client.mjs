import { apiJson, apiFetch, jsonHeaders } from "./api-client.mjs";

export const DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash";

export function resolveDeepSeekConfig(env = process.env) {
  return {
    apiKey: env.DEEPSEEK_API_KEY || "",
    model: env.DEEPSEEK_MODEL || DEFAULT_DEEPSEEK_MODEL
  };
}

export async function askDeepSeekChat({
  messages,
  userText,
  systemPrompt = "",
  apiKey,
  model = DEFAULT_DEEPSEEK_MODEL,
  maxTokens,
  temperature,
  thinking,
  stream = false,
  extra = {}
}) {
  if (!apiKey) {
    throw new Error("DEEPSEEK_API_KEY is not set.");
  }

  const resolvedMessages = messages || [
    ...(systemPrompt ? [{ role: "system", content: systemPrompt }] : []),
    { role: "user", content: userText || "" }
  ];
  const resolvedThinking = thinking === undefined ? { type: "disabled" } : thinking;
  const payload = {
    model,
    messages: resolvedMessages,
    ...(maxTokens ? { max_tokens: maxTokens } : {}),
    ...(temperature !== undefined ? { temperature } : {}),
    ...(stream ? { stream: true } : {}),
    ...(resolvedThinking ? { thinking: resolvedThinking } : {}),
    ...extra
  };
  const requestOptions = {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      ...jsonHeaders()
    },
    body: JSON.stringify(payload)
  };

  if (stream) {
    const response = await apiFetch("deepseek", "chat/completions", requestOptions);
    if (!response.ok) {
      throw new Error(`DeepSeek request failed: HTTP ${response.status}`);
    }
    return readStreamText(await response.text());
  }

  const data = await apiJson("deepseek", "chat/completions", requestOptions);
  const message = data.choices?.[0]?.message || {};
  const content = message.content || message.reasoning_content || "";
  if (!content.trim()) {
    throw new Error(`No DeepSeek output text: ${JSON.stringify(data)}`);
  }
  return content.trim();
}

function readStreamText(text) {
  const chunks = [];
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line === "data: [DONE]" || !line.startsWith("data: ")) {
      continue;
    }
    try {
      const obj = JSON.parse(line.slice(6));
      const delta = obj.choices?.[0]?.delta?.content || "";
      if (delta) {
        chunks.push(delta);
      }
    } catch {
      // Ignore malformed stream chunks.
    }
  }
  return chunks.join("").trim();
}
