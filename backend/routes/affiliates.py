"""Affiliate system routes: signup, stats, admin management, offers."""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid, os

from database import db, logger
from services import send_email
from models import (
    UserRole, Affiliate, AffiliateRewardType,
    BrandOffer, UserOfferPreference,
)
from auth import get_current_user, get_current_admin, get_current_guardian

router = APIRouter()

# ================================
# AFFILIATE SYSTEM ENDPOINTS
# ================================

@router.post("/affiliates/signup")
async def affiliate_signup(data: dict = Body(...)):
    """Public signup for affiliate program"""
    email = data.get("email", "").strip().lower()
    full_name = data.get("full_name", "").strip()
    if not email or not full_name:
        raise HTTPException(status_code=400, detail="Email and full name required")
    
    # Check if already an affiliate
    existing = await db.affiliates.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="This email is already registered as an affiliate")
    
    # Check settings
    settings = await db.system_config.find_one({"key": "affiliate_settings"})
    if settings and not settings.get("value", {}).get("affiliate_program_enabled", True):
        raise HTTPException(status_code=400, detail="Affiliate program is currently closed")
    
    auto_approve = settings.get("value", {}).get("auto_approve", True) if settings else True
    defaults = settings.get("value", {}) if settings else {}
    
    affiliate = Affiliate(
        email=email, full_name=full_name, user_id="",
        reward_type=AffiliateRewardType(defaults.get("default_reward_type", "flat_fee")),
        flat_fee_amount=defaults.get("default_flat_fee", 5.0),
        percentage_rate=defaults.get("default_percentage", 10.0),
        wallet_credit_amount=defaults.get("default_wallet_credits", 5.0),
        confirmed=auto_approve, is_active=auto_approve,
    )
    
    doc = affiliate.model_dump()
    await db.affiliates.insert_one(doc)
    
    # Send confirmation email via Resend
    try:
        import resend
        resend_key = os.environ.get("RESEND_API_KEY")
        if resend_key:
            resend.api_key = resend_key
            affiliate_link = f"{os.environ.get('FRONTEND_URL', 'https://patent-filing-deploy.preview.emergentagent.com')}/register?ref={affiliate.affiliate_code}"
            resend.Emails.send({
                "from": f"Semantic Vision <{os.environ.get('SENDER_EMAIL', 'hello@semanticvision.ai')}>",
                "to": [email],
                "subject": "Welcome to the Semantic Vision Affiliate Program!",
                "html": f"""
                <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;background:#1A2236;color:#fff;border-radius:12px;">
                    <h1 style="color:#D4A853;">Welcome, {full_name}!</h1>
                    <p>You've been {'approved' if auto_approve else 'registered'} as a Semantic Vision affiliate.</p>
                    <div style="background:#0F172A;padding:16px;border-radius:8px;margin:16px 0;">
                        <p style="margin:0;color:#D4A853;font-size:12px;text-transform:uppercase;">Your Affiliate Code</p>
                        <p style="margin:4px 0 0;font-size:24px;font-weight:bold;font-family:monospace;">{affiliate.affiliate_code}</p>
                    </div>
                    <div style="background:#0F172A;padding:16px;border-radius:8px;margin:16px 0;">
                        <p style="margin:0;color:#D4A853;font-size:12px;text-transform:uppercase;">Your Referral Link</p>
                        <p style="margin:4px 0 0;word-break:break-all;"><a href="{affiliate_link}" style="color:#38BDF8;">{affiliate_link}</a></p>
                    </div>
                    <p>Share your link and earn rewards for every user who signs up!</p>
                    <p style="color:#94a3b8;font-size:12px;">Reward: ${affiliate.flat_fee_amount} per referral</p>
                </div>
                """
            })
    except Exception as e:
        logging.warning(f"Failed to send affiliate welcome email: {e}")
    
    return {
        "message": "Affiliate registration successful!" if auto_approve else "Registration received. Pending admin approval.",
        "affiliate_code": affiliate.affiliate_code,
        "confirmed": affiliate.confirmed,
    }


