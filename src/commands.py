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
    """Заглушка cd: выводит имя команды и аргументы."""
    return (f"cd: команда вызвана"
            f" с аргументами {", ".join(args)}")


def cmd_list(args: list[str]) -> str:
    """Заглушка ls: выводит имя команды и аргументы."""
    return (f"ls: команда вызвана"
            f" с аргументами {", ".join(args)}")


def cmd_exit(args: list[str]) -> str:
    """Заглушка: закрытие окна выполняет gui."""
    return ""


COMMANDS = {"echo": pr_text, "clear": clear, "help": cmd_help,
            "cd": chng_dir, "ls": cmd_list, "exit": cmd_exit}
