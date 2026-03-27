from dataclasses import dataclass, field
from typing import Any


@dataclass
class SortStep:
    step_type: str
    payload: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"SortStep(type='{self.step_type}', payload={self.payload})"
    