# -*- coding: utf-8 -*-
"""
Railway Face Rec Pro - Attendance Page
Organizes checked-in staff members currently authorized inside facilities.
"""

import streamlit as st
import pandas as pd

# --- LOCAL UTILITY IMPORTS ---
from utils.ui_helper import apply_custom_theme, render_sidebar_header
from utils.db_helper import get_attendance_logs

# Page configurations
st.set_page_config(page_title="Railway Face Rec Pro - Daily Attendance", page_icon="🕐", layout="wide")
apply_custom_theme()
render_sidebar_header()

st.title("🕐 Attendance Check-In Dashboard")
st.write("Track active logins, timestamps, and authorized staff profiles currently inside the building.")
st.markdown("---")

try:
    df = get_attendance_logs()
except Exception as e:
    st.error(f"Error reading logs: {e}")
    df = pd.DataFrame()

if not df.empty:
    # Filter out entries that represent actual authorized check-ins
    authorized_staff = df[df["Status"].str.contains("Authorized", na=False)]
    
    st.subheader("👥 Active On-Site Staff Profiles")
    if not authorized_staff.empty:
        st.dataframe(authorized_staff.sort_values(by="Timestamp", ascending=False), use_container_width=True)
    else:
        st.info("No authorized check-ins captured today yet. Access 'Live Scanner' to register log lines.")
else:
    st.info("Terminal records empty: No check-in events recorded.")
