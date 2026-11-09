"""Cross-platform regressions for paths, hook guards and relocation."""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.agents/hooks'))
import hook_utils as hooks


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guard = load_module('path_guard', ROOT / 'tools/workspace-guard/check_paths.py')
bootstrap = load_module('bootstrap', ROOT / 'tools/windows/bootstrap.py')


class WindowsCompatibilityTests(unittest.TestCase):
    def test_windows_drive_paths_keep_backslashes(self):
        self.assertEqual(hooks.shell_tokens(r'copy "C:\工程 folder\a.txt" "D:\外部 folder\b.txt"'),
                         ['copy', r'C:\工程 folder\a.txt', r'D:\外部 folder\b.txt'])

    def test_windows_shell_destination_paths(self):
        self.assertIn(r'D:\outside folder\b.txt', hooks.extract_shell_write_paths(
            r'cmd /s /c copy "C:\工程 folder\a.txt" "D:\outside folder\b.txt"'))
        self.assertIn(r'D:\outside folder\b.txt', hooks.extract_shell_write_paths(
            '''powershell -Command "Set-Content -LiteralPath 'D:\\outside folder\\b.txt' -Value 'hello'"'''))

    def test_quoted_redirect_is_not_truncated(self):
        path = r'C:\repo\sub folder\..\..\outside.txt'
        self.assertIn(path, hooks.extract_shell_write_paths(f'echo data > "{path}"'))

    def test_guard_normalizes_parent_traversal(self):
        self.assertTrue(guard.is_allowed(ROOT / 'workspace/中文 folder/file.txt'))
        self.assertFalse(guard.is_allowed(ROOT / '../external-project/file.txt'))
        self.assertFalse(guard.is_allowed(ROOT.parent / (ROOT.name + '-other') / 'x'))

    def test_guard_and_hooks_agree_on_temp(self):
        for root in guard.allowed_roots():
            self.assertTrue(hooks.is_allowed_write(root / 'windows-compat-test'))

    def test_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            # Use the temporary folder as a simulated checkout so the link target
            # can still be outside the allowed roots used for this assertion.
            link = Path(folder) / 'escape'
            try:
                link.symlink_to(ROOT.parent, target_is_directory=True)
            except OSError:
                self.skipTest('Symlink creation unavailable (normal on Windows without developer mode)')
            self.assertFalse(guard.is_allowed(link / 'external-project/file.txt'))

    def run_hook(self, target: str, payload: dict):
        return subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / '.agents/hooks/run-hook.py'),
                               '--runtime', 'compat-test', target], input=json.dumps(payload),
                              capture_output=True, text=True, encoding='utf-8', cwd=ROOT)

    def test_commit_guard_applies_to_windows_tool(self):
        result = self.run_hook('check-commit-message.py', {'cwd': str(ROOT), 'tool_name': 'exec_command',
                              'tool_input': {'cmd': 'git commit -m "English only"'}})
        self.assertEqual(result.returncode, 2, result.stderr)
        good = self.run_hook('check-commit-message.py', {'cwd': str(ROOT), 'tool_name': 'PowerShell',
                             'tool_input': {'command': 'git commit -m "修复 Windows 兼容"'}})
        self.assertEqual(good.returncode, 0, good.stderr)

    def test_dangerous_powershell_command_is_denied(self):
        result = self.run_hook('warn-dangerous.py', {'cwd': str(ROOT), 'tool_name': 'PowerShell',
                              'tool_input': {'command': 'Remove-Item data -Recurse -Force'}})
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_unrelated_checkout_is_not_hooked(self):
        result = self.run_hook('check-commit-message.py', {'cwd': str(ROOT.parent / 'another-project'),
                              'tool_name': 'Bash', 'tool_input': {'command': 'git commit -m "English"'}})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_runtime_config_contains_only_portable_hook_entries(self):
        for runtime in ('codex', 'claude', 'agent'):
            config = bootstrap.render_hooks(runtime)
            commands = [hook['command'] for events in config['hooks'].values()
                        for event in events for hook in event['hooks']]
            self.assertEqual(len(commands), 16)
            self.assertTrue(all('run-hook.py' in cmd and '--runtime' in cmd for cmd in commands))
            self.assertTrue(all(' bash ' not in cmd for cmd in commands))
        self.assertNotIn('/Users/mt/', (ROOT / '.agents/hooks.json').read_text(encoding='utf-8'))

    def test_windows_command_strings_quote_shell_metacharacters(self):
        command = bootstrap.quote_command(['C:\\用户 A&B\\python.exe', 'C:\\工程 & demo\\run.py'], windows=True)
        self.assertEqual(command, '"C:\\用户 A&B\\python.exe" "C:\\工程 & demo\\run.py"')
        with self.assertRaises(ValueError):
            bootstrap.quote_command(['C:\\%PATH%\\python.exe'], windows=True)

    def test_relocation_with_chinese_spaces(self):
        with tempfile.TemporaryDirectory(prefix='兼容 test ') as folder:
            root = Path(folder)
            for relative in ('tools/workspace-guard/check_paths.py', '.agents/hooks/hook_utils.py'):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)
            relocated_guard = load_module('relocated_guard', root / 'tools/workspace-guard/check_paths.py')
            self.assertEqual(relocated_guard.WORKSPACE, root.resolve())
            self.assertTrue(relocated_guard.is_allowed(root / '中文 folder/file.txt'))
            self.assertFalse(relocated_guard.is_allowed(ROOT.parent / 'external/file.txt'))

    def test_existing_checkout_paths_are_windows_legal(self):
        files = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-z']).decode('utf-8').split('\0')
        seen = {}
        reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}
        for relative in filter(None, files):
            path = ROOT / relative
            if not path.exists():  # pre-existing user deletions and migrated source names
                continue
            self.assertFalse(path.is_symlink(), relative)
            for component in Path(relative).parts:
                self.assertFalse(re.search(r'[<>:"\\|?*]|[ .]$', component), relative)
                self.assertNotIn(component.split('.')[0].upper(), reserved, relative)
            self.assertNotIn(relative.casefold(), seen, relative)
            seen[relative.casefold()] = relative


if __name__ == '__main__':
    unittest.main()
