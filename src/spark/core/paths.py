"""User-owned SPARK data paths."""

import os
from pathlib import Path

from spark.core.errors import PathError


def data_dir() -> Path:
    """Return %LOCALAPPDATA%\\SPARK, creating it on demand."""
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        raise PathError(
            "Windows did not provide LOCALAPPDATA; SPARK cannot locate its data folder."
        )
    path = Path(local) / "SPARK"
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise PathError(f"SPARK cannot create its data folder at {path}: {exc}") from exc
    return path


def settings_path() -> Path:
    return data_dir() / "settings.json"


def logs_dir() -> Path:
    path = data_dir() / "logs"
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise PathError(f"SPARK cannot create its log folder at {path}: {exc}") from exc
    return path


def log_path() -> Path:
    return logs_dir() / "spark.log"
