# -*- coding: utf-8 -*-
"""
Database helper - CSV logs, settings, enrolled-profile bookkeeping.

All paths are anchored to the project folder (not the current working
directory), so the app works no matter where `streamlit run` is started from.
"""

import json
import threading
import uuid
import datetime
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------
# PATHS
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWN_FACES_DIR = DATA_DIR / "known_faces"
UNAUTHORIZED_DIR = DATA_DIR / "unauthorized_logs"
SOUNDS_DIR = DATA_DIR / "sounds"
IMAGES_DIR = DATA_DIR / "Images"

ATTENDANCE_CSV = DATA_DIR / "attendance.csv"
ALERTS_CSV = DATA_DIR / "alerts.csv"
SETTINGS_JSON = DATA_DIR / "settings.json"

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

ATTENDANCE_COLUMNS = ["Timestamp", "Name", "Role", "Status", "Confidence"]
ALERT_COLUMNS = ["Timestamp", "AlertID", "PhotoPath", "Status", "ResolutionName"]

STATUS_AUTHORIZED = "Authorized Check-In"
STATUS_INTRUSION = "Intrusion Flagged"
ALERT_UNRESOLVED = "unresolved"
ALERT_RESOLVED = "resolved"

TS_FORMAT = "%Y-%m-%d %H:%M:%S"
_LOCK = threading.RLock()

# --------------------------------------------------------------------------
# SETTINGS (saved to data/settings.json so the Settings page really works)
# --------------------------------------------------------------------------
DEFAULT_SETTINGS = {
    "tolerance": 0.50,            # max face distance for a match (lower = stricter)
    "checkin_cooldown_min": 10,   # don't re-log the same person within N minutes
    "alert_cooldown_sec": 30,     # don't raise a new intruder alert within N seconds
    "siren_enabled": True,        # play siren when an unknown face is scanned
    "save_snapshots": True,       # keep a photo of every intruder
    "confirm_frames": 3,          # live mode: same answer needed N times in a row before acting
}


def load_settings() -> dict:
    settings = dict(DEFAULT_SETTINGS)
    try:
        if SETTINGS_JSON.exists():
            stored = json.loads(SETTINGS_JSON.read_text(encoding="utf-8"))
            for key in DEFAULT_SETTINGS:
                if key in stored:
                    settings[key] = stored[key]
    except (OSError, ValueError):
        pass  # corrupt file -> fall back to defaults
    return settings


