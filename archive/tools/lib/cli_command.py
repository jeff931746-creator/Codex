"""Resolve executable argument prefixes without invoking Windows batch shells."""
from __future__ import annotations

from pathlib import Path
import re
import shutil


def command_prefix(executable: str) -> list[str]:
    """Use the Node entry named by a standard npm shim, keeping arguments literal.

    Unknown batch wrappers are rejected rather than passing JSON, URLs or messages
    through cmd.exe, whose quoting rules differ from executable argv handling.
    """
    resolved = shutil.which(executable) or executable
    shim = Path(resolved).expanduser()
    if shim.suffix.lower() not in {".cmd", ".bat"}:
        return [str(shim)]
    if not shim.is_file():
        raise FileNotFoundError(f"CLI batch shim not found: {shim}")
    text = shim.read_text(encoding="utf-8-sig")
    entries = re.findall(r'"%(?:dp0%|~dp0)[\\/]([^"\r\n]+?\.(?:[cm]?js))"', text, re.IGNORECASE)
    node = shutil.which("node")
    if node and Path(node).suffix.lower() in {".cmd", ".bat"}:
        node = None
    for relative in entries:
        entry = (shim.parent / relative.replace("\\", "/")).resolve()
        if node and entry.is_file():
            return [node, str(entry)]
    raise RuntimeError(
        f"Cannot safely resolve npm JavaScript entry for {shim}. "
        "Install Node and the CLI's standard npm shim, or configure a native executable."
    )
