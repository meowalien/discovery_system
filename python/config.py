import os
import yaml

# 設定檔路徑，這裡假設 conf 資料夾與 config.py 在同一層
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'conf', 'config.yaml')

with open(CONFIG_PATH, 'r') as f:
    CONFIG = yaml.safe_load(f)