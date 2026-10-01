def load_script(path: str) -> list[tuple[int, str]]:
    """Возвращает пары (номер строки, команда) без комментариев."""
    commands = []
    with open(path, encoding="utf-8") as file:
        for number, line in enumerate(file, start=1):
            line = line.strip()
            if line and not line.startswith("#"):
                commands.append((number, line))
    return commands
