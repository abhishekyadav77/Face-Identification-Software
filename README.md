# 🚆 Railway Face Identification Software

An AI-powered **Face Identification and Attendance Management System** designed to identify registered individuals, record attendance, and detect unauthorized persons using facial recognition.

The system is built with **Python, Streamlit, OpenCV, and face-recognition** and provides a simple web-based dashboard for face enrollment, identification, attendance tracking, logs, and alerts.

---

## 📌 Project Overview

Railway stations and railway organizations require reliable systems for monitoring authorized personnel and maintaining attendance records.

This project provides a prototype solution that combines **computer vision and face recognition** to:

* Register and enroll authorized individuals.
* Identify registered individuals using facial features.
* Automatically record attendance.
* Detect unknown or unauthorized individuals.
* Maintain attendance and identification logs.
* Display alerts for unauthorized detections.
* Provide a centralized dashboard for monitoring.

> **Note:** This project is developed as an academic/portfolio prototype and is not intended to replace production-grade railway security systems.

---

## ✨ Features

### 👤 Face Enrollment

* Add a person's name and identification details.
* Capture/upload a facial image.
* Store enrolled face data locally.
* Use enrolled faces for future identification.

### 🔍 Face Identification

* Detect faces from images.
* Compare detected faces with enrolled faces.
* Display the identified person's information.
* Handle unknown faces when no matching identity is found.

### 📋 Attendance Management

* Automatically record recognized individuals.
* Store attendance information with timestamps.
* View attendance records through the dashboard.

### 🚨 Unauthorized Person Detection

* Detect faces that are not present in the registered database.
* Record unauthorized detections.
* Store relevant logs/images locally.
* Display alerts through the application.

### 📊 Dashboard

The dashboard provides access to:

* Total registered individuals
* Attendance information
* Identification activity
* Unauthorized detection alerts
* System statistics

### 📜 Logs & Records

The application provides separate views for:

* Attendance records
* Identification logs
* Unauthorized detection logs
* System alerts

### ⚙️ Settings

The application includes configurable settings for managing system behavior and application preferences.

---

## 🛠️ Technology Stack

| Technology       | Purpose                                    |
| ---------------- | ------------------------------------------ |
| Python           | Core programming language                  |
| Streamlit        | Web application interface                  |
| OpenCV           | Image processing and face detection        |
| face-recognition | Facial feature extraction and comparison   |
| NumPy            | Numerical processing                       |
| Pandas           | Data handling and CSV management           |
| Docker           | Application containerization               |
| Git & GitHub     | Version control and source code management |

---

## 📂 Project Structure

```text
Face-Identification-Software/
│
├── app.py
├── Dockerfile
├── requirements.txt
├── README.md
├── .gitignore
├── .dockerignore
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

> Runtime-generated files such as attendance records, alerts, enrolled face images, and unauthorized-person logs are excluded from Git using `.gitignore`.

---

## 🔄 How the System Works

```text
                ┌──────────────────┐
                │   User / Admin   │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │    Streamlit UI   │
                └────────┬─────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    Face Enrollment  Face Scanner   Dashboard
          │              │              │
          ▼              ▼              ▼
    Known Faces     Face Detection   Records/Stats
                         │
                         ▼
                  Face Recognition
                         │
                 ┌───────┴────────┐
                 ▼                ▼
             Recognized         Unknown
                 │                │
                 ▼                ▼
             Attendance        Alert/Log
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/abhishekyadav77/Face-Identification-Software.git
```

Move into the project directory:

```bash
cd Face-Identification-Software
```

---

### 2. Create a Virtual Environment

#### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

> The `venv` folder is for local development only and should **not** be committed to GitHub.

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

The application will normally be available at:

```text
http://localhost:8501
```

---

## 🐳 Running with Docker

The project includes a Dockerfile for containerized deployment.

### Build the Docker image

```bash
docker build -t railway-face-identification .
```

### Run the container

```bash
docker run -p 8501:8501 railway-face-identification
```

Then open:

```text
http://localhost:8501
```

---

## ☁️ Deployment

The project can be deployed using a Docker-compatible hosting platform such as **Render**.

Recommended deployment flow:

```text
GitHub Repository
        ↓
     Render
        ↓
    Dockerfile
        ↓
  Streamlit Application
