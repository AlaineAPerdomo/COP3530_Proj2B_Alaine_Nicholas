from random import shuffle

from PySide6.QtCore import QSignalBlocker, QThread, QTimer, Qt
from PySide6.QtWidgets import QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from src.app.animation_worker import AnimationWorker
from src.app.benchmark_worker import BenchmarkWorker
from src.animations.animator import MergeSortAnimator
from src.data.filters import sample_songs
from src.models.song import Song
from src.models.sort_step import SortStep
from src.ui.detail_panel import DetailPanel
from src.ui.header import HeaderPanel
from src.ui.metrics_panel import MetricsPanel
from src.ui.playlist_panel import PlaylistPanel
from src.ui.sidebar import SidebarPanel


class MainLayout(QWidget):
    DEFAULT_ANIMATION_SPEED_MS = 160
    VISUALIZATION_LIMIT = 50
    DEFAULT_FEATURE = "danceability"
    DEFAULT_ALGORITHM = "Merge Sort"
    DEFAULT_ORDER = "Ascending"
    DEFAULT_SAMPLE_SIZE = 25
    BENCHMARK_PREVIEW_LIMIT = 20

    def __init__(self, songs: list[Song]):
        super().__init__()

        self.all_songs = songs[:]
        self.original_songs: list[Song] = []
        self.visual_songs: list[Song] = []
        self.song_lookup: dict[str, Song] = {}
        self.current_feature = self.DEFAULT_FEATURE
        self.animator = None
        self.animation_thread: QThread | None = None
        self.animation_worker: AnimationWorker | None = None
        self.benchmark_thread: QThread | None = None
        self.benchmark_worker: BenchmarkWorker | None = None

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(14)

        self.sidebar = SidebarPanel()
        self.sidebar.set_sample_size_limit(len(self.all_songs))
        sidebar_scroll = self._build_column_scroll_area(
            object_name="SidebarScrollArea",
            content_widget=self.sidebar,
        )

        center_container = QWidget()
        center_container.setObjectName("CenterPanel")
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(16)

        self.header = HeaderPanel()
        self.playlist = PlaylistPanel()
        self.metrics = MetricsPanel()

        self._reload_dataset_sample(self.DEFAULT_SAMPLE_SIZE)

        center_layout.addWidget(self.header, 1)
        center_layout.addWidget(self.playlist, 5)
        center_layout.addWidget(self.metrics, 1)
        center_scroll = self._build_column_scroll_area(
            object_name="CenterScrollArea",
            content_widget=center_container,
        )

        self.detail_panel = DetailPanel()
        self.detail_panel.set_song_catalog(self.all_songs)

        root_layout.addWidget(sidebar_scroll, 1)
        root_layout.addWidget(center_scroll, 3)
        root_layout.addWidget(self.detail_panel, 1)

        self.playlist.table.itemSelectionChanged.connect(self.handle_song_selection)
        self.sidebar.animate_button.clicked.connect(self.run_merge_sort_animation)
        self.sidebar.compare_button.clicked.connect(self.compare_algorithms)
        self.sidebar.shuffle_button.clicked.connect(self.shuffle_playlist)
        self.sidebar.reset_button.clicked.connect(self.reset_playlist)
        self.sidebar.feature_dropdown.currentTextChanged.connect(self.change_feature)
        self.sidebar.sample_knob.valueChanged.connect(self.preview_dataset_mode)

    def handle_song_selection(self) -> None:
        selected_rows = self.playlist.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        self._focus_song_row(selected_rows[0].row())

    def change_feature(self, feature: str) -> None:
        self.current_feature = feature
        self.header.set_feature(feature)
        self.playlist.load_songs(self.visual_songs, feature=feature)
        self._update_mode_ui()

    def load_dataset_sample(self) -> None:
        if self.benchmark_thread is not None or self.animation_thread is not None:
            return

        if self.animator is not None:
            self.animator.stop()

        self._reload_dataset_sample(self.sidebar.sample_size_value())
        self.playlist.end_animation_highlighting()
        self.playlist.clear_all_highlights()
        self.playlist.table.clearSelection()
        self.header.set_status("Ready")
        self.metrics.set_comparisons(0)
        self.metrics.set_moves(0)
        self.metrics.set_overwrites(0)
        self.metrics.set_steps(0)
        self.metrics.set_runtime_ms(0)
        self.detail_panel.reset_view()

    def shuffle_playlist(self) -> None:
        if (
            self.benchmark_thread is not None
            or self.animation_thread is not None
            or len(self.original_songs) > self.VISUALIZATION_LIMIT
        ):
            return

        if self.animator is not None:
            self.animator.stop()

        self.visual_songs = self.original_songs[:]
        shuffle(self.visual_songs)
        self.original_songs = self.visual_songs[:]
        self.song_lookup = {song.id: song for song in self.original_songs}
        self.playlist.load_songs(self.visual_songs, feature=self.current_feature)
        self.playlist.end_animation_highlighting()
        self.playlist.clear_all_highlights()
        self.playlist.table.clearSelection()
        self.header.set_status("Shuffled")
        self.metrics.set_comparisons(0)
        self.metrics.set_moves(0)
        self.metrics.set_overwrites(0)
        self.metrics.set_steps(0)
        self.metrics.set_runtime_ms(0)

    def reset_playlist(self) -> None:
        if self.benchmark_thread is not None or self.animation_thread is not None:
            return

        if self.animator is not None:
            self.animator.stop()

        with QSignalBlocker(self.sidebar.algorithm_dropdown):
            self.sidebar.algorithm_dropdown.setCurrentText(self.DEFAULT_ALGORITHM)
        with QSignalBlocker(self.sidebar.feature_dropdown):
            self.sidebar.feature_dropdown.setCurrentText(self.DEFAULT_FEATURE)
        with QSignalBlocker(self.sidebar.order_dropdown):
            self.sidebar.order_dropdown.setCurrentText(self.DEFAULT_ORDER)
        with QSignalBlocker(self.sidebar.sample_knob):
            self.sidebar.set_sample_size_value(self.DEFAULT_SAMPLE_SIZE)

        self._reload_dataset_sample(self.DEFAULT_SAMPLE_SIZE)
        self.playlist.table.clearSelection()
        self.playlist.end_animation_highlighting()
        self.playlist.clear_all_highlights()
        self.header.set_status("Ready")
        self.header.set_algorithm(self.DEFAULT_ALGORITHM)
        self.metrics.set_comparisons(0)
        self.metrics.set_moves(0)
        self.metrics.set_overwrites(0)
        self.metrics.set_steps(0)
        self.metrics.set_runtime_ms(0)
        self.detail_panel.reset_view()

    def run_merge_sort_animation(self) -> None:
        if self.benchmark_thread is not None or self.animation_thread is not None:
            return

        self._prepare_run_view()

        if len(self.original_songs) > self.VISUALIZATION_LIMIT:
            self.run_selected_benchmark()
            return

        self.header.set_algorithm("Merge Sort")
        self.header.set_status("Preparing Animation")
        self._set_benchmark_controls_enabled(False)

        worker = AnimationWorker(
            songs=self.visual_songs,
            feature=self.current_feature,
            ascending=self.sidebar.order_dropdown.currentText() == "Ascending",
        )
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(self._update_animation_progress)
        worker.finished.connect(self._handle_animation_ready)
        worker.failed.connect(self._handle_animation_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_animation_thread)

        self.animation_worker = worker
        self.animation_thread = thread
        QTimer.singleShot(0, thread.start)

    def run_merge_sort_benchmark(self) -> None:
        self._start_benchmark(mode="single", algorithm="Merge Sort")

    def run_selected_benchmark(self) -> None:
        selected_algorithm = self.sidebar.algorithm_dropdown.currentText()
        if selected_algorithm == "Quick Sort":
            self.run_quick_sort_benchmark()
            return
        self.run_merge_sort_benchmark()

    def run_quick_sort_benchmark(self) -> None:
        self._start_benchmark(mode="single", algorithm="Quick Sort")

    def compare_algorithms(self) -> None:
        if (
            self.benchmark_thread is not None
            or self.animation_thread is not None
            or len(self.original_songs) <= self.VISUALIZATION_LIMIT
        ):
            return

        self._start_benchmark(mode="compare_preview")

    def prepare_for_animation(self) -> None:
        self.visual_songs = self.original_songs[:]
        self.playlist.begin_animation_highlighting()
        self.playlist.clear_all_highlights()

    def finish_animation(self) -> None:
        self.header.set_status("Completed")
        self.playlist.clear_all_highlights()
        self.playlist.highlight_sorted_range(0, len(self.visual_songs) - 1)
        self.playlist.end_animation_highlighting()
        self._focus_song_row(0)

    def update_status(self, status: str) -> None:
        self.header.set_status(status)

    def update_step_count(self, count: int) -> None:
        self.metrics.set_steps(count)

    def update_comparisons(self, count: int) -> None:
        self.metrics.set_comparisons(count)

    def update_moves(self, count: int) -> None:
        self.metrics.set_moves(count)

    def update_overwrites(self, count: int) -> None:
        self.metrics.set_overwrites(count)

    def update_runtime_ms(self, runtime_ms: int) -> None:
        self.metrics.set_runtime_ms(runtime_ms)

    def apply_sort_step(self, step: SortStep) -> None:
        step_type = step.step_type
        payload = step.payload

        if step_type == "compare":
            self._focus_song_row(payload["left_index"])
            self.playlist.highlight_compare(
                payload["left_index"],
                payload["right_index"],
            )

        elif step_type == "split":
            self._focus_song_row(payload["left"])
            self.playlist.highlight_merge_region(
                payload["left"],
                payload["right"],
            )

        elif step_type in {"take_left", "take_right"}:
            self._focus_song_row(payload["target_index"])
            self.playlist.highlight_move(
                payload["source_index"],
                payload["target_index"],
            )

        elif step_type == "overwrite":
            row_index = payload["index"]
            song_id = payload["song_id"]

            matching_song = self.song_lookup.get(song_id)
            if matching_song is not None:
                self.visual_songs[row_index] = matching_song
                self.playlist.update_song_at_index(row_index, matching_song)
                self._focus_song_row(row_index)
                self.playlist.highlight_overwrite(row_index)

        elif step_type == "sorted_range":
            self._focus_song_row(payload["left"])
            self.playlist.highlight_sorted_range(
                payload["left"],
                payload["right"],
            )

    def _build_column_scroll_area(self, object_name: str, content_widget: QWidget) -> QScrollArea:
        scroll_area = QScrollArea()
        scroll_area.setObjectName(object_name)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidget(content_widget)
        return scroll_area

    def _reload_dataset_sample(self, sample_size: int) -> None:
        self.current_feature = self.sidebar.feature_dropdown.currentText()
        self.original_songs = sample_songs(self.all_songs, sample_size)
        performance_mode = sample_size > self.VISUALIZATION_LIMIT
        preview_count = min(len(self.original_songs), self.BENCHMARK_PREVIEW_LIMIT)
        self.visual_songs = (
            self.original_songs[:preview_count]
            if performance_mode
            else self.original_songs[:]
        )
        self.song_lookup = {song.id: song for song in self.original_songs}
        self.header.set_feature(self.current_feature)
        self.playlist.load_songs(self.visual_songs, feature=self.current_feature)
        self._update_mode_ui()

    def _update_mode_ui(self) -> None:
        sample_size = self.sidebar.sample_size_value()
        performance_mode = sample_size > self.VISUALIZATION_LIMIT
        preview_count = (
            min(len(self.visual_songs), self.BENCHMARK_PREVIEW_LIMIT)
            if performance_mode
            else len(self.visual_songs)
        )
        self.sidebar.set_sort_mode(not performance_mode)
        self.header.set_mode(performance_mode)
        self.header.set_dataset_size(len(self.original_songs), performance_mode=performance_mode)
        self.playlist.set_workspace_mode(
            performance_mode=performance_mode,
            dataset_size=len(self.original_songs),
            feature=self.current_feature,
            preview_limit=preview_count,
        )

    def preview_dataset_mode(self, _value: int) -> None:
        self._update_mode_ui()

    def _start_benchmark(self, mode: str, algorithm: str = "Merge Sort") -> None:
        if self.benchmark_thread is not None or self.animation_thread is not None:
            return

        benchmark_title = algorithm if mode == "single" else "Merge Sort vs Quick Sort"
        benchmark_status = "Benchmark Sorting" if mode == "single" else "Comparing Algorithms"
        self._prepare_run_view()
        self.header.set_algorithm(benchmark_title)
        self.header.set_status(benchmark_status)
        self.playlist.end_animation_highlighting()
        self.playlist.clear_all_highlights()
        self.playlist.table.clearSelection()
        self.playlist.clear_benchmark_summary()
        self._set_benchmark_controls_enabled(False)

        self.metrics.set_comparisons(0)
        self.metrics.set_moves(0)
        self.metrics.set_overwrites(0)
        self.metrics.set_steps(0)
        self.metrics.set_runtime_ms(0)

        worker = BenchmarkWorker(
            songs=self.original_songs,
            feature=self.current_feature,
            ascending=self.sidebar.order_dropdown.currentText() == "Ascending",
            preview_limit=self.BENCHMARK_PREVIEW_LIMIT,
            mode=mode,
            algorithm=algorithm,
        )
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(self._update_benchmark_progress)
        worker.finished.connect(self._handle_benchmark_finished)
        worker.failed.connect(self._handle_benchmark_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_benchmark_thread)

        self.benchmark_worker = worker
        self.benchmark_thread = thread
        QTimer.singleShot(0, thread.start)

    def _update_benchmark_progress(self, value: int, text: str) -> None:
        self.header.set_status(text)

    def _handle_benchmark_finished(self, result: dict) -> None:
        self.visual_songs = result["preview_songs"]
        self.playlist.load_songs(self.visual_songs, feature=self.current_feature)
        self.playlist.set_benchmark_summary(
            dataset_size=len(self.original_songs),
            feature=self.current_feature,
            preview_rows=result["preview_count"],
            merge_runtime_ms=result.get("merge_runtime_ms"),
            quick_runtime_ms=result.get("quick_runtime_ms"),
            quick_summary_text=result.get("quick_summary_text"),
            faster_text=result.get("faster_text"),
        )
        self.playlist.table.clearSelection()
        self.header.set_algorithm(result["algorithm"])
        final_status = (
            f"Comparison Ready - Top {result['preview_count']} shown"
            if result["mode"] == "compare_preview"
            else f"Benchmark Completed - Top {result['preview_count']} shown"
        )
        self.header.set_status(final_status)
        self._set_benchmark_controls_enabled(True)
        self.metrics.set_runtime_ms(result["runtime_ms"])

    def _handle_benchmark_failed(self, error_text: str) -> None:
        self.header.set_status(f"Benchmark Failed: {error_text}")
        self._set_benchmark_controls_enabled(True)

    def _clear_benchmark_thread(self) -> None:
        self.benchmark_worker = None
        self.benchmark_thread = None

    def _update_animation_progress(self, value: int, text: str) -> None:
        self.header.set_status(text)

    def _handle_animation_ready(self, steps: list[SortStep]) -> None:
        self._set_benchmark_controls_enabled(True)
        self.animator = MergeSortAnimator(
            steps=steps,
            layout_controller=self,
            speed_ms=self.DEFAULT_ANIMATION_SPEED_MS,
        )
        self.animator.start()

    def _handle_animation_failed(self, error_text: str) -> None:
        self.header.set_status(f"Animation Failed: {error_text}")
        self._set_benchmark_controls_enabled(True)

    def _clear_animation_thread(self) -> None:
        self.animation_worker = None
        self.animation_thread = None

    def _set_benchmark_controls_enabled(self, enabled: bool) -> None:
        self.sidebar.algorithm_dropdown.setEnabled(enabled)
        self.sidebar.feature_dropdown.setEnabled(enabled)
        self.sidebar.order_dropdown.setEnabled(enabled)
        self.sidebar.sample_knob.setEnabled(enabled)
        self.sidebar.animate_button.setEnabled(enabled)
        self.sidebar.compare_button.setEnabled(enabled and self.sidebar.compare_button.isVisible())
        self.sidebar.shuffle_button.setEnabled(enabled and self.sidebar.shuffle_button.isVisible())
        self.sidebar.reset_button.setEnabled(enabled)

    def _prepare_run_view(self) -> None:
        if self.animator is not None:
            self.animator.stop()

        self._reload_dataset_sample(self.sidebar.sample_size_value())
        self.playlist.end_animation_highlighting()
        self.playlist.clear_all_highlights()
        self.playlist.table.clearSelection()
        self.detail_panel.reset_view()
        self.metrics.set_comparisons(0)
        self.metrics.set_moves(0)
        self.metrics.set_overwrites(0)
        self.metrics.set_steps(0)
        self.metrics.set_runtime_ms(0)
        self.header.set_status("Preparing Selection")

    def _focus_song_row(self, row_index: int) -> None:
        if 0 <= row_index < len(self.visual_songs):
            self.detail_panel.update_song(self.visual_songs[row_index])
