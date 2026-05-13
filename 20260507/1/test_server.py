"""Tests for MOOD server command handling."""

import multiprocessing
import socket
import time
import pytest
from mood.server.__main__ import run_server

HOST = "127.0.0.1"
PORT = 5556


class ServerConnection:
    """Helper class for communicating with the server."""

    def __init__(self, sock):
        """Initialize with a connected socket."""
        self.sock = sock
        self.buf = ""

    def recv_line(self):
        """Receive a single line from server."""
        while "\n" not in self.buf:
            self.buf += self.sock.recv(1024).decode()
        line, self.buf = self.buf.split("\n", 1)
        return line

    def send(self, message):
        """Send a message to server."""
        self.sock.sendall((message + "\n").encode())

    def send_recv(self, message):
        """Send a message and receive one line response."""
        self.send(message)
        return self.recv_line()


@pytest.fixture
def conn():
    """Start server and connect client, teardown after test."""
    proc = multiprocessing.Process(
        target=run_server, args=(HOST, PORT), daemon=True
    )
    proc.start()
    time.sleep(0.5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    c = ServerConnection(sock)

    c.send("testplayer")
    c.recv_line()
    c.recv_line()

    c.send_recv("movemonsters off")

    yield c

    sock.close()
    proc.terminate()
    proc.join()


def test_addmon(conn):
    """Test adding a monster to the game."""
    resp = conn.send_recv("addmon cow 1 0 hello 100")
    assert "added" in resp
    assert "cow" in resp


def test_encounter(conn):
    """Test moving to a cell with a monster triggers encounter."""
    conn.send_recv("addmon cow 1 0 hello 100")
    conn.recv_line()

    moved = conn.send_recv("move 1 0")
    assert "moved" in moved

    encounter = conn.recv_line()
    assert "encounter" in encounter
    assert "cow" in encounter


def test_attack(conn):
    """Test attacking a monster reduces its health."""
    conn.send_recv("addmon cow 1 0 hello 100")
    conn.recv_line()

    conn.send_recv("move 1 0")
    conn.recv_line()

    resp = conn.send_recv("attack cow 10 sword")
    assert "attacked" in resp
    assert "cow" in resp

def test_attack_russian(conn):
    """Test attack response is localized in Russian."""
    conn.send_recv("locale ru_RU")
    conn.send_recv("addmon cow 1 0 hello 100")
    conn.recv_line()

    conn.send_recv("move 1 0")
    conn.recv_line()

    resp = conn.send_recv("attack cow 10 sword")
    assert "атаковал" in resp
    assert "очко" in resp or "очка" in resp or "очков" in resp
