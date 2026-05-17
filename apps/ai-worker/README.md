# 🤖 Gallery — AI Worker

This is the Celery background worker service for the Gallery project. It handles CPU- and memory-intensive AI pipelines asynchronously, including face detection & extraction (via InsightFace) and per-event vector indexing & face searches (via FAISS flat inner-product vector indexes).

---

## 🛠️ Setup & Local Installation

### Prerequisites

- **Python**: `>=3.11` (recommended `3.11` or `3.12`)
- **System Packages**: InsightFace and FAISS require certain system-level dependencies for image processing and compilation.
  - **On Ubuntu/Debian**:
    ```bash
    sudo apt-get update && sudo apt-get install -y gcc g++ libgomp1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1-mesa-glx libpq-dev
    ```
- **Redis**: Redis must be running as it serves as the Celery message broker and result backend.

### 1. Virtual Environment Setup

**Mandatory**: You must use a local virtual environment (`.venv`) for this project as outlined in `PROJECT_RULES.md`.

1. **Create the virtual environment**:
   ```bash
   python -m venv .venv
   ```

2. **Activate the virtual environment**:
   - **On Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```
   - **On Windows**:
     ```bash
     .venv\Scripts\activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Pre-downloading the InsightFace Model

To prevent slow initialization during the first background job, pre-download and prepare the face detection model (`buffalo_l`) by running this command in your terminal (with your virtual environment active):
```bash
python -c "import insightface; app = insightface.app.FaceAnalysis(name='buffalo_l'); app.prepare(ctx_id=-1)"
```

### 3. Environment Variables

This project relies on the **root `.env`** file as its single source of truth. 

To override specific variables for local development, create a copy called `.env.local` inside this directory:
```bash
# Point Celery to your local Redis instance
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## ⚡ Running the Worker

### 1. Running the Celery Worker Locally

To start the Celery worker processing background tasks locally on the `ai_processing` queue:
```bash
# Ensure your virtual environment is active
celery -A worker.celery_app worker --loglevel=info --concurrency=2 -Q ai_processing
```

### 2. Monitoring Celery Tasks with Flower

Flower is a real-time web-based monitoring tool for Celery. To run Flower locally to inspect job queues, workers, and task history:
```bash
# Ensure your virtual environment is active
celery -A worker.celery_app flower
```
By default, the Flower dashboard will be accessible at [http://localhost:5555](http://localhost:5555).

### 3. Running via Docker

To start all containers, including the AI worker and Redis broker:
```bash
# From the root directory
make up
```

---

## 📁 FAISS Vector Indexes Storage

*   FAISS vector index files (`.index` files) are generated dynamically for each event (e.g. `event_{event_id}.index`).
*   Locally, they are stored under the folder specified by your settings (usually `apps/ai-worker/indexes/`). Make sure this folder is ignored by version control to avoid pushing local vector indexes.
