FROM python:3.12-slim

WORKDIR /app

# libgl/glib are needed by OpenCV; dlib-bin ships pre-built, so no compiler is required
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Persist enrolled faces, logs and settings outside the container:
#   docker run -p 8501:8501 -v face_data:/app/data railway-face-rec
VOLUME ["/app/data"]
EXPOSE 8501

CMD ["sh", "-c", "streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]
