import json
from utils.paths import get_root_path


def save_resp_to_json(name: str, data: any):
    with open(get_root_path() + '/' + name + ".json", "w") as f:
        json.dump(data, f)
