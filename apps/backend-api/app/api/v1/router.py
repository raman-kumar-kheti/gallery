from fastapi import APIRouter

from app.api.v1 import auth, events, images, search, qr, payments, organizations, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(images.router, prefix="/images", tags=["Images"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(qr.router, prefix="/qr", tags=["QR Codes"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

