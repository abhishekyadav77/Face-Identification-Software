# -*- coding: utf-8 -*-
"""
Real-time scanner that does NOT lag.

Why the old loop lagged: it read a frame, ran the (slow) recognition on it, and only
then drew it - so the video could never be faster than the recognition, and OpenCV's
internal buffer made the picture seconds old.

How this works:
  Thread 1  READER   - reads the camera as fast as it can, always keeping only the NEWEST frame.
  Thread 2  WORKER   - fast face *detection* on every new frame (~25 ms), but the slow face
                       *encoding* (~140 ms) only for NEW faces / once every few seconds.
                       Faces are followed between frames (IoU tracking).
  Main loop (Streamlit) - shows the newest frame with the latest boxes: smooth video,
                       independent of how long recognition takes.
  A person is only logged / an alert raised after the SAME answer was seen on several frames
  (vote), so one bad frame can't cause a false intruder alarm.
"""

from __future__ import annotations

import collections
import platform
import threading
import time
from dataclasses import dataclass, field

import cv2
import numpy as np

from utils import db_helper as db
from utils.simple_facerec import SimpleFacerec, crop_face

REID_SECONDS = 2.5       # re-check a followed face's identity this often
LOST_SECONDS = 1.0       # forget a face that has been gone this long
IOU_MATCH = 0.25


def _iou(a, b) -> float:
    at, ar, ab, al = a
    bt, br, bb, bl = b
    iw, ih = min(ar, br) - max(al, bl), min(ab, bb) - max(at, bt)
    if iw <= 0 or ih <= 0:
        return 0.0
    inter = iw * ih
    return inter / float((ar - al) * (ab - at) + (br - bl) * (bb - bt) - inter)


@dataclass
class Track:
    box: tuple
    last_seen: float
    votes: collections.deque = field(default_factory=lambda: collections.deque(maxlen=6))
    name: str = "Unknown"
    role: str = "Unauthorized"
    known: bool = False
    confidence: float = 0.0
    last_encoded: float = 0.0
    fired: bool = False          # event (check-in / alert) already raised for this track

    def verdict(self, need: int):
        """(state, name) once `need` identical answers were seen, else ('verifying', '')."""
        if len(self.votes) < need:
            return "verifying", ""
        recent = list(self.votes)[-need:]
        if all(v == recent[0] for v in recent):
            return ("unknown", "") if recent[0] is None else ("known", recent[0])
        return "verifying", ""


