import argparse
from pathlib import Path
from .datastore import Datastore
from .review import cmd_review
from .stats import cmd_stats

FILE_PATH = Path.home() / Path(".tsurara.json")


def main():
    data = Datastore(FILE_PATH)
    (old_version, new_version) = data.migrate()
    if old_version != new_version:
        print(f"Migrated stored data (v{old_version} -> v{new_version}).")

    parser = argparse.ArgumentParser(description="tsurara")
    subparsers = parser.add_subparsers()
    # review
    parser_review = subparsers.add_parser("review", help="review words in a file")
    parser_review.add_argument(
        "-i",
        "--input",
        help="Path to the input file",
    )
    parser_review.add_argument("-o", "--output", help="Path to the output csv")
    parser_review.add_argument(
        "-s",
        "--stored",
        help="Review stored words in the frequency table",
        action="store_true",
    )
    parser_review.add_argument(
        "-f",
        "--save-frequency",
        help="Update the frequency table with the current subtitle file's frequency data",
        action="store_true",
    )
    parser_review.set_defaults(func=lambda args: cmd_review(args, data))

    # stats
    parser_stats = subparsers.add_parser("stats", help="show stats")
    parser_stats.set_defaults(func=lambda args: cmd_stats(args, data))

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