@router.get("/affiliates/track/{affiliate_code}")
async def track_affiliate_click(affiliate_code: str):
    """Track when someone clicks an affiliate link"""
    affiliate = await db.affiliates.find_one({"affiliate_code": affiliate_code, "is_active": True})
    if not affiliate:
        raise HTTPException(status_code=404, detail="Invalid affiliate code")
    return {"valid": True, "affiliate_code": affiliate_code}


@router.get("/affiliates/my-stats")
async def get_affiliate_stats(current_user: dict = Depends(get_current_user)):
    """Get affiliate stats for current user"""
    affiliate = await db.affiliates.find_one({"email": current_user["email"]}, {"_id": 0})
    if not affiliate:
        return {"is_affiliate": False}
    referrals = await db.affiliate_referrals.find(
        {"affiliate_id": affiliate["id"]}, {"_id": 0}
    ).sort("created_date", -1).to_list(100)
    return {"is_affiliate": True, "affiliate": affiliate, "referrals": referrals}


# Admin Affiliate Management
@router.get("/admin/affiliates")
async def admin_get_affiliates(current_user: dict = Depends(get_current_admin)):
    """Admin: List all affiliates"""
    affiliates = await db.affiliates.find({}, {"_id": 0}).sort("created_date", -1).to_list(500)
    settings = await db.system_config.find_one({"key": "affiliate_settings"})
    return {
        "affiliates": affiliates,
        "settings": settings.get("value", {}) if settings else AffiliateSettings().model_dump(),
    }


@router.put("/admin/affiliates/settings")
async def admin_update_affiliate_settings(data: dict = Body(...), current_user: dict = Depends(get_current_admin)):
    """Admin: Update affiliate program settings"""
    await db.system_config.update_one(
        {"key": "affiliate_settings"},
        {"$set": {"key": "affiliate_settings", "value": data}},
        upsert=True
    )
    return {"message": "Affiliate settings updated"}


@router.put("/admin/affiliates/{affiliate_id}")
async def admin_update_affiliate(affiliate_id: str, data: dict = Body(...), current_user: dict = Depends(get_current_admin)):
    """Admin: Update individual affiliate (approve, change rates, deactivate)"""
    update = {}
    for field in ["is_active", "confirmed", "reward_type", "flat_fee_amount", "percentage_rate", "wallet_credit_amount"]:
        if field in data:
            update[field] = data[field]
    if update:
        await db.affiliates.update_one({"id": affiliate_id}, {"$set": update})
    
    # If confirming, send confirmation email
    if data.get("confirmed") and not data.get("_skip_email"):
        affiliate = await db.affiliates.find_one({"id": affiliate_id})
        if affiliate:
            try:
                import resend
                resend_key = os.environ.get("RESEND_API_KEY")
                if resend_key:
                    resend.api_key = resend_key
                    resend.Emails.send({
                        "from": f"Semantic Vision <{os.environ.get('SENDER_EMAIL', 'hello@semanticvision.ai')}>",
                        "to": [affiliate["email"]],
                        "subject": "Your Semantic Vision Affiliate Account is Approved!",
                        "html": f"<p>Hi {affiliate['full_name']},</p><p>Your affiliate account has been approved. Your code is <b>{affiliate['affiliate_code']}</b>.</p>"
                    })
            except Exception:
                pass
    
    return {"message": "Affiliate updated"}


@router.post("/admin/affiliates/{affiliate_id}/payout")
async def admin_payout_affiliate(affiliate_id: str, data: dict = Body(...), current_user: dict = Depends(get_current_admin)):
    """Admin: Record a payout to an affiliate"""
    amount = data.get("amount", 0)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    affiliate = await db.affiliates.find_one({"id": affiliate_id})
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    
    if amount > affiliate.get("pending_balance", 0):
        raise HTTPException(status_code=400, detail="Amount exceeds pending balance")
    
    await db.affiliates.update_one({"id": affiliate_id}, {
        "$inc": {"pending_balance": -amount, "total_paid": amount}
    })
    
    # Log the payout
    await db.affiliate_payouts.insert_one({
        "id": str(uuid.uuid4()),
        "affiliate_id": affiliate_id,
        "amount": amount,
        "method": data.get("method", "manual"),
        "created_date": datetime.now(timezone.utc).isoformat(),
    })
    
    return {"message": f"Payout of ${amount:.2f} recorded"}


