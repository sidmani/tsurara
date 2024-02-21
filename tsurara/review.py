from pathlib import Path
import fugashi
from pathlib import Path
from jamdict import Jamdict
import csv

from .datastore import Datastore
from .filter import filter_word_list
from .util import to_unique_key, save_json, process_srt, WordState
from .interface import select_word_forms, MainOptions, show_main_options
from .frequency import FrequencyTable


FREQUENCY_DATA_PATH = "jp_freq.json"


def cmd_review(args, datastore: Datastore):
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
        if not datastore.has_seen_file(input_path.name):
            freq_table.add_words(map(lambda w: w.feature.lemma, unfiltered_words))
            freq_table.save_data()
            datastore.add_seen_file(input_path.name)
            datastore.save()
            print("Updated frequency data.")
        else:
            print("Not updating frequency data with known file.")

    words, (seen_count, ignore_count) = filter_word_list(
        unfiltered_words, datastore, jam
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
            datastore.set_word_state(to_unique_key(word), WordState.Ignore)
            datastore.save()
        elif option == MainOptions.Known:
            datastore.set_word_state(to_unique_key(word), WordState.Seen)
            datastore.save()
        elif option == MainOptions.Add:
            (kanji, kana, sense) = select_word_forms(word, data)
            datastore.set_word_state(to_unique_key(word), WordState.Seen)
            datastore.save()
            with open(args.output, "a", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows([(kanji, kana, sense)])
