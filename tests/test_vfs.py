import os
import tempfile
import unittest
from src.vfs import (VFSDir, VFSError, VFSFile, count_nodes, default_vfs,
                     format_path, get_node, list_dir, load_vfs, move,
                     resolve_path, save_vfs, touch, tree_lines)


class TestVFS(unittest.TestCase):

    def _write_xml(self, text):
        """Создаёт временный XML-файл и возвращает путь к нему."""
        file = tempfile.NamedTemporaryFile("w", suffix=".xml",
                                           encoding="utf-8", delete=False)
        file.write(text)
        file.close()
        self.addCleanup(os.remove, file.name)
        return file.name

    def test_load_file_content_from_base64(self):
        path = self._write_xml('<vfs><file name="a.txt">SGk=</file></vfs>')
        root = load_vfs(path)
        self.assertEqual(root.children["a.txt"].content, b"Hi")

    def test_load_nested_dirs(self):
        path = self._write_xml('<vfs><dir name="a"><dir name="b">'
                               '<dir name="c"><file name="f">SGk=</file>'
                               '</dir></dir></dir></vfs>')
        root = load_vfs(path)
        c_dir = root.children["a"].children["b"].children["c"]
        self.assertIn("f", c_dir.children)
        self.assertEqual(count_nodes(root), (3, 1))

    def test_empty_file_and_dir(self):
        path = self._write_xml('<vfs><file name="e"/><dir name="d"/></vfs>')
        root = load_vfs(path)
        self.assertEqual(root.children["e"].content, b"")
        self.assertEqual(count_nodes(root), (1, 1))

    def test_missing_file(self):
        with self.assertRaises(VFSError):
            load_vfs("no_such_vfs.xml")

    def test_broken_xml(self):
        path = self._write_xml('<vfs><dir name="a"></vfs>')
        with self.assertRaises(VFSError):
            load_vfs(path)

    def test_wrong_root(self):
        path = self._write_xml('<files></files>')
        with self.assertRaises(VFSError):
            load_vfs(path)

    def test_unknown_element(self):
        path = self._write_xml('<vfs><link name="x"/></vfs>')
        with self.assertRaises(VFSError):
            load_vfs(path)

    def test_missing_name(self):
        path = self._write_xml('<vfs><file>SGk=</file></vfs>')
        with self.assertRaises(VFSError):
            load_vfs(path)

    def test_bad_base64(self):
        path = self._write_xml('<vfs><file name="a">не base64</file></vfs>')
        with self.assertRaises(VFSError):
            load_vfs(path)

    def test_duplicate_names(self):
        path = self._write_xml('<vfs><file name="a"/><dir name="a"/></vfs>')
        with self.assertRaises(VFSError):
            load_vfs(path)

    def test_default_vfs_not_empty(self):
        self.assertNotEqual(count_nodes(default_vfs()), (0, 0))

    def test_save_and_load_back(self):
        root = VFSDir("/")
        folder = VFSDir("dir")
        folder.add(VFSFile("bin", bytes(range(256))))
        root.add(folder)
        path = self._write_xml("")
        save_vfs(root, path)
        loaded = load_vfs(path)
        self.assertEqual(loaded, root)

    def test_save_to_missing_dir(self):
        with self.assertRaises(VFSError):
            save_vfs(default_vfs(), "/no/such/dir/vfs.xml")

    def test_tree_lines(self):
        root = VFSDir("/")
        folder = VFSDir("dir")
        folder.add(VFSFile("inner.txt"))
        root.add(folder)
        root.add(VFSFile("last.txt"))
        self.assertEqual(tree_lines(root), ["├── dir/",
                                            "│   └── inner.txt",
                                            "└── last.txt"])

    def test_tree_lines_empty_dir(self):
        self.assertEqual(tree_lines(VFSDir("/")), [])



