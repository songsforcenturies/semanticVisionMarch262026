from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
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
    ClassroomSession, SystemConfig,
    get_biological_target
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
        story_data = await story_service.generate_story(
            student_name=student["full_name"],
            student_age=student.get("age", 10),
            grade_level=student.get("grade_level", "1-12"),
            interests=student.get("interests", []),
            virtues=student.get("virtues", []),
            prompt=narrative_data.prompt,
            baseline_words=baseline_words,
            target_words=target_words,
            stretch_words=stretch_words
        )
        
        # Create narrative object
        from models import Chapter, EmbeddedToken, VisionCheck
        
        chapters = []
        for ch_data in story_data.get("chapters", []):
            chapter = Chapter(
                number=ch_data["number"],
                title=ch_data["title"],
                content=ch_data["content"],
                word_count=ch_data["word_count"],
                embedded_tokens=[
                    EmbeddedToken(**token) for token in ch_data.get("embedded_tokens", [])
                ],
                vision_check=VisionCheck(**ch_data["vision_check"])
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
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
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
- Overall: If both are reasonable, mark as correct

Words to evaluate:
{json.dumps(evaluation_requests, indent=2)}

Return ONLY valid JSON (no markdown):
{{
  "results": [
    {{
      "word": "word",
      "definition_correct": true/false,
      "sentence_correct": true/false,
      "overall_correct": true/false,
      "feedback": "brief encouraging feedback"
    }}
  ]
}}"""

        chat = LlmChat(
            api_key=api_key,
            session_id=f"assess_{assessment_id}",
            system_message="You are an educational assessment evaluator. Be encouraging but fair in evaluating student vocabulary understanding."
        )
        chat.with_model("openai", "gpt-5.2")
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        evaluation = json.loads(response)
        
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
    """Migrate existing students that are missing student_code"""
    from models import generate_student_code
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
