from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QImage, QFont, QColor, QPainter
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel

from app.core.models import AlbumResult

CARD_W = 200
CARD_H = 270
ART_SIZE = 180


def _placeholder_pixmap(size: int) -> QPixmap:
    px = QPixmap(size, size)
    px.fill(QColor("#1f2937"))
    painter = QPainter(px)
    painter.setPen(QColor("#374151"))
    painter.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "♪")
    painter.end()
    return px


class AlbumCard(QFrame):
    clicked = pyqtSignal(object)  # emits AlbumResult

    def __init__(self, album: AlbumResult, parent=None):
        super().__init__(parent)
        self.album = album
        self.setFixedSize(CARD_W, CARD_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            AlbumCard {
                background-color: #1f2937;
                border-radius: 10px;
                border: 1px solid #374151;
            }
            AlbumCard:hover {
                border: 1px solid #6366f1;
                background-color: #252f3f;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        self._art_label = QLabel()
        self._art_label.setFixedSize(ART_SIZE, ART_SIZE)
        self._art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._art_label.setPixmap(_placeholder_pixmap(ART_SIZE))
        self._art_label.setStyleSheet("border-radius: 6px;")
        layout.addWidget(self._art_label, alignment=Qt.AlignmentFlag.AlignCenter)

        artist_label = QLabel(album.artist)
        artist_label.setFont(QFont("Ubuntu", 10, QFont.Weight.Bold))
        artist_label.setWordWrap(False)
        artist_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        artist_label.setStyleSheet("color: #f9fafb;")
        artist_label.setMaximumWidth(CARD_W - 20)
        artist_label.setText(self._elide(album.artist, 22))
        layout.addWidget(artist_label)

        album_label = QLabel(album.album)
        album_label.setFont(QFont("Ubuntu", 9))
        album_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        album_label.setStyleSheet("color: #d1d5db;")
        album_label.setText(self._elide(album.album, 24))
        layout.addWidget(album_label)

        year_label = QLabel(str(album.year) if album.year else "")
        year_label.setFont(QFont("Ubuntu", 8))
        year_label.setStyleSheet("color: #6b7280;")
        layout.addWidget(year_label)

        layout.addStretch()

    def set_artwork(self, image: QImage):
        px = QPixmap.fromImage(image)
        px = px.scaled(
            ART_SIZE, ART_SIZE,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        # Crop to square
        x = (px.width() - ART_SIZE) // 2
        y = (px.height() - ART_SIZE) // 2
        px = px.copy(x, y, ART_SIZE, ART_SIZE)
        self._art_label.setPixmap(px)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.album)
        super().mousePressEvent(event)

    @staticmethod
    def _elide(text: str, max_chars: int) -> str:
        return text if len(text) <= max_chars else text[:max_chars - 1] + "…"
