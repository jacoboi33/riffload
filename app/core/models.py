from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TorrentResult:
    name: str
    info_hash: str
    magnet_uri: str
    size_bytes: int
    seeders: int
    leechers: int
    source: str          # "TPB" | "1337x"
    quality_hint: str    # "FLAC" | "MP3 320k" | "MP3" | "Unknown"

    def size_str(self) -> str:
        if self.size_bytes >= 1024 ** 3:
            return f"{self.size_bytes / 1024**3:.1f} GB"
        if self.size_bytes >= 1024 ** 2:
            return f"{self.size_bytes / 1024**2:.0f} MB"
        return f"{self.size_bytes / 1024:.0f} KB"


@dataclass
class AlbumResult:
    artist: str
    album: str
    year: int
    genre: str
    track_count: int
    artwork_url: str
    itunes_collection_id: int
    torrents: List[TorrentResult] = field(default_factory=list)
