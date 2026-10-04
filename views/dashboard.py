# -*- coding: utf-8 -*-
"""Dashboard - live numbers from the CSV logs and the face engine."""

import datetime

import altair as alt
import pandas as pd
import streamlit as st

from utils.db_helper import (
    get_attendance_logs, get_alerts, list_enrolled, load_settings,
    STATUS_AUTHORIZED, ALERT_UNRESOLVED,
)
from utils.simple_facerec import get_engine
from utils.ui_helper import page_header, kv_card, stat_card, esc, show_flash

page_header("Security Control Panel",
            "Live overview of enrolled staff, today's check-ins and open intruder alerts.", "📊")
show_flash()

attendance = get_attendance_logs()
alerts = get_alerts()
enrolled = list_enrolled()
settings = load_settings()
engine = get_engine(settings["tolerance"])

attendance["_ts"] = pd.to_datetime(attendance["Timestamp"], errors="coerce")
today = datetime.date.today()
today_rows = attendance[(attendance["_ts"].dt.date == today) & (attendance["Status"] == STATUS_AUTHORIZED)]
open_alerts = alerts[alerts["Status"] == ALERT_UNRESOLVED]
people = len({p["name"] for p in enrolled})

m1, m2, m3, m4 = st.columns(4)
with m1:
    stat_card("Enrolled people", people, f"{len(enrolled)} reference photo(s)")
with m2:
    stat_card("Check-ins today", len(today_rows), f"{today_rows['Name'].nunique()} unique person(s)")
with m3:
    stat_card("Open intruder alerts", len(open_alerts),
              "Needs review" if len(open_alerts) else "All clear", "bad" if len(open_alerts) else "ok")
with m4:
    stat_card("Face engine", "Ready" if engine.available else "Offline",
              "dlib ResNet" if engine.available else "see Settings", "ok" if engine.available else "bad")

st.write("")
left, right = st.columns([2, 1], gap="large")

with left:
    st.subheader("Recent activity")
    recent = attendance.sort_values("_ts", ascending=False).head(8)
    if recent.empty:
        st.info("No scans yet. Enroll a person, then open **Live Scanner** to start.")
    for _, row in recent.iterrows():
        is_ok = row["Status"] == STATUS_AUTHORIZED
        conf = f" &middot; match {esc(row['Confidence'])}" if row["Confidence"] else ""
        st.markdown(
            f"""
            <div class="log-row {'' if is_ok else 'alert'}">
              <div>
                <div class="who">{esc(row['Name'])}</div>
                <div class="meta">{esc(row['Role'])} &middot; {esc(row['Timestamp'])}{conf}</div>
              </div>
              <span class="{'status-badge-active' if is_ok else 'status-badge-alert'}">{esc(row['Status'])}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Check-ins, last 7 days")
    days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    ok_rows = attendance[attendance["Status"] == STATUS_AUTHORIZED]
    counts = [int((ok_rows["_ts"].dt.date == d).sum()) for d in days]
    chart_df = pd.DataFrame({"Day": [d.strftime("%a %d") for d in days], "Check-ins": counts})
    chart = (alt.Chart(chart_df)
             .mark_bar(color="#16a34a", cornerRadiusTopLeft=5, cornerRadiusTopRight=5, size=34)
             .encode(x=alt.X("Day:N", sort=None, title=None, axis=alt.Axis(labelAngle=0)),
                     y=alt.Y("Check-ins:Q", title=None, axis=alt.Axis(tickMinStep=1, format="d")),
                     tooltip=["Day", "Check-ins"])
             .properties(height=220))
    st.altair_chart(chart, width="stretch")

with right:
    st.subheader("Security flags")
    if len(open_alerts):
        st.markdown(
            f"""
            <div class="alert-banner">
              <h4>&#9888;&#65039; {len(open_alerts)} unrecognised face(s)</h4>
              <p>Open <b>Unknown Alerts</b> in the menu to enroll or dismiss them.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success("No open security alerts.")

    st.subheader("System status")
    kv_card("Node diagnostics", [
        ("Recognition engine", '<span class="status-badge-active">dlib ready</span>' if engine.available
         else '<span class="status-badge-alert">offline</span>'),
        ("Match tolerance", f"{settings['tolerance']:.2f}"),
        ("Check-in cooldown", f"{settings['checkin_cooldown_min']} min"),
        ("Alert cooldown (live)", f"{settings['alert_cooldown_sec']} sec"),
        ("Siren on intruder", "On" if settings["siren_enabled"] else "Off"),
    ])
    if not engine.available:
        st.error(engine.error or "Face engine unavailable.")
