from unittest.mock import Mock

from PySide6.QtCore import Qt
from PySide6.QtNetwork import QLocalServer
from PySide6.QtWidgets import QApplication, QDialog

from spark.core.settings import Settings
from spark.ui.main_window import MainWindow
from spark.ui.settings_dialog import SettingsDialog
from spark.ui.tray import Tray


def test_second_instance_detected(qtbot, monkeypatch):
    from spark.app import activate_existing

    name = "spark-test-instance"
    server = QLocalServer()
    assert server.listen(name)
    assert activate_existing(name)
    assert server.waitForNewConnection(500)
    client = server.nextPendingConnection()
    assert client is not None
    client.disconnectFromServer()
    server.close()
    QLocalServer.removeServer(name)


def test_window_send_and_help(qtbot, tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr("spark.ui.main_window.is_configured", lambda: True)
    window = MainWindow(Settings("", "INFO", False), None, lambda: None)
    qtbot.addWidget(window)
    window.show()
    window.input.setPlainText("/help")
    window.send_message()
    assert "/help" in window.transcript.toPlainText()
    assert "Commands:" in window.transcript.toPlainText()


def test_window_shell_reply(qtbot, tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr("spark.ui.main_window.is_configured", lambda: True)
    window = MainWindow(Settings("", "INFO", False), None, lambda: None)
    qtbot.addWidget(window)
    window.input.setPlainText("hello")
    window.send_message()
    assert "AI chat arrives in Phase 2" in window.transcript.toPlainText()


def test_enter_sends_and_shift_enter_adds_newline(qtbot, tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr("spark.ui.main_window.is_configured", lambda: True)
    window = MainWindow(Settings("", "INFO", False), None, lambda: None)
    qtbot.addWidget(window)
    window.input.setFocus()
    qtbot.keyClicks(window.input, "first")
    qtbot.keyPress(window.input, Qt.Key.Key_Return, Qt.KeyboardModifier.ShiftModifier)
    qtbot.keyClicks(window.input, "second")
    assert "first" in window.input.toPlainText()
    assert "second" in window.input.toPlainText()
    qtbot.keyPress(window.input, Qt.Key.Key_Return)
    assert window.input.toPlainText() == ""
    assert "first" in window.transcript.toPlainText()
    assert "second" in window.transcript.toPlainText()


def test_settings_dialog_key_is_masked(qtbot, monkeypatch, tmp_path):
    monkeypatch.setattr("spark.ui.settings_dialog.secrets.masked_key", lambda: "••••6789")
    dialog = SettingsDialog(Settings("", "INFO", False), tmp_path / "settings.json", None)
    qtbot.addWidget(dialog)
    assert dialog.key.echoMode() == dialog.key.EchoMode.Password
    assert dialog.key.text() == ""
    assert dialog.key.placeholderText() == "••••6789"


def test_settings_dialog_opens(qtbot, tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr("spark.ui.main_window.is_configured", lambda: True)
    monkeypatch.setattr("spark.ui.main_window.configure_logging", lambda *args: None)
    monkeypatch.setattr("spark.ui.main_window.get_key", lambda: None)
    window = MainWindow(Settings("", "INFO", False), None, lambda: None)
    qtbot.addWidget(window)
    opened = []
    was_visible = []
    from spark.ui.main_window import SettingsDialog as OriginalDialog

    class TrackingDialog(OriginalDialog):
        def exec(self):
            opened.append(self)
            self.show()
            QApplication.processEvents()
            was_visible.append(self.isVisible())
            self.close()
            return QDialog.DialogCode.Accepted if was_visible[-1] else QDialog.DialogCode.Rejected

    monkeypatch.setattr("spark.ui.main_window.SettingsDialog", TrackingDialog)
    window.open_settings()
    assert len(opened) == 1
    assert was_visible == [True]


def test_tray_actions_show_settings_and_quit(qtbot):
    window = Mock()
    open_settings = Mock()
    quit_app = Mock()
    tray = Tray(window, open_settings, quit_app, QApplication.instance())
    qtbot.addWidget(tray.contextMenu())

    actions = {action.text(): action for action in tray.contextMenu().actions() if action.text()}
    actions["Show"].trigger()
    actions["Settings"].trigger()
    actions["Quit"].trigger()

    window.showNormal.assert_called_once_with()
    window.raise_.assert_called_once_with()
    window.activateWindow.assert_called_once_with()
    open_settings.assert_called_once_with()
    quit_app.assert_called_once_with()
    tray.hide()
    tray.deleteLater()


def test_close_hides_when_key_configured(qtbot, monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr("spark.ui.main_window.is_configured", lambda: True)
    quit_app = Mock()
    window = MainWindow(Settings("", "INFO", False), None, quit_app)
    qtbot.addWidget(window)
    window.show()
    window.close()
    assert not window.isVisible()
    quit_app.assert_not_called()


def test_close_exits_when_no_key(qtbot, monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr("spark.ui.main_window.is_configured", lambda: False)
    quit_app = Mock()
    window = MainWindow(Settings("", "INFO", False), None, quit_app)
    qtbot.addWidget(window)
    window.show()
    window.close()
    quit_app.assert_called_once()
