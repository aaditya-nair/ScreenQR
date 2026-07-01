import mss
import mss.tools
import numpy as np
import cv2
import logging


def capture_screen_region(x: int, y: int, width: int, height: int) -> np.ndarray:
    """
    Captures a specific region of the screen and returns it as an
    OpenCV-compatible BGR numpy array (3 channels).
    """
    try:
        with mss.mss() as sct:
            monitor = {"top": y, "left": x, "width": width, "height": height}
            sct_img = sct.grab(monitor)

            img_bgra = np.array(sct_img, dtype=np.uint8)
            img_bgr = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)

            return img_bgr
    except Exception as e:
        logging.error(f"Error capturing screen region: {e}")
        return None
