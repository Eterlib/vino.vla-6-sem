import sys
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

print("<<< Welcome to Python-MUD 0.1 >>>")


def encounter(x, y):
    if (x, y) in monsters:
        name, hello = monsters[(x, y)]
        print(cowsay.chars[name](hello))


def move(dx, dy):
    global player_x, player_y
    player_x = (player_x + dx) % 10
    player_y = (player_y + dy) % 10
    print(f"Moved to ({player_x}, {player_y})")
    encounter(player_x, player_y)


def addmon(name, x, y, hello):
    if name not in cowsay.chars:
        print("Cannot add unknown monster")
        return
    replaced = (x, y) in monsters
    monsters[(x, y)] = (name, hello)
    print(f"Added monster {name} to ({x}, {y}) saying {hello}")
    if replaced:
        print("Replaced the old monster")


for line in sys.stdin:
    parts = line.strip().split()
    if not parts:
        continue
    cmd = parts[0]
    if cmd == "up":
        move(0, -1)
    elif cmd == "down":
        move(0, 1)
    elif cmd == "left":
        move(-1, 0)
    elif cmd == "right":
        move(1, 0)
    elif cmd == "addmon":
        if len(parts) != 5:
            print("Invalid arguments")
            continue
        try:
            name = parts[1]
            x = int(parts[2])
            y = int(parts[3])
            hello = parts[4]
        except Exception:
            print("Invalid arguments")
            continue
        addmon(name, x, y, hello)
    else:
        print("Invalid command")
