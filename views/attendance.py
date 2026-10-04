# -*- coding: utf-8 -*-
"""Attendance - who is present on a given day, and who has not turned up."""

import datetime

import pandas as pd
import streamlit as st

from utils.db_helper import get_attendance_logs, list_enrolled, STATUS_AUTHORIZED
from utils.ui_helper import page_header, stat_card

page_header("Attendance", "Daily presence report built from authorised check-ins.", "🕐")

day = st.columns([1, 3])[0].date_input("Date", value=datetime.date.today(), max_value=datetime.date.today())

df = get_attendance_logs()
df["_ts"] = pd.to_datetime(df["Timestamp"], errors="coerce")
rows = df[(df["Status"] == STATUS_AUTHORIZED) & (df["_ts"].dt.date == day)]

present = (rows.groupby(["Name", "Role"])
           .agg(First_check_in=("_ts", "min"), Last_seen=("_ts", "max"), Scans=("_ts", "count"))
           .reset_index())
for col in ("First_check_in", "Last_seen"):
    present[col] = present[col].dt.strftime("%H:%M:%S")
present = present.rename(columns={"First_check_in": "First check-in", "Last_seen": "Last seen"})

enrolled_names = sorted({p["name"] for p in list_enrolled()})
absent = [n for n in enrolled_names if n not in set(present["Name"])]

m1, m2, m3 = st.columns(3)
with m1:
    stat_card("Present", len(present), f"on {day:%d %b}", "ok")
with m2:
    stat_card("Not yet seen", len(absent), "enrolled, no check-in", "bad" if absent else "ok")
with m3:
    stat_card("Total scans", int(present["Scans"].sum()) if not present.empty else 0, "authorised check-ins")

st.write("")
left, right = st.columns([3, 2], gap="large")
with left:
    st.subheader(f"Present on {day:%d %b %Y}")
    if present.empty:
        st.info("No authorised check-ins on this date.")
    else:
        st.dataframe(present.sort_values("First check-in"), width="stretch", hide_index=True)
        st.download_button("Download this day (CSV)", present.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"attendance_{day:%Y%m%d}.csv", mime="text/csv")
with right:
    st.subheader("Not yet seen")
    if not enrolled_names:
        st.caption("Nobody is enrolled yet.")
    elif not absent:
        st.success("Everyone enrolled has checked in.")
    else:
        st.dataframe(pd.DataFrame({"Name": absent}), width="stretch", hide_index=True)
