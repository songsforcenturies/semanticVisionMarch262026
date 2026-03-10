"""Authentication routes: register, login, forgot password, email verification."""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import uuid, random, string, os

from database import db, logger
from services import send_email, generate_6digit_code
from models import (
    User, UserCreate, UserLogin, UserResponse, UserRole,
    Subscription, SubscriptionPlan, SubscriptionStatus, SubscriptionFeatures,
    WalletTransaction, WalletTransactionType,
    Referral, Affiliate, AffiliateReferral, AffiliateRewardType,
    generate_referral_code,
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_admin,
)

router = APIRouter()

# ==================== AUTHENTICATION ROUTES ====================

class UserCreateWithReferral(BaseModel):
    email: str
    full_name: str
    password: str
    role: UserRole = UserRole.GUARDIAN
    referral_code: Optional[str] = None


@router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreateWithReferral):
    """Register a new guardian/teacher user"""
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        referred_by=user_data.referral_code.strip().upper() if user_data.referral_code else None,
    )
    
    user_dict = user.model_dump()
    await db.users.insert_one(user_dict)
    
    # Create default subscription for guardians
    if user.role == UserRole.GUARDIAN:
        subscription = Subscription(
            guardian_id=user.id,
            plan=SubscriptionPlan.FREE,
            student_seats=10,
            active_students=0
        )
        await db.subscriptions.insert_one(subscription.model_dump())
    
    # Process referral reward
    if user_data.referral_code:
        ref_code = user_data.referral_code.strip().upper()
        
        # Check if it's an affiliate code (AFF-XXXXX format)
        affiliate = await db.affiliates.find_one({"affiliate_code": ref_code, "is_active": True, "confirmed": True})
        if affiliate:
            # Process affiliate referral
            reward_type = affiliate.get("reward_type", "flat_fee")
            reward_amount = 0.0
            if reward_type == "flat_fee":
                reward_amount = affiliate.get("flat_fee_amount", 5.0)
            elif reward_type == "wallet_credits":
                reward_amount = affiliate.get("wallet_credit_amount", 5.0)
            elif reward_type == "percentage":
                reward_amount = 0  # calculated on subscription payment
            
            # Record affiliate referral
            await db.affiliate_referrals.insert_one(AffiliateReferral(
                affiliate_id=affiliate["id"], affiliate_code=ref_code,
                referred_user_id=user.id, referred_email=user.email,
                reward_type=AffiliateRewardType(reward_type), reward_amount=reward_amount,
                status="credited" if reward_amount > 0 else "pending",
            ).model_dump())
            
            # Credit affiliate's pending balance
            if reward_amount > 0:
                await db.affiliates.update_one({"id": affiliate["id"]}, {
                    "$inc": {"total_referrals": 1, "total_earnings": reward_amount, "pending_balance": reward_amount}
                })
            else:
                await db.affiliates.update_one({"id": affiliate["id"]}, {"$inc": {"total_referrals": 1}})
        else:
            # Regular user referral (existing logic)
            referrer = await db.users.find_one({"referral_code": ref_code})
            if referrer:
                settings = await db.system_config.find_one({"key": "admin_settings"}, {"_id": 0})
                reward = 5.0
                if settings and settings.get("value"):
                    reward = settings["value"].get("referral_reward_amount", 5.0)
                
                old_bal = referrer.get("wallet_balance", 0.0)
                new_bal = round(old_bal + reward, 2)
                await db.users.update_one({"id": referrer["id"]}, {"$set": {"wallet_balance": new_bal}})
                await db.wallet_transactions.insert_one(WalletTransaction(
                    user_id=referrer["id"], type=WalletTransactionType.CREDIT,
                    amount=reward, description=f"Referral reward: {user.full_name} joined!",
                    reference_id=user.id, balance_after=new_bal,
                ).model_dump())
                
                new_user_bal = round(user.wallet_balance + reward, 2)
                await db.users.update_one({"id": user.id}, {"$set": {"wallet_balance": new_user_bal}})
                await db.wallet_transactions.insert_one(WalletTransaction(
                    user_id=user.id, type=WalletTransactionType.CREDIT,
                    amount=reward, description=f"Welcome bonus from referral!",
                    reference_id=referrer["id"], balance_after=new_user_bal,
                ).model_dump())
                
                await db.referrals.insert_one(Referral(
                    referrer_id=referrer["id"], referred_id=user.id,
                    referral_code=ref_code, reward_amount=reward, reward_given=True,
                ).model_dump())
    
    # Send verification email (non-blocking, don't fail registration if email fails)
    try:
        verify_code = generate_6digit_code()
        expires = datetime.now(timezone.utc) + timedelta(minutes=30)
        await db.email_verifications.insert_one({
            "email": user.email, "user_id": user.id,
            "code": verify_code, "expires": expires.isoformat(), "used": False,
        })
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #1a1a1a; border-bottom: 3px solid #f59e0b; padding-bottom: 10px;">Welcome to Semantic Vision!</h2>
          <p>Hi {user.full_name}, please verify your email with the code below:</p>
          <div style="background: #fef3c7; border: 3px solid #1a1a1a; padding: 20px; text-align: center; margin: 20px 0;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1a1a1a;">{verify_code}</span>
          </div>
          <p style="color: #666; font-size: 14px;">This code expires in 30 minutes.</p>
        </div>
        """
        await send_email(user.email, "Semantic Vision - Verify Your Email", html)
    except Exception as e:
        logger.warning(f"Failed to send verification email to {user.email}: {e}")

    return UserResponse(**user_dict)


@router.post("/auth/login")
async def login(credentials: UserLogin):
    """Login for parents/teachers/admin"""
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Block deactivated users
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Your account has been deactivated. Please contact an administrator.")
    
    # Create access token
    access_token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"]
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "wallet_balance": user.get("wallet_balance", 0.0),
            "is_delegated_admin": user.get("is_delegated_admin", False),
            "referral_code": user.get("referral_code", ""),
            "linked_brand_id": user.get("linked_brand_id"),
            "brand_approved": user.get("brand_approved", False),
        }
    }



# ==================== EMAIL SERVICE (RESEND) ====================
import resend
import asyncio
import random
import string

resend.api_key = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "Semantic Vision <hello@semanticvision.ai>")


async def send_email(to_email: str, subject: str, html: str):
    """Send email via Resend (non-blocking)"""
    params = {"from": SENDER_EMAIL, "to": [to_email], "subject": subject, "html": html}
    try:
        result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {result}")
        return result
    except Exception as e:
        logger.error(f"Email send failed to {to_email}: {e}")
        raise


def generate_6digit_code():
    return ''.join(random.choices(string.digits, k=6))


# ==================== FORGOT PASSWORD ====================

class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str


@router.post("/auth/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    """Send a 6-digit reset code to the user email"""
    email = data.email.lower().strip()
    user = await db.users.find_one({"email": email})
    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If an account exists with that email, a reset code has been sent."}

    code = generate_6digit_code()
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    await db.password_resets.delete_many({"email": email})
    await db.password_resets.insert_one({
        "email": email,
        "code": code,
        "expires": expires.isoformat(),
        "used": False,
    })

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #1a1a1a; border-bottom: 3px solid #f59e0b; padding-bottom: 10px;">Semantic Vision Password Reset</h2>
      <p>Your password reset code is:</p>
      <div style="background: #fef3c7; border: 3px solid #1a1a1a; padding: 20px; text-align: center; margin: 20px 0;">
        <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1a1a1a;">{code}</span>
      </div>
      <p style="color: #666; font-size: 14px;">This code expires in 15 minutes. If you did not request this, please ignore this email.</p>
    </div>
    """
    try:
        await send_email(email, "Semantic Vision - Password Reset Code", html)
    except Exception as e:
        logger.error(f"Failed to send reset email: {e}")

    return {"message": "If an account exists with that email, a reset code has been sent."}


