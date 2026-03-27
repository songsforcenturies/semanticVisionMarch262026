"""Admin routes: costs, delegation, users, plans, stats, wallet admin, coupons, billing, features, referrals, donations, currency."""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional, List, Any, Dict
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import uuid, os, json as json_lib, random, string

from database import db, logger
from services import send_email
from models import (
    UserRole, SystemConfig,
    WalletTransaction, WalletTransactionType,
    Coupon, CouponType, CouponRedemption,
    AdminSubscriptionPlan, Subscription, SubscriptionPlan, SubscriptionStatus, SubscriptionFeatures,
    Referral, Donation, generate_referral_code,
    Brand, PaymentTransaction,
    WordBank, WordBankCreate,
)
from auth import get_current_user, get_current_admin, get_current_guardian
from story_service import story_service
import stripe

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

router = APIRouter()


async def _get_stripe_key():
    """Get Stripe API key from DB first, then env fallback"""
    config = await db.system_config.find_one({"key": "integration_keys"}, {"_id": 0})
    stored = config.get("value", {}) if config else {}
    key = stored.get("stripe_api_key") or os.environ.get("STRIPE_API_KEY", "")
    return key

class PurchaseRequest(BaseModel):
    guardian_id: str
    bank_id: str


# ==================== ADMIN ROUTES ====================

@router.get("/admin/costs")
async def get_admin_costs(current_user: dict = Depends(get_current_user)):
    """Get cost tracking data for admin — includes per-user, per-family, per-model breakdowns"""
    if current_user.get("role") not in ["admin", "guardian", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    cost_logs = await db.cost_logs.find({}, {"_id": 0}).sort("created_date", -1).to_list(2000)

    # Aggregate by user
    user_costs = {}
    model_costs = {}
    total_cost = 0
    for log in cost_logs:
        uid = log.get("user_id", "unknown")
        model = log.get("model", "unknown")
        cost = log.get("estimated_cost", 0)
        total_cost += cost

        if uid not in user_costs:
            user_costs[uid] = {"user_id": uid, "user_name": log.get("user_name", "Unknown"), "total_cost": 0, "story_count": 0}
        user_costs[uid]["total_cost"] += cost
        user_costs[uid]["story_count"] += 1

        if model not in model_costs:
            model_costs[model] = {"model": model, "total_cost": 0, "usage_count": 0}
        model_costs[model]["total_cost"] += cost
        model_costs[model]["usage_count"] += 1

    # Family-level aggregation: group users by guardian_id
    family_data = {}
    all_users = await db.users.find({}, {"_id": 0, "id": 1, "full_name": 1, "email": 1}).to_list(5000)
    user_lookup = {u["id"]: u for u in all_users}
    all_students = await db.students.find({}, {"_id": 0, "guardian_id": 1, "full_name": 1}).to_list(5000)
    guardian_students = {}
    for s in all_students:
        gid = s.get("guardian_id", "")
        if gid not in guardian_students:
            guardian_students[gid] = []
        guardian_students[gid].append(s.get("full_name", ""))

    # Get payment/revenue per user
    all_payments = await db.payment_transactions.find(
        {"payment_status": "paid"}, {"_id": 0, "user_id": 1, "amount": 1}
    ).to_list(5000)
    user_revenue = {}
    total_revenue = 0
    for p in all_payments:
        uid = p.get("user_id", "")
        amt = p.get("amount", 0)
        user_revenue[uid] = user_revenue.get(uid, 0) + amt
        total_revenue += amt

    # Build family breakdown
    for uid, udata in user_costs.items():
        guardian_info = user_lookup.get(uid, {})
        family_name = guardian_info.get("full_name", udata["user_name"])
        family_email = guardian_info.get("email", "")
        students = guardian_students.get(uid, [])
        revenue = user_revenue.get(uid, 0)
        expense = round(udata["total_cost"], 4)
        roi = round(((revenue - expense) / expense) * 100, 1) if expense > 0 else 0

        family_data[uid] = {
            "family_name": family_name,
            "email": family_email,
            "students": students,
            "student_count": len(students),
            "total_expense": expense,
            "gross_income": round(revenue, 2),
            "net_income": round(revenue - expense, 2),
            "roi_percent": roi,
            "story_count": udata["story_count"],
        }

    return {
        "total_cost": round(total_cost, 4),
        "total_revenue": round(total_revenue, 2),
        "total_net": round(total_revenue - total_cost, 2),
        "total_roi": round(((total_revenue - total_cost) / total_cost) * 100, 1) if total_cost > 0 else 0,
        "total_stories": len(cost_logs),
        "per_user": sorted(user_costs.values(), key=lambda x: x["total_cost"], reverse=True),
        "per_model": sorted(model_costs.values(), key=lambda x: x["total_cost"], reverse=True),
        "per_family": sorted(family_data.values(), key=lambda x: x["total_expense"], reverse=True),
        "recent_logs": cost_logs[:50],
    }


@router.get("/admin/models")
async def get_available_models(current_user: dict = Depends(get_current_user)):
    """Get list of configured LLM models"""
    config = await db.system_config.find_one({"key": "llm_config"}, {"_id": 0})
    default_config = {
        "provider": "openrouter",
        "model": "openai/gpt-4o-mini",
        "fallback_provider": None,
        "fallback_model": None,
        "openrouter_key": None,
    }
    return config.get("value", default_config) if config else default_config


class LLMConfigUpdate(BaseModel):
    provider: str  # "openrouter"
    model: str
    openrouter_key: Optional[str] = None


@router.post("/admin/models")
async def update_llm_config(
    data: LLMConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update LLM configuration (admin only)"""
    if current_user.get("role") not in ["admin", "guardian", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    config = {
        "provider": data.provider,
        "model": data.model,
        "openrouter_key": data.openrouter_key,
    }
    await db.system_config.update_one(
        {"key": "llm_config"},
        {"$set": {"key": "llm_config", "value": config, "updated_date": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "LLM config updated", "config": config}


# ==================== WALLET & PAYMENT ROUTES ====================

TOPUP_PACKAGES = {
    "small": 5.00,
    "medium": 10.00,
    "large": 25.00,
    "xl": 50.00,
    "xxl": 100.00,
}


@router.get("/wallet/balance")
async def get_wallet_balance(current_user: dict = Depends(get_current_user)):
    """Get user's wallet balance"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "wallet_balance": 1})
    balance = user.get("wallet_balance", 0.0) if user else 0.0
    return {"balance": round(balance, 2)}


@router.get("/wallet/transactions")
async def get_wallet_transactions(current_user: dict = Depends(get_current_user)):
    """Get wallet transaction history"""
    transactions = await db.wallet_transactions.find(
        {"user_id": current_user["id"]}, {"_id": 0}
    ).sort("created_date", -1).to_list(100)
    return transactions


@router.get("/wallet/packages")
async def get_topup_packages():
    """Get available top-up packages"""
    return [{"id": k, "amount": v} for k, v in TOPUP_PACKAGES.items()]


class TopupRequest(BaseModel):
    package_id: str
    origin_url: str


@router.post("/wallet/topup")
async def create_wallet_topup(data: TopupRequest, request: Request, current_user: dict = Depends(get_current_user)):
    """Create a Stripe checkout session for wallet top-up"""
    if data.package_id not in TOPUP_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")

    amount = TOPUP_PACKAGES[data.package_id]
    origin = data.origin_url.rstrip("/")

    stripe_key = await _get_stripe_key()
    if not stripe_key:
        raise HTTPException(status_code=500, detail="Payment system not configured")

    from stripe_utils import StripeCheckout, CheckoutSessionRequest

    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_key, webhook_url=webhook_url)

    success_url = f"{origin}/portal?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin}/portal?payment=cancelled"

    metadata = {
        "user_id": current_user["id"],
        "package_id": data.package_id,
        "type": "wallet_topup",
    }

    checkout_req = CheckoutSessionRequest(
        amount=amount,
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata,
        payment_methods=["card"],
    )
    session = await stripe_checkout.create_checkout_session(checkout_req)

    # Create payment transaction record
    txn = PaymentTransaction(
        user_id=current_user["id"],
        session_id=session.session_id,
        amount=amount,
        currency="usd",
        payment_status="pending",
        status="initiated",
        metadata=metadata,
    )
    await db.payment_transactions.insert_one(txn.model_dump())

    return {"url": session.url, "session_id": session.session_id}


@router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    """Check payment status and credit wallet if paid"""
    txn = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Payment not found")

    if txn.get("payment_status") == "paid":
        return {"status": txn["status"], "payment_status": "paid", "amount": txn["amount"]}

    stripe_key = await _get_stripe_key()
    from stripe_utils import StripeCheckout

    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_key, webhook_url=webhook_url)

    checkout_status = await stripe_checkout.get_checkout_status(session_id)
    now_iso = datetime.now(timezone.utc).isoformat()

    if checkout_status.payment_status == "paid" and txn.get("payment_status") != "paid":
        # Credit wallet — idempotent check on session_id
        already_credited = await db.payment_transactions.find_one(
            {"session_id": session_id, "payment_status": "paid"}
        )
        if not already_credited:
            amount = txn["amount"]
            user_id = txn["user_id"]

            # Update payment transaction
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": "paid", "status": "completed", "updated_date": now_iso}}
            )

            # Credit wallet
            user = await db.users.find_one({"id": user_id}, {"_id": 0, "wallet_balance": 1})
            old_balance = user.get("wallet_balance", 0.0) if user else 0.0
            new_balance = round(old_balance + amount, 2)

            await db.users.update_one(
                {"id": user_id},
                {"$set": {"wallet_balance": new_balance}}
            )

            # Create wallet transaction
            wallet_txn = WalletTransaction(
                user_id=user_id,
                type=WalletTransactionType.CREDIT,
                amount=amount,
                description=f"Wallet top-up (${amount:.2f})",
                reference_id=session_id,
                balance_after=new_balance,
            )
            await db.wallet_transactions.insert_one(wallet_txn.model_dump())

        return {"status": "completed", "payment_status": "paid", "amount": txn["amount"]}

    elif checkout_status.status == "expired":
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": "expired", "status": "expired", "updated_date": now_iso}}
        )
        return {"status": "expired", "payment_status": "expired", "amount": txn["amount"]}

    return {"status": txn.get("status", "initiated"), "payment_status": checkout_status.payment_status, "amount": txn["amount"]}


