import base64
import xml.etree.ElementTree as et
from dataclasses import dataclass, field


class VFSError(Exception):
    """Ошибка загрузки или сохранения VFS."""


@dataclass
class VFSFile:
    """Файл VFS: имя и содержимое в байтах."""
    name: str
    content: bytes = b""


@dataclass
class VFSDir:
    """Папка VFS: имя и вложенные файлы и папки."""
    name: str
    children: dict = field(default_factory=dict)

    def add(self, node):
        """Добавляет вложенный файл или папку."""
        if node.name in self.children:
            raise VFSError(f"повторяющееся имя '{node.name}'")
        self.children[node.name] = node


def default_vfs() -> VFSDir:
    """Создаёт VFS по умолчанию в памяти."""
    root = VFSDir("/")
    home = VFSDir("home")
    user = VFSDir("user")
    user.add(VFSFile("readme.txt", "VFS по умолчанию\n".encode("utf-8")))
    home.add(user)
    root.add(home)
    return root


def load_vfs(path: str) -> VFSDir:
    """Загружает VFS из XML-файла."""
    try:
        tree = et.parse(path)
    except FileNotFoundError:
        raise VFSError(f"файл не найден: {path}") from None
    except et.ParseError:
        raise VFSError(f"неверный формат XML: {path}") from None
    except OSError:
        raise VFSError(f"не удалось прочитать файл: {path}") from None

    xml_root = tree.getroot()
    if xml_root.tag != "vfs":
        raise VFSError("корневой элемент должен называться <vfs>")
    root = VFSDir("/")
    _fill_dir(root, xml_root)
    return root


def _fill_dir(directory: VFSDir, element: et.Element):
    """Заполняет папку элементами XML."""
    for child in element:
        name = child.get("name")
        if not name:
            raise VFSError(f"у элемента <{child.tag}> нет атрибута name")
        if child.tag == "dir":
            subdir = VFSDir(name)
            _fill_dir(subdir, child)
            directory.add(subdir)
        elif child.tag == "file":
            directory.add(VFSFile(name, _decode(child.text, name)))
        else:
            raise VFSError(f"неизвестный элемент <{child.tag}>")


def _decode(text: str | None, name: str) -> bytes:
    """Декодирует содержимое файла из base64."""
    try:
        return base64.b64decode((text or "").strip(), validate=True)
    except ValueError:
        raise VFSError(f"содержимое файла '{name}' не в base64") from None


def save_vfs(root: VFSDir, path: str):
    """Сохраняет VFS в XML-файл в исходном формате."""
    xml_root = et.Element("vfs")
    _dump_dir(root, xml_root)
    tree = et.ElementTree(xml_root)
    et.indent(tree)
    try:
        tree.write(path, encoding="utf-8", xml_declaration=True)
    except OSError:
        raise VFSError(f"не удалось записать файл: {path}") from None


def _dump_dir(directory: VFSDir, element: et.Element):
    """Записывает содержимое папки в элемент XML."""
    for node in directory.children.values():
        if isinstance(node, VFSDir):
            child = et.SubElement(element, "dir", name=node.name)
            _dump_dir(node, child)
        else:
            child = et.SubElement(element, "file", name=node.name)
            child.text = base64.b64encode(node.content).decode("ascii")


def count_nodes(directory: VFSDir) -> tuple[int, int]:
    """Возвращает количество папок и файлов внутри папки."""
    dirs, files = 0, 0
    for node in directory.children.values():
        if isinstance(node, VFSDir):
            sub_dirs, sub_files = count_nodes(node)
            dirs += sub_dirs + 1
            files += sub_files
        else:
            files += 1
    return dirs, files


def tree_lines(directory: VFSDir, prefix: str = "") -> list[str]:
    """Возвращает содержимое папки в виде строк дерева."""
    lines = []
    nodes = list(directory.children.values())
    for node in nodes:
        is_last = node is nodes[-1]
        branch = "└── " if is_last else "├── "
        if isinstance(node, VFSDir):
            lines.append(f"{prefix}{branch}{node.name}/")
            indent = "    " if is_last else "│   "
            lines.extend(tree_lines(node, prefix + indent))
        else:
            lines.append(f"{prefix}{branch}{node.name}")
    return lines
