from math import ceil, log2

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QTimer, Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.models.song import Song
from src.models.sort_step import SortStep
from src.presentation.helpers import set_transparent_surface
from src.presentation.song_card import SongCard


class MergeSortCanvas(QWidget):
    CANVAS_W = 900
    CANVAS_H = 600

    Y_TOP = 82
    SORT_ROW_Y = 132

    TREE_START_Y = 218
    DEPTH_GAP = 54
    MERGE_GAP = 70

    CENTER_X = 450
    CARD_GAP = 16
    ROW_GAP = 10
    SORT_ROW_GAP = 10

    TREE_MARGIN_X = 130
    WORK_LEFT_X = 285
    WORK_RIGHT_X = 615

    LABEL_OFFSET_Y = 30
    LABEL_ROW_GAP = 14

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(self.CANVAS_H)
        self.setObjectName("MergeSortCanvas")
        self.feature = "danceability"
        self.cards: dict[str, SongCard] = {}
        self.snapshot_groups: dict[tuple[int, int], list[SongCard]] = {}
        self.home_rects: dict[str, QRect] = {}
        self.visible_song_ids: list[str] = []
        self._animations: list[QPropertyAnimation] = []
        self._merged_song_ids: list[str] = []
        self.total_song_count = 0
        self.max_depth = 0

        self.current_label = self._make_label("Playlist")
        self.left_label = self._make_label("Sorting Left")
        self.right_label = self._make_label("Sorting Right")
        self.merge_label = self._make_label("Merged Result")

        self._move_chip_centered(self.current_label, self.CENTER_X, 18)
        self.left_label.hide()
        self.right_label.hide()
        self.merge_label.hide()

    def reset_stage(self, songs: list[Song], feature: str) -> None:
        self.feature = feature
        preview = songs[:]
        self.total_song_count = len(preview)
        self.max_depth = max(1, ceil(log2(max(1, len(preview)))))
        stage_bottom = self._final_sorted_row_y() + SongCard.SORT_ROW_HEIGHT + 32
        stage_height = max(self.CANVAS_H, stage_bottom)
        self.setMinimumHeight(stage_height)
        self.setMaximumHeight(stage_height)

        self._clear_snapshots()
        self.home_rects.clear()
        self._merged_song_ids = []
        self._show_cards(preview)

        rects = self._stack_rects(len(preview))
        for song, rect in zip(preview, rects):
            card = self.cards[song.id]
            card.set_song(song, feature, highlight_kind="default", display_mode="row")
            card.setGeometry(rect)
            card.show()
            self.home_rects[song.id] = QRect(rect)

        self.current_label.show()
        self.current_label.setText("Playlist")
        self._move_chip_centered(self.current_label, self.CENTER_X, 18)
        self.left_label.hide()
        self.right_label.hide()
        self.merge_label.hide()

    def apply_step(self, step: SortStep, songs: list[Song], feature: str) -> None:
        self.feature = feature
        payload = step.payload
        segment_left = payload.get("merge_left", payload.get("left", 0))
        segment_mid = payload.get("merge_mid", payload.get("mid", segment_left))
        segment_right = payload.get("merge_right", payload.get("right", segment_mid))
        depth = payload.get("depth", 0)

        active_songs = songs[segment_left:segment_right + 1]
        left_songs = songs[segment_left:segment_mid + 1]
        right_songs = songs[segment_mid + 1:segment_right + 1]
        merged_songs: list[Song] = []
        segment_key = (segment_left, segment_right)

        if step.step_type == "write":
            merged_songs = songs[
                segment_left:payload.get("index", payload.get("target_index", segment_left)) + 1
            ]
        elif step.step_type in {"merge_complete", "final"}:
            merged_songs = songs[segment_left:segment_right + 1]

        self._show_cards(active_songs, left_songs, right_songs, merged_songs)

        if step.step_type == "focus_segment":
            self._clear_snapshots()
            self.current_label.show()
            self.current_label.setText("Current Segment")
            self._move_chip_above_row(self.current_label, self.CENTER_X, self.SORT_ROW_Y)
            self.left_label.hide()
            self.right_label.hide()
            self.merge_label.hide()

            self._animate_sort_row(
                active_songs,
                highlight_song_ids=[song.id for song in active_songs],
                kind="active",
            )
            return

        if step.step_type == "split":
            self._clear_snapshots()

            self.current_label.show()
            self.current_label.setText("Split Stage")
            self._move_chip_above_row(self.current_label, self.CENTER_X, self._branch_y(depth))
            self.left_label.hide()
            self.right_label.hide()
            self.merge_label.hide()

            # keep the parent row visible as context
            self._animate_sort_row(active_songs, kind="default")

            branch_y = self._branch_y(depth)
            self._animate_card_row(
                left_songs,
                self._segment_center_x(segment_left, segment_mid),
                branch_y,
                kind="default",
                duration=420,
            )
            self._animate_card_row(
                right_songs,
                self._segment_center_x(segment_mid + 1, segment_right),
                branch_y,
                kind="default",
                duration=420,
            )
            return

        if step.step_type == "merge_focus":
            work_y = self._workspace_branch_y()

            self.current_label.show()
            self.current_label.setText("Active Merge")
            self._move_chip_above_row(self.current_label, self.CENTER_X, work_y)

            self.left_label.show()
            self.right_label.show()
            self.merge_label.hide()

            self._move_chip_above_row(self.left_label, self.WORK_LEFT_X, work_y)
            self._move_chip_above_row(self.right_label, self.WORK_RIGHT_X, work_y)

            self._position_live_from_row(left_songs, self.WORK_LEFT_X, work_y)
            self._position_live_from_row(right_songs, self.WORK_RIGHT_X, work_y)

            self._animate_card_row(
                left_songs,
                self.WORK_LEFT_X,
                work_y,
                kind="active",
                duration=420,
            )
            self._animate_card_row(
                right_songs,
                self.WORK_RIGHT_X,
                work_y,
                kind="active",
                duration=420,
            )
            return

        if step.step_type == "compare":
            compare_ids = []
            left_index = payload["left_index"] - segment_left
            right_index = payload["right_index"] - (segment_mid + 1)

            if 0 <= left_index < len(left_songs):
                compare_ids.append(left_songs[left_index].id)
            if 0 <= right_index < len(right_songs):
                compare_ids.append(right_songs[right_index].id)

            branch_y = self._workspace_branch_y()
            self._animate_card_row(
                left_songs,
                self.WORK_LEFT_X,
                branch_y,
                highlight_song_ids=compare_ids,
                kind="active",
                lift_ids=compare_ids,
                duration=240,
            )
            self._animate_card_row(
                right_songs,
                self.WORK_RIGHT_X,
                branch_y,
                highlight_song_ids=compare_ids,
                kind="active",
                lift_ids=compare_ids,
                duration=240,
            )
            return

        if step.step_type == "write":
            self._merged_song_ids = [song.id for song in merged_songs]
            branch_y = self._workspace_branch_y()
            merge_y = self._workspace_merge_y()

            self.current_label.hide()
            self.left_label.show()
            self.right_label.show()
            self.merge_label.show()

            self._move_chip_above_row(self.left_label, self.WORK_LEFT_X, branch_y)
            self._move_chip_above_row(self.right_label, self.WORK_RIGHT_X, branch_y)
            self._move_chip_above_row(self.merge_label, self.CENTER_X, merge_y)

            self._animate_card_row(
                left_songs,
                self.WORK_LEFT_X,
                branch_y,
                duration=300,
            )
            self._animate_card_row(
                right_songs,
                self.WORK_RIGHT_X,
                branch_y,
                duration=300,
            )
            self._animate_card_row(
                merged_songs,
                self.CENTER_X,
                merge_y,
                highlight_song_ids=self._merged_song_ids[-1:],
                kind="active",
                duration=360,
            )
            return

        if step.step_type in {"merge_complete", "final"}:
            sorted_songs = songs[segment_left:segment_right + 1]
            sorted_ids = [song.id for song in sorted_songs]
            is_root_merge = segment_left == 0 and segment_right == self.total_song_count - 1

            target_rects = (
                self._final_sorted_row_rects(len(sorted_songs))
                if is_root_merge
                else self._sort_row_rects(len(sorted_songs))
            )

            self._clear_snapshots()
            self._upsert_snapshot_group(
                segment_key,
                sorted_songs,
                target_rects,
                "sort_row",
                kind="sorted",
            )

            if step.step_type == "merge_complete":
                self.current_label.show()
                self.current_label.setText("Merged Segment")
                label_center_x = self.CENTER_X
                label_y = (
                    self._label_y_for_row(self._final_sorted_row_y())
                    if is_root_merge
                    else self._label_y_for_row(self.SORT_ROW_Y)
                )
                self._move_chip_centered(self.current_label, label_center_x, label_y)

                self.left_label.hide()
                self.right_label.hide()
                self.merge_label.hide()

                source_y = self._workspace_merge_y() if len(sorted_songs) > 1 else self._workspace_branch_y()
                self._position_live_from_row(sorted_songs, self.CENTER_X, source_y)

                for song, rect in zip(sorted_songs, target_rects):
                    card = self.cards[song.id]
                    card.set_song(
                        song,
                        self.feature,
                        highlight_kind="sorted",
                        display_mode="sort_row",
                    )
                    self._animate_card(card, rect, 400)
                    self.home_rects[song.id] = QRect(rect)
                return

            self.current_label.show()
            self.current_label.setText("Playlist")
            self._move_chip_centered(self.current_label, self.CENTER_X, 18)
            self.left_label.hide()
            self.right_label.hide()
            self.merge_label.hide()
            self._animate_stack(
                sorted_songs,
                highlight_song_ids=sorted_ids,
                kind="sorted",
            )
            return

    def _make_label(self, text: str) -> QLabel:
        label = QLabel(text, self)
        label.setObjectName("StageChip")
        label.setAlignment(Qt.AlignCenter)
        self._resize_stage_chip(label)
        label.hide()
        return label

    def _move_chip_centered(self, label: QLabel, center_x: int, y: int) -> None:
        self._resize_stage_chip(label)
        label.move(int(center_x - (label.width() / 2)), y)

    def _move_chip_above_row(self, label: QLabel, center_x: int, row_y: int) -> None:
        self._move_chip_centered(label, center_x, self._label_y_for_row(row_y))

    def _label_y_for_row(self, row_y: int) -> int:
        self._resize_stage_chip(self.current_label)
        return row_y - self.current_label.height() - self.LABEL_ROW_GAP

    def _resize_stage_chip(self, label: QLabel) -> None:
        label.style().unpolish(label)
        label.style().polish(label)
        label.ensurePolished()
        metrics = QFontMetrics(label.font())
        text_width = metrics.horizontalAdvance(label.text())
        text_height = metrics.height()
        label.resize(max(140, text_width + 52), max(40, text_height + 18))

    def _clear_snapshots(self) -> None:
        for cards in self.snapshot_groups.values():
            for card in cards:
                card.hide()
                card.deleteLater()
        self.snapshot_groups.clear()

    def _upsert_snapshot_group(
        self,
        key: tuple[int, int],
        songs: list[Song],
        rects: list[QRect],
        display_mode: str,
        kind: str = "default",
        visible: bool = True,
    ) -> None:
        self._remove_snapshot_group(key)
        cards: list[SongCard] = []
        for song, rect in zip(songs, rects):
            snapshot = SongCard()
            snapshot.setParent(self)
            snapshot.set_song(song, self.feature, highlight_kind=kind, display_mode=display_mode)
            snapshot.setGeometry(rect)
            if visible:
                snapshot.show()
            else:
                snapshot.hide()
            snapshot.lower()
            cards.append(snapshot)
            self.home_rects[song.id] = QRect(rect)
        self.snapshot_groups[key] = cards

    def _remove_snapshot_group(self, key: tuple[int, int]) -> None:
        cards = self.snapshot_groups.pop(key, [])
        for card in cards:
            card.hide()
            card.deleteLater()

    def _show_cards(self, *song_groups: list[Song]) -> None:
        ordered_songs: list[Song] = []
        seen_song_ids: set[str] = set()

        for group in song_groups:
            for song in group:
                if song.id in seen_song_ids:
                    continue
                ordered_songs.append(song)
                seen_song_ids.add(song.id)

        self.visible_song_ids = [song.id for song in ordered_songs]

        for song in ordered_songs:
            if song.id not in self.cards:
                self.cards[song.id] = SongCard()
                self.cards[song.id].setParent(self)
            self.cards[song.id].set_song(song, self.feature)
            self.cards[song.id].show()
            self.cards[song.id].raise_()

        for song_id, card in self.cards.items():
            if song_id not in self.visible_song_ids:
                card.hide()

    def _card_row_rects(
        self,
        center_x: int,
        y: int,
        count: int,
        lift_indexes: set[int] | None = None,
    ) -> list[QRect]:
        if count <= 0:
            return []

        card_width = SongCard.SORT_ROW_WIDTH
        card_height = SongCard.SORT_ROW_HEIGHT
        gap = self.SORT_ROW_GAP
        total_width = count * card_width + (count - 1) * gap
        start_x = int(center_x - total_width / 2)

        lift_indexes = lift_indexes or set()

        rects: list[QRect] = []
        for index in range(count):
            lift_y = y - 10 if index in lift_indexes else y
            rects.append(
                QRect(
                    start_x + index * (card_width + gap),
                    lift_y,
                    card_width,
                    card_height,
                )
            )
        return rects

    def _stack_rects(self, count: int) -> list[QRect]:
        if count <= 0:
            return []
        start_x = int(self.CENTER_X - SongCard.ROW_WIDTH / 2)
        return [
            QRect(
                start_x,
                self.Y_TOP + index * (SongCard.ROW_HEIGHT + self.ROW_GAP),
                SongCard.ROW_WIDTH,
                SongCard.ROW_HEIGHT,
            )
            for index in range(count)
        ]

    def _branch_y(self, depth: int) -> int:
        return self.TREE_START_Y + (depth * self.DEPTH_GAP)

    def _workspace_branch_y(self) -> int:
        return self._branch_y(self.max_depth) + 42

    def _workspace_merge_y(self) -> int:
        return self._workspace_branch_y() + 112

    def _final_sorted_row_y(self) -> int:
        return self._workspace_merge_y() + 104

    def _segment_center_x(self, left: int, right: int) -> int:
        if self.total_song_count <= 0:
            return self.CENTER_X
        total_width = self.CANVAS_W - (2 * self.TREE_MARGIN_X)
        midpoint = (left + right + 1) / 2
        ratio = midpoint / self.total_song_count
        return int(self.TREE_MARGIN_X + (ratio * total_width))

    def _final_sorted_row_rects(self, count: int) -> list[QRect]:
        if count <= 0:
            return []
        card_width = SongCard.SORT_ROW_WIDTH
        card_height = SongCard.SORT_ROW_HEIGHT
        total_width = count * card_width + (count - 1) * self.SORT_ROW_GAP
        start_x = int(self.CENTER_X - total_width / 2)
        return [
            QRect(
                start_x + index * (card_width + self.SORT_ROW_GAP),
                self._final_sorted_row_y(),
                card_width,
                card_height,
            )
            for index in range(count)
        ]

    def _position_live_from_row(self, songs: list[Song], center_x: int, y: int) -> None:
        rects = self._card_row_rects(center_x, y, len(songs))
        for song, rect in zip(songs, rects):
            card = self.cards[song.id]
            card.setGeometry(rect)
            card.show()
            card.raise_()

    def _animate_stack(
        self,
        songs: list[Song],
        highlight_song_ids: list[str] | None = None,
        kind: str = "default",
    ) -> None:
        rects = self._stack_rects(len(songs))
        highlight_song_ids = highlight_song_ids or []

        for index, (song, rect) in enumerate(zip(songs, rects)):
            card = self.cards[song.id]
            highlight_kind = kind if song.id in highlight_song_ids else "default"
            card.set_song(song, self.feature, highlight_kind=highlight_kind, display_mode="row")
            self._animate_card(card, rect, 300 + index * 18)
            self.home_rects[song.id] = QRect(rect)

    def _sort_row_rects(self, count: int) -> list[QRect]:
        if count <= 0:
            return []
        card_width = SongCard.SORT_ROW_WIDTH
        card_height = SongCard.SORT_ROW_HEIGHT
        total_width = count * card_width + (count - 1) * self.SORT_ROW_GAP
        start_x = int(self.CENTER_X - total_width / 2)
        return [
            QRect(
                start_x + index * (card_width + self.SORT_ROW_GAP),
                self.SORT_ROW_Y,
                card_width,
                card_height,
            )
            for index in range(count)
        ]

    def _animate_sort_row(
        self,
        songs: list[Song],
        highlight_song_ids: list[str] | None = None,
        kind: str = "default",
    ) -> None:
        rects = self._sort_row_rects(len(songs))
        highlight_song_ids = highlight_song_ids or []

        for index, (song, rect) in enumerate(zip(songs, rects)):
            card = self.cards[song.id]
            highlight_kind = kind if song.id in highlight_song_ids else "default"
            card.set_song(song, self.feature, highlight_kind=highlight_kind, display_mode="sort_row")
            self._animate_card(card, rect, 360 + index * 16)

    def _animate_card_row(
        self,
        songs: list[Song],
        center_x: int,
        y: int,
        highlight_song_ids: list[str] | None = None,
        kind: str = "default",
        lift_ids: list[str] | None = None,
        duration: int = 340,
    ) -> None:
        highlight_song_ids = highlight_song_ids or []
        lift_ids = lift_ids or []
        lift_indexes = {
            index for index, song in enumerate(songs) if song.id in lift_ids
        }
        rects = self._card_row_rects(center_x, y, len(songs), lift_indexes)

        for index, (song, rect) in enumerate(zip(songs, rects)):
            card = self.cards[song.id]
            highlight_kind = kind if song.id in highlight_song_ids else "default"
            card.set_song(song, self.feature, highlight_kind=highlight_kind, display_mode="sort_row")
            self._animate_card(card, rect, duration + index * 18)

    def _animate_card(self, card: SongCard, target: QRect, duration: int = 320) -> None:
        animation = QPropertyAnimation(card, b"geometry", self)
        animation.setDuration(duration)
        animation.setStartValue(card.geometry())
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.finished.connect(
            lambda a=animation: self._animations.remove(a) if a in self._animations else None
        )
        self._animations.append(animation)
        animation.start()


