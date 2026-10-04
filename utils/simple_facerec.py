# -*- coding: utf-8 -*-
"""
Face recognition engine.

Uses dlib directly (HOG face detector + 5-point landmarks + ResNet that turns
a face into a 128-number "fingerprint"). It is the same technology the old
`face_recognition` package wrapped, but it installs from a pre-built wheel
(`dlib-bin`) so no C++ compiler or CMake is required, and it works on
current Python versions.

Public API (used by the Streamlit pages):
    engine = get_engine()            # shared instance, models loaded once
    engine.refresh()                 # (re)load enrolled faces - only changed files are re-encoded
    engine.identify(bgr_image)       # -> list[FaceResult]
    engine.encode_for_enrollment(..) # validate a reference photo
    draw_results(bgr_image, results) # draw boxes / names
"""

from __future__ import annotations

import importlib.util
import math
import threading
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from utils.db_helper import KNOWN_FACES_DIR, IMAGE_EXTENSIONS, parse_profile_filename

try:
    import dlib  # provided by the `dlib-bin` (or `dlib`) package
    _DLIB_ERROR = None
except Exception as exc:  # pragma: no cover - depends on the user's machine
    dlib = None
    _DLIB_ERROR = f"dlib could not be imported: {exc}"


MIN_DETECTION_SCORE = 0.5   # reject weak (usually false) face detections
MIN_ENROLL_FACE_PX = 64     # reference faces smaller than this match poorly
MIN_ENROLL_SHARPNESS = 15.0 # Laplacian variance of the 128px face crop


def _find_model_dir() -> Path | None:
    """Locate the pre-trained model files shipped by `face_recognition_models`
    WITHOUT importing that package (its __init__ needs the deprecated pkg_resources)."""
    spec = importlib.util.find_spec("face_recognition_models")
    if spec and spec.submodule_search_locations:
        model_dir = Path(list(spec.submodule_search_locations)[0]) / "models"
        if model_dir.is_dir():
            return model_dir
    return None


@dataclass
class FaceResult:
    box: tuple              # (top, right, bottom, left) in ORIGINAL image pixels
    known: bool = False
    name: str = "Unknown"
    role: str = "Unauthorized"
    distance: float | None = None      # 0 = identical, bigger = more different
    confidence: float = 0.0            # 0..1 for display
    encoding: np.ndarray | None = field(default=None, repr=False)


def distance_to_confidence(distance: float, threshold: float = 0.6) -> float:
    """Convert a dlib face distance into an easy-to-read 0..1 score."""
    if distance > threshold:
        value = (1.0 - distance) / ((1.0 - threshold) * 2.0)
        return float(max(0.0, min(1.0, value)))
    value = 1.0 - distance / (threshold * 2.0)
    return float(min(1.0, value + (1.0 - value) * math.pow((value - 0.5) * 2, 0.2)))


