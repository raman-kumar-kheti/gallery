# 🚀 Gallery — Backend API

This is the FastAPI backend API for the Gallery project—an AI-powered event photo delivery SaaS platform. It handles user authentication, event management, R2 storage interaction, PostgreSQL database operations, and triggers asynchronous face analysis tasks in the Celery worker pipeline.

---

## 🛠️ Setup & Local Installation

### Prerequisites

- **Python**: `>=3.11` (recommended `3.11` or `3.12`)
- **Services**: Postgres (with `pgvector` extension) and Redis must be running (either locally or via Docker Compose from the root directory).

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

### 2. Environment Variables

This project relies on the **root `.env`** file as its single source of truth. 

To override specific variables for local development, create a copy called `.env.local` inside this directory:
```bash
cp .env.local.example .env.local  # If an example is present, otherwise create manually
```
Ensure your database credentials and Redis URL in `.env` point to your local development instances:
```env
DATABASE_URL=postgresql+asyncpg://gallery:gallery@localhost:5432/gallery
REDIS_URL=redis://localhost:6379/0
```

---

## 🗄️ Database Migrations (Alembic)

Database schema updates are managed strictly through Alembic. **Do not modify the database schema manually.**

### Running Migrations Locally

To apply all migrations to the database from your local machine:
```bash
# Ensure your virtual environment is active and variables are set
alembic upgrade head
```

### Creating a New Migration

When you update any SQLAlchemy model in `app/models/`:
```bash
alembic revision --autogenerate -m "describe your changes"
```

### Running Migrations via Docker (Root Orchestrated)

If you are running the backend inside Docker, you can run migrations using the root `Makefile`:
```bash
# Apply migrations
make migrate

# Generate new migration
make makemigrations MSG="your changes summary"
```

---

## ⚡ Running the Application

### 1. Running Locally (Development Mode)

To start the FastAPI server locally with auto-reload:
```bash
# Ensure your virtual environment is active
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
The API will be accessible at `http://127.0.0.1:8000`.

### 2. Running via Docker

To start all services (Postgres, Redis, Backend, Worker, Frontend) together:
```bash
# From the root directory
make up
```

---

## 📖 API Documentation

FastAPI automatically generates interactive API documentation. When the backend is running, you can access the docs at:

*   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) (Highly recommended for testing endpoints interactively)
*   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
