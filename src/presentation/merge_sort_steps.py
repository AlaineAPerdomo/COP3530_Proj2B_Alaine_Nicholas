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
        recorder.record(
            "focus_segment",
            left=0,
            right=len(songs_copy) - 1,
            merge_left=0,
            merge_mid=(len(songs_copy) - 1) // 2,
            merge_right=len(songs_copy) - 1,
            depth=0,
        )
        _record_split_phase(
            left_index=0,
            right_index=len(songs_copy) - 1,
            depth=0,
            recorder=recorder,
        )
        _merge_sort_recursive(
            songs=songs_copy,
            left_index=0,
            right_index=len(songs_copy) - 1,
            feature=feature,
            ascending=ascending,
            depth=0,
            recorder=recorder,
        )

        recorder.record(
            "final",
            left=0,
            right=len(songs_copy) - 1,
            merge_left=0,
            merge_mid=(len(songs_copy) - 1) // 2,
            merge_right=len(songs_copy) - 1,
            depth=0,
        )

    return songs_copy, recorder.get_steps()


def _record_split_phase(
    left_index: int,
    right_index: int,
    depth: int,
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
        merge_left=left_index,
        merge_mid=midpoint,
        merge_right=right_index,
        depth=depth,
    )

    _record_split_phase(left_index, midpoint, depth + 1, recorder)
    _record_split_phase(midpoint + 1, right_index, depth + 1, recorder)


def _merge_sort_recursive(
    songs: list[Song],
    left_index: int,
    right_index: int,
    feature: str,
    ascending: bool,
    depth: int,
    recorder: StepRecorder,
) -> None:
    if left_index >= right_index:
        return

    midpoint = (left_index + right_index) // 2

    _merge_sort_recursive(songs, left_index, midpoint, feature, ascending, depth + 1, recorder)
    _merge_sort_recursive(songs, midpoint + 1, right_index, feature, ascending, depth + 1, recorder)

    recorder.record(
        "merge_focus",
        left=left_index,
        mid=midpoint,
        right=right_index,
        merge_left=left_index,
        merge_mid=midpoint,
        merge_right=right_index,
        depth=depth,
    )

    _merge(songs, left_index, midpoint, right_index, feature, ascending, depth, recorder)

    recorder.record(
        "merge_complete",
        left=left_index,
        right=right_index,
        merge_left=left_index,
        merge_mid=midpoint,
        merge_right=right_index,
        depth=depth,
    )


def _merge(
    songs: list[Song],
    left_index: int,
    midpoint: int,
    right_index: int,
    feature: str,
    ascending: bool,
    depth: int,
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
            merge_left=left_index,
            merge_mid=midpoint,
            merge_right=right_index,
            depth=depth,
        )

        if should_take_left(left_value, right_value, ascending):
            songs[merged_pointer] = left_song
            recorder.record(
                "write",
                source_index=left_index + left_pointer,
                target_index=merged_pointer,
                index=merged_pointer,
                merge_left=left_index,
                merge_mid=midpoint,
                merge_right=right_index,
                song_id=left_song.id,
                from_side="left",
                depth=depth,
            )
            left_pointer += 1
        else:
            songs[merged_pointer] = right_song
            recorder.record(
                "write",
                source_index=midpoint + 1 + right_pointer,
                target_index=merged_pointer,
                index=merged_pointer,
                merge_left=left_index,
                merge_mid=midpoint,
                merge_right=right_index,
                song_id=right_song.id,
                from_side="right",
                depth=depth,
            )
            right_pointer += 1

        merged_pointer += 1

    while left_pointer < len(left_half):
        left_song = left_half[left_pointer]
        left_value = left_song.get_feature_value(feature)

        songs[merged_pointer] = left_song

        recorder.record(
            "write",
            source_index=left_index + left_pointer,
            target_index=merged_pointer,
            index=merged_pointer,
            song_id=left_song.id,
            merge_left=left_index,
            merge_mid=midpoint,
            merge_right=right_index,
            from_side="left",
            depth=depth,
        )

        left_pointer += 1
        merged_pointer += 1

    while right_pointer < len(right_half):
        right_song = right_half[right_pointer]
        right_value = right_song.get_feature_value(feature)

        songs[merged_pointer] = right_song

        recorder.record(
            "write",
            source_index=midpoint + 1 + right_pointer,
            target_index=merged_pointer,
            index=merged_pointer,
            song_id=right_song.id,
            merge_left=left_index,
            merge_mid=midpoint,
            merge_right=right_index,
            from_side="right",
            depth=depth,
        )

        right_pointer += 1
        merged_pointer += 1


def should_take_left(left_value, right_value, ascending: bool) -> bool:
    if ascending:
        return left_value <= right_value
    return left_value >= right_value
