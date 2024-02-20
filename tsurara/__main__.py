import json
import fugashi
import argparse
from pathlib import Path
from jamdict import Jamdict
import csv
from .filter import filter_word_list
from .util import to_unique_key, save_json, process_srt, WordState
from .interface import select_word_forms, MainOptions, show_main_options
from .frequency import FrequencyTable
from .migrations import apply_migrations

FILE_PATH = "data.json"
FREQUENCY_DATA_PATH = "jp_freq.json"

if __name__ == "__main__":
    try:
        with open(FILE_PATH, "r") as file:
            json_data = json.load(file)
    except FileNotFoundError:
        print(f"Creating new data file at {FILE_PATH}")
        json_data = {"words": {}, "seen_files": {}, "version": 3}
        save_json(json_data, FILE_PATH)

    (old_version, new_version) = apply_migrations(json_data, FILE_PATH)
    if old_version != new_version:
        print(f"Migrated stored data (v{old_version} -> v{new_version}).")

    parser = argparse.ArgumentParser(description="Process an input file.")
    parser.add_argument("-i", "--input", help="Path to the input file", required=True)
    parser.add_argument("-o", "--output", help="Path to the output csv", required=True)
    parser.add_argument(
        "-f",
        "--save-frequency",
        help="Update the frequency table with the current subtitle file's frequency data",
        action="store_true",
    )
    args = parser.parse_args()
    input_path = Path(args.input)
    with open(input_path, "r") as file:
        file_contents = file.read()

    if input_path.suffix == ".srt":
        processed_contents = process_srt(file_contents)
    else:
        processed_contents = file_contents

    tagger = fugashi.Tagger()
    jam = Jamdict(memory_mode=True)
    freq_table = FrequencyTable(FREQUENCY_DATA_PATH)

    unfiltered_words = list(tagger(processed_contents))
    if args.save_frequency:
        if args.input not in json_data["seen_files"]:
            freq_table.add_words(map(lambda w: w.feature.lemma, unfiltered_words))
            freq_table.save_data()
            json_data["seen_files"][args.input] = True
            save_json(json_data, FILE_PATH)
            print("Updated frequency data.")
        else:
            print("Not updating frequency data with known file.")

    words, (seen_count, ignore_count) = filter_word_list(
        unfiltered_words, json_data, jam
    )
    words = sorted(
        words, key=lambda w: freq_table.word_to_freq(w.feature.lemma), reverse=True
    )

    print(
        f"{len(words) + seen_count + ignore_count} unique words ({len(words)} new/{seen_count} seen/{ignore_count} ignore)"
    )

    count = 0
    for word in words:
        count += 1
        data = jam.lookup(word.feature.lemma)

        meanings = "\n".join(map(lambda e: e.text(), data.entries))
        option = show_main_options(
            f"{count}/{len(words)} {word.feature.lemma}",
            meanings,
        )

        if option == MainOptions.Quit:
            break
        elif option == MainOptions.Ignore:
            json_data["words"][to_unique_key(word)] = WordState.Ignore
            save_json(json_data, FILE_PATH)
        elif option == MainOptions.Known:
            json_data["words"][to_unique_key(word)] = WordState.Seen
            save_json(json_data, FILE_PATH)
        elif option == MainOptions.Add:
            (kanji, kana, sense) = select_word_forms(word, data)
            json_data["words"][to_unique_key(word)] = WordState.Seen
            save_json(json_data, FILE_PATH)
            with open(args.output, "a", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows([(kanji, kana, sense)])
