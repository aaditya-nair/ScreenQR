import sys
import logging
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import pyqtSlot, Qt, QObject

from overlay import OverlayWindow
from capture import capture_screen_region
from decoder import QRDecoderThread
from popup import PopupDialog, HistoryDialog
from hotkeys import HotkeyManager
from utils import load_config, save_config

class ScreenQRApp(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.config = load_config()

        self.overlay = None
        self.decoder_thread = None

        self.setup_tray()

        self.hotkey_manager = HotkeyManager()
        self.hotkey_manager.trigger_signal.connect(self.show_overlay)
        self.hotkey_manager.quit_signal.connect(self.quit_app)
        self.hotkey_manager.start()

        self.tray.showMessage("ScreenQR Started",
                              f"Scan: {self.hotkey_manager.hotkey_combo} | Quit: {self.hotkey_manager.quit_combo}",
                              QSystemTrayIcon.MessageIcon.Information,
                              3000)

    def create_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)

        from PyQt6.QtGui import QPainter, QColor
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(0, 120, 215))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(4, 4, 24, 24, 4, 4)
        painter.drawRoundedRect(36, 4, 24, 24, 4, 4)
        painter.drawRoundedRect(4, 36, 24, 24, 4, 4)
        painter.drawRoundedRect(40, 40, 16, 16, 2, 2)

        painter.end()
        return QIcon(pixmap)

    def setup_tray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.create_icon())

        self.menu = QMenu()

        scan_action = self.menu.addAction("Scan Now")
        scan_action.triggered.connect(self.show_overlay)

        history_action = self.menu.addAction("View History")
        history_action.triggered.connect(self.show_history)

        self.menu.addSeparator()

        auto_copy_action = self.menu.addAction("Auto-Copy (Single QR)")
        auto_copy_action.setCheckable(True)
        auto_copy_action.setChecked(self.config.get("auto_copy", True))
        auto_copy_action.triggered.connect(self.toggle_auto_copy)

        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app)

        self.tray.setContextMenu(self.menu)
        self.tray.show()

    def toggle_auto_copy(self, checked):
        self.config["auto_copy"] = checked
        save_config(self.config)

    @pyqtSlot()
    def show_history(self):
        self.history_dialog = HistoryDialog(self.config)
        self.history_dialog.show()

    @pyqtSlot()
    def show_overlay(self):
        if self.overlay is not None:
            return

        self.overlay = OverlayWindow()
        self.overlay.region_selected.connect(self.process_selection)
        self.overlay.cancelled.connect(self.cleanup_overlay)
        self.overlay.show()

    @pyqtSlot(int, int, int, int)
    def process_selection(self, x, y, width, height):
        self.cleanup_overlay()

        image = capture_screen_region(x, y, width, height)
        if image is None:
            self.show_notification("Capture failed.")
            return

        self.decoder_thread = QRDecoderThread(image)
        self.decoder_thread.finished_signal.connect(self.on_decode_finished)
        self.decoder_thread.error_signal.connect(self.on_decode_error)
        self.decoder_thread.start()

    @pyqtSlot()
    def cleanup_overlay(self):
        if self.overlay:
            self.overlay.deleteLater()
            self.overlay = None

    @pyqtSlot(list)
    def on_decode_finished(self, results):
        if not results:
            self.show_notification("No QR code detected.")
            return

        self.popup = PopupDialog(results, self.config)
        self.popup.show()

        self.popup.finished.connect(lambda: save_config(self.config))

    @pyqtSlot(str)
    def on_decode_error(self, error_msg):
        self.show_notification(f"Error decoding: {error_msg}")

    def show_notification(self, message):
        self.tray.showMessage("ScreenQR", message, QSystemTrayIcon.MessageIcon.Warning, 2000)

    def quit_app(self):
        self.hotkey_manager.stop()
        save_config(self.config)
        self.app.quit()

    def run(self):
        return self.app.exec()


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        app = ScreenQRApp()
        sys.exit(app.run())
    except Exception as e:
        logging.critical(f"Critical error: {e}")
