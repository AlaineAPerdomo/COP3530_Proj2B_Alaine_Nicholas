from math import cos, radians, sin

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QConicalGradient, QFont, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import (
    QComboBox,
    QDial,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.presentation.helpers import set_transparent_surface


class SampleSizeDial(QDial):
    def __init__(self):
        super().__init__()
        self.setObjectName("SampleKnob")
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect().adjusted(8, 8, -8, -8)
        arc_rect = QRectF(rect)
        dial_rect = arc_rect.adjusted(11, 11, -11, -11)
        center = dial_rect.center()
        radius = dial_rect.width() / 2

        start_degrees = 225
        sweep_degrees = -270
        ratio = 0 if self.maximum() == self.minimum() else (
            (self.value() - self.minimum()) / (self.maximum() - self.minimum())
        )
        indicator_degrees = start_degrees + (sweep_degrees * ratio)

        painter.setPen(QPen(QColor("#262a32"), 10, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(arc_rect, start_degrees * 16, sweep_degrees * 16)

        gradient = QConicalGradient(arc_rect.center(), -135)
        gradient.setColorAt(0.00, QColor("#1ed760"))
        gradient.setColorAt(0.50, QColor("#2f7dff"))
        gradient.setColorAt(1.00, QColor("#1ed760"))
        painter.setPen(QPen(gradient, 10, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(arc_rect, start_degrees * 16, sweep_degrees * 16)

        rim_gradient = QRadialGradient(center, radius)
        rim_gradient.setColorAt(0.0, QColor("#606773"))
        rim_gradient.setColorAt(0.45, QColor("#343841"))
        rim_gradient.setColorAt(1.0, QColor("#0f1116"))
        painter.setBrush(rim_gradient)
        painter.setPen(QPen(QColor("#8c93a3"), 2))
        painter.drawEllipse(dial_rect)

        inner_rect = dial_rect.adjusted(7, 7, -7, -7)
        face_gradient = QRadialGradient(
            inner_rect.left() + inner_rect.width() * 0.35,
            inner_rect.top() + inner_rect.height() * 0.28,
            inner_rect.width() * 0.85,
        )
        face_gradient.setColorAt(0.0, QColor("#7b8089"))
        face_gradient.setColorAt(0.42, QColor("#4f5560"))
        face_gradient.setColorAt(1.0, QColor("#171a20"))
        painter.setBrush(face_gradient)
        painter.setPen(QPen(QColor("#adb4c3"), 1))
        painter.drawEllipse(inner_rect)

        pointer_length = inner_rect.width() * 0.34
        pointer_angle = radians(indicator_degrees)
        pointer_end = QPointF(
            center.x() + cos(pointer_angle) * pointer_length,
            center.y() - sin(pointer_angle) * pointer_length,
        )
        painter.setPen(QPen(QColor("#ff5d7a"), 3.5, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(center, pointer_end)

        hub_rect = QRectF(center.x() - 11, center.y() - 11, 22, 22)
        hub_gradient = QRadialGradient(hub_rect.center(), 14)
        hub_gradient.setColorAt(0.0, QColor("#2f343d"))
        hub_gradient.setColorAt(1.0, QColor("#121418"))
        painter.setBrush(hub_gradient)
        painter.setPen(QPen(QColor("#1c2028"), 1))
        painter.drawEllipse(hub_rect)

        label_font = QFont(self.font())
        label_font.setBold(True)
        label_font.setPointSize(7)
        painter.setFont(label_font)
        painter.setPen(QColor("#8e97ac"))
        painter.drawText(QRectF(2, self.height() - 20, 30, 18), Qt.AlignCenter, "MIN")
        painter.drawText(
            QRectF(self.width() - 32, self.height() - 20, 30, 18),
            Qt.AlignCenter,
            "MAX",
        )


class SidebarPanel(QFrame):
    MIN_SAMPLE_SIZE = 5
    VISUALIZATION_LIMIT = 50
    FINE_DIAL_SPAN = VISUALIZATION_LIMIT - MIN_SAMPLE_SIZE
    COMPRESSED_DIAL_STEPS = 160

    def __init__(self):
        super().__init__()
        self.setObjectName("SidebarPanel")
        self.setMinimumWidth(240)
        self.setMaximumWidth(290)
        self._sample_max_size = 500

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
        sample_row_layout.setSpacing(12)

        knob_column = QWidget()
        knob_column.setObjectName("KnobColumn")
        knob_layout = QVBoxLayout(knob_column)
        knob_layout.setContentsMargins(0, 0, 0, 0)
        knob_layout.setSpacing(6)
        knob_layout.setAlignment(Qt.AlignCenter)

        self.sample_value_label = QLabel("25")
        self.sample_value_label.setObjectName("ModeChip")
        self.sample_value_label.setAlignment(Qt.AlignCenter)
        self.sample_value_label.setMinimumHeight(40)

        self.sample_mode_label = QLabel("Animation Mode")
        self.sample_mode_label.setObjectName("ModeChip")
        self.sample_mode_label.setAlignment(Qt.AlignCenter)
        self.sample_mode_label.setWordWrap(True)
        self.sample_mode_label.setMinimumHeight(40)

        self.sample_knob = SampleSizeDial()
        self.sample_knob.setRange(0, self._dial_maximum())
        self.sample_knob.setValue(self._sample_size_to_dial_position(25))
        self.sample_knob.setWrapping(False)
        self.sample_knob.setPageStep(1)
        self.sample_knob.setFixedSize(98, 98)
        self.sample_knob.valueChanged.connect(self._update_sample_size_ui)

        knob_shell = QFrame()
        knob_shell.setObjectName("KnobShell")
        knob_shell.setFixedSize(116, 116)
        knob_shell_layout = QVBoxLayout(knob_shell)
        knob_shell_layout.setContentsMargins(0, 0, 0, 0)
        knob_shell_layout.setAlignment(Qt.AlignCenter)
        knob_shell_layout.addWidget(self.sample_knob)

        min_max_label = QLabel("min 5 / max 500")
        min_max_label.setObjectName("KnobCaption")
        min_max_label.setAlignment(Qt.AlignCenter)

        animation_note = QLabel(
            "Step-by-step animation available for up to 50 songs."
        )
        animation_note.setObjectName("KnobNote")
        animation_note.setWordWrap(True)

        knob_layout.addWidget(knob_shell, 0, Qt.AlignCenter)
        knob_layout.addWidget(min_max_label)

        sample_row_layout.addWidget(knob_column)

        sample_meta_column = QWidget()
        sample_meta_layout = QVBoxLayout(sample_meta_column)
        sample_meta_layout.setContentsMargins(0, 0, 0, 0)
        sample_meta_layout.setSpacing(10)
        sample_meta_layout.addWidget(self.sample_value_label)
        sample_meta_layout.addWidget(self.sample_mode_label)
        sample_meta_layout.addWidget(animation_note)
        sample_meta_layout.addStretch()

        sample_row_layout.addWidget(sample_meta_column, 1)

        actions_label = QLabel("Available Actions")
        actions_label.setObjectName("SectionTitle")

        self.animate_button = QPushButton("Animate Sorting Algorithm")
        self.animate_button.setObjectName("PrimaryButton")
        self.animate_button.setMinimumWidth(190)
        self.compare_button = QPushButton("Compare Algorithms")
        self.compare_button.setObjectName("SecondaryButton")
        self.shuffle_button = QPushButton("Shuffle Playlist")
        self.shuffle_button.setObjectName("SecondaryButton")
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

        layout.addWidget(actions_label)
        layout.addWidget(self.animate_button)
        layout.addWidget(self.compare_button)
        layout.addWidget(self.shuffle_button)
        layout.addWidget(self.reset_button)

        layout.addStretch()

        set_transparent_surface(
            title,
            algorithm_label,
            feature_label,
            order_label,
            sample_label,
            sample_row,
            knob_column,
            min_max_label,
            animation_note,
            sample_meta_column,
            actions_label,
        )

        self._sample_min_max_label = min_max_label
        self._animation_note_label = animation_note
        self._update_sample_size_ui(self.sample_knob.value())
        self.set_layout_mode(performance_mode=False)

    def set_sample_size_limit(self, max_size: int) -> None:
        self._sample_max_size = max(self.MIN_SAMPLE_SIZE, max_size)
        current_value = self.sample_size_value()
        self.sample_knob.setRange(0, self._dial_maximum())
        self.sample_knob.setValue(
            self._sample_size_to_dial_position(min(current_value, self._sample_max_size))
        )
        self._update_sample_size_ui(self.sample_knob.value())

    def set_sample_size_value(self, value: int) -> None:
        clamped_value = max(self.MIN_SAMPLE_SIZE, min(value, self._sample_max_size))
        self.sample_knob.setValue(self._sample_size_to_dial_position(clamped_value))

    def sample_size_value(self) -> int:
        return self._dial_position_to_sample_size(self.sample_knob.value())

    def _update_sample_size_ui(self, dial_value: int) -> None:
        sample_value = self._dial_position_to_sample_size(dial_value)
        minimum = self.MIN_SAMPLE_SIZE
        maximum = self._sample_max_size
        self.sample_value_label.setText(str(sample_value))
        self.sample_knob.setToolTip(
            f"Sample Size: {sample_value} (min {minimum}, max {maximum})"
        )
        self._sample_min_max_label.setText(f"min {minimum} / max {maximum}")
        self.set_sort_mode(sample_value <= self.VISUALIZATION_LIMIT)

    def set_sort_mode(self, visual_mode: bool) -> None:
        if visual_mode:
            self.animate_button.setText("Animate Sorting Algorithm")
            self.animate_button.setProperty("sortMode", "visual")
            self.animate_button.setToolTip("Record steps and animate the selected sorting algorithm.")
            self.animate_button.setVisible(True)
            self.animate_button.setEnabled(True)
            self.compare_button.setVisible(False)
            self.compare_button.setEnabled(False)
            self.shuffle_button.setVisible(True)
            self.shuffle_button.setEnabled(True)
            self.sample_mode_label.setText("Animation Mode")
            self.sample_mode_label.setProperty("modeState", "animation")
            self.sample_value_label.setProperty("modeState", "animation")
            self._animation_note_label.setText(
                "Step-by-step sorting available for up to 50 songs."
            )
        else:
            self.animate_button.setText("Run Benchmark")
            self.animate_button.setProperty("sortMode", "performance")
            self.animate_button.setToolTip(
                "Large datasets skip animation and run benchmark analysis instead."
            )
            self.animate_button.setVisible(True)
            self.animate_button.setEnabled(True)
            self.compare_button.setVisible(True)
            self.compare_button.setEnabled(True)
            self.compare_button.setToolTip(
                "Benchmark merge sort and quick sort side by side on the selected dataset."
            )
            self.shuffle_button.setVisible(False)
            self.shuffle_button.setEnabled(False)
            self.sample_mode_label.setText("Performance Mode")
            self.sample_mode_label.setProperty("modeState", "performance")
            self.sample_value_label.setProperty("modeState", "performance")
            self._animation_note_label.setText(
                "Animation is disabled above 50 songs. Use benchmark tools below."
            )

        self._refresh_widget_style(self.animate_button)
        self._refresh_widget_style(self.compare_button)
        self._refresh_widget_style(self.sample_mode_label)
        self._refresh_widget_style(self.sample_value_label)

    def set_layout_mode(self, performance_mode: bool) -> None:
        self.setMinimumWidth(240 if performance_mode else 220)
        self.setMaximumWidth(290 if performance_mode else 300)

        knob_size = 98 if performance_mode else 104
        shell_size = 116 if performance_mode else 124
        self.sample_knob.setFixedSize(knob_size, knob_size)
        self.findChild(QFrame, "KnobShell").setFixedSize(shell_size, shell_size)

        self.sample_value_label.setMinimumHeight(40 if performance_mode else 0)
        self.sample_mode_label.setMinimumHeight(40 if performance_mode else 0)

    def _refresh_widget_style(self, widget: QWidget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def _dial_maximum(self) -> int:
        if self._sample_max_size <= self.VISUALIZATION_LIMIT:
            return self._sample_max_size - self.MIN_SAMPLE_SIZE
        return self.FINE_DIAL_SPAN + self.COMPRESSED_DIAL_STEPS

    def _dial_position_to_sample_size(self, dial_position: int) -> int:
        if self._sample_max_size <= self.VISUALIZATION_LIMIT:
            return self.MIN_SAMPLE_SIZE + dial_position

        if dial_position <= self.FINE_DIAL_SPAN:
            return self.MIN_SAMPLE_SIZE + dial_position

        coarse_position = dial_position - self.FINE_DIAL_SPAN
        coarse_span = max(1, self.COMPRESSED_DIAL_STEPS)
        ratio = coarse_position / coarse_span
        value_span = self._sample_max_size - self.VISUALIZATION_LIMIT
        sample_value = self.VISUALIZATION_LIMIT + round((ratio ** 3) * value_span)
        return max(self.MIN_SAMPLE_SIZE, min(sample_value, self._sample_max_size))

    def _sample_size_to_dial_position(self, sample_size: int) -> int:
        sample_size = max(self.MIN_SAMPLE_SIZE, min(sample_size, self._sample_max_size))

        if self._sample_max_size <= self.VISUALIZATION_LIMIT:
            return sample_size - self.MIN_SAMPLE_SIZE

        if sample_size <= self.VISUALIZATION_LIMIT:
            return sample_size - self.MIN_SAMPLE_SIZE

        value_span = max(1, self._sample_max_size - self.VISUALIZATION_LIMIT)
        ratio = (sample_size - self.VISUALIZATION_LIMIT) / value_span
        coarse_position = max(1, round((ratio ** (1 / 3)) * self.COMPRESSED_DIAL_STEPS))
        return min(self._dial_maximum(), self.FINE_DIAL_SPAN + coarse_position)
