import json
import logging

import pytest

from spark.core.errors import ConfigError, PathError
from spark.core.logging_setup import SecretRedactionFilter, configure_logging
from spark.core.paths import data_dir, logs_dir
from spark.core.settings import Settings, load_settings, save_settings


def test_settings_defaults_and_validation(tmp_path):
    path = tmp_path / "settings.json"
    assert load_settings(path)[0] == Settings("")
    with pytest.raises(ConfigError):
        Settings.from_dict({"gemini_model": 4})
    with pytest.raises(ConfigError):
        Settings.from_dict({"log_level": "LOUD"})
    with pytest.raises(ConfigError):
        Settings.from_dict({"start_minimized": "false"})


def test_settings_atomic_write_and_roundtrip(tmp_path):
    path = tmp_path / "settings.json"
    settings = Settings("user-model", "DEBUG", True)
    save_settings(path, settings)
    assert json.loads(path.read_text()) == {
        "gemini_model": "user-model",
        "log_level": "DEBUG",
        "start_minimized": True,
    }
    assert load_settings(path)[0] == settings
    assert list(tmp_path.iterdir()) == [path]


def test_corrupt_settings_backup_and_recovery(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("{")
    settings, recovered = load_settings(path)
    assert settings == Settings("")
    assert recovered
    assert (tmp_path / "settings.json.bad").read_text() == "{"


def test_paths_use_localappdata_and_create(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert data_dir() == tmp_path / "SPARK"
    assert logs_dir().is_dir()


def test_paths_error_without_localappdata(monkeypatch):
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    with pytest.raises(PathError):
        data_dir()


def test_paths_writable_failure_is_reported(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    from pathlib import Path

    original = Path.mkdir

    def fail(path, *args, **kwargs):
        if path == tmp_path / "SPARK":
            raise PermissionError("denied")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", fail)
    with pytest.raises(PathError, match="cannot create"):
        data_dir()


def test_redaction_filter_removes_stored_and_pattern_keys():
    filt = SecretRedactionFilter(("private-secret-123",))
    record = logging.LogRecord(
        "x", logging.INFO, "", 0, "stored=%s api_key=AIza12345678901234567890", (), None
    )
    record.args = ()
    record.msg = "stored=private-secret-123 api_key=AIza12345678901234567890"
    assert filt.filter(record)
    assert "private-secret-123" not in record.getMessage()
    assert "AIza" not in record.getMessage()


def test_log_rotation_configuration(tmp_path):
    logger = configure_logging(tmp_path / "spark.log", "INFO", "secret-value")
    handler = logger.handlers[0]
    assert handler.maxBytes == 1_000_000
    assert handler.backupCount == 3
    logger.info("key secret-value")
    handler.flush()
    assert "secret-value" not in (tmp_path / "spark.log").read_text()


def test_exception_traceback_redacted(tmp_path):
    logger = configure_logging(tmp_path / "trace.log", "INFO", "token-secret")
    try:
        raise ValueError("failed with token-secret")
    except ValueError:
        logger.exception("request failed")
    for handler in logger.handlers:
        handler.flush()
    content = (tmp_path / "trace.log").read_text()
    assert "token-secret" not in content
    assert "[REDACTED]" in content
