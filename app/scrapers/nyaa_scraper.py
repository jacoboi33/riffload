"""Nyaa.si — best source for Japanese/Asian music. Uses public RSS API."""
import xml.etree.ElementTree as ET
import requests
from typing import List
from app.core.models import TorrentResult
from app.scrapers.base_scraper import BaseScraper

RSS_URL = "https://nyaa.si/"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
NYAA_NS = "https://nyaa.si/xmlns/nyaa"


class NyaaScraper(BaseScraper):
    def search(self, query: str) -> List[TorrentResult]:
        try:
            resp = requests.get(
                RSS_URL,
                params={"page": "rss", "q": query, "c": "2_0", "f": "0"},
                headers=HEADERS,
                timeout=15,
            )
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
        except Exception:
            return []

        results = []
        for item in root.findall(".//item"):
            try:
                title = item.findtext("title", "").strip()
                info_hash = item.findtext(f"{{{NYAA_NS}}}infoHash", "").lower()
                seeders = int(item.findtext(f"{{{NYAA_NS}}}seeders", "0"))
                leechers = int(item.findtext(f"{{{NYAA_NS}}}leechers", "0"))
                size_text = item.findtext(f"{{{NYAA_NS}}}size", "0")

                if not info_hash:
                    continue

                magnet = self._build_magnet(info_hash, title)
                results.append(TorrentResult(
                    name=title,
                    info_hash=info_hash,
                    magnet_uri=magnet,
                    size_bytes=self._parse_size(size_text),
                    seeders=seeders,
                    leechers=leechers,
                    source="Nyaa",
                    quality_hint=self._parse_quality(title),
                ))
            except Exception:
                continue

        results.sort(key=lambda r: r.seeders, reverse=True)
        return results[:10]
