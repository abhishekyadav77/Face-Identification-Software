# -*- coding: utf-8 -*-
"""
Railway Face Rec Pro - Profile Enrollment Page
Allows system operators to register a new user in the facial recognition database.
"""

import streamlit as st
from pathlib import Path

# --- LOCAL UTILITY IMPORTS ---
from utils.ui_helper import apply_custom_theme, render_sidebar_header
from utils.upload_face import save_uploaded_face

# Page config setup
st.set_page_config(page_title="Railway Face Rec Pro - Register ID", page_icon="➕", layout="wide")
apply_custom_theme()
render_sidebar_header()

st.title("➕ Register New Biometric ID")
st.write("Securely register a name, role, and face image to grant authorization to facility areas.")
st.markdown("---")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📋 Enrollment Registration Card")
    
    # Simple form container for profile entries
    with st.form("enrollment_form", clear_on_submit=True):
        full_name = st.text_input("Full Name *", placeholder="E.g., John Miller")
        role = st.selectbox(
            "Organizational Clearance Designation *", 
            ["Developer", "Manager", "Security Guard", "Contractor", "Executive", "Visitor"]
        )
        uploaded_file = st.file_uploader(
            "Upload Frontal Reference Portrait * (PNG/JPG)", 
            type=["png", "jpg", "jpeg", "webp"]
        )
        
        submit_btn = st.form_submit_button("Grant Access & Encode Reference")
        
        if submit_btn:
            if not full_name.strip() or uploaded_file is None:
                st.error("Submission Error: All fields marked with * are strictly required.")
            else:
                success, msg = save_uploaded_face(uploaded_file, full_name, role)
                if success:
                    st.success(f"Success: {msg}")
                    st.balloons()
                else:
                    st.error(f"Encoding Error: {msg}")

with col_right:
    st.subheader("⚙️ Verification Guidelines")
    st.markdown("""
    <div class="terminal-card">
        <h4 style="color: #f8fafc; margin-top: 0px; margin-bottom: 12px;">Reference Standard Criteria:</h4>
        <ul style="margin-bottom: 0px; padding-left: 1.2rem;">
            <li style="margin-bottom: 10px;">Subject's face must occupy at least 30% of overall frame dimensions.</li>
            <li style="margin-bottom: 10px;">Ensure high brightness with even lighting vectors across the forehead and cheekbones.</li>
            <li style="margin-bottom: 10px;">Subject must look straight toward the scanner camera during capture.</li>
            <li style="margin-bottom: 0px;">Avoid sunglasses, hats, or extreme face coverings during enrollment.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📁 Currently Registered Reference Profiles")
    known_faces_dir = Path("data/known_faces")
    if known_faces_dir.exists():
        files = list(known_faces_dir.glob("*"))
        if files:
            for f in files[:5]:
                st.markdown(f"**👤 Encoded Profile:** `{f.name}`")
            if len(files) > 5:
                st.markdown(f"*And {len(files)-5} more profile(s) encoded in data directory...*")
        else:
            st.info("No employee profiles registered yet in the local database storage.")
    else:
        st.info("No profiles registered.")
