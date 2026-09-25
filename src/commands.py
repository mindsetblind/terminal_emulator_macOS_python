



def pr_text(args: list[str]) -> str:
    return " ".join(args)



def clear(args: list[str]) -> str:
    return ""


def help(args: list[str]) -> str:
    return ", ".join(COMMANDS.keys())


def chng_dir(args: list[str]) -> str:
    return (f"cd: команда вызвана"
            f" с аргументами {", ".join(args)}")


def cmd_list(args: list[str]) -> str:
    return (f"ls: команда вызвана"
            f" с аргументами {", ".join(args)}")


def cmd_exit(args: list[str]) -> str:
    return ""




#словарь с командами
COMMANDS = {"echo": pr_text, "clear": clear, "help":help,
            "cd":chng_dir, "ls": cmd_list, "exit":cmd_exit}





