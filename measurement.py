import sched, time
from pathlib import Path
import os
from BatteryProperties import BatteryProperties

BACKUP_DIR = Path("./backups")
UPOWER_DOC_DIR = BACKUP_DIR / "upower"
os.makedirs(UPOWER_DOC_DIR, exist_ok=True)

def do_something(scheduler): 
    # schedule the next call first
    scheduler.enter(10, 1, do_something, (scheduler,))
    print("Doing stuff...")
    # then do your stuff
    try:
        props = BatteryProperties.get_props_from_upower_cmd()
    except Exception:
        pass
    props.to_json(UPOWER_DOC_DIR / f"{props.created_utc}.json")


my_scheduler = sched.scheduler(time.time, time.sleep)
my_scheduler.enter(10, 1, do_something, (my_scheduler,))
my_scheduler.run()
