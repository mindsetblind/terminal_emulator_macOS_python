import unittest
from src.cli import parse_args


class TestCli(unittest.TestCase):

    def test_no_args(self):
        args = parse_args([])
        self.assertIsNone(args.vfs)
        self.assertIsNone(args.script)

    def test_only_vfs(self):
        args = parse_args(["--vfs", "vfs.xml"])
        self.assertEqual(args.vfs, "vfs.xml")
        self.assertIsNone(args.script)

    def test_both_args_any_order(self):
        args = parse_args(["--script", "start.txt", "--vfs", "vfs.xml"])
        self.assertEqual(args.vfs, "vfs.xml")
        self.assertEqual(args.script, "start.txt")

    def test_unknown_arg_exits(self):
        with self.assertRaises(SystemExit):
            parse_args(["--abc"])


if __name__ == "__main__":
    unittest.main()
