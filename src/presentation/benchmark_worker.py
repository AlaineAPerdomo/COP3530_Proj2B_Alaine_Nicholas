from time import perf_counter

from PySide6.QtCore import QObject, Signal, Slot

from src.algorithms.merge_sort import merge_sort_songs
from src.algorithms.quick_sort import quick_sort_songs
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

            if self.mode == "single" and self.algorithm == "Quick Sort":
                self._run_quick_benchmark()
                return

            if self.algorithm == "Merge Sort":
                self._run_merge_benchmark()
                return

            self._run_compare_preview()
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
                "quick_summary_text": "Quick Sort Time: Select Compare Algorithms",
                "faster_text": "Faster Algorithm: Run compare mode",
            }
        )

    def _run_quick_benchmark(self) -> None:
        self.progress.emit(10, "Preparing quick sort analysis")
        self.progress.emit(40, "Running Quick Sort")
        start_time = perf_counter()
        sorted_songs = quick_sort_songs(
            self.songs,
            feature=self.feature,
            ascending=self.ascending,
        )
        runtime_ms = int((perf_counter() - start_time) * 1000)

        self.progress.emit(85, "Building quick sort preview")
        preview_count = min(self.preview_limit, len(sorted_songs))
        preview_songs = sorted_songs[:preview_count]

        self.progress.emit(100, "Quick sort analysis complete")
        self.finished.emit(
            {
                "mode": "single",
                "algorithm": "Quick Sort",
                "runtime_ms": runtime_ms,
                "preview_count": preview_count,
                "preview_songs": preview_songs,
                "merge_runtime_ms": None,
                "quick_runtime_ms": runtime_ms,
                "quick_summary_text": None,
                "faster_text": "Faster Algorithm: Run compare mode",
            }
        )

    def _run_compare_preview(self) -> None:
        self.progress.emit(10, "Preparing comparison preview")
        self.progress.emit(45, "Running Merge Sort analytics")
        merge_start = perf_counter()
        merge_sorted = merge_sort_songs(
            self.songs,
            feature=self.feature,
            ascending=self.ascending,
        )
        merge_runtime_ms = int((perf_counter() - merge_start) * 1000)

        self.progress.emit(70, "Running Quick Sort analytics")
        quick_start = perf_counter()
        quick_sorted = quick_sort_songs(
            self.songs,
            feature=self.feature,
            ascending=self.ascending,
        )
        quick_runtime_ms = int((perf_counter() - quick_start) * 1000)

        self.progress.emit(90, "Building comparison preview")
        preview_count = min(self.preview_limit, len(merge_sorted))
        preview_songs = merge_sorted[:preview_count]

        self.progress.emit(100, "Comparison preview ready")
        self.finished.emit(
            {
                "mode": "compare_preview",
                "algorithm": "Merge Sort vs Quick Sort",
                "runtime_ms": max(merge_runtime_ms, quick_runtime_ms),
                "preview_count": preview_count,
                "preview_songs": preview_songs,
                "merge_runtime_ms": merge_runtime_ms,
                "quick_runtime_ms": quick_runtime_ms,
                "quick_summary_text": None,
                "faster_text": self._faster_label(merge_runtime_ms, quick_runtime_ms),
            }
        )

    def _faster_label(self, merge_runtime_ms: int, quick_runtime_ms: int) -> str:
        if merge_runtime_ms < quick_runtime_ms:
            return "Faster Algorithm: Merge Sort"
        if quick_runtime_ms < merge_runtime_ms:
            return "Faster Algorithm: Quick Sort"
        return "Faster Algorithm: Tie"