class MergeSortVisualizer(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("PlaybackStage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(10)

        phase_row = QWidget()
        phase_layout = QHBoxLayout(phase_row)
        phase_layout.setContentsMargins(0, 0, 0, 0)
        phase_layout.setSpacing(8)

        for label_text in ("Split", "Compare", "Merge"):
            chip = QLabel(label_text)
            chip.setObjectName("PlaybackChip")
            phase_layout.addWidget(chip)
        phase_layout.addStretch()

        controls_row = QWidget()
        controls_layout = QHBoxLayout(controls_row)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)

        self.back_button = QPushButton("⏮")
        self.back_button.setObjectName("SecondaryButton")
        self.back_button.setToolTip("Go back one stage")
        self.back_button.setFixedWidth(72)

        self.play_pause_button = QPushButton("▶")
        self.play_pause_button.setObjectName("PrimaryButton")
        self.play_pause_button.setToolTip("Play full animation")
        self.play_pause_button.setFixedWidth(72)

        self.next_button = QPushButton("⏭")
        self.next_button.setObjectName("SecondaryButton")
        self.next_button.setToolTip("Advance one stage")
        self.next_button.setFixedWidth(72)

        self.step_counter = QLabel("0 / 0")
        self.step_counter.setObjectName("InfoChip")

        controls_layout.addWidget(self.back_button)
        controls_layout.addWidget(self.play_pause_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addWidget(self.step_counter)
        controls_layout.addStretch()

        self.action_label = QLabel("Initial playlist ready for playback.")
        self.action_label.setObjectName("MutedText")
        self.action_label.setWordWrap(True)

        self.canvas = MergeSortCanvas()

        layout.addWidget(phase_row)
        layout.addWidget(controls_row)
        layout.addWidget(self.action_label)
        layout.addWidget(self.canvas)

        set_transparent_surface(phase_row, controls_row, self.action_label)
        self.set_playback_state(current_step=0, total_steps=0, is_playing=False, ready=False)

    def reset_stage(self, songs: list[Song], feature: str) -> None:
        self.canvas.reset_stage(songs, feature)
        self.action_label.setText("Initial playlist ready for playback.")
        self.set_playback_state(current_step=0, total_steps=0, is_playing=False, ready=False)

    def apply_step(self, step: SortStep, songs: list[Song], feature: str) -> None:
        if step.step_type == "focus_segment":
            self.action_label.setText("Preparing playlist for merge sort...")
        elif step.step_type == "split":
            self.action_label.setText("Splitting the current row into left and right halves...")
        elif step.step_type == "merge_focus":
            self.action_label.setText("Moving the active halves into the merge workspace...")
        elif step.step_type == "compare":
            self.action_label.setText("Comparing front songs...")
        elif step.step_type == "write":
            self.action_label.setText("Writing the chosen song into the merged row...")
        elif step.step_type == "merge_complete":
            self.action_label.setText("Merged segment completed.")
        elif step.step_type == "final":
            self.action_label.setText("Playlist optimized.")

        self.canvas.apply_step(step, songs, feature)

    def set_playback_state(
        self,
        current_step: int,
        total_steps: int,
        is_playing: bool,
        ready: bool,
    ) -> None:
        self.back_button.setEnabled(ready and current_step > 0 and not is_playing)
        self.play_pause_button.setEnabled(ready and total_steps > 0 and current_step < total_steps)
        self.play_pause_button.setText("⏸" if is_playing else "▶")
        self.play_pause_button.setToolTip("Pause animation" if is_playing else "Play full animation")
        self.next_button.setEnabled(ready and current_step < total_steps and not is_playing)
        self.step_counter.setText(f"{current_step} / {total_steps}")