# ==================== STRIPE WEBHOOK ====================

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    body = await request.body()
    sig = request.headers.get("Stripe-Signature")
    stripe_key = await _get_stripe_key()

    try:
        from stripe_utils import StripeCheckout
        host_url = str(request.base_url).rstrip("/")
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_key, webhook_url=webhook_url)
        webhook_response = await stripe_checkout.handle_webhook(body, sig)

        if webhook_response.payment_status == "paid":
            session_id = webhook_response.session_id
            txn = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
            if txn and txn.get("payment_status") != "paid":
                amount = txn["amount"]
                user_id = txn["user_id"]
                now_iso = datetime.now(timezone.utc).isoformat()

                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": {"payment_status": "paid", "status": "completed", "updated_date": now_iso}}
                )

                user = await db.users.find_one({"id": user_id}, {"_id": 0, "wallet_balance": 1})
                old_balance = user.get("wallet_balance", 0.0) if user else 0.0
                new_balance = round(old_balance + amount, 2)

                await db.users.update_one(
                    {"id": user_id},
                    {"$set": {"wallet_balance": new_balance}}
                )

                wallet_txn = WalletTransaction(
                    user_id=user_id,
                    type=WalletTransactionType.CREDIT,
                    amount=amount,
                    description=f"Wallet top-up (${amount:.2f})",
                    reference_id=session_id,
                    balance_after=new_balance,
                )
                await db.wallet_transactions.insert_one(wallet_txn.model_dump())

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "error", "detail": str(e)}


# ==================== WALLET PURCHASE (WORD BANK) ====================

@router.post("/wallet/purchase-bank")
async def purchase_bank_with_wallet(
    request_data: PurchaseRequest,
    current_user: dict = Depends(get_current_guardian)
):
    """Purchase a word bank using wallet balance"""
    bank = await db.word_banks.find_one({"id": request_data.bank_id})
    if not bank:
        raise HTTPException(status_code=404, detail="Word bank not found")

    price_dollars = bank.get("price", 0) / 100.0  # price stored in cents

    if price_dollars > 0:
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "wallet_balance": 1})
        balance = user.get("wallet_balance", 0.0) if user else 0.0

        if balance < price_dollars:
            raise HTTPException(status_code=400, detail=f"Insufficient balance. Need ${price_dollars:.2f}, have ${balance:.2f}")

        # Debit wallet
        new_balance = round(balance - price_dollars, 2)
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": {"wallet_balance": new_balance}}
        )

        wallet_txn = WalletTransaction(
            user_id=current_user["id"],
            type=WalletTransactionType.DEBIT,
            amount=price_dollars,
            description=f"Purchased: {bank['name']}",
            reference_id=request_data.bank_id,
            balance_after=new_balance,
        )
        await db.wallet_transactions.insert_one(wallet_txn.model_dump())

    # Add to subscription
    subscription = await db.subscriptions.find_one({"guardian_id": request_data.guardian_id})
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if request_data.bank_id in subscription.get("bank_access", []):
        raise HTTPException(status_code=400, detail="Word bank already purchased")

    await db.subscriptions.update_one(
        {"guardian_id": request_data.guardian_id},
        {"$push": {"bank_access": request_data.bank_id}}
    )
    await db.word_banks.update_one(
        {"id": request_data.bank_id},
        {"$inc": {"purchase_count": 1}}
    )

    return {"message": "Word bank purchased", "bank_id": request_data.bank_id, "new_balance": new_balance if price_dollars > 0 else None}


# ==================== COUPON ROUTES ====================

class CouponCreate(BaseModel):
    code: str
    coupon_type: CouponType
    value: float
    max_uses: int = 1
    expires_at: Optional[str] = None
    description: str = ""


@router.post("/admin/coupons")
async def create_coupon(data: CouponCreate, current_user: dict = Depends(get_current_user)):
    """Create a digital coupon (admin only)"""
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

    existing = await db.coupons.find_one({"code": data.code.upper()})
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")

    coupon = Coupon(
        code=data.code.upper(),
        coupon_type=data.coupon_type,
        value=data.value,
        max_uses=data.max_uses,
        expires_at=datetime.fromisoformat(data.expires_at) if data.expires_at else None,
        created_by=current_user["id"],
        description=data.description,
    )
    await db.coupons.insert_one(coupon.model_dump())
    result = coupon.model_dump()
    return result


@router.get("/admin/coupons")
async def list_coupons(current_user: dict = Depends(get_current_user)):
    """List all coupons"""
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

    coupons = await db.coupons.find({}, {"_id": 0}).sort("created_date", -1).to_list(200)
    return coupons


