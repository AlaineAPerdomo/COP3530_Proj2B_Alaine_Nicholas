from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class SidebarPanel(QFrame):
    MIN_SAMPLE_SIZE = 5

    def __init__(self):
        super().__init__()
        self.setObjectName("SidebarPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(320)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("SoundSeekers")
        title.setObjectName("SidebarTitle")

        algorithm_label = QLabel("Algorithm")
        algorithm_label.setObjectName("SectionTitle")
        self.algorithm_dropdown = QComboBox()
        self.algorithm_dropdown.addItems(["Merge Sort", "Quick Sort"])

        feature_label = QLabel("Feature")
        feature_label.setObjectName("SectionTitle")
        self.feature_dropdown = QComboBox()
        self.feature_dropdown.addItems([
            "danceability",
            "energy",
            "valence",
            "tempo",
            "loudness",
            "popularity",
            "acousticness",
            "speechiness",
        ])

        order_label = QLabel("Order")
        order_label.setObjectName("SectionTitle")
        self.order_dropdown = QComboBox()
        self.order_dropdown.addItems(["Ascending", "Descending"])

        sample_label = QLabel("Sample Size")
        sample_label.setObjectName("SectionTitle")

        sample_row = QWidget()
        sample_row_layout = QHBoxLayout(sample_row)
        sample_row_layout.setContentsMargins(0, 0, 0, 0)
        sample_row_layout.setSpacing(8)

        self.sample_value_label = QLabel("25")
        self.sample_value_label.setObjectName("InfoChip")

        self.sample_slider = QSlider(Qt.Horizontal)
        self.sample_slider.setRange(self.MIN_SAMPLE_SIZE, 500)
        self.sample_slider.setValue(25)
        self.sample_slider.setTickPosition(QSlider.NoTicks)
        self.sample_slider.valueChanged.connect(self._update_sample_size_ui)

        sample_row_layout.addWidget(self.sample_value_label)
        sample_row_layout.addWidget(self.sample_slider, 1)

        self.load_button = QPushButton("Load Dataset")
        self.load_button.setObjectName("SecondaryButton")
        self.animate_button = QPushButton("Animate Sort")
        self.animate_button.setObjectName("PrimaryButton")
        self.compare_button = QPushButton("Compare")
        self.compare_button.setObjectName("SecondaryButton")
        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("SecondaryButton")

        layout.addWidget(title)
        layout.addSpacing(8)

        layout.addWidget(algorithm_label)
        layout.addWidget(self.algorithm_dropdown)

        layout.addWidget(feature_label)
        layout.addWidget(self.feature_dropdown)

        layout.addWidget(order_label)
        layout.addWidget(self.order_dropdown)

        layout.addWidget(sample_label)
        layout.addWidget(sample_row)

        layout.addWidget(self.load_button)
        layout.addWidget(self.animate_button)
        layout.addWidget(self.compare_button)
        layout.addWidget(self.reset_button)

        layout.addStretch()

        self._update_sample_size_ui(self.sample_slider.value())

    def set_sample_size_limit(self, max_size: int) -> None:
        max_size = max(self.MIN_SAMPLE_SIZE, max_size)
        current_value = self.sample_slider.value()
        self.sample_slider.setRange(self.MIN_SAMPLE_SIZE, max_size)
        self.sample_slider.setValue(min(current_value, max_size))
        self._update_sample_size_ui(self.sample_slider.value())

    def set_sample_size_value(self, value: int) -> None:
        self.sample_slider.setValue(value)

    def sample_size_value(self) -> int:
        return self.sample_slider.value()

    def _update_sample_size_ui(self, value: int) -> None:
        minimum = self.sample_slider.minimum()
        maximum = self.sample_slider.maximum()
        self.sample_value_label.setText(str(value))
        self.sample_slider.setToolTip(f"Sample Size: {value} (min {minimum}, max {maximum})")
