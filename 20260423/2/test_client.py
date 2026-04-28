"""Tests for MOOD client command translation to protocol format."""

from unittest.mock import MagicMock
import pytest
from mood.client.__main__ import MudClient


@pytest.fixture
def client():
    """Create a MudClient with a mock socket."""
    sock = MagicMock()
    return MudClient(sock, "testplayer")


def get_sent(client):
    """Get the last message sent to server."""
    call_args = client.sock.sendall.call_args
    return call_args[0][0].decode().strip()


def test_attack_sword(client):
    """Test attack with sword sends correct protocol message."""
    client.local_monsters[(0, 0)] = "dragon"
    client.onecmd("attack dragon with sword")
    assert get_sent(client) == "attack dragon 10 sword"


def test_attack_axe(client):
    """Test attack with axe sends correct protocol message."""
    client.local_monsters[(0, 0)] = "dragon"
    client.onecmd("attack dragon with axe")
    assert get_sent(client) == "attack dragon 20 axe"


def test_attack_unknown_weapon(client, capsys):
    """Test attack with unknown weapon prints error and does not send."""
    client.local_monsters[(0, 0)] = "dragon"
    client.onecmd("attack dragon with laser")
    captured = capsys.readouterr()
    assert "Unknown weapon" in captured.out
    client.sock.sendall.assert_not_called()


def test_addmon_cow(client):
    """Test addmon sends protocol message with default hp=100."""
    client.onecmd("addmon cow 1 0 hello")
    assert get_sent(client) == "addmon cow 1 0 hello 100"


def test_addmon_dragon(client):
    """Test addmon with different monster sends correct protocol message."""
    client.onecmd("addmon dragon 3 5 Rawr")
    assert get_sent(client) == "addmon dragon 3 5 Rawr 100"


def test_addmon_invalid_args(client, capsys):
    """Test addmon with wrong number of arguments prints error."""
    client.onecmd("addmon cow 1")
    captured = capsys.readouterr()
    assert "Invalid arguments" in captured.out
    client.sock.sendall.assert_not_called()
