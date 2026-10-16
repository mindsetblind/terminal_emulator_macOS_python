import getpass
import unittest
from src.commands import (
    CommandError,
    pr_text,
    clear,
    cmd_help,
    cmd_whoami,
    parse_ls_args,
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
        result = cmd_help([])
        self.assertIn("ls", result)
        self.assertIn("cd", result)
        self.assertIn("exit", result)

    def test_help_lists_new_commands(self):
        result = cmd_help([])
        self.assertIn("whoami", result)
        self.assertIn("vfs-save", result)

    def test_whoami_returns_os_user(self):
        self.assertEqual(cmd_whoami([]), getpass.getuser())

    def test_whoami_with_args_raises(self):
        with self.assertRaises(CommandError):
            cmd_whoami(["root"])

    def test_ls_args_default_path(self):
        self.assertEqual(parse_ls_args([]), (set(), "."))

    def test_ls_args_flags_and_path(self):
        flags, path = parse_ls_args(["-la", "home"])
        self.assertEqual(flags, {"l", "a"})
        self.assertEqual(path, "home")

    def test_ls_args_unknown_flag(self):
        with self.assertRaises(CommandError):
            parse_ls_args(["-x"])

    def test_ls_args_too_many_paths(self):
        with self.assertRaises(CommandError):
            parse_ls_args(["a", "b"])

if __name__ == "__main__":
    unittest.main()