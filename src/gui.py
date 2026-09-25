import getpass
import socket
import tkinter as tk
from parser import pars_command
from commands import COMMANDS


class TerminalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        username = getpass.getuser()
        hostname = socket.gethostname()


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



        self.button = tk.Button(self, text="Выполнить",
                                command=self.on_enter)
        self.button.grid(row=1, column=1, padx=20, pady=20)




    def _write_output(self, text):
        self.output.config(state="normal")
        self.output.insert(tk.END, f"{text}\n")
        self.output.config(state="disabled")

    def _select_all(self, event=None):
        self.command_entry.select_range(0, tk.END)
        return "break"


    def on_enter(self, event=None):
        raw_text = self.command_entry.get()
        try:
            parsed_command = pars_command(raw_text)
        except ValueError:
            self._write_output("Ошибка: незакрытые кавычки")
            return None

        if parsed_command is None:
            return None
        self._write_output(f"> {raw_text}")
        command = parsed_command.command
        args = parsed_command.args

        if command in COMMANDS:
            if command == "clear":
                self.output.config(state="normal")
                self.output.delete("1.0", tk.END)
                self.output.config(state="disabled")
            elif command == "help":
                self._write_output(f"Список доступных "
                                   f"команд: {COMMANDS[command](args)}")
            elif command == "exit":
                self._write_output("Завершение сессии...")
                self.update_idletasks()
                self.after(1000, self.destroy)
            else:
                self._write_output(COMMANDS[command](args))


        else:
            self._write_output("Ошибка: команда не найдена")

        self.command_entry.delete(0, tk.END)




