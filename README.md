# 🛡️RAILWAY FACE REC PRO MODEL 1 — Biometric Terminal Console (Streamlit Model)

Welcome to the **RAILWAY FACE REC PRO** repository! This application is built entirely as a modular, high-performance biometric security terminal system using **Python** and **Streamlit**. 

## 📁 Folder Structure Overview

We have organized the files into structured subfolders representing clean separation of concerns:
├── data/                             # persistent database storage folders
│   ├── known_faces/                  # stores reference pictures of enrolled staff (Name_Role_ID.jpg)
│   ├── unauthorized_logs/            # snapshots of unrecognized intruders
│   ├── attendance.csv                # historical logs of all access events
│   └── alerts.csv                    # logs of active, unresolved security alarms
│
├── utils/                            # custom application logic modules
│   ├── db_helper.py                  # reads/writes records, handles folder creation, and data purges
│   ├── simple_facerec.py             # core face recognition engine (OpenCV face_recognition library)
│   ├── ui_helper.py                  # customized dark slate styles & visual themes injection
│   └── upload_face.py                # handles secure uploaded image stream writes to disk
│
├── pages/                            # modular streamlit page scripts (automatic navigation tabs)
│   ├── 1_📷_Live_Scanner.py          # real-time face tracking webcam capture & browser scanner demo
│   ├── 2_➕_Enroll_Person.py         # identity registry and face-profile encoder
│   ├── 3_📋_Detection_Logs.py        # logs database table search and excel-friendly CSV exports
│   ├── 4_🚨_Unknown_Alerts.py        # security threat desk for resolving flagged intrusion logs
│   ├── 5_🕐_Attendance.py            # live staff check-in analytics board
│   └── 6_⚙_Settings.py               # algorithms distance tuning metrics and hardware resets
│
├── app.py                            # main entrypoint & executive central dashboard
├── requirements.txt                  # full python dependencies list
└── README.md                         # elegant documentation and manual (this file)

## 🛠️ Installation & Getting Started

Follow these simple steps on your local machine or server to spin up the biometric node:

### 1. Prerequisite Requirements
Make sure you have **Python 3.9+** and a physical **Webcam** (if you want to test physical hardware scans) installed on your system.

### 2. Clone and Setup Environment
Open your terminal inside the project root folder and execute:

```bash
# Update pip to the latest version
python -m pip install --upgrade pip

# Install dependencies from our requirements file
pip install -r requirements.txt
```

### 3. Start the Biometric Node Server
Once the setup process finishes, launch the Streamlit instance using:

```bash
streamlit run app.py
```

The server will boot instantly, and open the console inside your default web browser at `http://localhost:8501`.

---

## 💡 Code Module Breakdown (With Deep In-Code Comments)

### 1. `app.py` (Main Entrance)
This file is the main gateway. It loads first, configures standard layouts, triggers folder check setups, and displays an elegant biometric telemetry dashboard with active metrics (staff counts, access history, active alarm flags).

### 2. `utils/db_helper.py` (Persistence Layer)
We've abstracted the datastore logic. This helper creates required folders automatically and reads/saves historical states into lightweight `attendance.csv` and `alerts.csv` spreadsheets. It includes an automated cooldown algorithm to prevent duplicating check-ins.

### 3. `utils/simple_facerec.py` (Computer Vision Engine)
Leverages `opencv` and the premium `face_recognition` models to detect faces inside frame streams, calculate a 128-dimensional biometric embedding vector, and match identity parameters. If the dependencies are absent on standard server previews, it triggers safe, interactive fallback demos!

### 4. `utils/ui_helper.py` (Visual Styling)
Applies a stunning, uniform **Dark Slate Terminal Theme** with customized cards, smooth interactive buttons, pulsating warning badges, and typography settings to deliver a cohesive experience across all pages.

### 5. `utils/upload_face.py` (Secure Profiler)
Cleans user-submitted names and designations to remove unsupported characters, assigns randomized secure hashes, and formats files to matching protocols for disk persistence.
