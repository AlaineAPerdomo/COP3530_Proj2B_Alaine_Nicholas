from dataclasses import dataclass
from typing import List

from src.utils.constants import FEATURE_RANGES, RADAR_FEATURES


@dataclass
class Song:
    id: str
    name: str
    artists: str
    duration_ms: int
    release_date: str
    year: int
    acousticness: float
    danceability: float
    energy: float
    instrumentalness: float
    liveness: float
    loudness: float
    speechiness: float
    tempo: float
    valence: float
    mode: int
    key: int
    popularity: int
    explicit: bool

    def get_feature_value(self, feature_name: str):
        """Return any feature dynamically for sorting/analysis."""
        if not hasattr(self, feature_name):
            raise ValueError(f"Song has no feature named '{feature_name}'")
        return getattr(self, feature_name)

    def normalize_feature(self, feature_name: str) -> float:
        """Normalize a single feature to [0, 1] using configured ranges."""
        value = float(self.get_feature_value(feature_name))

        if feature_name not in FEATURE_RANGES:
            raise ValueError(f"No normalization range defined for '{feature_name}'")

        min_val, max_val = FEATURE_RANGES[feature_name]

        if max_val == min_val:
            return 0.0

        normalized = (value - min_val) / (max_val - min_val)

        # Clamp to [0, 1]
        return max(0.0, min(1.0, normalized))

    def to_feature_vector(self, feature_names: List[str] | None = None) -> List[float]:
        """Return a normalized vector for similarity/radar usage."""
        if feature_names is None:
            feature_names = RADAR_FEATURES
        return [self.normalize_feature(feature) for feature in feature_names]

    def short_display(self) -> str:
        return f"{self.name} — {self.artists} ({self.year})"

    def __str__(self) -> str:
        return (
            f"Song(name='{self.name}', artists='{self.artists}', year={self.year}, "
            f"popularity={self.popularity})"
        )