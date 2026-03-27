from src.algorithms.validators import validate_sort_feature
from src.models.song import Song


def merge_sort_songs(songs: list[Song], feature: str, ascending: bool = True) -> list[Song]:
    """
    Benchmark merge sort for large datasets.
    Returns only the sorted result without recording animation steps.
    """
    validate_sort_feature(feature)
    return _merge_sort_recursive_plain(songs, feature, ascending)


def _merge_sort_recursive_plain(
    songs: list[Song],
    feature: str,
    ascending: bool,
) -> list[Song]:
    if len(songs) <= 1:
        return songs[:]

    midpoint = len(songs) // 2
    left_sorted = _merge_sort_recursive_plain(songs[:midpoint], feature, ascending)
    right_sorted = _merge_sort_recursive_plain(songs[midpoint:], feature, ascending)
    return _merge_plain(left_sorted, right_sorted, feature, ascending)


def _merge_plain(
    left_half: list[Song],
    right_half: list[Song],
    feature: str,
    ascending: bool,
) -> list[Song]:
    merged: list[Song] = []
    left_pointer = 0
    right_pointer = 0

    while left_pointer < len(left_half) and right_pointer < len(right_half):
        left_song = left_half[left_pointer]
        right_song = right_half[right_pointer]

        left_value = left_song.get_feature_value(feature)
        right_value = right_song.get_feature_value(feature)

        if should_take_left(left_value, right_value, ascending):
            merged.append(left_song)
            left_pointer += 1
        else:
            merged.append(right_song)
            right_pointer += 1

    while left_pointer < len(left_half):
        merged.append(left_half[left_pointer])
        left_pointer += 1

    while right_pointer < len(right_half):
        merged.append(right_half[right_pointer])
        right_pointer += 1

    return merged


def should_take_left(left_value, right_value, ascending: bool) -> bool:
    """
    Stable comparison rule:
    take left first when equal.
    """
    if ascending:
        return left_value <= right_value
    return left_value >= right_value
