import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from typing import List, Optional, Tuple
from app.core.models import TorrentResult
from app.scrapers.base_scraper import BaseScraper

BASE_URL = "https://www.1337x.to"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class Leet337xScraper(BaseScraper):
    def search(self, query: str) -> List[TorrentResult]:
        try:
            from urllib.parse import quote
            url = f"{BASE_URL}/search/{quote(query)}/1/"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code in (403, 503):
                return []
            soup = BeautifulSoup(resp.text, "lxml")
        except Exception:
            return []

        name_tags = soup.select('a[href*="/torrent/"]')
        seeder_cells = [td.text.strip() for td in soup.select("td.coll-2")]
        leecher_cells = [td.text.strip() for td in soup.select("td.coll-3")]
        size_cells = [td.text.strip() for td in soup.select("td.coll-4")]

        entries = []
        for i, tag in enumerate(name_tags[:8]):
            detail_url = BASE_URL + tag["href"]
            name = tag.text.strip()
            seeders = int(seeder_cells[i]) if i < len(seeder_cells) else 0
            leechers = int(leecher_cells[i]) if i < len(leecher_cells) else 0
            size_str = size_cells[i] if i < len(size_cells) else "0"
            entries.append((detail_url, name, seeders, leechers, size_str))

        results = []
        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = {
                ex.submit(self._get_magnet, url): (url, name, s, l, sz)
                for url, name, s, l, sz in entries
            }
            for future in as_completed(futures, timeout=20):
                url, name, seeders, leechers, size_str = futures[future]
                try:
                    magnet, ih = future.result()
                    if not magnet:
                        continue
                    results.append(TorrentResult(
                        name=name,
                        info_hash=ih,
                        magnet_uri=magnet,
                        size_bytes=self._parse_size(size_str),
                        seeders=seeders,
                        leechers=leechers,
                        source="1337x",
                        quality_hint=self._parse_quality(name),
                    ))
                except Exception:
                    continue

        results.sort(key=lambda r: r.seeders, reverse=True)
        return results

    def _get_magnet(self, detail_url: str) -> Tuple[Optional[str], str]:
        time.sleep(0.3)
        try:
            resp = requests.get(detail_url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "lxml")
            magnet_tag = soup.select_one('a[href^="magnet"]')
            if not magnet_tag:
                return None, ""
            magnet = magnet_tag["href"]
            ih_box = soup.find("div", {"class": "infohash-box"})
            ih = ih_box.find("span").text.strip().lower() if ih_box else ""
            return magnet, ih
        except Exception:
            return None, ""
