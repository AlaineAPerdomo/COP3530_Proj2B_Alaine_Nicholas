from src.models.sort_step import SortStep


class StepRecorder:
    def __init__(self):
        self.steps: list[SortStep] = []

    def record(self, step_type: str, **payload) -> None:
        self.steps.append(SortStep(step_type=step_type, payload=payload))

    def get_steps(self) -> list[SortStep]:
        return self.steps[:]

    def clear(self) -> None:
        self.steps.clear()