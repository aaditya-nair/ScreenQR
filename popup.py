import webbrowser
import pyperclip
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QListWidgetItem, QWidget, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from utils import is_valid_url, add_to_history

class ResultItemWidget(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        self.text_label = QLineEdit(self.text)
        self.text_label.setReadOnly(True)
        self.text_label.setStyleSheet("border: none; background: transparent; color: #E0E0E0;")

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self.copy_text)

        layout.addWidget(self.text_label, stretch=1)
        layout.addWidget(self.copy_btn)

        if is_valid_url(self.text):
            self.open_btn = QPushButton("Open")
            self.open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.open_btn.clicked.connect(self.open_url)
            layout.addWidget(self.open_btn)

        self.setLayout(layout)

    def copy_text(self):
        pyperclip.copy(self.text)
        self.copy_btn.setText("Copied!")

    def open_url(self):
        webbrowser.open(self.text)

class PopupDialog(QDialog):
    def __init__(self, results, config):
        super().__init__()
        self.results = results
        self.config = config

        self.setWindowTitle("ScreenQR Results")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog)

        if self.config.get("window_x") is not None and self.config.get("window_y") is not None:
            self.move(self.config["window_x"], self.config["window_y"])

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("QR Codes Detected" if len(self.results) > 1 else "QR Code Detected")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        if len(self.results) == 1:
            text = self.results[0]
            add_to_history(text)
            if self.config.get("auto_copy", True):
                pyperclip.copy(text)

            item = ResultItemWidget(text)
            layout.addWidget(item)
        else:
            list_widget = QListWidget()
            for text in self.results:
                add_to_history(text)
                item_widget = ResultItemWidget(text)
                list_item = QListWidgetItem(list_widget)
                list_item.setSizeHint(item_widget.sizeHint())
                list_widget.addItem(list_item)
                list_widget.setItemWidget(list_item, item_widget)
            layout.addWidget(list_widget)

        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.resize(400, 150 if len(self.results) == 1 else 300)

    def apply_styles(self):
        if self.config.get("dark_mode", True):
            self.setStyleSheet("""
                QDialog {
                    background-color:
                    color:
                    border-radius: 10px;
                }
                QLabel {
                    color:
                }
                QPushButton {
                    background-color:
                    color:
                    border: 1px solid
                    border-radius: 5px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color:
                }
                QListWidget {
                    background-color:
                    border: 1px solid
                    border-radius: 5px;
                }
                QLineEdit {
                    background-color:
                    color:
                    border: 1px solid
                    border-radius: 3px;
                    padding: 3px;
                }
            """)

    def closeEvent(self, event):
        self.config["window_x"] = self.x()
        self.config["window_y"] = self.y()
        event.accept()

class HistoryDialog(QDialog):
    def __init__(self, config):
        super().__init__()
        self.config = config

        self.setWindowTitle("ScreenQR Scan History")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog)

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        from utils import load_history
        layout = QVBoxLayout()

        title = QLabel("Scan History (Last 20)")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        history = load_history()

        if not history:
            no_history = QLabel("No scans recorded yet.")
            layout.addWidget(no_history)
        else:
            from PyQt6.QtWidgets import QListWidget, QListWidgetItem
            list_widget = QListWidget()
            for text in history:
                item_widget = ResultItemWidget(text)
                list_item = QListWidgetItem(list_widget)
                list_item.setSizeHint(item_widget.sizeHint())
                list_widget.addItem(list_item)
                list_widget.setItemWidget(list_item, item_widget)
            layout.addWidget(list_widget)

        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.resize(450, 350)

    def apply_styles(self):
        if self.config.get("dark_mode", True):
            self.setStyleSheet("""
                QDialog {
                    background-color:
                    color:
                    border-radius: 10px;
                }
                QLabel {
                    color:
                }
                QPushButton {
                    background-color:
                    color:
                    border: 1px solid
                    border-radius: 5px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color:
                }
                QListWidget {
                    background-color:
                    border: 1px solid
                    border-radius: 5px;
                }
                QLineEdit {
                    background-color:
                    color:
                    border: 1px solid
                    border-radius: 3px;
                    padding: 3px;
                }
            """)
