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

player_x = 0
player_y = 0
monsters = {}


def handle_command(line):
    global player_x, player_y
    parts = line.strip().split()
    if not parts:
        return ""
    cmd = parts[0]

    if cmd == "move":
        dx, dy = int(parts[1]), int(parts[2])
        player_x = (player_x + dx) % 10
        player_y = (player_y + dy) % 10
        pos = (player_x, player_y)
        if pos in monsters:
            m = monsters[pos]
            return f"moved {player_x} {player_y} encounter {m['name']} {m['hello']}"
        return f"moved {player_x} {player_y}"

    elif cmd == "addmon":
        name = parts[1]
        x, y = int(parts[2]), int(parts[3])
        hello = parts[4]
        hp = int(parts[5])
        replaced = (x, y) in monsters
        monsters[(x, y)] = {"name": name, "hello": hello, "hp": hp}
        if replaced:
            return f"added {name} {x} {y} replaced"
        return f"added {name} {x} {y}"

    elif cmd == "attack":
        name = parts[1]
        damage = int(parts[2])
        pos = (player_x, player_y)
        if pos not in monsters or monsters[pos]["name"] != name:
            return f"no_monster {name}"
        m = monsters[pos]
        actual = min(damage, m["hp"])
        m["hp"] -= actual
        if m["hp"] == 0:
            del monsters[pos]
            return f"attacked {name} {actual} 0"
        return f"attacked {name} {actual} {m['hp']}"

    return "unknown_command"


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(1)
        print(f"Server listening on {HOST}:{PORT}")
        conn, addr = srv.accept()
        with conn:
            buf = ""
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                buf += data
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    response = handle_command(line)
                    conn.sendall((response + "\n").encode())


if __name__ == "__main__":
    main()