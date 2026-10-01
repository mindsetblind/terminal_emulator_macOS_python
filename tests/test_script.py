import os
import tempfile
import unittest
from src.script import load_script


class TestLoadScript(unittest.TestCase):

    def _write_script(self, text):
        """Создаёт временный файл скрипта и возвращает путь к нему."""
        file = tempfile.NamedTemporaryFile("w", suffix=".txt",
                                           encoding="utf-8", delete=False)
        file.write(text)
        file.close()
        self.addCleanup(os.remove, file.name)
        return file.name

    def test_skips_comments_and_empty_lines(self):
        path = self._write_script("# комментарий\n\nls\n   \ncd dir\n")
        self.assertEqual(load_script(path), [(3, "ls"), (5, "cd dir")])

    def test_strips_spaces(self):
        path = self._write_script("   echo hi   \n")
        self.assertEqual(load_script(path), [(1, "echo hi")])

    def test_empty_file(self):
        path = self._write_script("")
        self.assertEqual(load_script(path), [])

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_script("no_such_script.txt")


if __name__ == "__main__":
    unittest.main()
