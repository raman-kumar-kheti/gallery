# Gallery — AI-Powered Event Photo Gallery SaaS

> Guests scan a QR code → upload a selfie → instantly find all their photos using AI face recognition.

---

## Architecture Overview

```
gallery/
├── apps/
│   ├── frontend-web/     # Next.js 14 App Router + TypeScript + TailwindCSS
│   ├── backend-api/      # FastAPI + SQLAlchemy + Alembic + PostgreSQL
│   └── ai-worker/        # Celery + InsightFace + FAISS
├── shared/
│   ├── types/            # Shared TypeScript types
│   └── config/           # Zod env schemas
├── docker-compose.yml
├── .env.example
├── Makefile
└── README.md
```

---

## Tech Stack

| Layer      | Technology                              |
|------------|-----------------------------------------|
| Frontend   | Next.js 14, TypeScript, TailwindCSS     |
| Backend    | FastAPI, SQLAlchemy (async), Alembic    |
| Database   | PostgreSQL 16 (UUID PKs)               |
| Queue      | Redis + Celery                          |
| AI         | InsightFace, FAISS, Pillow              |
| Storage    | Cloudflare R2 (S3-compatible)           |
| Payments   | Razorpay                                |

---

## Quickstart

### Prerequisites
- Docker + Docker Compose
- Node.js 20+
- Python 3.11+

### 1. Clone and configure
```bash
git clone <repo>
cd gallery
make setup-env      # copies .env.example → .env
# Edit .env with your real values
```

### 2. Start all services
```bash
make up
```

### 3. Run database migrations
```bash
make migrate
```

### 4. Access services
| Service     | URL                       |
|-------------|---------------------------|
| Frontend    | http://localhost:3000     |
| Backend API | http://localhost:8000     |
| API Docs    | http://localhost:8000/docs |
| Flower      | http://localhost:5555     |

---

## User Types

| Type         | Organization | Team RBAC | Events | Pay Model        |
|--------------|-------------|-----------|--------|------------------|
| Studio       | ✅           | ✅         | ∞      | Subscription     |
| Photographer | ❌           | ❌         | ∞      | Subscription     |
| Customer     | ❌           | ❌         | Per-event | Pay-per-event |

---

## AI Pipeline

### Upload Flow
1. Photo uploaded → stored in Cloudflare R2
2. Metadata saved to PostgreSQL
3. Celery task queued → AI worker picks up
4. InsightFace generates face embedding vector
5. Embedding added to event's FAISS index
6. `faiss_pos` mapping saved to PostgreSQL
7. Thumbnail generated via Pillow

### Guest Search Flow
1. Guest scans QR code → mobile web page
2. Guest uploads selfie
3. Backend generates query embedding (InsightFace)
4. FAISS similarity search on event index
5. `faiss_pos` → image metadata mapping
6. Matching photos returned to guest
7. Session cached in `search_sessions` (avoid re-processing)

---

## FAISS Index Design
- One FAISS `IndexFlatL2` per event: `indexes/event_{id}.index`
- `images.faiss_pos` maps PostgreSQL rows → FAISS vector positions
- Indexes are volume-mounted and persist across restarts

---

## Development Commands

```bash
make up               # Start all containers
make down             # Stop all containers
make migrate          # Run migrations
make makemigrations MSG="add column x"  # Generate migration
make logs-backend     # Tail backend logs
make logs-worker      # Tail worker logs
make shell-backend    # Shell into backend container
make shell-db         # psql into database
make flower           # Celery task monitoring
```

---

## API Structure

```
/api/v1/
├── auth/           # Google OAuth + JWT
├── events/         # CRUD + ownership
├── images/         # Upload + presigned URLs
├── search/         # Guest selfie search
├── qr/             # QR code generation
├── payments/       # Razorpay integration
└── organizations/  # Studio workspace management
```
