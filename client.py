import cmd
import socket
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


def send_command(sock, line):
    sock.sendall((line + "\n").encode())
    response = ""
    while True:
        chunk = sock.recv(1024).decode()
        response += chunk
        if "\n" in response:
            return response.split("\n", 1)[0]


class MudClient(cmd.Cmd):
    prompt = ""

    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.player_x = 0
        self.player_y = 0
        self.local_monsters = {}

    # --- Движение ---

    def _move(self, dx, dy):
        resp = send_command(self.sock, f"move {dx} {dy}")
        parts = resp.split()
        x, y = int(parts[1]), int(parts[2])
        self.player_x = x
        self.player_y = y
        print(f"Moved to ({x}, {y})")
        if len(parts) > 3 and parts[3] == "encounter":
            name = parts[4]
            hello = parts[5]
            self.local_monsters[(x, y)] = name
            print(cowsay.get_output_string(name, hello))

    def do_up(self, arg):
        self._move(0, -1)

    def do_down(self, arg):
        self._move(0, 1)

    def do_left(self, arg):
        self._move(-1, 0)

    def do_right(self, arg):
        self._move(1, 0)

    # --- addmon ---

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
        resp = send_command(self.sock, f"addmon {name} {x} {y} {hello} 100")
        parts_r = resp.split()
        print(f"Added monster {parts_r[1]} to ({parts_r[2]}, {parts_r[3]}) saying {hello}")
        if len(parts_r) > 4 and parts_r[4] == "replaced":
            print("Replaced the old monster")
        self.local_monsters[(x, y)] = name

    def complete_addmon(self, text, line, begidx, endidx):
        parts = line.split()
        if len(parts) == 1 or (len(parts) == 2 and not line.endswith(" ")):
            return [c for c in cowsay.CHARS if c.startswith(text)]
        return []

    # --- attack ---

    WEAPONS = {"sword": 10, "spear": 15, "axe": 20}

    def _do_attack_monster(self, monster_name, damage):
        resp = send_command(self.sock, f"attack {monster_name} {damage}")
        parts = resp.split()
        if parts[0] == "no_monster":
            print(f"No {parts[1]} here")
            return
        name, actual, hp_left = parts[1], parts[2], int(parts[3])
        print(f"Attacked {name}, damage {actual} hp")
        if hp_left == 0:
            print(f"{name} died")
            pos = (self.player_x, self.player_y)
            if pos in self.local_monsters:
                del self.local_monsters[pos]
        else:
            print(f"{name} now has {hp_left}")

    def do_attack(self, arg):
        parts = arg.split()
        damage = self.WEAPONS["sword"]
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

        self._do_attack_monster(monster_name, damage)

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

    # --- служебные ---

    def do_EOF(self, arg):
        return True

    def default(self, line):
        print("Invalid command")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print("<<< Welcome to Python-MUD 0.1 >>>")
        MudClient(sock).cmdloop()


if __name__ == "__main__":
    main()