class SimpleFacerec:
    def __init__(self, tolerance: float = 0.5):
        self.tolerance = tolerance
        self.error: str | None = _DLIB_ERROR
        self._lock = threading.RLock()
        self._detector = None
        self._shaper = None
        self._encoder = None

        # enrolled faces (one entry per reference photo)
        self.known_face_encodings: list[np.ndarray] = []
        self.known_face_names: list[str] = []
        self.known_face_roles: list[str] = []
        self._cache: dict[str, tuple] = {}     # path -> (mtime_ns, size, encoding|None)
        self._signature: tuple | None = None

        if dlib is not None:
            self._load_models()

    # ------------------------------------------------------------------ setup
    def _load_models(self) -> None:
        model_dir = _find_model_dir()
        if model_dir is None:
            self.error = ("Model files not found. Run:  pip install face_recognition_models")
            return
        try:
            self._detector = dlib.get_frontal_face_detector()
            self._shaper = dlib.shape_predictor(str(model_dir / "shape_predictor_5_face_landmarks.dat"))
            self._encoder = dlib.face_recognition_model_v1(str(model_dir / "dlib_face_recognition_resnet_model_v1.dat"))
            self.error = None
        except Exception as exc:  # pragma: no cover
            self.error = f"Could not load face models: {exc}"

    @property
    def available(self) -> bool:
        return self._encoder is not None and self.error is None

    @property
    def people_count(self) -> int:
        return len(set(self.known_face_names))

    @property
    def photo_count(self) -> int:
        return len(self.known_face_encodings)

    # --------------------------------------------------------- low level
    @staticmethod
    def _to_rgb_scaled(bgr: np.ndarray, max_side: int):
        h, w = bgr.shape[:2]
        scale = 1.0
        if max(h, w) > max_side:
            scale = max_side / float(max(h, w))
            bgr = cv2.resize(bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        rgb = np.ascontiguousarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        return rgb, scale

    @staticmethod
    def _non_max_suppression(dets, iou_limit: float = 0.3):
        """Keep the best-scoring box among overlapping detections of the same face."""
        keep = []
        for rect, score in sorted(dets, key=lambda d: d[1], reverse=True):
            clash = False
            for k, _ in keep:
                iw = min(rect.right(), k.right()) - max(rect.left(), k.left())
                ih = min(rect.bottom(), k.bottom()) - max(rect.top(), k.top())
                if iw > 0 and ih > 0:
                    inter = iw * ih
                    union = rect.area() + k.area() - inter
                    if inter / union > iou_limit:
                        clash = True
                        break
            if not clash:
                keep.append((rect, score))
        return keep

    def _detect_rects(self, rgb: np.ndarray, upsample: int, merge_levels: bool):
        """HOG detection with a confidence filter.  Real faces score ~0.8+, background
        false-positives < 0.3, so MIN_DETECTION_SCORE stops fake intruder alerts.
        Fast path (merge_levels=False): try zoom level 0 first and only zoom in
        further if nothing was found.  Enrollment (merge_levels=True) merges all levels."""
        found = []
        for level in range(upsample + 1):
            rects, scores, _ = self._detector.run(rgb, level, 0.0)
            found += [(r, float(sc)) for r, sc in zip(rects, scores) if sc >= MIN_DETECTION_SCORE]
            if found and not merge_levels:
                break
        return self._non_max_suppression(found)

    def _encode_faces(self, bgr: np.ndarray, upsample: int = 1, max_side: int = 640,
                      jitters: int = 1, merge_levels: bool = False):
        """Detect every face and return [(box_in_original_pixels, encoding), ...]."""
        if not self.available or bgr is None or bgr.size == 0:
            return []
        rgb, scale = self._to_rgb_scaled(bgr, max_side)
        out = []
        with self._lock:
            for rect, _score in self._detect_rects(rgb, upsample, merge_levels):
                shape = self._shaper(rgb, rect)
                enc = np.array(self._encoder.compute_face_descriptor(rgb, shape, jitters))
                box = tuple(int(round(v / scale)) for v in (rect.top(), rect.right(), rect.bottom(), rect.left()))
                out.append((box, enc))
        return out

    # ---- split API used by the live scanner (detect often, encode rarely) ----
    def detect(self, bgr: np.ndarray, max_side: int = 480) -> list[tuple]:
        """Fast detection only (no encoding). Boxes are (top, right, bottom, left) in the
        original image's pixels."""
        if not self.available or bgr is None or bgr.size == 0:
            return []
        rgb, scale = self._to_rgb_scaled(bgr, max_side)
        with self._lock:
            rects = self._detect_rects(rgb, 0, False)
        return [tuple(int(round(v / scale)) for v in (r.top(), r.right(), r.bottom(), r.left())) for r, _ in rects]

    def encode_box(self, bgr: np.ndarray, box: tuple) -> np.ndarray | None:
        """128-D encoding of the face inside `box` (original pixels)."""
        top, right, bottom, left = box
        h, w = bgr.shape[:2]
        left, top, right, bottom = max(0, left), max(0, top), min(w - 1, right), min(h - 1, bottom)
        if right - left < 20 or bottom - top < 20:
            return None
        rgb = np.ascontiguousarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        with self._lock:
            shape = self._shaper(rgb, dlib.rectangle(left, top, right, bottom))
            return np.array(self._encoder.compute_face_descriptor(rgb, shape, 1))

    def identify_encoding(self, enc: np.ndarray, box: tuple) -> "FaceResult":
        idx, dist = self._best_match(enc)
        if idx is not None and dist <= self.tolerance:
            return FaceResult(box=box, known=True, name=self.known_face_names[idx],
                              role=self.known_face_roles[idx], distance=dist,
                              confidence=distance_to_confidence(dist), encoding=enc)
        return FaceResult(box=box, known=False, distance=dist, encoding=enc)

    # --------------------------------------------------- enrolled faces
    def refresh(self, images_path: str | Path = KNOWN_FACES_DIR) -> int:
        """(Re)load enrolled faces. Only new/changed photos are re-encoded, so
        calling this on every Streamlit rerun is cheap. Returns number of photos loaded."""
        path = Path(images_path)
        path.mkdir(parents=True, exist_ok=True)
        files = sorted(p for p in path.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)
        sig = tuple((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in files)
        if sig == self._signature:
            return self.photo_count
        if not self.available:
            self._signature = sig
            return 0

        with self._lock:
            fresh_cache = {}
            for p in files:
                st = p.stat()
                key = str(p)
                cached = self._cache.get(key)
                if cached and cached[0] == st.st_mtime_ns and cached[1] == st.st_size:
                    fresh_cache[key] = cached
                    continue
                enc = None
                try:
                    img = cv2.imread(str(p))
                    faces = self._encode_faces(img, upsample=2, jitters=2, max_side=900, merge_levels=True) if img is not None else []
                    if faces:
                        # a reference photo should show one person: use the biggest face
                        faces.sort(key=lambda f: (f[0][2] - f[0][0]) * (f[0][1] - f[0][3]), reverse=True)
                        enc = faces[0][1]
                except Exception as exc:  # corrupt image etc. - skip, never crash the app
                    print(f"[Facerec] Could not encode {p.name}: {exc}")
                fresh_cache[key] = (st.st_mtime_ns, st.st_size, enc)
            self._cache = fresh_cache

            self.known_face_encodings, self.known_face_names, self.known_face_roles = [], [], []
            for p in files:
                enc = self._cache[str(p)][2]
                if enc is not None:
                    name, role = parse_profile_filename(p)
                    self.known_face_encodings.append(enc)
                    self.known_face_names.append(name)
                    self.known_face_roles.append(role)
            self._signature = sig
        return self.photo_count

    load_encoding_images = refresh  # backwards-compatible name

    def unreadable_photos(self) -> list[str]:
        """Reference photos in which no face could be found (need re-uploading)."""
        return [Path(k).name for k, v in self._cache.items() if v[2] is None]

    # ------------------------------------------------------- recognition
    def _best_match(self, enc: np.ndarray):
        if not self.known_face_encodings:
            return None, None
        dists = np.linalg.norm(np.array(self.known_face_encodings) - enc, axis=1)
        idx = int(np.argmin(dists))
        return idx, float(dists[idx])

    def identify(self, bgr: np.ndarray, upsample: int = 1, max_side: int = 640) -> list[FaceResult]:
        """Find all faces in an image and say who each one is."""
        return [self.identify_encoding(enc, box)
                for box, enc in self._encode_faces(bgr, upsample=upsample, max_side=max_side)]

    def encode_for_enrollment(self, bgr: np.ndarray):
        """Check that a photo is usable as a reference.
        Returns (ok, message, encoding, box)."""
        if not self.available:
            return False, self.error or "Face engine is not available.", None, None
        faces = self._encode_faces(bgr, upsample=2, jitters=1, max_side=900, merge_levels=True)
        if not faces:
            return False, "No face found in this photo. Use a clear, front-facing, well-lit portrait.", None, None
        if len(faces) > 1:
            return False, f"{len(faces)} faces found. Please use a photo that contains only one person.", None, None
        box, enc = faces[0]
        top, right, bottom, left = box
        if (right - left) < MIN_ENROLL_FACE_PX:
            return False, (f"Face is too small ({right - left}px). Move closer or use a higher-resolution photo "
                           f"(at least {MIN_ENROLL_FACE_PX}px wide face)."), None, None
        crop = bgr[max(0, top):bottom, max(0, left):right]
        if crop.size:
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (128, 128))                       # compare sharpness at equal scale
            if cv2.Laplacian(gray, cv2.CV_64F).var() < MIN_ENROLL_SHARPNESS:
                return False, "Photo is too blurry. Hold the camera steady and retake it.", None, None
            if gray.mean() < 45:
                return False, "Photo is too dark. Use more even lighting.", None, None
            if gray.mean() > 225:
                return False, "Photo is overexposed. Reduce glare / backlight.", None, None
        return True, "ok", enc, box


# ------------------------------------------------------------------ helpers
_ENGINE: SimpleFacerec | None = None
_ENGINE_LOCK = threading.Lock()


def get_engine(tolerance: float | None = None) -> SimpleFacerec:
    """Shared engine (models are loaded only once per server process)."""
    global _ENGINE
    with _ENGINE_LOCK:
        if _ENGINE is None:
            _ENGINE = SimpleFacerec()
        if tolerance is not None:
            _ENGINE.tolerance = float(tolerance)
        return _ENGINE


def crop_face(bgr: np.ndarray, box: tuple, margin: float = 0.45) -> np.ndarray:
    """Crop a face with some surrounding context (the detector needs it later)."""
    top, right, bottom, left = box
    h, w = bgr.shape[:2]
    mh, mw = int((bottom - top) * margin), int((right - left) * margin)
    return bgr[max(0, top - mh):min(h, bottom + mh), max(0, left - mw):min(w, right + mw)].copy()


def _ascii(text: str) -> str:
    return text.encode("ascii", "replace").decode("ascii")


def draw_results(bgr: np.ndarray, results: list[FaceResult]) -> np.ndarray:
    """Return a copy of the image with a box + label around every face."""
    img = bgr.copy()
    h, w = img.shape[:2]
    thick = max(2, int(round(min(h, w) / 220)))
    font_scale = max(0.5, min(h, w) / 900)
    for r in results:
        top, right, bottom, left = r.box
        color = (74, 163, 22) if r.known else (38, 38, 220)          # BGR green / red
        cv2.rectangle(img, (left, top), (right, bottom), color, thick)
        label = _ascii(f"{r.name} ({r.confidence:.0%})" if r.known else "UNKNOWN")
        (tw, th), base = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, font_scale, 1)
        y0 = bottom if bottom + th + base + 8 < h else max(0, top - th - base - 8)
        cv2.rectangle(img, (left, y0), (left + tw + 12, y0 + th + base + 8), color, cv2.FILLED)
        cv2.putText(img, label, (left + 6, y0 + th + 3), cv2.FONT_HERSHEY_DUPLEX, font_scale, (255, 255, 255), 1, cv2.LINE_AA)
    return img
