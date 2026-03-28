import os
import tempfile
from math import pi

os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

from src.data.similarity import rank_similar_songs
from src.models.song import Song
from src.presentation.helpers import set_transparent_surface
from src.utils.constants import RADAR_FEATURES


class RadarChartCanvas(FigureCanvasQTAgg):
    LABELS = {
        "danceability": "Dance",
        "energy": "Energy",
        "valence": "Valence",
        "acousticness": "Acoustic",
        "speechiness": "Speech",
        "tempo": "Tempo",
    }

    def __init__(self):
        self.figure = Figure(figsize=(3.0, 2.7), facecolor="#171718")
        self.axis = self.figure.add_subplot(111, polar=True)
        super().__init__(self.figure)
        self.setStyleSheet("background: transparent;")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(232, 214)
        self._angles = [
            angle for angle in [index * (2 * pi / len(RADAR_FEATURES)) for index in range(len(RADAR_FEATURES))]
        ]
        self._angles.append(self._angles[0])
        self._configure_axis()

    def _configure_axis(self) -> None:
        self.axis.set_facecolor("#171718")
        self.axis.set_ylim(0, 1)
        self.axis.set_yticks([0.25, 0.5, 0.75, 1.0])
        self.axis.set_yticklabels([])
        self.axis.grid(color="#2d3748", alpha=0.9, linewidth=0.8)
        self.axis.spines["polar"].set_color("#334155")
        self.axis.set_xticks(self._angles[:-1])
        self.axis.set_xticklabels([self.LABELS[feature] for feature in RADAR_FEATURES])
        self.axis.tick_params(axis="x", colors="#cbd5e1", labelsize=7, pad=6)
        self.axis.set_position([0.20, 0.18, 0.60, 0.60])

    def plot_profile(self, profile: dict[str, float]) -> None:
        values = [profile[feature] for feature in RADAR_FEATURES]
        values.append(values[0])

        self.axis.clear()
        self._configure_axis()
        self.axis.plot(self._angles, values, color="#ff5d7a", linewidth=2.4)
        self.axis.fill(self._angles, values, color="#2f7dff", alpha=0.24)
        self.draw_idle()


class DetailPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("DetailPanel")
        self.setMinimumWidth(350)
        self.setMaximumWidth(430)

        self.all_songs: list[Song] = []
        self.current_song: Song | None = None
        self.slider_rows: dict[str, dict] = {}

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("DetailScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("DetailScrollContent")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Now Inspecting")
        title.setObjectName("SectionTitle")

        subtitle = QLabel("A closer look at the song currently in focus.")
        subtitle.setObjectName("MutedText")
        subtitle.setWordWrap(True)

        self.radar_chart = RadarChartCanvas()

        chart_row = QWidget()
        chart_layout = QHBoxLayout(chart_row)
        chart_layout.setContentsMargins(6, 0, 6, 0)
        chart_layout.addStretch()
        chart_layout.addWidget(self.radar_chart, 0, Qt.AlignHCenter)
        chart_layout.addStretch()

        self.song_name = QLabel("Select a song")
        self.song_name.setObjectName("HeroSubtitle")
        self.song_name.setWordWrap(True)

        self.song_meta = QLabel("Artist • Year")
        self.song_meta.setObjectName("MutedText")
        self.song_meta.setWordWrap(True)

        self.state_label = QLabel("Role: Not active")
        self.state_label.setObjectName("StatusBadge")

        stat_row = QWidget()
        stat_layout = QHBoxLayout(stat_row)
        stat_layout.setContentsMargins(0, 0, 0, 0)
        stat_layout.setSpacing(10)

        self.duration_chip = QLabel("0:00")
        self.duration_chip.setObjectName("InfoChip")
        self.explicit_chip = QLabel("Clean")
        self.explicit_chip.setObjectName("InfoChip")
        stat_layout.addWidget(self.duration_chip)
        stat_layout.addWidget(self.explicit_chip)
        stat_layout.addStretch()

        slider_title = QLabel("Adjust Sound Profile")
        slider_title.setObjectName("SectionTitle")

        slider_subtitle = QLabel("Adjust the core audio traits and see the profile change live.")
        slider_subtitle.setObjectName("MutedText")
        slider_subtitle.setWordWrap(True)

        slider_panel = QWidget()
        slider_layout = QVBoxLayout(slider_panel)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.setSpacing(10)

        for feature in RADAR_FEATURES:
            row = self._make_slider_row(feature)
            self.slider_rows[feature] = row
            slider_layout.addWidget(row["container"])

        similar_title = QLabel("Similar Songs")
        similar_title.setObjectName("SectionTitle")

        self.similar_list = QListWidget()
        self.similar_list.setObjectName("SimilarSongsList")
        self.similar_list.setMinimumHeight(180)
        self.similar_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.similar_list.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(chart_row)
        layout.addWidget(self.song_name)
        layout.addWidget(self.song_meta)
        layout.addWidget(self.state_label)
        layout.addWidget(stat_row)
        layout.addWidget(slider_title)
        layout.addWidget(slider_subtitle)
        layout.addWidget(slider_panel)
        layout.addWidget(similar_title)
        layout.addWidget(self.similar_list)

        layout.addStretch()
        set_transparent_surface(
            title,
            subtitle,
            chart_row,
            self.song_name,
            self.song_meta,
            stat_row,
            slider_title,
            slider_subtitle,
            slider_panel,
            similar_title,
        )
        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area)
        self._set_controls_enabled(False)
        self.radar_chart.plot_profile({feature: 0.0 for feature in RADAR_FEATURES})
        self.set_layout_mode(performance_mode=False)

    def set_layout_mode(self, performance_mode: bool) -> None:
        self.setMinimumWidth(350 if performance_mode else 390)
        self.setMaximumWidth(430 if performance_mode else 500)

    def set_song_catalog(self, songs: list[Song]) -> None:
        self.all_songs = songs[:]

    def reset_view(self) -> None:
        self.current_song = None
        self.song_name.setText("Select a song")
        self.song_meta.setText("Artist • Year")
        self.state_label.setText("Role: Not active")
        self.duration_chip.setText("0:00")
        self.explicit_chip.setText("Clean")

        for feature, row in self.slider_rows.items():
            slider = row["slider"]
            with QSignalBlocker(slider):
                slider.setValue(0)
            row["value"].setText("0%")

        self.similar_list.clear()
        self._set_controls_enabled(False)
        self.radar_chart.plot_profile({feature: 0.0 for feature in RADAR_FEATURES})

    def _make_slider_row(self, feature_name: str) -> dict:
        container = QWidget()
        row_layout = QVBoxLayout(container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        label = QLabel(feature_name.title())
        label.setObjectName("MetricLabel")

        value = QLabel("0%")
        value.setObjectName("MutedText")
        set_transparent_surface(container, header, label, value)

        header_layout.addWidget(label)
        header_layout.addStretch()
        header_layout.addWidget(value)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.valueChanged.connect(self._handle_slider_change)

        row_layout.addWidget(header)
        row_layout.addWidget(slider)

        return {"container": container, "slider": slider, "value": value}

    def update_song(self, song: Song) -> None:
        self.current_song = song
        self._set_controls_enabled(True)

        self.song_name.setText(song.name)
        self.song_meta.setText(f"{song.artists} • {song.year}")
        self.state_label.setText("Sound Profile")
        self.duration_chip.setText(self._format_duration(song.duration_ms))
        self.explicit_chip.setText("Explicit" if song.explicit else "Clean")

        for feature, row in self.slider_rows.items():
            slider = row["slider"]
            normalized_value = song.normalize_feature(feature)
            with QSignalBlocker(slider):
                slider.setValue(int(round(normalized_value * 100)))
            row["value"].setText(f"{slider.value()}%")

        self._refresh_profile_views()

    def _handle_slider_change(self) -> None:
        if self.current_song is None:
            return

        for row in self.slider_rows.values():
            row["value"].setText(f"{row['slider'].value()}%")

        self._refresh_profile_views()

    def _refresh_profile_views(self) -> None:
        profile = self._current_profile()
        self.radar_chart.plot_profile(profile)
        self._populate_similar_songs(profile)

    def _current_profile(self) -> dict[str, float]:
        return {
            feature: self.slider_rows[feature]["slider"].value() / 100
            for feature in RADAR_FEATURES
        }

    def _populate_similar_songs(self, profile: dict[str, float]) -> None:
        self.similar_list.clear()

        if self.current_song is None or not self.all_songs:
            return

        similar_songs = rank_similar_songs(
            songs=self.all_songs,
            profile=profile,
            exclude_song_id=self.current_song.id,
            limit=6,
        )

        for song, score in similar_songs:
            item = QListWidgetItem(
                f"{song.name}\n{song.artists} • {song.year} • {int(round(score * 100))}% match"
            )
            self.similar_list.addItem(item)

    def _set_controls_enabled(self, enabled: bool) -> None:
        for row in self.slider_rows.values():
            row["slider"].setEnabled(enabled)
        self.similar_list.setEnabled(enabled)

    def _format_duration(self, duration_ms: int) -> str:
        total_seconds = max(0, duration_ms // 1000)
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes}:{seconds:02d}"
