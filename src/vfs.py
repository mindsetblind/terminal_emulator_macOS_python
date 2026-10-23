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


def resolve_path(cwd: list[str], target: str) -> list[str]:
    """Переводит путь относительно текущей папки в список имён от корня."""
    parts = [] if target.startswith("/") else list(cwd)
    for name in target.split("/"):
        if name in ("", "."):
            continue
        if name == "..":
            if parts:
                parts.pop()
        else:
            parts.append(name)
    return parts


def format_path(parts: list[str]) -> str:
    """Переводит список имён в строку пути."""
    return "/" + "/".join(parts)


def get_node(root: VFSDir, parts: list[str]):
    """Находит файл или папку по пути от корня."""
    node = root
    for name in parts:
        if not isinstance(node, VFSDir) or name not in node.children:
            raise VFSError("нет такого файла или каталога")
        node = node.children[name]
    return node


def list_dir(node, long_format: bool = False,
             show_all: bool = False) -> list[str]:
    """Возвращает строки вывода ls для файла или папки."""
    if isinstance(node, VFSFile):
        return [_ls_entry(node, long_format)]
    lines = []
    if show_all:
        lines += [_ls_entry(VFSDir("."), long_format),
                  _ls_entry(VFSDir(".."), long_format)]
    for name in sorted(node.children):
        lines.append(_ls_entry(node.children[name], long_format))
    return lines


def _ls_entry(node, long_format: bool) -> str:
    """Форматирует одну строку вывода ls."""
    if isinstance(node, VFSDir):
        name, kind, size = f"{node.name}/", "d", "-"
    else:
        name, kind, size = node.name, "-", str(len(node.content))
    if long_format:
        return f"{kind} {size:>8} {name}"
    return name


def _get_dir(root: VFSDir, parts: list[str]) -> VFSDir:
    """Находит папку по пути, иначе выдаёт ошибку."""
    node = get_node(root, parts)
    if not isinstance(node, VFSDir):
        raise VFSError("не каталог")
    return node


def touch(root: VFSDir, parts: list[str]):
    """Создаёт пустой файл, если его ещё нет."""
    if not parts:
        raise VFSError("нельзя создать файл с таким именем")
    parent = _get_dir(root, parts[:-1])
    if parts[-1] not in parent.children:
        parent.add(VFSFile(parts[-1]))


def move(root: VFSDir, src: list[str], dst: list[str]) -> list[str]:
    """Перемещает или переименовывает узел, возвращает его новый путь."""
    if not src:
        raise VFSError("нельзя переместить корень")
    node = get_node(root, src)
    target = _resolve_target(root, src, dst)
    if target == src:
        raise VFSError("источник и назначение совпадают")
    if target[:len(src)] == src:
        raise VFSError("нельзя переместить папку в саму себя")
    parent = _get_dir(root, target[:-1])
    _check_replace(parent.children.get(target[-1]), node)
    del _get_dir(root, src[:-1]).children[src[-1]]
    node.name = target[-1]
    parent.children[node.name] = node
    return target


def _resolve_target(root: VFSDir, src: list[str],
                    dst: list[str]) -> list[str]:
    """Определяет итоговый путь: в папку назначения или под новым именем."""
    try:
        is_dir = isinstance(get_node(root, dst), VFSDir)
    except VFSError:
        is_dir = False
    if is_dir:
        return dst + [src[-1]]
    if not dst:
        raise VFSError("неверный путь назначения")
    return dst


def _check_replace(existing, node):
    """Проверяет, можно ли заменить существующий узел перемещаемым."""
    if existing is None:
        return
    if isinstance(existing, VFSDir):
        raise VFSError(f"каталог '{existing.name}' уже существует")
    if isinstance(node, VFSDir):
        raise VFSError(f"нельзя заменить файл '{existing.name}' папкой")
