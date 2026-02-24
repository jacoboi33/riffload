"""BitSearch — indexes DHT network, good for finding obscure releases."""
import re
import requests
from bs4 import BeautifulSoup
from typing import List
from app.core.models import TorrentResult
from app.scrapers.base_scraper import BaseScraper

SEARCH_URL = "https://bitsearch.to/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
}
# cat=8 = Music


class BitSearchScraper(BaseScraper):
    def search(self, query: str) -> List[TorrentResult]:
        try:
            resp = requests.get(
                SEARCH_URL,
                params={"q": query, "cat": 8, "p": 1},
                headers=HEADERS,
                timeout=15,
            )
            if resp.status_code in (403, 503):
                return []
            soup = BeautifulSoup(resp.text, "lxml")
        except Exception:
            return []

        results = []
        for card in soup.select("li.search-result")[:10]:
            try:
                name_tag = card.select_one("h5.title a")
                if not name_tag:
                    continue
                name = name_tag.text.strip()

                magnet_tag = card.select_one('a[href^="magnet:"]')
                if not magnet_tag:
                    continue
                magnet = magnet_tag["href"]

                ih_match = re.search(r"btih:([a-fA-F0-9]{40})", magnet, re.I)
                ih = ih_match.group(1).lower() if ih_match else ""

                stats = card.select("div.stats span")
                seeders, leechers, size_bytes = 0, 0, 0
                for stat in stats:
                    text = stat.text.strip()
                    if "Seeder" in stat.get("title", ""):
                        seeders = int(re.sub(r"\D", "", text) or 0)
                    elif "Leecher" in stat.get("title", ""):
                        leechers = int(re.sub(r"\D", "", text) or 0)
                    elif re.match(r"[\d.]+ [KMGT]B", text):
                        size_bytes = self._parse_size(text)

                results.append(TorrentResult(
                    name=name,
                    info_hash=ih,
                    magnet_uri=magnet,
                    size_bytes=size_bytes,
                    seeders=seeders,
                    leechers=leechers,
                    source="BitSearch",
                    quality_hint=self._parse_quality(name),
                ))
            except Exception:
                continue

        results.sort(key=lambda r: r.seeders, reverse=True)
        return results
