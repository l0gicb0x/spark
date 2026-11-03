"""System tray controls with an original icon drawn at runtime."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


def make_icon() -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor("#17243a"))
    painter = QPainter(pixmap)
    painter.setPen(QColor("#79e0bd"))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "S")
    painter.end()
    return QIcon(pixmap)


class Tray(QSystemTrayIcon):
    def __init__(self, window, open_settings, quit_app, parent=None):
        super().__init__(make_icon(), parent)
        self.setToolTip("SPARK")

        def show_window():
            window.showNormal()
            window.raise_()
            window.activateWindow()

        menu = QMenu()
        show = QAction("Show", menu)
        show.triggered.connect(show_window)
        settings = QAction("Settings", menu)
        settings.triggered.connect(open_settings)
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(quit_app)
        menu.addAction(show)
        menu.addAction(settings)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.setContextMenu(menu)

        def tray_activated(reason):
            if reason in (
                QSystemTrayIcon.ActivationReason.Trigger,
                QSystemTrayIcon.ActivationReason.DoubleClick,
            ):
                show_window()

        self.activated.connect(tray_activated)
        self.show()
