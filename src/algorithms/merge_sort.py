from src.algorithms.step_recorder import StepRecorder
from src.models.song import Song
from src.models.sort_step import SortStep


def merge_sort_songs(songs: list[Song], feature: str, ascending: bool = True) -> list[Song]:
    """
    Basic merge sort from Phase 2.
    Returns only the sorted result.
    """
    sorted_songs, _ = merge_sort_with_steps(songs, feature, ascending)
    return sorted_songs


def merge_sort_with_steps(
    songs: list[Song],
    feature: str,
    ascending: bool = True,
) -> tuple[list[Song], list[SortStep]]:
    """
    Merge Sort written from scratch, now with step recording.

    Returns:
        (sorted_songs, steps)
    """
    songs_copy = songs[:]
    recorder = StepRecorder()

    if songs_copy:
        _merge_sort_recursive(
            songs=songs_copy,
            left_index=0,
            right_index=len(songs_copy) - 1,
            feature=feature,
            ascending=ascending,
            recorder=recorder,
        )

    return songs_copy, recorder.get_steps()


def _merge_sort_recursive(
    songs: list[Song],
    left_index: int,
    right_index: int,
    feature: str,
    ascending: bool,
    recorder: StepRecorder,
) -> None:
    if left_index >= right_index:
        recorder.record(
            "sorted_range",
            left=left_index,
            right=right_index,
        )
        return

    midpoint = (left_index + right_index) // 2

    recorder.record(
        "split",
        left=left_index,
        mid=midpoint,
        right=right_index,
    )

    _merge_sort_recursive(songs, left_index, midpoint, feature, ascending, recorder)
    _merge_sort_recursive(songs, midpoint + 1, right_index, feature, ascending, recorder)

    _merge(songs, left_index, midpoint, right_index, feature, ascending, recorder)

    recorder.record(
        "sorted_range",
        left=left_index,
        right=right_index,
    )


def _merge(
    songs: list[Song],
    left_index: int,
    midpoint: int,
    right_index: int,
    feature: str,
    ascending: bool,
    recorder: StepRecorder,
) -> None:
    left_half = songs[left_index:midpoint + 1]
    right_half = songs[midpoint + 1:right_index + 1]

    left_pointer = 0
    right_pointer = 0
    merged_pointer = left_index

    while left_pointer < len(left_half) and right_pointer < len(right_half):
        left_song = left_half[left_pointer]
        right_song = right_half[right_pointer]

        left_value = left_song.get_feature_value(feature)
        right_value = right_song.get_feature_value(feature)

        recorder.record(
            "compare",
            left_index=left_index + left_pointer,
            right_index=midpoint + 1 + right_pointer,
            left_song_id=left_song.id,
            right_song_id=right_song.id,
            left_song_name=left_song.name,
            right_song_name=right_song.name,
            left_value=left_value,
            right_value=right_value,
            feature=feature,
        )

        if should_take_left(left_value, right_value, ascending):
            recorder.record(
                "take_left",
                source_index=left_index + left_pointer,
                target_index=merged_pointer,
                song_id=left_song.id,
                song_name=left_song.name,
                value=left_value,
            )
            songs[merged_pointer] = left_song
            left_pointer += 1
        else:
            recorder.record(
                "take_right",
                source_index=midpoint + 1 + right_pointer,
                target_index=merged_pointer,
                song_id=right_song.id,
                song_name=right_song.name,
                value=right_value,
            )
            songs[merged_pointer] = right_song
            right_pointer += 1

        recorder.record(
            "overwrite",
            index=merged_pointer,
            song_id=songs[merged_pointer].id,
            song_name=songs[merged_pointer].name,
            value=songs[merged_pointer].get_feature_value(feature),
        )

        merged_pointer += 1

    while left_pointer < len(left_half):
        left_song = left_half[left_pointer]
        left_value = left_song.get_feature_value(feature)

        recorder.record(
            "take_left",
            source_index=left_index + left_pointer,
            target_index=merged_pointer,
            song_id=left_song.id,
            song_name=left_song.name,
            value=left_value,
        )

        songs[merged_pointer] = left_song

        recorder.record(
            "overwrite",
            index=merged_pointer,
            song_id=left_song.id,
            song_name=left_song.name,
            value=left_value,
        )

        left_pointer += 1
        merged_pointer += 1

    while right_pointer < len(right_half):
        right_song = right_half[right_pointer]
        right_value = right_song.get_feature_value(feature)

        recorder.record(
            "take_right",
            source_index=midpoint + 1 + right_pointer,
            target_index=merged_pointer,
            song_id=right_song.id,
            song_name=right_song.name,
            value=right_value,
        )

        songs[merged_pointer] = right_song

        recorder.record(
            "overwrite",
            index=merged_pointer,
            song_id=right_song.id,
            song_name=right_song.name,
            value=right_value,
        )

        right_pointer += 1
        merged_pointer += 1


def should_take_left(left_value, right_value, ascending: bool) -> bool:
    """
    Stable comparison rule:
    take left first when equal.
    """
    if ascending:
        return left_value <= right_value
    return left_value >= right_value
