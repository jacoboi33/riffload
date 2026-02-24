import requests
from typing import List
from app.core.models import AlbumResult

SEARCH_URL = "https://itunes.apple.com/search"


def search(query: str, limit: int = 15) -> List[AlbumResult]:
    params = {
        "term": query,
        "entity": "album",
        "media": "music",
        "limit": limit,
        "country": "US",
    }
    resp = requests.get(SEARCH_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    results = []
    seen_ids = set()
    for item in data.get("results", []):
        cid = item.get("collectionId")
        if cid in seen_ids:
            continue
        seen_ids.add(cid)

        artwork = item.get("artworkUrl100", "")
        artwork = artwork.replace("100x100bb", "600x600bb")

        release = item.get("releaseDate", "1900-01-01")
        year = int(release[:4]) if release else 0

        results.append(AlbumResult(
            artist=item.get("artistName", "Unknown Artist"),
            album=item.get("collectionName", "Unknown Album"),
            year=year,
            genre=item.get("primaryGenreName", ""),
            track_count=item.get("trackCount", 0),
            artwork_url=artwork,
            itunes_collection_id=cid or 0,
        ))
    return results
