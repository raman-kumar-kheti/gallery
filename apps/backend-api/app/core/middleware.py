"""
Custom FastAPI middleware:
- RequestID: Assigns a unique request ID to every request (for log tracing)
- AuditMiddleware: Logs sensitive action routes to audit_logs
"""
import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger("gallery.middleware")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Adds a unique X-Request-ID header to every request and response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        logger.info(
            f"{request.method} {request.url.path} → {response.status_code} ({duration_ms}ms) [{request_id}]"
        )
        return response
