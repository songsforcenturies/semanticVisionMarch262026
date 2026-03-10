"""Student management routes: CRUD, progress, export, parental controls."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid, random, string

from database import db, logger
from models import (
    Student, StudentCreate, StudentUpdate, UserRole,
    get_biological_target,
)
from auth import get_current_user, get_current_guardian

router = APIRouter()

# ==================== STUDENT ROUTES ====================

@router.post("/students", response_model=Student)
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


@router.get("/students", response_model=List[Student])
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


@router.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: str):
    """Get a specific student"""
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.patch("/students/{student_id}", response_model=Student)
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


@router.post("/students/{student_id}/reset-pin")
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



class ChangePinRequest(BaseModel):
    current_pin: str
    new_pin: str


@router.post("/students/{student_id}/change-pin")
async def change_student_pin(
    student_id: str,
    data: ChangePinRequest,
    current_user: dict = Depends(get_current_guardian)
):
    """Allow parent or student to change their PIN to a custom one"""
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student["guardian_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    if str(student.get("access_pin", "")) != str(data.current_pin):
        raise HTTPException(status_code=400, detail="Current PIN is incorrect")
    if len(data.new_pin) < 4 or len(data.new_pin) > 10:
        raise HTTPException(status_code=400, detail="PIN must be 4-10 digits")
    if not data.new_pin.isdigit():
        raise HTTPException(status_code=400, detail="PIN must be numbers only")
    existing = await db.students.find_one({"access_pin": data.new_pin, "id": {"$ne": student_id}})
    if existing:
        raise HTTPException(status_code=400, detail="This PIN is already in use. Please choose another.")
    await db.students.update_one({"id": student_id}, {"$set": {"access_pin": data.new_pin}})
    return {"message": "PIN changed successfully"}


@router.post("/student/change-my-pin")
async def student_change_own_pin(data: ChangePinRequest):
    """Allow a student to change their own PIN (no auth needed, just current PIN)"""
    student = await db.students.find_one({"access_pin": str(data.current_pin)})
    if not student:
        raise HTTPException(status_code=400, detail="Current PIN is incorrect")
    if len(data.new_pin) < 4 or len(data.new_pin) > 10:
        raise HTTPException(status_code=400, detail="PIN must be 4-10 digits")
    if not data.new_pin.isdigit():
        raise HTTPException(status_code=400, detail="PIN must be numbers only")
    existing = await db.students.find_one({"access_pin": data.new_pin, "id": {"$ne": student["id"]}})
    if existing:
        raise HTTPException(status_code=400, detail="This PIN is already in use. Please choose another.")
    await db.students.update_one({"id": student["id"]}, {"$set": {"access_pin": data.new_pin}})
    return {"message": "PIN changed successfully"}


@router.delete("/students/{student_id}")
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

@router.get("/students/{student_id}/progress")
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
            "recent_mastered": [t if isinstance(t, str) else t.get("token", "") for t in mastered_tokens[-10:]],
            "all_mastered": [t if isinstance(t, str) else t.get("token", "") for t in mastered_tokens],
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


@router.get("/students/{student_id}/export")
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
<title>Semantic Vision Report - {s["full_name"]}</title>
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
    <h1>Semantic Vision Progress Report</h1>
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
  Generated by Semantic Vision &middot; {report_date}
</div>
</body>
</html>"""

    return HTMLResponse(content=html)


