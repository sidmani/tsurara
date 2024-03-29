from pathlib import Path
import fugashi
from pathlib import Path
from jamdict import Jamdict
import csv

from .datastore import Datastore
from .filter import dedupe_word_list, filter_non_words
from .util import to_unique_key, process_srt, WordState
from .interface import select_word_forms, MainOptions, show_main_options


def cmd_review(args, datastore: Datastore):
    jam = Jamdict(memory_mode=True)

    if args.input:
        input_path = Path(args.input)
        with open(input_path, "r") as file:
            file_contents = file.read()

        if input_path.suffix == ".srt":
            processed_contents = process_srt(file_contents)
        else:
            processed_contents = file_contents

        tagger = fugashi.Tagger()
        words = filter_non_words(tagger(processed_contents), datastore, jam)
        words: list[str] = list(map(lambda w: w.feature.lemma, words))

        if args.save_frequency:
            if not datastore.has_seen_file(input_path.name):
                datastore.add_words_to_freq(words)
                datastore.add_seen_file(input_path.name)
                datastore.save()
                print("Updated frequency data.")
            else:
                print("Not updating frequency data with known file.")
    elif args.stored:
        words = list(datastore.get_freq().keys())
    else:
        exit()

    words, (seen_count, ignore_count) = dedupe_word_list(words, datastore)
    words = sorted(words, key=lambda w: datastore.word_to_freq(w), reverse=True)

    print(
        f"{len(words) + seen_count + ignore_count} unique words ({len(words)} new/{seen_count} seen/{ignore_count} ignore)"
    )

    idx = -1
    while idx < len(words) - 1:
        idx += 1
        word = words[idx]
        data = jam.lookup(word)

        meanings = "\n".join(map(lambda e: e.text(), data.entries))
        option = show_main_options(
            f"{idx + 1}/{len(words)} {word}",
            meanings,
        )

        if option == MainOptions.Quit:
            break
        elif option == MainOptions.Ignore:
            datastore.set_word_state(word, WordState.Ignore)
            datastore.save()
        elif option == MainOptions.Known:
            datastore.set_word_state(word, WordState.Seen)
            datastore.save()
        elif option == MainOptions.Add:
            result = select_word_forms(word, data)
            if result is None:
                idx -= 1
                continue

            (kanji, kana, sense) = result
            datastore.set_word_state(word, WordState.Seen)
            datastore.save()
            with open(args.output, "a", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows([(kanji, kana, sense)])
