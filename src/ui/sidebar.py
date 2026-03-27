from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class SidebarPanel(QFrame):
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
        self.sample_spinbox = QSpinBox()
        self.sample_spinbox.setRange(5, 500)
        self.sample_spinbox.setValue(25)

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
        layout.addWidget(self.sample_spinbox)

        layout.addWidget(self.load_button)
        layout.addWidget(self.animate_button)
        layout.addWidget(self.compare_button)
        layout.addWidget(self.reset_button)

        layout.addStretch()
