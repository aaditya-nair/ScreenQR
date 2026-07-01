from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

class OverlayWindow(QWidget):
    # Emits (x, y, width, height) of the selected region
    region_selected = pyqtSignal(int, int, int, int)
    cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Make the window frameless, always on top, and a tool window to hide from taskbar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        # Transparent background for the widget itself
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Determine the total geometry of all screens
        screens = QApplication.screens()
        self.total_rect = QRect()
        for screen in screens:
            self.total_rect = self.total_rect.united(screen.geometry())
            
        self.setGeometry(self.total_rect)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Dim the whole screen
        overlay_color = QColor(0, 0, 0, 100) # Semi-transparent black
        painter.fillRect(self.rect(), overlay_color)

        if self.is_drawing and not self.start_point.isNull() and not self.end_point.isNull():
            # Calculate the rectangle relative to the widget's coordinates
            rect = QRect(self.start_point, self.end_point).normalized()
            
            # Draw the clear selection area
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, Qt.GlobalColor.transparent)
            
            # Draw the border
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 120, 215, 255), 2)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.end_point = self.start_point
            self.is_drawing = True
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self.cancelled.emit()
            self.close()

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.end_point = event.pos()
            self.is_drawing = False
            self.update()
            
            rect = QRect(self.start_point, self.end_point).normalized()
            
            if rect.width() > 10 and rect.height() > 10:
                # Convert coordinates back to global screen coordinates
                global_rect = rect.translated(self.geometry().topLeft())
                
                # High-DPI displays (like Windows laptops at 125%/150% scaling) cause a mismatch
                # between PyQt's logical coordinates and mss's physical pixel coordinates.
                # We need to scale the coordinates by the devicePixelRatio to capture the correct region.
                screen = QApplication.screenAt(global_rect.center())
                ratio = screen.devicePixelRatio() if screen else self.devicePixelRatioF()
                
                px = int(global_rect.x() * ratio)
                py = int(global_rect.y() * ratio)
                pw = int(global_rect.width() * ratio)
                ph = int(global_rect.height() * ratio)
                
                self.region_selected.emit(px, py, pw, ph)
            else:
                self.cancelled.emit()
                
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            self.close()
