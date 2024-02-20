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

FILE_PATH = "./data.json"


def apply_migrations(json_data):
    if "version" not in json_data:
        init_version = 0
        # migrate from old unique key to pure lemma
        for group in {"seen", "ignore"}:
            for k in list(json_data[group].keys()):
                del json_data[group][k]
                new_k = k.split(",")[0]
                json_data[group][new_k] = True

        json_data["version"] = 1
        save_json(json_data, FILE_PATH)
    else:
        init_version = json_data["version"]

    if json_data["version"] == 1:
        # migrate to version 2, which stores everything as one dictionary
        new_dict = {}
        for word in json_data["seen"]:
            new_dict[word] = WordState.Seen

        for word in json_data["ignore"]:
            new_dict[word] = WordState.Ignore

        json_data["words"] = new_dict
        del json_data["seen"]
        del json_data["ignore"]
        json_data["version"] = 2
        save_json(json_data, FILE_PATH)

    if init_version != json_data["version"]:
        print(f"Migrated stored data (v{init_version} -> v{json_data['version']}).")


if __name__ == "__main__":
    try:
        with open(FILE_PATH, "r") as file:
            json_data = json.load(file)
    except FileNotFoundError:
        json_data = {"words": {}, "version": 2}
        save_json(json_data, FILE_PATH)

    apply_migrations(json_data)

    parser = argparse.ArgumentParser(description="Process an input file.")
    parser.add_argument("-i", "--input", help="Path to the input file", required=True)
    parser.add_argument("-o", "--output", help="Path to the output csv", required=True)
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

    words, (seen_count, ignore_count) = filter_word_list(
        tagger(processed_contents), json_data, jam
    )
    freq_table = FrequencyTable("./jp_freq.csv")
    words = freq_table.sorted(words)

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