def save_settings(settings: dict) -> None:
    clean = {k: settings.get(k, v) for k, v in DEFAULT_SETTINGS.items()}
    with _LOCK:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_JSON.write_text(json.dumps(clean, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------
# LOW-LEVEL CSV HELPERS
# --------------------------------------------------------------------------
def _write_csv(df: pd.DataFrame, path: Path) -> None:
    """Atomic write: a crash mid-write can never leave a half-written CSV."""
    tmp = path.with_suffix(".tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(path)


def _read_csv(path: Path, columns: list) -> pd.DataFrame:
    """Read a CSV, repairing missing / empty / corrupt files automatically."""
    if not path.exists():
        initialize_database()
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError):
        df = pd.DataFrame(columns=columns)
        _write_csv(df, path)
    for col in columns:               # tolerate files from older versions
        if col not in df.columns:
            df[col] = ""
    return df[columns]


def initialize_database() -> None:
    """Create folders and empty CSV files (headers only - no fake demo data)."""
    with _LOCK:
        for folder in (DATA_DIR, KNOWN_FACES_DIR, UNAUTHORIZED_DIR, SOUNDS_DIR):
            folder.mkdir(parents=True, exist_ok=True)
        if not ATTENDANCE_CSV.exists():
            _write_csv(pd.DataFrame(columns=ATTENDANCE_COLUMNS), ATTENDANCE_CSV)
        if not ALERTS_CSV.exists():
            _write_csv(pd.DataFrame(columns=ALERT_COLUMNS), ALERTS_CSV)


# --------------------------------------------------------------------------
# ATTENDANCE
# --------------------------------------------------------------------------
def get_attendance_logs() -> pd.DataFrame:
    return _read_csv(ATTENDANCE_CSV, ATTENDANCE_COLUMNS)


def add_attendance_log(name: str, role: str, status: str, confidence: float | None = None) -> None:
    with _LOCK:
        df = get_attendance_logs()
        row = {
            "Timestamp": datetime.datetime.now().strftime(TS_FORMAT),
            "Name": name,
            "Role": role,
            "Status": status,
            "Confidence": "" if confidence is None else f"{confidence:.0%}",
        }
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        _write_csv(df, ATTENDANCE_CSV)


def log_checkin_if_due(name: str, role: str, cooldown_min: float, confidence: float | None = None) -> bool:
    """Log an authorized check-in unless this person was logged within the cooldown.
    Returns True when a new row was written."""
    with _LOCK:
        df = get_attendance_logs()
        mine = df[(df["Name"] == name) & (df["Status"] == STATUS_AUTHORIZED)]
        if not mine.empty:
            last = pd.to_datetime(mine["Timestamp"], errors="coerce").max()
            if pd.notna(last):
                elapsed = (datetime.datetime.now() - last.to_pydatetime()).total_seconds()
                if elapsed < cooldown_min * 60:
                    return False
        add_attendance_log(name, role, STATUS_AUTHORIZED, confidence)
        return True


# --------------------------------------------------------------------------
# ALERTS (unknown / intruder faces)
# --------------------------------------------------------------------------
def get_alerts() -> pd.DataFrame:
    df = _read_csv(ALERTS_CSV, ALERT_COLUMNS)
    # Old versions wrote "unidentified" which no page understood - normalise it.
    df["Status"] = df["Status"].replace({"unidentified": ALERT_UNRESOLVED, "": ALERT_UNRESOLVED})
    return df


def resolve_photo_path(photo_path: str) -> Path | None:
    """Turn a stored photo path (new or legacy style) into a real file, or None."""
    if not photo_path:
        return None
    p = Path(photo_path)
    for candidate in (p, DATA_DIR / p, BASE_DIR / p, UNAUTHORIZED_DIR / p.name):
        if candidate.is_file():
            return candidate
    return None


def add_alert(photo_path: str | None) -> str:
    """Create a new unresolved alert and return its AlertID."""
    with _LOCK:
        df = get_alerts()
        alert_id = f"ALT_{uuid.uuid4().hex[:6].upper()}"
        row = {
            "Timestamp": datetime.datetime.now().strftime(TS_FORMAT),
            "AlertID": alert_id,
            "PhotoPath": photo_path or "",
            "Status": ALERT_UNRESOLVED,
            "ResolutionName": "",
        }
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        _write_csv(df, ALERTS_CSV)
        return alert_id


def recent_alert_exists(within_seconds: float) -> bool:
    """True if an alert was raised within the last N seconds (anti-flood guard)."""
    df = get_alerts()
    if df.empty:
        return False
    last = pd.to_datetime(df["Timestamp"], errors="coerce").max()
    if pd.isna(last):
        return False
    return (datetime.datetime.now() - last.to_pydatetime()).total_seconds() < within_seconds


def resolve_alert(alert_id: str, identity_name: str) -> bool:
    with _LOCK:
        df = get_alerts()
        mask = df["AlertID"] == alert_id
        if not mask.any():
            return False
        df.loc[mask, "Status"] = ALERT_RESOLVED
        df.loc[mask, "ResolutionName"] = identity_name
        _write_csv(df, ALERTS_CSV)
        return True


def dismiss_alert(alert_id: str) -> bool:
    """Close an alert without enrolling anyone (false alarm)."""
    return resolve_alert(alert_id, "(dismissed)")


# --------------------------------------------------------------------------
# ENROLLED PROFILES  (file name format: Name_Role_ID.jpg)
# --------------------------------------------------------------------------
def parse_profile_filename(path: Path) -> tuple[str, str]:
    parts = path.stem.split("_")
    name = parts[0].replace("-", " ") if parts and parts[0] else path.stem
    role = parts[1].replace("-", " ") if len(parts) >= 2 and parts[1] else "Authorized Staff"
    return name, role


def list_enrolled() -> list[dict]:
    """All reference photos as dicts: {path, name, role}, sorted by name."""
    KNOWN_FACES_DIR.mkdir(parents=True, exist_ok=True)
    people = []
    for p in sorted(KNOWN_FACES_DIR.iterdir()):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS:
            name, role = parse_profile_filename(p)
            people.append({"path": p, "name": name, "role": role})
    return sorted(people, key=lambda d: d["name"].lower())


def delete_profile_photo(path: Path) -> bool:
    try:
        Path(path).unlink()
        return True
    except OSError:
        return False


# --------------------------------------------------------------------------
# RESET
# --------------------------------------------------------------------------
def purge_all_data() -> None:
    """Delete every log, alert, snapshot and enrolled face. Settings are kept."""
    with _LOCK:
        for csv_file in (ATTENDANCE_CSV, ALERTS_CSV):
            if csv_file.exists():
                csv_file.unlink()
        for folder in (KNOWN_FACES_DIR, UNAUTHORIZED_DIR):
            if folder.exists():
                for item in folder.iterdir():
                    if item.is_file() and item.name != ".gitkeep":
                        item.unlink()
        initialize_database()
