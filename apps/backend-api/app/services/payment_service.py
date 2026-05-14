import razorpay
import hmac
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.config import settings
from app.models.payment import Payment, PaymentStatus, PaymentProvider
from app.repositories.event_repo import EventRepository


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = razorpay.Client(
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
        )

    async def create_order(
        self,
        amount_inr: float,
        user_id,
        event_id=None,
        subscription_id=None,
        currency: str = "INR",
    ) -> dict:
        """Create a Razorpay order and a pending payment record."""
        amount_paise = int(amount_inr * 100)  # Razorpay uses paise

        order = self.client.order.create({
            "amount": amount_paise,
            "currency": currency,
            "payment_capture": 1,
        })

        payment = Payment(
            user_id=user_id,
            event_id=event_id,
            subscription_id=subscription_id,
            amount=amount_inr,
            currency=currency,
            provider=PaymentProvider.razorpay,
            provider_order_id=order["id"],
            status=PaymentStatus.pending,
        )
        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)

        return {
            "order_id": order["id"],
            "payment_id": str(payment.id),
            "amount": amount_paise,
            "currency": currency,
            "razorpay_key": settings.razorpay_key_id,
        }

    async def verify_and_capture(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> Payment:
        """Verify Razorpay signature and mark payment captured."""
        # Verify signature
        body = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected_signature = hmac.new(
            settings.razorpay_key_secret.encode(),
            body.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, razorpay_signature):
            raise HTTPException(status_code=400, detail="Invalid payment signature")

        # Update payment record
        from sqlalchemy import select
        from app.models.payment import Payment as PaymentModel
        result = await self.db.execute(
            select(PaymentModel).where(
                PaymentModel.provider_order_id == razorpay_order_id
            )
        )
        payment = result.scalar_one_or_none()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment record not found")

        payment.provider_payment_id = razorpay_payment_id
        payment.status = PaymentStatus.captured
        await self.db.flush()
        await self.db.refresh(payment)
        return payment

    async def handle_webhook(self, payload: dict, signature: str) -> None:
        """Handle Razorpay webhook events."""
        # Verify webhook signature
        webhook_body = str(payload)
        expected = hmac.new(
            settings.razorpay_webhook_secret.encode(),
            webhook_body.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected, signature):
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        event_type = payload.get("event")
        if event_type == "payment.captured":
            payment_data = payload["payload"]["payment"]["entity"]
            # Update payment status
            from sqlalchemy import select
            from app.models.payment import Payment as PaymentModel
            result = await self.db.execute(
                select(PaymentModel).where(
                    PaymentModel.provider_payment_id == payment_data["id"]
                )
            )
            payment = result.scalar_one_or_none()
            if payment:
                payment.status = PaymentStatus.captured
                await self.db.flush()
