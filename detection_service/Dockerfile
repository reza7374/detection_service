FROM python:3.10-slim-bookworm

# ---- environment stability fixes ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Force IPv4 (fixes many Debian repo issues on Docker/Fedora)
RUN echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4

# Optional but improves retry stability
RUN echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/99retries

# ---- system dependencies (OpenCV / MediaPipe) ----
RUN apt-get update -o Acquire::Retries=5 && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libv4l-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- working directory ----
WORKDIR /app

# ---- install python dependencies first (better caching) ----
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- copy source code ----
COPY . .

CMD ["python", "detection_service.py"]