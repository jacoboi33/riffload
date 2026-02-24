from typing import Dict
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame
)

from app.core.models import TorrentResult


class DownloadRow(QWidget):
    cancel_requested = pyqtSignal(str)  # info_hash

    def __init__(self, torrent: TorrentResult, parent=None):
        super().__init__(parent)
        self.info_hash = torrent.info_hash
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)
        layout.setSpacing(12)

        name_label = QLabel(f"{torrent.name[:50]}{'…' if len(torrent.name) > 50 else ''}")
        name_label.setFont(QFont("Ubuntu", 9))
        name_label.setStyleSheet("color: #d1d5db;")
        name_label.setMinimumWidth(200)
        layout.addWidget(name_label)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(8)
        layout.addWidget(self._progress, stretch=1)

        self._pct_label = QLabel("0%")
        self._pct_label.setFont(QFont("Ubuntu", 9))
        self._pct_label.setStyleSheet("color: #9ca3af;")
        self._pct_label.setFixedWidth(40)
        layout.addWidget(self._pct_label)

        self._speed_label = QLabel("")
        self._speed_label.setFont(QFont("Ubuntu", 9))
        self._speed_label.setStyleSheet("color: #6b7280;")
        self._speed_label.setFixedWidth(80)
        layout.addWidget(self._speed_label)

        cancel_btn = QPushButton("✕")
        cancel_btn.setFixedSize(24, 24)
        cancel_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #6b7280; border: none; font-size: 12px; }
            QPushButton:hover { color: #ef4444; }
        """)
        cancel_btn.clicked.connect(lambda: self.cancel_requested.emit(self.info_hash))
        layout.addWidget(cancel_btn)

    def update_progress(self, pct: float, dl_rate: int, ul_rate: int):
        self._progress.setValue(int(pct))
        self._pct_label.setText(f"{pct:.0f}%")
        if dl_rate > 0:
            rate_kb = dl_rate / 1024
            if rate_kb >= 1024:
                self._speed_label.setText(f"{rate_kb/1024:.1f} MB/s")
            else:
                self._speed_label.setText(f"{rate_kb:.0f} KB/s")

    def set_fetching_metadata(self):
        self._speed_label.setText("Fetching…")

    def set_complete(self):
        self._progress.setValue(100)
        self._pct_label.setText("Done")
        self._speed_label.setText("")


class DownloadBar(QFrame):
    cancel_download = pyqtSignal(str)  # info_hash

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            DownloadBar {
                background-color: #0f172a;
                border-top: 1px solid #374151;
            }
        """)
        self._rows: Dict[str, DownloadRow] = {}

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.hide()

    def add_download(self, torrent: TorrentResult):
        if torrent.info_hash in self._rows:
            return
        row = DownloadRow(torrent)
        row.cancel_requested.connect(self._on_cancel)
        self._rows[torrent.info_hash] = row
        self._layout.addWidget(row)
        self.show()
        self._update_height()

    def update_progress(self, info_hash: str, pct: float, dl_rate: int, ul_rate: int):
        if info_hash in self._rows:
            self._rows[info_hash].update_progress(pct, dl_rate, ul_rate)

    def set_fetching_metadata(self, info_hash: str):
        if info_hash in self._rows:
            self._rows[info_hash].set_fetching_metadata()

    def set_complete(self, info_hash: str):
        if info_hash in self._rows:
            self._rows[info_hash].set_complete()

    def _on_cancel(self, info_hash: str):
        self.cancel_download.emit(info_hash)
        row = self._rows.pop(info_hash, None)
        if row:
            row.deleteLater()
        if not self._rows:
            self.hide()
        self._update_height()

    def _update_height(self):
        self.setFixedHeight(len(self._rows) * 52)
