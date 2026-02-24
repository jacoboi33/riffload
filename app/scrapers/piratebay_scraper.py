import requests
from typing import List
from app.core.models import TorrentResult
from app.scrapers.base_scraper import BaseScraper

API_URL = "https://apibay.org/q.php"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}


class PirateBayScraper(BaseScraper):
    def search(self, query: str) -> List[TorrentResult]:
        try:
            resp = requests.get(
                API_URL,
                params={"q": query, "cat": 100},
                headers=HEADERS,
                timeout=15,
            )
            resp.raise_for_status()
            items = resp.json()
        except Exception:
            return []

        results = []
        for item in items:
            if item.get("id") == "0" or item.get("info_hash") == "0":
                continue
            ih = item["info_hash"].lower()
            magnet = self._build_magnet(ih, item["name"])
            results.append(TorrentResult(
                name=item["name"],
                info_hash=ih,
                magnet_uri=magnet,
                size_bytes=int(item.get("size", 0)),
                seeders=int(item.get("seeders", 0)),
                leechers=int(item.get("leechers", 0)),
                source="TPB",
                quality_hint=self._parse_quality(item["name"]),
            ))

        results.sort(key=lambda r: r.seeders, reverse=True)
        return results[:10]
