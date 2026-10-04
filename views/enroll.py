# -*- coding: utf-8 -*-
"""Enroll Person - register reference photos and manage who is authorised."""

import cv2
import streamlit as st

from utils.db_helper import list_enrolled, delete_profile_photo
from utils.simple_facerec import get_engine
from utils.upload_face import save_uploaded_face, decode_image, preview_with_box
from utils.ui_helper import page_header, esc, show_flash, flash, bgr_to_rgb

ROLES = ["Staff", "Developer", "Manager", "Security Guard", "Contractor", "Executive", "Admin", "Visitor"]

page_header("Enroll Person",
            "Register a name, role and a clear face photo to grant access.", "🪪")
show_flash()

engine = get_engine()
if not engine.available:
    st.error(f"Face engine is offline. {engine.error or ''}")
    st.stop()

left, right = st.columns([3, 2], gap="large")

with left:
    st.subheader("Registration card")
    with st.form("enrollment_form", clear_on_submit=True):
        full_name = st.text_input("Full name *", placeholder="e.g. Rahul Sharma", max_chars=40)
        role = st.selectbox("Role / clearance *", ROLES)
        t_up, t_cam = st.tabs(["Upload photo", "Take photo"])
        with t_up:
            uploaded = st.file_uploader("Front-facing portrait (PNG / JPG)", type=["png", "jpg", "jpeg", "webp"])
        with t_cam:
            camera = st.camera_input("Capture with camera")
        submitted = st.form_submit_button("Enroll person", type="primary", width="stretch")

    if submitted:
        source = uploaded or camera
        if not full_name.strip() or source is None:
            st.error("Please enter a name and provide a photo (upload or camera).")
        else:
            raw = source.getvalue()
            ok, msg = save_uploaded_face(raw, full_name, role)
            if ok:
                st.success(msg)
                img = decode_image(raw)
                if img is not None:
                    st.image(preview_with_box(img), caption="Face detected and stored", width=280)
            else:
                st.error(msg)

with right:
    st.subheader("Photo guidelines")
    st.markdown(
        """
        <div class="terminal-card">
          <ul>
            <li>Exactly <b>one</b> person in the photo.</li>
            <li>Face the camera straight on; the face should fill a good part of the frame.</li>
            <li>Even lighting, no strong shadows or backlight.</li>
            <li>No sunglasses, mask or hat covering the face.</li>
            <li>Add 2-3 photos of the same person (different light) for better accuracy - use the same name.</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
st.subheader("Registered profiles")
profiles = list_enrolled()
if not profiles:
    st.info("Nobody is enrolled yet.")
else:
    n_people = len({p["name"] for p in profiles})
    st.caption(f"{n_people} {'person' if n_people == 1 else 'people'} · {len(profiles)} photo(s)")
    cols = st.columns(4)
    for i, p in enumerate(profiles):
        with cols[i % 4]:
            with st.container(border=True):
                img = cv2.imread(str(p["path"]))
                if img is not None:
                    h, w = img.shape[:2]
                    side = min(h, w)
                    y0, x0 = (h - side) // 2, (w - side) // 2
                    st.image(bgr_to_rgb(img[y0:y0 + side, x0:x0 + side]), width="stretch")
                st.markdown(f"**{esc(p['name'])}**  \n<span class='status-badge-active'>{esc(p['role'])}</span>",
                            unsafe_allow_html=True)
                if st.button("Remove", key=f"rm_{p['path'].name}", width="stretch"):
                    if delete_profile_photo(p["path"]):
                        engine.refresh()
                        flash(f"Removed a photo of {p['name']}.")
                        st.rerun()

engine.refresh()
bad = engine.unreadable_photos()
if bad:
    st.warning("No face could be detected in: " + ", ".join(bad) + " - remove and re-upload a clearer photo.")
