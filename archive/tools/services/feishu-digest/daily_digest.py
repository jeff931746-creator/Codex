#!/usr/bin/env python3
"""Collect unread group messages, summarize, and send to an explicitly configured chat."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

BASE = Path(__file__).resolve().parent
TZ = dt.timezone(dt.timedelta(hours=8))


def cli(name: str, env_name: str) -> list[str]:
    binary = os.environ.get(env_name) or shutil.which(name)
    if not binary:
        raise RuntimeError(f'{name} not found; set {env_name} or add it to PATH')
    wrapper = Path(binary)
    if os.name == 'nt' and wrapper.suffix.lower() in {'.cmd', '.bat'}:
        match = re.search(r'%dp0%[\\/]([^"\r\n]+\.(?:js|mjs|cjs))"', wrapper.read_text(encoding='utf-8'))
        node = shutil.which('node')
        if not match or not node:
            raise RuntimeError(f'{name}: set {env_name} to a real executable or reinstall the npm CLI')
        return [node, str(wrapper.parent / match.group(1).replace('\\', '/'))]
    return [binary]


def run(command: list[str], timeout: int = 120) -> str:
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'{Path(command[0]).name} failed (exit {result.returncode}): {result.stderr[:300]}')
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chat-id', default=os.environ.get('BOT_CHAT_ID', ''), help='Destination chat; required unless BOT_CHAT_ID is set')
    parser.add_argument('--state-dir', type=Path, default=Path(os.environ.get('FEISHU_DIGEST_STATE_DIR', str(BASE / '.state'))))
    args = parser.parse_args()
    if not args.chat_id:
        parser.error('Set --chat-id or BOT_CHAT_ID to authorize the destination')
    lark = cli('lark-cli', 'LARK_BIN')
    claude = cli('claude', 'CLAUDE_BIN')
    args.state_dir.mkdir(parents=True, exist_ok=True)
    state_file = args.state_dir / 'last_read.json'
    state = json.loads(state_file.read_text(encoding='utf-8')) if state_file.exists() else {}
    new_state = dict(state)
    chats = [json.loads(line) for line in run(lark + ['im', 'chats', 'list', '--as', 'user', '--page-all', '--format', 'ndjson']).splitlines() if line.strip()]
    yesterday = dt.datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0) - dt.timedelta(days=1)
    sections = []
    for chat in chats:
        chat_id = chat['chat_id']
        start = int(state.get(chat_id, int(yesterday.timestamp())))
        latest = start
        lines = []
        page_token = ''
        try:
            while True:
                params = {'container_id_type': 'chat', 'container_id': chat_id,
                          'sort_type': 'ByCreateTimeAsc', 'start_time': str(start), 'page_size': 50}
                if page_token:
                    params['page_token'] = page_token
                raw = json.loads(run(lark + ['api', 'GET', '/open-apis/im/v1/messages', '--as', 'user', '--params', json.dumps(params)], 30))
                if raw.get('code', 0) != 0:
                    raise RuntimeError(f"API returned code {raw['code']}")
                data = raw.get('data', {})
                for message in data.get('items', []):
                    created = int(message.get('create_time', 0)) // 1000
                    latest = max(latest, created)
                    if message.get('deleted') or message.get('sender', {}).get('sender_type', '') in {'', 'app'}:
                        continue
                    body = message.get('body', {}).get('content', '')
                    try:
                        content = json.loads(body)
                        if isinstance(content, dict) and 'zh_cn' in content:
                            text = ' '.join(e.get('text', '') for p in content['zh_cn'].get('content', []) for e in p if e.get('tag') == 'text')
                        else:
                            text = content.get('text', '') if isinstance(content, dict) else str(content)
                    except (ValueError, TypeError):
                        text = body
                    if text.strip():
                        stamp = dt.datetime.fromtimestamp(created, TZ).strftime('%m-%d %H:%M')
                        lines.append(f'[{stamp}] {text.strip()}')
                if not data.get('has_more'):
                    break
                next_token = data.get('page_token', '')
                if not next_token or next_token == page_token:
                    raise RuntimeError('Invalid pagination token')
                page_token = next_token
        except (RuntimeError, ValueError) as error:
            print(f"Skipping {chat.get('name', chat_id)}: {error}")
            continue
        if lines:
            sections.append(f"【{chat.get('name', chat_id)}】\n" + '\n'.join(lines))
        # API timestamps are seconds. Move past the consumed second to avoid repeats.
        if latest > start:
            new_state[chat_id] = str(latest + 1)
    if sections:
        today = dt.datetime.now(TZ).date().isoformat()
        prompt = (f'以下为飞书群未读消息。只依据这些记录，用中文生成 {today} 飞书群消息日报，'
                  '按群提炼重要决策、进展和待办，跳过闲聊，800字以内。资料未覆盖的不要补充。\n\n' + '\n\n'.join(sections))
        summary = run(claude + ['-p', prompt], 300).strip()
        if not summary:
            raise RuntimeError('Summary was empty; read progress is unchanged')
        print(run(lark + ['im', '+messages-send', '--chat-id', args.chat_id, '--as', 'bot', '--markdown', summary]))
    # Commit read progress only after a successful send (or no relevant messages).
    temporary = state_file.with_suffix('.tmp')
    temporary.write_text(json.dumps(new_state, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(state_file)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
