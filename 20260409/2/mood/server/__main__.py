"""MOOD server entry point.

This module implements the MOOD game server with support
for multiple clients, wandering monsters, and chat.
"""

import random
import socket
import threading
import time
from mood.common import setup_cowsay
from mood.common.constants import HOST, PORT

setup_cowsay()

monsters = {}
clients = {}
clients_lock = threading.Lock()

DIRECTIONS = {
    "right": (1, 0),
    "left": (-1, 0),
    "up": (0, -1),
    "down": (0, 1),
}

WANDER_INTERVAL = 30


def broadcast(message):
    """Send a message to all connected clients."""
    with clients_lock:
        for username, info in list(clients.items()):
            try:
                info["conn"].sendall((message + "\n").encode())
            except Exception:
                pass


def send_to(username, message):
    """Send a message to a specific client."""
    with clients_lock:
        if username in clients:
            try:
                clients[username]["conn"].sendall((message + "\n").encode())
            except Exception:
                pass


def encounter_at(pos):
    """Notify all players at given position about a monster encounter."""
    if pos not in monsters:
        return
    m = monsters[pos]
    with clients_lock:
        for username, info in list(clients.items()):
            if (info["x"], info["y"]) == pos:
                try:
                    info["conn"].sendall(
                        f"encounter {m['name']} {m['hello']}\n".encode()
                    )
                except Exception:
                    pass


def wander_monsters():
    """Move a random monster one cell every WANDER_INTERVAL seconds."""
    while True:
        time.sleep(WANDER_INTERVAL)
        with clients_lock:
            if not monsters:
                continue
            while True:
                pos = random.choice(list(monsters.keys()))
                direction = random.choice(list(DIRECTIONS.keys()))
                dx, dy = DIRECTIONS[direction]
                new_x = (pos[0] + dx) % 10
                new_y = (pos[1] + dy) % 10
                new_pos = (new_x, new_y)
                if new_pos not in monsters:
                    break
            monster = monsters.pop(pos)
            monsters[new_pos] = monster
            name = monster["name"]

        broadcast(f"{name} moved one cell {direction}")
        encounter_at(new_pos)


def handle_command(username, line):
    """Handle a command received from a client."""
    parts = line.split()
    if not parts:
        return
    cmd = parts[0]

    if cmd == "move":
        dx, dy = int(parts[1]), int(parts[2])
        with clients_lock:
            x = (clients[username]["x"] + dx) % 10
            y = (clients[username]["y"] + dy) % 10
            clients[username]["x"] = x
            clients[username]["y"] = y
        pos = (x, y)
        send_to(username, f"moved {x} {y}")
        if pos in monsters:
            m = monsters[pos]
            send_to(username, f"encounter {m['name']} {m['hello']}")

    elif cmd == "addmon":
        name = parts[1]
        x, y = int(parts[2]), int(parts[3])
        hello = parts[4]
        hp = int(parts[5])
        replaced = (x, y) in monsters
        monsters[(x, y)] = {"name": name, "hello": hello, "hp": hp}
        if replaced:
            send_to(username, f"added {name} {x} {y} replaced")
        else:
            send_to(username, f"added {name} {x} {y}")
        broadcast(
            f"{username} added monster {name} at ({x}, {y}) with {hp} hp"
        )

    elif cmd == "attack":
        name = parts[1]
        damage = int(parts[2])
        weapon = parts[3] if len(parts) > 3 else "sword"
        with clients_lock:
            x = clients[username]["x"]
            y = clients[username]["y"]
        pos = (x, y)
        if pos not in monsters or monsters[pos]["name"] != name:
            send_to(username, f"no_monster {name}")
            return
        m = monsters[pos]
        actual = min(damage, m["hp"])
        m["hp"] -= actual
        if m["hp"] == 0:
            del monsters[pos]
            broadcast(
                f"{username} attacked {name} with {weapon}, "
                f"damage {actual} hp, {name} died"
            )
        else:
            broadcast(
                f"{username} attacked {name} with {weapon}, "
                f"damage {actual} hp, {name} has {m['hp']} hp left"
            )

    elif cmd == "sayall":
        message = " ".join(parts[1:])
        broadcast(f"{username}: {message}")


def handle_client(conn, addr):
    """Handle a single client connection lifecycle."""
    username = None
    buf = ""
    try:
        while "\n" not in buf:
            data = conn.recv(1024).decode()
            if not data:
                return
            buf += data
        line, buf = buf.split("\n", 1)
        username = line.strip()

        with clients_lock:
            if username in clients:
                conn.sendall("error name_taken\n".encode())
                conn.close()
                return
            clients[username] = {"conn": conn, "x": 0, "y": 0}

        conn.sendall(f"ok Welcome, {username}!\n".encode())
        broadcast(f"{username} joined the game")

        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            buf += data
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                handle_command(username, line.strip())

    finally:
        if username:
            with clients_lock:
                if username in clients:
                    del clients[username]
            broadcast(f"{username} left the game")
        conn.close()


def main():
    """Start the MOOD server and wandering monster thread."""
    wander_thread = threading.Thread(target=wander_monsters, daemon=True)
    wander_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(10)
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(
                target=handle_client, args=(conn, addr), daemon=True
            )
            t.start()


if __name__ == "__main__":
    main()
