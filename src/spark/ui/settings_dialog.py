"""Settings UI, including secure API-key entry and connection test."""

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from spark.core import secrets
from spark.core.errors import SecretError
from spark.core.logging_setup import configure_logging
from spark.core.paths import log_path
from spark.core.settings import Settings, save_settings
from spark.providers.gemini import GeminiProvider
from spark.ui.workers import ConnectionWorker


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, path, logger, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SPARK Settings")
        self.settings = settings
        self.path = path
        self.logger = logger
        self.pool = QThreadPool.globalInstance()
        self.model = QLineEdit(settings.gemini_model)
        self.key = QLineEdit()
        self.key.setEchoMode(QLineEdit.EchoMode.Password)
        self.key.setPlaceholderText(secrets.masked_key())
        self.level = QComboBox()
        self.level.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level.setCurrentText(settings.log_level)
        self.minimized = QCheckBox("Start minimized")
        self.minimized.setChecked(settings.start_minimized)
        form = QFormLayout()
        form.addRow("Gemini model", self.model)
        form.addRow("Gemini API key", self.key)
        form.addRow("Log level", self.level)
        form.addRow("", self.minimized)
        save = QPushButton("Save")
        save.clicked.connect(self.save)
        delete = QPushButton("Delete key…")
        delete.clicked.connect(self.delete_key)
        test = QPushButton("Test connection")
        test.clicked.connect(self.test_connection)
        actions = QHBoxLayout()
        for button in (save, delete, test):
            actions.addWidget(button)
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(actions)
        layout.addWidget(close)

    def save(self):
        try:
            if self.key.text():
                secrets.set_key(self.key.text())
                self.logger = configure_logging(
                    log_path(), self.settings.log_level, self.key.text().strip()
                )
            self.key.clear()
            self.settings = Settings(
                self.model.text(), self.level.currentText(), self.minimized.isChecked()
            )
            save_settings(self.path, self.settings)
            QMessageBox.information(self, "Settings", "Settings saved.")
            self.accept()
        except Exception as exc:
            QMessageBox.warning(self, "Settings", str(exc))

    def delete_key(self):
        answer = QMessageBox.question(self, "Delete Gemini key", "Delete the saved Gemini API key?")
        if answer == QMessageBox.StandardButton.Yes:
            try:
                secrets.delete_key()
                self.key.clear()
                self.key.setPlaceholderText("Not configured")
            except SecretError as exc:
                QMessageBox.warning(self, "Settings", str(exc))

    def test_connection(self):
        try:
            key = self.key.text().strip() or secrets.get_key()
            if not key:
                QMessageBox.information(self, "Gemini test", "No Gemini API key is configured.")
                return
            if self.key.text():
                secrets.set_key(self.key.text())
                key = self.key.text().strip()
                self.key.clear()
                self.key.setPlaceholderText(secrets.masked_key())
                self.logger = configure_logging(log_path(), self.settings.log_level, key)
            worker = ConnectionWorker(GeminiProvider(), key, self.model.text())
            worker.signals.finished.connect(
                lambda msg: QMessageBox.information(self, "Gemini test", msg)
            )
            worker.signals.failed.connect(lambda msg: QMessageBox.warning(self, "Gemini test", msg))
            self.pool.start(worker)
        except Exception as exc:
            self.logger.exception("Could not start Gemini connection test")
            QMessageBox.warning(self, "Gemini test", str(exc))
