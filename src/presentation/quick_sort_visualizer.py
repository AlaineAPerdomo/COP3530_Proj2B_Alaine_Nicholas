from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.models.song import Song
from src.models.sort_step import SortStep
from src.presentation.helpers import set_transparent_surface
from src.presentation.song_card import SongCard


class QuickSortVisualizer(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("PlaybackStage")
        self.current_feature = "danceability"
        self.song_lookup: dict[str, Song] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        phase_row = QWidget()
        phase_layout = QHBoxLayout(phase_row)
        phase_layout.setContentsMargins(0, 0, 0, 0)
        phase_layout.setSpacing(8)
        for label_text in ("Choose Pivot", "Partition", "Recurse"):
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

        self.message = QLabel("Quick Sort playback ready.")
        self.message.setObjectName("MutedText")
        self.message.setWordWrap(True)

        self.current_segment = self._build_lane("Current Segment")
        buckets_row = QWidget()
        buckets_layout = QHBoxLayout(buckets_row)
        buckets_layout.setContentsMargins(0, 0, 0, 0)
        buckets_layout.setSpacing(14)

        self.less_lane = self._build_lane("Less Than Pivot")
        self.pivot_lane = self._build_lane("Pivot")
        self.greater_lane = self._build_lane("Greater Than Pivot")

        buckets_layout.addWidget(self.less_lane["frame"], 1)
        buckets_layout.addWidget(self.pivot_lane["frame"], 1)
        buckets_layout.addWidget(self.greater_lane["frame"], 1)

        self.preview_lane = self._build_lane("Partitioned Playlist")

        layout.addWidget(phase_row)
        layout.addWidget(controls_row)
        layout.addWidget(self.message)
        layout.addWidget(self.current_segment["frame"])
        layout.addWidget(buckets_row)
        layout.addWidget(self.preview_lane["frame"])

        set_transparent_surface(phase_row, controls_row, self.message, buckets_row)
        self.set_playback_state(0, 0, False, False)

    def reset_stage(self, songs: list[Song], feature: str) -> None:
        self.current_feature = feature
        self.song_lookup = {song.id: song for song in songs}
        preview = songs[:]

        self._populate_lane(self.current_segment, preview)
        self._populate_lane(self.less_lane, [])
        self._populate_lane(self.greater_lane, [])
        self._populate_lane(self.pivot_lane, [])
        self._populate_lane(self.preview_lane, preview)
        self.message.setText("Quick Sort playback ready.")
        self.set_playback_state(0, 0, False, False)

    def apply_step(self, step: SortStep, songs: list[Song], feature: str) -> None:
        self.current_feature = feature
        self.song_lookup = {song.id: song for song in songs}
        payload = step.payload
        left = payload.get("left", 0)
        right = payload.get("right", len(songs) - 1)

        current_segment = songs[left:right + 1] if songs else []
        less_songs = self._songs_from_ids(payload.get("less_song_ids", []))
        greater_songs = self._songs_from_ids(payload.get("greater_song_ids", []))
        pivot_song = self.song_lookup.get(payload.get("pivot_song_id", ""))

        self._populate_lane(
            self.current_segment,
            current_segment,
            highlight_ids=self._highlight_ids_for_step(step),
        )
        self._populate_lane(self.less_lane, less_songs)
        self._populate_lane(
            self.pivot_lane,
            [pivot_song] if pivot_song is not None else [],
            badge_text="Pivot",
            highlight_kind="pivot",
        )
        self._populate_lane(self.greater_lane, greater_songs)
        self._populate_lane(self.preview_lane, songs, highlight_ids=self._preview_highlight_ids(step))

        if step.step_type == "focus_segment":
            self.message.setText("Focusing the active segment for quick sort...")
        elif step.step_type == "choose_pivot":
            self.message.setText("Choosing the middle song as the pivot...")
        elif step.step_type == "compare":
            self.message.setText("Comparing the active songs around the pivot...")
        elif step.step_type == "swap":
            self.message.setText("Swapping songs to keep lower and higher partitions separated...")
        elif step.step_type == "move_left":
            self.message.setText("Sending the song into the left partition...")
        elif step.step_type == "move_right":
            self.message.setText("Sending the song into the right partition...")
        elif step.step_type == "place_pivot":
            self.message.setText("Placing the pivot into its final partition spot...")
        elif step.step_type == "partition_done":
            self.message.setText("Partition complete. Moving deeper into the next segment...")
        elif step.step_type == "final":
            self.message.setText("Quick Sort finished.")

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

    def _songs_from_ids(self, song_ids: list[str]) -> list[Song]:
        return [self.song_lookup[song_id] for song_id in song_ids if song_id in self.song_lookup]

    def _highlight_ids_for_step(self, step: SortStep) -> list[str]:
        payload = step.payload
        if step.step_type == "compare":
            return [payload.get("left_song_id", ""), payload.get("right_song_id", "")]
        if step.step_type in {"move_left", "move_right"}:
            return [payload.get("current_song_id", "")]
        if step.step_type == "place_pivot":
            return [payload.get("pivot_song_id", "")]
        return []

    def _preview_highlight_ids(self, step: SortStep) -> list[str]:
        payload = step.payload
        if step.step_type == "place_pivot":
            return [payload.get("pivot_song_id", "")]
        if step.step_type == "partition_done":
            return [payload.get("pivot_song_id", "")]
        return []

    def _build_lane(self, title_text: str) -> dict:
        frame = QFrame()
        frame.setObjectName("PlaybackLane")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel(title_text)
        title.setObjectName("SectionTitle")

        cards = QWidget()
        cards_layout = QHBoxLayout(cards)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(10)
        cards_layout.setAlignment(Qt.AlignLeft)

        empty = QLabel("Waiting for playback...")
        empty.setObjectName("MutedText")

        layout.addWidget(title)
        layout.addWidget(cards)
        layout.addWidget(empty)

        set_transparent_surface(title, cards, empty)
        return {"frame": frame, "layout": cards_layout, "empty": empty}

    def _populate_lane(
        self,
        lane: dict,
        songs: list[Song],
        badge_text: str = "",
        highlight_kind: str = "default",
        highlight_ids: list[str] | None = None,
    ) -> None:
        while lane["layout"].count():
            item = lane["layout"].takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        lane["empty"].setVisible(not songs)
        highlight_ids = highlight_ids or []

        for song in songs[:6]:
            card = SongCard()
            current_highlight = highlight_kind if song.id in highlight_ids or badge_text else "default"
            card.set_song(
                song,
                self.current_feature,
                highlight_kind=current_highlight,
                badge_text=badge_text,
                display_mode="sort_row",
            )
            lane["layout"].addWidget(card)

        lane["layout"].addStretch()
