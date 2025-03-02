import os
import yaml

CONFIG_PATH = os.path.join('conf', 'config.yaml')

with open(CONFIG_PATH, 'r') as f:
    CONFIG = yaml.safe_load(f)