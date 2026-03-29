from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.models.song import Song


class SongCard(QFrame):
    ROW_WIDTH = 760
    ROW_HEIGHT = 54
    CARD_WIDTH = 156
    CARD_HEIGHT = 84
    COMPACT_CARD_WIDTH = 164
    COMPACT_CARD_HEIGHT = 72
    SORT_ROW_WIDTH = 132
    SORT_ROW_HEIGHT = 62

    def __init__(self):
        super().__init__()
        self.setObjectName("SongCard")
        self._display_mode = "card"

        self.root_layout = QHBoxLayout(self)
        self.root_layout.setContentsMargins(12, 8, 12, 8)
        self.root_layout.setSpacing(10)

        self.left_column = QWidget()
        self.left_layout = QVBoxLayout(self.left_column)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(1)

        self.badge = QLabel("")
        self.badge.setObjectName("SongCardBadge")
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.hide()

        self.title = QLabel("")
        self.title.setObjectName("SongCardTitle")
        self.title.setWordWrap(True)

        self.meta = QLabel("")
        self.meta.setObjectName("SongCardMeta")
        self.meta.setWordWrap(True)

        self.left_layout.addWidget(self.badge)
        self.left_layout.addWidget(self.title)
        self.left_layout.addWidget(self.meta)

        self.artist = QLabel("")
        self.artist.setObjectName("SongCardMeta")
        self.artist.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.year = QLabel("")
        self.year.setObjectName("SongCardYear")
        self.year.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.feature_value = QLabel("")
        self.feature_value.setObjectName("SongCardFeature")
        self.feature_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.root_layout.addWidget(self.left_column, 1)
        self.root_layout.addWidget(self.artist, 1)
        self.root_layout.addWidget(self.year, 0)
        self.root_layout.addWidget(self.feature_value, 0)

        self.set_display_mode("card")

    def set_song(
        self,
        song: Song,
        feature: str,
        highlight_kind: str = "default",
        badge_text: str = "",
        display_mode: str | None = None,
    ) -> None:
        if display_mode is not None:
            self.set_display_mode(display_mode)

        title_width = self._text_width_for(self.title)
        meta_width = self._text_width_for(self.meta)
        artist_width = self._text_width_for(self.artist)

        self.title.setText(self._elide_text(self.title, song.name, title_width))
        if self._display_mode == "row":
            self.meta.setText(self._elide_text(self.meta, song.artists, meta_width))
        else:
            self.meta.setText(f"{float(song.get_feature_value(feature)):.3f}")
        self.artist.setText(self._elide_text(self.artist, song.artists, artist_width))
        self.year.setText(str(song.year))
        if self._display_mode == "row":
            self.feature_value.setText(f"{float(song.get_feature_value(feature)):.3f}")
        else:
            self.feature_value.setText("")

        self.setProperty("highlightKind", highlight_kind)
        if badge_text:
            self.badge.setText(badge_text)
            self.badge.show()
        else:
            self.badge.hide()

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_display_mode(self, display_mode: str) -> None:
        self._display_mode = display_mode
        is_row = display_mode == "row"
        is_compact = display_mode == "compact_card"
        is_sort_row = display_mode == "sort_row"
        self.setProperty("displayMode", display_mode)

        if is_row:
            self.setFixedSize(self.ROW_WIDTH, self.ROW_HEIGHT)
            self.left_column.show()
            self.artist.show()
            self.year.show()
            self.badge.hide()
            self.meta.hide()
            self.title.setWordWrap(False)
            self.artist.setWordWrap(False)
            self.root_layout.setContentsMargins(12, 8, 12, 8)
            self.root_layout.setSpacing(10)
            self.left_layout.setSpacing(1)
            self._apply_font(self.title, 12, QFont.Weight.Bold)
            self._apply_font(self.meta, 11, QFont.Weight.Normal)
        else:
            if is_sort_row:
                self.setFixedSize(self.SORT_ROW_WIDTH, self.SORT_ROW_HEIGHT)
            elif is_compact:
                self.setFixedSize(self.COMPACT_CARD_WIDTH, self.COMPACT_CARD_HEIGHT)
            else:
                self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)
            self.left_column.show()
            self.artist.hide()
            self.year.hide()
            self.meta.setVisible(True)
            self.feature_value.setVisible(False)
            self.title.setWordWrap(False)
            self.artist.setWordWrap(False)
            if is_compact or is_sort_row:
                self.badge.hide()
            if is_sort_row:
                self.root_layout.setContentsMargins(9, 7, 9, 7)
                self.root_layout.setSpacing(0)
                self.left_layout.setSpacing(0)
                self._apply_font(self.title, 11, QFont.Weight.Bold)
                self._apply_font(self.meta, 10, QFont.Weight.Medium)
            else:
                self.root_layout.setContentsMargins(12, 8, 12, 8)
                self.root_layout.setSpacing(10)
                self.left_layout.setSpacing(1)
                self._apply_font(self.title, 12, QFont.Weight.Bold)
                self._apply_font(self.meta, 11, QFont.Weight.Normal)

        self._sync_text_heights()

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def display_mode(self) -> str:
        return self._display_mode

    def _text_width_for(self, label: QLabel) -> int:
        if self._display_mode == "row":
            if label is self.title:
                return 280
            if label is self.meta or label is self.artist:
                return 180
        if self._display_mode == "compact_card":
            if label is self.title:
                return 148
            if label is self.meta:
                return 148
        if self._display_mode == "sort_row":
            if label is self.title:
                return 112
            if label is self.meta:
                return 112
        if label is self.title:
            return 132
        if label is self.meta:
            return 132
        return 120

    def _elide_text(self, label: QLabel, text: str, width: int) -> str:
        metrics = QFontMetrics(label.font())
        return metrics.elidedText(text, Qt.ElideRight, width)

    def _apply_font(self, label: QLabel, point_size: int, weight: QFont.Weight) -> None:
        font = QFont(label.font())
        font.setPointSize(point_size)
        font.setWeight(weight)
        label.setFont(font)

    def _sync_text_heights(self) -> None:
        title_metrics = QFontMetrics(self.title.font())
        meta_metrics = QFontMetrics(self.meta.font())
        self.title.setFixedHeight(title_metrics.height())
        self.meta.setFixedHeight(meta_metrics.height())
