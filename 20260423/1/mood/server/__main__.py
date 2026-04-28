"""MOOD server entry point.

This module implements the MOOD game server with support
for multiple clients, wandering monsters, chat and localization.
"""

import random
import socket
import threading
import time
import gettext
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

wander_enabled = True


def get_translation(locale):
    """Get translation object for given locale."""
    try:
        return gettext.translation(
            'messages',
            localedir='mood/server/po',
            languages=[locale],
        )
    except FileNotFoundError:
        return gettext.NullTranslations()


def send_raw(username, message):
    """Send raw string message to a specific client."""
    with clients_lock:
        if username in clients:
            try:
                clients[username]["conn"].sendall((message + "\n").encode())
            except Exception:
                pass


def broadcast_raw(message_by_locale):
    """Send message to all clients using per-client locale."""
    with clients_lock:
        for username, info in list(clients.items()):
            try:
                t = get_translation(info.get("locale", "en"))
                msg = message_by_locale(t.gettext, t.ngettext)
                info["conn"].sendall((msg + "\n").encode())
            except Exception:
                pass


def send_localized(username, message_by_locale):
    """Send localized message to a specific client."""
    with clients_lock:
        if username not in clients:
            return
        try:
            t = get_translation(clients[username].get("locale", "en"))
            msg = message_by_locale(t.gettext, t.ngettext)
            clients[username]["conn"].sendall((msg + "\n").encode())
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
        if not wander_enabled:
            continue
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

        broadcast_raw(lambda g, ng: f"{name} moved one cell {direction}")
        encounter_at(new_pos)


def handle_command(username, line):
    """Handle a command received from a client."""
    global wander_enabled
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
        send_raw(username, f"moved {x} {y}")
        if pos in monsters:
            m = monsters[pos]
            send_raw(username, f"encounter {m['name']} {m['hello']}")

    elif cmd == "addmon":
        name = parts[1]
        x, y = int(parts[2]), int(parts[3])
        hello = parts[4]
        hp = int(parts[5])
        replaced = (x, y) in monsters
        monsters[(x, y)] = {"name": name, "hello": hello, "hp": hp}
        if replaced:
            send_raw(username, f"added {name} {x} {y} replaced")
        else:
            send_raw(username, f"added {name} {x} {y}")
        broadcast_raw(lambda g, ng: (
            "{} ".format(username) +
            g("added monster {} at ({}, {}) with {} {}.").format(
                name, x, y, hp, ng("point", "points", hp)
            )
        ))

    elif cmd == "attack":
        name = parts[1]
        damage = int(parts[2])
        weapon = parts[3] if len(parts) > 3 else "sword"
        with clients_lock:
            x = clients[username]["x"]
            y = clients[username]["y"]
        pos = (x, y)
        if pos not in monsters or monsters[pos]["name"] != name:
            send_raw(username, f"no_monster {name}")
            return
        m = monsters[pos]
        actual = min(damage, m["hp"])
        m["hp"] -= actual
        if m["hp"] == 0:
            del monsters[pos]
            broadcast_raw(lambda g, ng: (
                "{} ".format(username) +
                g("attacked {} with {}, damage {} {}, {} died.").format(
                    name, weapon, actual, ng("point", "points", actual), name
                )
            ))
        else:
            hp_left = m["hp"]
            broadcast_raw(lambda g, ng: (
                "{} ".format(username) +
                g("attacked {} with {}, damage {} {}, {} has {} {} left.").format(
                    name, weapon, actual, ng("point", "points", actual),
                    name, hp_left, ng("point", "points", hp_left)
                )
            ))

    elif cmd == "sayall":
        message = " ".join(parts[1:])
        broadcast_raw(lambda g, ng: f"{username}: {message}")

    elif cmd == "movemonsters":
        if parts[1] == "on":
            wander_enabled = True
            send_raw(username, "Moving monsters: on")
        elif parts[1] == "off":
            wander_enabled = False
            send_raw(username, "Moving monsters: off")

    elif cmd == "locale":
        locale = parts[1]
        with clients_lock:
            clients[username]["locale"] = locale
        send_localized(
            username,
            lambda g, ng: g("Set up locale: {}").format(locale)
        )


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
            clients[username] = {"conn": conn, "x": 0, "y": 0, "locale": "en"}

        conn.sendall(f"ok Welcome, {username}!\n".encode())
        broadcast_raw(lambda g, ng: g("{} joined the game.").format(username))

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
            broadcast_raw(lambda g, ng: g("{} left the game.").format(username))
        conn.close()


def run_server(host=HOST, port=PORT):
    """Start the MOOD server on given host and port."""
    wander_thread = threading.Thread(target=wander_monsters, daemon=True)
    wander_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(10)
        print(f"Server listening on {host}:{port}")
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(
                target=handle_client, args=(conn, addr), daemon=True
            )
            t.start()


def main():
    """Start the MOOD server and wandering monster thread."""
    run_server()


if __name__ == "__main__":
    main()