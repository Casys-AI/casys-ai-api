# src/config.py
import yaml
from pathlib import Path


#TODO faire une vraie différence entre la config système et le stockage des informatiosn des projets
def load_global_config():
    config_path = Path(__file__).parent.parent / "../config.yaml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


GLOBAL_CONFIG = load_global_config()
