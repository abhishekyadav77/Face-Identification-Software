# Railway Face Rec Pro

Face-recognition access control and attendance system built with Streamlit, OpenCV and dlib.
Known staff are checked in automatically; unknown faces raise an alert with a snapshot you can review, enroll or dismiss.

## Quick start

**Requirements:** Python **3.10 - 3.13** (3.12 recommended) and an internet connection for the first install.

| System | Command |
|---|---|
| Windows | double-click **`run.bat`** |
| Linux / macOS | `chmod +x run.sh && ./run.sh` |

Then open **http://localhost:8501**.

Manual install (any system):
```bash
python -m venv venv
venv\Scripts\activate          # Windows      |   source venv/bin/activate   (Linux/macOS)
pip install -r requirements.txt
streamlit run app.py
```
No C++ compiler or CMake is needed - `dlib-bin` is a pre-built wheel.

## How to use
1. **Enroll Person** - enter a name + role and upload / capture ONE clear front-facing photo. Add 2-3 photos (different light) under the same name for better accuracy.
2. **Live Scanner**
   - *Camera snapshot*: take a photo with the browser camera (works anywhere, also Docker/cloud).
   - *Upload photo*: scan an existing image.
   - *Live webcam (local)*: smooth real-time video with face tracking. Orange = verifying, green = known, red = unknown.
3. **Unknown Alerts** - authorise & enroll the person from the snapshot, or dismiss a false alarm.
4. **Detection Logs / Attendance** - filter, search and export CSV; see who is present / not yet seen.
5. **Settings** - match tolerance, cooldowns, live confirmation frames, siren, snapshots, data purge.

## Why it is fast now
- Camera reading, face detection and the display run in separate threads - the video never waits for recognition.
- Cheap detection on every frame; the expensive face encoding only for new faces / every few seconds (faces are tracked between frames).
- Always shows the newest frame (buffer size 1, MJPG, 640x480).
- A check-in or alarm needs the *same* answer on several consecutive frames (Settings -> Live confirmation) - no false alarms from one bad frame.
- Enrolled faces are cached; only new/changed photos are re-encoded.

## Project layout
```
app.py                  entry point + navigation
views/                  dashboard, scanner, enroll, logs, alerts, attendance, settings
utils/simple_facerec.py face engine (dlib)
utils/live_camera.py    threaded real-time scanner + tracker
utils/db_helper.py      CSV logs, settings, profile helpers
utils/upload_face.py    enrollment + photo quality checks
assets/style.css        UI theme
data/                   known_faces/, unauthorized_logs/, attendance.csv, alerts.csv, settings.json
```

## Troubleshooting
| Problem | Fix |
|---|---|
| "Face engine: OFFLINE" | `pip install -r requirements.txt` inside the activated venv; use Python 3.10-3.13. |
| Browser camera shows nothing | Allow camera permission; use `localhost` or HTTPS. |
| Live webcam won't open | Close Zoom/Teams/Camera app, try camera index 1, or use the snapshot tab. |
| A known person is rejected | Add more photos of them; raise tolerance slightly (0.55) in Settings. |
| A stranger is accepted | Lower tolerance (0.45) in Settings. |
| `pip` fails on Apple Silicon / Python 3.14 | Use Python 3.12. |

## Docker
```bash
docker build -t railway-face-rec .
docker run -p 8501:8501 -v face_data:/app/data railway-face-rec
```
(Use the *Camera snapshot* tab in Docker - the server has no webcam.)

## Notes & limits
- Face data is biometric and personal: `data/` is git-ignored; keep it private and get consent before enrolling people.
- Recognition is not spoof-proof: a printed photo or a screen can fool any basic 2D system. For real security add liveness detection and use it as a second factor.
