from tqdm import tqdm
from .util import to_unique_key, WordState

BASE_EXCLUDE_LIST = {"　", "．"}


def contains_full_width_roman(text):
    for char in text:
        if "\uff21" <= char <= "\uff3a" or "\uff41" <= char <= "\uff5a":
            return True
    return False


def filter_condition(word):
    return (
        word.feature.pos1 == "助詞"
        or word.feature.pos1 == "代名詞"
        or word.feature.pos1 == "感動詞"
        or word.feature.pos1 == "助動詞"
        or word.feature.pos1 == "接尾辞"
        or word.feature.pos1 == "補助記号"
        or word.feature.pos2 == "数詞"
        or word.feature.pos3 == "人名"
        or word.feature.pos3 == "地名"
        or word.surface in BASE_EXCLUDE_LIST
        or word.feature.lemma is None
        or contains_full_width_roman(word.feature.lemma)
    )


def filter_non_words(words, datastore, jam):
    result = []
    known_ok = set()
    for word in tqdm(words):
        unique_key = to_unique_key(word)
        if unique_key in known_ok:
            result.append(word)
            continue

        if filter_condition(word):
            continue

        # if the word is in the datastore or it's in the frequency table
        # it's known valid, so skip the slow dictionary lookup
        if (
            datastore.get_word_state(to_unique_key(word)) is not None
            or datastore.word_to_freq(word) > 0
            or len(jam.lookup(word.feature.lemma).entries) > 0
        ):
            known_ok.add(unique_key)
            result.append(word)
    return result


def dedupe_word_list(words, datastore):
    filtered_words = []
    dupes = set()

    seen_count = 0
    ignore_count = 0

    for word in words:
        unique_key = to_unique_key(word)
        if unique_key in dupes:
            continue
        dupes.add(unique_key)

        word_state = datastore.get_word_state(unique_key)
        if word_state is not None:
            if word_state == WordState.Seen:
                seen_count += 1
                continue
            elif word_state == WordState.Ignore:
                ignore_count += 1
                continue

        filtered_words.append(word)

    return filtered_words, (seen_count, ignore_count)