@router.delete("/admin/coupons/{coupon_id}")
async def delete_coupon(coupon_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a coupon"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.coupons.delete_one({"id": coupon_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return {"message": "Coupon deleted"}


@router.get("/admin/coupons/stats")
async def get_coupon_stats(current_user: dict = Depends(get_current_user)):
    """Get comprehensive coupon value tracking stats"""
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

    # Get all coupons
    all_coupons = await db.coupons.find({}, {"_id": 0}).to_list(5000)
    total_coupons_created = len(all_coupons)
    total_coupons_active = len([c for c in all_coupons if c.get("is_active", False)])

    # Get all redemptions
    all_redemptions = await db.coupon_redemptions.find({}, {"_id": 0}).to_list(10000)
    total_redemptions = len(all_redemptions)

    # Get all users for name/email lookup
    all_users = await db.users.find({}, {"_id": 0, "id": 1, "email": 1, "full_name": 1}).to_list(10000)
    user_lookup = {u["id"]: u for u in all_users}

    # Aggregate by type
    by_type = {}
    for r in all_redemptions:
        ct = r.get("coupon_type", "unknown")
        if ct not in by_type:
            by_type[ct] = {"count": 0, "total_value": 0.0}
        by_type[ct]["count"] += 1
        by_type[ct]["total_value"] += r.get("value", 0)

    # Total value given out (sum of all redemption values, grouped by type)
    total_value_given_out = {}
    for ct, data in by_type.items():
        total_value_given_out[ct] = data["total_value"]

    # Aggregate by user
    user_redemptions_map: Dict[str, list] = {}
    for r in all_redemptions:
        uid = r.get("user_id", "unknown")
        if uid not in user_redemptions_map:
            user_redemptions_map[uid] = []
        user_redemptions_map[uid].append(r)

    by_user = []
    for uid, redemptions in user_redemptions_map.items():
        user_info = user_lookup.get(uid, {})
        total_value = sum(r.get("value", 0) for r in redemptions)
        by_user.append({
            "user_id": uid,
            "user_email": user_info.get("email", ""),
            "user_name": user_info.get("full_name", ""),
            "total_redeemed": len(redemptions),
            "total_value": total_value,
            "redemptions": [
                {
                    "coupon_code": r.get("coupon_code", ""),
                    "value": r.get("value", 0),
                    "type": r.get("coupon_type", ""),
                    "date": str(r.get("created_date", "")),
                }
                for r in redemptions
            ],
        })

    return {
        "total_coupons_created": total_coupons_created,
        "total_coupons_active": total_coupons_active,
        "total_value_given_out": total_value_given_out,
        "total_redemptions": total_redemptions,
        "by_user": by_user,
        "by_type": by_type,
    }


class RedeemCouponRequest(BaseModel):
    code: str


@router.post("/coupons/redeem")
async def redeem_coupon(data: RedeemCouponRequest, current_user: dict = Depends(get_current_user)):
    """Redeem a coupon code"""
    code = data.code.strip().upper()
    coupon = await db.coupons.find_one({"code": code, "is_active": True}, {"_id": 0})
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid or expired coupon code")

    # Check expiration
    if coupon.get("expires_at"):
        exp = coupon["expires_at"]
        if isinstance(exp, str):
            exp = datetime.fromisoformat(exp)
        if exp < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Coupon has expired")

    # Check usage limit (0 = unlimited)
    if coupon["max_uses"] > 0 and coupon["uses_count"] >= coupon["max_uses"]:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")

    # Check if user already redeemed
    existing = await db.coupon_redemptions.find_one(
        {"coupon_id": coupon["id"], "user_id": current_user["id"]}
    )
    if existing:
        raise HTTPException(status_code=400, detail="You have already redeemed this coupon")

    coupon_type = coupon["coupon_type"]
    value = coupon["value"]

    # Apply coupon based on type
    if coupon_type == "wallet_credit":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "wallet_balance": 1})
        old_balance = user.get("wallet_balance", 0.0) if user else 0.0
        new_balance = round(old_balance + value, 2)
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": {"wallet_balance": new_balance}}
        )
        wallet_txn = WalletTransaction(
            user_id=current_user["id"],
            type=WalletTransactionType.COUPON,
            amount=value,
            description=f"Coupon: {code} (+${value:.2f})",
            reference_id=coupon["id"],
            balance_after=new_balance,
        )
        await db.wallet_transactions.insert_one(wallet_txn.model_dump())
        message = f"${value:.2f} added to your wallet!"

    elif coupon_type == "free_stories":
        # Add bonus stories to subscription
        sub = await db.subscriptions.find_one({"guardian_id": current_user["id"]})
        if sub:
            bonus = sub.get("bonus_stories", 0) + int(value)
            await db.subscriptions.update_one(
                {"guardian_id": current_user["id"]},
                {"$set": {"bonus_stories": bonus}}
            )
        message = f"{int(value)} free stories added!"

    elif coupon_type == "free_students":
        sub = await db.subscriptions.find_one({"guardian_id": current_user["id"]})
        if sub:
            seats = sub.get("student_seats", 10) + int(value)
            await db.subscriptions.update_one(
                {"guardian_id": current_user["id"]},
                {"$set": {"student_seats": seats}}
            )
        message = f"{int(value)} additional student seats added!"

    elif coupon_type == "free_days":
        sub = await db.subscriptions.find_one({"guardian_id": current_user["id"]})
        if sub:
            from datetime import timedelta
            trial_end = datetime.now(timezone.utc) + timedelta(days=int(value))
            await db.subscriptions.update_one(
                {"guardian_id": current_user["id"]},
                {"$set": {"plan": "starter", "status": "active", "trial_ends": trial_end.isoformat()}}
            )
        message = f"{int(value)} free days of premium access activated!"

    elif coupon_type == "percentage_discount":
        # Store the discount percentage for the user's next applicable purchase
        discount_pct = min(value, 100)
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": {"active_discount": {"percentage": discount_pct, "coupon_code": code, "coupon_id": coupon["id"]}}}
        )
        if discount_pct >= 100:
            message = f"100% discount applied! Your next purchase is free."
        else:
            message = f"{int(discount_pct)}% discount applied to your account!"

    else:
        raise HTTPException(status_code=400, detail="Unknown coupon type")

    # Record redemption
    redemption = CouponRedemption(
        coupon_id=coupon["id"],
        coupon_code=code,
        user_id=current_user["id"],
        coupon_type=coupon_type,
        value=value,
    )
    await db.coupon_redemptions.insert_one(redemption.model_dump())

    # Increment usage
    await db.coupons.update_one({"id": coupon["id"]}, {"$inc": {"uses_count": 1}})

    return {"message": message, "coupon_type": coupon_type, "value": value}



# ==================== BRAND COUPON MANAGEMENT ====================

def get_current_brand_partner(current_user: dict = Depends(get_current_user)):
    """Verify user is an approved brand partner"""
    if current_user.get("role") != "brand_partner":
        raise HTTPException(status_code=403, detail="Brand partner access required")
    return current_user


class BrandCouponCreate(BaseModel):
    code: str
    coupon_type: str = "percentage_discount"
    value: float  # percentage (0-100)
    expires_at: Optional[str] = None
    description: str = ""


@router.get("/brand-portal/coupons")
async def list_brand_coupons(current_user: dict = Depends(get_current_brand_partner)):
    """List coupons created by this brand"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id", "")
    coupons = await db.coupons.find(
        {"created_by_brand_id": brand_id}, {"_id": 0}
    ).sort("created_date", -1).to_list(100)
    return coupons


@router.post("/brand-portal/coupons")
async def create_brand_coupon(data: BrandCouponCreate, current_user: dict = Depends(get_current_brand_partner)):
    """Brand creates a discount coupon"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id", "")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")

    if data.value < 0 or data.value > 100:
        raise HTTPException(status_code=400, detail="Discount must be between 0 and 100 percent")

    existing = await db.coupons.find_one({"code": data.code.upper()})
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")

    coupon = Coupon(
        code=data.code.upper(),
        coupon_type=CouponType.PERCENTAGE_DISCOUNT,
        value=data.value,
        max_uses=0,  # unlimited
        expires_at=datetime.fromisoformat(data.expires_at) if data.expires_at else None,
        created_by=current_user["id"],
        created_by_brand_id=brand_id,
        description=data.description,
    )
    await db.coupons.insert_one(coupon.model_dump())
    result = coupon.model_dump()
    return result


@router.delete("/brand-portal/coupons/{coupon_id}")
async def delete_brand_coupon(coupon_id: str, current_user: dict = Depends(get_current_brand_partner)):
    """Brand deletes one of their coupons"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id", "")
    result = await db.coupons.delete_one({"id": coupon_id, "created_by_brand_id": brand_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Coupon not found or not yours")
    return {"message": "Coupon deleted"}


# ==================== ADMIN: ADD CREDITS TO ANY USER ====================

class AdminAddCredits(BaseModel):
    user_id: str
    amount: float
    description: str = ""


@router.post("/admin/users/{user_id}/add-credits")
async def admin_add_credits(user_id: str, data: AdminAddCredits, current_user: dict = Depends(get_current_user)):
    """Admin adds wallet credits to any user account"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_balance = user.get("wallet_balance", 0.0)
    new_balance = round(old_balance + data.amount, 2)

    await db.users.update_one({"id": user_id}, {"$set": {"wallet_balance": new_balance}})

    # Record transaction
    txn = WalletTransaction(
        user_id=user_id,
        type=WalletTransactionType.COUPON,
        amount=data.amount,
        description=data.description or f"Admin credit: +${data.amount:.2f}",
        reference_id=f"admin_{current_user['id']}",
        balance_after=new_balance,
    )
    await db.wallet_transactions.insert_one(txn.model_dump())

    return {
        "message": f"${data.amount:.2f} added to {user['full_name']} wallet",
        "new_balance": new_balance,
    }


# ==================== ADMIN DELEGATION ROUTES ====================

class DelegateRequest(BaseModel):
    email: str
    is_delegated: bool = True


@router.post("/admin/delegate")
async def delegate_admin(data: DelegateRequest, current_user: dict = Depends(get_current_user)):
    """Delegate or revoke admin privileges for a user"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Master admin access required")

    target_user = await db.users.find_one({"email": data.email})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.users.update_one(
        {"email": data.email},
        {"$set": {"is_delegated_admin": data.is_delegated}}
    )
    action = "granted" if data.is_delegated else "revoked"
    return {"message": f"Delegated admin {action} for {data.email}"}


@router.get("/admin/users")
async def list_all_users(
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """List all users (admin only) — supports search by name or email"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    query = {}
    if search and search.strip():
        s = search.strip()
        query = {"$or": [
            {"email": {"$regex": s, "$options": "i"}},
            {"full_name": {"$regex": s, "$options": "i"}},
        ]}

    users = await db.users.find(
        query, {"_id": 0, "password_hash": 0}
    ).sort("created_date", -1).to_list(500)
    return users


@router.get("/admin/plan-stats")
async def get_plan_stats(current_user: dict = Depends(get_current_user)):
    """Get count of users per subscription plan (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    pipeline = [
        {"$group": {"_id": "$plan", "count": {"$sum": 1}, "total_seats": {"$sum": "$student_seats"}, "active_students": {"$sum": "$active_students"}}},
        {"$sort": {"count": -1}},
    ]
    stats = await db.subscriptions.aggregate(pipeline).to_list(50)
    total_guardians = await db.users.count_documents({"role": "guardian"})
    total_with_sub = await db.subscriptions.count_documents({})

    return {
        "plan_breakdown": [{"plan": s["_id"], "users": s["count"], "total_seats": s["total_seats"], "active_students": s["active_students"]} for s in stats],
        "total_guardians": total_guardians,
        "total_with_subscription": total_with_sub,
        "total_without_subscription": total_guardians - total_with_sub,
    }


class AdminEditUserSubscription(BaseModel):
    plan_name: Optional[str] = None
    student_seats: Optional[int] = None
    status: Optional[str] = None


@router.put("/admin/users/{user_id}/subscription")
async def admin_edit_user_subscription(user_id: str, data: AdminEditUserSubscription, current_user: dict = Depends(get_current_user)):
    """Admin directly edits a user's subscription (seats, plan, status)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    sub = await db.subscriptions.find_one({"guardian_id": user_id})
    if not sub:
        # Auto-create
        active_students = await db.students.count_documents({"guardian_id": user_id})
        new_sub = Subscription(guardian_id=user_id, plan=SubscriptionPlan.FREE, student_seats=10, active_students=active_students)
        await db.subscriptions.insert_one(new_sub.model_dump())

    update = {}
    if data.plan_name is not None:
        update["plan"] = data.plan_name.lower().replace(" ", "_")
    if data.student_seats is not None:
        update["student_seats"] = data.student_seats
    if data.status is not None:
        update["status"] = data.status

    if not update:
        raise HTTPException(status_code=400, detail="No fields to update")

    await db.subscriptions.update_one({"guardian_id": user_id}, {"$set": update})
    updated = await db.subscriptions.find_one({"guardian_id": user_id}, {"_id": 0})
    return updated


