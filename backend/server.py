from fastapi import FastAPI, APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json as json_lib
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

# Import models and auth
from models import (
    User, UserCreate, UserLogin, UserResponse, UserRole,
    Student, StudentCreate, StudentUpdate,
    Subscription, SubscriptionPlan, SubscriptionStatus,
    WordBank, WordBankCreate,
    Narrative, NarrativeCreate, NarrativeStatus,
    Assessment, ReadLog, WordBankGift, GiftCreate,
    ClassroomSession, SystemConfig, SessionStatus, ParticipatingStudent,
    get_biological_target,
    WalletTransaction, WalletTransactionType, PaymentTransaction,
    Coupon, CouponType, CouponRedemption, AdminSubscriptionPlan,
    Referral, Donation, generate_referral_code,
    Brand, BrandProduct, BrandImpression, ClassroomSponsorship, BrandCampaign,
    TargetRegion,
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_admin, get_current_guardian, get_current_teacher
)
from story_service import story_service
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="LexiMaster API", version="1.0.0")

# Create router with /api prefix
api_router = APIRouter(prefix="/api")

# Serve uploaded files
from fastapi.staticfiles import StaticFiles
_upload_root = Path(__file__).parent / "uploads"
_upload_root.mkdir(parents=True, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=str(_upload_root)), name="uploads")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== WEBSOCKET CONNECTION MANAGER ====================

class ConnectionManager:
    """Manages WebSocket connections per session"""
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id] = [c for c in self.active_connections[session_id] if c != websocket]
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            dead = []
            for conn in self.active_connections[session_id]:
                try:
                    await conn.send_json(message)
                except Exception:
                    dead.append(conn)
            for d in dead:
                self.disconnect(d, session_id)

ws_manager = ConnectionManager()


# ==================== AUTHENTICATION ROUTES ====================

class UserCreateWithReferral(BaseModel):
    email: str
    full_name: str
    password: str
    role: UserRole = UserRole.GUARDIAN
    referral_code: Optional[str] = None


@api_router.post("/auth/register", response_model=UserResponse)
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
        referrer = await db.users.find_one({"referral_code": ref_code})
        if referrer:
            # Get reward amount from admin settings
            settings = await db.system_config.find_one({"key": "admin_settings"}, {"_id": 0})
            reward = 5.0
            if settings and settings.get("value"):
                reward = settings["value"].get("referral_reward_amount", 5.0)
            
            # Credit referrer
            old_bal = referrer.get("wallet_balance", 0.0)
            new_bal = round(old_bal + reward, 2)
            await db.users.update_one({"id": referrer["id"]}, {"$set": {"wallet_balance": new_bal}})
            await db.wallet_transactions.insert_one(WalletTransaction(
                user_id=referrer["id"], type=WalletTransactionType.CREDIT,
                amount=reward, description=f"Referral reward: {user.full_name} joined!",
                reference_id=user.id, balance_after=new_bal,
            ).model_dump())
            
            # Credit new user
            new_user_bal = round(user.wallet_balance + reward, 2)
            await db.users.update_one({"id": user.id}, {"$set": {"wallet_balance": new_user_bal}})
            await db.wallet_transactions.insert_one(WalletTransaction(
                user_id=user.id, type=WalletTransactionType.CREDIT,
                amount=reward, description=f"Welcome bonus from referral!",
                reference_id=referrer["id"], balance_after=new_user_bal,
            ).model_dump())
            
            # Record referral
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
          <h2 style="color: #1a1a1a; border-bottom: 3px solid #f59e0b; padding-bottom: 10px;">Welcome to LexiMaster!</h2>
          <p>Hi {user.full_name}, please verify your email with the code below:</p>
          <div style="background: #fef3c7; border: 3px solid #1a1a1a; padding: 20px; text-align: center; margin: 20px 0;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1a1a1a;">{verify_code}</span>
          </div>
          <p style="color: #666; font-size: 14px;">This code expires in 30 minutes.</p>
        </div>
        """
        await send_email(user.email, "LexiMaster - Verify Your Email", html)
    except Exception as e:
        logger.warning(f"Failed to send verification email to {user.email}: {e}")

    return UserResponse(**user_dict)


@api_router.post("/auth/login")
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
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")


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


@api_router.post("/auth/forgot-password")
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
      <h2 style="color: #1a1a1a; border-bottom: 3px solid #f59e0b; padding-bottom: 10px;">LexiMaster Password Reset</h2>
      <p>Your password reset code is:</p>
      <div style="background: #fef3c7; border: 3px solid #1a1a1a; padding: 20px; text-align: center; margin: 20px 0;">
        <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1a1a1a;">{code}</span>
      </div>
      <p style="color: #666; font-size: 14px;">This code expires in 15 minutes. If you did not request this, please ignore this email.</p>
    </div>
    """
    try:
        await send_email(email, "LexiMaster - Password Reset Code", html)
    except Exception as e:
        logger.error(f"Failed to send reset email: {e}")

    return {"message": "If an account exists with that email, a reset code has been sent."}


@api_router.post("/auth/reset-password")
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

