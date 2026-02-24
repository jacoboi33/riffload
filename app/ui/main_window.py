from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap, QImage
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QStackedWidget, QFrame
)

from app.core.models import AlbumResult, TorrentResult
from app.core.torrent_manager import TorrentManager
from app.ui.album_grid import AlbumGrid
from app.ui.torrent_panel import TorrentPanel
from app.ui.download_bar import DownloadBar
from app.ui.styles import DARK_THEME
from app.workers.search_worker import SearchWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Riffload")
        self.resize(1100, 750)
        self.setMinimumSize(700, 500)
        self.setStyleSheet(DARK_THEME)

        self._search_worker: SearchWorker | None = None
        self._torrent_manager = TorrentManager(self)
        self._torrent_manager.download_progress.connect(self._on_progress)
        self._torrent_manager.download_finished.connect(self._on_finished)
        self._torrent_manager.download_error.connect(self._on_dl_error)
        self._torrent_manager.metadata_fetching.connect(self._on_metadata_fetching)

        self._current_album: AlbumResult | None = None
        self._art_cache: dict[str, QPixmap] = {}

        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Top bar
        topbar = QWidget()
        topbar.setFixedHeight(64)
        topbar.setStyleSheet("background-color: #0f172a; border-bottom: 1px solid #1f2937;")
        top_layout = QHBoxLayout(topbar)
        top_layout.setContentsMargins(24, 0, 24, 0)
        top_layout.setSpacing(12)

        logo = QLabel("🎵 Riffload")
        logo.setFont(QFont("Ubuntu", 16, QFont.Weight.Bold))
        logo.setStyleSheet("color: #6366f1;")
        top_layout.addWidget(logo)
        top_layout.addSpacing(24)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search artist or album…")
        self._search_input.returnPressed.connect(self._do_search)
        top_layout.addWidget(self._search_input, stretch=1)

        self._search_btn = QPushButton("Search")
        self._search_btn.setObjectName("search_btn")
        self._search_btn.clicked.connect(self._do_search)
        top_layout.addWidget(self._search_btn)

        root_layout.addWidget(topbar)

        # Main content area (grid + panel side by side)
        content = QWidget()
        self._content_layout = QHBoxLayout(content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)

        self._grid = AlbumGrid()
        self._grid.album_selected.connect(self._on_album_selected)
        self._content_layout.addWidget(self._grid, stretch=1)

        self._panel = TorrentPanel()
        self._panel.download_requested.connect(self._on_download_requested)
        self._panel.close_requested.connect(self._close_panel)
        self._panel.hide()
        self._content_layout.addWidget(self._panel)

        root_layout.addWidget(content, stretch=1)

        # Status bar
        self._status_label = QLabel("")
        self._status_label.setObjectName("status_label")
        self._status_label.setContentsMargins(24, 6, 24, 6)
        root_layout.addWidget(self._status_label)

        # Download bar
        self._dl_bar = DownloadBar()
        self._dl_bar.cancel_download.connect(self._torrent_manager.cancel_download)
        root_layout.addWidget(self._dl_bar)

    def _do_search(self):
        query = self._search_input.text().strip()
        if not query:
            return

        self._close_panel()

        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.cancel()
            self._search_worker.quit()

        self._search_btn.setEnabled(False)
        self._status_label.setText(f'Searching for "{query}"…')

        self._search_worker = SearchWorker(query)
        self._search_worker.itunes_ready.connect(self._on_itunes_ready)
        self._search_worker.torrents_updated.connect(self._on_torrents_updated)
        self._search_worker.finished.connect(self._on_search_finished)
        self._search_worker.error.connect(self._on_search_error)
        self._search_worker.start()

    def _on_itunes_ready(self, albums: list):
        self._grid.show_albums(albums)
        count = len(albums)
        self._status_label.setText(
            f"{count} album{'s' if count != 1 else ''} found — fetching torrents…"
        )

    def _on_torrents_updated(self, albums: list):
        self._grid.update_cards(albums)
        if self._current_album:
            for album in albums:
                if album.itunes_collection_id == self._current_album.itunes_collection_id:
                    self._panel.refresh_torrents(album)

    def _on_search_finished(self):
        self._search_btn.setEnabled(True)
        self._status_label.setText("Done. Click an album to see download options.")

    def _on_search_error(self, msg: str):
        self._search_btn.setEnabled(True)
        self._status_label.setText(f"Search error: {msg}")

    def _on_album_selected(self, album: AlbumResult):
        self._current_album = album
        art_px = self._get_art_pixmap(album)
        self._panel.show_album(album, art_px)
        self._panel.show()

    def _get_art_pixmap(self, album: AlbumResult) -> QPixmap | None:
        card = self._grid._cards.get(album.itunes_collection_id)
        if card:
            return card._art_label.pixmap()
        return None

    def _close_panel(self):
        self._panel.hide()
        self._current_album = None

    def _on_download_requested(self, torrent: TorrentResult):
        self._dl_bar.add_download(torrent)
        self._torrent_manager.add_download(torrent)

    def _on_progress(self, info_hash: str, pct: float, dl_rate: int, ul_rate: int):
        self._dl_bar.update_progress(info_hash, pct, dl_rate, ul_rate)

    def _on_finished(self, info_hash: str):
        self._dl_bar.set_complete(info_hash)

    def _on_dl_error(self, info_hash: str, msg: str):
        self._status_label.setText(f"Download error: {msg}")

    def _on_metadata_fetching(self, info_hash: str):
        self._dl_bar.set_fetching_metadata(info_hash)

    def closeEvent(self, event):
        self._torrent_manager.shutdown()
        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.cancel()
            self._search_worker.quit()
            self._search_worker.wait(3000)
        super().closeEvent(event)