class AdminEditUserWallet(BaseModel):
    wallet_balance: float
    description: str = "Admin wallet adjustment"


@router.put("/admin/users/{user_id}/wallet")
async def admin_edit_user_wallet(user_id: str, data: AdminEditUserWallet, current_user: dict = Depends(get_current_user)):
    """Admin directly sets a user's wallet balance"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    user = await db.users.find_one({"id": user_id}, {"_id": 0, "wallet_balance": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_balance = user.get("wallet_balance", 0.0)
    new_balance = round(data.wallet_balance, 2)
    await db.users.update_one({"id": user_id}, {"$set": {"wallet_balance": new_balance}})

    diff = round(new_balance - old_balance, 2)
    txn_type = WalletTransactionType.CREDIT if diff >= 0 else WalletTransactionType.DEBIT
    await db.wallet_transactions.insert_one(WalletTransaction(
        user_id=user_id, type=txn_type, amount=abs(diff),
        description=data.description, reference_id="admin-adjustment",
        balance_after=new_balance,
    ).model_dump())

    return {"message": f"Wallet updated to ${new_balance:.2f}", "new_balance": new_balance}



# ==================== ADMIN USER MANAGEMENT ====================

class AdminCreateUser(BaseModel):
    email: str
    full_name: str
    role: str  # guardian, teacher, brand_partner


class AdminUpdateUser(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    brand_approved: Optional[bool] = None


@router.post("/admin/users")
async def admin_create_user(data: AdminCreateUser, current_user: dict = Depends(get_current_user)):
    """Admin creates a new user with a temp password"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    if data.role not in ["guardian", "teacher", "brand_partner"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be: guardian, teacher, or brand_partner")

    existing = await db.users.find_one({"email": data.email.lower().strip()})
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists")

    import secrets
    import uuid as _uuid2
    temp_password = secrets.token_urlsafe(8)

    user_doc = {
        "id": str(_uuid2.uuid4()),
        "email": data.email.lower().strip(),
        "full_name": data.full_name.strip(),
        "role": data.role,
        "password_hash": get_password_hash(temp_password),
        "wallet_balance": 0.0,
        "is_active": True,
        "is_delegated_admin": False,
        "brand_approved": True if data.role == "brand_partner" else False,
        "referral_code": str(_uuid2.uuid4())[:8].upper(),
        "created_date": datetime.now(timezone.utc).isoformat(),
        "must_change_password": True,
    }
    await db.users.insert_one(user_doc)

    if data.role == "brand_partner":
        new_brand = Brand(name=data.full_name.strip(), created_by=user_doc["id"])
        await db.brands.insert_one(new_brand.model_dump())
        await db.users.update_one({"id": user_doc["id"]}, {"$set": {"linked_brand_id": new_brand.id}})

    return {
        "message": "User created successfully",
        "user_id": user_doc["id"],
        "email": user_doc["email"],
        "temp_password": temp_password,
        "role": data.role,
    }


@router.put("/admin/users/{user_id}")
async def admin_update_user(user_id: str, data: AdminUpdateUser, current_user: dict = Depends(get_current_user)):
    """Admin edits user profile"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update = {}
    if data.email is not None:
        existing = await db.users.find_one({"email": data.email.lower().strip(), "id": {"$ne": user_id}})
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        update["email"] = data.email.lower().strip()
    if data.full_name is not None:
        update["full_name"] = data.full_name.strip()
    if data.role is not None and data.role in ["guardian", "teacher", "brand_partner", "admin"]:
        update["role"] = data.role
    if data.is_active is not None:
        update["is_active"] = data.is_active
    if data.brand_approved is not None:
        update["brand_approved"] = data.brand_approved

    if not update:
        raise HTTPException(status_code=400, detail="No fields to update")

    await db.users.update_one({"id": user_id}, {"$set": update})
    return {"message": "User updated"}


@router.post("/admin/users/{user_id}/reset-password")
async def admin_reset_password(user_id: str, current_user: dict = Depends(get_current_user)):
    """Admin resets user password to a new temp password"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    import secrets
    temp_password = secrets.token_urlsafe(8)
    await db.users.update_one({"id": user_id}, {"$set": {
        "password_hash": get_password_hash(temp_password),
        "must_change_password": True,
    }})
    return {"message": "Password reset", "temp_password": temp_password, "email": user["email"]}


@router.post("/admin/users/{user_id}/deactivate")
async def admin_deactivate_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Admin deactivates or reactivates a user account"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Cannot deactivate an admin account")

    is_active = user.get("is_active", True)
    await db.users.update_one({"id": user_id}, {"$set": {"is_active": not is_active}})
    return {"message": f"User {'deactivated' if is_active else 'reactivated'}", "is_active": not is_active}


@router.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Admin deletes a user account permanently"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete an admin account")

    if user.get("linked_brand_id"):
        await db.brands.delete_one({"id": user["linked_brand_id"]})

    await db.users.delete_one({"id": user_id})
    return {"message": "User deleted permanently"}



# ==================== ADMIN SUBSCRIPTION PLANS ====================

class PlanCreate(BaseModel):
    name: str
    description: str = ""
    price_monthly: float = 0.0
    student_seats: int = 10
    story_limit: int = -1
    features: dict = {}


@router.post("/admin/plans")
async def create_plan(data: PlanCreate, current_user: dict = Depends(get_current_user)):
    """Create a subscription plan (admin/delegated)"""
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

    plan = AdminSubscriptionPlan(
        name=data.name,
        description=data.description,
        price_monthly=data.price_monthly,
        student_seats=data.student_seats,
        story_limit=data.story_limit,
        features=data.features,
        created_by=current_user["id"],
    )
    await db.subscription_plans.insert_one(plan.model_dump())
    result = plan.model_dump()
    return result


@router.get("/admin/plans")
async def list_plans(current_user: dict = Depends(get_current_user)):
    """List subscription plans"""
    plans = await db.subscription_plans.find({}, {"_id": 0}).sort("created_date", -1).to_list(50)
    return plans


@router.delete("/admin/plans/{plan_id}")
async def delete_plan(plan_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a subscription plan"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.subscription_plans.delete_one({"id": plan_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan deleted"}


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[float] = None
    student_seats: Optional[int] = None
    story_limit: Optional[int] = None
    features: Optional[dict] = None
    is_active: Optional[bool] = None


