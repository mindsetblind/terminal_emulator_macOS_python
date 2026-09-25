import unittest
from src.parser import pars_command, ParsedCommand


class TestParser(unittest.TestCase):

    def test_simple_command_no_args(self):
        result = pars_command("ls")
        self.assertEqual(result, ParsedCommand(command="ls", args=[]))

    def test_simple_command_with_args(self):
        result = pars_command("cd folder")
        self.assertEqual(result, ParsedCommand(command="cd", args=["folder"]))

    def test_multiple_args_without_quotes(self):
        result = pars_command("cd My Folder")
        self.assertEqual(result, ParsedCommand(command="cd", args=["My", "Folder"]))

    def test_quoted_argument_kept_as_one(self):
        result = pars_command('cd "My Folder"')
        self.assertEqual(result, ParsedCommand(command="cd", args=["My Folder"]))

    def test_empty_input_returns_none(self):
        result = pars_command("")
        self.assertIsNone(result)

    def test_whitespace_only_input_returns_none(self):
        result = pars_command("   ")
        self.assertIsNone(result)

    def test_unclosed_quote_raises_value_error(self):
        with self.assertRaises(ValueError):
            pars_command('cd "test')


if __name__ == "__main__":
    unittest.main()