"""TorrentGalaxy — strong general library, music category."""
import re
import requests
from bs4 import BeautifulSoup
from typing import List
from app.core.models import TorrentResult
from app.scrapers.base_scraper import BaseScraper

BASE_URL = "https://torrentgalaxy.to"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
# cat=10 = Music
SEARCH_URL = f"{BASE_URL}/torrents.php"


class TorrentGalaxyScraper(BaseScraper):
    def search(self, query: str) -> List[TorrentResult]:
        try:
            resp = requests.get(
                SEARCH_URL,
                params={"search": query, "cat": 10, "lang": 0, "nox": 1, "sort": "seeders", "order": "desc"},
                headers=HEADERS,
                timeout=15,
            )
            if resp.status_code in (403, 503):
                return []
            soup = BeautifulSoup(resp.text, "lxml")
        except Exception:
            return []

        results = []
        # Each result row has class "tgxtablerow"
        for row in soup.select("div.tgxtablerow")[:10]:
            try:
                name_tag = row.select_one("a.txlight")
                if not name_tag:
                    continue
                name = name_tag.text.strip()

                magnet_tag = row.select_one('a[href^="magnet:"]')
                if not magnet_tag:
                    continue
                magnet = magnet_tag["href"]

                ih_match = re.search(r"btih:([a-fA-F0-9]{40})", magnet)
                ih = ih_match.group(1).lower() if ih_match else ""

                # Seeders/leechers in <span> with class "badge"
                badges = row.select("span.badge-success, span.badge-danger")
                seeders = int(badges[0].text.strip()) if len(badges) > 0 else 0
                leechers = int(badges[1].text.strip()) if len(badges) > 1 else 0

                # Size
                size_tag = row.select_one("span.badge-secondary")
                size_bytes = self._parse_size(size_tag.text.strip()) if size_tag else 0

                results.append(TorrentResult(
                    name=name,
                    info_hash=ih,
                    magnet_uri=magnet,
                    size_bytes=size_bytes,
                    seeders=seeders,
                    leechers=leechers,
                    source="TGx",
                    quality_hint=self._parse_quality(name),
                ))
            except Exception:
                continue

        results.sort(key=lambda r: r.seeders, reverse=True)
        return results