@router.put("/admin/plans/{plan_id}")
async def update_plan(plan_id: str, data: PlanUpdate, current_user: dict = Depends(get_current_user)):
    """Edit a subscription plan (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    update_fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.subscription_plans.update_one({"id": plan_id}, {"$set": update_fields})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")

    updated = await db.subscription_plans.find_one({"id": plan_id}, {"_id": 0})
    return updated


# ==================== SUBSCRIPTION PLANS (PUBLIC) ====================

@router.get("/subscription-plans/available")
async def get_available_plans():
    """Get all active subscription plans (for parents to choose from)"""
    plans = await db.subscription_plans.find({"is_active": True}, {"_id": 0}).sort("price_monthly", 1).to_list(50)
    return plans


# ==================== SUBSCRIPTION UPGRADE (PARENT) ====================

class SubscriptionUpgradeRequest(BaseModel):
    plan_id: str
    use_wallet: bool = True


@router.post("/subscriptions/upgrade")
async def upgrade_subscription(data: SubscriptionUpgradeRequest, current_user: dict = Depends(get_current_user)):
    """Parent upgrades their subscription to a chosen plan"""
    # Fetch the plan
    plan = await db.subscription_plans.find_one({"id": data.plan_id, "is_active": True}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found or inactive")

    # Fetch current subscription
    subscription = await db.subscriptions.find_one({"guardian_id": current_user["id"]})
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    price = plan.get("price_monthly", 0.0)

    # If plan costs money and user wants to pay with wallet
    if price > 0 and data.use_wallet:
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "wallet_balance": 1})
        balance = user.get("wallet_balance", 0.0) if user else 0.0

        # Check for active discount
        discount_info = (await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "active_discount": 1})) or {}
        discount = discount_info.get("active_discount", {})
        discount_pct = discount.get("percentage", 0)
        if discount_pct > 0:
            price = round(price * (1 - discount_pct / 100), 2)
            # Clear the discount after use
            await db.users.update_one({"id": current_user["id"]}, {"$unset": {"active_discount": ""}})

        if balance < price:
            raise HTTPException(status_code=400, detail=f"Insufficient wallet balance. Need ${price:.2f}, have ${balance:.2f}")

        new_balance = round(balance - price, 2)
        await db.users.update_one({"id": current_user["id"]}, {"$set": {"wallet_balance": new_balance}})

        txn = WalletTransaction(
            user_id=current_user["id"],
            type=WalletTransactionType.DEBIT,
            amount=price,
            description=f"Subscription upgrade: {plan['name']}",
            reference_id=plan["id"],
            balance_after=new_balance,
        )
        await db.wallet_transactions.insert_one(txn.model_dump())

    # Update subscription
    update = {
        "plan": plan.get("name", "starter").lower().replace(" ", "_"),
        "student_seats": plan.get("student_seats", 10),
        "status": "active",
        "price_monthly": int(price * 100),
        "features": SubscriptionFeatures(
            voice_mentor=plan.get("features", {}).get("voice_mentor", False),
            contracts=plan.get("features", {}).get("contracts", False),
            advanced_analytics=plan.get("features", {}).get("advanced_analytics", False),
            custom_narratives=plan.get("features", {}).get("custom_narratives", False),
        ).model_dump(),
    }
    await db.subscriptions.update_one({"guardian_id": current_user["id"]}, {"$set": update})

    return {
        "message": f"Upgraded to {plan['name']}!",
        "plan_name": plan["name"],
        "student_seats": plan.get("student_seats", 10),
        "price_paid": price,
    }


# ==================== ADMIN ASSIGN SUBSCRIPTION ====================

class AdminAssignSubscription(BaseModel):
    plan_id: str


@router.post("/admin/users/{user_id}/assign-subscription")
async def admin_assign_subscription(user_id: str, data: AdminAssignSubscription, current_user: dict = Depends(get_current_user)):
    """Admin assigns a subscription plan to a user"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plan = await db.subscription_plans.find_one({"id": data.plan_id}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Check if subscription exists
    subscription = await db.subscriptions.find_one({"guardian_id": user_id})

    update = {
        "plan": plan.get("name", "starter").lower().replace(" ", "_"),
        "student_seats": plan.get("student_seats", 10),
        "status": "active",
        "price_monthly": int(plan.get("price_monthly", 0) * 100),
        "features": SubscriptionFeatures(
            voice_mentor=plan.get("features", {}).get("voice_mentor", False),
            contracts=plan.get("features", {}).get("contracts", False),
            advanced_analytics=plan.get("features", {}).get("advanced_analytics", False),
            custom_narratives=plan.get("features", {}).get("custom_narratives", False),
        ).model_dump(),
    }

    if subscription:
        await db.subscriptions.update_one({"guardian_id": user_id}, {"$set": update})
    else:
        new_sub = Subscription(guardian_id=user_id, **update, active_students=0)
        await db.subscriptions.insert_one(new_sub.model_dump())

    return {"message": f"Assigned {plan['name']} plan to {user['full_name']}"}


# ==================== COMPREHENSIVE ADMIN STATISTICS ====================

@router.get("/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    """Get comprehensive platform statistics"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    # User counts
    total_guardians = await db.users.count_documents({"role": "guardian"})
    total_teachers = await db.users.count_documents({"role": "teacher"})
    total_students = await db.students.count_documents({})

    # Content stats
    total_word_banks = await db.word_banks.count_documents({})
    total_narratives = await db.narratives.count_documents({})
    total_assessments = await db.assessments.count_documents({})
    completed_assessments = await db.assessments.count_documents({"status": "completed"})

    # Reading stats
    pipeline = [{"$group": {"_id": None, "total_seconds": {"$sum": "$duration_seconds"}, "total_words": {"$sum": "$words_read"}}}]
    reading_agg = await db.read_logs.aggregate(pipeline).to_list(1)
    total_reading_seconds = reading_agg[0]["total_seconds"] if reading_agg else 0
    total_words_read = reading_agg[0]["total_words"] if reading_agg else 0

    # Payment stats
    total_revenue_pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]
    revenue_agg = await db.payment_transactions.aggregate(total_revenue_pipeline).to_list(1)
    total_revenue = revenue_agg[0]["total"] if revenue_agg else 0
    total_payments = revenue_agg[0]["count"] if revenue_agg else 0

    # Coupon stats
    total_coupons = await db.coupons.count_documents({})
    total_redemptions = await db.coupon_redemptions.count_documents({})

    # Classroom stats
    total_sessions = await db.classroom_sessions.count_documents({})
    active_sessions = await db.classroom_sessions.count_documents({"status": {"$in": ["waiting", "active"]}})

    # AI cost stats
    cost_pipeline = [{"$group": {"_id": None, "total": {"$sum": "$estimated_cost"}, "count": {"$sum": 1}}}]
    cost_agg = await db.cost_logs.aggregate(cost_pipeline).to_list(1)
    total_ai_cost = cost_agg[0]["total"] if cost_agg else 0
    total_ai_calls = cost_agg[0]["count"] if cost_agg else 0

    # Recent registrations (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc).replace(day=1)
    recent_users = await db.users.count_documents({"created_date": {"$gte": thirty_days_ago}})

    return {
        "users": {
            "guardians": total_guardians,
            "teachers": total_teachers,
            "students": total_students,
            "recent_signups": recent_users,
        },
        "content": {
            "word_banks": total_word_banks,
            "narratives": total_narratives,
            "assessments_total": total_assessments,
            "assessments_completed": completed_assessments,
        },
        "reading": {
            "total_reading_hours": round(total_reading_seconds / 3600, 1),
            "total_words_read": total_words_read,
        },
        "revenue": {
            "total_revenue": round(total_revenue, 2),
            "total_payments": total_payments,
        },
        "coupons": {
            "total_coupons": total_coupons,
            "total_redemptions": total_redemptions,
        },
        "classrooms": {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
        },
        "ai": {
            "total_cost": round(total_ai_cost, 4),
            "total_calls": total_ai_calls,
        },
    }


# ==================== ADMIN WORD BANK MANAGEMENT (DELEGATED) ====================

