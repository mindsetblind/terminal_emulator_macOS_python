from gui import TerminalApp
from cli import parse_args

if __name__ == "__main__":
    args = parse_args()
    app = TerminalApp(vfs_path = args.vfs, script_path = args.script)
    app.mainloop()
