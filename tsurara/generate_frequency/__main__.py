from tsurara.filter import filter_condition
import argparse
import srt
from tqdm import tqdm
from pathlib import Path
import fugashi
from jamdict import Jamdict
import csv
import os


def list_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)


ALLOWED_FILETYPES = {".srt"}


def subtitles_to_str(path: Path):
    if path.suffix not in ALLOWED_FILETYPES:
        return None

    try:
        with open(path, "r") as file:
            contents = file.read()
    except Exception:
        print("could not open " + str(path))
        return None

    try:
        if path.suffix == ".srt":
            result = ""
            for s in srt.parse(contents):
                result += s.content
                result += "\n"

            print("done: " + str(path))
            return result
    except Exception as e:
        print("could not parse " + str(path))

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process an input file.")
    parser.add_argument("-i", "--input", help="Path to the input folder", required=True)
    parser.add_argument("-o", "--output", help="Path to the output csv", required=True)
    args = parser.parse_args()

    files = list_files(args.input)
    frequency = {}
    tagger = fugashi.Tagger()
    for file_path in files:
        contents = subtitles_to_str(Path(file_path))
        if contents is None:
            continue
        words = tagger(contents)
        words = filter(lambda w: not filter_condition(w), words)
        for word in words:
            if word.feature.lemma in frequency:
                frequency[word.feature.lemma] += 1
            else:
                frequency[word.feature.lemma] = 1

    jam = Jamdict(memory_mode=True)
    result = []
    for lemma in tqdm(frequency.keys()):
        lookup = jam.lookup(lemma)
        if len(lookup.entries) == 0:
            continue

        result.append((frequency[lemma], lemma))

    result = map(
        lambda x: (x[0] + 1, x[1][0], x[1][1]),
        enumerate(sorted(result, key=lambda x: x[0], reverse=True)),
    )

    with open(args.output, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(result)
