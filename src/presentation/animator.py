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
        self._prepared = False

    def start(self, auto_play: bool = False) -> None:
        self.current_step_index = 0
        self.comparisons = 0
        self.moves = 0
        self.overwrites = 0
        self._prepared = True

        self.layout_controller.prepare_for_animation()
        self.layout_controller.update_status("Ready to Step")
        self.layout_controller.update_step_count(0)
        self.layout_controller.update_comparisons(0)
        self.layout_controller.update_moves(0)
        self.layout_controller.update_overwrites(0)
        self.layout_controller.update_runtime_ms(0)
        self.layout_controller.update_animation_controls(
            current_step=0,
            total_steps=len(self.steps),
            is_playing=False,
            ready=True,
        )

        self.elapsed_timer.start()

        if auto_play:
            self.play()

    def stop(self) -> None:
        self.timer.stop()
        self.layout_controller.update_animation_controls(
            current_step=self.current_step_index,
            total_steps=len(self.steps),
            is_playing=False,
            ready=self._prepared,
        )

    def play(self) -> None:
        if not self._prepared or self.current_step_index >= len(self.steps):
            return
        self.layout_controller.update_status("Animating")
        self.timer.start(self.speed_ms)
        self.layout_controller.update_animation_controls(
            current_step=self.current_step_index,
            total_steps=len(self.steps),
            is_playing=True,
            ready=True,
        )

    def pause(self) -> None:
        if not self._prepared:
            return
        self.timer.stop()
        self.layout_controller.update_status("Paused")
        self.layout_controller.update_animation_controls(
            current_step=self.current_step_index,
            total_steps=len(self.steps),
            is_playing=False,
            ready=True,
        )

    def next_step(self) -> None:
        if not self._prepared or self.current_step_index >= len(self.steps):
            return
        if self.timer.isActive():
            self.timer.stop()
        self.layout_controller.update_status("Advancing Stage")
        self.play_next_step()

    def previous_step(self) -> None:
        if not self._prepared or self.current_step_index <= 0:
            return

        if self.timer.isActive():
            self.timer.stop()

        target_index = self.current_step_index - 1
        self.current_step_index = 0
        self.comparisons = 0
        self.moves = 0
        self.overwrites = 0

        self.layout_controller.prepare_for_animation()
        self.layout_controller.update_status("Rewinding")
        self.layout_controller.update_step_count(0)
        self.layout_controller.update_comparisons(0)
        self.layout_controller.update_moves(0)
        self.layout_controller.update_overwrites(0)

        for _ in range(target_index):
            step = self.steps[self.current_step_index]
            self.layout_controller.apply_sort_step(step)

            if step.step_type == "compare":
                self.comparisons += 1
            elif step.step_type == "write":
                self.moves += 1
                self.overwrites += 1

            self.current_step_index += 1

        self.layout_controller.update_step_count(self.current_step_index)
        self.layout_controller.update_comparisons(self.comparisons)
        self.layout_controller.update_moves(self.moves)
        self.layout_controller.update_overwrites(self.overwrites)
        self.layout_controller.update_runtime_ms(self.elapsed_timer.elapsed())
        self.layout_controller.update_status(
            f"Stage {self.current_step_index} Ready"
        )
        self.layout_controller.update_animation_controls(
            current_step=self.current_step_index,
            total_steps=len(self.steps),
            is_playing=False,
            ready=True,
        )

    def play_next_step(self) -> None:
        if self.current_step_index >= len(self.steps):
            self.stop()
            self.layout_controller.update_runtime_ms(self.elapsed_timer.elapsed())
            self.layout_controller.finish_animation()
            self.layout_controller.update_animation_controls(
                current_step=len(self.steps),
                total_steps=len(self.steps),
                is_playing=False,
                ready=False,
            )
            return

        step = self.steps[self.current_step_index]
        self.layout_controller.apply_sort_step(step)

        if step.step_type == "compare":
            self.comparisons += 1
        elif step.step_type == "write":
            self.moves += 1
            self.overwrites += 1

        self.current_step_index += 1

        self.layout_controller.update_step_count(self.current_step_index)
        self.layout_controller.update_comparisons(self.comparisons)
        self.layout_controller.update_moves(self.moves)
        self.layout_controller.update_overwrites(self.overwrites)
        self.layout_controller.update_runtime_ms(self.elapsed_timer.elapsed())
        self.layout_controller.update_animation_controls(
            current_step=self.current_step_index,
            total_steps=len(self.steps),
            is_playing=self.timer.isActive(),
            ready=True,
        )
