import keyboard
from PyQt6.QtCore import QObject, pyqtSignal, QMetaObject, Qt, pyqtSlot
import logging


class HotkeyManager(QObject):
    """Manages global hotkey registration.

    The keyboard library fires callbacks on a background thread.
    We marshal the signal emission back to the Qt main thread using
    QMetaObject.invokeMethod with Qt.ConnectionType.QueuedConnection,
    which is the safe cross-thread call mechanism in PyQt6.
    """

    trigger_signal = pyqtSignal()
    quit_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hotkey_combo = 'ctrl+shift+q'
        self.quit_combo = 'ctrl+shift+x'

    def start(self):
        try:
            keyboard.add_hotkey(self.hotkey_combo, self._on_hotkey)
            keyboard.add_hotkey(self.quit_combo, self._on_quit_hotkey)
            logging.info(f"Registered hotkeys: {self.hotkey_combo}, {self.quit_combo}")
        except Exception as e:
            logging.error(f"Failed to register hotkeys: {e}")

    def stop(self):
        try:
            keyboard.remove_hotkey(self.hotkey_combo)
            keyboard.remove_hotkey(self.quit_combo)
        except Exception as e:
            logging.error(f"Failed to remove hotkeys: {e}")

    def _on_hotkey(self):
        QMetaObject.invokeMethod(self, "_emit_trigger", Qt.ConnectionType.QueuedConnection)

    def _on_quit_hotkey(self):
        QMetaObject.invokeMethod(self, "_emit_quit", Qt.ConnectionType.QueuedConnection)

    @pyqtSlot()
    def _emit_trigger(self):
        self.trigger_signal.emit()

    @pyqtSlot()
    def _emit_quit(self):
        self.quit_signal.emit()
