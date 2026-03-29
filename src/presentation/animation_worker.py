from PySide6.QtCore import QObject, Signal, Slot

from src.models.song import Song
from src.presentation.merge_sort_steps import merge_sort_with_steps
from src.presentation.quick_sort_steps import quick_sort_with_steps


class AnimationWorker(QObject):
    progress = Signal(int, str)
    finished = Signal(list)
    failed = Signal(str)

    def __init__(self, songs: list[Song], feature: str, ascending: bool, algorithm: str):
        super().__init__()
        self.songs = songs[:]
        self.feature = feature
        self.ascending = ascending
        self.algorithm = algorithm

    @Slot()
    def run(self) -> None:
        try:
            self.progress.emit(15, "Preparing animation dataset")
            if self.algorithm == "Quick Sort":
                self.progress.emit(55, "Recording quick sort steps")
                _, steps = quick_sort_with_steps(
                    self.songs,
                    feature=self.feature,
                    ascending=self.ascending,
                )
            else:
                self.progress.emit(55, "Recording merge sort steps")
                _, steps = merge_sort_with_steps(
                    self.songs,
                    feature=self.feature,
                    ascending=self.ascending,
                )
            self.progress.emit(100, "Animation ready")
            self.finished.emit(steps)
        except Exception as exc:
            self.failed.emit(str(exc))
