#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
SESSION_INDEX = CODEX_HOME / "session_index.jsonl"
DEFAULT_WORKDIR = Path(os.environ.get("CODEX_BRIDGE_WORKDIR", "/Users/mt/Documents/Codex"))
STATE_DIR = Path(
    os.environ.get(
        "CODEX_BRIDGE_STATE_DIR",
        Path(__file__).resolve().parent / ".state",
    )
)
STATE_FILE = STATE_DIR / "codex-desktop-bridge-state.json"


@dataclass
class SessionRecord:
    session_id: str
    thread_name: str
    updated_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "thread_name": self.thread_name,
            "updated_at": self.updated_at,
            "session_file": find_session_file(self.session_id),
        }


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_updated_at(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    if "." in normalized:
        head, tail = normalized.split(".", 1)
        tz_pos = max(tail.find("+"), tail.find("-"))
        if tz_pos != -1:
            fraction = tail[:tz_pos]
            tz = tail[tz_pos:]
            fraction = (fraction + "000000")[:6]
            normalized = f"{head}.{fraction}{tz}"
    return datetime.fromisoformat(normalized)


def codex_bin() -> str:
    return os.environ.get("CODEX_BIN") or shutil.which("codex") or "/Applications/Codex.app/Contents/Resources/codex"


def load_session_index() -> list[SessionRecord]:
    if not SESSION_INDEX.exists():
        raise SystemExit(f"Session index not found: {SESSION_INDEX}")

    latest_by_id: dict[str, SessionRecord] = {}
    with SESSION_INDEX.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            session_id = str(payload.get("id", "")).strip()
            if not session_id:
                continue
            record = SessionRecord(
                session_id=session_id,
                thread_name=str(payload.get("thread_name", "")).strip() or "(untitled)",
                updated_at=str(payload.get("updated_at", "")).strip() or now_iso(),
            )
            existing = latest_by_id.get(session_id)
            if existing is None or parse_updated_at(record.updated_at) >= parse_updated_at(existing.updated_at):
                latest_by_id[session_id] = record

    return sorted(latest_by_id.values(), key=lambda item: parse_updated_at(item.updated_at), reverse=True)


def find_session_file(session_id: str) -> str | None:
    pattern = f"*-{session_id}.jsonl"
    matches = list((CODEX_HOME / "sessions").rglob(pattern))
    if not matches:
        return None
    return str(sorted(matches)[-1])


def resolve_target(target: str, records: list[SessionRecord]) -> SessionRecord:
    needle = target.strip()
    if not needle:
        raise ValueError("Target cannot be empty.")

    exact_id = [item for item in records if item.session_id == needle]
    if exact_id:
        return exact_id[0]

    exact_name = [item for item in records if item.thread_name == needle]
    if len(exact_name) == 1:
        return exact_name[0]

    lowered = needle.lower()
    partial = [
        item
        for item in records
        if lowered in item.session_id.lower() or lowered in item.thread_name.lower()
    ]
    if len(partial) == 1:
        return partial[0]
    if not partial:
        raise ValueError(f"No Codex Desktop session matched: {needle}")

    raise ValueError(
        "Multiple Codex Desktop sessions matched: "
        + ", ".join(f"{item.thread_name} ({item.session_id})" for item in partial[:8])
    )


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> dict[str, Any] | None:
    if not STATE_FILE.exists():
        return None
    with STATE_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(session: SessionRecord) -> dict[str, Any]:
    ensure_state_dir()
    payload = {
        "selected_session_id": session.session_id,
        "selected_thread_name": session.thread_name,
        "selected_updated_at": session.updated_at,
        "selected_at": now_iso(),
    }
    with STATE_FILE.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return payload


def clear_state() -> bool:
    if not STATE_FILE.exists():
        return False
    STATE_FILE.unlink()
    return True


def selected_record(records: list[SessionRecord]) -> SessionRecord | None:
    state = load_state()
    if not state:
        return None
    selected_id = str(state.get("selected_session_id", "")).strip()
    for item in records:
        if item.session_id == selected_id:
            return item
    return None


def emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    if "message" in payload:
        print(payload["message"])
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_list(args: argparse.Namespace) -> int:
    records = load_session_index()
    selected = selected_record(records)

    if args.query:
        lowered = args.query.lower()
        records = [
            item
            for item in records
            if lowered in item.thread_name.lower() or lowered in item.session_id.lower()
        ]

    limited = records[: args.limit]
    payload = {
        "status": "ok",
        "count": len(limited),
        "selected_session_id": selected.session_id if selected else None,
        "sessions": [
            {
                "index": idx + 1,
                **item.as_dict(),
                "selected": bool(selected and selected.session_id == item.session_id),
            }
            for idx, item in enumerate(limited)
        ],
    }
    emit(payload, args.json)
    return 0


def cmd_select(args: argparse.Namespace) -> int:
    records = load_session_index()
    record = resolve_target(args.target, records)
    state = save_state(record)
    payload = {
        "status": "ok",
        "selected": {
            **record.as_dict(),
            "selected_at": state["selected_at"],
        },
    }
    emit(payload, args.json)
    return 0


def cmd_current(args: argparse.Namespace) -> int:
    records = load_session_index()
    record = selected_record(records)
    if not record:
        payload = {"status": "empty", "message": "No Codex Desktop session is currently selected."}
        emit(payload, args.json)
        return 1
    payload = {"status": "ok", "selected": record.as_dict()}
    emit(payload, args.json)
    return 0


def cmd_clear(args: argparse.Namespace) -> int:
    removed = clear_state()
    payload = {
        "status": "ok",
        "cleared": removed,
        "message": "Cleared current Codex Desktop selection." if removed else "No Codex Desktop selection was stored.",
    }
    emit(payload, args.json)
    return 0


def load_message(args: argparse.Namespace) -> str:
    if args.message and args.message_file:
        raise ValueError("Use either --message or --message-file, not both.")
    if args.message:
        return args.message
    if args.message_file:
        return Path(args.message_file).read_text(encoding="utf-8")
    raise ValueError("A message is required. Use --message or --message-file.")


def session_file_path(record: SessionRecord) -> Path | None:
    path = find_session_file(record.session_id)
    return Path(path) if path else None


def join_text_blocks(blocks: Iterable[dict[str, Any]]) -> str:
    parts: list[str] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        block_type = str(block.get("type", "")).strip()
        if block_type in {"input_text", "output_text", "text"}:
            text = str(block.get("text", ""))
            if text:
                parts.append(text)
    return "".join(parts).strip()


def parse_session_messages(path: Path, limit: int) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "response_item":
                continue
            payload = obj.get("payload", {})
            if not isinstance(payload, dict) or payload.get("type") != "message":
                continue
            role = str(payload.get("role", "")).strip()
            if role not in {"user", "assistant"}:
                continue
            content = payload.get("content", [])
            text = join_text_blocks(content if isinstance(content, list) else [])
            if not text:
                continue
            entries.append(
                {
                    "timestamp": obj.get("timestamp"),
                    "role": role,
                    "phase": payload.get("phase"),
                    "text": text,
                }
            )
    if limit <= 0:
        return []
    return entries[-limit:]


def format_readable_messages(messages: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for item in messages:
        timestamp = str(item.get("timestamp", "")).strip()
        role = str(item.get("role", "")).strip()
        phase = str(item.get("phase", "")).strip()
        header = f"[{timestamp}] {role}"
        if phase:
            header += f" ({phase})"
        lines.append(header)
        lines.append(str(item.get("text", "")).rstrip())
        lines.append("")
    return "\n".join(lines).rstrip()


def cmd_read(args: argparse.Namespace) -> int:
    records = load_session_index()
    if args.session:
        record = resolve_target(args.session, records)
    else:
        record = selected_record(records)
        if not record:
            raise ValueError("No current Codex Desktop session is selected. Run select first or pass --session.")

    path = session_file_path(record)
    if not path or not path.exists():
        payload = {
            "status": "error",
            "message": f"No session transcript found for {record.session_id}.",
            "session": record.as_dict(),
        }
        emit(payload, args.json)
        return 1

    messages = parse_session_messages(path, args.limit)
    payload = {
        "status": "ok",
        "session": record.as_dict(),
        "count": len(messages),
        "messages": messages,
        "transcript": format_readable_messages(messages),
    }
    emit(payload, args.json)
    return 0


def cmd_send(args: argparse.Namespace) -> int:
    records = load_session_index()
    if args.session:
        record = resolve_target(args.session, records)
    else:
        record = selected_record(records)
        if not record:
            raise ValueError("No current Codex Desktop session is selected. Run select first or pass --session.")

    message = load_message(args)
    save_state(record)

    with tempfile.TemporaryDirectory(prefix="codex-bridge-", dir="/tmp") as temp_dir:
        last_message_file = Path(temp_dir) / "last-message.txt"
        stdout_file = Path(temp_dir) / "stdout.txt"
        stderr_file = Path(temp_dir) / "stderr.txt"
        cmd = [
            codex_bin(),
            "-C",
            str(DEFAULT_WORKDIR),
            "exec",
            "resume",
            record.session_id,
            message,
            "-o",
            str(last_message_file),
        ]
        proc = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            check=False,
        )
        stdout_file.write_text(proc.stdout, encoding="utf-8")
        stderr_file.write_text(proc.stderr, encoding="utf-8")

        response_text = last_message_file.read_text(encoding="utf-8").strip() if last_message_file.exists() else ""
        payload = {
            "status": "ok" if proc.returncode == 0 else "error",
            "session": record.as_dict(),
            "response": response_text,
            "returncode": proc.returncode,
            "stdout_tail": tail_text(proc.stdout),
            "stderr_tail": tail_text(proc.stderr),
        }
        if proc.returncode != 0:
            emit(payload, args.json)
            return proc.returncode or 1

        emit(payload, args.json)
        return 0


def tail_text(value: str, max_chars: int = 1200) -> str:
    stripped = value.strip()
    if len(stripped) <= max_chars:
        return stripped
    return stripped[-max_chars:]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bridge local Codex Desktop sessions for OpenClaw chat surfaces.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List Codex Desktop sessions from ~/.codex/session_index.jsonl")
    list_parser.add_argument("--limit", type=int, default=8)
    list_parser.add_argument("--query", default="")
    list_parser.add_argument("--json", action="store_true")
    list_parser.set_defaults(func=cmd_list)

    select_parser = subparsers.add_parser("select", help="Select a Codex Desktop session by id or thread name")
    select_parser.add_argument("--target", required=True)
    select_parser.add_argument("--json", action="store_true")
    select_parser.set_defaults(func=cmd_select)

    current_parser = subparsers.add_parser("current", help="Show the currently selected Codex Desktop session")
    current_parser.add_argument("--json", action="store_true")
    current_parser.set_defaults(func=cmd_current)

    clear_parser = subparsers.add_parser("clear", help="Clear the currently selected Codex Desktop session")
    clear_parser.add_argument("--json", action="store_true")
    clear_parser.set_defaults(func=cmd_clear)

    send_parser = subparsers.add_parser("send", help="Send a prompt into a Codex Desktop session via codex exec resume")
    send_parser.add_argument("--session")
    send_parser.add_argument("--message")
    send_parser.add_argument("--message-file")
    send_parser.add_argument("--json", action="store_true")
    send_parser.set_defaults(func=cmd_send)

    read_parser = subparsers.add_parser("read", help="Read the latest messages from a Codex Desktop session transcript")
    read_parser.add_argument("--session")
    read_parser.add_argument("--limit", type=int, default=12)
    read_parser.add_argument("--json", action="store_true")
    read_parser.set_defaults(func=cmd_read)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        payload = {"status": "error", "message": str(exc)}
        emit(payload, getattr(args, "json", False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
