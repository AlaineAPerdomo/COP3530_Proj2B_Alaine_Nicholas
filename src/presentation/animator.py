from PySide6.QtCore import QElapsedTimer, QObject, QTimer

from src.models.sort_step import SortStep


class MergeSortAnimator(QObject):
    def __init__(self, steps: list[SortStep], layout_controller, speed_ms: int = 500):
        super().__init__()
        self.steps = steps
        self.layout_controller = layout_controller
        self.speed_ms = speed_ms

        self.current_step_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_next_step)
        self.elapsed_timer = QElapsedTimer()

        self.comparisons = 0
        self.moves = 0
        self.overwrites = 0

    def start(self) -> None:
        self.current_step_index = 0
        self.comparisons = 0
        self.moves = 0
        self.overwrites = 0

        self.layout_controller.prepare_for_animation()
        self.layout_controller.update_status("Animating")
        self.layout_controller.update_step_count(0)
        self.layout_controller.update_comparisons(0)
        self.layout_controller.update_moves(0)
        self.layout_controller.update_overwrites(0)
        self.layout_controller.update_runtime_ms(0)

        self.elapsed_timer.start()

        self.timer.start(self.speed_ms)

    def stop(self) -> None:
        self.timer.stop()

    def play_next_step(self) -> None:
        if self.current_step_index >= len(self.steps):
            self.stop()
            self.layout_controller.update_runtime_ms(self.elapsed_timer.elapsed())
            self.layout_controller.finish_animation()
            return

        step = self.steps[self.current_step_index]
        self.layout_controller.apply_sort_step(step)

        if step.step_type == "compare":
            self.comparisons += 1
        elif step.step_type in {"take_left", "take_right"}:
            self.moves += 1
        elif step.step_type == "overwrite":
            self.overwrites += 1

        self.current_step_index += 1

        self.layout_controller.update_step_count(self.current_step_index)
        self.layout_controller.update_comparisons(self.comparisons)
        self.layout_controller.update_moves(self.moves)
        self.layout_controller.update_overwrites(self.overwrites)
        self.layout_controller.update_runtime_ms(self.elapsed_timer.elapsed())
