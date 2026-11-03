"""Qt application setup and lifecycle."""

import getpass
import hashlib
import sys

from PySide6.QtCore import QThreadPool
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from spark import __version__
from spark.core import secrets
from spark.core.errors import SecretError
from spark.core.logging_setup import configure_logging
from spark.core.paths import log_path, settings_path
from spark.core.settings import load_settings, save_settings
from spark.ui.main_window import MainWindow
from spark.ui.tray import Tray

SERVER_NAME = "SPARK-" + hashlib.sha256(getpass.getuser().encode()).hexdigest()[:16]


def activate_existing(server_name: str = SERVER_NAME) -> bool:
    socket = QLocalSocket()
    socket.connectToServer(server_name)
    if not socket.waitForConnected(500):
        return False
    socket.write(b"show")
    socket.waitForBytesWritten(500)
    socket.disconnectFromServer()
    return True


def run() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("SPARK")
    app.setQuitOnLastWindowClosed(False)
    if activate_existing():
        return 0
    server = QLocalServer()
    server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)
    if not server.listen(SERVER_NAME):
        QLocalServer.removeServer(SERVER_NAME)
        if not server.listen(SERVER_NAME):
            QMessageBox.critical(
                None, "SPARK", f"Could not start single-instance service: {server.errorString()}"
            )
            return 1
    try:
        config_path = settings_path()
        settings, recovered = load_settings(config_path)
        save_settings(config_path, settings)
    except Exception as exc:
        QMessageBox.critical(None, "SPARK", f"SPARK could not initialize its local data: {exc}")
        return 1
    try:
        logger = configure_logging(log_path(), settings.log_level, secrets.get_key())
    except SecretError as exc:
        QMessageBox.critical(None, "SPARK", str(exc))
        return 1
    except OSError as exc:
        QMessageBox.critical(None, "SPARK", f"SPARK could not open its log file: {exc}")
        return 1

    window = None

    def quit_app():
        if logger:
            logger.info("SPARK shutting down")
        QThreadPool.globalInstance().waitForDone()
        app.quit()

    def exception_hook(exc_type, exc, tb):
        logger.error("Unhandled exception", exc_info=(exc_type, exc, tb))
        QMessageBox.critical(
            window, "SPARK error", "SPARK encountered an unexpected error. See the log for details."
        )

    sys.excepthook = exception_hook
    window = MainWindow(settings, logger, quit_app)
    app.tray_icon = Tray(window, window.open_settings, quit_app, app)

    def incoming():
        while server.hasPendingConnections():
            client = server.nextPendingConnection()
            client.waitForReadyRead(500)
            if client.readAll() == b"show":
                window.showNormal()
                window.raise_()
                window.activateWindow()
            client.disconnectFromServer()
            client.deleteLater()

    server.newConnection.connect(incoming)

    if recovered:
        QMessageBox.warning(
            None,
            "SPARK settings",
            "Your settings file was corrupted. SPARK backed it up as settings.json.bad "
            "and restored defaults.",
        )
    if settings.start_minimized and secrets.is_configured():
        window.hide()
    else:
        window.show()
    if not QSystemTrayIcon.isSystemTrayAvailable():
        logger.warning("System tray is unavailable; window close will exit SPARK")
        window.tray_available = False
    logger.info("SPARK %s started", __version__)
    return app.exec()
