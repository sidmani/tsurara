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


def filter_word_list(words, json_data, jam):
    filtered_words = []
    dupes = set()

    seen_count = 0
    ignore_count = 0

    for word in tqdm(words):
        if filter_condition(word):
            continue

        unique_key = to_unique_key(word)
        if unique_key in dupes:
            continue
        dupes.add(unique_key)

        if unique_key in json_data["words"]:
            if json_data["words"][unique_key] == WordState.Seen:
                seen_count += 1
                continue
            elif json_data["words"][unique_key] == WordState.Ignore:
                ignore_count += 1
                continue

        data = jam.lookup(word.feature.lemma)
        if len(data.entries) == 0:
            continue

        filtered_words.append(word)

    return filtered_words, (seen_count, ignore_count)
