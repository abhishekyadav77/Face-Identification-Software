# -*- coding: utf-8 -*-
"""
Live Scanner - three ways to scan a face:
  1. Browser camera snapshot  (works everywhere, incl. Docker / cloud)
  2. Upload a photo
  3. Live webcam stream        (OpenCV, only when the app runs on the machine that has the camera)
"""

import hashlib
import time
import uuid

import cv2
import streamlit as st

from utils.db_helper import (
    UNAUTHORIZED_DIR, add_alert, add_attendance_log, list_enrolled, load_settings,
    log_checkin_if_due, recent_alert_exists, STATUS_INTRUSION,
)
from utils.simple_facerec import get_engine, draw_results, crop_face
from utils.upload_face import decode_image
from utils.live_camera import LiveScanner
from utils.ui_helper import page_header, esc, bgr_to_rgb, play_siren

page_header("Biometric Scanner",
            "Scan a face against the enrolled database. Known staff are checked in, unknown faces raise an alert.", "📷")

settings = load_settings()
engine = get_engine(settings["tolerance"])

if not engine.available:
    st.error(f"Face engine is offline. {engine.error or ''}")
    st.code("pip install -r requirements.txt", language="bash")
    st.stop()

engine.refresh()
if not list_enrolled():
    st.warning("No faces are enrolled yet - every face will be treated as an intruder. "
               "Add people in **Enroll Person** first.")
bad = engine.unreadable_photos()
if bad:
    st.warning("No face could be found in these reference photos (re-upload them): " + ", ".join(bad))


# --------------------------------------------------------------------------
def save_intruder_snapshot(frame, box) -> str | None:
    """Store a cropped photo of the intruder; returns the path relative to /data."""
    if not settings["save_snapshots"]:
        return None
    UNAUTHORIZED_DIR.mkdir(parents=True, exist_ok=True)
    name = f"snap_{uuid.uuid4().hex[:10]}.jpg"
    cv2.imwrite(str(UNAUTHORIZED_DIR / name), crop_face(frame, box), [cv2.IMWRITE_JPEG_QUALITY, 90])
    return f"unauthorized_logs/{name}"


def process_still(frame):
    """Identify, log and describe every face in a still image. Returns (annotated_rgb, messages, has_unknown)."""
    results = engine.identify(frame, upsample=1)
    messages, has_unknown = [], False
    for r in results:
        if r.known:
            logged = log_checkin_if_due(r.name, r.role, settings["checkin_cooldown_min"], r.confidence)
            note = "check-in recorded" if logged else f"already checked in within {settings['checkin_cooldown_min']} min"
            messages.append(("ok", f"<b>{esc(r.name)}</b> &middot; {esc(r.role)} &mdash; access granted "
                                   f"(match {r.confidence:.0%}), {note}."))
        else:
            has_unknown = True
            photo = save_intruder_snapshot(frame, r.box)
            alert_id = add_alert(photo)
            add_attendance_log("Unknown Person", "Unauthorized", STATUS_INTRUSION)
            messages.append(("bad", f"<b>UNKNOWN FACE</b> &mdash; access denied. Alert <b>{alert_id}</b> raised "
                                    f"(see <i>Unknown Alerts</i>)."))
    return bgr_to_rgb(draw_results(frame, results)), messages, has_unknown


def render_still(frame, key: str):
    """Process each distinct image ONCE (Streamlit reruns the script on every click,
    which would otherwise log the same photo again and again)."""
    digest = hashlib.sha1(frame.tobytes()).hexdigest()
    cache = st.session_state.setdefault("scan_cache", {})
    fresh = cache.get(key, {}).get("digest") != digest
    if fresh:
        with st.spinner("Analysing face..."):
            image, messages, unknown = process_still(frame)
        cache[key] = {"digest": digest, "image": image, "messages": messages}
    else:
        image, messages, unknown = cache[key]["image"], cache[key]["messages"], False

    if not messages:
        st.info("No face detected. Move closer, face the camera and make sure the light is even.")
        return
    st.image(image, caption="Scan result", width="stretch")
    for kind, html in messages:
        st.markdown(f'<div class="scan-{kind}">{html}</div>', unsafe_allow_html=True)
    if fresh and unknown and settings["siren_enabled"]:
        play_siren()