# ================================
# BRAND OFFERS ENDPOINTS
# ================================

@router.post("/brands/offers")
async def create_brand_offer(data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """Brand: Create an offer/promotion"""
    brand_id = current_user.get("linked_brand_id")
    if not brand_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only brand partners can create offers")
    if current_user.get("role") == "admin":
        brand_id = data.get("brand_id")
    
    brand = await db.brands.find_one({"id": brand_id})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    offer = BrandOffer(
        brand_id=brand_id,
        brand_name=brand["name"],
        title=data.get("title", ""),
        description=data.get("description", ""),
        offer_type=data.get("offer_type", "free"),
        price=data.get("price", 0),
        external_link=data.get("external_link"),
        internal_promo_code=data.get("internal_promo_code"),
        target_all_users=data.get("target_all_users", True),
        target_user_ids=data.get("target_user_ids", []),
    )
    doc = offer.model_dump()
    await db.brand_offers.insert_one(doc)
    del doc["_id"]
    return doc


@router.get("/brands/offers")
async def get_brand_offers(current_user: dict = Depends(get_current_user)):
    """Brand: Get own offers"""
    brand_id = current_user.get("linked_brand_id")
    if not brand_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No brand linked")
    query = {"brand_id": brand_id} if brand_id else {}
    offers = await db.brand_offers.find(query, {"_id": 0}).sort("created_date", -1).to_list(100)
    return offers


@router.put("/brands/offers/{offer_id}")
async def update_brand_offer(offer_id: str, data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """Brand: Update an offer"""
    update = {}
    for f in ["title", "description", "offer_type", "price", "external_link", "internal_promo_code", "is_active", "target_all_users", "target_user_ids"]:
        if f in data:
            update[f] = data[f]
    if update:
        await db.brand_offers.update_one({"id": offer_id}, {"$set": update})
    return {"message": "Offer updated"}


@router.delete("/brands/offers/{offer_id}")
async def delete_brand_offer(offer_id: str, current_user: dict = Depends(get_current_user)):
    """Brand: Delete an offer"""
    await db.brand_offers.delete_one({"id": offer_id})
    return {"message": "Offer deleted"}


# Parent-facing offers
@router.get("/offers")
async def get_available_offers(current_user: dict = Depends(get_current_user)):
    """Parent: Get available brand offers"""
    # Check user preference
    pref = await db.user_offer_preferences.find_one({"user_id": current_user["id"]})
    if pref and not pref.get("offers_enabled", True):
        return {"offers_enabled": False, "offers": []}
    
    dismissed = pref.get("dismissed_offer_ids", []) if pref else []
    
    # Get active offers targeting this user or all users
    offers = await db.brand_offers.find({
        "is_active": True,
        "id": {"$nin": dismissed},
        "$or": [
            {"target_all_users": True},
            {"target_user_ids": current_user["id"]},
        ]
    }, {"_id": 0}).sort("created_date", -1).to_list(50)
    
    return {"offers_enabled": True, "offers": offers}


@router.put("/offers/preferences")
async def update_offer_preferences(data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """Parent: Toggle offers on/off or dismiss specific offers"""
    update = {"user_id": current_user["id"]}
    if "offers_enabled" in data:
        update["offers_enabled"] = data["offers_enabled"]
    if "dismiss_offer_id" in data:
        update["$addToSet"] = {"dismissed_offer_ids": data["dismiss_offer_id"]}
    
    await db.user_offer_preferences.update_one(
        {"user_id": current_user["id"]},
        {"$set": {k: v for k, v in update.items() if k != "$addToSet"},
         **({} if "$addToSet" not in update else {"$addToSet": update["$addToSet"]})},
        upsert=True
    )
    return {"message": "Preferences updated"}


@router.post("/offers/{offer_id}/click")
async def track_offer_click(offer_id: str, current_user: dict = Depends(get_current_user)):
    """Track when parent clicks an offer"""
    await db.brand_offers.update_one({"id": offer_id}, {"$inc": {"clicks": 1}})
    return {"message": "Click tracked"}


