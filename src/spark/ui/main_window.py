"""Text chat shell for Phase 1."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from spark import __version__
from spark.core.channels import TextChannel
from spark.core.commands import CommandHandler
from spark.core.logging_setup import configure_logging
from spark.core.paths import log_path, settings_path
from spark.core.secrets import get_key, is_configured
from spark.core.settings import Settings, save_settings
from spark.ui.settings_dialog import SettingsDialog
from spark.ui.tray import make_icon


class MessageInput(QPlainTextEdit):
    send_requested = Signal()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if (
            event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        ):
            self.send_requested.emit()
            return
        super().keyPressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings, logger, on_quit):
        super().__init__()
        self.settings = settings
        self.logger = logger
        self.on_quit = on_quit
        self.tray_available = True
        self.setWindowTitle("SPARK")
        self.setWindowIcon(make_icon())
        self.resize(720, 560)
        self.transcript = QTextBrowser()
        self.input = MessageInput()
        self.input.setPlaceholderText("Type a message or /help…")
        self.input.setMaximumHeight(120)
        send = QPushButton("Send")
        send.clicked.connect(self.send_message)
        self.input.send_requested.connect(self.send_message)
        row = QHBoxLayout()
        row.addWidget(self.input, 1)
        row.addWidget(send)
        layout = QVBoxLayout()
        layout.addWidget(self.transcript, 1)
        layout.addLayout(row)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.dialog = None
        self.commands = CommandHandler(
            version=__version__,
            log_path=str(log_path()),
            settings_path=str(settings_path()),
            key_configured=is_configured,
            model=lambda: self.settings.gemini_model,
            open_settings=self.open_settings,
            clear=self.transcript.clear,
            quit_app=on_quit,
        )
        self.channel = TextChannel(self.process_input, lambda text: self.append("SPARK", text))
        if not is_configured():
            self.append(
                "SPARK",
                "Welcome to SPARK. Add your Gemini API key in Settings to prepare for AI chat "
                "in Phase 2. Create a key in Google AI Studio and check Google's current policy "
                "for availability and terms. Until a key is configured, closing this window "
                "exits SPARK.",
            )
        self.append("SPARK", "AI chat arrives in Phase 2. Type /help for available commands.")

    def append(self, speaker: str, text: str) -> None:
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        escaped = escaped.replace("\n", "<br>")
        self.transcript.append(f"<b>{speaker}</b><br>{escaped}")

    def process_input(self, text: str) -> str:
        if text.startswith("/"):
            return self.commands.handle(text) or ""
        return "AI chat arrives in Phase 2. Type /help for available commands."

    def send_message(self) -> None:
        text = self.input.toPlainText().strip()
        if not text:
            return
        self.input.clear()
        self.append("You", text)
        response = self.channel.receive(text)
        if response and response != "Transcript cleared.":
            self.channel.send(response)

    def open_settings(self) -> None:
        self.dialog = SettingsDialog(self.settings, settings_path(), self.logger, self)
        if self.dialog.exec():
            self.settings = self.dialog.settings
            self.logger = configure_logging(log_path(), self.settings.log_level, get_key())
            save_settings(settings_path(), self.settings)

    def closeEvent(self, event) -> None:
        if not is_configured() or not self.tray_available:
            event.accept()
            self.on_quit()
        else:
            event.ignore()
            self.hide()
