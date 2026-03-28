from src.algorithms.validators import validate_sort_feature
from src.models.song import Song
from src.models.sort_step import SortStep


class StepRecorder:
    def __init__(self):
        self.steps: list[SortStep] = []

    def record(self, step_type: str, **payload) -> None:
        self.steps.append(SortStep(step_type=step_type, payload=payload))

    def get_steps(self) -> list[SortStep]:
        return self.steps[:]


def merge_sort_with_steps(
    songs: list[Song],
    feature: str,
    ascending: bool = True,
) -> tuple[list[Song], list[SortStep]]:
    validate_sort_feature(feature)

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
        )

        if should_take_left(left_value, right_value, ascending):
            recorder.record(
                "take_left",
                source_index=left_index + left_pointer,
                target_index=merged_pointer,
            )
            songs[merged_pointer] = left_song
            left_pointer += 1
        else:
            recorder.record(
                "take_right",
                source_index=midpoint + 1 + right_pointer,
                target_index=merged_pointer,
            )
            songs[merged_pointer] = right_song
            right_pointer += 1

        recorder.record(
            "overwrite",
            index=merged_pointer,
            song_id=songs[merged_pointer].id,
        )

        merged_pointer += 1

    while left_pointer < len(left_half):
        left_song = left_half[left_pointer]
        left_value = left_song.get_feature_value(feature)

        recorder.record(
            "take_left",
            source_index=left_index + left_pointer,
            target_index=merged_pointer,
        )

        songs[merged_pointer] = left_song

        recorder.record(
            "overwrite",
            index=merged_pointer,
            song_id=left_song.id,
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
        )

        songs[merged_pointer] = right_song

        recorder.record(
            "overwrite",
            index=merged_pointer,
            song_id=right_song.id,
        )

        right_pointer += 1
        merged_pointer += 1


def should_take_left(left_value, right_value, ascending: bool) -> bool:
    if ascending:
        return left_value <= right_value
    return left_value >= right_value
