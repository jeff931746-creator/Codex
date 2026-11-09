"""CLI argument safety tests; no network or real CLI commands are executed."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from archive.tools.lib.cli_command import command_prefix


class CliCommandTests(unittest.TestCase):
    def test_native_executable_stays_one_argument(self):
        with patch("archive.tools.lib.cli_command.shutil.which", return_value="C:/Program Files/Codex/codex.exe"):
            self.assertEqual(command_prefix("codex"), [str(Path("C:/Program Files/Codex/codex.exe"))])

    @unittest.skipUnless(shutil.which("node"), "Node is required for the argv integration check")
    def test_npm_shim_runs_node_and_preserves_json_and_shell_characters(self):
        node = shutil.which("node")
        with tempfile.TemporaryDirectory(prefix="CLI 中文 ") as directory:
            root = Path(directory)
            entry = root / "node_modules/fixture/cli.mjs"
            entry.parent.mkdir(parents=True)
            entry.write_text("console.log(JSON.stringify(process.argv.slice(2)));\n", encoding="utf-8")
            shim = root / "fixture.cmd"
            shim.write_text('@echo off\r\n"%dp0%\\node.exe" "%dp0%\\node_modules\\fixture\\cli.mjs" %*\r\n', encoding="utf-8")
            def which(name):
                return str(shim) if name == "fixture" else node if name == "node" else None
            with patch("archive.tools.lib.cli_command.shutil.which", side_effect=which):
                prefix = command_prefix("fixture")
            arguments = ['{"rows":[["中文 空格 & echo bad | test","a\\\\b","a\\\"b"]]}',
                         'User message with "quotes" & | < > ^ %PATH% !value!']
            self.assertEqual(prefix, [node, str(entry.resolve())])
            result = subprocess.run([*prefix, *arguments], capture_output=True, text=True, encoding="utf-8", check=True)
            self.assertEqual(json.loads(result.stdout), arguments)

    def test_local_npm_shim_finds_parent_package(self):
        with tempfile.TemporaryDirectory(prefix="npm-local-") as directory:
            root = Path(directory)
            shim = root / ".bin/fixture.cmd"
            shim.parent.mkdir()
            entry = root / "fixture/bin/cli.js"
            entry.parent.mkdir(parents=True)
            entry.write_text("", encoding="utf-8")
            shim.write_text('"%dp0%\\..\\fixture\\bin\\cli.js" %*', encoding="utf-8")
            with patch("archive.tools.lib.cli_command.shutil.which", side_effect=lambda name: "node.exe" if name == "node" else None):
                self.assertEqual(command_prefix(str(shim)), ["node.exe", str(entry.resolve())])

    def test_unknown_batch_wrapper_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="unknown-cli-") as directory:
            shim = Path(directory) / "unknown.cmd"
            shim.write_text("@echo off\necho %*\n", encoding="utf-8")
            with patch("archive.tools.lib.cli_command.shutil.which", return_value=None):
                with self.assertRaisesRegex(RuntimeError, "Cannot safely resolve"):
                    command_prefix(str(shim))


if __name__ == "__main__":
    unittest.main()
