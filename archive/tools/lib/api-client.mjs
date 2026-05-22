import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

export const API_BASE_URLS = {
  siliconflow: "https://api.siliconflow.cn/v1",
  deepseek: "https://api.deepseek.com",
  openai: "https://api.openai.com/v1",
  anthropic: "https://api.anthropic.com/v1",
  feishu: "https://open.feishu.cn/open-apis",
  gemini: "https://generativelanguage.googleapis.com/v1beta/models"
};

const DEFAULT_RUNTIME_ENV_PATH = join(
  homedir(),
  "Library/Application Support/FeishuCodexBridge/bridge/.env"
);
let runtimeEnvLoaded = false;

function runtimeEnvPath(env = process.env) {
  return env.CODEX_RUNTIME_ENV_PATH || DEFAULT_RUNTIME_ENV_PATH;
}

function parseEnvLine(line) {
  let trimmed = line.trim();
  if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) {
    return null;
  }
  if (trimmed.startsWith("export ")) {
    trimmed = trimmed.slice("export ".length).trimStart();
  }
  const separatorIndex = trimmed.indexOf("=");
  const key = trimmed.slice(0, separatorIndex).trim();
  let value = trimmed.slice(separatorIndex + 1).trim();
  if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(key)) {
    return null;
  }
  if (
    value.length >= 2 &&
    ((value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'")))
  ) {
    value = value.slice(1, -1);
  }
  return { key, value };
}

export function loadRuntimeEnv(env = process.env) {
  if (runtimeEnvLoaded) {
    return;
  }
  runtimeEnvLoaded = true;

  const path = runtimeEnvPath(env);
  if (!existsSync(path)) {
    return;
  }

  for (const line of readFileSync(path, "utf8").split(/\r?\n/)) {
    const parsed = parseEnvLine(line);
    if (!parsed || !parsed.value || Object.hasOwn(env, parsed.key)) {
      continue;
    }
    env[parsed.key] = parsed.value;
  }
}

export function envValue(name, defaultValue = "", env = process.env) {
  loadRuntimeEnv(env);
  return env[name] || defaultValue;
}

export function apiUrl(provider, path = "") {
  loadRuntimeEnv();
  const base = API_BASE_URLS[provider];
  if (!base) {
    throw new Error(`Unknown API provider: ${provider}`);
  }
  const envBase =
    process.env[`${provider.toUpperCase().replace(/-/g, "_")}_BASE_URL`] || base;
  return path
    ? `${envBase.replace(/\/$/, "")}/${String(path).replace(/^\//, "")}`
    : envBase;
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
