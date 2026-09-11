# -*- coding: utf-8 -*-
"""
Railway Face Rec Pro - Detection Logs Page
Exposes historical facial scanning events in a searchable data frame.
"""

import datetime
import pandas as pd
import streamlit as st

# --- LOCAL UTILITY IMPORTS ---
from utils.ui_helper import apply_custom_theme, render_sidebar_header
from utils.db_helper import get_attendance_logs

# Page settings
st.set_page_config(page_title="Railway Face Rec Pro - System Logs", page_icon="📋", layout="wide")
apply_custom_theme()
render_sidebar_header()

st.title("📋 Facial Detection & Access Logs")
st.write("Browse, search, and verify past biometric events recorded on terminal nodes.")
st.markdown("---")

# Load real database csv logs
try:
    df = get_attendance_logs()
except Exception as e:
    st.error(f"Error loading logs: {e}")
    df = pd.DataFrame(columns=["Timestamp", "Name", "Role", "Status"])

st.markdown("### 🔍 Filter and Query Records")
search_filter = st.text_input("Filter records by Name query:", "")


if not df.empty:
    # Filter by user query
    if search_filter:
        df = df[df["Name"].str.contains(search_filter, case=False, na=False)]
        
    # Render dataframe with full width
    st.dataframe(df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
    
    st.markdown("---")
    
    # Export function
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download All Spreadsheet (CSV Format)",
        data=csv_bytes,
        file_name=f"Railway_Face_rec_pro_historical_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.info("No biometric scans recorded on this server node yet.")
