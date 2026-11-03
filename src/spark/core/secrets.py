"""Credential Manager access through keyring."""

import keyring

from spark.core.errors import SecretError

SERVICE = "SPARK"
USERNAME = "gemini_api_key"


def get_key() -> str | None:
    try:
        return keyring.get_password(SERVICE, USERNAME)
    except Exception as exc:
        raise SecretError("Could not read the Gemini key from Windows Credential Manager.") from exc


def set_key(value: str) -> None:
    if not value.strip():
        raise SecretError("The Gemini API key cannot be empty.")
    try:
        keyring.set_password(SERVICE, USERNAME, value.strip())
    except Exception as exc:
        raise SecretError("Could not save the Gemini key to Windows Credential Manager.") from exc


def delete_key() -> None:
    try:
        keyring.delete_password(SERVICE, USERNAME)
    except keyring.errors.PasswordDeleteError:
        return
    except Exception as exc:
        raise SecretError(
            "Could not delete the Gemini key from Windows Credential Manager."
        ) from exc


def is_configured() -> bool:
    return bool(get_key())


def masked_key() -> str:
    value = get_key()
    return f"••••{value[-4:]}" if value else "Not configured"
