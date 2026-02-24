import re
from abc import ABC, abstractmethod
from typing import List
from app.core.models import TorrentResult

OPEN_TRACKERS = [
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.demonii.com:1337",
    "udp://tracker.openbittorrent.com:6969/announce",
]


class BaseScraper(ABC):
    @abstractmethod
    def search(self, query: str) -> List[TorrentResult]:
        ...

    def _parse_quality(self, name: str) -> str:
        n = name.lower()
        if "flac" in n:
            return "FLAC"
        if "320" in n:
            return "MP3 320k"
        if "256" in n:
            return "MP3 256k"
        if "128" in n:
            return "MP3 128k"
        if "mp3" in n:
            return "MP3"
        return "Unknown"

    def _parse_size(self, size_str: str) -> int:
        m = re.match(r"([\d.]+)\s*(KB|MB|GB)", size_str.strip(), re.I)
        if not m:
            return 0
        val, unit = float(m.group(1)), m.group(2).upper()
        return int(val * {"KB": 1024, "MB": 1024 ** 2, "GB": 1024 ** 3}[unit])

    def _build_magnet(self, info_hash: str, name: str) -> str:
        from urllib.parse import quote
        trackers = "&".join(f"tr={t}" for t in OPEN_TRACKERS)
        return f"magnet:?xt=urn:btih:{info_hash}&dn={quote(name)}&{trackers}"
