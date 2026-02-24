from difflib import SequenceMatcher
from typing import List, Optional
from app.core.models import AlbumResult, TorrentResult


def match_torrent_to_album(
    torrent: TorrentResult, albums: List[AlbumResult]
) -> Optional[AlbumResult]:
    torrent_lower = torrent.name.lower()
    best_score, best_album = 0, None

    for album in albums:
        artist_l = album.artist.lower()
        album_l = album.album.lower()

        if artist_l in torrent_lower and album_l in torrent_lower:
            score = 100
        elif artist_l in torrent_lower:
            score = 60
        elif album_l in torrent_lower:
            score = 40
        else:
            ratio = SequenceMatcher(
                None, torrent_lower, f"{artist_l} {album_l}"
            ).ratio()
            score = int(ratio * 39)

        if score > best_score:
            best_score, best_album = score, album

    return best_album if best_score >= 40 else None


def distribute_torrents(
    torrents: List[TorrentResult], albums: List[AlbumResult]
) -> List[TorrentResult]:
    """Match a list of torrents to albums in-place. Returns unmatched torrents."""
    unmatched = []
    for torrent in torrents:
        album = match_torrent_to_album(torrent, albums)
        if album is not None:
            album.torrents.append(torrent)
        else:
            unmatched.append(torrent)
    for album in albums:
        album.torrents.sort(key=lambda t: t.seeders, reverse=True)
    return unmatched
