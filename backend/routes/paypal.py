"""PayPal payment routes: create orders, capture payments, webhooks."""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime, timezone
import os, httpx, base64

from database import db, logger
from auth import get_current_user
from models import PaymentTransaction, WalletTransaction, WalletTransactionType

router = APIRouter()

async def _get_paypal_credentials():
    """Get PayPal credentials from DB first, then env fallback"""
    config = await db.system_config.find_one({"key": "integration_keys"}, {"_id": 0})
    stored = config.get("value", {}) if config else {}
    client_id = stored.get("paypal_client_id") or os.environ.get("PAYPAL_CLIENT_ID", "")
    secret = stored.get("paypal_secret") or os.environ.get("PAYPAL_SECRET", "")
    mode = stored.get("paypal_mode", "sandbox")
    base_url = "https://api-m.paypal.com" if mode == "live" else "https://api-m.sandbox.paypal.com"
    return client_id, secret, base_url


async def _get_paypal_token():
    client_id, secret, base_url = await _get_paypal_credentials()
    if not client_id or not secret:
        raise HTTPException(status_code=500, detail="PayPal not configured")
    credentials = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/v1/oauth2/token",
            headers={"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"},
            data="grant_type=client_credentials",
            timeout=15,
        )
        if resp.status_code != 200:
            logger.error(f"PayPal auth failed: {resp.text}")
            raise HTTPException(status_code=502, detail="PayPal authentication failed")
        return resp.json()["access_token"], base_url


TOPUP_PACKAGES = {"small": 5, "medium": 10, "large": 25, "xl": 50, "xxl": 100}


class PayPalOrderRequest(BaseModel):
    package_id: str
    origin_url: str


@router.post("/paypal/create-order")
async def create_paypal_order(data: PayPalOrderRequest, current_user: dict = Depends(get_current_user)):
    """Create a PayPal order for wallet top-up"""
    if data.package_id not in TOPUP_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")

    amount = TOPUP_PACKAGES[data.package_id]
    token, base_url = await _get_paypal_token()
    origin = data.origin_url.rstrip("/")

    order_body = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {"currency_code": "USD", "value": f"{amount:.2f}"},
            "description": f"Semantic Vision Wallet Top-Up (${amount})",
        }],
        "application_context": {
            "return_url": f"{origin}/portal?paypal=success",
            "cancel_url": f"{origin}/portal?paypal=cancelled",
            "brand_name": "Semantic Vision",
            "user_action": "PAY_NOW",
        },
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/v2/checkout/orders",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=order_body,
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            logger.error(f"PayPal create order failed: {resp.text}")
            raise HTTPException(status_code=502, detail="Failed to create PayPal order")
        order = resp.json()

    # Store transaction
    txn = PaymentTransaction(
        user_id=current_user["id"],
        session_id=order["id"],
        amount=amount,
        currency="usd",
        payment_status="pending",
        status="initiated",
        metadata={"user_id": current_user["id"], "package_id": data.package_id, "type": "wallet_topup", "provider": "paypal"},
    )
    await db.payment_transactions.insert_one(txn.model_dump())

    return {"order_id": order["id"], "status": order["status"]}


@router.post("/paypal/capture-order/{order_id}")
async def capture_paypal_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """Capture an approved PayPal order and credit wallet"""
    token, base_url = await _get_paypal_token()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/v2/checkout/orders/{order_id}/capture",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            logger.error(f"PayPal capture failed: {resp.text}")
            raise HTTPException(status_code=502, detail="Failed to capture PayPal payment")
        capture = resp.json()

    if capture.get("status") != "COMPLETED":
        return {"status": capture.get("status"), "message": "Payment not completed"}

    # Idempotent credit
    txn = await db.payment_transactions.find_one({"session_id": order_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if txn.get("payment_status") == "paid":
        return {"status": "already_credited", "amount": txn["amount"]}

    amount = txn["amount"]
    user_id = txn["user_id"]
    now_iso = datetime.now(timezone.utc).isoformat()

    await db.payment_transactions.update_one(
        {"session_id": order_id},
        {"$set": {"payment_status": "paid", "status": "completed", "updated_date": now_iso}},
    )

    user = await db.users.find_one({"id": user_id}, {"_id": 0, "wallet_balance": 1})
    old_balance = user.get("wallet_balance", 0.0) if user else 0.0
    new_balance = round(old_balance + amount, 2)

    await db.users.update_one({"id": user_id}, {"$set": {"wallet_balance": new_balance}})

    wallet_txn = WalletTransaction(
        user_id=user_id,
        type=WalletTransactionType.CREDIT,
        amount=amount,
        description=f"Wallet top-up via PayPal (${amount:.2f})",
        reference_id=order_id,
        balance_after=new_balance,
    )
    await db.wallet_transactions.insert_one(wallet_txn.model_dump())

    return {"status": "completed", "amount": amount, "new_balance": new_balance}


@router.get("/paypal/config")
async def get_paypal_config():
    """Return PayPal client ID for frontend (safe to expose)"""
    config = await db.system_config.find_one({"key": "integration_keys"}, {"_id": 0})
    stored = config.get("value", {}) if config else {}
    client_id = stored.get("paypal_client_id") or os.environ.get("PAYPAL_CLIENT_ID", "")
    enabled = stored.get("paypal_enabled", bool(client_id))
    return {"client_id": client_id, "enabled": enabled and bool(client_id)}
