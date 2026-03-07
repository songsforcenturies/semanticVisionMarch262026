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
from datetime import datetime, timezone
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
            "role": user["role"],
            "wallet_balance": user.get("wallet_balance", 0.0),
            "is_delegated_admin": user.get("is_delegated_admin", False),
        }
    }


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

    # Check usage limit
    if coupon["uses_count"] >= coupon["max_uses"]:
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
