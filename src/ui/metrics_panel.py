from PySide6.QtWidgets import QFrame, QGridLayout, QLabel


class MetricsPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")

        layout = QGridLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(12)

        title = QLabel("Session Metrics")
        title.setObjectName("SectionTitle")
        title.setProperty("surface", "transparent")

        self.comparisons = QLabel("Comparisons: 0")
        self.comparisons.setObjectName("InfoChip")

        self.moves = QLabel("Swaps/Moves: 0")
        self.moves.setObjectName("InfoChip")

        self.overwrites = QLabel("Overwrites: 0")
        self.overwrites.setObjectName("InfoChip")

        self.runtime = QLabel("Runtime: 0.00s")
        self.runtime.setObjectName("InfoChip")

        self.steps = QLabel("Steps: 0")
        self.steps.setObjectName("InfoChip")

        layout.addWidget(title, 0, 0, 1, 2)
        layout.addWidget(self.comparisons, 1, 0)
        layout.addWidget(self.moves, 1, 1)
        layout.addWidget(self.overwrites, 2, 0)
        layout.addWidget(self.steps, 2, 1)
        layout.addWidget(self.runtime, 3, 0, 1, 2)

    def set_comparisons(self, value: int) -> None:
        self.comparisons.setText(f"Comparisons: {value}")

    def set_moves(self, value: int) -> None:
        self.moves.setText(f"Swaps/Moves: {value}")

    def set_overwrites(self, value: int) -> None:
        self.overwrites.setText(f"Overwrites: {value}")

    def set_steps(self, value: int) -> None:
        self.steps.setText(f"Steps: {value}")

    def set_runtime_ms(self, runtime_ms: int) -> None:
        self.runtime.setText(f"Runtime: {runtime_ms / 1000:.2f}s")
