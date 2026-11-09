#!/usr/bin/env python3
"""Generate local hook commands and check Windows prerequisites; no installation."""
from __future__ import annotations
import argparse
import copy
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def quote_command(parts: list[str], windows: bool | None = None) -> str:
    windows = os.name == 'nt' if windows is None else windows
    if windows:
        # Hook configuration is a shell command string, not CreateProcess argv.
        if any(any(c in part for c in '%!"\r\n') for part in parts):
            raise ValueError('Hook command paths cannot contain %, !, quotes or newlines; use a simpler checkout/Python directory.')
        return ' '.join('"' + part + '"' for part in parts)
    return shlex.join(parts)


def render_hooks(runtime: str, *, absolute: bool = True) -> dict:
    config = json.loads((ROOT / '.agents/hooks.json').read_text(encoding='utf-8'))
    config = copy.deepcopy(config)
    runner = str(ROOT / '.agents/hooks/run-hook.py') if absolute else '.agents/hooks/run-hook.py'
    executable = sys.executable if absolute else 'python'
    for events in config['hooks'].values():
        for event in events:
            for hook in event['hooks']:
                # The checked-in templates always end with the Python hook filename.
                target = hook['command'].split()[-1]
                hook['command'] = quote_command([executable, '-X', 'utf8', runner,
                                                 '--runtime', runtime, target])
    return config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', choices=['codex', 'claude', 'agent'], default='codex')
    parser.add_argument('--output', type=Path, help='Generated JSON destination; defaults to workspace/tmp/runtime-config')
    parser.add_argument('--check', action='store_true', help='Check prerequisites only; do not write files')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error('Python 3.10+ is required')
    print(f'Workspace: {ROOT}')
    for command in ('git', 'node', 'npm', 'cloudflared', 'ollama'):
        print(f'{command}: {shutil.which(command) or "not on PATH (required only by relevant tools)"}')
    if args.check:
        return 0
    output = (args.output or ROOT / 'workspace/tmp/runtime-config' / f'{args.runtime}-hooks.json').expanduser().resolve()
    # Follow the same write guard as the rest of this workspace.
    guard_path = ROOT / 'tools/workspace-guard/check_paths.py'
    result = subprocess.run([sys.executable, str(guard_path), str(output)])
    if result.returncode:
        return result.returncode
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(render_hooks(args.runtime), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Generated {output}; merge its hooks into the runtime settings using that runtime\'s supported configuration.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
