import getpass


class CommandError(Exception):
    """Ошибка выполнения команды: неверные аргументы и т.п."""


def pr_text(args: list[str]) -> str:
    """Возвращает аргументы через пробел (echo)."""
    return " ".join(args)


def clear(args: list[str]) -> str:
    """Заглушка: очистку окна выполняет gui."""
    return ""


def cmd_help(args: list[str]) -> str:
    """Возвращает список доступных команд."""
    return ", ".join(COMMANDS.keys())


def chng_dir(args: list[str]) -> str:
    """Заглушка: переход по VFS выполняет gui."""
    return ""


def cmd_list(args: list[str]) -> str:
    """Заглушка: вывод содержимого VFS выполняет gui."""
    return ""


def parse_ls_args(args: list[str]) -> tuple[set[str], str]:
    """Разбирает аргументы ls на флаги и путь."""
    flags = set()
    paths = []
    for arg in args:
        if arg.startswith("-") and arg != "-":
            flags.update(arg[1:])
        else:
            paths.append(arg)
    unknown = sorted(flags - {"l", "a"})
    if unknown:
        raise CommandError(f"ls: неизвестный флаг -{unknown[0]}")
    if paths[1:]:
        raise CommandError("ls: слишком много аргументов")
    return flags, paths[0] if paths else "."


def cmd_whoami(args: list[str]) -> str:
    """Возвращает имя текущего пользователя ОС."""
    if args:
        raise CommandError("whoami: лишние аргументы")
    return getpass.getuser()


def cmd_exit(args: list[str]) -> str:
    """Заглушка: закрытие окна выполняет gui."""
    return ""


def cmd_vfs_save(args: list[str]) -> str:
    """Заглушка: сохранение VFS выполняет gui."""
    return ""


def cmd_touch(args: list[str]) -> str:
    """Заглушка: создание файла в VFS выполняет gui."""
    return ""


def cmd_mv(args: list[str]) -> str:
    """Заглушка: перемещение в VFS выполняет gui."""
    return ""


COMMANDS = {"echo": pr_text, "clear": clear, "help": cmd_help,
            "cd": chng_dir, "ls": cmd_list, "exit": cmd_exit,
            "vfs-save": cmd_vfs_save, "whoami": cmd_whoami,
            "touch": cmd_touch, "mv": cmd_mv}
