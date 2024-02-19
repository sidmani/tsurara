import json
import srt


def to_unique_key(word):
    return word.feature.lemma


def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def process_srt(srt_contents):
    result = ""
    for s in srt.parse(srt_contents):
        result += s.content
        result += "\n"
    return result
