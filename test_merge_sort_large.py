import argparse
from time import perf_counter

from src.algorithms.merge_sort import merge_sort_songs
from src.algorithms.validators import validate_sorted_result
from src.data.filters import filter_valid_songs, sample_songs
from src.data.loader import load_csv_rows
from src.data.parser import parse_songs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a merge sort benchmark and correctness check."
    )
    parser.add_argument(
        "--feature",
        default="energy",
        help="Song feature to sort by, for example energy, danceability, tempo, or valence.",
    )
    parser.add_argument(
        "--descending",
        action="store_true",
        help="Sort in descending order instead of ascending.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Optional sample size instead of using the full dataset.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    rows = load_csv_rows("data/data.csv")
    songs = filter_valid_songs(parse_songs(rows))

    if args.sample_size is not None:
        songs = sample_songs(songs, args.sample_size)

    ascending = not args.descending

    start_time = perf_counter()
    sorted_songs = merge_sort_songs(songs, args.feature, ascending=ascending)
    elapsed_seconds = perf_counter() - start_time

    is_valid = validate_sorted_result(
        original_songs=songs,
        sorted_songs=sorted_songs,
        feature=args.feature,
        ascending=ascending,
    )

    print(f"rows: {len(songs)}")
    print(f"feature: {args.feature}")
    print(f"order: {'ascending' if ascending else 'descending'}")
    print(f"seconds: {elapsed_seconds:.3f}")
    print(f"valid: {is_valid}")

    if sorted_songs:
        first_song = sorted_songs[0]
        last_song = sorted_songs[-1]
        print(f"first: {first_song.name} ({first_song.get_feature_value(args.feature)})")
        print(f"last: {last_song.name} ({last_song.get_feature_value(args.feature)})")


if __name__ == "__main__":
    main()
