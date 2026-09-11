FROM python:3.11-slim

WORKDIR /app

# System dependencies required by dlib / OpenCV
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-python-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Prevent dlib from using all available CPU cores/RAM
ENV CMAKE_BUILD_PARALLEL_LEVEL=1
ENV MAKEFLAGS=-j1

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    setuptools \
    wheel

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["sh", "-c", "streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]