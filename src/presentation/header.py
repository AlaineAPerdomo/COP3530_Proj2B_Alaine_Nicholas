from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.presentation.helpers import set_transparent_surface


class HeaderPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")

        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(24, 24, 24, 24)
        outer_layout.setSpacing(20)

        artwork = QLabel("MIX")
        artwork.setObjectName("HeroArtwork")
        artwork.setAlignment(Qt.AlignCenter)
        artwork.setFixedSize(140, 140)

        left_column = QVBoxLayout()
        left_column.setSpacing(10)

        self.eyebrow = QLabel("Feature-driven playlist sequencing")
        self.eyebrow.setObjectName("Eyebrow")

        self.title = QLabel("SoundSeekers Studio")
        self.title.setObjectName("HeroTitle")
        self.title.setWordWrap(True)

        self.status = QLabel("Status: Ready")
        self.status.setObjectName("StatusBadge")

        self.algorithm = QLabel("Merge Sort")
        self.algorithm.setObjectName("InfoChip")

        self.feature = QLabel("danceability")
        self.feature.setObjectName("InfoChip")

        self.dataset = QLabel("25 songs loaded")
        self.dataset.setObjectName("InfoChip")

        self.mode = QLabel("Mode: Animation")
        self.mode.setObjectName("InfoChip")

        chip_row = QWidget()
        chip_layout = QHBoxLayout(chip_row)
        chip_layout.setContentsMargins(0, 0, 0, 0)
        chip_layout.setSpacing(10)
        chip_layout.addWidget(self.status)
        chip_layout.addWidget(self.algorithm)
        chip_layout.addWidget(self.feature)
        chip_layout.addWidget(self.dataset)
        chip_layout.addWidget(self.mode)
        chip_layout.addStretch()

        legend_row = QWidget()
        legend_layout = QHBoxLayout(legend_row)
        legend_layout.setContentsMargins(0, 0, 0, 0)
        legend_layout.setSpacing(10)

        legend_title = QLabel("Now Sorting:")
        legend_title.setObjectName("MutedText")
        legend_layout.addWidget(legend_title)
        legend_layout.addWidget(self._build_legend_chip("#7c5d06", "Compare"))
        legend_layout.addWidget(self._build_legend_chip("#174ea6", "Overwrite"))
        legend_layout.addWidget(self._build_legend_chip("#166534", "Sorted"))
        legend_layout.addStretch()

        left_column.addWidget(self.eyebrow)
        left_column.addWidget(self.title)
        left_column.addSpacing(6)
        left_column.addWidget(chip_row)
        left_column.addWidget(legend_row)

        outer_layout.addWidget(artwork, 0, Qt.AlignTop)
        outer_layout.addLayout(left_column, 1)

        set_transparent_surface(self.eyebrow, self.title, chip_row, legend_row, legend_title)

    def set_status(self, text: str) -> None:
        self.status.setText(f"Status: {text}")

    def set_algorithm(self, text: str) -> None:
        self.algorithm.setText(text)

    def set_feature(self, text: str) -> None:
        self.feature.setText(text)

    def set_dataset_size(self, size: int, performance_mode: bool = False) -> None:
        descriptor = "songs selected" if performance_mode else "songs loaded"
        self.dataset.setText(f"{size:,} {descriptor}")

    def set_mode(self, performance_mode: bool) -> None:
        self.mode.setText(
            "Mode: Performance" if performance_mode else "Mode: Animation"
        )

    def _build_legend_chip(self, color: str, label_text: str) -> QWidget:
        chip = QWidget()
        chip.setObjectName("LegendChip")

        layout = QHBoxLayout(chip)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        swatch = QLabel()
        swatch.setFixedSize(10, 10)
        swatch.setStyleSheet(
            f"background-color: {color}; border-radius: 5px;"
        )

        label = QLabel(label_text)
        label.setObjectName("LegendChipText")
        set_transparent_surface(swatch, label)

        layout.addWidget(swatch)
        layout.addWidget(label)
        return chip
