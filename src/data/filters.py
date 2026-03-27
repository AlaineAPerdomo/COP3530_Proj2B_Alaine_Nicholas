from src.models.song import Song


def sample_songs(songs: list[Song], sample_size: int) -> list[Song]:
    """Return the first n songs."""
    if sample_size <= 0:
        return []
    return songs[:sample_size]


def filter_valid_songs(songs: list[Song]) -> list[Song]:
    """
    Basic Phase 1 validity filter.
    Keeps songs with a name and artist.
    """
    valid_songs = []

    for song in songs:
        if song.name.strip() and song.artists.strip():
            valid_songs.append(song)

    return valid_songs