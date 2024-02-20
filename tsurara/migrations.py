from .util import save_json, WordState


def apply_migrations(json_data, file_path):
    if "version" not in json_data:
        init_version = 0
        # migrate from old unique key to pure lemma
        for group in {"seen", "ignore"}:
            for k in list(json_data[group].keys()):
                del json_data[group][k]
                new_k = k.split(",")[0]
                json_data[group][new_k] = True

        json_data["version"] = 1
        save_json(json_data, file_path)
    else:
        init_version = json_data["version"]

    if json_data["version"] == 1:
        # migrate to version 2, which stores everything as one dictionary
        new_dict = {}
        for word in json_data["seen"]:
            new_dict[word] = WordState.Seen

        for word in json_data["ignore"]:
            new_dict[word] = WordState.Ignore

        json_data["words"] = new_dict
        del json_data["seen"]
        del json_data["ignore"]
        json_data["version"] = 2
        save_json(json_data, file_path)

    if json_data["version"] == 2:
        # add seen_files dict
        json_data["seen_files"] = {}
        json_data["version"] = 3

    return (init_version, json_data["version"])
