# -*- coding: utf-8 -*-
"""
Railway Face Rec Pro - Unknown Security Alerts Page
Allows administrators to audit, identify, and resolve unrecognized faces logged by scanners.
"""

import os
import streamlit as st
import pandas as pd
from pathlib import Path
from utils.upload_face import save_uploaded_face

# --- LOCAL UTILITY IMPORTS ---
from utils.ui_helper import apply_custom_theme, render_sidebar_header
from utils.db_helper import get_alerts, resolve_alert

# Config
st.set_page_config(page_title="Railway Face Rec Pro - Intruder Alerts", page_icon="🚨", layout="wide")
apply_custom_theme()
render_sidebar_header()

st.title("🚨 Security Threat Management")
st.write("Audit and identify unrecognized face scanner snaps to grant permission or secure zones.")
st.markdown("---")

try:
    alerts_df = get_alerts()
except Exception as e:
    st.error(f"Error accessing alerts data: {e}")
    alerts_df = pd.DataFrame()

if not alerts_df.empty:
    unresolved_alerts = alerts_df[alerts_df["Status"] == "unresolved"]
    resolved_alerts = alerts_df[alerts_df["Status"] != "unresolved"]
    
    st.subheader("⚠️ Pending Active Breaches")
    
    if not unresolved_alerts.empty:
        # Loop through active unrecognized alert items
        for idx, alert in unresolved_alerts.iterrows():
            col_img, col_form = st.columns([1, 2])
            
            with col_img:
                # Beautiful illustration of unrecognized subject matching
                st.image(
                    f"{alert['PhotoPath']}", 
                    caption=f"Intruder Profile ID: {alert['AlertID']}", 
                    use_container_width=True
                )
                
            with col_form:
                st.markdown(f"### Alert Tag: **{alert['AlertID']}**")
                st.markdown(f"**⏰ Timestamp logged:** `{alert['Timestamp']}`")
                st.markdown(f"**🛡️ Security Level:** Unrecognized Threat Signature")
                
                # Input identification parameters
                assigned_name = st.text_input("Enroll Subject Name:", key=f"name_{alert['AlertID']}")
                assigned_role = st.selectbox(
                    "Assign Designation:", 
                    ["Developer", "Manager", "Security Guard", "Contractor", "Executive", "Visitor"], 
                    key=f"role_{alert['AlertID']}"
                )
                
                if st.button("✅ Authorize Profile ID", key=f"resolve_{alert['AlertID']}", use_container_width=True):
                    if not assigned_name.strip():
                        st.error("Submission Error: You must enter an identification Name.")
                    else:
                        success = resolve_alert(alert['AlertID'], assigned_name)
                        if success:
                            st.success(f"Profile: '{assigned_name}' authorized successfully in biometric records.")
                            # now save the new person in the database
                            assigned_image=alert["PhotoPath"]
                            if Path(assigned_image).exists():
                                with open(assigned_image, "rb") as f:
                                    success2, msg2 = save_uploaded_face(f, assigned_name, assigned_role)
                            else:
                              st.error("The alert image file was not found.")

                            
                           

                            st.balloons()
                            st.rerun()
            st.markdown("<hr style='border-top: 1px solid #1e293b;'/>", unsafe_allow_html=True)
    else:
        st.success("Perfect status: No unresolved security threats logged on server.")
        
    st.subheader("✅ Historically Resolved Profiles")
    if not resolved_alerts.empty:
        st.dataframe(resolved_alerts, use_container_width=True)
else:
    st.info("System Record Empty: No security intrusion alarms logged.")
