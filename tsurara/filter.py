from tqdm import tqdm
from .util import to_unique_key

BASE_EXCLUDE_LIST = {"　", "．"}


def filter_word_list(words, json_data, jam):
    filtered_words = []
    dupes = set()

    for word in tqdm(words):
        if (
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
        ):
            continue

        unique_key = to_unique_key(word)
        if (
            unique_key in dupes
            or unique_key in json_data["seen"]
            or unique_key in json_data["ignore"]
        ):
            continue

        dupes.add(unique_key)
        data = jam.lookup(word.feature.lemma)
        if len(data.entries) == 0:
            continue

        filtered_words.append(word)

    return filtered_words
