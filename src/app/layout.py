from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtWidgets import QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from src.algorithms.merge_sort import merge_sort_with_steps
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
    DEFAULT_ANIMATION_SPEED_MS = 360
    DEFAULT_FEATURE = "danceability"
    DEFAULT_ALGORITHM = "Merge Sort"
    DEFAULT_ORDER = "Ascending"
    DEFAULT_SAMPLE_SIZE = 25

    def __init__(self, songs: list[Song]):
        super().__init__()

        self.all_songs = songs[:]
        self.original_songs: list[Song] = []
        self.visual_songs: list[Song] = []
        self.song_lookup: dict[str, Song] = {}
        self.current_feature = self.DEFAULT_FEATURE
        self.animator = None

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(14)

        self.sidebar = SidebarPanel()
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
        self.sidebar.load_button.clicked.connect(self.load_dataset_sample)
        self.sidebar.animate_button.clicked.connect(self.run_merge_sort_animation)
        self.sidebar.reset_button.clicked.connect(self.reset_playlist)
        self.sidebar.feature_dropdown.currentTextChanged.connect(self.change_feature)

    def handle_song_selection(self) -> None:
        selected_rows = self.playlist.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row_index = selected_rows[0].row()
        if 0 <= row_index < len(self.visual_songs):
            self.detail_panel.update_song(self.visual_songs[row_index])

    def change_feature(self, feature: str) -> None:
        self.current_feature = feature
        self.header.set_feature(feature)
        self.playlist.load_songs(self.visual_songs, feature=feature)

    def load_dataset_sample(self) -> None:
        if self.animator is not None:
            self.animator.stop()

        self._reload_dataset_sample(self.sidebar.sample_spinbox.value())
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

    def reset_playlist(self) -> None:
        if self.animator is not None:
            self.animator.stop()

        with QSignalBlocker(self.sidebar.algorithm_dropdown):
            self.sidebar.algorithm_dropdown.setCurrentText(self.DEFAULT_ALGORITHM)
        with QSignalBlocker(self.sidebar.feature_dropdown):
            self.sidebar.feature_dropdown.setCurrentText(self.DEFAULT_FEATURE)
        with QSignalBlocker(self.sidebar.order_dropdown):
            self.sidebar.order_dropdown.setCurrentText(self.DEFAULT_ORDER)
        with QSignalBlocker(self.sidebar.sample_spinbox):
            self.sidebar.sample_spinbox.setValue(self.DEFAULT_SAMPLE_SIZE)

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
        self.header.set_algorithm("Merge Sort")
        self.header.set_status("Animating")

        songs_for_sort = self.visual_songs[:]
        _, steps = merge_sort_with_steps(
            songs_for_sort,
            feature=self.current_feature,
            ascending=self.sidebar.order_dropdown.currentText() == "Ascending",
        )

        self.animator = MergeSortAnimator(
            steps=steps,
            layout_controller=self,
            speed_ms=self.DEFAULT_ANIMATION_SPEED_MS,
        )
        self.animator.start()

    def prepare_for_animation(self) -> None:
        self.visual_songs = self.original_songs[:]
        self.playlist.load_songs(self.visual_songs, feature=self.current_feature)
        self.playlist.begin_animation_highlighting()
        self.playlist.clear_all_highlights()

    def finish_animation(self) -> None:
        self.header.set_status("Completed")
        self.playlist.clear_all_highlights()
        self.playlist.highlight_sorted_range(0, len(self.visual_songs) - 1)
        self.playlist.end_animation_highlighting()

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
            self.playlist.highlight_compare(
                payload["left_index"],
                payload["right_index"],
            )

        elif step_type == "split":
            self.playlist.highlight_merge_region(
                payload["left"],
                payload["right"],
            )

        elif step_type in {"take_left", "take_right"}:
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
                self.playlist.highlight_overwrite(row_index)

        elif step_type == "sorted_range":
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
        self.current_feature = self.DEFAULT_FEATURE
        self.original_songs = sample_songs(self.all_songs, sample_size)
        self.visual_songs = self.original_songs[:]
        self.song_lookup = {song.id: song for song in self.original_songs}
        self.header.set_feature(self.current_feature)
        self.header.set_dataset_size(len(self.original_songs))
        self.playlist.load_songs(self.visual_songs, feature=self.current_feature)
