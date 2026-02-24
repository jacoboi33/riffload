from typing import List, Dict

from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLayout, QLabel
)

from app.core.models import AlbumResult
from app.ui.album_card import AlbumCard
from app.workers.image_loader import ImageLoader


class FlowLayout(QLayout):
    """Left-to-right wrapping flow layout."""

    def __init__(self, parent=None, h_spacing=16, v_spacing=16):
        super().__init__(parent)
        self._items = []
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        return size

    def _do_layout(self, rect, test_only):
        x, y = rect.x(), rect.y()
        row_height = 0
        for item in self._items:
            iw = item.sizeHint().width() + self._h_spacing
            ih = item.sizeHint().height() + self._v_spacing
            if x + iw - self._h_spacing > rect.right() and row_height > 0:
                x = rect.x()
                y += row_height
                row_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x += iw
            row_height = max(row_height, ih)
        return y + row_height - rect.y()


class AlbumGrid(QWidget):
    album_selected = pyqtSignal(object)  # AlbumResult

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Empty state — shown before first search
        self._empty_label = QLabel("Search for an artist or album above")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: #4b5563; font-size: 16px;")
        layout.addWidget(self._empty_label)

        # Scroll area with persistent FlowLayout — never replaced
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { border: none; background: #111827; }")

        self._container = QWidget()
        self._container.setStyleSheet("background: #111827;")
        self._flow = FlowLayout(self._container, h_spacing=16, v_spacing=16)
        self._flow.setContentsMargins(24, 24, 24, 24)
        self._container.setLayout(self._flow)
        self._scroll.setWidget(self._container)

        layout.addWidget(self._scroll)
        self._scroll.hide()

        self._cards: Dict[int, AlbumCard] = {}
        self._loaders: List[ImageLoader] = []

    def show_albums(self, albums: List[AlbumResult]):
        self.clear()

        if not albums:
            self._empty_label.show()
            self._scroll.hide()
            return

        self._empty_label.hide()
        self._scroll.show()

        for album in albums:
            card = AlbumCard(album)
            card.clicked.connect(self.album_selected)
            self._flow.addWidget(card)
            self._cards[album.itunes_collection_id] = card

            if album.artwork_url:
                loader = ImageLoader(album.artwork_url)
                loader.image_loaded.connect(self._on_image_loaded)
                loader.start()
                self._loaders.append(loader)

        self._container.adjustSize()

    def clear(self):
        for loader in self._loaders:
            loader.quit()
        self._loaders.clear()
        self._cards.clear()

        while self._flow.count():
            item = self._flow.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def update_cards(self, albums: List[AlbumResult]):
        pass  # Cards hold a live reference to AlbumResult; torrents auto-update

    def _on_image_loaded(self, url: str, image: QImage):
        for card in self._cards.values():
            if card.album.artwork_url == url:
                card.set_artwork(image)
