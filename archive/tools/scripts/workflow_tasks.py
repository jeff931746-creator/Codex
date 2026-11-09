#!/usr/bin/env python3
"""Portable launchers: build theme library, approve push, or inspect stale changes."""
from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=check, text=True, encoding="utf-8", errors="replace", capture_output=True)


def check_dirty(hours: float) -> int:
    result = git("status", "--porcelain=v1", "-z", check=False)
    if result.returncode:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    records = iter(result.stdout.split("\0"))
    changed: list[str] = []
    for record in records:
        if not record or record.startswith("??"):
            continue
        changed.append(record[3:])
        if record[0] in "RC" or record[1] in "RC":
            next(records, None)
    stale = []
    for name in changed:
        path = ROOT / name
        if path.is_file() and time.time() - path.stat().st_mtime > hours * 3600:
            stale.append(name)
    if stale:
        print(f"工作区有 {len(stale)} 个文件修改后超过 {hours:g} 小时未提交：")
        for name in stale:
            print(name)
    else:
        print("未发现超过指定时间的未提交文件。")
    return 0


def approve_push() -> int:
    result = git("rev-list", "origin/main..main", "--count", check=False)
    if result.returncode:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    marker = ROOT / "archive/tools/scripts/_logs/.pending_push"
    if not int(result.stdout.strip()):
        print("没有待 push 的 commit。")
        marker.unlink(missing_ok=True)
        return 0
    print(git("log", "origin/main..main", "--oneline").stdout)
    if marker.exists():
        print(marker.read_text(encoding="utf-8"))
    if input("确认 push 到 origin/main? [y/N] ").strip().lower() != "y":
        print("已取消。")
        return 0
    result = subprocess.run(["git", "-C", str(ROOT), "push", "origin", "main"])
    if result.returncode == 0:
        marker.unlink(missing_ok=True)
    return result.returncode


def build(background: bool, yes: bool) -> int:
    if not os.environ.get("SILICONFLOW_API_KEY"):
        print("请先设置 SILICONFLOW_API_KEY 环境变量。", file=sys.stderr)
        return 2
    print(f"输出：{ROOT / 'archive/资料/历史题材库'}")
    if not yes and input("确认开始运行（会调用付费 API）？[y/N] ").strip().lower() != "y":
        return 0
    env = os.environ.copy()
    env.update(LLM_ROUTE="SiliconFlow_DeepSeek_Flash", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    script = Path(__file__).with_name("build_historical_theme_library.py")
    if not background:
        return subprocess.run([sys.executable, str(script)], cwd=ROOT, env=env).returncode
    log_dir = ROOT / "workspace/tmp/theme-library"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / ("theme_library_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log")
    kwargs = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS} if os.name == "nt" else {"start_new_session": True}
    with log_path.open("ab") as log:
        process = subprocess.Popen([sys.executable, str(script)], cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, **kwargs)
    print(f"已启动 PID={process.pid}，日志：{log_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("check-dirty")
    p.add_argument("--hours", type=float, default=24)
    sub.add_parser("approve-push")
    p = sub.add_parser("build-theme")
    p.add_argument("--background", action="store_true")
    p.add_argument("--yes", action="store_true", help="Already authorized paid API usage")
    args = parser.parse_args()
    if args.action == "check-dirty":
        return check_dirty(args.hours)
    if args.action == "approve-push":
        return approve_push()
    return build(args.background, args.yes)


if __name__ == "__main__":
    raise SystemExit(main())
