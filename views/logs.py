# -*- coding: utf-8 -*-
"""Detection Logs - search, filter and export every scan event."""

import datetime

import pandas as pd
import streamlit as st

from utils.db_helper import get_attendance_logs
from utils.ui_helper import page_header

page_header("Detection Logs", "Search, filter and export every recorded biometric event.", "📋")

df = get_attendance_logs()
if df.empty:
    st.info("No scans recorded yet.")
    st.stop()

df["_ts"] = pd.to_datetime(df["Timestamp"], errors="coerce")

c1, c2, c3 = st.columns([2, 2, 2])
query = c1.text_input("Search by name", placeholder="type part of a name")
status = c2.selectbox("Status", ["All"] + sorted(df["Status"].unique().tolist()))
min_d, max_d = df["_ts"].min().date(), df["_ts"].max().date()
span = c3.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max(max_d, datetime.date.today()))

view = df
if query:
    view = view[view["Name"].str.contains(query, case=False, na=False, regex=False)]
if status != "All":
    view = view[view["Status"] == status]
if isinstance(span, (tuple, list)) and len(span) == 2:
    view = view[(view["_ts"].dt.date >= span[0]) & (view["_ts"].dt.date <= span[1])]

view = view.sort_values("_ts", ascending=False).drop(columns="_ts")
st.caption(f"{len(view)} of {len(df)} record(s)")
st.dataframe(view, width="stretch", hide_index=True)

st.download_button(
    "Download filtered logs (CSV)",
    data=view.to_csv(index=False).encode("utf-8-sig"),     # utf-8-sig opens cleanly in Excel
    file_name=f"face_logs_{datetime.datetime.now():%Y%m%d_%H%M%S}.csv",
    mime="text/csv",
    type="primary",
)
