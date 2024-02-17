import csv


class FrequencyTable:
    def __init__(self, path):
        with open(path, newline="") as csvfile:
            self.freq = {}
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                self.freq[row[2]] = int(row[1])

    def word_to_freq(self, word):
        if word.feature.lemma in self.freq:
            return self.freq[word.feature.lemma]

        return 0

    def sorted(self, words):
        return sorted(words, key=lambda w: self.word_to_freq(w), reverse=True)
