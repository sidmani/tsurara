import json
import fugashi
import argparse
import srt
from pathlib import Path
from jamdict import Jamdict
import csv
from .filter import filter_word_list
from .util import to_unique_key
from .interface import show_tmenu, MainOptions, show_main_options


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

        if option == MainOptions.Quit:
            break

        if option == MainOptions.Ignore:
            json_data["ignore"][to_unique_key(word)] = True
            save_json(json_data, FILE_PATH)
            continue

        json_data["seen"][to_unique_key(word)] = True

        if option == MainOptions.Known:
            save_json(json_data, FILE_PATH)
            continue
        if option == MainOptions.Add:
            if len(data.entries) == 1:
                entry = data.entries[0]
            else:
                _, entry_idx = show_tmenu(
                    [e.text() for e in data.entries],
                    f"Which entry for {word.feature.lemma} ({data.entries[0].kana_forms[0]})?",
                )
                entry = data.entries[entry_idx]

            if len(entry.kana_forms) == 1:
                kana = entry.kana_forms[0].text
            else:
                (options, idx) = show_tmenu(
                    [e.text for e in entry.kana_forms],
                    f"Which kana form for {word.feature.lemma} ({entry.kana_forms[0]})?",
                )
                kana = options[idx]

            if len(entry.kanji_forms) == 0:
                kanji = kana
            elif len(entry.kanji_forms) == 1:
                kanji = entry.kanji_forms[0].text
            else:
                (options, idx) = show_tmenu(
                    [e.text for e in entry.kanji_forms] + [kana],
                    f"Which kanji form for {word.feature.lemma} ({kana})?",
                )
                kanji = options[idx]

            if len(entry.senses) == 1:
                sense = entry.senses[0].gloss[0].text
            else:
                (options, idxs) = show_tmenu(
                    [s.gloss[0].text for s in entry.senses],
                    f"Which definition for {kanji} ({kana})?",
                    multi_select=True,
                )
                if len(options) == 0:
                    raise Exception("You must select at least one definition!")

                sense = "; ".join([options[i] for i in idxs])

            save_json(json_data, FILE_PATH)
            with open(args.output, "a", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows([(kanji, kana, sense)])
