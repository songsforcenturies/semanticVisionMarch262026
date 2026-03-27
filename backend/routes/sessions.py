"""Session tracking routes: track student login time for cumulative time logs."""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from database import db, logger
from auth import get_current_guardian

router = APIRouter()

SESSION_TIMEOUT_SECONDS = 120  # If no heartbeat for 2 min, session is considered ended


# ==================== SESSION TRACKING ====================

class SessionStartRequest(BaseModel):
    student_id: str


class SessionHeartbeatRequest(BaseModel):
    student_id: str
    session_id: str


class SessionEndRequest(BaseModel):
    student_id: str
    session_id: str


@router.post("/sessions/start")
async def start_session(data: SessionStartRequest):
    """Create a new session when a student logs in."""
    now = datetime.now(timezone.utc)
    session_id = str(uuid.uuid4())

    # Close any stale open sessions for this student
    await _close_stale_sessions(data.student_id, now)

    session = {
        "id": session_id,
        "student_id": data.student_id,
        "started_at": now.isoformat(),
        "last_active": now.isoformat(),
        "ended_at": None,
        "duration_seconds": 0,
        "date": now.strftime("%Y-%m-%d"),
    }
    await db.session_logs.insert_one(session)
    logger.info(f"Session started: {session_id} for student {data.student_id}")

    return {"session_id": session_id, "started_at": now.isoformat()}


@router.post("/sessions/heartbeat")
async def heartbeat(data: SessionHeartbeatRequest):
    """Update session last_active and duration."""
    session = await db.session_logs.find_one(
        {"id": data.session_id, "student_id": data.student_id},
        {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.get("ended_at"):
        raise HTTPException(status_code=400, detail="Session already ended")

    now = datetime.now(timezone.utc)
    started_at = datetime.fromisoformat(session["started_at"])
    duration = int((now - started_at).total_seconds())

    await db.session_logs.update_one(
        {"id": data.session_id},
        {"$set": {"last_active": now.isoformat(), "duration_seconds": duration}}
    )

    return {"status": "ok", "duration_seconds": duration}


@router.post("/sessions/end")
async def end_session(data: SessionEndRequest = None, request: Request = None):
    """End a session (on logout or tab close)."""
    # Handle sendBeacon (text/plain) from beforeunload
    if data is None or (data.student_id is None and data.session_id is None):
        try:
            body = await request.body()
            import json
            parsed = json.loads(body)
            student_id = parsed.get("student_id")
            session_id = parsed.get("session_id")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid request body")
    else:
        student_id = data.student_id
        session_id = data.session_id

    session = await db.session_logs.find_one(
        {"id": session_id, "student_id": student_id},
        {"_id": 0}
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.get("ended_at"):
        return {"status": "already_ended"}

    now = datetime.now(timezone.utc)
    started_at = datetime.fromisoformat(session["started_at"])
    duration = int((now - started_at).total_seconds())

    await db.session_logs.update_one(
        {"id": session_id},
        {"$set": {
            "ended_at": now.isoformat(),
            "last_active": now.isoformat(),
            "duration_seconds": duration,
        }}
    )
    logger.info(f"Session ended: {session_id}, duration={duration}s")

    return {"status": "ended", "duration_seconds": duration}


# ==================== TIME LOG AGGREGATION ====================

@router.get("/students/{student_id}/time-log")
async def get_student_time_log(
    student_id: str,
    current_user: dict = Depends(get_current_guardian),
):
    """Get aggregated time log data for a student (for parent progress reports)."""
    student = await db.students.find_one({"id": student_id}, {"_id": 0, "guardian_id": 1})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if current_user.get("role") != "admin" and student["guardian_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    now = datetime.now(timezone.utc)

    # Close stale sessions before aggregating
    await _close_stale_sessions(student_id, now)

    # Fetch all sessions for this student
    sessions = await db.session_logs.find(
        {"student_id": student_id},
        {"_id": 0, "date": 1, "duration_seconds": 1, "started_at": 1, "ended_at": 1}
    ).sort("started_at", 1).to_list(10000)

    # Aggregate by date
    daily_map = {}
    for s in sessions:
        date_key = s.get("date", "unknown")
        if date_key not in daily_map:
            daily_map[date_key] = 0
        daily_map[date_key] += s.get("duration_seconds", 0)

    daily_logs = [
        {
            "date": date,
            "total_seconds": secs,
            "hours": round(secs / 3600, 2),
            "display": _format_duration(secs),
        }
        for date, secs in sorted(daily_map.items())
    ]

    cumulative_seconds = sum(s.get("duration_seconds", 0) for s in sessions)
    total_days = len(daily_map)
    avg_daily_seconds = int(cumulative_seconds / total_days) if total_days > 0 else 0

    return {
        "student_id": student_id,
        "daily_logs": daily_logs,
        "total_days_logged_in": total_days,
        "cumulative_seconds": cumulative_seconds,
        "cumulative_display": _format_duration(cumulative_seconds),
        "average_daily_seconds": avg_daily_seconds,
        "average_daily_display": _format_duration(avg_daily_seconds),
        "total_sessions": len(sessions),
    }


# ==================== HELPERS ====================

async def _close_stale_sessions(student_id: str, now: datetime):
    """Close sessions that didn't receive a heartbeat within the timeout."""
    cutoff = (now - timedelta(seconds=SESSION_TIMEOUT_SECONDS)).isoformat()
    stale = db.session_logs.find({
        "student_id": student_id,
        "ended_at": None,
        "last_active": {"$lt": cutoff},
    })
    async for s in stale:
        last_active = datetime.fromisoformat(s["last_active"])
        started_at = datetime.fromisoformat(s["started_at"])
        duration = int((last_active - started_at).total_seconds()) + SESSION_TIMEOUT_SECONDS
        await db.session_logs.update_one(
            {"id": s["id"]},
            {"$set": {
                "ended_at": last_active.isoformat(),
                "duration_seconds": duration,
            }}
        )
        logger.info(f"Closed stale session {s['id']}, duration={duration}s")


def _format_duration(seconds: int) -> str:
    """Format seconds into a human-readable string."""
    if not seconds:
        return "0m"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m"
