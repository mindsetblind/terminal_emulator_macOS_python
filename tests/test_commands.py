import unittest
from src.commands import (
    pr_text,
    clear,
    help,
    chng_dir,
    cmd_list,
)


class TestCommands(unittest.TestCase):

    def test_pr_text_joins_args(self):
        result = pr_text(["hello", "world"])
        self.assertEqual(result, "hello world")

    def test_pr_text_empty_args(self):
        result = pr_text([])
        self.assertEqual(result, "")

    def test_clear_returns_empty_string(self):
        result = clear(["anything"])
        self.assertEqual(result, "")

    def test_help_lists_all_commands(self):
        result = help([])
        # help должен вернуть строку, содержащую все ключи COMMANDS
        self.assertIn("ls", result)
        self.assertIn("cd", result)
        self.assertIn("exit", result)

    def test_chng_dir_includes_command_name_and_args(self):
        result = chng_dir(["folder"])
        self.assertIn("cd", result)
        self.assertIn("folder", result)

    def test_cmd_list_includes_command_name_and_args(self):
        result = cmd_list(["-la"])
        self.assertIn("ls", result)
        self.assertIn("-la", result)


if __name__ == "__main__":
    unittest.main()