def is_japanese_kanji(char):
    code_point = ord(char)
    return 0x4E00 <= code_point <= 0x9FAF


def get_known_kanji(words):
    known_kanji = set()
    for word in words:
        for char in word:
            if is_japanese_kanji(char):
                known_kanji.add(char)

    return known_kanji


def cmd_stats(args, datastore):
    known_words = datastore.get_words().keys()
    known_kanji = get_known_kanji(known_words)
    print(f"{len(known_words)} known words with {len(known_kanji)} unique kanji.")
