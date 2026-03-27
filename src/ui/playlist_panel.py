from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QLabel,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.models.song import Song


class PlaylistPanel(QFrame):
    DEFAULT_SELECTION_STYLESHEET = """
        QTableWidget::item:selected {
            background-color: #21242c;
            color: #f5f7fb;
            border-radius: 14px;
        }
    """

    def __init__(self):
        super().__init__()
        self.setObjectName("Card")

        self.current_songs: list[Song] = []
        self.current_feature = "danceability"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        eyebrow = QLabel("Queue")
        eyebrow.setObjectName("Eyebrow")

        title = QLabel("Curated Playlist Workspace")
        title.setObjectName("SectionTitle")

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

        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(self.table)

    def begin_animation_highlighting(self) -> None:
        self.table.clearSelection()
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)

    def end_animation_highlighting(self) -> None:
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setStyleSheet(self.DEFAULT_SELECTION_STYLESHEET)

    def load_songs(self, songs: list[Song], feature: str = "danceability") -> None:
        self.current_songs = songs[:]
        self.current_feature = feature

        self.table.setUpdatesEnabled(False)
        self.table.clearSelection()
        self.table.clearContents()
        self.table.setRowCount(len(songs))

        for row_index, song in enumerate(songs):
            self._write_song_to_row(row_index, song)
            self.table.setRowHeight(row_index, 54)

        self.table.resizeColumnsToContents()
        self.table.setUpdatesEnabled(True)

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
        self.table.setItem(
            row_index,
            3,
            feature_item
        )

    def clear_all_highlights(self) -> None:
        self.table.clearSelection()
        self.table.setStyleSheet(self.DEFAULT_SELECTION_STYLESHEET)
        for row in range(self.table.rowCount()):
            self._style_row(
                row=row,
                background=QColor(0, 0, 0, 0),
                foreground=QColor("#f5f7fb"),
                accent_foreground=QColor("#c7ffd8"),
                bold=False,
            )

    def highlight_compare(self, left_row: int, right_row: int) -> None:
        self.clear_all_highlights()
        compare_color = "#7c5d06"
        compare_foreground = QColor("#fff7cc")
        self._set_animation_selection_style(compare_color, "#fff7cc")
        self.table.selectRow(left_row)
        self.table.selectRow(right_row)
        self._style_row(left_row, compare_color, compare_foreground, compare_foreground, True)
        self._style_row(right_row, compare_color, compare_foreground, compare_foreground, True)

    def highlight_overwrite(self, row: int) -> None:
        self.clear_all_highlights()
        overwrite_color = "#174ea6"
        overwrite_foreground = QColor("#eff6ff")
        self._set_animation_selection_style(overwrite_color, "#eff6ff")
        self.table.selectRow(row)
        self._style_row(row, overwrite_color, overwrite_foreground, overwrite_foreground, True)

    def highlight_move(self, source_row: int, target_row: int) -> None:
        self.clear_all_highlights()
        move_color = "#4b5563"
        move_foreground = QColor("#f8fafc")
        self._set_animation_selection_style(move_color, "#f8fafc")
        self.table.selectRow(source_row)
        self.table.selectRow(target_row)
        self._style_row(source_row, move_color, move_foreground, move_foreground, True)
        self._style_row(target_row, move_color, move_foreground, QColor("#dbeafe"), True)

    def highlight_merge_region(self, left: int, right: int) -> None:
        self.clear_all_highlights()
        merge_color = "#5b2a86"
        merge_foreground = QColor("#f5e9ff")
        self._set_animation_selection_style(merge_color, "#f5e9ff")

        for row in range(left, right + 1):
            self.table.selectRow(row)
            self._style_row(row, merge_color, merge_foreground, merge_foreground, True)

    def highlight_sorted_range(self, left: int, right: int) -> None:
        self.clear_all_highlights()
        sorted_color = "#166534"
        sorted_foreground = QColor("#ecfdf5")
        self._set_animation_selection_style(sorted_color, "#ecfdf5")

        for row in range(left, right + 1):
            self.table.selectRow(row)
            self._style_row(row, sorted_color, sorted_foreground, sorted_foreground, True)

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

    def _set_animation_selection_style(self, background_color: str, foreground_color: str) -> None:
        self.table.setStyleSheet(
            f"""
            QTableWidget::item:selected {{
                background-color: {background_color};
                color: {foreground_color};
                border-radius: 14px;
            }}
            """
        )
