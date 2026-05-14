from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import uuid

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.services.payment_service import PaymentService

router = APIRouter()


class CreateOrderRequest(BaseModel):
    amount: float
    event_id: Optional[uuid.UUID] = None
    subscription_id: Optional[uuid.UUID] = None
    currency: str = "INR"


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/create-order")
async def create_order(
    body: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Razorpay order for event payment or subscription."""
    service = PaymentService(db)
    order = await service.create_order(
        amount_inr=body.amount,
        user_id=current_user.id,
        event_id=body.event_id,
        subscription_id=body.subscription_id,
        currency=body.currency,
    )
    return order


@router.post("/verify")
async def verify_payment(
    body: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify Razorpay payment signature and capture the payment."""
    service = PaymentService(db)
    payment = await service.verify_and_capture(
        body.razorpay_order_id,
        body.razorpay_payment_id,
        body.razorpay_signature,
    )
    return {
        "payment_id": str(payment.id),
        "status": payment.status,
        "amount": float(payment.amount),
        "currency": payment.currency,
    }


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    """Razorpay webhook receiver for async payment events."""
    payload = await request.json()
    service = PaymentService(db)
    await service.handle_webhook(payload, x_razorpay_signature)
    return {"status": "ok"}
