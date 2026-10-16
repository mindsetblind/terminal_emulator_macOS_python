import os
import tempfile
import unittest
from src.vfs import (VFSDir, VFSError, VFSFile, count_nodes, default_vfs,
                     load_vfs, save_vfs, tree_lines)


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


if __name__ == "__main__":
    unittest.main()
