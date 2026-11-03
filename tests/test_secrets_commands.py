from unittest.mock import Mock

import keyring
import pytest

from spark.core import secrets
from spark.core.commands import CommandHandler
from spark.core.errors import SecretError


class MemoryBackend(keyring.backend.KeyringBackend):
    priority = 1

    def __init__(self):
        self.data = {}

    def get_password(self, service, username):
        return self.data.get((service, username))

    def set_password(self, service, username, password):
        self.data[(service, username)] = password

    def delete_password(self, service, username):
        if (service, username) not in self.data:
            raise keyring.errors.PasswordDeleteError("missing")
        del self.data[(service, username)]


def test_secret_helpers_use_mocked_backend(monkeypatch):
    backend = MemoryBackend()
    monkeypatch.setattr(secrets.keyring, "get_password", backend.get_password)
    monkeypatch.setattr(secrets.keyring, "set_password", backend.set_password)
    monkeypatch.setattr(secrets.keyring, "delete_password", backend.delete_password)
    secrets.set_key("  test-key-value ")
    assert secrets.get_key() == "test-key-value"
    assert secrets.is_configured()
    assert secrets.masked_key() == "••••alue"
    secrets.delete_key()
    assert not secrets.is_configured()


def test_empty_secret_rejected():
    with pytest.raises(SecretError):
        secrets.set_key(" ")


def make_commands():
    return CommandHandler(
        version="0.1",
        log_path="log",
        settings_path="settings",
        key_configured=lambda: True,
        model=lambda: "model",
        open_settings=Mock(),
        clear=Mock(),
        quit_app=Mock(),
    )


@pytest.mark.parametrize(
    "command,expected",
    [
        ("/help", "Commands:"),
        ("/version", "SPARK 0.1"),
        ("/status", "Gemini key: configured"),
        ("/unknown", "Unknown command:"),
    ],
)
def test_commands(command, expected):
    assert expected in make_commands().handle(command)


@pytest.mark.parametrize(
    "command,callback", [("/settings", "open_settings"), ("/clear", "clear"), ("/quit", "quit_app")]
)
def test_commands_call_actions(command, callback):
    handler = make_commands()
    handler.handle(command)
    getattr(handler, callback).assert_called_once()
