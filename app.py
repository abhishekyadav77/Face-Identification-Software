# -*- coding: utf-8 -*-
"""
Railway Face Rec Pro - entry point.
Run with:   streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Railway Face Rec Pro",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.db_helper import initialize_database
from utils.ui_helper import inject_css, render_sidebar

initialize_database()
inject_css()

pages = [
    st.Page("views/dashboard.py",  title="Dashboard",       icon=":material/dashboard:",       default=True),
    st.Page("views/scanner.py",    title="Live Scanner",    icon=":material/photo_camera:"),
    st.Page("views/enroll.py",     title="Enroll Person",   icon=":material/person_add:"),
    st.Page("views/logs.py",       title="Detection Logs",  icon=":material/receipt_long:"),
    st.Page("views/alerts.py",     title="Unknown Alerts",  icon=":material/notifications_active:"),
    st.Page("views/attendance.py", title="Attendance",      icon=":material/schedule:"),
    st.Page("views/settings.py",   title="Settings",        icon=":material/settings:"),
]
navigation = st.navigation(pages)
render_sidebar()
navigation.run()