class TestVFSPaths(unittest.TestCase):

    def setUp(self):
        self.root = VFSDir("/")
        home = VFSDir("home")
        home.add(VFSFile("b.txt", b"12345"))
        home.add(VFSDir("a"))
        self.root.add(home)

    def test_resolve_relative(self):
        self.assertEqual(resolve_path(["home"], "a"), ["home", "a"])

    def test_resolve_absolute(self):
        self.assertEqual(resolve_path(["home"], "/x/y"), ["x", "y"])

    def test_resolve_dots(self):
        self.assertEqual(resolve_path(["home", "a"], "../.././home"),
                         ["home"])

    def test_resolve_parent_of_root(self):
        self.assertEqual(resolve_path([], ".."), [])

    def test_format_path(self):
        self.assertEqual(format_path([]), "/")
        self.assertEqual(format_path(["home", "a"]), "/home/a")

    def test_get_node(self):
        node = get_node(self.root, ["home", "b.txt"])
        self.assertEqual(node.content, b"12345")

    def test_get_node_missing(self):
        with self.assertRaises(VFSError):
            get_node(self.root, ["nope"])

    def test_get_node_through_file(self):
        with self.assertRaises(VFSError):
            get_node(self.root, ["home", "b.txt", "x"])

    def test_list_dir_sorted(self):
        home = get_node(self.root, ["home"])
        self.assertEqual(list_dir(home), ["a/", "b.txt"])

    def test_list_dir_long_and_all(self):
        home = get_node(self.root, ["home"])
        lines = list_dir(home, long_format=True, show_all=True)
        self.assertEqual(lines[0].split(), ["d", "-", "./"])
        self.assertEqual(lines[-1].split(), ["-", "5", "b.txt"])

    def test_list_dir_file(self):
        node = get_node(self.root, ["home", "b.txt"])
        self.assertEqual(list_dir(node), ["b.txt"])



class TestVFSChanges(unittest.TestCase):

    def setUp(self):
        self.root = VFSDir("/")
        home = VFSDir("home")
        home.add(VFSFile("a.txt", b"A"))
        home.add(VFSFile("b.txt", b"B"))
        home.add(VFSDir("sub"))
        self.root.add(home)
        self.root.add(VFSDir("tmp"))

    def _names(self, *parts):
        """Возвращает имена внутри папки."""
        return sorted(get_node(self.root, list(parts)).children)

    def test_touch_creates_empty_file(self):
        touch(self.root, ["tmp", "new.txt"])
        self.assertEqual(get_node(self.root, ["tmp", "new.txt"]).content, b"")

    def test_touch_existing_file_keeps_content(self):
        touch(self.root, ["home", "a.txt"])
        self.assertEqual(get_node(self.root, ["home", "a.txt"]).content, b"A")

    def test_touch_missing_dir(self):
        with self.assertRaises(VFSError):
            touch(self.root, ["nope", "x.txt"])

    def test_touch_inside_file(self):
        with self.assertRaises(VFSError):
            touch(self.root, ["home", "a.txt", "x"])

    def test_touch_root(self):
        with self.assertRaises(VFSError):
            touch(self.root, [])

    def test_mv_rename(self):
        new_path = move(self.root, ["home", "a.txt"], ["home", "c.txt"])
        self.assertEqual(new_path, ["home", "c.txt"])
        self.assertEqual(self._names("home"), ["b.txt", "c.txt", "sub"])
        self.assertEqual(get_node(self.root, new_path).name, "c.txt")

    def test_mv_into_dir(self):
        move(self.root, ["home", "a.txt"], ["tmp"])
        self.assertEqual(self._names("tmp"), ["a.txt"])
        self.assertNotIn("a.txt", self._names("home"))

    def test_mv_dir_with_content(self):
        move(self.root, ["home"], ["tmp", "house"])
        self.assertEqual(self._names("tmp", "house"),
                         ["a.txt", "b.txt", "sub"])

    def test_mv_overwrites_file(self):
        move(self.root, ["home", "a.txt"], ["home", "b.txt"])
        self.assertEqual(get_node(self.root, ["home", "b.txt"]).content, b"A")
        self.assertEqual(self._names("home"), ["b.txt", "sub"])

    def test_mv_missing_source(self):
        with self.assertRaises(VFSError):
            move(self.root, ["nope"], ["tmp"])

    def test_mv_missing_target_dir(self):
        with self.assertRaises(VFSError):
            move(self.root, ["home", "a.txt"], ["nope", "x.txt"])

    def test_mv_dir_into_itself(self):
        with self.assertRaises(VFSError):
            move(self.root, ["home"], ["home", "sub"])

    def test_mv_same_path(self):
        with self.assertRaises(VFSError):
            move(self.root, ["home", "a.txt"], ["home", "a.txt"])

    def test_mv_root(self):
        with self.assertRaises(VFSError):
            move(self.root, [], ["tmp"])

    def test_mv_dir_over_file(self):
        with self.assertRaises(VFSError):
            move(self.root, ["home", "sub"], ["home", "a.txt"])

    def test_mv_file_over_dir_with_same_name(self):
        touch(self.root, ["tmp", "sub"])
        with self.assertRaises(VFSError):
            move(self.root, ["tmp", "sub"], ["home"])


if __name__ == "__main__":
    unittest.main()
