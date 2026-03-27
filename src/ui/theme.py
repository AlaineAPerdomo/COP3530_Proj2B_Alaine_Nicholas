APP_STYLESHEET = """
QWidget {
    background-color: #121212;
    color: #f5f7fb;
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0b0b0c;
}

QFrame#SidebarPanel,
QFrame#CenterPanel,
QFrame#DetailPanel,
QFrame#Card {
    background-color: #171718;
    border: 1px solid #2b2b2e;
    border-radius: 24px;
}

QLabel#TitleLabel {
    font-size: 24px;
    font-weight: bold;
    color: #f8fafc;
}

QLabel#SectionTitle {
    font-size: 17px;
    font-weight: 700;
    color: #f8fafc;
}

QLabel#MutedText {
    color: #a6abbc;
    font-size: 12px;
}

QLabel#SidebarTitle {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
}

QLabel#SidebarSubtitle {
    color: #c5cada;
    font-size: 13px;
}

QLabel#HeroTitle {
    font-size: 38px;
    font-weight: 800;
    color: #ffffff;
}

QLabel#HeroSubtitle {
    font-size: 22px;
    font-weight: 600;
    color: #eef1fa;
}

QLabel#Eyebrow {
    color: #ff5d7a;
    font-size: 11px;
    font-weight: 700;
}

QLabel#Pill,
QLabel#InfoChip,
QLabel#StatusBadge,
QWidget#LegendChip {
    background-color: #222225;
    border: 1px solid #33343a;
    border-radius: 13px;
    color: #f4f6fb;
    font-weight: 600;
}

QLabel#Pill,
QLabel#InfoChip,
QLabel#StatusBadge {
    padding: 6px 12px;
}

QLabel#StatusBadge {
    background-color: #1d3324;
    border: 1px solid #356443;
    color: #b8f3c5;
}

QLabel#LegendChipText {
    color: #f4f6fb;
    font-weight: 600;
}

QLabel#HeroArtwork,
QLabel#InspectorArt {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #6c63ff,
        stop: 0.45 #2f7dff,
        stop: 1 #111827
    );
    border: 1px solid #5060ff;
    border-radius: 24px;
    color: #ffffff;
    font-weight: 800;
}

QLabel#InspectorArt {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #1f2937,
        stop: 0.4 #0f766e,
        stop: 1 #111827
    );
    border: 1px solid #2f9c93;
    font-size: 18px;
    font-weight: 700;
    padding: 20px;
}

QLabel#MetricLabel {
    color: #dfe4f2;
    font-size: 12px;
    font-weight: 600;
}

QPushButton {
    background-color: #26272b;
    color: #f6f8ff;
    border: 1px solid #33343a;
    border-radius: 18px;
    padding: 12px 14px;
    font-weight: 700;
}

QPushButton#PrimaryButton {
    background-color: #1ed760;
    color: #08110b;
    border: none;
}

QPushButton#PrimaryButton:hover {
    background-color: #3be477;
}

QPushButton#SecondaryButton:hover,
QPushButton:hover {
    background-color: #303137;
}

QComboBox,
QSpinBox {
    background-color: #111214;
    border: 1px solid #34363d;
    border-radius: 16px;
    padding: 10px 12px;
    selection-background-color: #ff5d7a;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox QAbstractItemView {
    background-color: #161719;
    color: #f7f8fd;
    border: 1px solid #34363d;
    selection-background-color: #2a2d35;
}

QListWidget#SimilarSongsList {
    background-color: #111214;
    border: 1px solid #2b2d33;
    border-radius: 18px;
    padding: 8px;
}

QListWidget#SimilarSongsList::item {
    background-color: #1a1b1f;
    border: 1px solid #2d3138;
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 8px;
}

QListWidget#SimilarSongsList::item:selected {
    background-color: #2a2d35;
    border: 1px solid #3c434d;
}

QScrollArea#DetailScrollArea,
QScrollArea#SidebarScrollArea,
QScrollArea#CenterScrollArea {
    background-color: transparent;
    border: none;
}

QWidget#DetailScrollContent {
    background-color: transparent;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 8px 2px 8px 0;
}

QScrollBar::handle:vertical {
    background: #353841;
    border-radius: 5px;
    min-height: 28px;
}

QScrollBar::handle:vertical:hover {
    background: #4b505d;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
    height: 0px;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #2f3137;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #1ed760;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #f8fafc;
    border: 2px solid #1ed760;
    width: 18px;
    margin: -7px 0;
    border-radius: 9px;
}

QTableWidget {
    background-color: transparent;
    border: 1px solid #2b2d33;
    border-radius: 20px;
    padding: 8px;
    gridline-color: transparent;
    alternate-background-color: transparent;
    selection-background-color: #2b3140;
    outline: none;
}

QTableWidget::item {
    border-bottom: 1px solid #24262b;
    padding: 10px 12px;
}

QTableWidget::item:selected {
    background-color: #21242c;
    border-radius: 14px;
}

QHeaderView::section {
    background-color: transparent;
    color: #9ea5bb;
    border: none;
    padding: 12px 10px;
    font-weight: 700;
}

QProgressBar {
    background-color: #23242a;
    border: none;
    border-radius: 5px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #ff5d7a,
        stop: 1 #ff9f68
    );
    border-radius: 5px;
}
"""
