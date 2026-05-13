"""MOOD client entry point."""

import cmd
import sys
import socket
import threading
import time
import cowsay
from mood.common import setup_cowsay
from mood.common.constants import HOST, PORT, WEAPONS

setup_cowsay()


def readline_get_line_buffer():
    """Get current readline input buffer."""
    try:
        import readline
        return readline.get_line_buffer()
    except Exception:
        return ""


def handle_server_message(line, client):
    """Handle and display a message from the server."""
    parts = line.split()
    if not parts:
        return

    if parts[0] == "moved":
        x, y = int(parts[1]), int(parts[2])
        client.player_x = x
        client.player_y = y
        print(f"\rMoved to ({x}, {y})")

    elif parts[0] == "encounter":
        name = parts[1]
        hello = parts[2]
        client.local_monsters[(client.player_x, client.player_y)] = name
        print(f"\r{cowsay.get_output_string(name, hello)}")

    elif parts[0] == "added":
        name, x, y = parts[1], int(parts[2]), int(parts[3])
        print(f"\rAdded monster {name} to ({x}, {y})")
        if len(parts) > 4 and parts[4] == "replaced":
            print("\rReplaced the old monster")
        client.local_monsters[(x, y)] = name

    elif parts[0] == "no_monster":
        print(f"\rNo {parts[1]} here")

    else:
        print(f"\r{line}")

    if client.interactive:
        print(
            f"{client.prompt}{readline_get_line_buffer()}",
            end="",
            flush=True,
        )


def receive_messages(sock, client):
    """Receive messages from server in a separate thread."""
    buf = ""
    try:
        while True:
            data = sock.recv(1024).decode()
            if not data:
                break
            buf += data
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                handle_server_message(line.strip(), client)
    except Exception:
        pass


class MudClient(cmd.Cmd):
    """MOOD interactive client."""

    prompt = ""

    def __init__(self, sock, username, interactive=True):
        """Initialize the client with a socket and username."""
        super().__init__()
        self.sock = sock
        self.username = username
        self.player_x = 0
        self.player_y = 0
        self.local_monsters = {}
        self.interactive = interactive

    def send(self, line):
        """Send a command to the server."""
        self.sock.sendall((line + "\n").encode())

    def do_up(self, arg):
        """Move up."""
        self.send("move 0 -1")

    def do_down(self, arg):
        """Move down."""
        self.send("move 0 1")

    def do_left(self, arg):
        """Move left."""
        self.send("move -1 0")

    def do_right(self, arg):
        """Move right."""
        self.send("move 1 0")

    def do_addmon(self, arg):
        """Add a monster: addmon <name> <x> <y> <hello>."""
        parts = arg.split()
        if len(parts) != 4:
            print("Invalid arguments")
            return
        name, x_s, y_s, hello = parts
        if name not in cowsay.CHARS:
            print("Cannot add unknown monster")
            return
        try:
            x, y = int(x_s), int(y_s)
        except ValueError:
            print("Invalid arguments")
            return
        self.send(f"addmon {name} {x} {y} {hello} 100")

    def complete_addmon(self, text, line, begidx, endidx):
        """Complete monster name for addmon."""
        parts = line.split()
        if len(parts) == 1 or (len(parts) == 2 and not line.endswith(" ")):
            return [c for c in cowsay.CHARS if c.startswith(text)]
        return []

    def do_attack(self, arg):
        """Attack a monster: attack <name> [with <weapon>]."""
        parts = arg.split()
        damage = WEAPONS["sword"]
        weapon = "sword"
        monster_name = None

        i = 0
        if i < len(parts) and parts[i] != "with":
            monster_name = parts[i]
            i += 1
        if i < len(parts) and parts[i] == "with":
            i += 1
            if i >= len(parts):
                print("Unknown weapon")
                return
            weapon = parts[i]
            if weapon not in WEAPONS:
                print("Unknown weapon")
                return
            damage = WEAPONS[weapon]

        if monster_name is None:
            print("No monster here")
            return

        self.send(f"attack {monster_name} {damage} {weapon}")

    def complete_attack(self, text, line, begidx, endidx):
        """Complete monster name or weapon for attack."""
        parts = line.split()
        if "with" in parts:
            return [w for w in WEAPONS if w.startswith(text)]
        if len(parts) >= 2 and line.endswith(" "):
            return ["with"] if "with".startswith(text) else []
        if len(parts) >= 3:
            return ["with"] if "with".startswith(text) else []
        pos = (self.player_x, self.player_y)
        if pos in self.local_monsters:
            name = self.local_monsters[pos]
            return [name] if name.startswith(text) else []
        return []

    def do_sayall(self, arg):
        """Send a message to all players: sayall <message>."""
        if not arg:
            print("Usage: sayall <message>")
            return
        if arg.startswith('"') and arg.endswith('"'):
            arg = arg[1:-1]
        self.send(f"sayall {arg}")

    def do_movemonsters(self, arg):
        """Enable or disable wandering monsters: movemonsters on/off."""
        if arg not in ("on", "off"):
            print("Usage: movemonsters on/off")
            return
        self.send(f"movemonsters {arg}")

    def do_locale(self, arg):
        """Set locale: locale <locale_name>."""
        if not arg:
            print("Usage: locale <locale_name>")
            return
        self.send(f"locale {arg}")

    def do_documentation(self, arg):
        """Open server documentation in browser."""
        import webbrowser
        from importlib.resources import files
        doc_path = files('mood').joinpath('docs/index.html')
        webbrowser.open(f"file://{doc_path}")

    def do_EOF(self, arg):
        """Exit the client."""
        return True

    def default(self, line):
        """Handle unknown commands."""
        print("Invalid command")


def run_from_file(client, filename):
    """Execute commands from a .mood script file.

    :param client: The MudClient instance.
    :param filename: Path to the .mood script file.
    """
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            print(f"> {line}")
            client.onecmd(line)
            time.sleep(1)


def main():
    """Start the MOOD client."""
    args = sys.argv[1:]

    # Разбираем аргументы: username [--file <filename>]
    if not args:
        print("Usage: python -m mood.client <username> [--file <filename>]")
        sys.exit(1)

    username = args[0]
    filename = None

    if "--file" in args:
        idx = args.index("--file")
        if idx + 1 >= len(args):
            print("Error: --file requires a filename")
            sys.exit(1)
        filename = args[idx + 1]

    interactive = filename is None

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall((username + "\n").encode())

        response = ""
        while "\n" not in response:
            response += sock.recv(1024).decode()
        line = response.split("\n", 1)[0]

        if line.startswith("error"):
            print(f"Connection refused: {line}")
            return

        print("<<< Welcome to Python-MUD 0.1 >>>")
        print(line.split(" ", 1)[1] if " " in line else line)

        client = MudClient(sock, username, interactive=interactive)

        t = threading.Thread(
            target=receive_messages, args=(sock, client), daemon=True
        )
        t.start()

        if filename:
            run_from_file(client, filename)
        else:
            client.cmdloop()


if __name__ == "__main__":
    main()
