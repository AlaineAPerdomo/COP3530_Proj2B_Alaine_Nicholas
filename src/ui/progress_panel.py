from PySide6.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout


class ProgressPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        self.title = QLabel("Processing Progress")
        self.title.setObjectName("SectionTitle")

        self.status_label = QLabel("Benchmark progress")
        self.status_label.setObjectName("MutedText")

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("BenchmarkProgress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")

        layout.addWidget(self.title)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)

        self.setVisible(False)

    def show_progress(self, visible: bool) -> None:
        self.setVisible(visible)

        if not visible:
            self.status_label.setText("Benchmark progress")
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("%p%")

    def update_progress(self, value: int, text: str) -> None:
        self.status_label.setText(text)
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{value}%")
