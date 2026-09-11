# -*- coding: utf-8 -*-
"""
Database Helper Module
Handles reading and writing of CSV data logs, setting up folders, and initializing tables securely.
"""

import os
import datetime
import pandas as pd
from pathlib import Path

# --- DIRECTORY CONFIGURATION ---
DATA_DIR = Path("data")
KNOWN_FACES_DIR = DATA_DIR / "known_faces"
UNAUTHORIZED_DIR = DATA_DIR / "unauthorized_logs"

# --- FILE PATHS ---
ATTENDANCE_CSV = DATA_DIR / "attendance.csv"
ALERTS_CSV = DATA_DIR / "alerts.csv"

def initialize_database():
    """
    Initializes the local database directories and CSV files with standard schemas
    if they do not already exist on the workstation.
    """
    # Create directory tree
    KNOWN_FACES_DIR.mkdir(parents=True, exist_ok=True)
    UNAUTHORIZED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize attendance register spreadsheet
    if not ATTENDANCE_CSV.exists():
        df = pd.DataFrame(columns=["Timestamp", "Name", "Role", "Status"])
        # Seed with initial default logs for premium look
        now = datetime.datetime.now()
        seed_data = [
            {"Timestamp": (now - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "Name": "Demo-Rahul Sharma", "Role": "Admin", "Status": "Authorized Check-In"},
            {"Timestamp": (now - datetime.timedelta(hours=1.5)).strftime("%Y-%m-%d %H:%M:%S"), "Name": "Demo-Priya Patel", "Role": "Staff", "Status": "Authorized Check-In"},
            {"Timestamp": (now - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), "Name": "Demo-Amit Kumar", "Role": "Staff", "Status": "Authorized Check-In"},
            {"Timestamp": (now - datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"), "Name": "Demo-Sonia Verma", "Role": "Security", "Status": "Authorized Check-In"}
        ]
        df = pd.concat([df, pd.DataFrame(seed_data)], ignore_index=True)
        df.to_csv(ATTENDANCE_CSV, index=False)
        print("Attendance CSV initialized with seed logs.")

    # Initialize intrusion alert spreadsheet
    if not ALERTS_CSV.exists():
        df = pd.DataFrame(columns=["Timestamp", "AlertID", "PhotoPath", "Status", "ResolutionName"])
        now = datetime.datetime.now()
        seed_alerts = [
            {"Timestamp": (now - datetime.timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"), "AlertID": "ALT_3921", "PhotoPath": "Demo-simulated_intruder_1.jpg", "Status": "unresolved", "ResolutionName": ""},
            {"Timestamp": (now - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"), "AlertID": "ALT_7482", "PhotoPath": "Demo-simulated_intruder_2.jpg", "Status": "unresolved", "ResolutionName": ""}
        ]
        df = pd.concat([df, pd.DataFrame(seed_alerts)], ignore_index=True)
        df.to_csv(ALERTS_CSV, index=False)
        print("Alerts CSV initialized with unresolved items.")

def get_attendance_logs():
    """Reads and returns the attendance CSV as a DataFrame."""
    if not ATTENDANCE_CSV.exists():
        initialize_database()
    return pd.read_csv(ATTENDANCE_CSV)

def add_attendance_log(name, role, status):
    """Appends an authorized check-in or threat breach to the attendance log."""
    df = get_attendance_logs()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = {"Timestamp": now_str, "Name": name, "Role": role, "Status": status}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(ATTENDANCE_CSV, index=False)
    return df

def get_alerts():
    """Reads and returns the active threat alerts list."""
    if not ALERTS_CSV.exists():
        initialize_database()
    return pd.read_csv(ALERTS_CSV)

def add_alert(alert_id, photo_path):
    """Adds a new unauthorized threat flag log."""
    df = get_alerts()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = {
        "Timestamp": now_str, 
        "AlertID": alert_id, 
        "PhotoPath": str(photo_path), 
        # "Status": "unresolved", 
        "Status": "unidentified", 
        "ResolutionName": ""
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(ALERTS_CSV, index=False)
    return df

def resolve_alert(alert_id, identity_name):
    """Resolves an alert by naming the intruder and assigning permission."""
    df = get_alerts()
    if not df.empty and alert_id in df["AlertID"].values:
        df.loc[df["AlertID"] == alert_id, "Status"] = "resolved"
        df.loc[df["AlertID"] == alert_id, "ResolutionName"] = identity_name
        df.to_csv(ALERTS_CSV, index=False)
        return True
    return False

def purge_all_data():
    """Formats and fully resets the database folders to pristine defaults."""
    # Delete CSVs
    if ATTENDANCE_CSV.exists():
        ATTENDANCE_CSV.unlink()
    if ALERTS_CSV.exists():
        ALERTS_CSV.unlink()
        
    # Delete all known faces
    for item in KNOWN_FACES_DIR.glob("*"):
        if item.is_file():
            item.unlink()
            
    # Delete all threat alert photos
    for item in UNAUTHORIZED_DIR.glob("*"):
        if item.is_file():
            item.unlink()
            
    # Recreate structure
    initialize_database()
