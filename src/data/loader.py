import csv
from pathlib import Path
from typing import Dict, List


def load_csv_rows(file_path: str, limit: int | None = None) -> List[Dict[str, str]]:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    rows: List[Dict[str, str]] = []

    with path.open(mode="r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        for index, row in enumerate(reader):
            rows.append(row)

            if limit is not None and index + 1 >= limit:
                break

    return rows