from PySide6.QtWidgets import QMainWindow

from src.app.layout import MainLayout
from src.models.song import Song
from src.ui.theme import APP_STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self, songs: list[Song]):
        super().__init__()

        self.setWindowTitle("SoundSeekers")
        self.resize(1450, 860)

        self.setStyleSheet(APP_STYLESHEET)

        self.main_layout = MainLayout(songs)
        self.setCentralWidget(self.main_layout)