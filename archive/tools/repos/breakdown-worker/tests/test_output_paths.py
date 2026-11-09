"""Reject Windows rooted/model-controlled paths on every platform."""
import ast
from pathlib import Path, PureWindowsPath
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "run.py"
tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in {"relative_output_path", "game_directory_name"}]
namespace = {"Path": Path, "PureWindowsPath": PureWindowsPath}
exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), "exec"), namespace)
relative_output_path = namespace["relative_output_path"]
game_directory_name = namespace["game_directory_name"]


class OutputPathsTest(unittest.TestCase):
    def test_chinese_nested_paths_and_windows_separators(self):
        self.assertEqual(relative_output_path("02_模块/战斗机制.md"), Path("02_模块") / "战斗机制.md")
        self.assertEqual(relative_output_path(r"02_模块\战斗机制.md"), Path("02_模块") / "战斗机制.md")

    def test_reject_rooted_traversal_and_windows_device_paths(self):
        for raw in ("", "/outside.md", r"C:\outside.md", r"C:outside.md", r"\outside.md", r"\\server\share\file.md", "../outside.md", r"..\outside.md", "a/../outside.md", "a//b.md", "NUL.md", "a/COM1.txt", "a/坏:名.md", "a/尾部 .", "a/尾部 ", "a\x00b.md"):
            with self.subTest(path=raw), self.assertRaises(ValueError):
                relative_output_path(raw)

    def test_game_is_one_component(self):
        self.assertEqual(game_directory_name("向僵尸开炮"), "向僵尸开炮")
        for raw in ("a/b", r"a\b", "..", r"C:\outside"):
            with self.subTest(path=raw), self.assertRaises(ValueError):
                game_directory_name(raw)

    def test_device_name_whitespace_before_extension(self):
        for raw in ("CON .txt", "a/NUL .md", "COM1 .log"):
            with self.subTest(path=raw), self.assertRaises(ValueError):
                relative_output_path(raw)


if __name__ == "__main__":
    unittest.main()
