from time import perf_counter

from PySide6.QtCore import QObject, Signal, Slot

from src.algorithms.merge_sort import merge_sort_songs
from src.models.song import Song


class BenchmarkWorker(QObject):
    progress = Signal(int, str)
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(
        self,
        songs: list[Song],
        feature: str,
        ascending: bool,
        preview_limit: int,
        mode: str,
        algorithm: str = "Merge Sort",
    ):
        super().__init__()
        self.songs = songs[:]
        self.feature = feature
        self.ascending = ascending
        self.preview_limit = preview_limit
        self.mode = mode
        self.algorithm = algorithm

    @Slot()
    def run(self) -> None:
        try:
            if self.mode == "compare_preview":
                self._run_compare_preview()
                return

            if self.algorithm != "Merge Sort":
                self._run_placeholder_benchmark()
                return

            self._run_merge_benchmark()
        except Exception as exc:
            self.failed.emit(str(exc))

    def _run_merge_benchmark(self) -> None:
        self.progress.emit(10, "Preparing merge sort analysis")
        self.progress.emit(40, "Running Merge Sort")
        start_time = perf_counter()
        sorted_songs = merge_sort_songs(
            self.songs,
            feature=self.feature,
            ascending=self.ascending,
        )
        runtime_ms = int((perf_counter() - start_time) * 1000)

        self.progress.emit(85, "Building merge preview")
        preview_count = min(self.preview_limit, len(sorted_songs))
        preview_songs = sorted_songs[:preview_count]

        self.progress.emit(100, "Merge analysis complete")
        self.finished.emit(
            {
                "mode": "single",
                "algorithm": "Merge Sort",
                "runtime_ms": runtime_ms,
                "preview_count": preview_count,
                "preview_songs": preview_songs,
                "merge_runtime_ms": runtime_ms,
                "quick_runtime_ms": None,
                "quick_summary_text": "Quick Sort: Partner integration pending",
                "faster_text": "Faster Algorithm: Pending teammate integration",
            }
        )

    def _run_compare_preview(self) -> None:
        self.progress.emit(10, "Preparing comparison preview")
        self.progress.emit(45, "Running Merge Sort analytics")
        start_time = perf_counter()
        sorted_songs = merge_sort_songs(
            self.songs,
            feature=self.feature,
            ascending=self.ascending,
        )
        runtime_ms = int((perf_counter() - start_time) * 1000)

        self.progress.emit(85, "Building placeholder comparison")
        preview_count = min(self.preview_limit, len(sorted_songs))
        preview_songs = sorted_songs[:preview_count]

        self.progress.emit(100, "Comparison preview ready")
        self.finished.emit(
            {
                "mode": "compare_preview",
                "algorithm": "Merge Sort Analytics",
                "runtime_ms": runtime_ms,
                "preview_count": preview_count,
                "preview_songs": preview_songs,
                "merge_runtime_ms": runtime_ms,
                "quick_runtime_ms": None,
                "quick_summary_text": "Quick Sort: Partner integration pending",
                "faster_text": "Faster Algorithm: Pending teammate integration",
            }
        )

    def _run_placeholder_benchmark(self) -> None:
        self.progress.emit(100, "Quick Sort benchmark pending teammate integration")
        preview_count = min(self.preview_limit, len(self.songs))
        self.finished.emit(
            {
                "mode": "single",
                "algorithm": self.algorithm,
                "runtime_ms": 0,
                "preview_count": preview_count,
                "preview_songs": self.songs[:preview_count],
                "merge_runtime_ms": None,
                "quick_runtime_ms": None,
                "quick_summary_text": "Quick Sort: Partner integration pending",
                "faster_text": "Faster Algorithm: Pending teammate integration",
            }
        )