@router.post("/auth/reset-password")
async def reset_password_with_code(data: ResetPasswordRequest):
    """Reset password using the 6-digit code"""
    email = data.email.lower().strip()
    reset_doc = await db.password_resets.find_one({"email": email, "code": data.code, "used": False})

    if not reset_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    # Check expiry
    expires = datetime.fromisoformat(reset_doc["expires"])
    if datetime.now(timezone.utc) > expires:
        raise HTTPException(status_code=400, detail="Reset code has expired. Please request a new one.")

    # Update password
    new_hash = get_password_hash(data.new_password)
    await db.users.update_one({"email": email}, {"$set": {"password_hash": new_hash}})
    await db.password_resets.update_one({"email": email, "code": data.code}, {"$set": {"used": True}})

    return {"message": "Password reset successfully. You can now log in with your new password."}


# ==================== EMAIL VERIFICATION ====================

@router.post("/auth/send-verification")
async def send_verification_email(current_user: dict = Depends(get_current_user)):
    """Send email verification code to the logged-in user"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("email_verified"):
        return {"message": "Email already verified"}

    code = generate_6digit_code()
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)

    await db.email_verifications.delete_many({"email": user["email"]})
    await db.email_verifications.insert_one({
        "email": user["email"],
        "user_id": user["id"],
        "code": code,
        "expires": expires.isoformat(),
        "used": False,
    })

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #1a1a1a; border-bottom: 3px solid #f59e0b; padding-bottom: 10px;">Welcome to Semantic Vision!</h2>
      <p>Hi {user['full_name']}, please verify your email with the code below:</p>
      <div style="background: #fef3c7; border: 3px solid #1a1a1a; padding: 20px; text-align: center; margin: 20px 0;">
        <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1a1a1a;">{code}</span>
      </div>
      <p style="color: #666; font-size: 14px;">This code expires in 30 minutes.</p>
    </div>
    """
    try:
        await send_email(user["email"], "Semantic Vision - Verify Your Email", html)
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return {"message": "Verification code sent to your email"}


