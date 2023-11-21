import json
import os
from typehints.bling import Access_Data
from utils.paths import get_root_path

def get_json_file_path():
    project_root = get_root_path()  # Go up one directory
    access_data_path = os.path.join(project_root, "access_data.json")
    return access_data_path


def get_access_data():
    print("Lendo os dados de acesso...")
    # Load configuration
    with open(get_json_file_path()) as config_file:
        config_data: Access_Data = json.load(config_file)
        return config_data


def update_access_data(new_access_data: Access_Data):
    with open(get_json_file_path(), "w") as f:
        json.dump(new_access_data, f)
    print('dados de acesso atualizados com sucesso!')
