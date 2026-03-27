SORTABLE_FEATURES = [
    "danceability",
    "energy",
    "loudness",
    "tempo",
    "valence",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
    "popularity",
    "year",
    "duration_ms",
]

FEATURE_RANGES = {
    "acousticness": (0.0, 1.0),
    "danceability": (0.0, 1.0),
    "energy": (0.0, 1.0),
    "instrumentalness": (0.0, 1.0),
    "liveness": (0.0, 1.0),
    "loudness": (-60.0, 0.0),
    "speechiness": (0.0, 1.0),
    "tempo": (0.0, 250.0),
    "valence": (0.0, 1.0),
    "popularity": (0.0, 100.0),
    "year": (1900.0, 2100.0),
    "duration_ms": (0.0, 600000.0),
}

RADAR_FEATURES = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "speechiness",
    "tempo",
]

DEFAULT_SAMPLE_SIZE = 100