class VerifyEmailRequest(BaseModel):
    code: str


@router.post("/auth/verify-email")
async def verify_email(data: VerifyEmailRequest, current_user: dict = Depends(get_current_user)):
    """Verify email with 6-digit code"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    verify_doc = await db.email_verifications.find_one({
        "user_id": user["id"], "code": data.code, "used": False
    })

    if not verify_doc:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    expires = datetime.fromisoformat(verify_doc["expires"])
    if datetime.now(timezone.utc) > expires:
        raise HTTPException(status_code=400, detail="Verification code expired. Please request a new one.")

    await db.users.update_one({"id": user["id"]}, {"$set": {"email_verified": True}})
    await db.email_verifications.update_one({"user_id": user["id"], "code": data.code}, {"$set": {"used": True}})

    return {"message": "Email verified successfully!"}



class StudentPinLogin(BaseModel):
    student_code: str
    pin: str

@router.post("/auth/student-login")
async def student_login(data: StudentPinLogin):
    """PIN-based login for students - requires both student code and PIN"""
    student = await db.students.find_one({
        "student_code": data.student_code,
        "access_pin": data.pin,
        "status": "active"
    })
    if not student:
        raise HTTPException(status_code=401, detail="Invalid student code or PIN")
    
    # Get guardian info
    guardian = await db.users.find_one({"id": student["guardian_id"]})
    
    return {
        "student": {
            "id": student["id"],
            "full_name": student["full_name"],
            "access_pin": student["access_pin"],
            "guardian_id": student["guardian_id"],
            "age": student.get("age"),
            "grade_level": student.get("grade_level"),
            "interests": student.get("interests", []),
            "mastered_tokens": student.get("mastered_tokens", []),
            "agentic_reach_score": student.get("agentic_reach_score", 0),
            "biological_target": student.get("biological_target", 0)
        },
        "guardian_name": guardian["full_name"] if guardian else "Unknown"
    }


@router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user"""
    user = await db.users.find_one({"id": current_user["id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**user)




# ==================== USER ID CARDS ====================

@router.get("/user-card")
async def get_user_card(current_user: dict = Depends(get_current_user)):
    """Get data for generating a user ID/invitation card"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    students = await db.students.find(
        {"guardian_id": current_user["id"]}, {"_id": 0}
    ).to_list(50)

    base_url = os.environ.get("APP_URL", "https://semanticvision.ai")

    # Guardian card
    guardian_card = {
        "type": "guardian",
        "name": user.get("full_name", ""),
        "email": user.get("email", ""),
        "referral_code": user.get("referral_code", ""),
        "referral_url": f"{base_url}/register?ref={user.get('referral_code', '')}",
        "member_since": user.get("created_date", ""),
        "student_count": len(students),
    }

    # Student cards
    student_cards = []
    for s in students:
        student_cards.append({
            "type": "student",
            "name": s.get("full_name", ""),
            "student_code": s.get("student_code", ""),
            "age": s.get("age", 0),
            "reading_level": s.get("reading_level", "beginner"),
            "login_url": f"{base_url}/student-login",
        })

    return {"guardian_card": guardian_card, "student_cards": student_cards}
