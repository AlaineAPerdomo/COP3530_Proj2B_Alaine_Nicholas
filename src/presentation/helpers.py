from PySide6.QtWidgets import QWidget


def set_transparent_surface(*widgets: QWidget) -> None:
    for widget in widgets:
        widget.setProperty("surface", "transparent")
