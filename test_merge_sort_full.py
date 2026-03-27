from time import perf_counter

from src.algorithms.merge_sort import merge_sort_songs
from src.algorithms.validators import validate_sorted_result
from src.data.filters import filter_valid_songs
from src.data.loader import load_csv_rows
from src.data.parser import parse_songs


def main() -> None:
    feature = "energy"
    ascending = True

    rows = load_csv_rows("data/data.csv")
    songs = filter_valid_songs(parse_songs(rows))

    start_time = perf_counter()
    sorted_songs = merge_sort_songs(songs, feature, ascending=ascending)
    elapsed_seconds = perf_counter() - start_time

    is_valid = validate_sorted_result(
        original_songs=songs,
        sorted_songs=sorted_songs,
        feature=feature,
        ascending=ascending,
    )

    print("Merge Sort Full Dataset Test")
    print(f"rows: {len(songs)}")
    print(f"feature: {feature}")
    print(f"order: {'ascending' if ascending else 'descending'}")
    print(f"seconds: {elapsed_seconds:.3f}")
    print(f"valid: {is_valid}")

    if sorted_songs:
        print(f"first: {sorted_songs[0].name} ({sorted_songs[0].get_feature_value(feature)})")
        print(f"last: {sorted_songs[-1].name} ({sorted_songs[-1].get_feature_value(feature)})")


if __name__ == "__main__":
    main()
