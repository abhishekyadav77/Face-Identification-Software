# -*- coding: utf-8 -*-
"""Settings - these values are saved to data/settings.json and used by the scanner."""

import streamlit as st

from utils.db_helper import load_settings, save_settings, purge_all_data, DEFAULT_SETTINGS
from utils.simple_facerec import get_engine
from utils.ui_helper import page_header, show_flash, flash

page_header("System Settings", "Tune recognition strictness, cooldowns, alarm behaviour and manage data.", "⚙️")
show_flash()

current = load_settings()

with st.form("settings_form"):
    st.subheader("Recognition")
    tolerance = st.slider(
        "Match tolerance (face distance)", 0.30, 0.70, float(current["tolerance"]), 0.01,
        help="Lower = stricter: fewer wrong people accepted, but you may be rejected in poor light. "
             "0.45-0.55 is a good range, 0.60 is the library default.")
    cooldown = st.number_input("Check-in cooldown (minutes)", 0, 240, int(current["checkin_cooldown_min"]),
                               help="The same person is not logged again within this time.")

    confirm = st.slider("Live confirmation (frames)", 1, 6, int(current["confirm_frames"]),
                        help="Live webcam only: the same result must be seen this many times in a row before a check-in "
                             "or alarm. Higher = fewer false alarms, slightly slower reaction.")

    st.subheader("Intruder alarm")
    siren = st.checkbox("Play siren when an unknown face is scanned", value=bool(current["siren_enabled"]))
    snaps = st.checkbox("Save a snapshot of every intruder", value=bool(current["save_snapshots"]),
                        help="Needed if you want to enroll the person later from the Unknown Alerts page.")
    alert_cd = st.number_input("Alert cooldown for live webcam (seconds)", 0, 600, int(current["alert_cooldown_sec"]),
                               help="Stops one intruder standing in front of the camera from creating hundreds of alerts.")

    c1, c2 = st.columns(2)
    saved = c1.form_submit_button("Save settings", type="primary", width="stretch")
    reset = c2.form_submit_button("Restore defaults", width="stretch")

if saved:
    save_settings({"tolerance": tolerance, "checkin_cooldown_min": int(cooldown), "alert_cooldown_sec": int(alert_cd),
                   "siren_enabled": siren, "save_snapshots": snaps, "confirm_frames": int(confirm)})
    flash("Settings saved.")
    st.rerun()
if reset:
    save_settings(DEFAULT_SETTINGS)
    flash("Defaults restored.")
    st.rerun()

st.divider()
st.subheader("Engine")
engine = get_engine()
if engine.available:
    st.success(f"Face engine ready - {engine.people_count} person(s), {engine.photo_count} reference photo(s) loaded.")
else:
    st.error(engine.error or "Face engine unavailable.")

st.divider()
st.subheader("Danger zone")
st.warning("This permanently deletes all enrolled faces, attendance logs, alerts and intruder snapshots.")
confirm = st.text_input("Type DELETE to confirm", key="purge_confirm")
if st.button("Purge all biometric data", disabled=confirm.strip() != "DELETE"):
    purge_all_data()
    get_engine().refresh()
    st.session_state.pop("purge_confirm", None)
    flash("All data was deleted.")
    st.rerun()
