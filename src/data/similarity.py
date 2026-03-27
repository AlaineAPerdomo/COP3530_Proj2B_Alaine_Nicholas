from math import sqrt

from src.models.song import Song
from src.utils.constants import RADAR_FEATURES


def rank_similar_songs(
    songs: list[Song],
    profile: dict[str, float],
    exclude_song_id: str | None = None,
    limit: int = 5,
) -> list[tuple[Song, float]]:
    scored_songs: list[tuple[Song, float]] = []
    max_distance = sqrt(len(RADAR_FEATURES))

    for song in songs:
        if song.id == exclude_song_id:
            continue

        distance = _profile_distance(song, profile)
        similarity_score = max(0.0, 1.0 - (distance / max_distance))
        scored_songs.append((song, similarity_score))

    scored_songs.sort(key=lambda item: item[1], reverse=True)
    return scored_songs[:limit]


def _profile_distance(song: Song, profile: dict[str, float]) -> float:
    squared_sum = 0.0

    for feature in RADAR_FEATURES:
        target_value = profile[feature]
        song_value = song.normalize_feature(feature)
        squared_sum += (song_value - target_value) ** 2

    return sqrt(squared_sum)