@router.post("/admin/word-banks")
async def admin_create_word_bank(
    bank_data: WordBankCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a word bank (admin or delegated admin)"""
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

    total_tokens = len(bank_data.baseline_words) + len(bank_data.target_words) + len(bank_data.stretch_words)
    word_bank = WordBank(
        **bank_data.model_dump(),
        owner_id=current_user["id"],
        total_tokens=total_tokens
    )
    bank_dict = word_bank.model_dump()
    await db.word_banks.insert_one(bank_dict)
    return word_bank


# ==================== WORD DEFINITION API ====================

class DefineWordRequest(BaseModel):
    word: str
    context: str = ""  # optional sentence context


@router.post("/words/define")
async def define_word(data: DefineWordRequest, current_user: dict = Depends(get_current_user)):
    """Get AI-powered definition for a word"""
    from story_service import story_service
    
    llm_config = await story_service._get_llm_config()
    model = llm_config.get("model", "openai/gpt-4o-mini")
    api_key = llm_config.get("openrouter_key") or os.environ.get("OPENROUTER_API_KEY")

    prompt = f"""Define the word "{data.word}" for a student learning vocabulary.
{f'The word appears in this context: "{data.context}"' if data.context else ''}

Return ONLY valid JSON:
{{"word": "{data.word}", "definition": "clear simple definition", "part_of_speech": "noun/verb/adj/etc", "example_sentence": "example usage", "pronunciation_hint": "how to say it", "synonyms": ["syn1", "syn2"]}}"""

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key, timeout=30.0)
        resp = await client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=500, temperature=0.3,
        )
        text = resp.choices[0].message.content or ""
        
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"): text = text[:-3]
            text = text.strip()
        
        import json
        return json.loads(text)
    except Exception as e:
        # Fallback: return basic definition
        return {
            "word": data.word,
            "definition": f"Look up '{data.word}' in a dictionary for a detailed definition.",
            "part_of_speech": "unknown",
            "example_sentence": "",
            "pronunciation_hint": data.word,
            "synonyms": [],
            "error": str(e),
        }


# ==================== REFERRAL ROUTES ====================

@router.get("/referrals/my-code")
async def get_my_referral_code(current_user: dict = Depends(get_current_user)):
    """Get current user's referral code"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "referral_code": 1})
    code = user.get("referral_code", "") if user else ""
    if not code:
        code = generate_referral_code()
        await db.users.update_one({"id": current_user["id"]}, {"$set": {"referral_code": code}})
    return {"referral_code": code}


@router.get("/referrals/my-referrals")
async def get_my_referrals(current_user: dict = Depends(get_current_user)):
    """Get list of users I've referred"""
    referrals = await db.referrals.find(
        {"referrer_id": current_user["id"]}, {"_id": 0}
    ).sort("created_date", -1).to_list(100)
    
    total_earned = 0.0
    for ref in referrals:
        referred_user = await db.users.find_one({"id": ref["referred_id"]}, {"_id": 0, "full_name": 1, "email": 1})
        if referred_user:
            ref["referred_name"] = referred_user.get("full_name", "Unknown")
        total_earned += ref.get("reward_amount", 0)
    
    return {"referrals": referrals, "total_earned": total_earned, "total_count": len(referrals)}


@router.get("/referrals/reward-amount")
async def get_referral_reward_amount():
    """Get current referral reward amount (public for display)"""
    config = await db.system_config.find_one({"key": "billing_config"}, {"_id": 0})
    reward = config.get("value", {}).get("referral_reward_amount", 5.0) if config else 5.0
    return {"referral_reward_amount": reward}


# ==================== REFERRAL CONTESTS & LEADERBOARD ====================

class ContestCreate(BaseModel):
    title: str
    description: str = ""
    prize_description: str
    prize_value: Optional[float] = None
    start_date: str  # ISO date string
    end_date: str    # ISO date string
    is_active: bool = True
    runner_up_prizes: Optional[List[Dict[str, Any]]] = None  # [{place: 2, prize: "..."}, ...]


class ContestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    prize_description: Optional[str] = None
    prize_value: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_active: Optional[bool] = None
    runner_up_prizes: Optional[List[Dict[str, Any]]] = None


@router.post("/admin/contests")
async def create_contest(data: ContestCreate, current_user: dict = Depends(get_current_admin)):
    """Create a new referral contest"""
    contest = {
        "id": str(uuid.uuid4()),
        "title": data.title,
        "description": data.description,
        "prize_description": data.prize_description,
        "prize_value": data.prize_value,
        "start_date": data.start_date,
        "end_date": data.end_date,
        "is_active": data.is_active,
        "runner_up_prizes": data.runner_up_prizes or [],
        "created_date": datetime.now(timezone.utc).isoformat(),
        "created_by": current_user["id"],
    }
    await db.referral_contests.insert_one(contest)
    contest.pop("_id", None)
    return contest


@router.get("/admin/contests")
async def list_contests(current_user: dict = Depends(get_current_admin)):
    """List all referral contests"""
    contests = await db.referral_contests.find({}, {"_id": 0}).sort("created_date", -1).to_list(50)
    return contests


@router.put("/admin/contests/{contest_id}")
async def update_contest(contest_id: str, data: ContestUpdate, current_user: dict = Depends(get_current_admin)):
    """Update a referral contest"""
    update_fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await db.referral_contests.update_one({"id": contest_id}, {"$set": update_fields})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Contest not found")
    updated = await db.referral_contests.find_one({"id": contest_id}, {"_id": 0})
    return updated


@router.delete("/admin/contests/{contest_id}")
async def delete_contest(contest_id: str, current_user: dict = Depends(get_current_admin)):
    """Delete a referral contest"""
    result = await db.referral_contests.delete_one({"id": contest_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contest not found")
    return {"message": "Contest deleted"}


@router.get("/contests/active")
async def get_active_contest():
    """Get the currently active referral contest (public)"""
    now = datetime.now(timezone.utc).isoformat()
    contest = await db.referral_contests.find_one(
        {"is_active": True, "end_date": {"$gte": now}},
        {"_id": 0}
    )
    return contest or {}


@router.get("/contests/leaderboard")
async def get_referral_leaderboard(contest_id: Optional[str] = None):
    """Get the referral leaderboard, optionally filtered by contest date range"""
    match_stage = {}
    
    if contest_id:
        contest = await db.referral_contests.find_one({"id": contest_id}, {"_id": 0})
        if contest:
            match_stage = {
                "created_date": {
                    "$gte": contest["start_date"],
                    "$lte": contest["end_date"],
                }
            }
    
    pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {"$group": {
            "_id": "$referrer_id",
            "referral_count": {"$sum": 1},
            "total_earned": {"$sum": {"$ifNull": ["$reward_amount", 0]}},
        }},
        {"$sort": {"referral_count": -1}},
        {"$limit": 25},
    ]
    
    results = await db.referrals.aggregate(pipeline).to_list(25)
    
    leaderboard = []
    for i, entry in enumerate(results):
        user = await db.users.find_one({"id": entry["_id"]}, {"_id": 0, "full_name": 1, "email": 1})
        name = user.get("full_name", "Unknown") if user else "Unknown"
        # Mask name for privacy: "Allen A." 
        parts = name.split()
        display_name = f"{parts[0]} {parts[1][0]}." if len(parts) > 1 else parts[0] if parts else "User"
        
        leaderboard.append({
            "rank": i + 1,
            "user_id": entry["_id"],
            "display_name": display_name,
            "referral_count": entry["referral_count"],
            "total_earned": entry["total_earned"],
        })
    
    return {"leaderboard": leaderboard}


# ==================== CURRENCY / EXCHANGE RATES ====================

import httpx

# Cache for exchange rates (refresh every 6 hours)
_exchange_rate_cache = {"rates": {}, "last_fetched": None}

COUNTRY_TO_CURRENCY = {
    "US": "USD", "GB": "GBP", "CA": "CAD", "AU": "AUD", "EU": "EUR",
    "NG": "NGN", "GH": "GHS", "KE": "KES", "ZA": "ZAR", "IN": "INR",
    "JP": "JPY", "CN": "CNY", "BR": "BRL", "MX": "MXN", "KR": "KRW",
    "DE": "EUR", "FR": "EUR", "IT": "EUR", "ES": "EUR", "NL": "EUR",
    "PT": "EUR", "BE": "EUR", "AT": "EUR", "IE": "EUR", "FI": "EUR",
    "GR": "EUR", "PH": "PHP", "TH": "THB", "MY": "MYR", "SG": "SGD",
    "HK": "HKD", "TW": "TWD", "AE": "AED", "SA": "SAR", "EG": "EGP",
    "PK": "PKR", "BD": "BDT", "LK": "LKR", "NP": "NPR", "ID": "IDR",
    "VN": "VND", "CO": "COP", "AR": "ARS", "CL": "CLP", "PE": "PEN",
    "SE": "SEK", "NO": "NOK", "DK": "DKK", "PL": "PLN", "CZ": "CZK",
    "HU": "HUF", "RO": "RON", "UA": "UAH", "RU": "RUB", "TR": "TRY",
    "IL": "ILS", "NZ": "NZD", "JM": "JMD", "TT": "TTD", "GY": "GYD",
}

CURRENCY_SYMBOLS = {
    "USD": "$", "GBP": "£", "EUR": "€", "NGN": "₦", "GHS": "₵",
    "KES": "KSh", "ZAR": "R", "INR": "₹", "JPY": "¥", "CNY": "¥",
    "BRL": "R$", "MXN": "$", "KRW": "₩", "PHP": "₱", "THB": "฿",
    "MYR": "RM", "SGD": "S$", "HKD": "HK$", "TWD": "NT$", "AED": "د.إ",
    "SAR": "﷼", "EGP": "£", "PKR": "₨", "BDT": "৳", "IDR": "Rp",
    "VND": "₫", "COP": "$", "ARS": "$", "CLP": "$", "PEN": "S/.",
    "SEK": "kr", "NOK": "kr", "DKK": "kr", "PLN": "zł", "CZK": "Kč",
    "HUF": "Ft", "RON": "lei", "UAH": "₴", "RUB": "₽", "TRY": "₺",
    "ILS": "₪", "NZD": "NZ$", "CAD": "C$", "AUD": "A$", "JMD": "J$",
    "TTD": "TT$", "GYD": "G$", "LKR": "Rs", "NPR": "₨",
}


async def _fetch_exchange_rates():
    """Fetch and cache exchange rates from free API"""
    now = datetime.now(timezone.utc)
    if _exchange_rate_cache["last_fetched"] and (now - _exchange_rate_cache["last_fetched"]).total_seconds() < 21600:
        return _exchange_rate_cache["rates"]
    
    try:
        async with httpx.AsyncClient(timeout=10) as client_http:
            resp = await client_http.get("https://open.er-api.com/v6/latest/USD")
            data = resp.json()
            if data.get("result") == "success":
                _exchange_rate_cache["rates"] = data.get("rates", {})
                _exchange_rate_cache["last_fetched"] = now
                return _exchange_rate_cache["rates"]
    except Exception as e:
        logging.warning(f"Exchange rate fetch failed: {e}")
    
    return _exchange_rate_cache["rates"] or {"USD": 1}


@router.get("/currency/detect")
async def detect_currency(request: Request):
    """Detect user's currency based on IP geolocation"""
    # Get client IP
    forwarded = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
    
    country_code = "US"
    try:
        async with httpx.AsyncClient(timeout=5) as client_http:
            resp = await client_http.get(f"http://ip-api.com/json/{client_ip}?fields=countryCode")
            data = resp.json()
            if data.get("countryCode"):
                country_code = data["countryCode"]
    except Exception:
        pass
    
    currency_code = COUNTRY_TO_CURRENCY.get(country_code, "USD")
    rates = await _fetch_exchange_rates()
    rate = rates.get(currency_code, 1.0)
    symbol = CURRENCY_SYMBOLS.get(currency_code, currency_code)
    
    return {
        "country_code": country_code,
        "currency_code": currency_code,
        "currency_symbol": symbol,
        "rate_to_usd": rate,
    }


@router.get("/currency/rates")
async def get_exchange_rates():
    """Get all exchange rates (base USD)"""
    rates = await _fetch_exchange_rates()
    return {"base": "USD", "rates": rates}


# ==================== DONATION / SPONSOR A READER ====================

class DonationRequest(BaseModel):
    amount: float
    message: str = ""
    origin_url: str


@router.post("/donations/create")
async def create_donation(data: DonationRequest, request: Request, current_user: dict = Depends(get_current_user)):
    """Create a donation to sponsor readers"""
    if data.amount < 1:
        raise HTTPException(status_code=400, detail="Minimum donation is $1")
    
    # Get billing config to calc stories funded
    settings = await db.system_config.find_one({"key": "admin_settings"}, {"_id": 0})
    cost_per_story = 0.20  # default
    if settings and settings.get("value"):
        cost_per_story = settings["value"].get("avg_cost_per_story", 0.20)
    
    stories_funded = int(data.amount / cost_per_story) if cost_per_story > 0 else 0
    
    stripe_key = await _get_stripe_key()
    if not stripe_key:
        raise HTTPException(status_code=500, detail="Payment not configured")
    
    from stripe_utils import StripeCheckout, CheckoutSessionRequest
    origin = data.origin_url.rstrip("/")
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_key, webhook_url=webhook_url)
    
    metadata = {"user_id": current_user["id"], "type": "donation", "message": data.message[:200]}
    
    checkout_req = CheckoutSessionRequest(
        amount=data.amount, currency="usd",
        success_url=f"{origin}/donate?status=success&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{origin}/donate?status=cancelled",
        metadata=metadata, payment_methods=["card"],
    )
    session = await stripe_checkout.create_checkout_session(checkout_req)
    
    donation = Donation(
        donor_id=current_user["id"],
        donor_name=current_user.get("full_name", current_user.get("email", "Anonymous")),
        amount=data.amount, stories_funded=stories_funded,
        payment_session_id=session.session_id, message=data.message,
    )
    await db.donations.insert_one(donation.model_dump())
    
    # Also create payment transaction for tracking
    txn = PaymentTransaction(
        user_id=current_user["id"], session_id=session.session_id,
        amount=data.amount, currency="usd", metadata=metadata,
    )
    await db.payment_transactions.insert_one(txn.model_dump())
    
    return {"url": session.url, "session_id": session.session_id, "stories_funded": stories_funded}


@router.get("/donations/status/{session_id}")
async def get_donation_status(session_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    """Check donation payment status"""
    donation = await db.donations.find_one({"payment_session_id": session_id}, {"_id": 0})
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    
    if donation.get("payment_status") == "paid":
        return {"status": "paid", "amount": donation["amount"], "stories_funded": donation["stories_funded"]}
    
    stripe_key = await _get_stripe_key()
    from stripe_utils import StripeCheckout
    host_url = str(request.base_url).rstrip("/")
    stripe_checkout = StripeCheckout(api_key=stripe_key, webhook_url=f"{host_url}/api/webhook/stripe")
    checkout_status = await stripe_checkout.get_checkout_status(session_id)
    
    if checkout_status.payment_status == "paid" and donation.get("payment_status") != "paid":
        await db.donations.update_one(
            {"payment_session_id": session_id},
            {"$set": {"payment_status": "paid"}}
        )
        return {"status": "paid", "amount": donation["amount"], "stories_funded": donation["stories_funded"]}
    
    return {"status": donation.get("payment_status", "pending"), "amount": donation["amount"], "stories_funded": donation["stories_funded"]}


@router.get("/donations/stats")
async def get_donation_stats():
    """Get public donation statistics"""
    pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "stories": {"$sum": "$stories_funded"}, "count": {"$sum": 1}}}
    ]
    agg = await db.donations.aggregate(pipeline).to_list(1)
    total = agg[0]["total"] if agg else 0
    stories = agg[0]["stories"] if agg else 0
    count = agg[0]["count"] if agg else 0
    
    recent = await db.donations.find(
        {"payment_status": "paid"}, {"_id": 0, "donor_name": 1, "amount": 1, "stories_funded": 1, "message": 1, "created_date": 1}
    ).sort("created_date", -1).to_list(10)
    
    return {"total_donated": round(total, 2), "total_stories_funded": stories, "total_donors": count, "recent": recent}