# --------------------------------------------------------------------------
tab_cam, tab_up, tab_live = st.tabs(["📸 Camera snapshot", "🖼️ Upload photo", "🎥 Live webcam (local)"])

with tab_cam:
    st.caption("Uses your browser camera (allow camera access when asked). Works on localhost or HTTPS.")
    col_in, col_out = st.columns(2, gap="large")
    with col_in:
        shot = st.camera_input("Take a photo to scan", key="scan_camera")
    with col_out:
        if shot is not None:
            frame = decode_image(shot.getvalue())
            if frame is None:
                st.error("Could not read the camera image.")
            else:
                render_still(frame, "camera")
        else:
            st.info("The scan result appears here after you take a photo.")

with tab_up:
    col_in, col_out = st.columns(2, gap="large")
    with col_in:
        up = st.file_uploader("Upload a photo to scan", type=["png", "jpg", "jpeg", "webp"], key="scan_upload")
        if up is not None:
            st.image(up.getvalue(), caption="Uploaded photo", width="stretch")
    with col_out:
        if up is not None:
            frame = decode_image(up.getvalue())
            if frame is None:
                st.error("Could not read this image file.")
            else:
                render_still(frame, "upload")
        else:
            st.info("The scan result appears here after you upload a photo.")

with tab_live:
    st.caption("Smooth real-time scanning through OpenCV. Works when this app runs on the computer that has the "
               "camera (not in Docker / cloud - use the *Camera snapshot* tab there).")
    c1, c2 = st.columns([1, 3])
    cam_index = c1.number_input("Camera index", min_value=0, max_value=5, value=0, step=1)
    live = c2.toggle("Start live scanning", key="live_on")
    stage = st.empty()
    status_box = st.empty()
    feed_box = st.empty()
    siren_box = st.empty()

    if not live:
        stage.info("Switch **Start live scanning** on to begin. Faces are shown orange while being verified, "
                   "then green (known) or red (unknown).")
    else:
        scanner = LiveScanner(engine, settings, source=int(cam_index))
        if not scanner.start():
            st.error("Could not open the webcam. Close other apps using it (Zoom, Teams, Camera), "
                     "try another camera index, or use the *Camera snapshot* tab.")
        else:
            last_id, shown, t_fps, t_feed = -1, 0, time.time(), 0.0
            try:
                while True:             # Streamlit stops this loop (and runs `finally`) when the toggle is switched off
                    img, fid = scanner.snapshot()
                    if img is None or fid == last_id:
                        time.sleep(0.01)
                        continue
                    last_id = fid
                    stage.image(bgr_to_rgb(img), output_format="JPEG", width="stretch")
                    shown += 1
                    if scanner.siren_pending:
                        scanner.siren_pending = False
                        play_siren(siren_box)
                    now = time.time()
                    if now - t_fps >= 1.0:
                        status_box.caption(f"{shown / (now - t_fps):.0f} FPS display · recognition {scanner.proc_ms:.0f} ms/frame"
                                           + (f" · {scanner.error}" if scanner.error else ""))
                        shown, t_fps = 0, now
                    if now - t_feed >= 1.0 and scanner.events:
                        t_feed = now
                        rows = "".join(f'<div class="scan-{k}">{esc(t_)} &mdash; {time.strftime("%H:%M:%S", time.localtime(ts))}</div>'
                                       for ts, k, t_ in list(scanner.events)[-4:][::-1])
                        feed_box.markdown(rows, unsafe_allow_html=True)
                    time.sleep(0.02)    # cap display ~30 FPS; keeps the browser responsive
            finally:
                scanner.stop()          # always release the camera
