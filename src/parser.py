import shlex
from dataclasses import dataclass

@dataclass
class ParsedCommand:
    command: str
    args: list[str]

def pars_command(line:str) -> ParsedCommand | None:
    tokens = shlex.split(line)

    if not tokens:
        return None
    return ParsedCommand(command=tokens[0], args=tokens[1:])

