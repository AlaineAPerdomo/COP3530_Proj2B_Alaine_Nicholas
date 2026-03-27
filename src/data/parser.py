import ast

from src.models.song import Song


def safe_int(value, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default


def safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def parse_explicit(value) -> bool:
    return str(value).strip() in {"1", "True", "true"}


def clean_artists(raw_artists: str) -> str:
    """
    Convert artist strings like "['Drake']" or "['A', 'B']" into readable text.
    """
    if raw_artists is None:
        return "Unknown Artist"

    raw_artists = raw_artists.strip()

    if not raw_artists:
        return "Unknown Artist"

    try:
        parsed = ast.literal_eval(raw_artists)
        if isinstance(parsed, list):
            return ", ".join(str(artist) for artist in parsed)
    except (ValueError, SyntaxError):
        pass

    return raw_artists


def parse_song(row: dict) -> Song:
    """Convert one raw CSV row into a Song object."""
    return Song(
        id=str(row.get("id", "")).strip(),
        name=str(row.get("name", "Unknown Title")).strip(),
        artists=clean_artists(row.get("artists", "")),
        duration_ms=safe_int(row.get("duration_ms")),
        release_date=str(row.get("release_date", "")).strip(),
        year=safe_int(row.get("year")),
        acousticness=safe_float(row.get("acousticness")),
        danceability=safe_float(row.get("danceability")),
        energy=safe_float(row.get("energy")),
        instrumentalness=safe_float(row.get("instrumentalness")),
        liveness=safe_float(row.get("liveness")),
        loudness=safe_float(row.get("loudness")),
        speechiness=safe_float(row.get("speechiness")),
        tempo=safe_float(row.get("tempo")),
        valence=safe_float(row.get("valence")),
        mode=safe_int(row.get("mode")),
        key=safe_int(row.get("key")),
        popularity=safe_int(row.get("popularity")),
        explicit=parse_explicit(row.get("explicit")),
    )


def parse_songs(rows: list[dict]) -> list[Song]:
    """Convert many raw rows into Song objects."""
    return [parse_song(row) for row in rows]