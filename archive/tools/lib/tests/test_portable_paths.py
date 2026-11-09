from pathlib import Path
import unittest

from archive.tools.lib.portable_paths import filename_stem, relative_output_path


class PortablePathTests(unittest.TestCase):
    def test_generated_titles_remove_invalid_windows_characters(self):
        self.assertEqual(filename_stem('Re:从零/开始*?"<>|\\\x01'), 'Re_从零_开始________')
        self.assertEqual(filename_stem("中文名称"), "中文名称")
        self.assertEqual(filename_stem("末尾. "), "末尾")
        self.assertEqual(filename_stem(".."), "untitled")
        self.assertEqual(filename_stem("abc", limit=2), "ab")

    def test_generated_names_avoid_devices_even_with_extensions(self):
        for name in ("CON", "nul", "COM1", "LPT9", "COM¹", "CONIN$", "NUL.txt", "CON .txt"):
            with self.subTest(name=name):
                self.assertTrue(filename_stem(name).startswith("_"))

    def test_relative_paths_preserve_safe_subdirectories(self):
        self.assertEqual(relative_output_path("专题\\机制.md"), Path("专题") / "机制.md")

    def test_relative_paths_reject_windows_escape_and_invalid_components(self):
        for name in ("C:\\outside.md", "C:outside.md", "\\\\server\\share\\x.md", "/outside.md",
                     "../x.md", "a/../x.md", "a/CON.md", "a/NUL.txt", "a/CON .txt", "a/file:stream",
                     "a/file?.md", "a/file.", "a/", "a//b.md"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    relative_output_path(name)


if __name__ == "__main__":
    unittest.main()
