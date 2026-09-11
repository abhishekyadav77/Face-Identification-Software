# -*- coding: utf-8 -*-
"""
Railway Face REC Pro - Live Camera Scanner Page
Provides both a browser simulated environment scanning demo and a local OpenCV webcam integration.
"""

import os
import datetime
import time
import pandas as pd
import numpy as np
import cv2
import streamlit as st
from pathlib import Path

# --- LOCAL UTILITY IMPORTS ---
from utils.ui_helper import apply_custom_theme, render_sidebar_header
from utils.db_helper import get_attendance_logs, add_attendance_log, add_alert, get_alerts
from utils.simple_facerec import SimpleFacerec

# Page Config
st.set_page_config(page_title="Railway Face REC Pro - Live Biometric Scanner", page_icon="📷", layout="wide")
apply_custom_theme()
render_sidebar_header()

st.title("📷 Biometric Scanner Terminal")
st.write("Scan human faces against references to track attendance and automatically trigger alarms for intruders.")
st.markdown("---")

col_left, col_right = st.columns([3, 1])

with col_left:
    st.markdown("### 🔴 Live video")
    
    # Input options
    video_source = st.radio(
        "Select Active Video Input Source:", 
        ["Simulated Scanning Demo (Standard Browser Support)", "Physical Video0 Hardware Webcam (Runs on local laptop/workstation only)"], 
        horizontal=True
    )
    
    # CASE A: SIMULATED SCANNING DEMO (For AI Studio Preview / Streamlit Cloud)
    if video_source == "Simulated Scanning Demo (Standard Browser Support)":
        st.info("Browser Demo Mode: Press any button below to trigger simulated face-scans in the system database.")
        
        c_btn1, c_btn2, c_btn3 = st.columns(3)
        with c_btn1:
            if st.button("👥 Scan Alice Vance (Developer)", use_container_width=True):
                add_attendance_log("Alice Vance", "Developer", "Authorized Check-In")
                st.success("Alice Vance scanned successfully! Access Granted.")
                st.balloons()
                
        with c_btn2:
            if st.button("👥 Scan Bob Miller (Manager)", use_container_width=True):
                add_attendance_log("Bob Miller", "Manager", "Authorized Check-In")
                st.success("Bob Miller scanned successfully! Access Granted.")
                st.balloons()
                
        with c_btn3:
            if st.button("🚨 Scan Unknown Profile (Intruder Alert)", use_container_width=True):
                alert_id = f"ALT_{int(os.urandom(2).hex(), 16)}"
                # Register intrusion alert
                add_alert(alert_id, "simulated_intruder.jpg")
                # Add to attendance
                add_attendance_log("Unknown Profile", "Unauthorized", "⚠️ Intrusion Flagged")
                
                st.error("⚠️ CRITICAL BREACH: Unknown individual detected at STC Admin Room - Charbagh. Logged immediately.")
                # Trigger an elegant web-audio alert
                # st.audio("./sounds/sirensound.mp3", format="audio/mpeg")
                if st.button("Start Siren"):
                     # 2. Use native st.audio with autoplay
                    st.audio("data/sounds/sirensound.mp3", format="audio/mp3", autoplay=True ,key=f"siren_{time.time()}" )
                st.markdown("""
                    <audio autoplay>
                        <source src="./sounds/sirensound.mp3" type="audio/wav">
                    </audio>
                           
                """, unsafe_allow_html=True)
                
        # Interactive scanning screen card
        st.image("data/Images/image.png", caption="Active Scanning Overlay Map Grid", use_container_width=True)
        
    # CASE B: LOCAL OpenCV WEBCAM INPUT
    else:
        st.warning("⚠️ Accessing physical webcams requires the Streamlit server to be running on your local machine.")
        run_camera = st.checkbox("Toggle Physical Webcam Feed Stream")
        
        if run_camera:
            # Initialize our modular face rec system
            sfr = SimpleFacerec()
            sfr.load_encoding_images()
            
            # Start camera capture from hardware index 0
            cap = cv2.VideoCapture(0)
            frame_placeholder = st.empty()
            
            # Streaming loop
            while run_camera:
                ret, frame = cap.read()
                if not ret:
                    st.error("Could not capture video from local physical device /dev/video0.")
                    break
                    
                # Execute face search
                locations, names, roles = sfr.detect_known_faces(frame)
                
                for face_loc, name, role in zip(locations, names, roles):
                    y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
                    
                    # Blue/Green boundary box for staff, red for unrecognized intrusion
                    box_color = (46, 204, 113) if role != "Unauthorized" else (52, 152, 219)
                    if name == "Unknown":
                        box_color = (0, 0, 255) # Warning Red
                        
                    # Draw visual boxes directly onto OpenCV frames
                    cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
                    cv2.putText(frame, f"{name} ({role})", (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 0.8, box_color, 2)
                    
                    # Logging verification mechanisms
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if name == "Unknown":
                        # Generate alert code
                        alert_id = f"ALT_{int(os.urandom(2).hex(), 16)}"
                        photo_filename = f"data/unauthorized_logs/{alert_id}.jpg"
                        cv2.imwrite(photo_filename, frame[y1:y2, x1:x2])
                        
                        # Guard duplicate logging triggers
                        alerts_df = get_alerts()
                        if alerts_df.empty or not (alerts_df["Status"] == "unresolved").any():
                            add_alert(alert_id, photo_filename)
                    else:
                        # Log success checkout checkin logs
                        att_df = get_attendance_logs()
                        last_scans = att_df[att_df["Name"] == name]
                        should_write = True
                        if not last_scans.empty:
                            last_time = datetime.datetime.strptime(last_scans.iloc[-1]["Timestamp"], "%Y-%m-%d %H:%M:%S")
                            # 10 minute cooldown logic to prevent double check-ins
                            if (datetime.datetime.now() - last_time).seconds < 600:
                                should_write = False
                        
                        if should_write:
                            add_attendance_log(name, role, "Authorized Check-In")
                
                # Convert OpenCV BGR to Streamlit standard RGB color matrix
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                
            cap.release()

with col_right:
    st.markdown("### 🎚️ Feed Status")
    
    st.markdown("""
    <div class="terminal-card">
        <h4 style="margin-top: 0px;">Frame Output</h4>
        <h2 style="color: #34d399; margin-bottom: 0px;">30 FPS</h2>
        <p style="color: #94a3b8; font-size: 0.8rem; margin-top: 4px;">Hardware optimized sync speed</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="terminal-card">
        <h4 style="margin-top: 0px;">Biometric Status</h4>
        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 12px;">Reference matching engine active</p>
        <span class="status-badge-active">ACTIVE SCANNER</span>
    </div>
    """, unsafe_allow_html=True)
