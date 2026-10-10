import getpass
import socket
import tkinter as tk
from parser import pars_command
from commands import COMMANDS
from script import load_script
from vfs import VFSError, count_nodes, default_vfs, load_vfs, save_vfs


class TerminalApp(tk.Tk):
    """Окно эмулятора терминала."""

    def __init__(self, vfs_path=None, script_path=None):
        """Создаёт окно и запоминает параметры запуска."""
        super().__init__()
        username = getpass.getuser()
        hostname = socket.gethostname()

        self.vfs_path = vfs_path
        self.script_path = script_path

        self.title(f"Эмулятор - [{username}@{hostname}]")
        self.geometry("1000x700")
        self.configure(bg="#000000")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.command_entry = tk.Entry(self, font=("Menlo", 12))
        self.command_entry.grid(row=1, column=0, sticky="ew",
                                padx=20, pady=20)
        self.command_entry.bind("<Return>", self.on_enter)
        self.command_entry.bind("<Command-a>", self._select_all)

        self.output = tk.Text(self, font=("Menlo", 12))
        self.output.grid(row=0, column=0,columnspan=2, sticky="nsew",
                         padx = 20, pady= 20)
        self.output.config(state="disabled")

        self._write_output(f"[debug] VFS: {self.vfs_path}")
        self._write_output(f"[debug] Стартовый скрипт: {self.script_path}")
        self._load_vfs()

        self.button = tk.Button(self, text="Выполнить",
                                command=self.on_enter)
        self.button.grid(row=1, column=1, padx=20, pady=20)

        self.after(100, self.run_script)

    def _write_output(self, text):
        """Добавляет строку в поле вывода."""
        self.output.config(state="normal")
        self.output.insert(tk.END, f"{text}\n")
        self.output.config(state="disabled")

    def _select_all(self, event=None):
        """Выделяет весь текст в поле ввода."""
        self.command_entry.select_range(0, tk.END)
        return "break"

    def _load_vfs(self):
        """Загружает VFS из файла или создаёт VFS по умолчанию."""
        self.vfs = default_vfs()
        source = "по умолчанию"
        if self.vfs_path is not None:
            try:
                self.vfs = load_vfs(self.vfs_path)
                source = self.vfs_path
            except VFSError as error:
                self._write_output(f"Ошибка загрузки VFS: {error}")
        dirs, files = count_nodes(self.vfs)
        self._write_output(f"[debug] Загружена VFS {source} "
                           f"(папок: {dirs}, файлов: {files})")

    def on_enter(self, event=None):
        """Выполняет команду из поля ввода."""
        self.execute_command(self.command_entry.get())
        self.command_entry.delete(0, tk.END)

    def execute_command(self, raw_text: str) -> bool:
        """Выполняет одну команду, возвращает False при ошибке."""
        try:
            parsed_command = pars_command(raw_text)
        except ValueError:
            self._write_output(f"> {raw_text}")
            self._write_output("Ошибка: незакрытые кавычки")
            return False

        if parsed_command is None:
            return True
        self._write_output(f"> {raw_text}")
        command = parsed_command.command
        args = parsed_command.args

        if command not in COMMANDS:
            self._write_output("Ошибка: команда не найдена")
            return False

        gui_commands = {"clear": self._cmd_clear, "help": self._cmd_help,
                        "exit": self._cmd_exit,
                        "vfs-save": self._cmd_vfs_save}
        if command in gui_commands:
            return gui_commands[command](args)
        self._write_output(COMMANDS[command](args))
        return True

    def _cmd_clear(self, args: list[str]) -> bool:
        """Очищает поле вывода."""
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.config(state="disabled")
        return True

    def _cmd_help(self, args: list[str]) -> bool:
        """Выводит список доступных команд."""
        self._write_output(f"Список доступных "
                           f"команд: {COMMANDS['help'](args)}")
        return True

    def _cmd_exit(self, args: list[str]) -> bool:
        """Закрывает окно через секунду."""
        self._write_output("Завершение сессии...")
        self.update_idletasks()
        self.after(1000, self.destroy)
        return True

    def _cmd_vfs_save(self, args: list[str]) -> bool:
        """Сохраняет VFS на диск в формате XML."""
        if not args:
            self._write_output("Ошибка: vfs-save: не указан путь")
            return False
        try:
            save_vfs(self.vfs, args[0])
        except VFSError as error:
            self._write_output(f"Ошибка: vfs-save: {error}")
            return False
        self._write_output(f"VFS сохранена в {args[0]}")
        return True

    def run_script(self):
        """Выполняет команды стартового скрипта до первой ошибки."""
        if self.script_path is None:
            return
        try:
            lines = load_script(self.script_path)
        except OSError:
            self._write_output(f"Ошибка: не удалось открыть стартовый "
                               f"скрипт {self.script_path}")
            return

        for number, line in lines:
            ok = self.execute_command(line)
            if not ok:
                self._write_output(f"Скрипт остановлен: ошибка "
                                   f"в строке {number}")
                return
            if line.split()[0] == "exit":
                return
