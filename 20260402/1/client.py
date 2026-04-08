import cmd
import sys
import socket
import threading
import cowsay

JGSBAT_BODY = r"""
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\''--''//__
         (((""`  `"")))
"""

cowsay.CHARS["jgsbat"] = JGSBAT_BODY

HOST = "127.0.0.1"
PORT = 5555


class MudClient(cmd.Cmd):
    prompt = ""

    def __init__(self, sock, username):
        super().__init__()
        self.sock = sock
        self.username = username
        self.player_x = 0
        self.player_y = 0
        self.local_monsters = {}

    def send(self, line):
        """Отправляет команду серверу без ожидания ответа"""
        self.sock.sendall((line + "\n").encode())

    # Движение
    def do_up(self, arg):
        self.send("move 0 -1")

    def do_down(self, arg):
        self.send("move 0 1")

    def do_left(self, arg):
        self.send("move -1 0")

    def do_right(self, arg):
        self.send("move 1 0")

    # addmon
    def do_addmon(self, arg):
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
        parts = line.split()
        if len(parts) == 1 or (len(parts) == 2 and not line.endswith(" ")):
            return [c for c in cowsay.CHARS if c.startswith(text)]
        return []

    # attack
    WEAPONS = {"sword": 10, "spear": 15, "axe": 20}

    def do_attack(self, arg):
        parts = arg.split()
        damage = self.WEAPONS["sword"]
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
            if weapon not in self.WEAPONS:
                print("Unknown weapon")
                return
            damage = self.WEAPONS[weapon]

        if monster_name is None:
            print("No monster here")
            return

        self.send(f"attack {monster_name} {damage} {weapon}")

    def complete_attack(self, text, line, begidx, endidx):
        parts = line.split()
        if "with" in parts:
            return [w for w in self.WEAPONS if w.startswith(text)]
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
        if not arg:
            print("Usage: sayall <message>")
            return
        if arg.startswith('"') and arg.endswith('"'):
            arg = arg[1:-1]
        self.send(f"sayall {arg}")

    # --- служебные ---
    def do_EOF(self, arg):
        return True

    def default(self, line):
        print("Invalid command")


def receive_messages(sock, client):
    """Поток для асинхронного приёма сообщений от сервера"""
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


def handle_server_message(line, client):
    """Обрабатывает сообщение от сервера и выводит его"""
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

    print(f"{client.prompt}{readline_get_line_buffer()}", end="", flush=True)


def readline_get_line_buffer():
    try:
        import readline
        return readline.get_line_buffer()
    except Exception:
        return ""


def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <username>")
        sys.exit(1)

    username = sys.argv[1]

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

        print(f"<<< Welcome to Python-MUD 0.1 >>>")
        print(line.split(" ", 1)[1] if " " in line else line)

        client = MudClient(sock, username)

        t = threading.Thread(target=receive_messages, args=(sock, client), daemon=True)
        t.start()

        client.cmdloop()


if __name__ == "__main__":
    main()
