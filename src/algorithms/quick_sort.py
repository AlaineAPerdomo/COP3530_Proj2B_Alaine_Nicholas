from src.algorithms.validators import validate_sort_feature
from src.models.song import Song


def quick_sort_songs(songs: list[Song], feature: str, ascending: bool = True) -> list[Song]:
    """
    Python runtime port of the teammate-owned C++ quick sort in `src/algorithms/cpp/quicksort.cpp`.
    This keeps the UI and benchmarks inside the PySide app while following the same
    midpoint-pivot partition strategy.
    """
    validate_sort_feature(feature)
    songs_copy = songs[:]
    if songs_copy:
        _quick_sort_recursive(songs_copy, feature, ascending, 0, len(songs_copy) - 1)
    return songs_copy


def _quick_sort_recursive(
    songs: list[Song],
    feature: str,
    ascending: bool,
    low: int,
    high: int,
) -> None:
    if low >= high:
        return

    partition_index = _partition(songs, feature, ascending, low, high)
    _quick_sort_recursive(songs, feature, ascending, low, partition_index - 1)
    _quick_sort_recursive(songs, feature, ascending, partition_index + 1, high)


def _partition(
    songs: list[Song],
    feature: str,
    ascending: bool,
    low: int,
    high: int,
) -> int:
    middle = low + (high - low) // 2
    songs[middle], songs[high] = songs[high], songs[middle]
    pivot_value = songs[high].get_feature_value(feature)

    left = low
    right = high - 1

    while True:
        while left <= right and _comes_before(
            songs[left].get_feature_value(feature),
            pivot_value,
            ascending,
        ):
            left += 1

        while right >= left and _comes_after(
            songs[right].get_feature_value(feature),
            pivot_value,
            ascending,
        ):
            right -= 1

        if left >= right:
            break

        songs[left], songs[right] = songs[right], songs[left]
        left += 1
        right -= 1

    songs[left], songs[high] = songs[high], songs[left]
    return left


def _comes_before(value: float, pivot_value: float, ascending: bool) -> bool:
    return value < pivot_value if ascending else value > pivot_value


def _comes_after(value: float, pivot_value: float, ascending: bool) -> bool:
    return value > pivot_value if ascending else value < pivot_value