class LiveScanner:
    def __init__(self, engine: SimpleFacerec, settings: dict, source=0):
        self.engine, self.settings, self.source = engine, settings, source
        self.cap = None
        self._frame = None
        self._frame_id = 0
        self._lock = threading.Lock()
        self._tracks: list[Track] = []
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []
        self.error: str | None = None
        self.events = collections.deque(maxlen=30)     # (time, kind, text)
        self.siren_pending = False
        self.proc_ms = 0.0

    # ------------------------------------------------------------ lifecycle
    def start(self) -> bool:
        backend = cv2.CAP_DSHOW if (platform.system() == "Windows" and isinstance(self.source, int)) else cv2.CAP_ANY
        self.cap = cv2.VideoCapture(self.source, backend)
        if not self.cap.isOpened():
            self.cap.release()
            self.error = "Could not open the camera."
            return False
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)       # small frames = fast pipeline
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)          # don't queue old frames
        try:
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))   # much faster than raw YUY2 on USB cams
        except Exception:
            pass
        self._stop.clear()
        for fn in (self._read_loop, self._work_loop):
            t = threading.Thread(target=fn, daemon=True)
            t.start()
            self._threads.append(t)
        return True

    def stop(self) -> None:
        self._stop.set()
        for t in self._threads:
            t.join(timeout=2)
        if self.cap is not None:
            self.cap.release()
        self._threads = []

    # -------------------------------------------------------------- threads
    def _read_loop(self) -> None:
        is_file = isinstance(self.source, str)
        while not self._stop.is_set():
            ok, frame = self.cap.read()
            if not ok:
                if is_file:                                   # loop test videos
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    time.sleep(0.01)
                    continue
                self.error = "Lost the camera signal."
                time.sleep(0.2)
                continue
            with self._lock:
                self._frame, self._frame_id = frame, self._frame_id + 1
            if is_file:
                time.sleep(1 / 30)

    def _work_loop(self) -> None:
        last_id = -1
        while not self._stop.is_set():
            with self._lock:
                frame, fid = self._frame, self._frame_id
            if frame is None or fid == last_id:
                time.sleep(0.005)
                continue
            last_id = fid
            t0 = time.time()
            try:
                self._process(frame)
            except Exception as exc:                          # never let the worker die silently
                self.error = f"Recognition error: {exc}"
            self.proc_ms = 0.8 * self.proc_ms + 0.2 * (time.time() - t0) * 1000

    # ---------------------------------------------------------- recognition
    def _process(self, frame: np.ndarray) -> None:
        now = time.time()
        boxes = self.engine.detect(frame)
        need = int(self.settings.get("confirm_frames", 3))
        unmatched = list(self._tracks)
        updated: list[Track] = []

        for box in boxes:
            best, best_iou = None, IOU_MATCH
            for tr in unmatched:
                v = _iou(box, tr.box)
                if v > best_iou:
                    best, best_iou = tr, v
            if best is None:
                best = Track(box=box, last_seen=now)
            else:
                unmatched.remove(best)
            best.box, best.last_seen = box, now

            if now - best.last_encoded >= (0.0 if not best.votes else REID_SECONDS) or len(best.votes) < need:
                enc = self.engine.encode_box(frame, box)
                if enc is not None:
                    res = self.engine.identify_encoding(enc, box)
                    best.votes.append(res.name if res.known else None)
                    best.name, best.role, best.known, best.confidence = res.name, res.role, res.known, res.confidence
                    best.last_encoded = now
            self._decide(best, frame, need)
            updated.append(best)

        # keep tracks that were only briefly missed (face turned / blink of the detector)
        updated += [t for t in unmatched if now - t.last_seen < LOST_SECONDS]
        self._tracks = updated

    def _decide(self, tr: Track, frame: np.ndarray, need: int) -> None:
        state, name = tr.verdict(need)
        if state == "verifying":
            return
        if state == "known":
            tr.known, tr.name = True, name
            if not tr.fired:
                tr.fired = True
                if db.log_checkin_if_due(name, tr.role, self.settings["checkin_cooldown_min"], tr.confidence):
                    self.events.append((time.time(), "ok", f"{name} ({tr.role}) checked in"))
        else:
            tr.known, tr.name = False, "Unknown"
            if not tr.fired:
                tr.fired = True
                if not db.recent_alert_exists(self.settings["alert_cooldown_sec"]):
                    photo = None
                    if self.settings["save_snapshots"]:
                        import uuid
                        fname = f"snap_{uuid.uuid4().hex[:10]}.jpg"
                        db.UNAUTHORIZED_DIR.mkdir(parents=True, exist_ok=True)
                        cv2.imwrite(str(db.UNAUTHORIZED_DIR / fname), crop_face(frame, tr.box),
                                    [cv2.IMWRITE_JPEG_QUALITY, 90])
                        photo = f"unauthorized_logs/{fname}"
                    aid = db.add_alert(photo)
                    db.add_attendance_log("Unknown Person", "Unauthorized", db.STATUS_INTRUSION)
                    self.events.append((time.time(), "bad", f"UNKNOWN person - alert {aid} raised"))
                    if self.settings["siren_enabled"]:
                        self.siren_pending = True

    # -------------------------------------------------------------- display
    def snapshot(self):
        """(annotated BGR frame, frame_id) - cheap, called from the Streamlit loop."""
        with self._lock:
            frame, fid = self._frame, self._frame_id
        if frame is None:
            return None, fid
        img = frame.copy()
        need = int(self.settings.get("confirm_frames", 3))
        for tr in list(self._tracks):
            top, right, bottom, left = tr.box
            state, _ = tr.verdict(need)
            if state == "verifying":
                color, label = (0, 165, 255), "Verifying..."
            elif tr.known:
                color, label = (74, 163, 22), f"{tr.name} {tr.confidence:.0%}"
            else:
                color, label = (38, 38, 220), "UNKNOWN"
            cv2.rectangle(img, (left, top), (right, bottom), color, 2)
            (tw, th), base = cv2.getTextSize(label.encode("ascii", "replace").decode(), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            y0 = max(0, top - th - base - 8)
            cv2.rectangle(img, (left, y0), (left + tw + 10, y0 + th + base + 6), color, cv2.FILLED)
            cv2.putText(img, label.encode("ascii", "replace").decode(), (left + 5, y0 + th + 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        return img, fid
