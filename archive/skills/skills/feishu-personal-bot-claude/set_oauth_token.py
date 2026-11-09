#!/usr/bin/env python3
"""Store a Claude OAuth token without clipboard commands or secret argv values.

Run `claude setup-token` first, then paste the token at this script's hidden
prompt. Restart the relevant bridge explicitly after updating credentials.
"""
from __future__ import annotations

import argparse
import getpass
import json
from pathlib import Path
import shutil
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdin", action="store_true", help="Read token from stdin instead of a hidden prompt")
    parser.add_argument("--settings", type=Path, default=Path.home() / ".claude/settings.json")
    args = parser.parse_args()
    token = "".join((sys.stdin.read() if args.stdin else getpass.getpass("Claude OAuth token（不回显）: ")).split())
    if len(token) < 50:
        parser.error("Token too short; copy the complete setup-token output")
    path = args.settings.expanduser()
    data = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
    if not isinstance(data, dict) or not isinstance(data.get("env", {}), dict):
        parser.error("settings.json and its env must be JSON objects")
    if path.exists():
        shutil.copy2(path, str(path) + ".bak")
    path.parent.mkdir(parents=True, exist_ok=True)
    data.setdefault("env", {})["CLAUDE_CODE_OAUTH_TOKEN"] = token
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("已更新 env.CLAUDE_CODE_OAUTH_TOKEN。请重启使用此认证的 bridge profile。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
