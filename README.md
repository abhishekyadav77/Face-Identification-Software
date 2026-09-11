# 🛡️ RAILWAY FACE REC PRO

### Face Recognition, Attendance & Security Monitoring System

RAILWAY FACE REC PRO is a Python-based face recognition application built using **Streamlit, OpenCV, face_recognition and dlib**.

It can recognize registered people, maintain attendance records, track detection logs and generate alerts for unknown faces.

## 🚀 Features

- 👤 Face Enrollment
- 📷 Face Detection & Recognition
- 🕐 Attendance Management
- 📋 Detection Logs
- 🚨 Unknown Face Alerts
- ⚙️ Settings & Data Management
- 🌐 Browser Demo Mode
- 🐳 Docker Support
- ☁️ Render Deployment

## 🛠️ Technologies

- Python
- Streamlit
- OpenCV
- face_recognition
- dlib
- NumPy
- Pandas
- Docker
- GitHub
- Render

## 📂 Project Structure

    RAIL/
    ├── app.py
    ├── requirements.txt
    ├── README.md
    │
    ├── data/
    │   ├── known_faces/
    │   ├── unauthorized_logs/
    │   ├── attendance.csv
    │   └── alerts.csv
    │
    ├── pages/
    │   ├── 1_📷_Live_Scanner.py
    │   ├── 2_➕_Enroll_Person.py
    │   ├── 3_📋_Detection_Logs.py
    │   ├── 4_🚨_Unknown_Alerts.py
    │   ├── 5_🕐_Attendance.py
    │   └── 6_⚙_Settings.py
    │
    └── utils/
        ├── db_helper.py
        ├── simple_facerec.py
        ├── ui_helper.py
        └── upload_face.py

## 🌐 Live Demo

https://face-identification-software.onrender.com/

## 💻 Run Locally

Clone the repository:

    git clone https://github.com/YOUR_USERNAME/RAIL.git
    cd RAIL

Create a virtual environment:

    python -m venv venv

Activate it on Windows:

    venv\Scripts\activate

Install dependencies:

    pip install -r requirements.txt

Run the application:

    streamlit run app.py

Open in your browser:

    http://localhost:8501

## 🐳 Deployment

The application is containerized using **Docker** and deployed on **Render**.

Python → Streamlit → Docker → GitHub → Render

## 🔮 Future Improvements

- 🔐 User Authentication & Role-Based Access
- 🗄️ PostgreSQL / Cloud Database
- ☁️ Persistent Cloud Storage
- 📹 Multi-Camera Support
- 📊 Advanced Analytics Dashboard
- 🛡️ Liveness / Anti-Spoofing Detection
- 📧 Email & SMS Alerts
- ⚡ Real-Time Monitoring

## 👨‍💻 Author

**Abhishek Kumar Yadav**

B.Tech CSE

## ⚠️ Disclaimer

This project is developed for educational, academic and demonstration purposes. Production use of biometric systems requires proper security, privacy and data-protection measures.
