import json
import fugashi
import argparse
import srt
from pathlib import Path
from jamdict import Jamdict
import csv
from .filter import filter_word_list
from .util import to_unique_key
from .interface import select_word_forms, MainOptions, show_main_options
from .frequency import FrequencyTable


def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def process_srt(srt_contents):
    result = ""
    for s in srt.parse(srt_contents):
        result += s.content
        result += "\n"
    return result


FILE_PATH = "./data.json"


def apply_migrations(json_data):
    if "version" not in json_data:
        print("Migrating stored data (v0 -> v1).")
        # migrate from old unique key to pure lemma
        for group in {"seen", "ignore"}:
            for k in list(json_data[group].keys()):
                del json_data[group][k]
                new_k = k.split(",")[0]
                json_data[group][new_k] = True

        json_data["version"] = 1
        save_json(json_data, FILE_PATH)


if __name__ == "__main__":
    try:
        with open(FILE_PATH, "r") as file:
            json_data = json.load(file)
    except FileNotFoundError:
        json_data = {"seen": {}, "ignore": {}, "version": 1}
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
    jam = Jamdict()

    words = filter_word_list(tagger(processed_contents), json_data, jam)
    freq_table = FrequencyTable("./jp_freq.csv")
    words = freq_table.sorted(words)

    print(f"{len(words)} unknown words found.")

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
            json_data["ignore"][to_unique_key(word)] = True
            save_json(json_data, FILE_PATH)
        elif option == MainOptions.Known:
            json_data["seen"][to_unique_key(word)] = True
            save_json(json_data, FILE_PATH)
        elif option == MainOptions.Add:
            (kanji, kana, sense) = select_word_forms(word, data)
            json_data["seen"][to_unique_key(word)] = True
            save_json(json_data, FILE_PATH)
            with open(args.output, "a", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows([(kanji, kana, sense)])
