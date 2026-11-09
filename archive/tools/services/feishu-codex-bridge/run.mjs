import { readFileSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { loadRuntimeEnv } from '../../lib/api-client.mjs';

const dir = dirname(fileURLToPath(import.meta.url));

// Literal dotenv values only. Never evaluate shell code from a configuration file.
export function parseEnv(text) {
  const values = {};
  for (const line of text.replace(/^\uFEFF/, '').split(/\r?\n/)) {
    const match = line.match(/^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$/);
    if (!match) continue;
    let value = match[2];
    if ((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))) value = value.slice(1, -1);
    else value = value.replace(/\s+#.*$/, '').trim();
    values[match[1]] = value;
  }
  return values;
}

export function launch(mode = 'bridge') {
  const env = { ...process.env };
  if (existsSync(join(dir, '.env'))) {
    for (const [key, value] of Object.entries(parseEnv(readFileSync(join(dir, '.env'), 'utf8')))) {
      if (env[key] === undefined) env[key] = value;
    }
  }
  // Shared platform-specific runtime configuration fills any remaining values.
  loadRuntimeEnv(env);
  let command, args;
  if (mode === 'bridge') {
    command = env.NODE_BIN || process.execPath;
    args = [join(dir, 'server.mjs')];
  } else if (mode === 'named-tunnel') {
    command = env.CLOUDFLARED_BIN || 'cloudflared';
    const config = resolve(dir, env.CLOUDFLARED_CONFIG_FILE || 'cloudflared/config.yml');
    if (!existsSync(config)) throw new Error(`Named tunnel config not found: ${config}`);
    args = ['tunnel', '--config', config, 'run'];
  } else if (mode === 'quick-tunnel') {
    command = env.CLOUDFLARED_BIN || 'cloudflared';
    args = ['tunnel', '--url', env.QUICK_TUNNEL_TARGET_URL ||
      `http://${env.QUICK_TUNNEL_TARGET_HOST || '127.0.0.1'}:${env.PORT || 3000}`];
  } else throw new Error(`Unknown mode: ${mode}`);
  const child = spawn(command, args, { cwd: dir, env, stdio: 'inherit' });
  child.on('error', error => { console.error(error.message); process.exitCode = 1; });
  child.on('exit', code => { process.exitCode = code ?? 1; });
  for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal));
  return child;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { launch(process.argv[2]); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
