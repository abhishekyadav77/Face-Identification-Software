# -*- coding: utf-8 -*-
"""Unknown Alerts - review unrecognised faces: enroll them or dismiss as false alarm."""

import streamlit as st

from utils.db_helper import (
    get_alerts, resolve_alert, dismiss_alert, resolve_photo_path, ALERT_UNRESOLVED,
)
from utils.upload_face import save_uploaded_face
from utils.ui_helper import page_header, flash, show_flash, esc

ROLES = ["Staff", "Developer", "Manager", "Security Guard", "Contractor", "Executive", "Admin", "Visitor"]

page_header("Unknown Alerts",
            "Unrecognised faces caught by the scanner. Authorise a real person or dismiss a false alarm.", "🚨")
show_flash()

alerts = get_alerts()
if alerts.empty:
    st.info("No alerts have been raised.")
    st.stop()

pending = alerts[alerts["Status"] == ALERT_UNRESOLVED].sort_values("Timestamp", ascending=False)
history = alerts[alerts["Status"] != ALERT_UNRESOLVED].sort_values("Timestamp", ascending=False)

st.subheader(f"Pending ({len(pending)})")
if pending.empty:
    st.success("Nothing to review - all alerts are resolved.")

for _, alert in pending.iterrows():
    aid = alert["AlertID"]
    photo = resolve_photo_path(alert["PhotoPath"])
    with st.container(border=True):
        col_img, col_form = st.columns([1, 2], gap="large")
        with col_img:
            if photo:
                st.image(str(photo), caption=aid, width="stretch")
            else:
                st.markdown('<div class="terminal-card"><p>No snapshot saved for this alert.</p></div>',
                            unsafe_allow_html=True)
        with col_form:
            st.markdown(f"#### {esc(aid)}  <span class='status-badge-alert'>UNRESOLVED</span>", unsafe_allow_html=True)
            st.caption(f"Logged at {alert['Timestamp']}")
            name = st.text_input("Person's name", key=f"name_{aid}", placeholder="Enter a name to authorise")
            role = st.selectbox("Role", ROLES, key=f"role_{aid}")
            b1, b2 = st.columns(2)
            if b1.button("Authorise & enroll", key=f"ok_{aid}", type="primary", width="stretch", disabled=photo is None):
                if not name.strip():
                    st.error("Enter the person's name first.")
                else:
                    ok, msg = save_uploaded_face(photo.read_bytes(), name, role)
                    if ok:
                        resolve_alert(aid, name.strip())
                        flash(f"{msg} Alert {aid} resolved.")
                        st.rerun()
                    else:
                        st.error(msg)       # alert stays open - nothing is lost
            if b2.button("Dismiss (false alarm)", key=f"no_{aid}", width="stretch"):
                dismiss_alert(aid)
                flash(f"Alert {aid} dismissed.", "info")
                st.rerun()

st.subheader("History")
if history.empty:
    st.caption("No resolved alerts yet.")
else:
    st.dataframe(history, width="stretch", hide_index=True)
