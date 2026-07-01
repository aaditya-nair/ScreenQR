import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
import logging


class QRDecoderThread(QThread):
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self, image: np.ndarray, parent=None):
        super().__init__(parent)
        self.image = image

    def run(self):
        try:
            if self.image is None or self.image.size == 0:
                self.finished_signal.emit([])
                return

            detector = cv2.QRCodeDetector()

            detection = detector.detectAndDecodeMulti(self.image)

            retval = detection[0]
            decoded_info = detection[1] if len(detection) > 1 else []

            results = []
            if retval and decoded_info:
                for info in decoded_info:
                    stripped = info.strip() if info else ""
                    if stripped:
                        results.append(stripped)

            if not results:
                try:
                    from pyzbar.pyzbar import decode
                    zbar_results = decode(self.image)
                    for barcode in zbar_results:
                        data = barcode.data.decode("utf-8")
                        if data:
                            results.append(data)
                except ImportError:
                    logging.warning("pyzbar not installed; cannot use fallback decoding.")
                except Exception as e:
                    logging.error(f"pyzbar fallback failed: {e}")

            logging.info(f"QR decode results: {results}")
            self.finished_signal.emit(results)

        except Exception as e:
            logging.error(f"Error decoding QR: {e}", exc_info=True)
            self.error_signal.emit(str(e))
