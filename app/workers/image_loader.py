import requests
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage


class ImageLoader(QThread):
    # Emits (artwork_url, QImage) — convert to QPixmap in main thread
    image_loaded = pyqtSignal(str, QImage)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        if not self.url:
            return
        try:
            resp = requests.get(self.url, timeout=10)
            resp.raise_for_status()
            image = QImage()
            image.loadFromData(resp.content)
            if not image.isNull():
                self.image_loaded.emit(self.url, image)
        except Exception:
            pass