@api_router.post("/auth/send-verification")
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
      <h2 style="color: #1a1a1a; border-bottom: 3px solid #f59e0b; padding-bottom: 10px;">Welcome to LexiMaster!</h2>
      <p>Hi {user['full_name']}, please verify your email with the code below:</p>
      <div style="background: #fef3c7; border: 3px solid #1a1a1a; padding: 20px; text-align: center; margin: 20px 0;">
        <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1a1a1a;">{code}</span>
      </div>
      <p style="color: #666; font-size: 14px;">This code expires in 30 minutes.</p>
    </div>
    """
    try:
        await send_email(user["email"], "LexiMaster - Verify Your Email", html)
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return {"message": "Verification code sent to your email"}


class VerifyEmailRequest(BaseModel):
    code: str


@api_router.post("/auth/verify-email")
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

@api_router.post("/auth/student-login")
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


@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user"""
    user = await db.users.find_one({"id": current_user["id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**user)


# ==================== STUDENT ROUTES ====================

@api_router.post("/students", response_model=Student)
async def create_student(
    student_data: StudentCreate,
    current_user: dict = Depends(get_current_guardian)
):
    """Create a new student"""
    # Check subscription limits
    subscription = await db.subscriptions.find_one({"guardian_id": student_data.guardian_id})
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if subscription["active_students"] >= subscription["student_seats"]:
        raise HTTPException(status_code=400, detail="Student seat limit reached")
    
    # Generate unique PIN and student code
    while True:
        from models import generate_pin, generate_student_code
        pin = generate_pin()
        student_code = generate_student_code()
        # Check PIN is unique
        existing_pin = await db.students.find_one({"access_pin": pin})
        # Check student code is unique
        existing_code = await db.students.find_one({"student_code": student_code})
        if not existing_pin and not existing_code:
            break
    
    # Calculate biological target
    biological_target = get_biological_target(student_data.age) if student_data.age else 0
    
    student = Student(
        **student_data.model_dump(),
        student_code=student_code,
        access_pin=pin,
        biological_target=biological_target
    )
    
    student_dict = student.model_dump()
    await db.students.insert_one(student_dict)
    
    # Update subscription active count
    await db.subscriptions.update_one(
        {"guardian_id": student_data.guardian_id},
        {"$inc": {"active_students": 1}}
    )
    
    return student


@api_router.get("/students", response_model=List[Student])
async def get_students(
    guardian_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get students (filtered by guardian if specified)"""
    query = {}
    if guardian_id:
        query["guardian_id"] = guardian_id
    
    students = await db.students.find(query).to_list(1000)
    return students


@api_router.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: str):
    """Get a specific student"""
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@api_router.patch("/students/{student_id}", response_model=Student)
async def update_student(
    student_id: str,
    update_data: StudentUpdate,
    current_user: dict = Depends(get_current_guardian)
):
    """Update student information"""
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    # If age is updated, recalculate biological target
    if "age" in update_dict:
        update_dict["biological_target"] = get_biological_target(update_dict["age"])
    
    result = await db.students.update_one(
        {"id": student_id},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    updated_student = await db.students.find_one({"id": student_id})
    return updated_student


@api_router.post("/students/{student_id}/reset-pin")
async def reset_student_pin(
    student_id: str,
    current_user: dict = Depends(get_current_guardian)
):
    """Reset a student's PIN to a new 9-digit PIN"""
    from models import generate_pin
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student["guardian_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    while True:
        new_pin = generate_pin()
        existing = await db.students.find_one({"access_pin": new_pin})
        if not existing:
            break
    await db.students.update_one({"id": student_id}, {"$set": {"access_pin": new_pin}})
    return {"message": "PIN reset successfully", "new_pin": new_pin}


@api_router.delete("/students/{student_id}")
async def delete_student(
    student_id: str,
    current_user: dict = Depends(get_current_guardian)
):
    """Delete a student"""
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Delete student
    await db.students.delete_one({"id": student_id})
    
    # Update subscription active count
    await db.subscriptions.update_one(
        {"guardian_id": student["guardian_id"]},
        {"$inc": {"active_students": -1}}
    )
    
    return {"message": "Student deleted successfully"}


# ==================== PROGRESS ROUTES ====================

@api_router.get("/students/{student_id}/progress")
async def get_student_progress(
    student_id: str,
    current_user: dict = Depends(get_current_guardian)
):
    """Get comprehensive progress data for a student"""
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student["guardian_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Narratives
    narratives = await db.narratives.find(
        {"student_id": student_id}, {"_id": 0, "id": 1, "title": 1, "status": 1, "total_word_count": 1, "created_date": 1, "chapters_completed": 1, "chapters": 1}
    ).sort("created_date", -1).to_list(100)
    narrative_summaries = []
    for n in narratives:
        narrative_summaries.append({
            "id": n["id"],
            "title": n.get("title", "Untitled"),
            "status": n.get("status", "unknown"),
            "total_word_count": n.get("total_word_count", 0),
            "chapters_total": len(n.get("chapters", [])),
            "chapters_completed": len(n.get("chapters_completed", [])),
            "created_date": n.get("created_date", ""),
        })

    # Assessments
    assessments = await db.assessments.find(
        {"student_id": student_id}, {"_id": 0, "id": 1, "type": 1, "total_questions": 1, "correct_count": 1, "accuracy_percentage": 1, "status": 1, "tokens_mastered": 1, "started_at": 1, "completed_at": 1}
    ).sort("started_at", -1).to_list(100)

    # Read logs
    read_logs = await db.read_logs.find(
        {"student_id": student_id}, {"_id": 0, "duration_seconds": 1, "words_read": 1, "wpm": 1, "created_date": 1, "tokens_encountered": 1}
    ).sort("created_date", -1).to_list(500)

    # Aggregate reading stats
    total_reading_seconds = sum(r.get("duration_seconds", 0) for r in read_logs)
    total_words_read = sum(r.get("words_read", 0) for r in read_logs)
    wpm_values = [r.get("wpm", 0) for r in read_logs if r.get("wpm", 0) > 0]
    avg_wpm = round(sum(wpm_values) / len(wpm_values), 1) if wpm_values else 0

    # Mastery stats
    mastered_tokens = student.get("mastered_tokens", [])
    biological_target = student.get("biological_target", 0)
    mastery_percentage = round((len(mastered_tokens) / biological_target * 100), 1) if biological_target > 0 else 0

    # Assessment accuracy over time
    assessment_history = []
    for a in assessments:
        if a.get("status") == "completed":
            assessment_history.append({
                "accuracy": a.get("accuracy_percentage", 0),
                "correct": a.get("correct_count", 0),
                "total": a.get("total_questions", 0),
                "tokens_mastered": len(a.get("tokens_mastered", [])),
                "date": str(a.get("completed_at") or a.get("started_at", "")),
            })

    # Assigned word banks info
    assigned_bank_ids = student.get("assigned_banks", [])
    assigned_banks = []
    if assigned_bank_ids:
        banks = await db.word_banks.find({"id": {"$in": assigned_bank_ids}}, {"_id": 0, "id": 1, "name": 1, "total_tokens": 1}).to_list(50)
        assigned_banks = banks

    return {
        "student": {
            "id": student["id"],
            "full_name": student["full_name"],
            "age": student.get("age"),
            "grade_level": student.get("grade_level"),
            "agentic_reach_score": student.get("agentic_reach_score", 0),
            "biological_target": biological_target,
            "virtues": student.get("virtues", []),
        },
        "reading_stats": {
            "total_reading_seconds": total_reading_seconds,
            "total_words_read": total_words_read,
            "average_wpm": avg_wpm,
            "sessions_count": len(read_logs),
        },
        "vocabulary": {
            "mastered_count": len(mastered_tokens),
            "biological_target": biological_target,
            "mastery_percentage": mastery_percentage,
            "recent_mastered": [t.get("token", "") for t in mastered_tokens[-10:]],
            "all_mastered": [t.get("token", "") for t in mastered_tokens],
        },
        "assessments": {
            "total": len(assessments),
            "completed": len([a for a in assessments if a.get("status") == "completed"]),
            "average_accuracy": round(sum(a.get("accuracy_percentage", 0) for a in assessments if a.get("status") == "completed") / max(1, len([a for a in assessments if a.get("status") == "completed"])), 1),
            "history": assessment_history,
        },
        "narratives": {
            "total": len(narratives),
            "completed": len([n for n in narratives if n.get("status") == "completed"]),
            "stories": narrative_summaries,
        },
        "assigned_banks": assigned_banks,
    }


@api_router.get("/students/{student_id}/export")
async def export_student_progress(
    student_id: str,
    format: str = "json",
    current_user: dict = Depends(get_current_guardian)
):
    """Export student progress as JSON or printable HTML"""
    # Reuse the progress data
    progress = await get_student_progress(student_id, current_user)
    report_date = datetime.now(timezone.utc).strftime("%B %d, %Y")

    if format == "json":
        return JSONResponse(
            content={"report_date": report_date, "exported_by": current_user.get("full_name", ""), **progress},
            headers={"Content-Disposition": f"attachment; filename=leximaster_{progress['student']['full_name'].replace(' ', '_')}_report.json"}
        )

    # HTML report
    s = progress["student"]
    r = progress["reading_stats"]
    v = progress["vocabulary"]
    a = progress["assessments"]
    n = progress["narratives"]
    banks = progress["assigned_banks"]

    hours = r["total_reading_seconds"] // 3600
    mins = (r["total_reading_seconds"] % 3600) // 60
    time_str = f"{hours}h {mins}m" if hours else f"{mins}m"

    mastered_words_html = "".join(f'<span class="tag mastered">{w}</span>' for w in v.get("all_mastered", [])) or '<p class="empty">No words mastered yet</p>'
    virtues_html = "".join(f'<span class="tag virtue">{vt}</span>' for vt in s.get("virtues", [])) or '<p class="empty">No virtues assigned</p>'
    banks_html = "".join(f'<tr><td>{b["name"]}</td><td>{b.get("total_tokens", 0)}</td></tr>' for b in banks) or '<tr><td colspan="2" class="empty">No word banks assigned</td></tr>'

    stories_html = ""
    for st in n["stories"]:
        date_str = str(st.get("created_date", ""))[:10]
        stories_html += f'<tr><td>{st["title"]}</td><td>{st["status"]}</td><td>{st["chapters_completed"]}/{st["chapters_total"]}</td><td>{st["total_word_count"]}</td><td>{date_str}</td></tr>'
    if not stories_html:
        stories_html = '<tr><td colspan="5" class="empty">No stories generated yet</td></tr>'

    assessments_html = ""
    for ah in a["history"]:
        date_str = str(ah.get("date", ""))[:10]
        assessments_html += f'<tr><td>{date_str}</td><td>{ah["correct"]}/{ah["total"]}</td><td>{ah["accuracy"]}%</td><td>{ah["tokens_mastered"]}</td></tr>'
    if not assessments_html:
        assessments_html = '<tr><td colspan="4" class="empty">No assessments completed yet</td></tr>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LexiMaster Report - {s["full_name"]}</title>
<style>
  @page {{ margin: 1in; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; color: #1a1a1a; line-height: 1.5; padding: 40px; max-width: 900px; margin: 0 auto; }}
  .header {{ border-bottom: 4px solid #000; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: flex-end; }}
  .header h1 {{ font-size: 28px; font-weight: 900; text-transform: uppercase; }}
  .header .meta {{ text-align: right; font-size: 13px; color: #666; }}
  .section {{ margin-bottom: 30px; }}
  .section h2 {{ font-size: 18px; font-weight: 800; text-transform: uppercase; border-bottom: 3px solid #000; padding-bottom: 6px; margin-bottom: 14px; }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
  .stat-box {{ border: 3px solid #000; padding: 14px; text-align: center; }}
  .stat-box .label {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: #666; }}
  .stat-box .value {{ font-size: 28px; font-weight: 900; margin: 4px 0; }}
  .stat-box .sub {{ font-size: 12px; color: #888; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ border: 2px solid #000; padding: 8px 12px; text-align: left; font-size: 14px; }}
  th {{ background: #f0f0f0; font-weight: 800; text-transform: uppercase; font-size: 12px; }}
  .tag {{ display: inline-block; border: 2px solid #000; padding: 4px 12px; margin: 3px; font-weight: 700; font-size: 13px; }}
  .tag.mastered {{ background: #d1fae5; }}
  .tag.virtue {{ background: #dbeafe; }}
  .empty {{ color: #999; font-style: italic; padding: 8px 0; }}
  .profile-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
  .profile-grid p {{ font-size: 14px; }}
  .profile-grid strong {{ font-weight: 700; }}
  @media print {{ body {{ padding: 0; }} .no-print {{ display: none; }} }}
  .print-btn {{ background: #6366f1; color: #fff; border: 3px solid #000; padding: 10px 24px; font-weight: 800; font-size: 14px; cursor: pointer; text-transform: uppercase; margin-bottom: 20px; }}
  .print-btn:hover {{ background: #4f46e5; }}
</style>
</head>
<body>
<button class="print-btn no-print" onclick="window.print()">Print / Save as PDF</button>
<div class="header">
  <div>
    <h1>LexiMaster Progress Report</h1>
    <p style="font-size:22px;font-weight:800;margin-top:6px;">{s["full_name"]}</p>
  </div>
  <div class="meta">
    <p>Report Date: {report_date}</p>
    <p>Generated by: {current_user.get("full_name", "Guardian")}</p>
  </div>
</div>

<div class="section">
  <h2>Student Profile</h2>
  <div class="profile-grid">
    <p><strong>Age:</strong> {s.get("age") or "N/A"}</p>
    <p><strong>Grade Level:</strong> {s.get("grade_level") or "N/A"}</p>
    <p><strong>Agentic Reach Score:</strong> {s.get("agentic_reach_score", 0)}</p>
    <p><strong>Biological Target:</strong> {s.get("biological_target", 0)} words</p>
  </div>
</div>

<div class="section">
  <h2>Overview</h2>
  <div class="stats-grid">
    <div class="stat-box"><div class="label">Words Mastered</div><div class="value">{v["mastered_count"]}</div><div class="sub">of {v["biological_target"]} target</div></div>
    <div class="stat-box"><div class="label">Reading Time</div><div class="value">{time_str}</div><div class="sub">{r["sessions_count"]} sessions</div></div>
    <div class="stat-box"><div class="label">Avg WPM</div><div class="value">{r["average_wpm"] or "—"}</div><div class="sub">{r["total_words_read"]} total words</div></div>
    <div class="stat-box"><div class="label">Assessments</div><div class="value">{a["completed"]}</div><div class="sub">{a["average_accuracy"]}% avg accuracy</div></div>
  </div>
</div>

<div class="section">
  <h2>Mastered Vocabulary ({v["mastered_count"]} words — {v["mastery_percentage"]}%)</h2>
  <div>{mastered_words_html}</div>
</div>

<div class="section">
  <h2>Character Education</h2>
  <div>{virtues_html}</div>
</div>

<div class="section">
  <h2>Assessment History</h2>
  <table>
    <thead><tr><th>Date</th><th>Score</th><th>Accuracy</th><th>Words Mastered</th></tr></thead>
    <tbody>{assessments_html}</tbody>
  </table>
</div>

<div class="section">
  <h2>Story History</h2>
  <table>
    <thead><tr><th>Title</th><th>Status</th><th>Chapters</th><th>Words</th><th>Date</th></tr></thead>
    <tbody>{stories_html}</tbody>
  </table>
</div>

<div class="section">
  <h2>Assigned Word Banks</h2>
  <table>
    <thead><tr><th>Name</th><th>Total Words</th></tr></thead>
    <tbody>{banks_html}</tbody>
  </table>
</div>

<div style="margin-top:40px;border-top:3px solid #000;padding-top:12px;font-size:12px;color:#888;text-align:center;">
  Generated by LexiMaster &middot; {report_date}
</div>
</body>
</html>"""

    return HTMLResponse(content=html)


# ==================== SUBSCRIPTION ROUTES ====================

@api_router.get("/subscriptions/{guardian_id}", response_model=Subscription)
async def get_subscription(
    guardian_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get guardian's subscription"""
    subscription = await db.subscriptions.find_one({"guardian_id": guardian_id})
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


# ==================== WORD BANK ROUTES ====================

@api_router.post("/word-banks", response_model=WordBank)
async def create_word_bank(
    bank_data: WordBankCreate,
    current_user: dict = Depends(get_current_admin)
):
    """Create a new word bank (admin only)"""
    total_tokens = len(bank_data.baseline_words) + len(bank_data.target_words) + len(bank_data.stretch_words)
    
    word_bank = WordBank(
        **bank_data.model_dump(),
        owner_id=current_user["id"],
        total_tokens=total_tokens
    )
    
    bank_dict = word_bank.model_dump()
    await db.word_banks.insert_one(bank_dict)
    
    return word_bank


@api_router.get("/word-banks", response_model=List[WordBank])
async def get_word_banks(
    visibility: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Get word banks with optional filters"""
    query = {}
    if visibility:
        query["visibility"] = visibility
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"specialty": {"$regex": search, "$options": "i"}}
        ]
    
    word_banks = await db.word_banks.find(query).to_list(1000)
    return word_banks


@api_router.get("/word-banks/{bank_id}", response_model=WordBank)
async def get_word_bank(bank_id: str):
    """Get a specific word bank"""
    word_bank = await db.word_banks.find_one({"id": bank_id})
    if not word_bank:
        raise HTTPException(status_code=404, detail="Word bank not found")
    return word_bank


class PurchaseRequest(BaseModel):
    guardian_id: str
    bank_id: str


@api_router.post("/word-banks/purchase")
async def purchase_word_bank(
    request: PurchaseRequest,
    current_user: dict = Depends(get_current_guardian)
):
    """Purchase a word bank (add to subscription)"""
    # Verify bank exists
    word_bank = await db.word_banks.find_one({"id": request.bank_id})
    if not word_bank:
        raise HTTPException(status_code=404, detail="Word bank not found")
    
    # Get subscription
    subscription = await db.subscriptions.find_one({"guardian_id": request.guardian_id})
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Check if already purchased
    if request.bank_id in subscription.get("bank_access", []):
        raise HTTPException(status_code=400, detail="Word bank already purchased")
    
    # Add to subscription (for now, free - can add payment later)
    await db.subscriptions.update_one(
        {"guardian_id": request.guardian_id},
        {"$push": {"bank_access": request.bank_id}}
    )
    
    # Increment purchase count
    await db.word_banks.update_one(
        {"id": request.bank_id},
        {"$inc": {"purchase_count": 1}}
    )
    
    return {"message": "Word bank purchased successfully", "bank_id": request.bank_id}


class AssignBanksRequest(BaseModel):
    student_id: str
    bank_ids: List[str]


@api_router.post("/students/assign-banks")
async def assign_word_banks(
    request: AssignBanksRequest,
    current_user: dict = Depends(get_current_guardian)
):
    """Assign word banks to a student"""
    # Verify student exists
    student = await db.students.find_one({"id": request.student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get guardian's subscription to verify access
    subscription = await db.subscriptions.find_one({"guardian_id": student["guardian_id"]})
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Verify guardian has access to all requested banks
    available_banks = subscription.get("bank_access", [])
    for bank_id in request.bank_ids:
        if bank_id not in available_banks:
            bank = await db.word_banks.find_one({"id": bank_id})
            # Allow global/free banks
            if not bank or bank.get("visibility") not in ["global", "marketplace"]:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Guardian does not have access to bank {bank_id}"
                )
    
    # Update student's assigned banks
    await db.students.update_one(
        {"id": request.student_id},
        {"$set": {"assigned_banks": request.bank_ids}}
    )
    
    updated_student = await db.students.find_one({"id": request.student_id}, {"_id": 0})
    return updated_student


# ==================== NARRATIVE ROUTES ====================

@api_router.post("/narratives")
async def create_narrative(narrative_data: NarrativeCreate):
    """Generate a new AI story for a student"""
    # Get student
    student = await db.students.find_one({"id": narrative_data.student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if student has assigned word banks
    if not student.get("assigned_banks"):
        raise HTTPException(
            status_code=400, 
            detail="Student has no assigned word banks. Please assign word banks first."
        )
    
    # Fetch word banks
    word_banks = []
    for bank_id in narrative_data.bank_ids:
        bank = await db.word_banks.find_one({"id": bank_id})
        if bank:
            word_banks.append(bank)
    
    if not word_banks:
        raise HTTPException(status_code=404, detail="No valid word banks found")
    
    # Collect vocabulary from all assigned banks
    all_baseline = []
    all_target = []
    all_stretch = []
    
    for bank in word_banks:
        all_baseline.extend(bank.get("baseline_words", []))
        all_target.extend(bank.get("target_words", []))
        all_stretch.extend(bank.get("stretch_words", []))
    
    # Shuffle and limit vocabulary (max 30 words total for story)
    random.shuffle(all_baseline)
    random.shuffle(all_target)
    random.shuffle(all_stretch)
    
    baseline_words = all_baseline[:18]  # 60% of 30
    target_words = all_target[:9]       # 30% of 30
    stretch_words = all_stretch[:3]     # 10% of 30
    
    # Generate story using AI
    try:
        # Ensure story service has db reference
        story_service.set_db(db)
        
        # Get guardian info for cost tracking
        guardian = await db.users.find_one({"id": student["guardian_id"]}, {"_id": 0, "full_name": 1})
        
        # Check for eligible brand placements
        brand_placements = []
        flags = await db.system_config.find_one({"key": "feature_flags"}, {"_id": 0})
        brand_enabled = True
        if flags and flags.get("value"):
            brand_enabled = flags["value"].get("brand_sponsorship_enabled", True)
        
        ad_prefs = student.get("ad_preferences", {})
        if brand_enabled and ad_prefs.get("allow_brand_stories", False):
            blocked = ad_prefs.get("blocked_categories", [])
            student_age = student.get("age", 10)
            active_brands = await db.brands.find({"is_active": True}, {"_id": 0}).to_list(20)
            for b in active_brands:
                if b.get("target_ages") and student_age not in b["target_ages"]:
                    continue
                if b.get("budget_total", 0) > 0 and b.get("budget_spent", 0) >= b.get("budget_total", 0):
                    continue
                brand_cats = b.get("target_categories", [])
                if any(c in blocked for c in brand_cats):
                    continue
                brand_placements.append({
                    "id": b["id"], "name": b["name"], "products": b.get("products", []),
                    "problem_statement": b.get("problem_statement", ""),
                    "logo_url": b.get("logo_url", ""),
                })
                if len(brand_placements) >= 2:
                    break
        
        story_data = await story_service.generate_story(
            student_name=student["full_name"],
            student_age=student.get("age", 10),
            grade_level=student.get("grade_level", "1-12"),
            interests=student.get("interests", []),
            virtues=student.get("virtues", []),
            prompt=narrative_data.prompt,
            baseline_words=baseline_words,
            target_words=target_words,
            stretch_words=stretch_words,
            student_id=student["id"],
            guardian_id=student.get("guardian_id", ""),
            guardian_name=guardian.get("full_name", "") if guardian else "",
            belief_system=student.get("belief_system", ""),
            cultural_context=student.get("cultural_context", ""),
            language=student.get("language", "English"),
            brand_placements=brand_placements,
        )
        
        # Record brand impressions
        if brand_placements:
            for bp in brand_placements:
                impression = BrandImpression(
                    brand_id=bp["id"], brand_name=bp["name"],
                    narrative_id="pending", student_id=student["id"],
                    guardian_id=student.get("guardian_id", ""),
                    products_featured=[p.get("name", "") for p in bp.get("products", [])],
                    cost=0.05,  # default cost per impression
                )
                await db.brand_impressions.insert_one(impression.model_dump())
                await db.brands.update_one(
                    {"id": bp["id"]},
                    {"$inc": {"total_impressions": 1, "total_stories": 1, "budget_spent": 0.05}}
                )
        
        # Create narrative object
        from models import Chapter, EmbeddedToken, VisionCheck
        
        valid_tiers = {"baseline", "target", "stretch"}
        chapters = []
        for ch_data in story_data.get("chapters", []):
            # Filter embedded tokens to only valid tiers
            tokens = []
            for token in ch_data.get("embedded_tokens", []):
                if isinstance(token, dict) and token.get("tier") in valid_tiers:
                    tokens.append(EmbeddedToken(**token))
            
            # Handle vision_check with defaults
            vc_data = ch_data.get("vision_check", {})
            if not vc_data or not vc_data.get("question"):
                vc_data = {"question": "What happened in this chapter?", "options": ["A", "B", "C", "D"], "correct_index": 0}
            
            chapter = Chapter(
                number=ch_data.get("number", len(chapters) + 1),
                title=ch_data.get("title", f"Chapter {len(chapters) + 1}"),
                content=ch_data.get("content", ""),
                word_count=ch_data.get("word_count", len(ch_data.get("content", "").split())),
                embedded_tokens=tokens,
                vision_check=VisionCheck(**vc_data)
            )
            chapters.append(chapter)
        
        # Collect all target and stretch words for verification
        tokens_to_verify = [w["word"] for w in target_words] + [w["word"] for w in stretch_words]
        
        narrative = Narrative(
            title=story_data["title"],
            student_id=narrative_data.student_id,
            bank_ids=narrative_data.bank_ids,
            theme=story_data.get("theme", narrative_data.prompt),
            chapters=chapters,
            total_word_count=story_data.get("total_word_count", 0),
            status=NarrativeStatus.READY,
            tokens_to_verify=tokens_to_verify
        )
        
        narrative_dict = narrative.model_dump()
        await db.narratives.insert_one(narrative_dict)
        
        return narrative
        
    except Exception as e:
        logger.error(f"Story generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")


@api_router.get("/narratives")
async def get_narratives(student_id: Optional[str] = None):
    """Get narratives, optionally filtered by student"""
    query = {}
    if student_id:
        query["student_id"] = student_id
    
    narratives = await db.narratives.find(query, {"_id": 0}).to_list(1000)
    return narratives


@api_router.get("/narratives/{narrative_id}")
async def get_narrative(narrative_id: str):
    """Get a specific narrative"""
    narrative = await db.narratives.find_one({"id": narrative_id}, {"_id": 0})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    return narrative


@api_router.delete("/narratives/{narrative_id}")
async def delete_narrative(narrative_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a narrative"""
    result = await db.narratives.delete_one({"id": narrative_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Narrative not found")
    return {"message": "Narrative deleted successfully"}


# ==================== READ LOG ROUTES ====================

class ReadLogCreate(BaseModel):
    student_id: str
    narrative_id: str
    chapter_number: int
    session_start: datetime
    session_end: datetime
    words_read: int


@api_router.post("/read-logs")
async def create_read_log(log_data: ReadLogCreate):
    """Create a reading session log"""
    from models import ReadLog
    
    # Calculate duration and WPM
    duration = (log_data.session_end - log_data.session_start).total_seconds()
    wpm = (log_data.words_read / (duration / 60)) if duration > 0 else 0
    
    read_log = ReadLog(
        student_id=log_data.student_id,
        narrative_id=log_data.narrative_id,
        chapter_number=log_data.chapter_number,
        session_start=log_data.session_start,
        session_end=log_data.session_end,
        duration_seconds=int(duration),
        words_read=log_data.words_read,
        wpm=round(wpm, 1)
    )
    
    log_dict = read_log.model_dump()
    await db.read_logs.insert_one(log_dict)
    
    # Update student statistics
    student = await db.students.find_one({"id": log_data.student_id})
    if student:
        new_total_seconds = student.get("total_reading_seconds", 0) + int(duration)
        new_total_words = student.get("total_words_read", 0) + log_data.words_read
        new_average_wpm = (new_total_words / (new_total_seconds / 60)) if new_total_seconds > 0 else 0
        
        await db.students.update_one(
            {"id": log_data.student_id},
            {
                "$set": {
                    "total_reading_seconds": new_total_seconds,
                    "total_words_read": new_total_words,
                    "average_wpm": round(new_average_wpm, 1)
                }
            }
        )
    
    return read_log


@api_router.get("/read-logs")
async def get_read_logs(student_id: Optional[str] = None):
    """Get read logs, optionally filtered by student"""
    query = {}
    if student_id:
        query["student_id"] = student_id
    
    logs = await db.read_logs.find(query, {"_id": 0}).to_list(1000)
    return logs


class WrittenAnswerEval(BaseModel):
    student_id: str
    chapter_number: int
    question: str
    student_answer: str
    chapter_summary: str = ""
    spelling_mode: str = "phonetic"  # "exact" or "phonetic"


@api_router.post("/assessments/evaluate-written")
async def evaluate_written_answer(data: WrittenAnswerEval):
    """Evaluate a written comprehension answer using AI"""
    from story_service import story_service
    story_service.set_db(db)
    llm_config = await story_service._get_llm_config()
    provider = llm_config.get("provider", "emergent")
    model = llm_config.get("model", "gpt-5.2")

    prompt = f"""Evaluate this student's written answer to a reading comprehension question.

Question: {data.question}
Student's Answer: {data.student_answer}
Chapter Context (first 500 chars): {data.chapter_summary}
Spelling Mode: {data.spelling_mode}

Evaluate:
1. Does the answer demonstrate understanding of the chapter content?
2. Is the answer relevant to the question?
3. {"Check for exact spelling. List any misspelled words." if data.spelling_mode == "exact" else "Accept phonetic/close spellings. Only note severely misspelled words."}

Return ONLY valid JSON:
{{
  "passed": true/false,
  "feedback": "brief encouraging feedback",
  "spelling_errors": [{{"written": "misspeled", "correct": "misspelled"}}],
  "comprehension_score": 0-100
}}"""

    try:
        if provider == "openrouter":
            from openai import AsyncOpenAI
            api_key = llm_config.get("openrouter_key") or os.environ.get("OPENROUTER_API_KEY")
            client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1", api_key=api_key,
                default_headers={"HTTP-Referer": "https://leximaster.app"},
                max_retries=1, timeout=30.0,
            )
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3, max_tokens=500,
            )
            text = response.choices[0].message.content or ""
        else:
            api_key = os.environ.get('EMERGENT_LLM_KEY')
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            chat = LlmChat(api_key=api_key, session_id=f"eval_{data.student_id}_{data.chapter_number}")
            chat.with_model("openai", model if provider == "emergent" else "gpt-5.2")
            text = await chat.send_message(UserMessage(text=prompt))

        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"): text = text[:-3]
            text = text.strip()

        result = json_lib.loads(text)

        # Log spelling errors for the student
        if result.get("spelling_errors"):
            await db.spelling_logs.insert_one({
                "student_id": data.student_id,
                "chapter_number": data.chapter_number,
                "errors": result["spelling_errors"],
                "answer_text": data.student_answer,
                "created_date": datetime.now(timezone.utc).isoformat(),
            })

        return result

    except Exception as e:
        logger.error(f"Written answer evaluation failed: {str(e)}")
        # Lenient fallback — pass if answer has enough words
        word_count = len(data.student_answer.split())
        return {
            "passed": word_count >= 5,
            "feedback": "Your answer was recorded. Keep reading!" if word_count >= 5 else "Please write a more complete answer.",
            "spelling_errors": [],
            "comprehension_score": 60 if word_count >= 5 else 30,
        }


# ==================== ADMIN SPELLING & LIMITS CONFIG ====================

@api_router.get("/admin/settings")
async def get_admin_settings(current_user: dict = Depends(get_current_user)):
    """Get admin settings (spelling, free limits, etc.)"""
    settings = await db.system_config.find_one({"key": "admin_settings"}, {"_id": 0})
    defaults = {
        "global_spellcheck_disabled": False,
        "global_spelling_mode": "phonetic",
        "free_account_story_limit": 5,
        "free_account_assessment_limit": 10,
    }
    return settings.get("value", defaults) if settings else defaults


class AdminSettingsUpdate(BaseModel):
    global_spellcheck_disabled: Optional[bool] = None
    global_spelling_mode: Optional[str] = None
    free_account_story_limit: Optional[int] = None
    free_account_assessment_limit: Optional[int] = None


@api_router.post("/admin/settings")
async def update_admin_settings(data: AdminSettingsUpdate, current_user: dict = Depends(get_current_user)):
    """Update admin settings"""
    current = await get_admin_settings(current_user)
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    current.update(updates)
    await db.system_config.update_one(
        {"key": "admin_settings"},
        {"$set": {"key": "admin_settings", "value": current, "updated_date": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return {"message": "Settings updated", "settings": current}


@api_router.post("/students/{student_id}/spellcheck")
async def update_student_spellcheck(
    student_id: str,
    current_user: dict = Depends(get_current_guardian)
):
    """Toggle spellcheck for a specific student"""
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student["guardian_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    current = student.get("spellcheck_disabled", False)
    await db.students.update_one(
        {"id": student_id},
        {"$set": {"spellcheck_disabled": not current}}
    )
    return {"spellcheck_disabled": not current}


@api_router.post("/students/{student_id}/spelling-mode")
async def update_student_spelling_mode(
    student_id: str,
    current_user: dict = Depends(get_current_guardian)
):
    """Toggle spelling mode between exact and phonetic for a student"""
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student["guardian_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    current = student.get("spelling_mode", "phonetic")
    new_mode = "exact" if current == "phonetic" else "phonetic"
    await db.students.update_one(
        {"id": student_id},
        {"$set": {"spelling_mode": new_mode}}
    )
    return {"spelling_mode": new_mode}


@api_router.get("/students/{student_id}/spelling-logs")
async def get_spelling_logs(
    student_id: str,
    current_user: dict = Depends(get_current_guardian)
):
    """Get spelling error logs for a student"""
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student["guardian_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    logs = await db.spelling_logs.find(
        {"student_id": student_id}, {"_id": 0}
    ).sort("created_date", -1).to_list(100)
    return logs


# ==================== ASSESSMENT ROUTES ====================

class AssessmentCreate(BaseModel):
    student_id: str
    narrative_id: str
    type: str = "token_verification"


@api_router.post("/assessments")
async def create_assessment(assessment_data: AssessmentCreate):
    """Create a vocabulary assessment for a completed narrative"""
    from models import Assessment, AssessmentQuestion, AssessmentType, QuestionType
    
    # Get narrative
    narrative = await db.narratives.find_one({"id": assessment_data.narrative_id})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    
    # Get words to test (target + stretch)
    tokens_to_verify = narrative.get("tokens_to_verify", [])
    
    if not tokens_to_verify:
        raise HTTPException(status_code=400, detail="No tokens to verify in this narrative")
    
    # Create questions for each token
    questions = []
    for word in tokens_to_verify:
        question = AssessmentQuestion(
            word=word,
            question_type=QuestionType.DEFINITION,
            prompt=f"Provide a definition for '{word}' and use it in a sentence.",
            correct_answer=""  # Will be filled from word bank
        )
        questions.append(question)
    
    assessment = Assessment(
        student_id=assessment_data.student_id,
        narrative_id=assessment_data.narrative_id,
        type=AssessmentType.TOKEN_VERIFICATION,
        questions=questions,
        total_questions=len(questions)
    )
    
    assessment_dict = assessment.model_dump()
    await db.assessments.insert_one(assessment_dict)
    
    return assessment


class AssessmentAnswer(BaseModel):
    word: str
    definition: str
    sentence: str


class AssessmentSubmission(BaseModel):
    answers: List[AssessmentAnswer]


@api_router.post("/assessments/{assessment_id}/evaluate")
async def evaluate_assessment(assessment_id: str, submission: AssessmentSubmission):
    """Evaluate student responses using LLM"""
    
    # Get assessment
    assessment = await db.assessments.find_one({"id": assessment_id})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Get narrative to find correct definitions
    narrative = await db.narratives.find_one({"id": assessment["narrative_id"]})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    
    # Get word banks to find correct definitions
    word_definitions = {}
    for bank_id in narrative.get("bank_ids", []):
        bank = await db.word_banks.find_one({"id": bank_id})
        if bank:
            for tier in ["baseline_words", "target_words", "stretch_words"]:
                for word_obj in bank.get(tier, []):
                    word_definitions[word_obj["word"]] = {
                        "definition": word_obj["definition"],
                        "example": word_obj["example_sentence"]
                    }
    
    # Prepare LLM evaluation
    try:
        from story_service import story_service
        story_service.set_db(db)
        llm_config = await story_service._get_llm_config()
        provider = llm_config.get("provider", "emergent")
        model = llm_config.get("model", "gpt-5.2")

        # Get student spelling settings
        student_record = await db.students.find_one({"id": assessment["student_id"]})
        spelling_mode = student_record.get("spelling_mode", "phonetic") if student_record else "phonetic"
        
        # Build evaluation prompt
        evaluation_requests = []
        for answer in submission.answers:
            correct_info = word_definitions.get(answer.word, {})
            evaluation_requests.append({
                "word": answer.word,
                "correct_definition": correct_info.get("definition", ""),
                "correct_example": correct_info.get("example", ""),
                "student_definition": answer.definition,
                "student_sentence": answer.sentence
            })
        
        prompt = f"""Evaluate these vocabulary responses from a student. For each word, determine if the student demonstrates understanding.

Evaluation Criteria:
- Definition: Does it capture the core meaning? (Allow for different wording)
- Sentence: Is the word used correctly in context?
- Spelling Mode: {spelling_mode} ({'Require exact spelling' if spelling_mode == 'exact' else 'Accept phonetic/close spellings'})
- Overall: If both are reasonable, mark as correct
- Track any spelling errors found

Words to evaluate:
{json_lib.dumps(evaluation_requests, indent=2)}

Return ONLY valid JSON (no markdown):
{{
  "results": [
    {{
      "word": "word",
      "definition_correct": true/false,
      "sentence_correct": true/false,
      "overall_correct": true/false,
      "feedback": "brief encouraging feedback",
      "spelling_errors": [{{"written": "misspeled", "correct": "misspelled"}}]
    }}
  ]
}}"""

        if provider == "openrouter":
            from openai import AsyncOpenAI
            api_key = llm_config.get("openrouter_key") or os.environ.get("OPENROUTER_API_KEY")
            client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1", api_key=api_key,
                default_headers={"HTTP-Referer": "https://leximaster.app"},
                max_retries=1, timeout=60.0,
            )
            response_obj = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3, max_tokens=4000,
            )
            response = response_obj.choices[0].message.content or ""
        else:
            api_key = os.environ.get('EMERGENT_LLM_KEY')
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            chat = LlmChat(
                api_key=api_key,
                session_id=f"assess_{assessment_id}",
                system_message="You are an educational assessment evaluator. Be encouraging but fair."
            )
            chat.with_model("openai", model if provider == "emergent" else "gpt-5.2")
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)

        # Parse response
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"): text = text[:-3]
            text = text.strip()

        evaluation = json_lib.loads(text)
        
        # Update assessment with results
        correct_count = sum(1 for r in evaluation["results"] if r["overall_correct"])
        accuracy = (correct_count / len(submission.answers)) * 100 if submission.answers else 0
        
        # Update questions with student answers and feedback
        updated_questions = []
        for i, answer in enumerate(submission.answers):
            result = evaluation["results"][i]
            question = assessment["questions"][i]
            question.update({
                "student_definition": answer.definition,
                "student_sentence": answer.sentence,
                "is_correct": result["overall_correct"],
                "feedback": result["feedback"]
            })
            updated_questions.append(question)
        
        # Determine mastered tokens (80%+ accuracy)
        tokens_mastered = [
            r["word"] for r in evaluation["results"] 
            if r["overall_correct"]
        ]
        
        # Update assessment
        await db.assessments.update_one(
            {"id": assessment_id},
            {
                "$set": {
                    "questions": updated_questions,
                    "correct_count": correct_count,
                    "accuracy_percentage": round(accuracy, 1),
                    "tokens_mastered": tokens_mastered,
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Update student mastered tokens if 80%+ accuracy
        if accuracy >= 80:
            student = await db.students.find_one({"id": assessment["student_id"]})
            if student:
                from models import MasteredToken
                
                existing_tokens = [t["token"] for t in student.get("mastered_tokens", [])]
                new_tokens = []
                
                for word in tokens_mastered:
                    if word not in existing_tokens:
                        new_tokens.append(MasteredToken(
                            token=word,
                            source_type="narrative",
                            source_id=assessment["narrative_id"],
                            mastered_date=datetime.now(timezone.utc)
                        ).model_dump())
                
                if new_tokens:
                    await db.students.update_one(
                        {"id": assessment["student_id"]},
                        {"$push": {"mastered_tokens": {"$each": new_tokens}}}
                    )
                    
                    # Recalculate agentic reach score
                    updated_student = await db.students.find_one({"id": assessment["student_id"]})
                    mastered_count = len(updated_student.get("mastered_tokens", []))
                    
                    # Simple formula: mastered_tokens * 0.5 + (accuracy * 0.3)
                    agentic_score = (mastered_count * 0.5) + (accuracy * 3)
                    
                    await db.students.update_one(
                        {"id": assessment["student_id"]},
                        {"$set": {"agentic_reach_score": round(agentic_score, 1)}}
                    )
        
        # Return updated assessment
        updated_assessment = await db.assessments.find_one({"id": assessment_id}, {"_id": 0})
        return updated_assessment
        
    except Exception as e:
        logger.error(f"Assessment evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@api_router.get("/assessments")
async def get_assessments(student_id: Optional[str] = None, narrative_id: Optional[str] = None):
    """Get assessments with optional filters"""
    query = {}
    if student_id:
        query["student_id"] = student_id
    if narrative_id:
        query["narrative_id"] = narrative_id
    
    assessments = await db.assessments.find(query, {"_id": 0}).to_list(1000)
    return assessments


@api_router.get("/assessments/{assessment_id}")
async def get_assessment(assessment_id: str):
    """Get a specific assessment"""
    assessment = await db.assessments.find_one({"id": assessment_id}, {"_id": 0})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


# ==================== CLASSROOM SESSION ROUTES (TEACHER) ====================

class CreateSessionRequest(BaseModel):
    title: str
    bank_ids: List[str] = []
    description: Optional[str] = None


@api_router.post("/classroom-sessions")
async def create_classroom_session(
    data: CreateSessionRequest,
    current_user: dict = Depends(get_current_teacher)
):
    """Create a new classroom session"""
    from models import generate_pin
    while True:
        code = generate_pin()[:6]  # 6-digit session code
        existing = await db.classroom_sessions.find_one({"session_code": code, "status": {"$ne": "completed"}})
        if not existing:
            break

    session = {
        "id": str(__import__('uuid').uuid4()),
        "teacher_id": current_user["id"],
        "title": data.title,
        "description": data.description or "",
        "session_code": code,
        "bank_ids": data.bank_ids,
        "status": "waiting",
        "participating_students": [],
        "created_date": datetime.now(timezone.utc).isoformat(),
    }
    await db.classroom_sessions.insert_one(session)
    session.pop("_id", None)
    return session


@api_router.get("/classroom-sessions")
async def list_classroom_sessions(
    current_user: dict = Depends(get_current_teacher)
):
    """List all sessions for the current teacher"""
    sessions = await db.classroom_sessions.find(
        {"teacher_id": current_user["id"]}, {"_id": 0}
    ).sort("created_date", -1).to_list(100)
    return sessions


@api_router.get("/classroom-sessions/{session_id}")
async def get_classroom_session(
    session_id: str,
    current_user: dict = Depends(get_current_teacher)
):
    """Get a specific classroom session"""
    session = await db.classroom_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["teacher_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return session


@api_router.post("/classroom-sessions/{session_id}/start")
async def start_classroom_session(
    session_id: str,
    current_user: dict = Depends(get_current_teacher)
):
    """Start a classroom session (change status to active)"""
    session = await db.classroom_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["teacher_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.classroom_sessions.update_one({"id": session_id}, {"$set": {"status": "active"}})
    return {"message": "Session started", "status": "active"}


@api_router.post("/classroom-sessions/{session_id}/end")
async def end_classroom_session(
    session_id: str,
    current_user: dict = Depends(get_current_teacher)
):
    """End a classroom session"""
    session = await db.classroom_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["teacher_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.classroom_sessions.update_one({"id": session_id}, {"$set": {"status": "completed"}})
    return {"message": "Session ended", "status": "completed"}


class JoinSessionRequest(BaseModel):
    session_code: str
    student_id: str


@api_router.post("/classroom-sessions/join")
async def join_classroom_session(data: JoinSessionRequest):
    """Student joins a classroom session via code"""
    session = await db.classroom_sessions.find_one(
        {"session_code": data.session_code, "status": {"$in": ["waiting", "active"]}},
        {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or already ended")

    # Check if already joined
    for p in session.get("participating_students", []):
        if p["student_id"] == data.student_id:
            return {"message": "Already joined", "session_id": session["id"], "title": session["title"]}

    student = await db.students.find_one({"id": data.student_id}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    participant = {
        "student_id": data.student_id,
        "student_name": student["full_name"],
        "joined_at": datetime.now(timezone.utc).isoformat(),
        "progress": {}
    }
    await db.classroom_sessions.update_one(
        {"id": session["id"]},
        {"$push": {"participating_students": participant}}
    )
    # Broadcast real-time update to teacher's WebSocket
    await ws_manager.broadcast(session["id"], {
        "type": "student_joined",
        "student_name": student["full_name"],
        "student_id": data.student_id,
        "joined_at": participant["joined_at"],
        "total_students": len(session.get("participating_students", [])) + 1,
    })
    return {"message": "Joined session", "session_id": session["id"], "title": session["title"]}


@api_router.get("/classroom-sessions/{session_id}/analytics")
async def get_session_analytics(
    session_id: str,
    current_user: dict = Depends(get_current_teacher)
):
    """Get analytics for a classroom session"""
    session = await db.classroom_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["teacher_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    student_ids = [p["student_id"] for p in session.get("participating_students", [])]
    if not student_ids:
        return {
            "session": {"id": session["id"], "title": session.get("title", ""), "status": session["status"], "student_count": 0},
            "students": [],
            "class_summary": {"avg_accuracy": 0, "total_assessments": 0, "total_words_mastered": 0, "avg_reading_time": 0},
        }

    students_data = []
    total_accuracy = 0
    total_assessments = 0
    total_mastered = 0
    total_reading = 0

    for sid in student_ids:
        student = await db.students.find_one({"id": sid}, {"_id": 0, "id": 1, "full_name": 1, "mastered_tokens": 1, "agentic_reach_score": 1})
        if not student:
            continue

        assessments = await db.assessments.find({"student_id": sid, "status": "completed"}, {"_id": 0, "accuracy_percentage": 1}).to_list(100)
        read_logs = await db.read_logs.find({"student_id": sid}, {"_id": 0, "duration_seconds": 1}).to_list(500)

        mastered = len(student.get("mastered_tokens", []))
        avg_acc = round(sum(a.get("accuracy_percentage", 0) for a in assessments) / max(1, len(assessments)), 1) if assessments else 0
        reading_time = sum(r.get("duration_seconds", 0) for r in read_logs)

        students_data.append({
            "id": sid,
            "name": student["full_name"],
            "words_mastered": mastered,
            "assessments_completed": len(assessments),
            "avg_accuracy": avg_acc,
            "reading_seconds": reading_time,
            "score": student.get("agentic_reach_score", 0),
        })

        total_accuracy += avg_acc
        total_assessments += len(assessments)
        total_mastered += mastered
        total_reading += reading_time

    n = len(students_data) or 1
    return {
        "session": {
            "id": session["id"],
            "title": session.get("title", ""),
            "status": session["status"],
            "session_code": session["session_code"],
            "student_count": len(students_data),
            "created_date": session.get("created_date", ""),
        },
        "students": sorted(students_data, key=lambda x: x["words_mastered"], reverse=True),
        "class_summary": {
            "avg_accuracy": round(total_accuracy / n, 1),
            "total_assessments": total_assessments,
            "total_words_mastered": total_mastered,
            "avg_reading_seconds": round(total_reading / n),
        },
    }


# ==================== WEBSOCKET ROUTES ====================

@app.websocket("/ws/session/{session_id}")
async def websocket_session(websocket: WebSocket, session_id: str):
    """WebSocket for real-time session updates"""
    await ws_manager.connect(websocket, session_id)
    try:
        while True:
            await websocket.receive_text()  # Keep alive
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, session_id)


# ==================== ADMIN ROUTES ====================

@api_router.get("/admin/costs")
async def get_admin_costs(current_user: dict = Depends(get_current_user)):
    """Get cost tracking data for admin"""
    if current_user.get("role") not in ["admin", "guardian", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get all cost logs
    cost_logs = await db.cost_logs.find({}, {"_id": 0}).sort("created_date", -1).to_list(500)

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

    return {
        "total_cost": round(total_cost, 4),
        "total_stories": len(cost_logs),
        "per_user": sorted(user_costs.values(), key=lambda x: x["total_cost"], reverse=True),
        "per_model": sorted(model_costs.values(), key=lambda x: x["total_cost"], reverse=True),
        "recent_logs": cost_logs[:50],
    }


@api_router.get("/admin/models")
async def get_available_models(current_user: dict = Depends(get_current_user)):
    """Get list of configured LLM models"""
    config = await db.system_config.find_one({"key": "llm_config"}, {"_id": 0})
    default_config = {
        "provider": "emergent",
        "model": "gpt-5.2",
        "fallback_provider": None,
        "fallback_model": None,
        "openrouter_key": None,
    }
    return config.get("value", default_config) if config else default_config


class LLMConfigUpdate(BaseModel):
    provider: str  # "emergent" | "openrouter"
    model: str
    openrouter_key: Optional[str] = None


@api_router.post("/admin/models")
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


@api_router.get("/wallet/balance")
async def get_wallet_balance(current_user: dict = Depends(get_current_user)):
    """Get user's wallet balance"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "wallet_balance": 1})
    balance = user.get("wallet_balance", 0.0) if user else 0.0
    return {"balance": round(balance, 2)}


@api_router.get("/wallet/transactions")
async def get_wallet_transactions(current_user: dict = Depends(get_current_user)):
    """Get wallet transaction history"""
    transactions = await db.wallet_transactions.find(
        {"user_id": current_user["id"]}, {"_id": 0}
    ).sort("created_date", -1).to_list(100)
    return transactions


@api_router.get("/wallet/packages")
async def get_topup_packages():
    """Get available top-up packages"""
    return [{"id": k, "amount": v} for k, v in TOPUP_PACKAGES.items()]


class TopupRequest(BaseModel):
    package_id: str
    origin_url: str


@api_router.post("/wallet/topup")
async def create_wallet_topup(data: TopupRequest, request: Request, current_user: dict = Depends(get_current_user)):
    """Create a Stripe checkout session for wallet top-up"""
    if data.package_id not in TOPUP_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")

    amount = TOPUP_PACKAGES[data.package_id]
    origin = data.origin_url.rstrip("/")

    stripe_key = os.environ.get("STRIPE_API_KEY")
    if not stripe_key:
        raise HTTPException(status_code=500, detail="Payment system not configured")

    from emergentintegrations.payments.stripe.checkout import (
        StripeCheckout, CheckoutSessionRequest,
    )

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


@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    """Check payment status and credit wallet if paid"""
    txn = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Payment not found")

    if txn.get("payment_status") == "paid":
        return {"status": txn["status"], "payment_status": "paid", "amount": txn["amount"]}

    stripe_key = os.environ.get("STRIPE_API_KEY")
    from emergentintegrations.payments.stripe.checkout import StripeCheckout

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

@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    body = await request.body()
    sig = request.headers.get("Stripe-Signature")
    stripe_key = os.environ.get("STRIPE_API_KEY")

    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
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

@api_router.post("/wallet/purchase-bank")
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


@api_router.post("/admin/coupons")
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


@api_router.get("/admin/coupons")
async def list_coupons(current_user: dict = Depends(get_current_user)):
    """List all coupons"""
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

    coupons = await db.coupons.find({}, {"_id": 0}).sort("created_date", -1).to_list(200)
    return coupons


@api_router.delete("/admin/coupons/{coupon_id}")
async def delete_coupon(coupon_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a coupon"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.coupons.delete_one({"id": coupon_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return {"message": "Coupon deleted"}


class RedeemCouponRequest(BaseModel):
    code: str


@api_router.post("/coupons/redeem")
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


@api_router.get("/brand-portal/coupons")
async def list_brand_coupons(current_user: dict = Depends(get_current_brand_partner)):
    """List coupons created by this brand"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id", "")
    coupons = await db.coupons.find(
        {"created_by_brand_id": brand_id}, {"_id": 0}
    ).sort("created_date", -1).to_list(100)
    return coupons


@api_router.post("/brand-portal/coupons")
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


@api_router.delete("/brand-portal/coupons/{coupon_id}")
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


@api_router.post("/admin/users/{user_id}/add-credits")
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


@api_router.post("/admin/delegate")
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


@api_router.get("/admin/users")
async def list_all_users(current_user: dict = Depends(get_current_user)):
    """List all users (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    users = await db.users.find(
        {}, {"_id": 0, "password_hash": 0}
    ).sort("created_date", -1).to_list(500)
    return users



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


@api_router.post("/admin/users")
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


@api_router.put("/admin/users/{user_id}")
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


@api_router.post("/admin/users/{user_id}/reset-password")
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


@api_router.post("/admin/users/{user_id}/deactivate")
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


@api_router.delete("/admin/users/{user_id}")
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


@api_router.post("/admin/plans")
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


@api_router.get("/admin/plans")
async def list_plans(current_user: dict = Depends(get_current_user)):
    """List subscription plans"""
    plans = await db.subscription_plans.find({}, {"_id": 0}).sort("created_date", -1).to_list(50)
    return plans


@api_router.delete("/admin/plans/{plan_id}")
async def delete_plan(plan_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a subscription plan"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.subscription_plans.delete_one({"id": plan_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan deleted"}


# ==================== COMPREHENSIVE ADMIN STATISTICS ====================

@api_router.get("/admin/stats")
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

@api_router.post("/admin/word-banks")
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


@api_router.post("/words/define")
async def define_word(data: DefineWordRequest, current_user: dict = Depends(get_current_user)):
    """Get AI-powered definition for a word"""
    from story_service import story_service
    
    llm_config = await story_service._get_llm_config()
    provider = llm_config.get("provider", "emergent")
    model = llm_config.get("model", "gpt-5.2")
    
    if provider == "openrouter":
        api_key = llm_config.get("openrouter_key") or os.environ.get("OPENROUTER_API_KEY")
    else:
        api_key = os.environ.get("EMERGENT_LLM_KEY")
    
    prompt = f"""Define the word "{data.word}" for a student learning vocabulary.
{f'The word appears in this context: "{data.context}"' if data.context else ''}

Return ONLY valid JSON:
{{"word": "{data.word}", "definition": "clear simple definition", "part_of_speech": "noun/verb/adj/etc", "example_sentence": "example usage", "pronunciation_hint": "how to say it", "synonyms": ["syn1", "syn2"]}}"""

    try:
        if provider == "openrouter":
            from openai import AsyncOpenAI
            client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key, timeout=30.0)
            resp = await client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}], max_tokens=500, temperature=0.3,
            )
            text = resp.choices[0].message.content or ""
        else:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            chat = LlmChat(api_key=api_key, session_id=f"define_{data.word}", system_message="You are a vocabulary dictionary assistant. Return only valid JSON.")
            chat.with_model("openai", model)
            text = await chat.send_message(UserMessage(text=prompt))
        
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

@api_router.get("/referrals/my-code")
async def get_my_referral_code(current_user: dict = Depends(get_current_user)):
    """Get current user's referral code"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "referral_code": 1})
    code = user.get("referral_code", "") if user else ""
    if not code:
        code = generate_referral_code()
        await db.users.update_one({"id": current_user["id"]}, {"$set": {"referral_code": code}})
    return {"referral_code": code}


@api_router.get("/referrals/my-referrals")
async def get_my_referrals(current_user: dict = Depends(get_current_user)):
    """Get list of users I've referred"""
    referrals = await db.referrals.find(
        {"referrer_id": current_user["id"]}, {"_id": 0}
    ).sort("created_date", -1).to_list(100)
    
    for ref in referrals:
        referred_user = await db.users.find_one({"id": ref["referred_id"]}, {"_id": 0, "full_name": 1, "email": 1})
        if referred_user:
            ref["referred_name"] = referred_user.get("full_name", "Unknown")
    
    return referrals


# ==================== DONATION / SPONSOR A READER ====================

class DonationRequest(BaseModel):
    amount: float
    message: str = ""
    origin_url: str


@api_router.post("/donations/create")
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
    
    stripe_key = os.environ.get("STRIPE_API_KEY")
    if not stripe_key:
        raise HTTPException(status_code=500, detail="Payment not configured")
    
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
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


@api_router.get("/donations/status/{session_id}")
async def get_donation_status(session_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    """Check donation payment status"""
    donation = await db.donations.find_one({"payment_session_id": session_id}, {"_id": 0})
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    
    if donation.get("payment_status") == "paid":
        return {"status": "paid", "amount": donation["amount"], "stories_funded": donation["stories_funded"]}
    
    stripe_key = os.environ.get("STRIPE_API_KEY")
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
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


@api_router.get("/donations/stats")
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


# ==================== ADMIN BILLING/ROI CONFIG ====================

@api_router.get("/admin/billing-config")
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


@api_router.post("/admin/billing-config")
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

@api_router.get("/admin/feature-flags")
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


@api_router.post("/admin/feature-flags")
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


# ==================== BRAND MANAGEMENT (ADMIN) ====================

class BrandCreate(BaseModel):
    name: str
    logo_url: str = ""
    website: str = ""
    description: str = ""
    products: list = []
    target_ages: list = []
    target_categories: list = []
    budget_total: float = 0.0
    cost_per_impression: float = 0.05


@api_router.post("/admin/brands")
async def create_brand(data: BrandCreate, current_user: dict = Depends(get_current_user)):
    """Create a brand sponsor"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    brand = Brand(
        name=data.name, logo_url=data.logo_url, website=data.website,
        description=data.description,
        products=[BrandProduct(**p) if isinstance(p, dict) else p for p in data.products],
        target_ages=data.target_ages, target_categories=data.target_categories,
        budget_total=data.budget_total, cost_per_impression=data.cost_per_impression,
        created_by=current_user["id"],
    )
    await db.brands.insert_one(brand.model_dump())
    result = brand.model_dump()
    return result


@api_router.get("/admin/brands")
async def list_brands(current_user: dict = Depends(get_current_user)):
    """List all brands"""
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
    brands = await db.brands.find({}, {"_id": 0}).sort("created_date", -1).to_list(100)
    return brands


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    products: Optional[list] = None
    target_ages: Optional[list] = None
    target_categories: Optional[list] = None
    budget_total: Optional[float] = None
    cost_per_impression: Optional[float] = None
    is_active: Optional[bool] = None


@api_router.put("/admin/brands/{brand_id}")
async def update_brand(brand_id: str, data: BrandUpdate, current_user: dict = Depends(get_current_user)):
    """Update a brand"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await db.brands.update_one({"id": brand_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {"message": "Brand updated"}


@api_router.delete("/admin/brands/{brand_id}")
async def delete_brand(brand_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a brand"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.brands.delete_one({"id": brand_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {"message": "Brand deleted"}


# ==================== BRAND ANALYTICS ====================

@api_router.get("/admin/brand-analytics")
async def get_brand_analytics(current_user: dict = Depends(get_current_user)):
    """Get brand sponsorship analytics"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    brands = await db.brands.find({}, {"_id": 0}).to_list(100)

    # Aggregate impressions per brand
    pipeline = [
        {"$group": {
            "_id": "$brand_id",
            "total_impressions": {"$sum": 1},
            "total_cost": {"$sum": "$cost"},
            "products_featured": {"$push": "$products_featured"},
        }}
    ]
    impressions_agg = await db.brand_impressions.aggregate(pipeline).to_list(100)
    impressions_map = {a["_id"]: a for a in impressions_agg}

    # Total revenue from sponsorships
    total_pipeline = [{"$group": {"_id": None, "total": {"$sum": "$cost"}, "count": {"$sum": 1}}}]
    total_agg = await db.brand_impressions.aggregate(total_pipeline).to_list(1)
    total_revenue = total_agg[0]["total"] if total_agg else 0
    total_impressions = total_agg[0]["count"] if total_agg else 0

    # Classroom sponsorships
    active_sponsorships = await db.classroom_sponsorships.count_documents({"is_active": True})
    total_sponsorship_amount = 0
    sponsorship_pipeline = [{"$match": {"is_active": True}}, {"$group": {"_id": None, "total": {"$sum": "$amount_paid"}}}]
    sp_agg = await db.classroom_sponsorships.aggregate(sponsorship_pipeline).to_list(1)
    total_sponsorship_amount = sp_agg[0]["total"] if sp_agg else 0

    brand_details = []
    for b in brands:
        imp = impressions_map.get(b["id"], {})
        brand_details.append({
            "id": b["id"], "name": b["name"], "is_active": b.get("is_active", True),
            "budget_total": b.get("budget_total", 0),
            "budget_spent": imp.get("total_cost", 0),
            "impressions": imp.get("total_impressions", 0),
            "cost_per_impression": b.get("cost_per_impression", 0.05),
            "budget_remaining": b.get("budget_total", 0) - imp.get("total_cost", 0),
        })

    return {
        "total_brand_revenue": round(total_revenue, 2),
        "total_impressions": total_impressions,
        "active_brands": sum(1 for b in brands if b.get("is_active")),
        "total_brands": len(brands),
        "active_classroom_sponsorships": active_sponsorships,
        "total_sponsorship_amount": round(total_sponsorship_amount, 2),
        "brands": brand_details,
    }


# ==================== CLASSROOM SPONSORSHIP ====================

class ClassroomSponsorshipCreate(BaseModel):
    brand_id: str
    classroom_session_id: Optional[str] = None
    teacher_id: Optional[str] = None
    school_name: str = ""
    stories_limit: int = -1
    amount_paid: float = 0.0


@api_router.post("/admin/classroom-sponsorships")
async def create_classroom_sponsorship(data: ClassroomSponsorshipCreate, current_user: dict = Depends(get_current_user)):
    """Create a classroom sponsorship"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    brand = await db.brands.find_one({"id": data.brand_id}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    sponsorship = ClassroomSponsorship(
        brand_id=data.brand_id, brand_name=brand["name"],
        classroom_session_id=data.classroom_session_id, teacher_id=data.teacher_id,
        school_name=data.school_name, stories_limit=data.stories_limit,
        amount_paid=data.amount_paid, badge_text=f"Sponsored by {brand['name']}",
    )
    await db.classroom_sponsorships.insert_one(sponsorship.model_dump())
    return sponsorship.model_dump()


@api_router.get("/admin/classroom-sponsorships")
async def list_classroom_sponsorships(current_user: dict = Depends(get_current_user)):
    """List all classroom sponsorships"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    sponsorships = await db.classroom_sponsorships.find({}, {"_id": 0}).sort("created_date", -1).to_list(100)
    return sponsorships


@api_router.delete("/admin/classroom-sponsorships/{sp_id}")
async def delete_classroom_sponsorship(sp_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a classroom sponsorship"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.classroom_sponsorships.delete_one({"id": sp_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Sponsorship deleted"}


# ==================== GUARDIAN AD PREFERENCES ====================

class AdPreferencesUpdate(BaseModel):
    allow_brand_stories: bool = False
    preferred_categories: List[str] = []
    blocked_categories: List[str] = []


@api_router.get("/students/{student_id}/ad-preferences")
async def get_ad_preferences(student_id: str, current_user: dict = Depends(get_current_guardian)):
    """Get a student's ad preferences"""
    student = await db.students.find_one(
        {"id": student_id, "guardian_id": current_user["id"]}, {"_id": 0, "ad_preferences": 1}
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student.get("ad_preferences", {"allow_brand_stories": False, "preferred_categories": [], "blocked_categories": []})


@api_router.post("/students/{student_id}/ad-preferences")
async def update_ad_preferences(student_id: str, data: AdPreferencesUpdate, current_user: dict = Depends(get_current_guardian)):
    """Update a student's ad preferences"""
    result = await db.students.update_one(
        {"id": student_id, "guardian_id": current_user["id"]},
        {"$set": {"ad_preferences": data.model_dump()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Ad preferences updated", **data.model_dump()}


# ==================== BRAND STORY INTEGRATION ====================

@api_router.get("/brands/active-for-student/{student_id}")
async def get_active_brands_for_student(student_id: str, current_user: dict = Depends(get_current_user)):
    """Get brands eligible for a student's stories (checks preferences + feature flags)"""
    # Check feature flag
    flags = await db.system_config.find_one({"key": "feature_flags"}, {"_id": 0})
    brand_enabled = True
    if flags and flags.get("value"):
        brand_enabled = flags["value"].get("brand_sponsorship_enabled", True)
    if not brand_enabled:
        return {"brands": [], "reason": "Brand sponsorship is disabled system-wide"}

    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        return {"brands": [], "reason": "Student not found"}

    ad_prefs = student.get("ad_preferences", {})
    if not ad_prefs.get("allow_brand_stories", False):
        return {"brands": [], "reason": "Guardian has not opted in to brand stories"}

    preferred = ad_prefs.get("preferred_categories", [])
    blocked = ad_prefs.get("blocked_categories", [])
    student_age = student.get("age", 10)

    query = {"is_active": True}
    brands = await db.brands.find(query, {"_id": 0}).to_list(50)

    eligible = []
    for b in brands:
        # Check age targeting
        if b.get("target_ages") and student_age not in b["target_ages"]:
            continue
        # Check budget remaining
        if b.get("budget_total", 0) > 0 and b.get("budget_spent", 0) >= b.get("budget_total", 0):
            continue
        # Check blocked categories
        brand_cats = b.get("target_categories", [])
        if any(c in blocked for c in brand_cats):
            continue
        # Prefer brands matching preferred categories
        eligible.append({
            "id": b["id"], "name": b["name"],
            "products": b.get("products", []),
            "categories": brand_cats,
        })

    return {"brands": eligible}


# ==================== BRAND PARTNER PORTAL ====================

@api_router.get("/brand-portal/profile")
async def get_brand_partner_profile(current_user: dict = Depends(get_current_brand_partner)):
    """Get brand partner profile with linked brand info. Auto-creates brand if none linked."""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    brand = None
    if user.get("linked_brand_id"):
        brand = await db.brands.find_one({"id": user["linked_brand_id"]}, {"_id": 0})

    # Auto-create a brand if none linked yet
    if not brand:
        new_brand = Brand(
            name=user.get("full_name", "My Brand"),
            created_by=user["id"],
        )
        await db.brands.insert_one(new_brand.model_dump())
        await db.users.update_one({"id": user["id"]}, {"$set": {"linked_brand_id": new_brand.id}})
        brand = new_brand.model_dump()

    return {
        "user": {
            "id": user["id"], "email": user["email"], "full_name": user["full_name"],
            "wallet_balance": user.get("wallet_balance", 0.0),
            "brand_approved": user.get("brand_approved", False),
        },
        "brand": brand,
    }



# ==================== BRAND PORTAL: PROFILE UPDATE ====================

class BrandProfileUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    problem_statement: Optional[str] = None
    target_categories: Optional[list] = None
    target_ages: Optional[list] = None
    target_regions: Optional[list] = None
    target_languages: Optional[list] = None
    onboarding_completed: Optional[bool] = None


@api_router.put("/brand-portal/profile")
async def update_brand_profile(data: BrandProfileUpdate, current_user: dict = Depends(get_current_brand_partner)):
    """Update brand profile (problem statement, targeting, etc.)"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked to your account")

    update_data = {}
    for k, v in data.model_dump().items():
        if v is not None:
            if k == "target_regions":
                update_data[k] = [TargetRegion(**r).model_dump() if isinstance(r, dict) else r for r in v]
            else:
                update_data[k] = v

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.brands.update_one({"id": brand_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Brand not found")

    updated_brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    return updated_brand


# ==================== BRAND PORTAL: LOGO UPLOAD ====================

from fastapi import UploadFile, File

# Ensure uploads directory exists
UPLOAD_DIR = Path(__file__).parent / "uploads" / "logos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_LOGO_SIZE = 10 * 1024 * 1024  # 10MB


@api_router.post("/brand-portal/logo-upload")
async def upload_brand_logo(file: UploadFile = File(...), current_user: dict = Depends(get_current_brand_partner)):
    """Upload brand logo (max 10MB, images only)"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked to your account")

    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/svg+xml"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: PNG, JPG, WebP, SVG")

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_LOGO_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")

    # Save file
    import uuid as _uuid
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"{brand_id}_{_uuid.uuid4().hex[:8]}.{ext}"
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        f.write(contents)

    logo_url = f"/api/uploads/logos/{filename}"
    await db.brands.update_one({"id": brand_id}, {"$set": {"logo_url": logo_url}})

    return {"logo_url": logo_url, "filename": filename}


# ==================== BRAND PORTAL: PRODUCT CRUD ====================

class ProductCreate(BaseModel):
    name: str
    description: str = ""
    category: str = ""


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


@api_router.get("/brand-portal/products")
async def list_brand_products(current_user: dict = Depends(get_current_brand_partner)):
    """List all products for the brand"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        return []
    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    return brand.get("products", []) if brand else []


@api_router.post("/brand-portal/products")
async def add_brand_product(data: ProductCreate, current_user: dict = Depends(get_current_brand_partner)):
    """Add a product to the brand"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")

    product = BrandProduct(name=data.name, description=data.description, category=data.category)
    await db.brands.update_one({"id": brand_id}, {"$push": {"products": product.model_dump()}})

    return product.model_dump()


@api_router.put("/brand-portal/products/{product_id}")
async def update_brand_product(product_id: str, data: ProductUpdate, current_user: dict = Depends(get_current_brand_partner)):
    """Update a specific product"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")

    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    products = brand.get("products", [])
    updated = False
    for p in products:
        if p.get("id") == product_id:
            if data.name is not None:
                p["name"] = data.name
            if data.description is not None:
                p["description"] = data.description
            if data.category is not None:
                p["category"] = data.category
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.brands.update_one({"id": brand_id}, {"$set": {"products": products}})
    return {"message": "Product updated"}


@api_router.delete("/brand-portal/products/{product_id}")
async def delete_brand_product(product_id: str, current_user: dict = Depends(get_current_brand_partner)):
    """Delete a product from the brand"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")

    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    products = [p for p in brand.get("products", []) if p.get("id") != product_id]
    await db.brands.update_one({"id": brand_id}, {"$set": {"products": products}})
    return {"message": "Product deleted"}


# ==================== BRAND PORTAL: STORY PREVIEW ====================

@api_router.get("/brand-portal/story-preview")
async def get_story_preview(current_user: dict = Depends(get_current_brand_partner)):
    """Get cached story preview for the brand"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")
    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {
        "preview": brand.get("story_preview", ""),
        "generated_at": brand.get("story_preview_generated_at"),
    }


@api_router.post("/brand-portal/story-preview")
async def generate_story_preview(current_user: dict = Depends(get_current_brand_partner)):
    """Generate a short AI story snippet showcasing how the brand is woven into a story"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")
    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_name = brand.get("name", "Brand")
    problem = brand.get("problem_statement", "")
    products = brand.get("products", [])
    prod_names = [p.get("name", "") for p in products if p.get("name")]

    if not problem and not prod_names:
        raise HTTPException(status_code=400, detail="Please add a problem statement or products first")

    # Build the prompt
    prod_text = f"Products: {', '.join(prod_names)}" if prod_names else ""
    problem_text = f"Problem they solve: {problem}" if problem else ""

    prompt = f"""Write a short educational story snippet (about 150-200 words, one scene) for children aged 8-12.
The story should naturally feature the brand "{brand_name}" as a helpful solution.
{problem_text}
{prod_text}

Requirements:
- The brand mention must feel organic, not like an advertisement
- Show how the brand/product helps a child character solve a real problem
- Keep it engaging, warm, and educational
- Write it as a single cohesive paragraph/scene
- Do NOT include any JSON formatting, just the story text"""

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import time as _time
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")

        story_service.set_db(db)
        llm_config = await story_service._get_llm_config()
        provider = llm_config.get("provider", "emergent")
        model = llm_config.get("model", "gpt-5.2")

        if provider == "openrouter":
            openrouter_key = llm_config.get("openrouter_key") or os.environ.get("OPENROUTER_API_KEY")
            if not openrouter_key:
                raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
            # OpenRouter path - use direct API
            import httpx
            headers = {"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"}
            body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
            async with httpx.AsyncClient(timeout=60) as client_http:
                resp = await client_http.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=headers)
                resp.raise_for_status()
                preview_text = resp.json()["choices"][0]["message"]["content"].strip()
        else:
            chat = LlmChat(
                api_key=api_key,
                session_id=f"brand_preview_{brand_id}_{int(_time.time())}",
                system_message="You are an expert educational story writer for children."
            )
            chat.with_model("openai", model)
            message = UserMessage(text=prompt)
            preview_text = await chat.send_message(message)
            preview_text = preview_text.strip()

        # Cache it
        now_iso = datetime.now(timezone.utc).isoformat()
        await db.brands.update_one(
            {"id": brand_id},
            {"$set": {"story_preview": preview_text, "story_preview_generated_at": now_iso}}
        )

        return {"preview": preview_text, "generated_at": now_iso}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Story preview generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate story preview. Please try again.")




@api_router.get("/brand-portal/dashboard")
async def get_brand_dashboard(current_user: dict = Depends(get_current_brand_partner)):
    """Get brand partner dashboard data"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")

    # Auto-create brand if none linked
    if not brand_id:
        new_brand = Brand(name=user.get("full_name", "My Brand"), created_by=user["id"])
        await db.brands.insert_one(new_brand.model_dump())
        await db.users.update_one({"id": user["id"]}, {"$set": {"linked_brand_id": new_brand.id}})
        brand_id = new_brand.id

    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})

    # Get campaigns
    campaigns = await db.brand_campaigns.find({"brand_id": brand_id}, {"_id": 0}).sort("created_date", -1).to_list(50)

    # Get impression stats
    pipeline = [
        {"$match": {"brand_id": brand_id}},
        {"$group": {"_id": None, "total": {"$sum": 1}, "cost": {"$sum": "$cost"}}}
    ]
    imp_agg = await db.brand_impressions.aggregate(pipeline).to_list(1)
    total_impressions = imp_agg[0]["total"] if imp_agg else 0
    total_spent = imp_agg[0]["cost"] if imp_agg else 0

    # Recent impressions
    recent_impressions = await db.brand_impressions.find(
        {"brand_id": brand_id}, {"_id": 0}
    ).sort("created_date", -1).to_list(20)

    # Sponsorships
    sponsorships = await db.classroom_sponsorships.find(
        {"brand_id": brand_id}, {"_id": 0}
    ).to_list(20)

    return {
        "brand": brand,
        "campaigns": campaigns,
        "sponsorships": sponsorships,
        "stats": {
            "total_impressions": total_impressions,
            "total_spent": round(total_spent, 2),
            "budget_total": brand.get("budget_total", 0) if brand else 0,
            "budget_remaining": round((brand.get("budget_total", 0) - total_spent), 2) if brand else 0,
            "active_campaigns": sum(1 for c in campaigns if c.get("status") == "active"),
            "active_sponsorships": sum(1 for s in sponsorships if s.get("is_active")),
        },
        "recent_impressions": recent_impressions,
    }



# ==================== BRAND PORTAL: ANALYTICS DASHBOARD ====================

@api_router.get("/brand-portal/analytics")
async def get_brand_analytics_dashboard(current_user: dict = Depends(get_current_brand_partner)):
    """Get comprehensive analytics for the brand partner dashboard"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        return {"daily_impressions": [], "campaign_breakdown": [], "product_breakdown": [],
                "region_breakdown": [], "metrics": {}}

    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    if not brand:
        return {"daily_impressions": [], "campaign_breakdown": [], "product_breakdown": [],
                "region_breakdown": [], "metrics": {}}

    # 1. Daily impressions over last 30 days
    from datetime import timedelta
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    daily_pipeline = [
        {"$match": {"brand_id": brand_id, "created_date": {"$gte": thirty_days_ago.isoformat()}}},
        {"$addFields": {
            "date_parsed": {"$dateFromString": {"dateString": "$created_date", "onError": "$created_date"}}
        }},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date_parsed"}},
            "impressions": {"$sum": 1},
            "cost": {"$sum": "$cost"},
        }},
        {"$sort": {"_id": 1}},
    ]
    try:
        daily_data = await db.brand_impressions.aggregate(daily_pipeline).to_list(31)
    except Exception:
        daily_data = []

    daily_impressions = [{"date": d["_id"], "impressions": d["impressions"], "cost": round(d["cost"], 3)} for d in daily_data]

    # 2. Campaign breakdown
    campaigns = await db.brand_campaigns.find({"brand_id": brand_id}, {"_id": 0}).to_list(50)
    campaign_breakdown = []
    for c in campaigns:
        camp_pipeline = [
            {"$match": {"brand_id": brand_id, "campaign_id": c["id"]}},
            {"$group": {"_id": None, "impressions": {"$sum": 1}, "cost": {"$sum": "$cost"}}},
        ]
        camp_agg = await db.brand_impressions.aggregate(camp_pipeline).to_list(1)
        imp_count = camp_agg[0]["impressions"] if camp_agg else 0
        imp_cost = camp_agg[0]["cost"] if camp_agg else 0
        campaign_breakdown.append({
            "id": c["id"],
            "name": c["name"],
            "status": c.get("status", "active"),
            "budget": c.get("budget", 0),
            "budget_spent": round(c.get("budget_spent", 0), 2),
            "impressions": imp_count,
            "cost": round(imp_cost, 2),
            "cpi": round(imp_cost / imp_count, 3) if imp_count > 0 else 0,
        })

    # 3. Product breakdown
    product_pipeline = [
        {"$match": {"brand_id": brand_id}},
        {"$unwind": "$products_featured"},
        {"$group": {
            "_id": "$products_featured",
            "impressions": {"$sum": 1},
            "cost": {"$sum": "$cost"},
        }},
        {"$sort": {"impressions": -1}},
    ]
    try:
        product_data = await db.brand_impressions.aggregate(product_pipeline).to_list(50)
    except Exception:
        product_data = []
    product_breakdown = [{"product": p["_id"], "impressions": p["impressions"], "cost": round(p["cost"], 3)} for p in product_data if p["_id"]]

    # 4. Overall metrics
    total_pipeline = [
        {"$match": {"brand_id": brand_id}},
        {"$group": {"_id": None, "total": {"$sum": 1}, "cost": {"$sum": "$cost"}}},
    ]
    total_agg = await db.brand_impressions.aggregate(total_pipeline).to_list(1)
    total_impressions = total_agg[0]["total"] if total_agg else 0
    total_cost = total_agg[0]["cost"] if total_agg else 0

    budget_total = brand.get("budget_total", 0)
    budget_utilization = round((total_cost / budget_total * 100), 1) if budget_total > 0 else 0
    avg_cpi = round(total_cost / total_impressions, 3) if total_impressions > 0 else 0

    # Impressions last 7 days vs previous 7 days for velocity
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    fourteen_days_ago = datetime.now(timezone.utc) - timedelta(days=14)
    recent_pipeline = [
        {"$match": {"brand_id": brand_id, "created_date": {"$gte": seven_days_ago.isoformat()}}},
        {"$group": {"_id": None, "count": {"$sum": 1}}},
    ]
    prev_pipeline = [
        {"$match": {"brand_id": brand_id, "created_date": {"$gte": fourteen_days_ago.isoformat(), "$lt": seven_days_ago.isoformat()}}},
        {"$group": {"_id": None, "count": {"$sum": 1}}},
    ]
    try:
        recent_agg = await db.brand_impressions.aggregate(recent_pipeline).to_list(1)
        prev_agg = await db.brand_impressions.aggregate(prev_pipeline).to_list(1)
    except Exception:
        recent_agg = []
        prev_agg = []
    recent_count = recent_agg[0]["count"] if recent_agg else 0
    prev_count = prev_agg[0]["count"] if prev_agg else 0
    velocity_change = round(((recent_count - prev_count) / prev_count * 100), 1) if prev_count > 0 else (100.0 if recent_count > 0 else 0)

    metrics = {
        "total_impressions": total_impressions,
        "total_cost": round(total_cost, 2),
        "budget_total": budget_total,
        "budget_remaining": round(budget_total - total_cost, 2),
        "budget_utilization": budget_utilization,
        "avg_cpi": avg_cpi,
        "impressions_last_7d": recent_count,
        "impressions_prev_7d": prev_count,
        "velocity_change": velocity_change,
        "total_campaigns": len(campaigns),
        "active_campaigns": sum(1 for c in campaigns if c.get("status") == "active"),
        "total_products_featured": len(product_breakdown),
        "total_stories": brand.get("total_stories", 0),
    }

    return {
        "daily_impressions": daily_impressions,
        "campaign_breakdown": campaign_breakdown,
        "product_breakdown": product_breakdown,
        "metrics": metrics,
    }



# ==================== BRAND PARTNER CAMPAIGN MANAGEMENT ====================

class CampaignCreate(BaseModel):
    name: str
    description: str = ""
    products: list = []
    target_ages: list = []
    target_categories: list = []
    budget: float = 0.0
    cost_per_impression: float = 0.05


@api_router.post("/brand-portal/campaigns")
async def create_campaign(data: CampaignCreate, current_user: dict = Depends(get_current_brand_partner)):
    """Create a brand campaign"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    if not user.get("brand_approved"):
        raise HTTPException(status_code=403, detail="Your brand account is pending approval")
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked to your account")

    campaign = BrandCampaign(
        brand_id=brand_id, name=data.name, description=data.description,
        products=[BrandProduct(**p) if isinstance(p, dict) else p for p in data.products],
        target_ages=data.target_ages, target_categories=data.target_categories,
        budget=data.budget, cost_per_impression=data.cost_per_impression,
        status="active", created_by=current_user["id"],
    )
    await db.brand_campaigns.insert_one(campaign.model_dump())
    return campaign.model_dump()


@api_router.get("/brand-portal/campaigns")
async def list_my_campaigns(current_user: dict = Depends(get_current_brand_partner)):
    """List brand partner's campaigns"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        return []
    campaigns = await db.brand_campaigns.find({"brand_id": brand_id}, {"_id": 0}).sort("created_date", -1).to_list(50)
    return campaigns


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    products: Optional[list] = None
    target_ages: Optional[list] = None
    target_categories: Optional[list] = None
    budget: Optional[float] = None
    cost_per_impression: Optional[float] = None
    status: Optional[str] = None


@api_router.put("/brand-portal/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, data: CampaignUpdate, current_user: dict = Depends(get_current_brand_partner)):
    """Update a campaign"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await db.brand_campaigns.update_one(
        {"id": campaign_id, "brand_id": brand_id}, {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign updated"}


@api_router.delete("/brand-portal/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str, current_user: dict = Depends(get_current_brand_partner)):
    """Delete a campaign"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    result = await db.brand_campaigns.delete_one({"id": campaign_id, "brand_id": brand_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign deleted"}


# ==================== BRAND PARTNER BUDGET TOP-UP ====================

class BrandTopupRequest(BaseModel):
    amount: float
    origin_url: str


@api_router.post("/brand-portal/topup")
async def brand_topup(data: BrandTopupRequest, request: Request, current_user: dict = Depends(get_current_brand_partner)):
    """Top up brand campaign budget via Stripe"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")
    if data.amount < 5:
        raise HTTPException(status_code=400, detail="Minimum top-up is $5")

    stripe_key = os.environ.get("STRIPE_API_KEY")
    if not stripe_key:
        raise HTTPException(status_code=500, detail="Payment not configured")

    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    origin = data.origin_url.rstrip("/")
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_key, webhook_url=webhook_url)

    metadata = {"user_id": current_user["id"], "brand_id": brand_id, "type": "brand_topup"}

    checkout_req = CheckoutSessionRequest(
        amount=data.amount, currency="usd",
        success_url=f"{origin}/brand-portal?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{origin}/brand-portal?payment=cancelled",
        metadata=metadata, payment_methods=["card"],
    )
    session = await stripe_checkout.create_checkout_session(checkout_req)

    txn = PaymentTransaction(
        user_id=current_user["id"], session_id=session.session_id,
        amount=data.amount, currency="usd", metadata=metadata,
    )
    await db.payment_transactions.insert_one(txn.model_dump())

    return {"url": session.url, "session_id": session.session_id}


@api_router.get("/brand-portal/topup-status/{session_id}")
async def brand_topup_status(session_id: str, request: Request, current_user: dict = Depends(get_current_brand_partner)):
    """Check brand top-up payment status and credit brand budget"""
    txn = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Payment not found")
    if txn.get("payment_status") == "paid":
        return {"status": "paid", "amount": txn["amount"]}

    stripe_key = os.environ.get("STRIPE_API_KEY")
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    host_url = str(request.base_url).rstrip("/")
    stripe_checkout = StripeCheckout(api_key=stripe_key, webhook_url=f"{host_url}/api/webhook/stripe")
    checkout_status = await stripe_checkout.get_checkout_status(session_id)

    if checkout_status.payment_status == "paid" and txn.get("payment_status") != "paid":
        already = await db.payment_transactions.find_one({"session_id": session_id, "payment_status": "paid"})
        if not already:
            amount = txn["amount"]
            brand_id = txn.get("metadata", {}).get("brand_id")
            now_iso = datetime.now(timezone.utc).isoformat()

            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": "paid", "status": "completed", "updated_date": now_iso}}
            )
            if brand_id:
                await db.brands.update_one({"id": brand_id}, {"$inc": {"budget_total": amount}})

        return {"status": "paid", "amount": txn["amount"]}

    return {"status": txn.get("status", "initiated"), "amount": txn["amount"]}


# ==================== ADMIN: APPROVE/REJECT BRAND PARTNERS ====================

@api_router.post("/admin/approve-brand-partner/{user_id}")
async def approve_brand_partner(user_id: str, current_user: dict = Depends(get_current_user)):
    """Approve a brand partner application"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    target = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not target or target.get("role") != "brand_partner":
        raise HTTPException(status_code=404, detail="Brand partner not found")

    await db.users.update_one({"id": user_id}, {"$set": {"brand_approved": True}})
    return {"message": f"Brand partner {target['email']} approved"}


@api_router.post("/admin/reject-brand-partner/{user_id}")
async def reject_brand_partner(user_id: str, current_user: dict = Depends(get_current_user)):
    """Reject/suspend a brand partner"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    await db.users.update_one({"id": user_id}, {"$set": {"brand_approved": False}})
    return {"message": "Brand partner suspended"}


@api_router.post("/admin/link-brand/{user_id}/{brand_id}")
async def link_brand_to_partner(user_id: str, brand_id: str, current_user: dict = Depends(get_current_user)):
    """Link a brand to a partner account"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    brand = await db.brands.find_one({"id": brand_id})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    await db.users.update_one({"id": user_id}, {"$set": {"linked_brand_id": brand_id}})
    return {"message": f"Brand '{brand['name']}' linked to user"}


# ==================== HEALTH CHECK ====================

@api_router.get("/")
async def root():
    return {"message": "LexiMaster API is running", "version": "1.0.0"}


@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


# Include router in app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_migrate():
    """Run startup migrations"""
    from models import generate_student_code
    
    # Ensure master admin role
    master_email = "allen@songsforcenturies.com"
    master_user = await db.users.find_one({"email": master_email})
    if master_user and master_user.get("role") != "admin":
        await db.users.update_one(
            {"email": master_email},
            {"$set": {"role": "admin", "is_delegated_admin": True}}
        )
        logger.info(f"Promoted {master_email} to admin")
    
    # Ensure wallet_balance field on all users
    await db.users.update_many(
        {"wallet_balance": {"$exists": False}},
        {"$set": {"wallet_balance": 0.0}}
    )
    
    # Ensure referral_code on all users
    from models import generate_referral_code as gen_ref
    cursor_users = db.users.find({"referral_code": {"$exists": False}}, {"_id": 0, "id": 1})
    async for u in cursor_users:
        await db.users.update_one({"id": u["id"]}, {"$set": {"referral_code": gen_ref()}})
    
    # Migrate existing students that are missing student_code
    cursor = db.students.find({"student_code": {"$exists": False}}, {"_id": 0, "id": 1})
    async for student in cursor:
        while True:
            code = generate_student_code()
            existing = await db.students.find_one({"student_code": code})
            if not existing:
                break
        await db.students.update_one(
            {"id": student["id"]},
            {"$set": {"student_code": code}}
        )
        logger.info(f"Migrated student {student['id']} with code {code}")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
