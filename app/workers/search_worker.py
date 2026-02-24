from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from PyQt6.QtCore import QThread, pyqtSignal

from app.core import itunes_client
from app.core.models import AlbumResult, TorrentResult
from app.core.search_coordinator import distribute_torrents
from app.scrapers.piratebay_scraper import PirateBayScraper
from app.scrapers.leet337x_scraper import Leet337xScraper
from app.scrapers.nyaa_scraper import NyaaScraper
from app.scrapers.torrentgalaxy_scraper import TorrentGalaxyScraper
from app.scrapers.bitsearch_scraper import BitSearchScraper
from app.scrapers.kickass_scraper import KickassScraper

# Add or remove scrapers here — they all run in parallel
SCRAPERS = [
    PirateBayScraper(),
    Leet337xScraper(),
    NyaaScraper(),
    TorrentGalaxyScraper(),
    BitSearchScraper(),
    KickassScraper(),
]


class SearchWorker(QThread):
    itunes_ready = pyqtSignal(list)       # List[AlbumResult]
    torrents_updated = pyqtSignal(list)   # List[AlbumResult] (with torrents attached)
    unmatched_ready = pyqtSignal(list)    # List[TorrentResult]
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, query: str, parent=None):
        super().__init__(parent)
        self.query = query
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            # Phase 1: fast iTunes lookup
            albums: List[AlbumResult] = itunes_client.search(self.query)
            if self._cancelled:
                return
            self.itunes_ready.emit(albums)

            # Phase 2: all scrapers in parallel
            all_torrents: List[TorrentResult] = []
            with ThreadPoolExecutor(max_workers=len(SCRAPERS)) as ex:
                futures = {ex.submit(s.search, self.query): s for s in SCRAPERS}
                for future in as_completed(futures, timeout=45):
                    if self._cancelled:
                        return
                    try:
                        all_torrents.extend(future.result())
                    except Exception:
                        continue

            if self._cancelled:
                return

            # Phase 3: distribute torrents to albums
            unmatched = distribute_torrents(all_torrents, albums)

            self.torrents_updated.emit(albums)
            self.unmatched_ready.emit(unmatched)
            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
