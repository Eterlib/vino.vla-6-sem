import sys
import cowsay
import shlex

list_cows = cowsay.list_cows()

player_x = 0
player_y = 0

monsters = {}


def encounter(x, y):
    if (x, y) in monsters:
        name, hello, hp = monsters[(x, y)]
        print(cowsay.cowsay(hello, cow=name))


def move(dx, dy):
    global player_x, player_y
    player_x = (player_x + dx) % 10
    player_y = (player_y + dy) % 10
    print(f"Moved to ({player_x}, {player_y})")
    encounter(player_x, player_y)


def addmon(name, x, y, hello, hp=100):
    if name not in list_cows:
        print("Cannot add unknown monster")
        return
    replaced = (x, y) in monsters
    monsters[(x, y)] = (name, hello, hp)
    print(f"Added monster {name} to ({x}, {y}) saying {hello}")
    if replaced:
        print("Replaced the old monster")


print("<<< Welcome to Python-MUD 0.1 >>>")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        parts = shlex.split(line)
    except ValueError:
        print("Invalid command")
        continue

    cmd = parts[0]
    args = parts[1:]

    if cmd == "up":
        move(0, -1)
    elif cmd == "down":
        move(0, 1)
    elif cmd == "left":
        move(-1, 0)
    elif cmd == "right":
        move(1, 0)
    elif cmd == "addmon":
        if len(args) < 7:
            print("Invalid arguments")
            continue

        name = args[0]
        param_dict = {}
        i = 1
        try:
            while i < len(args):
                key = args[i]
                if key == "hello":
                    param_dict["hello"] = args[i + 1]
                    i += 2
                elif key == "hp":
                    param_dict["hp"] = int(args[i + 1])
                    i += 2
                elif key == "coords":
                    param_dict["x"] = int(args[i + 1])
                    param_dict["y"] = int(args[i + 2])
                    i += 3
                else:
                    raise ValueError("Unknown parameter")
            if not all(k in param_dict for k in ("hello", "hp", "x", "y")):
                raise ValueError("Missing parameter")
        except:
            print("Invalid arguments")
            continue

        addmon(
            name,
            param_dict["x"],
            param_dict["y"],
            param_dict["hello"],
            param_dict["hp"],
        )
    else:
        print("Invalid command")
