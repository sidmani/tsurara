import json
from .util import save_json


class FrequencyTable:
    def __init__(self, path):
        with open(path, "r") as file:
            self.data = json.load(file)
        self.path = path

    def word_to_freq(self, word):
        if word in self.data["words"]:
            return self.data["words"][word]

        return 0

    def add_words(self, words):
        for word in words:
            if word in self.data["words"]:
                self.data["words"][word] += 1
            else:
                self.data["words"][word] = 1

    def save_data(self):
        save_json(self.data, self.path)
