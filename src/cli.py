import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Разбирает параметры командной строки эмулятора."""
    parser = argparse.ArgumentParser(description="Эмулятор командной строки")
    parser.add_argument("--vfs", help="путь к физическому расположению VFS")
    parser.add_argument("--script", help="путь к стартовому скрипту")
    return parser.parse_args(argv)
