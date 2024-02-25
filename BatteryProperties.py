from pathlib import Path
import os
import re
import datetime
from dataclasses import dataclass
import json


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

    def to_json(self, path: Path):
        with open(path, "w", encoding="utf8") as f:
            json.dump(self.to_dict(), f, indent=True)


    def to_dict(self) -> dict:
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
            r"present:\s*(\w+)\s*rechargeable:\s*(\w+)\s*state:\s*([\w-]+)\s*"\
            r"warning-level:\s*(\w+)\s*energy:\s*([\d.]+)(\s*\w+)\s*"\
            r"energy-empty:\s*([\d.]+)(\s*\w+)\s*energy-full:\s*([\d.]+)(\s*\w+)\s*"\
            r"energy-full-design:\s*([\d.]+)(\s*\w+)\s*energy-rate:\s*([\d.]+)(\s*\w+)\s*"\
            r"voltage:\s*([\d.]+)(\s*\w+)\s*charge-cycles:\s*([\d.]+)\s*"\
            r"(?:time to (\w+):\s*([\d.]+)(\s*\w+)\s*)?percentage:\s*([\d.]+)(%)\s*"\
            r"capacity:\s*([\d.]+)(%)\s*technology:\s*([\w-]+)\s*icon-name:\s*'([\w-]+)'\s*"
        data = os.popen('upower -i /org/freedesktop/UPower/devices/battery_BAT0').read()

        try:
            match = next(re.finditer(pattern, data))
        except StopIteration:
            print("<< DEBUG INFO START >>")
            print(data)
            print(f"\n\nPatterm:\n'{pattern}'")
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
        elif match.group(26) is None:
            time_to_full = None
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
