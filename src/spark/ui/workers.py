"""Background task objects for slow provider operations."""

import logging

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

logger = logging.getLogger("spark")


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class ConnectionWorker(QRunnable):
    def __init__(self, provider, api_key: str, model: str):
        super().__init__()
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            self.signals.finished.emit(self.provider.test_connection(self.api_key, self.model))
        except Exception as exc:
            logger.exception("Connection test worker failed")
            self.signals.failed.emit(str(exc))
