from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone

# Import models and auth
from models import (
    User, UserCreate, UserLogin, UserResponse, UserRole,
    Student, StudentCreate, StudentUpdate,
    Subscription, SubscriptionPlan, SubscriptionStatus,
    WordBank, WordBankCreate,
    Narrative, NarrativeCreate,
    Assessment, ReadLog, WordBankGift, GiftCreate,
    ClassroomSession, SystemConfig,
    get_biological_target
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_admin, get_current_guardian, get_current_teacher
)

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== AUTHENTICATION ROUTES ====================

@api_router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new guardian/teacher user"""
    # Check if email already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
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
    
    return UserResponse(**user_dict)


@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    """Login for guardians/teachers/admin"""
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
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
            "role": user["role"]
        }
    }


@api_router.post("/auth/student-login")
async def student_login(pin: str):
    """PIN-based login for students"""
    student = await db.students.find_one({"access_pin": pin, "status": "active"})
    if not student:
        raise HTTPException(status_code=401, detail="Invalid PIN or inactive student")
    
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
    
    # Generate unique PIN
    while True:
        from models import generate_pin
        pin = generate_pin()
        existing = await db.students.find_one({"access_pin": pin})
        if not existing:
            break
    
    # Calculate biological target
    biological_target = get_biological_target(student_data.age) if student_data.age else 0
    
    student = Student(
        **student_data.model_dump(),
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


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
