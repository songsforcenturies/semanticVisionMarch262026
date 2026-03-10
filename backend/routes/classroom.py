"""Classroom session routes and WebSocket management."""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid, json as json_lib

from database import db, logger
from services import ws_manager
from models import (
    ClassroomSession, SessionStatus, ParticipatingStudent, UserRole,
)
from auth import get_current_user, get_current_teacher

router = APIRouter()

# ==================== CLASSROOM SESSION ROUTES (TEACHER) ====================

class CreateSessionRequest(BaseModel):
    title: str
    bank_ids: List[str] = []
    description: Optional[str] = None


@router.post("/classroom-sessions")
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


@router.get("/classroom-sessions")
async def list_classroom_sessions(
    current_user: dict = Depends(get_current_teacher)
):
    """List all sessions for the current teacher"""
    sessions = await db.classroom_sessions.find(
        {"teacher_id": current_user["id"]}, {"_id": 0}
    ).sort("created_date", -1).to_list(100)
    return sessions


@router.get("/classroom-sessions/{session_id}")
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


@router.post("/classroom-sessions/{session_id}/start")
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


@router.post("/classroom-sessions/{session_id}/end")
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


@router.post("/classroom-sessions/join")
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


@router.get("/classroom-sessions/{session_id}/analytics")
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

@router.websocket("/ws/session/{session_id}")
async def websocket_session(websocket: WebSocket, session_id: str):
    """WebSocket for real-time session updates"""
    await ws_manager.connect(websocket, session_id)
    try:
        while True:
            await websocket.receive_text()  # Keep alive
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, session_id)


