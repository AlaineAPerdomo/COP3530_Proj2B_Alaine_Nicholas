from src.algorithms.validators import validate_sort_feature
from src.models.song import Song
from src.models.sort_step import SortStep


class QuickStepRecorder:
    def __init__(self):
        self.steps: list[SortStep] = []

    def record(self, step_type: str, **payload) -> None:
        self.steps.append(SortStep(step_type=step_type, payload=payload))

    def all_steps(self) -> list[SortStep]:
        return self.steps[:]


def quick_sort_with_steps(
    songs: list[Song],
    feature: str,
    ascending: bool = True,
) -> tuple[list[Song], list[SortStep]]:
    validate_sort_feature(feature)

    songs_copy = songs[:]
    recorder = QuickStepRecorder()

    if songs_copy:
        recorder.record(
            "focus_segment",
            left=0,
            right=len(songs_copy) - 1,
            snapshot_song_ids=_snapshot_song_ids(songs_copy),
        )
        _quick_sort_recursive(
            songs_copy,
            feature,
            ascending,
            0,
            len(songs_copy) - 1,
            recorder,
        )
        recorder.record(
            "final",
            left=0,
            right=len(songs_copy) - 1,
            snapshot_song_ids=_snapshot_song_ids(songs_copy),
        )

    return songs_copy, recorder.all_steps()


def _quick_sort_recursive(
    songs: list[Song],
    feature: str,
    ascending: bool,
    low: int,
    high: int,
    recorder: QuickStepRecorder,
) -> None:
    if low >= high:
        return

    partition_index = _partition(songs, feature, ascending, low, high, recorder)

    recorder.record(
        "partition_done",
        left=low,
        right=high,
        pivot_final_index=partition_index,
        pivot_song_id=songs[partition_index].id,
        snapshot_song_ids=_snapshot_song_ids(songs),
    )

    if low < partition_index - 1:
        recorder.record(
            "focus_segment",
            left=low,
            right=partition_index - 1,
            snapshot_song_ids=_snapshot_song_ids(songs),
        )
    _quick_sort_recursive(songs, feature, ascending, low, partition_index - 1, recorder)

    if partition_index + 1 < high:
        recorder.record(
            "focus_segment",
            left=partition_index + 1,
            right=high,
            snapshot_song_ids=_snapshot_song_ids(songs),
        )
    _quick_sort_recursive(songs, feature, ascending, partition_index + 1, high, recorder)


def _partition(
    songs: list[Song],
    feature: str,
    ascending: bool,
    low: int,
    high: int,
    recorder: QuickStepRecorder,
) -> int:
    middle = low + (high - low) // 2
    songs[middle], songs[high] = songs[high], songs[middle]
    pivot_song = songs[high]
    pivot_value = pivot_song.get_feature_value(feature)

    recorder.record(
        "choose_pivot",
        left=low,
        right=high,
        pivot_index=high,
        pivot_song_id=pivot_song.id,
        snapshot_song_ids=_snapshot_song_ids(songs),
        less_song_ids=[],
        greater_song_ids=[],
    )

    left = low
    right = high - 1

    while True:
        while left <= right and _comes_before(
            songs[left].get_feature_value(feature),
            pivot_value,
            ascending,
        ):
            recorder.record(
                "move_left",
                left=low,
                right=high,
                pivot_index=high,
                pivot_song_id=pivot_song.id,
                current_index=left,
                current_song_id=songs[left].id,
                snapshot_song_ids=_snapshot_song_ids(songs),
                less_song_ids=[song.id for song in songs[low:left + 1]],
                greater_song_ids=[],
            )
            left += 1

        while right >= left and _comes_after(
            songs[right].get_feature_value(feature),
            pivot_value,
            ascending,
        ):
            recorder.record(
                "move_right",
                left=low,
                right=high,
                pivot_index=high,
                pivot_song_id=pivot_song.id,
                current_index=right,
                current_song_id=songs[right].id,
                snapshot_song_ids=_snapshot_song_ids(songs),
                less_song_ids=[song.id for song in songs[low:left]],
                greater_song_ids=[song.id for song in songs[right:high]],
            )
            right -= 1

        if left >= right:
            break

        recorder.record(
            "compare",
            left=low,
            right=high,
            pivot_index=high,
            pivot_song_id=pivot_song.id,
            left_index=left,
            right_index=right,
            left_song_id=songs[left].id,
            right_song_id=songs[right].id,
            snapshot_song_ids=_snapshot_song_ids(songs),
            less_song_ids=[song.id for song in songs[low:left]],
            greater_song_ids=[song.id for song in songs[right + 1:high]],
        )

        songs[left], songs[right] = songs[right], songs[left]

        recorder.record(
            "swap",
            left=low,
            right=high,
            pivot_index=high,
            pivot_song_id=pivot_song.id,
            left_index=left,
            right_index=right,
            snapshot_song_ids=_snapshot_song_ids(songs),
            less_song_ids=[song.id for song in songs[low:left + 1]],
            greater_song_ids=[song.id for song in songs[right:high]],
        )

        left += 1
        right -= 1

    songs[left], songs[high] = songs[high], songs[left]

    recorder.record(
        "place_pivot",
        left=low,
        right=high,
        pivot_index=left,
        pivot_song_id=songs[left].id,
        snapshot_song_ids=_snapshot_song_ids(songs),
        less_song_ids=[song.id for song in songs[low:left]],
        greater_song_ids=[song.id for song in songs[left + 1:high + 1]],
    )

    return left


def _snapshot_song_ids(songs: list[Song]) -> list[str]:
    return [song.id for song in songs]


def _comes_before(value: float, pivot_value: float, ascending: bool) -> bool:
    return value < pivot_value if ascending else value > pivot_value


def _comes_after(value: float, pivot_value: float, ascending: bool) -> bool:
    return value > pivot_value if ascending else value < pivot_value
