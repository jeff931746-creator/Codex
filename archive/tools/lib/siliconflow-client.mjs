import { API_BASE_URLS, apiJson, envValue, jsonHeaders } from "./api-client.mjs";

export const DEFAULT_SILICONFLOW_BASE_URL = API_BASE_URLS.siliconflow;
export const DEFAULT_SILICONFLOW_MODEL = "deepseek-ai/DeepSeek-V3";

export function resolveSiliconFlowConfig(env = process.env) {
  return {
    apiKey: envValue("SILICONFLOW_API_KEY", "", env),
    model: envValue("SILICONFLOW_MODEL", DEFAULT_SILICONFLOW_MODEL, env),
    baseUrl: envValue("SILICONFLOW_BASE_URL", DEFAULT_SILICONFLOW_BASE_URL, env).replace(/\/$/, "")
  };
}

export async function askSiliconFlowChat({
  userText,
  systemPrompt = "",
  apiKey,
  model,
  baseUrl,
  maxTokens,
  temperature = 0.3
}) {
  if (!apiKey) {
    throw new Error("SILICONFLOW_API_KEY is not set.");
  }

  const data = await apiJson("siliconflow", "chat/completions", {
    url: `${baseUrl.replace(/\/$/, "")}/chat/completions`,
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      ...jsonHeaders()
    },
    body: JSON.stringify({
      model,
      messages: [
        ...(systemPrompt ? [{ role: "system", content: systemPrompt }] : []),
        { role: "user", content: userText }
      ],
      ...(maxTokens ? { max_tokens: maxTokens } : {}),
      temperature
    })
  });
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
