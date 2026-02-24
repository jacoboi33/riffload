from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QFrame
)

from app.core.models import AlbumResult, TorrentResult


class TorrentPanel(QWidget):
    download_requested = pyqtSignal(object)  # TorrentResult
    close_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(420)
        self.setMaximumWidth(480)
        self.setStyleSheet("""
            TorrentPanel {
                background-color: #161d2b;
                border-left: 1px solid #374151;
            }
        """)

        self._album: AlbumResult | None = None
        self._selected_torrent: TorrentResult | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        self._back_btn = QPushButton("← Back")
        self._back_btn.setObjectName("back_btn")
        self._back_btn.clicked.connect(self.close_requested)
        header.addWidget(self._back_btn)
        header.addStretch()
        layout.addLayout(header)

        # Album info
        info_layout = QHBoxLayout()
        self._art_label = QLabel()
        self._art_label.setFixedSize(80, 80)
        self._art_label.setStyleSheet("background-color: #1f2937; border-radius: 6px;")
        self._art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self._art_label)

        meta_layout = QVBoxLayout()
        meta_layout.setSpacing(2)
        self._album_label = QLabel()
        self._album_label.setFont(QFont("Ubuntu", 12, QFont.Weight.Bold))
        self._album_label.setWordWrap(True)
        self._album_label.setStyleSheet("color: #f9fafb;")
        meta_layout.addWidget(self._album_label)

        self._artist_label = QLabel()
        self._artist_label.setFont(QFont("Ubuntu", 10))
        self._artist_label.setStyleSheet("color: #9ca3af;")
        meta_layout.addWidget(self._artist_label)

        self._year_label = QLabel()
        self._year_label.setFont(QFont("Ubuntu", 9))
        self._year_label.setStyleSheet("color: #6b7280;")
        meta_layout.addWidget(self._year_label)
        meta_layout.addStretch()

        info_layout.addLayout(meta_layout)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #374151;")
        layout.addWidget(line)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Quality", "Size", "Seeds", "Source"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self._table)

        self._status_label = QLabel()
        self._status_label.setObjectName("status_label")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)

        self._dl_btn = QPushButton("Download")
        self._dl_btn.setObjectName("download_btn")
        self._dl_btn.setEnabled(False)
        self._dl_btn.clicked.connect(self._on_download)
        layout.addWidget(self._dl_btn)

    def show_album(self, album: AlbumResult, art_pixmap=None):
        self._album = album
        self._selected_torrent = None
        self._dl_btn.setEnabled(False)

        self._album_label.setText(album.album)
        self._artist_label.setText(album.artist)
        self._year_label.setText(str(album.year) if album.year else "")

        if art_pixmap:
            scaled = art_pixmap.scaled(
                80, 80,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._art_label.setPixmap(scaled)

        self._populate_table(album.torrents)

    def refresh_torrents(self, album: AlbumResult):
        if self._album and self._album.itunes_collection_id == album.itunes_collection_id:
            self._populate_table(album.torrents)

    def _populate_table(self, torrents):
        self._table.setRowCount(0)
        if not torrents:
            self._status_label.setText("No torrents found yet…")
            return
        self._status_label.setText("")
        for torrent in torrents:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(torrent.quality_hint))
            self._table.setItem(row, 1, QTableWidgetItem(torrent.size_str()))
            seeds_item = QTableWidgetItem(str(torrent.seeders))
            seeds_item.setForeground(
                Qt.GlobalColor.green if torrent.seeders > 50 else Qt.GlobalColor.yellow
            )
            self._table.setItem(row, 2, seeds_item)
            self._table.setItem(row, 3, QTableWidgetItem(torrent.source))
            # Store torrent ref in first cell
            self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, torrent)

    def _on_selection_changed(self):
        rows = self._table.selectedItems()
        if rows:
            torrent = self._table.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)
            self._selected_torrent = torrent
            self._dl_btn.setEnabled(True)
        else:
            self._selected_torrent = None
            self._dl_btn.setEnabled(False)

    def _on_download(self):
        if self._selected_torrent:
            self.download_requested.emit(self._selected_torrent)
