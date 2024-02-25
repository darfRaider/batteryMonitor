from pathlib import Path
import os
import pandas as pd
from BatteryProperties import BatteryProperties

BACKUP_DIR = Path("./backups")
PATH_TO_UPOWER_HISTORY = Path("/var/lib/upower/")
UPOWER_ID_NAME = "5B10W51869-52-511"
UPOWER_DATA_DIR = BACKUP_DIR / "upower.csv"
UPOWER_FILE_POSFIX = [
    "history-charge",
    "history-rate",
    "history-time-empty",
    "history-time-full"
]
EXPECTED_UPOWER_FILES = [
    f"{x}-{UPOWER_ID_NAME}.dat" for x in UPOWER_FILE_POSFIX
]
# Create and check paths
UPOWER_DOC_DIR = BACKUP_DIR / "upower"
UPOWER_BACKUP_HIST_DIR = BACKUP_DIR / "upower_hist"
os.makedirs(UPOWER_DOC_DIR, exist_ok=True)
os.makedirs(UPOWER_BACKUP_HIST_DIR, exist_ok=True)

for file in os.listdir(PATH_TO_UPOWER_HISTORY):
    assert UPOWER_ID_NAME in file, ""
    assert file in EXPECTED_UPOWER_FILES


if not os.path.exists(UPOWER_DATA_DIR):
    df_old = pd.DataFrame()
else:
    df_old = pd.read_csv(UPOWER_DATA_DIR, dtype={"ts": int, "value": float})

data = []
for file in UPOWER_FILE_POSFIX:
    filepath = PATH_TO_UPOWER_HISTORY / f"{file}-{UPOWER_ID_NAME}.dat"
    # assert UPOWER_ID_NAME in file, ""
    # assert file in EXPECTED_UPOWER_FILES
    with open(filepath, "r", encoding="utf8") as f:
        tmp_df = pd.DataFrame(
            [[*x.split("\t"), *[file]] for x in f.read().splitlines()],
            columns=["ts", "value", "state", "source"]
        )
        data.append(tmp_df)
        
df = pd.concat(data).sort_values(["ts", "source"]).astype({"ts": int, "value": float})
df_new = pd.concat([df_old, df]).drop_duplicates()
print(f"Appended {len(df_new)-len(df_old)} records")
df_new.to_csv(UPOWER_DATA_DIR, index=False)



assert os.path.exists(PATH_TO_UPOWER_HISTORY), "Path specified in 'PATH_TO_UPOWER_HISTORY' does not exist!"

props = BatteryProperties.get_props_from_upower_cmd()
props.to_json(UPOWER_DOC_DIR / f"{props.created_utc}.json")


for file in os.listdir(PATH_TO_UPOWER_HISTORY):
    filepath = PATH_TO_UPOWER_HISTORY / file
    if file not in EXPECTED_UPOWER_FILES:
        raise ValueError(f"The file {file} was not expected in upower folder.")
    # copyfile(, UPOWER_BACKUP_HIST_DIR / file)