# ==================== SYSTEM UPDATE / MAINTENANCE MODE ====================

class SystemStatusUpdate(BaseModel):
    maintenance: bool = False
    message: str = ""
    allow_access: bool = True  # False = block all access, True = show banner only

@router.post("/admin/system-status")
async def set_system_status(data: SystemStatusUpdate, current_user: dict = Depends(get_current_admin)):
    """Toggle maintenance mode / system update banner. Users see the message in real-time."""
    value = {"maintenance": data.maintenance, "message": data.message, "allow_access": data.allow_access}
    await db.system_config.update_one(
        {"key": "system_status"},
        {"$set": {"key": "system_status", "value": value, "updated_date": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return {"status": "ok", "system_status": value}

@router.get("/admin/system-status")
async def get_system_status(current_user: dict = Depends(get_current_admin)):
    """Get current system status (admin view)."""
    config = await db.system_config.find_one({"key": "system_status"}, {"_id": 0})
    if config and config.get("value"):
        return config["value"]
    return {"maintenance": False, "message": "", "allow_access": True}


# ==================== ADMIN BILLING/ROI CONFIG ====================

@router.get("/admin/billing-config")
async def get_billing_config(current_user: dict = Depends(get_current_user)):
    """Get billing/ROI configuration"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    config = await db.system_config.find_one({"key": "billing_config"}, {"_id": 0})
    if config and config.get("value"):
        return config["value"]
    
    default = {
        "pricing_model": "per_seat",  # per_seat, roi_markup, flat_fee
        "per_seat_price": 4.99,
        "roi_markup_percent": 300,  # 300% = 3x cost
        "flat_fee_per_story": 0.50,
        "avg_cost_per_story": 0.20,
        "free_tier_stories": 5,
        "remove_limits_on_paid": True,
        "referral_reward_amount": 5.0,
        "donation_cost_per_story": 0.20,
    }
    return default


class BillingConfigUpdate(BaseModel):
    pricing_model: str = "per_seat"
    per_seat_price: float = 4.99
    roi_markup_percent: float = 300
    flat_fee_per_story: float = 0.50
    avg_cost_per_story: float = 0.20
    free_tier_stories: int = 5
    remove_limits_on_paid: bool = True
    referral_reward_amount: float = 5.0
    donation_cost_per_story: float = 0.20


@router.post("/admin/billing-config")
async def update_billing_config(data: BillingConfigUpdate, current_user: dict = Depends(get_current_user)):
    """Update billing/ROI configuration"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await db.system_config.update_one(
        {"key": "billing_config"},
        {"$set": {"key": "billing_config", "value": data.model_dump()}},
        upsert=True
    )
    return {"message": "Billing configuration updated", **data.model_dump()}


# ==================== ADMIN FEATURE FLAGS ====================

@router.get("/admin/feature-flags")
async def get_feature_flags(current_user: dict = Depends(get_current_user)):
    """Get system-wide feature flags"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    config = await db.system_config.find_one({"key": "feature_flags"}, {"_id": 0})
    if config and config.get("value"):
        return config["value"]
    
    return {
        "belief_system_enabled": True,
        "cultural_context_enabled": True,
        "multi_language_enabled": True,
        "donations_enabled": True,
        "referrals_enabled": True,
        "word_definitions_enabled": True,
        "accessibility_mode": True,
        "brand_sponsorship_enabled": True,
        "classroom_sponsorship_enabled": True,
        "parent_wordbank_creation_enabled": False,
    }


class FeatureFlagsUpdate(BaseModel):
    belief_system_enabled: bool = True
    cultural_context_enabled: bool = True
    multi_language_enabled: bool = True
    donations_enabled: bool = True
    referrals_enabled: bool = True
    word_definitions_enabled: bool = True
    accessibility_mode: bool = True
    brand_sponsorship_enabled: bool = True
    classroom_sponsorship_enabled: bool = True
    parent_wordbank_creation_enabled: bool = False


@router.post("/admin/feature-flags")
async def update_feature_flags(data: FeatureFlagsUpdate, current_user: dict = Depends(get_current_user)):
    """Update feature flags"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await db.system_config.update_one(
        {"key": "feature_flags"},
        {"$set": {"key": "feature_flags", "value": data.model_dump()}},
        upsert=True
    )
    return {"message": "Feature flags updated", **data.model_dump()}


@router.get("/feature-flags/parent-wordbank")
async def get_parent_wordbank_flag(current_user: dict = Depends(get_current_user)):
    """Check if parent word bank creation is enabled (for guardian portal)"""
    config = await db.system_config.find_one({"key": "feature_flags"}, {"_id": 0})
    enabled = config.get("value", {}).get("parent_wordbank_creation_enabled", False) if config else False
    return {"parent_wordbank_creation_enabled": enabled}




# ==================== INTEGRATION / API KEYS MANAGEMENT ====================

INTEGRATION_PROVIDERS = ["stripe", "paypal", "resend"]

def _mask_key(key: str) -> str:
    """Mask an API key, showing only last 4 chars"""
    if not key or len(key) < 8:
        return "****" if key else ""
    return "*" * (len(key) - 4) + key[-4:]


class IntegrationUpdate(BaseModel):
    stripe_api_key: str = ""
    paypal_client_id: str = ""
    paypal_secret: str = ""
    resend_api_key: str = ""
    daily_api_key: str = ""
    sender_email: str = "Semantic Vision <hello@semanticvision.ai>"
    paypal_mode: str = "sandbox"  # sandbox or live
    stripe_enabled: bool = True
    paypal_enabled: bool = False
    resend_enabled: bool = True
    daily_enabled: bool = False


@router.get("/admin/integrations")
async def get_integrations(current_user: dict = Depends(get_current_user)):
    """Get integration configs with masked keys"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    config = await db.system_config.find_one({"key": "integration_keys"}, {"_id": 0})
    stored = config.get("value", {}) if config else {}

    # Merge DB values with env fallbacks
    stripe_key = stored.get("stripe_api_key") or os.environ.get("STRIPE_API_KEY", "")
    paypal_id = stored.get("paypal_client_id") or os.environ.get("PAYPAL_CLIENT_ID", "")
    paypal_secret = stored.get("paypal_secret") or os.environ.get("PAYPAL_SECRET", "")
    resend_key = stored.get("resend_api_key") or os.environ.get("RESEND_API_KEY", "")
    sender = stored.get("sender_email") or os.environ.get("SENDER_EMAIL", "Semantic Vision <hello@semanticvision.ai>")

    return {
        "stripe": {
            "api_key_masked": _mask_key(stripe_key),
            "has_key": bool(stripe_key),
            "enabled": stored.get("stripe_enabled", bool(stripe_key)),
        },
        "paypal": {
            "client_id_masked": _mask_key(paypal_id),
            "secret_masked": _mask_key(paypal_secret),
            "has_keys": bool(paypal_id and paypal_secret),
            "enabled": stored.get("paypal_enabled", bool(paypal_id and paypal_secret)),
            "mode": stored.get("paypal_mode", "sandbox"),
        },
        "resend": {
            "api_key_masked": _mask_key(resend_key),
            "has_key": bool(resend_key),
            "enabled": stored.get("resend_enabled", bool(resend_key)),
            "sender_email": sender,
        },
        "daily": {
            "api_key_masked": _mask_key(stored.get("daily_api_key", "")),
            "has_key": bool(stored.get("daily_api_key", "")),
            "enabled": stored.get("daily_enabled", False),
        },
    }


@router.put("/admin/integrations")
async def update_integrations(data: IntegrationUpdate, current_user: dict = Depends(get_current_user)):
    """Update integration API keys and settings"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    # Get existing config to preserve unchanged keys
    config = await db.system_config.find_one({"key": "integration_keys"}, {"_id": 0})
    existing = config.get("value", {}) if config else {}

    # Only update keys that are not masked placeholders (i.e., user actually typed a new key)
    update = {}
    if data.stripe_api_key and not data.stripe_api_key.startswith("*"):
        update["stripe_api_key"] = data.stripe_api_key
    else:
        update["stripe_api_key"] = existing.get("stripe_api_key", os.environ.get("STRIPE_API_KEY", ""))

    if data.paypal_client_id and not data.paypal_client_id.startswith("*"):
        update["paypal_client_id"] = data.paypal_client_id
    else:
        update["paypal_client_id"] = existing.get("paypal_client_id", os.environ.get("PAYPAL_CLIENT_ID", ""))

    if data.paypal_secret and not data.paypal_secret.startswith("*"):
        update["paypal_secret"] = data.paypal_secret
    else:
        update["paypal_secret"] = existing.get("paypal_secret", os.environ.get("PAYPAL_SECRET", ""))

    if data.resend_api_key and not data.resend_api_key.startswith("*"):
        update["resend_api_key"] = data.resend_api_key
    else:
        update["resend_api_key"] = existing.get("resend_api_key", os.environ.get("RESEND_API_KEY", ""))

    if data.daily_api_key and not data.daily_api_key.startswith("*"):
        update["daily_api_key"] = data.daily_api_key
    else:
        update["daily_api_key"] = existing.get("daily_api_key", "")

    update["sender_email"] = data.sender_email
    update["paypal_mode"] = data.paypal_mode
    update["stripe_enabled"] = data.stripe_enabled
    update["paypal_enabled"] = data.paypal_enabled
    update["resend_enabled"] = data.resend_enabled
    update["daily_enabled"] = data.daily_enabled
    update["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.system_config.update_one(
        {"key": "integration_keys"},
        {"$set": {"value": update}},
        upsert=True,
    )

    # Update runtime environment so services pick up new keys immediately
    os.environ["STRIPE_API_KEY"] = update["stripe_api_key"]
    os.environ["PAYPAL_CLIENT_ID"] = update["paypal_client_id"]
    os.environ["PAYPAL_SECRET"] = update["paypal_secret"]
    os.environ["RESEND_API_KEY"] = update["resend_api_key"]
    os.environ["SENDER_EMAIL"] = update["sender_email"]

    # Update resend module key and stripe module key
    try:
        import resend
        resend.api_key = update["resend_api_key"]
    except Exception:
        pass
    try:
        stripe.api_key = update["stripe_api_key"]
    except Exception:
        pass

    return {"message": "Integration settings saved successfully"}


# ==================== ADMIN IMPERSONATION ====================

@router.post("/admin/impersonate/{user_id}")
async def impersonate_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Generate a token to view app as another user (admin only)"""
    if current_user.get("role") != "admin" and not current_user.get("is_delegated_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    target = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a JWT for the target user using the same auth module
    from auth import create_access_token, SECRET_KEY
    token_data = {
        "sub": target["id"],
        "email": target.get("email", ""),
        "role": target.get("role", "guardian"),
        "impersonated_by": current_user["id"],
    }
    token = create_access_token(token_data, expires_delta=timedelta(hours=1))

    return {
        "access_token": token,
        "user": {
            "id": target["id"],
            "email": target.get("email", ""),
            "full_name": target.get("full_name", ""),
            "role": target.get("role", ""),
            "is_delegated_admin": target.get("is_delegated_admin", False),
            "impersonated_by": current_user.get("full_name", "Admin"),
        },
    }


# ==================== DAILY.CO SCREEN SHARE ====================

@router.post("/admin/support-session")
async def create_support_session(current_user: dict = Depends(get_current_user)):
    """Create a Daily.co room for screen sharing support"""
    if current_user.get("role") != "admin" and not current_user.get("is_delegated_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    config = await db.system_config.find_one({"key": "integration_keys"}, {"_id": 0})
    stored = config.get("value", {}) if config else {}
    daily_key = stored.get("daily_api_key") or os.environ.get("DAILY_API_KEY", "")

    if not daily_key:
        raise HTTPException(status_code=500, detail="Daily.co not configured. Add your API key in Admin > Integrations.")

    import httpx
    room_name = f"sv-support-{str(uuid.uuid4())[:8]}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.daily.co/v1/rooms",
            headers={"Authorization": f"Bearer {daily_key}", "Content-Type": "application/json"},
            json={
                "name": room_name,
                "properties": {
                    "enable_screenshare": True,
                    "enable_chat": True,
                    "exp": int((datetime.now(timezone.utc).timestamp()) + 7200),  # 2 hours
                    "max_participants": 4,
                },
            },
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            logger.error(f"Daily.co room creation failed: {resp.text}")
            raise HTTPException(status_code=502, detail="Failed to create support room")
        room = resp.json()

    session = {
        "id": str(uuid.uuid4()),
        "room_name": room_name,
        "room_url": room.get("url", f"https://semanticvision.daily.co/{room_name}"),
        "created_by": current_user["id"],
        "created_by_name": current_user.get("full_name", "Admin"),
        "status": "active",
        "created_date": datetime.now(timezone.utc).isoformat(),
    }
    await db.support_sessions.insert_one(dict(session))

    return session


@router.get("/admin/support-sessions")
async def get_support_sessions(current_user: dict = Depends(get_current_user)):
    """List active support sessions"""
    if current_user.get("role") != "admin" and not current_user.get("is_delegated_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    sessions = await db.support_sessions.find({"status": "active"}, {"_id": 0}).sort("created_date", -1).to_list(20)
    return sessions
