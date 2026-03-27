"""User support ticket / feedback routes — text, screenshot, audio, video messages to admin."""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid

from database import db, logger
from auth import get_current_user, get_current_admin

router = APIRouter()

SUPPORT_UPLOAD_DIR = Path(__file__).parent / "uploads" / "support"
SUPPORT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class SupportTicketCreate(BaseModel):
    subject: str
    message: str
    type: str = "text"  # text, bug, feedback, feature_request


@router.post("/support/tickets")
@router.post("/support/ticket")
async def create_support_ticket(data: SupportTicketCreate, current_user: dict = Depends(get_current_user)):
    """Create a new support ticket from any user"""
    ticket = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "user_name": current_user.get("full_name", "User"),
        "user_email": current_user.get("email", ""),
        "user_role": current_user.get("role", ""),
        "subject": data.subject,
        "message": data.message,
        "type": data.type,
        "status": "open",
        "attachments": [],
        "admin_replies": [],
        "created_date": datetime.now(timezone.utc).isoformat(),
        "updated_date": datetime.now(timezone.utc).isoformat(),
    }
    await db.support_tickets.insert_one(ticket)
    ticket.pop("_id", None)
    return ticket


@router.post("/support/tickets/{ticket_id}/attachment")
async def add_ticket_attachment(
    ticket_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Attach a screenshot, audio, or video to a support ticket"""
    ticket = await db.support_tickets.find_one({"id": ticket_id})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket["user_id"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    allowed = ["image/png", "image/jpeg", "image/webp", "image/gif",
               "audio/mpeg", "audio/wav", "audio/ogg", "audio/webm",
               "video/mp4", "video/webm", "video/quicktime"]
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="File type not supported")

    contents = await file.read()
    if len(contents) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 25MB)")

    ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    att_id = str(uuid.uuid4())
    filename = f"{att_id}.{ext}"
    with open(SUPPORT_UPLOAD_DIR / filename, "wb") as f:
        f.write(contents)

    attachment = {
        "id": att_id,
        "filename": filename,
        "original_name": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
        "url": f"/api/support/files/{filename}",
        "uploaded_by": current_user["id"],
        "uploaded_date": datetime.now(timezone.utc).isoformat(),
    }

    await db.support_tickets.update_one(
        {"id": ticket_id},
        {"$push": {"attachments": attachment}, "$set": {"updated_date": datetime.now(timezone.utc).isoformat()}}
    )
    return attachment


from fastapi.responses import FileResponse


@router.get("/support/files/{filename}")
async def get_support_file(filename: str):
    """Serve support attachment files"""
    file_path = SUPPORT_UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    ext = filename.rsplit(".", 1)[-1].lower()
    ct = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp", "gif": "image/gif",
          "mp3": "audio/mpeg", "wav": "audio/wav", "ogg": "audio/ogg", "webm": "video/webm", "mp4": "video/mp4"}
    return FileResponse(file_path, media_type=ct.get(ext, "application/octet-stream"))


@router.get("/support/tickets")
async def list_support_tickets(current_user: dict = Depends(get_current_user)):
    """List support tickets — admins see all, users see their own"""
    if current_user.get("role") == "admin" or current_user.get("is_delegated_admin"):
        query = {}
    else:
        query = {"user_id": current_user["id"]}
    tickets = await db.support_tickets.find(query, {"_id": 0}).sort("updated_date", -1).to_list(200)
    return tickets


@router.get("/support/tickets/{ticket_id}")
async def get_support_ticket(ticket_id: str, current_user: dict = Depends(get_current_user)):
    ticket = await db.support_tickets.find_one({"id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket["user_id"] != current_user["id"] and current_user.get("role") != "admin" and not current_user.get("is_delegated_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    return ticket


class AdminReply(BaseModel):
    message: str


@router.post("/support/tickets/{ticket_id}/reply")
async def admin_reply_to_ticket(ticket_id: str, data: AdminReply, current_user: dict = Depends(get_current_user)):
    """Admin replies to a support ticket — also creates a notification for the user"""
    if current_user.get("role") != "admin" and not current_user.get("is_delegated_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    ticket = await db.support_tickets.find_one({"id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    reply = {
        "id": str(uuid.uuid4()),
        "message": data.message,
        "admin_id": current_user["id"],
        "admin_name": current_user.get("full_name", "Admin"),
        "created_date": datetime.now(timezone.utc).isoformat(),
    }

    await db.support_tickets.update_one(
        {"id": ticket_id},
        {
            "$push": {"admin_replies": reply},
            "$set": {"status": "replied", "updated_date": datetime.now(timezone.utc).isoformat()}
        }
    )

    # Send notification to the user
    notif = {
        "id": str(uuid.uuid4()),
        "title": f"Re: {ticket['subject']}",
        "body": data.message,
        "target": "specific_user",
        "target_ids": [ticket["user_id"]],
        "target_email": ticket.get("user_email"),
        "target_user_name": ticket.get("user_name"),
        "priority": "normal",
        "sent_by": current_user["id"],
        "sent_by_name": current_user.get("full_name", "Admin"),
        "created_date": datetime.now(timezone.utc).isoformat(),
        "read_by": [],
        "email_sent": False,
        "support_ticket_id": ticket_id,
    }
    await db.admin_messages.insert_one(notif)

    return {"message": "Reply sent", "reply": reply}


class TicketStatusUpdate(BaseModel):
    status: str  # open, in_progress, replied, resolved, closed


@router.put("/support/tickets/{ticket_id}/status")
async def update_ticket_status(ticket_id: str, data: TicketStatusUpdate, current_user: dict = Depends(get_current_user)):
    """Update ticket status"""
    if current_user.get("role") != "admin" and not current_user.get("is_delegated_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    await db.support_tickets.update_one(
        {"id": ticket_id},
        {"$set": {"status": data.status, "updated_date": datetime.now(timezone.utc).isoformat()}}
    )
    return {"message": f"Status updated to {data.status}"}


# ==================== FAQ SYSTEM (from resolved tickets) ====================


class PublishFAQRequest(BaseModel):
    faq_question: Optional[str] = None
    faq_answer: Optional[str] = None
    faq_category: str = "General"  # "Account", "Stories", "Recording", "Billing", "Technical"


@router.post("/admin/support/tickets/{ticket_id}/publish-faq")
async def publish_ticket_as_faq(ticket_id: str, data: PublishFAQRequest, current_user: dict = Depends(get_current_user)):
    """Admin resolves a ticket and publishes it as a FAQ entry."""
    if current_user.get("role") != "admin" and not current_user.get("is_delegated_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    ticket = await db.support_tickets.find_one({"id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Default question to ticket subject
    faq_question = data.faq_question or ticket.get("subject", "")
    if not faq_question:
        raise HTTPException(status_code=400, detail="FAQ question is required (no subject on ticket)")

    # Default answer to last admin reply
    faq_answer = data.faq_answer
    if not faq_answer:
        admin_replies = ticket.get("admin_replies", [])
        if admin_replies:
            faq_answer = admin_replies[-1].get("message", "")
        if not faq_answer:
            raise HTTPException(status_code=400, detail="FAQ answer is required (no admin replies on ticket)")

    now = datetime.now(timezone.utc).isoformat()
    await db.support_tickets.update_one(
        {"id": ticket_id},
        {"$set": {
            "is_faq": True,
            "faq_question": faq_question,
            "faq_answer": faq_answer,
            "faq_category": data.faq_category,
            "faq_published_date": now,
            "status": "resolved",
            "updated_date": now,
        }}
    )

    return {
        "message": "Ticket published as FAQ",
        "faq": {
            "id": ticket_id,
            "question": faq_question,
            "answer": faq_answer,
            "category": data.faq_category,
            "published_date": now,
        }
    }


@router.get("/faq")
async def list_faq():
    """Public endpoint — returns all published FAQ entries sorted by category then date."""
    tickets = await db.support_tickets.find(
        {"is_faq": True},
        {"_id": 0, "id": 1, "faq_question": 1, "faq_answer": 1, "faq_category": 1, "faq_published_date": 1}
    ).sort([("faq_category", 1), ("faq_published_date", -1)]).to_list(500)

    return [
        {
            "id": t["id"],
            "question": t.get("faq_question", ""),
            "answer": t.get("faq_answer", ""),
            "category": t.get("faq_category", "General"),
            "published_date": t.get("faq_published_date", ""),
        }
        for t in tickets
    ]


@router.get("/faq/search")
async def search_faq(q: str = ""):
    """Public search across FAQ questions and answers."""
    if not q or not q.strip():
        return await list_faq()

    query = {
        "is_faq": True,
        "$or": [
            {"faq_question": {"$regex": q.strip(), "$options": "i"}},
            {"faq_answer": {"$regex": q.strip(), "$options": "i"}},
        ]
    }
    tickets = await db.support_tickets.find(
        query,
        {"_id": 0, "id": 1, "faq_question": 1, "faq_answer": 1, "faq_category": 1, "faq_published_date": 1}
    ).sort([("faq_category", 1), ("faq_published_date", -1)]).to_list(500)

    return [
        {
            "id": t["id"],
            "question": t.get("faq_question", ""),
            "answer": t.get("faq_answer", ""),
            "category": t.get("faq_category", "General"),
            "published_date": t.get("faq_published_date", ""),
        }
        for t in tickets
    ]
