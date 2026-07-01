---
name: api-key-loading-quick-reference
description: neutral quick reference for loading local LLM provider keys when running project scripts
metadata:
  node_type: memory
  type: reference
---

# API Key Loading Quick Reference

Use this only for local scripts that call LLM providers through the shared `llm_client` path.
Verify current paths and provider names before running long jobs.

## Principle

- Do not copy LLM provider keys into project files.
- Do not hard-code keys or fallback defaults in scripts.
- Load keys from the local bridge/runtime environment before running scripts.
- Keep project memory and source files free of secrets.

## Typical local startup shape

```bash
set -a
source "$HOME/Library/Application Support/FeishuCodexBridge/bridge/.env"
set +a
export LLM_PROVIDER=deepseek
python3 path/to/script.py
```

## Script-side expectation

Prefer the shared client when available:

```python
from archive.tools.lib.llm_client import chat_text
```

If a script reports a missing provider key, check in order:

1. Whether the bridge/runtime env was sourced in the current shell.
2. Whether the target key exists in that env file.
3. Whether `LLM_PROVIDER` points to the intended provider.
4. Whether a subprocess lost exported environment variables.

## Archive

Full historical notes, including old model defaults and old rule pointers, were moved to:

`archived/reference_api_key_loading_full_2026-07-01.md`
