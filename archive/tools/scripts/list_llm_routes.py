#!/usr/bin/env python3
"""List managed LLM routes without printing secret values."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_repo_import_path(current_file: str | Path) -> None:
    """Allow scripts under archive/tools/** to import archive.tools.lib."""
    path = Path(current_file).resolve()
    for parent in [path.parent, *path.parents]:
        if (parent / "archive" / "tools" / "lib").is_dir():
            root = str(parent)
            if root not in sys.path:
                sys.path.insert(0, root)
            return


ensure_repo_import_path(__file__)

from archive.tools.lib.model_registry import iter_model_routes, key_is_configured  # noqa: E402


def main() -> int:
    for route in iter_model_routes():
        key_status = "configured" if key_is_configured(route) else "missing"
        print(f"{route.route}")
        print(f"  provider: {route.provider}")
        print(f"  model: {route.model}")
        print(f"  key_env: {route.key_env} ({key_status})")
        print(f"  base_url_env: {route.base_url_env}")
        if route.description:
            print(f"  description: {route.description}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
