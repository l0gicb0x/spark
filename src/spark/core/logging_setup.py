"""Rotating logs with API-key redaction."""

import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path

KEY_PATTERN = re.compile(r"(?i)(AIza[0-9A-Za-z_-]{20,}|(?:api[_ -]?key\s*[=:]\s*)[^\s,;]+)")


class SecretRedactionFilter(logging.Filter):
    def __init__(self, secrets: tuple[str, ...] = ()):
        super().__init__()
        self.secrets = tuple(s for s in secrets if s)

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
            if record.exc_info:
                message += "\n" + logging.Formatter().formatException(record.exc_info)
                record.exc_info = None
            for secret in self.secrets:
                message = message.replace(secret, "[REDACTED]")
            message = KEY_PATTERN.sub("[REDACTED]", message)
            record.msg, record.args = message, ()
        except Exception:
            record.msg, record.args = "[log message redaction failed]", ()
        return True


def configure_logging(path: Path, level: str, secret: str | None = None) -> logging.Logger:
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("spark")
    logger.setLevel(getattr(logging, level.upper()))
    for old_handler in logger.handlers[:]:
        logger.removeHandler(old_handler)
        old_handler.close()
    handler = RotatingFileHandler(path, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.addFilter(SecretRedactionFilter((secret,) if secret else ()))
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
    return logger
