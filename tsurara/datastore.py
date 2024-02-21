import json
from pathlib import Path
from .util import save_json, WordState


class Datastore:
    def __init__(self, path):
        try:
            with open(path, "r") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            print(
                "WARNING: the default location for the data file changed to ~/.tsurara.json. You might need to move your data manually."
            )
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
        if "version" not in self.data:
            init_version = 0
            # migrate from old unique key to pure lemma
            for group in {"seen", "ignore"}:
                for k in list(self.data[group].keys()):
                    del self.data[group][k]
                    new_k = k.split(",")[0]
                    self.data[group][new_k] = True

            self.data["version"] = 1
            self.save()
        else:
            init_version = self.data["version"]

        if self.data["version"] == 1:
            # migrate to version 2, which stores everything as one dictionary
            new_dict = {}
            for word in self.data["seen"]:
                new_dict[word] = WordState.Seen

            for word in self.data["ignore"]:
                new_dict[word] = WordState.Ignore

            self.data["words"] = new_dict
            del self.data["seen"]
            del self.data["ignore"]
            self.data["version"] = 2
            self.save()

        if self.data["version"] == 2:
            # add seen_files dict
            self.data["seen_files"] = {}
            self.data["version"] = 3
            self.save()

        if self.data["version"] == 3:
            # seen files use filename instead of full path
            new_seen_files = {}
            for p in self.data["seen_files"].keys():
                new_seen_files[Path(p).name] = True

            self.data["seen_files"] = new_seen_files
            self.data["version"] = 4
            self.save()

        return (init_version, self.data["version"])
