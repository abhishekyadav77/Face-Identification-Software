# -*- coding: utf-8 -*-
"""
Railway Face Rec Pro - System Settings Page
Handles tuning matching metrics, setting alarm modes, and database diagnostics/reset.
"""

import streamlit as st

# --- LOCAL UTILITY IMPORTS ---
from utils.ui_helper import apply_custom_theme, render_sidebar_header
from utils.db_helper import purge_all_data

# Page configurations
st.set_page_config(page_title="Railway Face Rec Pro - System Settings", page_icon="⚙️", layout="wide")
apply_custom_theme()
render_sidebar_header()

st.title("⚙️ System Control & Settings")
st.write("Configure spatial recognition models, security thresholds, audio triggers, and database utilities.")
st.markdown("---")

st.subheader("🧠 Threshold Configurations")
matching_tolerance = st.slider(
    "Facial Recognition Vector Distance Tolerance (Lesser is stricter):", 
    min_value=0.1, 
    max_value=0.8, 
    value=0.45, 
    step=0.05
)
st.info(f"💡 Active Tolerance: {matching_tolerance}. Lower limits increase confidence, while larger limits decrease false rejects.")

st.subheader("🚨 Intruder Alarm Settings")
trigger_siren = st.checkbox("Play browser audio siren warning immediately on unknown scans", value=True)
backup_alerts = st.checkbox("Write snapshots to local disk for forensics analysis", value=True)

st.markdown("---")

st.subheader("🧹 System Database Purging")
st.warning("⚠️ Warning: Resetting databases deletes all enrolled reference faces, logs, and unresolved alerts completely.")

if st.button("🗑️ Reset and Purge All Biometric Databases", use_container_width=True):
    try:
        purge_all_data()
        st.success("System Reset Completed successfully. All reference photos and event records cleared.")
        # st.balloons()
        st.snow()
    except Exception as e:
        st.error(f"Error resetting systems: {e}")
