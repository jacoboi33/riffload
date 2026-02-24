"""KickassTorrents (katcr.to) — one of the oldest indexes, still active."""
import re
import requests
from bs4 import BeautifulSoup
from typing import List
from app.core.models import TorrentResult
from app.scrapers.base_scraper import BaseScraper

BASE_URL = "https://katcr.to"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


class KickassScraper(BaseScraper):
    def search(self, query: str) -> List[TorrentResult]:
        try:
            from urllib.parse import quote
            url = f"{BASE_URL}/usearch/{quote(query)} category:music/"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code in (403, 503, 404):
                return []
            soup = BeautifulSoup(resp.text, "lxml")
        except Exception:
            return []

        results = []
        for row in soup.select("tr.even, tr.odd")[:10]:
            try:
                name_tag = row.select_one("a.cellMainLink")
                if not name_tag:
                    continue
                name = name_tag.text.strip()

                magnet_tag = row.select_one('a[href^="magnet:"]')
                if not magnet_tag:
                    continue
                magnet = magnet_tag["href"]

                ih_match = re.search(r"btih:([a-fA-F0-9]{40})", magnet, re.I)
                ih = ih_match.group(1).lower() if ih_match else ""

                cells = row.select("td")
                size_bytes = self._parse_size(cells[1].text.strip()) if len(cells) > 1 else 0
                seeders = int(re.sub(r"\D", "", cells[4].text) or 0) if len(cells) > 4 else 0
                leechers = int(re.sub(r"\D", "", cells[5].text) or 0) if len(cells) > 5 else 0

                results.append(TorrentResult(
                    name=name,
                    info_hash=ih,
                    magnet_uri=magnet,
                    size_bytes=size_bytes,
                    seeders=seeders,
                    leechers=leechers,
                    source="KAT",
                    quality_hint=self._parse_quality(name),
                ))
            except Exception:
                continue

        results.sort(key=lambda r: r.seeders, reverse=True)
        return results
