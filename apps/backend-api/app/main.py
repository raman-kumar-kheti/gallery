from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.api.v1.router import api_router
from app.core.exceptions import register_exception_handlers
from app.core.middleware import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify DB connection
    async with engine.begin() as conn:
        # Tables are managed by Alembic, not auto-create
        pass
    yield
    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Event Photo Gallery SaaS API",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID + response time tracing
app.add_middleware(RequestIDMiddleware)

# Register exception handlers
register_exception_handlers(app)

# Mount API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}
