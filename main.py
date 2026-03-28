import sys

from PySide6.QtWidgets import QApplication

from src.presentation.window import MainWindow
from src.data.filters import filter_valid_songs
from src.data.loader import load_csv_rows
from src.data.parser import parse_songs


def main():
    rows = load_csv_rows("data/data.csv")
    songs = parse_songs(rows)
    songs = filter_valid_songs(songs)

    app = QApplication(sys.argv)
    window = MainWindow(songs)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
