from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QLabel,
    QHeaderView,
    QSizePolicy,
    QStackedLayout,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.models.song import Song
from src.presentation.helpers import set_transparent_surface
from src.presentation.merge_sort_visualizer import MergeSortVisualizer
from src.presentation.quick_sort_visualizer import QuickSortVisualizer


class PlaylistPanel(QFrame):
    DEFAULT_SELECTION_STYLESHEET = """
        QTableWidget::item:selected {
            background-color: #21242c;
            color: #f5f7fb;
            border: none;
        }
    """

    def __init__(self):
        super().__init__()
        self.setObjectName("Card")

        self.current_songs: list[Song] = []
        self.current_feature = "danceability"
        self.current_algorithm = "Merge Sort"
        self._highlighted_rows: set[int] = set()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.eyebrow = QLabel("Queue")
        self.eyebrow.setObjectName("Eyebrow")

        self.title = QLabel("Curated Playlist Workspace")
        self.title.setObjectName("SectionTitle")

        self.subtitle = QLabel("Full playlist preview with animation-ready row tracking.")
        self.subtitle.setObjectName("MutedText")
        self.subtitle.setWordWrap(True)

        self.summary_panel = QWidget()
        summary_layout = QGridLayout(self.summary_panel)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setHorizontalSpacing(10)
        summary_layout.setVerticalSpacing(10)

        self.dataset_summary = QLabel("Dataset Size: 25")
        self.dataset_summary.setObjectName("InfoChip")
        self.feature_summary = QLabel("Sort Feature: danceability")
        self.feature_summary.setObjectName("InfoChip")
        self.merge_summary = QLabel("Merge Sort Time: Pending")
        self.merge_summary.setObjectName("InfoChip")
        self.quick_summary = QLabel("Quick Sort Time: Pending")
        self.quick_summary.setObjectName("InfoChip")
        self.faster_summary = QLabel("Faster Algorithm: Pending")
        self.faster_summary.setObjectName("InfoChip")
        self.preview_summary = QLabel("Preview Rows: 25")
        self.preview_summary.setObjectName("InfoChip")

        summary_layout.addWidget(self.dataset_summary, 0, 0)
        summary_layout.addWidget(self.feature_summary, 0, 1)
        summary_layout.addWidget(self.merge_summary, 1, 0)
        summary_layout.addWidget(self.quick_summary, 1, 1)
        summary_layout.addWidget(self.faster_summary, 2, 0)
        summary_layout.addWidget(self.preview_summary, 2, 1)

        self.merge_visualizer = MergeSortVisualizer()
        self.quick_visualizer = QuickSortVisualizer()

        self.playback_stack = QWidget()
        self.playback_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        playback_stack_layout = QStackedLayout(self.playback_stack)
        playback_stack_layout.setContentsMargins(0, 0, 0, 0)
        playback_stack_layout.addWidget(self.merge_visualizer)
        playback_stack_layout.addWidget(self.quick_visualizer)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Track", "Artist", "Year", "Feature"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setWordWrap(False)
        self.table.setCornerButtonEnabled(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setStyleSheet(self.DEFAULT_SELECTION_STYLESHEET)

        layout.addWidget(self.eyebrow)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addWidget(self.summary_panel)
        layout.addWidget(self.playback_stack)
        layout.addWidget(self.table)

        set_transparent_surface(self.eyebrow, self.title, self.subtitle, self.summary_panel)
        self.set_workspace_mode(
            performance_mode=False,
            dataset_size=25,
            feature="danceability",
            algorithm="Merge Sort",
        )

    def begin_animation_highlighting(self) -> None:
        self.table.clearSelection()
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)

    def end_animation_highlighting(self) -> None:
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setStyleSheet(self.DEFAULT_SELECTION_STYLESHEET)

    def load_songs(self, songs: list[Song], feature: str = "danceability") -> None:
        self.current_songs = songs[:]
        self.current_feature = feature
        self._highlighted_rows.clear()

        self.table.setUpdatesEnabled(False)
        self.table.clearSelection()
        self.table.clearContents()
        self.table.setRowCount(len(songs))

        for row_index, song in enumerate(songs):
            self._write_song_to_row(row_index, song)
            self.table.setRowHeight(row_index, 54)

        self.table.resizeColumnsToContents()
        self.table.setUpdatesEnabled(True)
        self.merge_visualizer.reset_stage(self.current_songs, self.current_feature)
        self.quick_visualizer.reset_stage(self.current_songs, self.current_feature)

    def set_workspace_mode(
        self,
        performance_mode: bool,
        dataset_size: int,
        feature: str,
        algorithm: str = "Merge Sort",
        preview_limit: int | None = None,
    ) -> None:
        preview_rows = preview_limit if preview_limit is not None else dataset_size
        self.current_algorithm = algorithm
        self.dataset_summary.setText(f"Dataset Size: {dataset_size:,}")
        self.feature_summary.setText(f"Sort Feature: {feature}")
        self.preview_summary.setText(f"Preview Rows: {preview_rows:,}")

        if performance_mode:
            self.eyebrow.setText("Analysis")
            self.title.setText("Benchmark Workspace")
            self.subtitle.setText(
                "Large datasets use benchmark analysis with a preview table instead of step playback."
            )
            self.summary_panel.setVisible(True)
            self.playback_stack.setVisible(False)
            self.playback_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.table.setVisible(True)
            self.clear_benchmark_summary()
            return

        self.eyebrow.setText("Algorithm Playback")
        self.summary_panel.setVisible(False)
        self.playback_stack.setVisible(True)
        self.playback_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.table.setVisible(False)
        self.clear_benchmark_summary()

        if algorithm == "Quick Sort":
            self.title.setText("Quick Sort Playback")
            self.subtitle.setText(
                "See how the playlist is partitioned around pivots and reordered step by step."
            )
            self.playback_stack.layout().setCurrentWidget(self.quick_visualizer)
        else:
            self.title.setText("Merge Sort Playback")
            self.subtitle.setText(
                "See how the playlist is split into smaller groups and merged back in order."
            )
            self.playback_stack.layout().setCurrentWidget(self.merge_visualizer)

    def prepare_animation_stage(self, algorithm: str, songs: list[Song], feature: str) -> None:
        self.current_algorithm = algorithm
        if algorithm == "Quick Sort":
            self.quick_visualizer.reset_stage(songs, feature)
        else:
            self.merge_visualizer.reset_stage(songs, feature)

    def apply_animation_step(self, algorithm: str, step, songs: list[Song], feature: str) -> None:
        if algorithm == "Quick Sort":
            self.quick_visualizer.apply_step(step, songs, feature)
            return
        self.merge_visualizer.apply_step(step, songs, feature)

    def clear_benchmark_summary(self) -> None:
        self.merge_summary.setText("Merge Sort Time: Pending")
        self.quick_summary.setText("Quick Sort Time: Pending")
        self.faster_summary.setText("Faster Algorithm: Pending")

    def set_benchmark_summary(
        self,
        dataset_size: int,
        feature: str,
        preview_rows: int,
        merge_runtime_ms: int | None = None,
        quick_runtime_ms: int | None = None,
        quick_summary_text: str | None = None,
        faster_text: str | None = None,
    ) -> None:
        self.dataset_summary.setText(f"Dataset Size: {dataset_size:,}")
        self.feature_summary.setText(f"Sort Feature: {feature}")
        self.preview_summary.setText(f"Preview Rows: {preview_rows:,}")

        self.merge_summary.setText(
            self._format_runtime_label("Merge Sort Time", merge_runtime_ms)
        )
        self.quick_summary.setText(
            quick_summary_text
            if quick_summary_text is not None
            else self._format_runtime_label("Quick Sort Time", quick_runtime_ms)
        )

        faster_label = "Faster Algorithm: Pending"
        if merge_runtime_ms is not None and quick_runtime_ms is not None:
            if merge_runtime_ms < quick_runtime_ms:
                faster_label = "Faster Algorithm: Merge Sort"
            elif quick_runtime_ms < merge_runtime_ms:
                faster_label = "Faster Algorithm: Quick Sort"
            else:
                faster_label = "Faster Algorithm: Tie"

        if faster_text is not None:
            faster_label = faster_text

        self.faster_summary.setText(faster_label)

    def _write_song_to_row(self, row_index: int, song: Song) -> None:
        song_item = QTableWidgetItem(song.name)
        artist_item = QTableWidgetItem(song.artists)
        year_item = QTableWidgetItem(str(song.year))
        feature_item = QTableWidgetItem(f"{float(song.get_feature_value(self.current_feature)):.3f}")

        for item in (song_item, artist_item, year_item, feature_item):
            item.setForeground(QColor("#f5f7fb"))

        artist_item.setForeground(QColor("#b8bfd3"))
        year_item.setForeground(QColor("#9aa3bb"))
        feature_item.setForeground(QColor("#c7ffd8"))

        self.table.setItem(row_index, 0, song_item)
        self.table.setItem(row_index, 1, artist_item)
        self.table.setItem(row_index, 2, year_item)
        self.table.setItem(row_index, 3, feature_item)

    def clear_all_highlights(self) -> None:
        with QSignalBlocker(self.table):
            self.table.clearSelection()
        self.table.setStyleSheet(self.DEFAULT_SELECTION_STYLESHEET)
        rows_to_clear = self._highlighted_rows or set(range(self.table.rowCount()))
        for row in rows_to_clear:
            self._style_row(
                row=row,
                background=QColor(0, 0, 0, 0),
                foreground=QColor("#f5f7fb"),
                accent_foreground=QColor("#c7ffd8"),
                bold=False,
            )
        self._highlighted_rows.clear()

    def highlight_sorted_range(self, left: int, right: int) -> None:
        self.clear_all_highlights()
        sorted_color = "#166534"
        sorted_foreground = QColor("#ecfdf5")
        self._apply_selection_highlight(sorted_color, "#ecfdf5")

        for row in range(left, right + 1):
            self._apply_row_highlight(row, sorted_color, sorted_foreground, sorted_foreground, True)

    def update_song_at_index(self, row_index: int, song: Song) -> None:
        if 0 <= row_index < len(self.current_songs):
            self.current_songs[row_index] = song
            self._write_song_to_row(row_index, song)

    def _style_row(
        self,
        row: int,
        background: QColor,
        foreground: QColor,
        accent_foreground: QColor,
        bold: bool,
    ) -> None:
        if row < 0 or row >= self.table.rowCount():
            return

        base_font = self.table.font()
        styled_font = QFont(base_font)
        styled_font.setBold(bold)

        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item is not None:
                item.setBackground(QColor(background))
                item.setFont(styled_font)

                if col == 0:
                    item.setForeground(foreground)
                elif col == 3:
                    item.setForeground(accent_foreground)
                else:
                    item.setForeground(QColor(foreground))

    def _apply_row_highlight(
        self,
        row: int,
        background: str,
        foreground: QColor,
        accent_foreground: QColor,
        bold: bool,
    ) -> None:
        self._style_row(row, QColor(background), foreground, accent_foreground, bold)
        with QSignalBlocker(self.table):
            self.table.selectRow(row)
        self._highlighted_rows.add(row)

    def _apply_selection_highlight(self, background: str, foreground: str) -> None:
        self.table.setStyleSheet(
            f"""
            QTableWidget::item:selected {{
                background-color: {background};
                color: {foreground};
                border: none;
            }}
            """
        )

    def _format_runtime_label(self, label: str, runtime_ms: int | None) -> str:
        if runtime_ms is None:
            return f"{label}: Pending"
        return f"{label}: {runtime_ms / 1000:.2f}s"
