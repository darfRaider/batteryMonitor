from pathlib import Path
import os
import re
import datetime
import warnings
from shutil import copyfile
from dataclasses import dataclass
import json
import pandas as pd

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
df_new = pd.concat([df_old, df]).drop_duplicates()
print(f"Appended {len(df_new)-len(df_old)} records")
df_new.to_csv(UPOWER_DATA_DIR, index=False)

@dataclass
class BatteryProperties:
    created_utc: int
    native_path: str
    vendor: str
    model: str
    technology: str
    model: str
    serial_nr: int
    power_supply: bool
    updated: str
    state: str
    energy: float
    energy_empty: float
    energy_full: float
    energy_full_design: float
    energy_rate: float
    voltage: float
    charge_cycles: int
    time_to_empty: str
    time_to_full : str
    percentage: float
    capacity_percent: float

    def to_json(self) -> dict:
        return {
            "created_utc": self.created_utc,
            "native_path": self.native_path,
            "vendor": self.vendor,
            "model": self.model,
            "technology": self.technology,
            "model": self.model,
            "serial_nr": self.serial_nr,
            "power_supply": self.power_supply,
            "updated": self.updated,
            "state": self.state,
            "energy": self.energy,
            "energy_empty": self.energy_empty,
            "energy_full": self.energy_full,
            "energy_full_design": self.energy_full_design,
            "energy_rate": self.energy_rate,
            "voltage": self.voltage,
            "charge_cycles": self.charge_cycles,
            "time_to_empty": self.time_to_empty,
            "time_to_full" : self.time_to_full,
            "percentage": self.percentage,
            "capacity_percent": self.capacity_percent
        }

    @staticmethod
    def get_props_from_upower_cmd():
        timestamp_now = int(datetime.datetime.now().timestamp())
        pattern = r"native-path:\s*(\w+)\s*vendor:\s*(\w+)\s*model:\s*(\w+)"\
            r"\s*serial:\s*(\w+)\s*power supply:\s*(\w+)\s*updated:\s*([^\n]+)\s*"\
            r"has history:\s*(\w+)\s*has statistics:\s*(\w+)\s*battery\s*"\
            r"present:\s*(\w+)\s*rechargeable:\s*(\w+)\s*state:\s*(\w+)\s*"\
            r"warning-level:\s*(\w+)\s*energy:\s*([\d.]+)(\s*\w+)\s*"\
            r"energy-empty:\s*([\d.]+)(\s*\w+)\s*energy-full:\s*([\d.]+)(\s*\w+)\s*"\
            r"energy-full-design:\s*([\d.]+)(\s*\w+)\s*energy-rate:\s*([\d.]+)(\s*\w+)\s*"\
            r"voltage:\s*([\d.]+)(\s*\w+)\s*charge-cycles:\s*([\d.]+)\s*"\
            r"time to (\w+):\s*([\d.]+)(\s*\w+)\s*percentage:\s*([\d.]+)(%)\s*"\
            r"capacity:\s*([\d.]+)(%)\s*technology:\s*([\w-]+)\s*icon-name:\s*'([\w-]+)'\s*"
        data = os.popen('upower -i /org/freedesktop/UPower/devices/battery_BAT0').read()

        try:
            match = next(re.finditer(pattern, data))
        except StopIteration:
            print("<< DEBUG INFO START >>")
            print(data)
            print("<< DEBUG INFO END >>")
            raise StopIteration("Could not match output of command by regex")
        try:
            energy = float(match.group(13))
            energy_empty = float(match.group(15))
            energy_full = float(match.group(17))
            energy_full_design = float(match.group(19))
            energy_rate = float(match.group(21))
            voltage = float(match.group(23))
            charge_cycles = int(match.group(25))
            percentage = float(match.group(29))
            capacity_percent = float(match.group(31))
        except Exception as e:
            print(data)
            print(f"Unable to cast data: {repr(e)}")
        time_to_empty = None
        time_to_full = None
        if match.group(26) == "empty":
            time_to_empty = match.group(27)
        elif match.group(26) == "full":
            time_to_full = match.group(27)
        else:
            raise ValueError(f"Unexpected match value '{match.group(26)}'")

        return BatteryProperties(
            created_utc = timestamp_now,
            native_path = match.group(1),
            vendor = match.group(2),
            model = match.group(3),
            technology = match.group(33),
            serial_nr = match.group(4),
            power_supply = True if match.group(5) == "yes" else False,
            updated = match.group(6),
            state = match.group(11),
            energy = energy,
            energy_empty = energy_empty,
            energy_full = energy_full,
            energy_full_design = energy_full_design,
            energy_rate = energy_rate,
            voltage = voltage,
            charge_cycles = charge_cycles,
            time_to_empty = time_to_empty,
            time_to_full = time_to_full,
            percentage = percentage,
            capacity_percent = capacity_percent,
        )




# Create and check paths
UPOWER_DOC_DIR = BACKUP_DIR / "upower"
UPOWER_BACKUP_HIST_DIR = BACKUP_DIR / "upower_hist"
os.makedirs(UPOWER_DOC_DIR, exist_ok=True)
os.makedirs(UPOWER_BACKUP_HIST_DIR, exist_ok=True)

assert os.path.exists(PATH_TO_UPOWER_HISTORY), "Path specified in 'PATH_TO_UPOWER_HISTORY' does not exist!"

props = BatteryProperties.get_props_from_upower_cmd()

with open(UPOWER_DOC_DIR / f"{props.created_utc}.json", "w", encoding="utf8") as f:
    json.dump(props.to_json(), f, indent=True)


for file in os.listdir(PATH_TO_UPOWER_HISTORY):
    filepath = PATH_TO_UPOWER_HISTORY / file
    if file not in EXPECTED_UPOWER_FILES:
        raise ValueError(f"The file {file} was not expected in upower folder.")
    # copyfile(, UPOWER_BACKUP_HIST_DIR / file)
