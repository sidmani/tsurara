def to_unique_key(word):
    return ",".join((word.feature.lemma, word.feature.pos1))
