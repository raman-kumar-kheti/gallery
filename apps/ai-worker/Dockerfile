FROM python:3.11-slim

WORKDIR /app

# System dependencies for InsightFace + FAISS
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download InsightFace model (buffalo_l)
RUN python -c "import insightface; app = insightface.app.FaceAnalysis(name='buffalo_l'); app.prepare(ctx_id=-1)"

COPY . .

# Create indexes directory
RUN mkdir -p /app/indexes

CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info", "--concurrency=2", "-Q", "ai_processing"]
