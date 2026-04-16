# Gemma 4 Local Deployment Notes

This folder contains a minimal local deployment workflow for running Gemma 4
through Ollama on this machine.

## Recommended model for this Mac

- Machine: Apple M1 Pro
- Memory: 16 GB
- Recommended first model: `gemma4:e2b`
- Optional second step: `gemma4:e4b` if you can tolerate higher memory pressure

`gemma4:26b` and `gemma4:31b` are not a good fit for this machine as local
always-on models.

## Temporary runtime layout

To keep the workspace clean, the temporary Ollama runtime and model cache are
kept outside the repository:

- App bundle: `/tmp/Ollama.app`
- Ollama home: `/tmp/ollama-home`
- Model store: `/tmp/ollama-models`

## Persistent runtime layout

For a persistent install on this Mac:

- App bundle: `/Applications/Ollama.app`
- CLI symlink: `/usr/local/bin/ollama`
- Ollama home: `/Users/mt/.ollama`
- Model store: `/Users/mt/.ollama/models`
- launchd agent: `/Users/mt/Library/LaunchAgents/com.mt.ollama.plist`

## Scripts

- `install_tmp_ollama.sh`: downloads and unpacks Ollama to `/tmp/Ollama.app`
- `start_tmp_ollama.sh`: starts the local Ollama server on `127.0.0.1:11434`
- `pull_model.sh`: pulls a model tag such as `gemma4:e2b`
- `smoke_test_gemma4.sh`: sends a non-streaming chat request to the local API
- `stop_tmp_ollama.sh`: stops the temporary Ollama server process
- `cleanup_tmp_ollama.sh`: removes the temporary app bundle and model cache
- `com.mt.ollama.plist`: launchd template for a persistent Ollama service

## Typical flow

```bash
/Users/mt/Documents/Codex/tools/gemma4/install_tmp_ollama.sh
/Users/mt/Documents/Codex/tools/gemma4/start_tmp_ollama.sh
/Users/mt/Documents/Codex/tools/gemma4/pull_model.sh gemma4:e2b
/Users/mt/Documents/Codex/tools/gemma4/smoke_test_gemma4.sh gemma4:e2b
```

## Cleanup

```bash
/Users/mt/Documents/Codex/tools/gemma4/stop_tmp_ollama.sh
/Users/mt/Documents/Codex/tools/gemma4/cleanup_tmp_ollama.sh
```

## Persistent service notes

The persistent setup uses `launchd` to keep `ollama serve` running after login.
Its logs are written to:

- `/Users/mt/Library/Logs/Ollama/ollama.stdout.log`
- `/Users/mt/Library/Logs/Ollama/ollama.stderr.log`