```

The Dockerfile installs the required system dependencies and Python packages before starting the Streamlit application.

---

## 📷 Camera Usage

The application supports image-based face identification through the web interface.

For local development, OpenCV can access a webcam connected to the computer running the application.

However, when the application is deployed to a cloud server, OpenCV's direct webcam access refers to the **server's hardware**, not the user's laptop or phone camera.

Therefore, the deployed version should use browser-based camera capture or image upload functionality.

---

## ⚠️ Limitations

This project is a prototype and has several limitations:

1. **Face recognition accuracy** can be affected by lighting, camera quality, face angle, distance, and appearance changes.

2. **False positives and false negatives** are possible during identification.

3. **Direct OpenCV webcam access does not work remotely** in the same way as it does on a local computer.

4. **Local file-based storage is not suitable for large-scale deployment.**

5. **Cloud deployment may use temporary storage**, meaning generated attendance records and uploaded face data may not persist after certain server restarts or redeployments unless persistent storage is configured.

6. **Performance depends on available CPU and memory**, particularly when processing multiple faces.

7. **The current system does not provide advanced liveness detection**, so it should not be considered resistant to sophisticated spoofing attacks.

8. **Biometric data requires careful security and privacy management** in any real-world implementation.

9. The system would require a proper database and scalable architecture for deployment across multiple railway locations.

---

## 🔐 Privacy & Security

Facial images and face-recognition data are sensitive information.

For this reason:

* Actual enrolled face images should not be committed to GitHub.
* Runtime-generated attendance data is excluded using `.gitignore`.
* Credentials and secrets should be stored using environment variables.
* Production deployments should use secure databases and appropriate access controls.
* Real-world deployment should follow applicable privacy, security, and organizational requirements.

---

## 🔮 Future Improvements

Possible future enhancements include:

* [ ] PostgreSQL/MongoDB database integration
* [ ] Cloud-based persistent storage
* [ ] Browser-based live camera recognition
* [ ] Real-time multi-face recognition
* [ ] Advanced liveness detection
* [ ] Anti-spoofing mechanisms
* [ ] Role-based authentication
* [ ] Admin/user management
* [ ] Email/SMS alerts
* [ ] Real-time notifications
* [ ] Improved recognition accuracy
* [ ] Multi-station support
* [ ] Attendance analytics and reports
* [ ] Scalable cloud deployment
* [ ] Improved biometric data encryption

---

## 🎯 Use Cases

The prototype can be adapted for:

* Railway employee attendance
* Staff identification
* Restricted-area monitoring
* Office attendance systems
* Campus security
* Access-control prototypes
* Personnel monitoring

---

## 👨‍💻 Author

**Abhishek Kumar Yadav**

B.Tech Computer Science & Engineering
Lucknow, Uttar Pradesh, India

### Connect with me

* **GitHub:** https://github.com/abhishekyadav77
* **LinkedIn:** https://www.linkedin.com/in/abhishek-yadav-mzp/
* **LeetCode:** https://leetcode.com/u/abhishek_yadav_12/

---

## 📄 License

This project is developed for **educational, academic, and portfolio purposes**.

You are free to study and modify the code for learning purposes. For commercial or production use, review the project's dependencies, licenses, privacy requirements, and security considerations first.

---

## ⭐ Acknowledgement

This project combines Python-based computer vision, face recognition, and Streamlit to demonstrate how an AI-assisted identification and attendance system can be developed as a practical software project.

If you find the project useful, consider giving the repository a ⭐ on GitHub.
