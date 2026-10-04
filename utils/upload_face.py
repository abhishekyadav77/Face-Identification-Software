# -*- coding: utf-8 -*-
"""
Enrollment helper - validates a reference photo and saves it as
data/known_faces/<Name>_<Role>_<ID>.jpg
"""

import uuid

import cv2
import numpy as np

from utils.db_helper import KNOWN_FACES_DIR, parse_profile_filename
from utils.simple_facerec import get_engine, draw_results, FaceResult

MAX_SAVE_SIDE = 900   # keep stored photos small


def clean_text(value: str, max_len: int = 40) -> str:
    """Keep letters, digits, space and hyphen. '_' is removed because it is the
    separator inside file names. Spaces become '-' (turned back into spaces on load)."""
    kept = "".join(c for c in str(value) if c.isalnum() or c in (" ", "-")).strip()
    return "-".join(kept.split())[:max_len]


def decode_image(source) -> np.ndarray | None:
    """Bytes / Streamlit UploadedFile / open file  ->  BGR image (or None)."""
    try:
        raw = source if isinstance(source, (bytes, bytearray)) else source.read()
        arr = np.frombuffer(raw, np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)   # also applies phone EXIF rotation
    except Exception:
        return None


def save_uploaded_face(uploaded_file, full_name: str, role: str):
    """Validate + store a reference photo.  Returns (success: bool, message: str)."""
    name = clean_text(full_name)
    role_clean = clean_text(role) or "Staff"
    if not name:
        return False, "Please enter a valid name (letters and numbers)."

    image = decode_image(uploaded_file)
    if image is None:
        return False, "File format not supported. Upload a normal PNG / JPG image."

    engine = get_engine()
    ok, msg, encoding, box = engine.encode_for_enrollment(image)
    if not ok:
        return False, msg

    # Refuse to register the same face under a second, different name.
    engine.refresh()
    if engine.known_face_encodings:
        dists = np.linalg.norm(np.array(engine.known_face_encodings) - encoding, axis=1)
        best = int(np.argmin(dists))
        existing = engine.known_face_names[best]
        if dists[best] <= engine.tolerance and existing.lower() != name.replace("-", " ").lower():
            return False, f"This face is already enrolled as '{existing}'. Use that name to add another photo."

    h, w = image.shape[:2]
    if max(h, w) > MAX_SAVE_SIDE:
        s = MAX_SAVE_SIDE / max(h, w)
        image = cv2.resize(image, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)

    KNOWN_FACES_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{name}_{role_clean}_{uuid.uuid4().hex[:8]}.jpg"
    if not cv2.imwrite(str(KNOWN_FACES_DIR / filename), image, [cv2.IMWRITE_JPEG_QUALITY, 92]):
        return False, "Could not write the image to disk (check folder permissions)."
    engine.refresh()
    return True, f"{name.replace('-', ' ')} ({role_clean.replace('-', ' ')}) enrolled successfully."


def preview_with_box(image_bgr: np.ndarray) -> np.ndarray:
    """RGB preview of the detected face - shown after a successful enrollment."""
    engine = get_engine()
    ok, _, _, box = engine.encode_for_enrollment(image_bgr)
    shown = draw_results(image_bgr, [FaceResult(box=box, known=True, name="Detected", confidence=1.0)]) if ok else image_bgr
    return cv2.cvtColor(shown, cv2.COLOR_BGR2RGB)
