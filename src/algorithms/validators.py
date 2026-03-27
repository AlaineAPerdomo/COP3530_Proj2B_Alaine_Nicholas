from src.utils.constants import SORTABLE_FEATURES


def validate_sort_feature(feature: str) -> None:
    if feature not in SORTABLE_FEATURES:
        raise ValueError(f"Unsupported sort feature: {feature}")


def is_sorted(songs: list, feature: str, ascending: bool = True) -> bool:
    validate_sort_feature(feature)

    for index in range(len(songs) - 1):
        current_value = songs[index].get_feature_value(feature)
        next_value = songs[index + 1].get_feature_value(feature)

        if ascending:
            if current_value > next_value:
                return False
        else:
            if current_value < next_value:
                return False

    return True


def same_song_set(original_songs: list, sorted_songs: list, id_key: str = "id") -> bool:
    if len(original_songs) != len(sorted_songs):
        return False

    original_counts: dict[str, int] = {}
    sorted_counts: dict[str, int] = {}

    for song in original_songs:
        song_id = str(getattr(song, id_key))
        original_counts[song_id] = original_counts.get(song_id, 0) + 1

    for song in sorted_songs:
        song_id = str(getattr(song, id_key))
        sorted_counts[song_id] = sorted_counts.get(song_id, 0) + 1

    return original_counts == sorted_counts


def validate_sorted_result(
    original_songs: list,
    sorted_songs: list,
    feature: str,
    ascending: bool = True,
) -> bool:
    return is_sorted(sorted_songs, feature, ascending) and same_song_set(original_songs, sorted_songs)
