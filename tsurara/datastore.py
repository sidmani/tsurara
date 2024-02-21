import json
from .util import save_json
from .migrations import apply_migrations


class Datastore:
    def __init__(self, path):
        try:
            with open(path, "r") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            print(f"Creating new data file at {path}")
            self.data = {"words": {}, "seen_files": {}, "version": 4}
            save_json(self.data, path)

        self.path = path

    def save(self):
        save_json(self.data, self.path)

    def set_word_state(self, word, state):
        self.data["words"][word] = state

    def get_word_state(self, word):
        if word in self.data["words"]:
            return self.data["words"][word]
        return None

    def add_seen_file(self, filename):
        self.data["seen_files"][filename] = True

    def has_seen_file(self, filename):
        return filename in self.data["seen_files"]

    def migrate(self):
        return apply_migrations(self.data, self.path)
