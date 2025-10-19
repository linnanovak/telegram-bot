import csv
import datetime
import json
from threading import Lock
from zoneinfo import ZoneInfo
from pathlib import Path

TZ = ZoneInfo("America/Los_Angeles")
EVENTS_FILE = "data/events.csv"
_events_lock = Lock()

def track_event(user, event: str, data: dict | None = None):
    """Записывает событие в CSV: ts, user_id, username, event, data(json)"""
    row = {
        "ts": datetime.datetime.now(tz=TZ).isoformat(timespec="seconds"),
        "user_id": getattr(user, "id", None),
        "username": getattr(user, "username", "") or "",
        "event": event,
        "data": json.dumps(data or {}, ensure_ascii=False),
    }
    with _events_lock:
        newfile = not Path(EVENTS_FILE).exists()
        with open(EVENTS_FILE, "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=row.keys())
            if newfile:
                w.writeheader()
            w.writerow(row)
