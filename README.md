# 🚆 Railway Face Identification Software

[![Live Demo](https://img.shields.io/badge/Live-Demo-success?style=for-the-badge)](https://face-identification-software-dafo.onrender.com)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge\&logo=github)](https://github.com/abhishekyadav77/Face-Identification-Software)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge\&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red?style=for-the-badge\&logo=streamlit)](https://streamlit.io/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?style=for-the-badge\&logo=opencv)](https://opencv.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge\&logo=docker)](https://www.docker.com/)

An AI-powered **Face Identification and Attendance Management System** designed to identify registered individuals, record attendance, and detect unauthorized persons using facial recognition.

The system is built using **Python, Streamlit, OpenCV, and face-recognition** and provides a web-based interface for face enrollment, identification, attendance tracking, logs, alerts, and system management.

---

## 🌐 Live Demo

🚀 **[Open Live Application](https://face-identification-software-dafo.onrender.com)**

> **Note:** The live deployment is intended primarily for demonstration purposes. Browser-based image/camera capture should be used for the online version because direct OpenCV webcam access is designed for local execution.

---

## 📌 Project Overview

Railway organizations require reliable systems for identifying authorized personnel and maintaining attendance records.

This project demonstrates a computer-vision-based solution that can:

* Register authorized individuals.
* Enroll facial information.
* Identify registered individuals.
* Automatically record attendance.
* Detect unknown or unauthorized individuals.
* Maintain identification and attendance logs.
* Generate alerts for unauthorized detections.
* Provide a centralized dashboard for monitoring.

> **Disclaimer:** This is an academic and portfolio-level prototype. It is not intended to replace production-grade railway security or biometric systems.

---

## ✨ Key Features

### 👤 Face Enrollment

* Register a new individual.
* Capture or upload a facial image.
* Store enrolled face information locally.
* Use the enrolled information for future identification.

### 🔍 Face Identification

* Detect faces from input images.
* Compare detected faces with registered face data.
* Identify known individuals.
* Handle unknown faces when no match is found.

### 📋 Attendance Management

* Automatically record attendance for recognized individuals.
* Store attendance information with timestamps.
* View attendance records through the dashboard.

### 🚨 Unauthorized Person Detection

* Detect individuals who are not present in the registered database.
* Record unauthorized detections.
* Store relevant logs/images locally.
* Display alerts through the application.

### 📊 Dashboard

The dashboard provides access to:

* Registered individuals
* Attendance information
* Identification activity
* Unauthorized detections
* Alerts
* System statistics

### 📜 Logs & Records

The application provides dedicated views for:

* Attendance records
* Identification logs
* Unauthorized detection logs
* System alerts

### ⚙️ Settings

The application provides settings for managing application preferences and system behavior.

---

## 🛠️ Technology Stack

| Technology           | Purpose                              |
| -------------------- | ------------------------------------ |
| **Python**           | Core programming language            |
| **Streamlit**        | Web application and dashboard        |
| **OpenCV**           | Image processing and computer vision |
| **face-recognition** | Face encoding and facial comparison  |
| **NumPy**            | Numerical operations                 |
| **Pandas**           | Data processing and CSV handling     |
| **Docker**           | Containerization and deployment      |
| **Git**              | Version control                      |
| **GitHub**           | Source code hosting                  |

---

## 🏗️ System Architecture

```text
                         ┌────────────────────┐
                         │      User/Admin    │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │    Streamlit UI    │
                         └─────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
       Face Enrollment       Face Scanner          Dashboard
              │                    │                    │
              ▼                    ▼                    ▼
        Known Faces         Face Detection       Statistics
                                   │
                                   ▼
                           Face Recognition
                                   │
                         ┌─────────┴─────────┐
                         │                   │
                         ▼                   ▼
                    Recognized            Unknown
                         │                   │
                         ▼                   ▼
                    Attendance          Alert / Log
```

---

## 🔄 How It Works

### Step 1 — Face Enrollment

An authorized person's facial image is captured or uploaded through the enrollment section.

```text
Person
   ↓
Capture / Upload Image
   ↓
Face Detection
   ↓
Face Encoding
   ↓
Store Known Face
```

### Step 2 — Face Identification

The scanner receives an image and searches for faces.

```text
Input Image
     ↓
Face Detection
     ↓
Face Encoding
     ↓
Compare with Known Faces
     ↓
┌──────────────┴──────────────┐
│                             │
Known Person              Unknown Person
│                             │
↓                             ↓
Attendance               Alert / Log
```

### Step 3 — Attendance

When a registered person is successfully identified, the system records their attendance along with the relevant timestamp.

### Step 4 — Unauthorized Detection

When the detected face does not match any registered person, the system treats it as an unknown/unauthorized detection and records an alert.

---

## 📂 Project Structure

```text
Face-Identification-Software/
│
├── app.py
├── Dockerfile
├── .dockerignore
├── .gitignore
├── README.md
├── requirements.txt
│
├── .streamlit/
│   └── config.toml
│
├── assets/
│   ├── logo.png
│   └── style.css
│
├── utils/
│   ├── db_helper.py
│   ├── live_camera.py
│   ├── simple_facerec.py
│   ├── ui_helper.py
│   └── upload_face.py
│
├── views/
│   ├── dashboard.py
│   ├── scanner.py
│   ├── enroll.py
│   ├── attendance.py
│   ├── alerts.py
│   ├── logs.py
│   └── settings.py
│
└── data/
    ├── known_faces/
    ├── unauthorized_logs/
    ├── sounds/
    └── Images/
```

### Runtime Data

The following data is generated while using the application:

```text
data/
├── known_faces/
├── unauthorized_logs/
├── attendance.csv
├── alerts.csv
└── settings.json
```

These runtime files are intentionally excluded from GitHub using `.gitignore`, especially the facial images and identification data.

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/abhishekyadav77/Face-Identification-Software.git
```

Navigate into the project:

```bash
cd Face-Identification-Software
```

---

### 2. Create a Virtual Environment

#### Windows

```powershell
python -m venv venv
```

Activate the environment:

```powershell
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

> The `venv` directory is only for local development and should **not** be uploaded to GitHub.

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run the Application

```bash
streamlit run app.py
```

The application will normally open at:

```text
http://localhost:8501
```

---

## 🐳 Docker Setup

The project includes a `Dockerfile` for containerized execution and deployment.

### Build the Docker Image

```bash
docker build -t railway-face-identification .
```

### Run the Container

```bash
docker run -p 8501:8501 railway-face-identification
```

Open:

```text
http://localhost:8501
```

---

## ☁️ Deployment

The project can be deployed using a Docker-compatible cloud platform such as **Render**.

Recommended deployment architecture:

```text
GitHub
   ↓
Render
   ↓
Dockerfile
   ↓
Python Environment
   ↓
Streamlit
   ↓
Live Web Application
```

The Dockerfile installs the required system dependencies and Python packages before starting the Streamlit application.

### Deployment Steps

1. Push the project to GitHub.
2. Create a new Web Service on Render.
3. Connect the GitHub repository.
4. Select the `main` branch.
5. Choose Docker as the environment.
6. Use the existing `Dockerfile`.
7. Deploy the application.
8. Copy the generated Render URL.
9. Replace `YOUR_LIVE_LINK_HERE` in this README with the live URL.

---

## 📷 Camera & Deployment Behavior

### Local Application

When running locally, OpenCV can access a webcam connected to the computer running the application.

### Cloud Deployment

A cloud server cannot directly access the webcam connected to your personal laptop.

Therefore:

```text
Local:
Laptop Camera → OpenCV → Python Application
```

but:

```text
Cloud:
User Browser → Internet → Cloud Server
```

For the deployed application, browser-based camera capture or image upload is the appropriate approach.

---

## 🔐 Privacy & Security

This application deals with facial recognition and therefore may process sensitive biometric information.

Important security practices include:

* Do not upload actual face images to GitHub.
* Do not commit attendance records containing personal information.
* Do not commit `.env` files or credentials.
* Keep runtime biometric data outside version control.
* Use environment variables for secrets.
* Use proper authentication and authorization in production.
* Use secure databases instead of local files for large-scale deployment.
* Apply appropriate privacy and data-retention policies.

The repository's `.gitignore` excludes runtime face images, logs, CSV files, virtual environments, and secrets.

---

## ⚠️ Limitations

This project has several limitations:

1. **Recognition accuracy** can be affected by lighting, camera quality, face angle, distance, and changes in appearance.

2. **False positives and false negatives** are possible during face identification.

3. **Direct OpenCV webcam access is primarily suitable for local execution** and does not directly access the user's camera when the application is hosted on a remote server.

4. **File-based storage** is suitable for a prototype but is not ideal for a large-scale production system.

5. **Cloud filesystem limitations** may cause generated data to be lost after certain restarts or redeployments unless persistent storage is configured.

6. **Performance depends on available hardware resources**, especially when processing multiple faces.

7. **The current implementation does not provide advanced liveness detection.**

8. **Basic face recognition can be vulnerable to spoofing**, such as presenting a photograph or screen image, if additional anti-spoofing mechanisms are not implemented.

9. **Biometric information requires strong privacy and security controls** in a real-world deployment.

10. **The system is not designed for large-scale multi-station deployment** without additional database, authentication, and infrastructure improvements.

---

## 🔮 Future Enhancements

Possible improvements include:

* [ ] MongoDB/PostgreSQL database integration
* [ ] Cloud-based persistent storage
* [ ] Browser-based real-time camera recognition
* [ ] Real-time multi-face recognition
* [ ] Advanced liveness detection
* [ ] Anti-spoofing mechanisms
* [ ] Secure user authentication
* [ ] Role-based access control
* [ ] Admin and employee management
* [ ] Email/SMS notifications
* [ ] Real-time alerts
* [ ] Attendance analytics
* [ ] PDF/Excel attendance reports
* [ ] Multi-station support
* [ ] Improved recognition accuracy
* [ ] Encrypted biometric storage
* [ ] Scalable cloud infrastructure

---

## 🎯 Potential Use Cases

The prototype can be adapted for:

* 🚆 Railway employee attendance
* 👨‍💼 Staff identification
* 🔐 Restricted-area monitoring
* 🏢 Office attendance systems
* 🎓 Campus security
* 🛂 Access-control prototypes
* 👥 Personnel monitoring

---

## 📸 Application Modules

The application includes the following major modules:

| Module              | Description                             |
| ------------------- | --------------------------------------- |
| **Dashboard**       | Displays system statistics and activity |
| **Face Enrollment** | Registers new individuals               |
| **Face Scanner**    | Performs face identification            |
| **Attendance**      | Displays attendance records             |
| **Alerts**          | Shows unauthorized detection alerts     |
| **Logs**            | Displays identification/activity logs   |
| **Settings**        | Manages application configuration       |

---

## 💻 Requirements

Recommended environment:

```text
Python: 3.12
Operating System: Windows / Linux / macOS
RAM: 4 GB or more recommended
Internet: Required for cloud deployment
```

The Docker configuration uses Python 3.12 for a consistent deployment environment.

---

## 📦 Main Dependencies

The project uses libraries including:

```text
streamlit
numpy
pandas
opencv-python-headless
dlib-bin
face_recognition_models
```

See `requirements.txt` for the complete dependency list.

---

## 🧪 Project Status

**Status: Completed Prototype / Portfolio Project**

The core functionality includes:

* ✅ Face enrollment
* ✅ Face identification
* ✅ Attendance management
* ✅ Unauthorized detection
* ✅ Alerts
* ✅ Logs
* ✅ Dashboard
* ✅ Docker support
* ✅ GitHub repository
* ✅ Cloud deployment support

---

## 👨‍💻 Author

### Abhishek Kumar Yadav

**B.Tech Computer Science & Engineering**

Lucknow, Uttar Pradesh, India

### Connect With Me

* 🔗 **GitHub:** https://github.com/abhishekyadav77
* 💼 **LinkedIn:** https://www.linkedin.com/in/abhishek-yadav-mzp/
* 💻 **LeetCode:** https://leetcode.com/u/abhishek_yadav_12/

---

## 📄 License

This project is developed for **educational, academic, and portfolio purposes**.

The project and its dependencies may have their own respective licenses. Review dependency licenses before using the project for commercial purposes.

---

## ⭐ Support

If you found this project useful or interesting, consider giving the repository a ⭐ on GitHub.

Your feedback and suggestions are welcome.

---

## 🙌 Acknowledgement

This project demonstrates the practical use of **computer vision and facial recognition** to build an AI-assisted identification and attendance management system.

It was developed as a learning and portfolio project to explore the integration of:

**Python + OpenCV + Face Recognition + Streamlit + Docker + Cloud Deployment**
