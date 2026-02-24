from pathlib import Path
from typing import Dict

try:
    import libtorrent as lt
    LIBTORRENT_AVAILABLE = True
except ImportError:
    LIBTORRENT_AVAILABLE = False

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from app.core.models import TorrentResult


class TorrentManager(QObject):
    download_progress = pyqtSignal(str, float, int, int)  # hash, %, dl_rate, ul_rate
    download_finished = pyqtSignal(str)                   # hash
    download_error = pyqtSignal(str, str)                 # hash, message
    metadata_fetching = pyqtSignal(str)                   # hash (magnet resolving)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.handles: Dict[str, object] = {}
        self.save_path = str(Path.home() / "Music")
        Path(self.save_path).mkdir(exist_ok=True)

        if LIBTORRENT_AVAILABLE:
            self.session = lt.session({
                "listen_interfaces": "0.0.0.0:6881",
                "alert_mask": (
                    lt.alert.category_t.progress_notification |
                    lt.alert.category_t.error_notification |
                    lt.alert.category_t.status_notification
                ),
            })
        else:
            self.session = None

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(1000)
        self._poll_timer.timeout.connect(self._poll_alerts)
        self._poll_timer.start()

    def add_download(self, torrent: TorrentResult) -> bool:
        if not LIBTORRENT_AVAILABLE or self.session is None:
            self.download_error.emit(torrent.info_hash, "libtorrent not installed")
            return False
        if torrent.info_hash in self.handles:
            return False
        try:
            atp = lt.parse_magnet_uri(torrent.magnet_uri)
            atp.save_path = self.save_path
            handle = self.session.add_torrent(atp)
            self.handles[torrent.info_hash] = handle
            return True
        except Exception as e:
            self.download_error.emit(torrent.info_hash, str(e))
            return False

    def cancel_download(self, info_hash: str) -> None:
        handle = self.handles.pop(info_hash, None)
        if handle and LIBTORRENT_AVAILABLE and handle.is_valid():
            self.session.remove_torrent(handle)

    def _poll_alerts(self) -> None:
        if not LIBTORRENT_AVAILABLE or self.session is None:
            return
        for alert in self.session.pop_alerts():
            if isinstance(alert, lt.torrent_finished_alert):
                ih = str(alert.handle.info_hash())
                self.handles.pop(ih, None)
                self.download_finished.emit(ih)
            elif isinstance(alert, lt.torrent_error_alert):
                ih = str(alert.handle.info_hash())
                self.download_error.emit(ih, alert.message())

        for ih, handle in list(self.handles.items()):
            if not handle.is_valid():
                continue
            s = handle.status()
            if s.state == lt.torrent_status.downloading_metadata:
                self.metadata_fetching.emit(ih)
            elif s.state in (lt.torrent_status.downloading,
                             lt.torrent_status.finished,
                             lt.torrent_status.seeding):
                self.download_progress.emit(
                    ih,
                    s.progress * 100.0,
                    s.download_payload_rate,
                    s.upload_payload_rate,
                )

    def shutdown(self) -> None:
        self._poll_timer.stop()
        if LIBTORRENT_AVAILABLE and self.session:
            for handle in self.handles.values():
                if handle.is_valid():
                    self.session.remove_torrent(handle)
