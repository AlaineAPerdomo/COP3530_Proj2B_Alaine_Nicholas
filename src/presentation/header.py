from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.presentation.helpers import set_transparent_surface


class HeaderPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")

        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(24, 24, 24, 24)
        outer_layout.setSpacing(16)

        artwork = QLabel("MIX")
        self.artwork = artwork
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

        self.chip_row = QWidget()
        self.chip_layout = QHBoxLayout(self.chip_row)
        self.chip_layout.setContentsMargins(0, 0, 0, 0)
        self.chip_layout.setSpacing(10)

        self.chip_row_bottom = QWidget()
        self.chip_row_bottom_layout = QHBoxLayout(self.chip_row_bottom)
        self.chip_row_bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.chip_row_bottom_layout.setSpacing(10)

        self.legend_row = QWidget()
        legend_layout = QHBoxLayout(self.legend_row)
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
        left_column.addWidget(self.chip_row)
        left_column.addWidget(self.chip_row_bottom)
        left_column.addWidget(self.legend_row)

        outer_layout.addWidget(artwork, 0, Qt.AlignTop)
        outer_layout.addLayout(left_column, 1)

        set_transparent_surface(
            self.eyebrow,
            self.title,
            self.chip_row,
            self.chip_row_bottom,
            self.legend_row,
            legend_title,
        )
        self.set_mode(performance_mode=False)

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
        self.artwork.setFixedSize(124, 124) if performance_mode else self.artwork.setFixedSize(140, 140)
        self._rebuild_chip_rows(performance_mode)
        self.legend_row.setVisible(not performance_mode)

    def _rebuild_chip_rows(self, performance_mode: bool) -> None:
        self._clear_layout(self.chip_layout)
        self._clear_layout(self.chip_row_bottom_layout)

        self.chip_layout.addWidget(self.status)
        self.chip_layout.addWidget(self.algorithm)
        self.chip_layout.addWidget(self.feature)

        if performance_mode:
            self.chip_layout.addStretch()
            self.chip_row_bottom_layout.addWidget(self.dataset)
            self.chip_row_bottom_layout.addWidget(self.mode)
            self.chip_row_bottom_layout.addStretch()
            self.chip_row_bottom.setVisible(True)
        else:
            self.chip_layout.addWidget(self.dataset)
            self.chip_layout.addWidget(self.mode)
            self.chip_layout.addStretch()
            self.chip_row_bottom.setVisible(False)

    def _clear_layout(self, layout: QHBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

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
