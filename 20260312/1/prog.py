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


    def do_up(self, arg):
        move(0, -1)

    def do_down(self, arg):
        move(0, 1)

    def do_left(self, arg):
        move(-1, 0)

    def do_right(self, arg):
        move(1, 0)


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


    def do_EOF(self, arg):
        return True

    def default(self, line):
        print("Invalid command")


print("<<< Welcome to Python-MUD 0.1 >>>")
MudCmd().cmdloop()
