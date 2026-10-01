import shlex
from dataclasses import dataclass

@dataclass
class ParsedCommand:
    """Команда и её аргументы."""
    command: str
    args: list[str]

def pars_command(line:str) -> ParsedCommand | None:
    """Разбирает строку на команду и аргументы, # начинает комментарий."""
    tokens = shlex.split(line, comments=True)

    if not tokens:
        return None
    return ParsedCommand(command=tokens[0], args=tokens[1:])

