import json
import fugashi
import argparse
import srt
from pathlib import Path
from jamdict import Jamdict
import csv
from .filter import filter_word_list
from .util import to_unique_key
from .interface import select_word_forms, show_tmenu, MainOptions, show_main_options


def save_json(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def process_srt(srt_contents):
    result = ""
    for s in srt.parse(srt_contents):
        result += s.content
        result += "\n"
    return result


FILE_PATH = "./data.json"

if __name__ == "__main__":
    try:
        with open(FILE_PATH, "r") as file:
            json_data = json.load(file)
    except FileNotFoundError:
        json_data = {"seen": {}, "ignore": {}}
        save_json(json_data, FILE_PATH)

    parser = argparse.ArgumentParser(description="Process an input file.")
    parser.add_argument("-i", "--input", help="Path to the input file")
    parser.add_argument("-o", "--output", help="Path to the output file")
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

    print(f"{len(words)} unknown words found.")
    count = 0

    for word in words:
        count += 1
        data = jam.lookup(word.feature.lemma)

        option = show_main_options(
            f"{count}/{len(words)} {word.feature.lemma}",
            f"({data.entries[0].kana_forms[0]}) - {data.entries[0].senses[0].text()}",
        )

        if option == MainOptions.Skip:
            continue
        elif option == MainOptions.Quit:
            break
        elif option == MainOptions.Ignore:
            json_data["ignore"][to_unique_key(word)] = True
            save_json(json_data, FILE_PATH)
            continue
        elif option == MainOptions.Known:
            json_data["seen"][to_unique_key(word)] = True
            save_json(json_data, FILE_PATH)
            continue
        elif option == MainOptions.Add:
            (kanji, kana, sense) = select_word_forms(word, data)
            json_data["seen"][to_unique_key(word)] = True
            save_json(json_data, FILE_PATH)
            with open(args.output, "a", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows([(kanji, kana, sense)])
