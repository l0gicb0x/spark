"""Validated, atomically persisted application settings."""

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from spark.core.errors import ConfigError

LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


@dataclass(frozen=True)
class Settings:
    gemini_model: str = ""
    log_level: str = "INFO"
    start_minimized: bool = False

    @classmethod
    def from_dict(cls, raw: object) -> "Settings":
        if not isinstance(raw, dict):
            raise ConfigError("Settings must be a JSON object.")
        model = raw.get("gemini_model", "")
        level = raw.get("log_level", "INFO")
        minimized = raw.get("start_minimized", False)
        if not isinstance(model, str):
            raise ConfigError("gemini_model must be a string.")
        if not isinstance(level, str) or level.upper() not in LEVELS:
            raise ConfigError("log_level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL.")
        if not isinstance(minimized, bool):
            raise ConfigError("start_minimized must be a boolean.")
        return cls(model.strip(), level.upper(), minimized)


DEFAULT_SETTINGS = Settings(gemini_model="")


def load_settings(path: Path) -> tuple[Settings, bool]:
    """Load settings; recover corrupt JSON as defaults and return recovery flag."""
    if not path.exists():
        return DEFAULT_SETTINGS, False
    try:
        return Settings.from_dict(json.loads(path.read_text(encoding="utf-8"))), False
    except (OSError, json.JSONDecodeError, ConfigError):
        bad = path.with_name("settings.json.bad")
        try:
            if bad.exists():
                bad.unlink()
            path.replace(bad)
        except OSError as exc:
            raise ConfigError(f"Settings are invalid and could not be backed up: {exc}") from exc
        return DEFAULT_SETTINGS, True


def save_settings(path: Path, settings: Settings) -> None:
    """Atomically persist validated settings."""
    validated = Settings.from_dict(asdict(settings))
    temporary: str | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as file:
            temporary = file.name
            json.dump(asdict(validated), file, indent=2)
            file.flush()
            os.fsync(file.fileno())
        Path(temporary).replace(path)
    except OSError as exc:
        raise ConfigError(f"SPARK could not save settings to {path}: {exc}") from exc
    finally:
        if temporary and Path(temporary).exists():
            Path(temporary).unlink(missing_ok=True)
