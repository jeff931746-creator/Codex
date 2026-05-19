export const API_BASE_URLS = {
  siliconflow: "https://api.siliconflow.cn/v1",
  deepseek: "https://api.deepseek.com",
  openai: "https://api.openai.com/v1",
  anthropic: "https://api.anthropic.com/v1",
  feishu: "https://open.feishu.cn/open-apis",
  gemini: "https://generativelanguage.googleapis.com/v1beta/models"
};

export function apiUrl(provider, path = "") {
  const base = API_BASE_URLS[provider];
  if (!base) {
    throw new Error(`Unknown API provider: ${provider}`);
  }
  return path ? `${base.replace(/\/$/, "")}/${String(path).replace(/^\//, "")}` : base;
}

export async function apiFetch(provider, path = "", options = {}) {
  const { url, ...fetchOptions } = options;
  const response = await fetch(url || apiUrl(provider, path), fetchOptions);
  return response;
}

export async function apiJson(provider, path = "", options = {}) {
  const response = await apiFetch(provider, path, options);
  const text = await response.text();
  let body = text;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }
  if (!response.ok) {
    throw new Error(
      `${provider} request failed: HTTP ${response.status} ${
        typeof body === "string" ? body : JSON.stringify(body)
      }`
    );
  }
  return body || {};
}

export function jsonHeaders(extra = {}) {
  return {
    "content-type": "application/json",
    ...extra
  };
}
