import cmd
import cowsay
from cowsay.main import draw

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

cowsay.chars["jgsbat"] = lambda text: draw(JGSBAT_BODY, text, to_console=False)

player_x = 0
player_y = 0
monsters = {}


def encounter(x, y):
    if (x, y) in monsters:
        m = monsters[(x, y)]
        print(cowsay.chars[m["name"]](m["hello"]))


def move(dx, dy):
    global player_x, player_y
    player_x = (player_x + dx) % 10
    player_y = (player_y + dy) % 10
    print(f"Moved to ({player_x}, {player_y})")
    encounter(player_x, player_y)


def execute_command(line):
    """Разбор и выполнение одной команды. Источник команды не важен."""
    pass


class MudCmd(cmd.Cmd):
    prompt = ""

    # Движение

    def do_up(self, arg):
        move(0, -1)

    def do_down(self, arg):
        move(0, 1)

    def do_left(self, arg):
        move(-1, 0)

    def do_right(self, arg):
        move(1, 0)

    # addmon

    def do_addmon(self, arg):
        parts = arg.split()
        if len(parts) != 4:
            print("Invalid arguments")
            return
        name, x_s, y_s, hello = parts
        if name not in cowsay.chars:
            print("Cannot add unknown monster")
            return
        try:
            x, y = int(x_s), int(y_s)
        except ValueError:
            print("Invalid arguments")
            return
        replaced = (x, y) in monsters
        monsters[(x, y)] = {"name": name, "hello": hello, "hp": 100}
        print(f"Added monster {name} to ({x}, {y}) saying {hello}")
        if replaced:
            print("Replaced the old monster")

    def complete_addmon(self, text, line, begidx, endidx):
        parts = line.split()
        if len(parts) == 1 or (len(parts) == 2 and not line.endswith(" ")):
            return [c for c in cowsay.chars if c.startswith(text)]
        return []

    # attack

    def _do_attack_monster(self, pos, damage):
        m = monsters[pos]
        name = m["name"]
        actual = min(damage, m["hp"])
        m["hp"] -= actual
        print(f"Attacked {name}, damage {actual} hp")
        if m["hp"] == 0:
            print(f"{name} died")
            del monsters[pos]
        else:
            print(f"{name} now has {m['hp']}")

    WEAPONS = {"sword": 10, "spear": 15, "axe": 20}

    def do_attack(self, arg):
        parts = arg.split()
        damage = 10
        if parts:
            if parts[0] == "with":
                if len(parts) < 2:
                    print("Unknown weapon")
                    return
                weapon = parts[1]
                if weapon not in self.WEAPONS:
                    print("Unknown weapon")
                    return
                damage = self.WEAPONS[weapon]
            else:
                print("Invalid command")
                return

        pos = (player_x, player_y)
        if pos not in monsters:
            print("No monster here")
            return
        self._do_attack_monster(pos, damage)

    def complete_attack(self, text, line, begidx, endidx):
        parts = line.split()
        if "with" in parts:
            return [w for w in self.WEAPONS if w.startswith(text)]
        if len(parts) <= 2 and not line.endswith(" "):
            return ["with"] if "with".startswith(text) else []
        return ["with"] if not line.endswith(" ") else []

    # служебные

    def do_EOF(self, arg):
        return True

    def default(self, line):
        print("Invalid command")


print("<<< Welcome to Python-MUD 0.1 >>>")
MudCmd().cmdloop()
