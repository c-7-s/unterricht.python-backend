from pydantic import BaseModel
from api.config import InterfaceConfig
import yaml


def read_yaml_config(file_path) -> InterfaceConfig:
    try:
        with open(file_path, 'r') as file:
            config_data = yaml.safe_load(file)
        return config_data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error reading YAML file '{file_path}': {e}")
        return None
