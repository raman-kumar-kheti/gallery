from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class GalleryException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(GalleryException):
    def __init__(self, resource: str, resource_id: str = ""):
        msg = f"{resource} not found"
        if resource_id:
            msg = f"{resource} '{resource_id}' not found"
        super().__init__(msg, status_code=404)


class ForbiddenError(GalleryException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(detail, status_code=403)


class ConflictError(GalleryException):
    def __init__(self, detail: str):
        super().__init__(detail, status_code=409)


class StorageQuotaExceededError(GalleryException):
    def __init__(self):
        super().__init__("Storage quota exceeded", status_code=402)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(GalleryException)
    async def gallery_exception_handler(request: Request, exc: GalleryException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "type": type(exc).__name__},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "type": "ValidationError"},
        )
