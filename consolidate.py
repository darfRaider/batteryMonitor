import pandas as pd
from pathlib import Path
import os
import re
import datetime
import warnings
from shutil import copyfile
from dataclasses import dataclass
import json


BACKUP_DIR = Path("./backups")
UPOWER_DOC_DIR = BACKUP_DIR / "upower"
UPOWER_BACKUP_HIST_DIR = BACKUP_DIR / "upower_hist"
UPOWER_ID_NAME = "5B10W51869-52-511"


data = []
for file in os.listdir(UPOWER_DOC_DIR):
    with open(UPOWER_DOC_DIR / file, "r", encoding="utf8") as f:
        data.append(json.load(f))

df = pd.DataFrame(data)
print("end")