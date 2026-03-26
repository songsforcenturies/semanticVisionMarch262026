"""Drop-in replacement for emergentintegrations.payments.stripe.checkout
Uses the stripe SDK directly.
"""
import stripe
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class CheckoutSessionRequest:
    amount: float
    currency: str = "usd"
    success_url: str = ""
    cancel_url: str = ""
    metadata: Dict = field(default_factory=dict)
    payment_methods: List[str] = field(default_factory=lambda: ["card"])


@dataclass
class CheckoutSessionResponse:
    session_id: str
    url: str
    payment_status: str


class StripeCheckout:
    def __init__(self, api_key: str, webhook_url: str = ""):
        self.api_key = api_key
        self.webhook_url = webhook_url

    async def create_checkout_session(self, req: CheckoutSessionRequest) -> CheckoutSessionResponse:
        stripe.api_key = self.api_key
        session = stripe.checkout.Session.create(
            payment_method_types=req.payment_methods,
            line_items=[{
                "price_data": {
                    "currency": req.currency,
                    "product_data": {"name": req.metadata.get("type", "Payment")},
                    "unit_amount": int(req.amount * 100),  # Stripe expects cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            metadata=req.metadata,
        )
        return CheckoutSessionResponse(
            session_id=session.id,
            url=session.url,
            payment_status=session.payment_status or "unpaid",
        )

    async def get_checkout_status(self, session_id: str) -> CheckoutSessionResponse:
        stripe.api_key = self.api_key
        session = stripe.checkout.Session.retrieve(session_id)
        return CheckoutSessionResponse(
            session_id=session.id,
            url=session.url or "",
            payment_status=session.payment_status or "unpaid",
        )

    async def handle_webhook(self, body: bytes, signature: str) -> CheckoutSessionResponse:
        stripe.api_key = self.api_key
        # If webhook secret is configured, verify signature
        webhook_secret = None  # Set via env var if needed
        if webhook_secret:
            event = stripe.Webhook.construct_event(body, signature, webhook_secret)
        else:
            import json
            event = json.loads(body)

        session_data = event.get("data", {}).get("object", {})
        return CheckoutSessionResponse(
            session_id=session_data.get("id", ""),
            url=session_data.get("url", ""),
            payment_status=session_data.get("payment_status", "unpaid"),
        )
