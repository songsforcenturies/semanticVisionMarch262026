"""Brand Digital Media management routes — audio/video uploads, streaming, downloads, and library."""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid, os

from database import db, logger
from auth import get_current_user, get_current_admin, get_current_guardian

router = APIRouter()

# Ensure uploads directory exists
MEDIA_UPLOAD_DIR = Path(__file__).parent / "uploads" / "media"
MEDIA_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_MEDIA_SIZE = 50 * 1024 * 1024  # 50MB


# ==================== ADMIN: MEDIA SETTINGS ====================

@router.get("/admin/media-settings")
async def get_media_settings(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
    config = await db.system_config.find_one({"key": "media_settings"}, {"_id": 0})
    defaults = {
        "digital_media_enabled": False,
        "default_price_per_stream": 0.00,
        "default_price_per_download": 0.99,
        "max_storage_per_user_mb": 500,
        "max_recording_duration_sec": 600,
        "auto_delete_recordings_days": 0,
    }
    if config and config.get("value"):
        defaults.update(config["value"])
    return defaults


class MediaSettingsUpdate(BaseModel):
    digital_media_enabled: Optional[bool] = None
    default_price_per_stream: Optional[float] = None
    default_price_per_download: Optional[float] = None
    max_storage_per_user_mb: Optional[int] = None
    max_recording_duration_sec: Optional[int] = None
    auto_delete_recordings_days: Optional[int] = None


@router.put("/admin/media-settings")
async def update_media_settings(data: MediaSettingsUpdate, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    update = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail="No fields to update")
    await db.system_config.update_one(
        {"key": "media_settings"},
        {"$set": {"value": {**((await db.system_config.find_one({"key": "media_settings"}, {"_id": 0}) or {}).get("value", {})), **update}}},
        upsert=True,
    )
    return {"message": "Media settings updated"}


# ==================== ADMIN: BRAND MEDIA CRUD ====================

@router.get("/admin/storage-stats")
async def get_storage_stats(current_user: dict = Depends(get_current_user)):
    """Get storage usage statistics"""
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

    # Calculate total storage from recordings and media uploads
    import os
    recordings_dir = Path(__file__).parent / "uploads" / "recordings"
    media_dir = MEDIA_UPLOAD_DIR
    support_dir = Path(__file__).parent / "uploads" / "support"

    def dir_size(path):
        total = 0
        if path.exists():
            for f in path.rglob("*"):
                if f.is_file():
                    total += f.stat().st_size
        return total

    recordings_bytes = dir_size(recordings_dir)
    media_bytes = dir_size(media_dir)
    support_bytes = dir_size(support_dir)
    total_bytes = recordings_bytes + media_bytes + support_bytes

    # Count files
    recordings_count = await db.recordings.count_documents({})
    media_count = await db.brand_media.count_documents({})

    return {
        "total_storage_mb": round(total_bytes / (1024 * 1024), 2),
        "recordings_storage_mb": round(recordings_bytes / (1024 * 1024), 2),
        "media_storage_mb": round(media_bytes / (1024 * 1024), 2),
        "support_storage_mb": round(support_bytes / (1024 * 1024), 2),
        "recordings_count": recordings_count,
        "media_count": media_count,
    }

@router.post("/admin/brand-media/upload")
async def upload_brand_media(
    file: UploadFile = File(...),
    title: str = Form(...),
    artist: str = Form(""),
    brand_id: str = Form(""),
    current_user: dict = Depends(get_current_user),
):
    """Upload an audio file for brand media"""
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

    allowed_types = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/ogg", "audio/aac", "audio/mp4", "audio/x-m4a",
                     "video/mp4", "video/webm", "video/quicktime"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}. Allowed: MP3, WAV, OGG, AAC, MP4, WebM")

    contents = await file.read()
    if len(contents) > MAX_MEDIA_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB")

    ext = file.filename.split(".")[-1] if "." in file.filename else "mp3"
    media_id = str(uuid.uuid4())
    filename = f"{media_id}.{ext}"
    file_path = MEDIA_UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        f.write(contents)

    is_video = file.content_type.startswith("video/")
    file_url = f"/api/media/stream/{filename}"

    doc = {
        "id": media_id,
        "title": title,
        "artist": artist,
        "brand_id": brand_id,
        "media_type": "video" if is_video else "audio",
        "source": "upload",
        "file_url": file_url,
        "youtube_url": "",
        "filename": filename,
        "file_size": len(contents),
        "status": "approved",
        "price_per_stream": 0.00,
        "price_per_download": 0.99,
        "total_streams": 0,
        "total_downloads": 0,
        "total_likes": 0,
        "created_by": current_user["id"],
        "created_date": datetime.now(timezone.utc).isoformat(),
    }
    await db.brand_media.insert_one(doc)
    doc.pop("_id", None)
    return doc


class BrandMediaCreate(BaseModel):
    title: str
    artist: str = ""
    brand_id: str = ""
    media_type: str = "video"  # audio or video
    youtube_url: str = ""
    price_per_stream: float = 0.00
    price_per_download: float = 0.99


@router.post("/admin/brand-media")
async def create_brand_media(data: BrandMediaCreate, current_user: dict = Depends(get_current_user)):
    """Create a brand media entry (for YouTube videos or links)"""
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

    media_id = str(uuid.uuid4())
    doc = {
        "id": media_id,
        "title": data.title,
        "artist": data.artist,
        "brand_id": data.brand_id,
        "media_type": data.media_type,
        "source": "youtube" if data.youtube_url else "link",
        "file_url": "",
        "youtube_url": data.youtube_url,
        "filename": "",
        "status": "approved",
        "price_per_stream": data.price_per_stream,
        "price_per_download": data.price_per_download,
        "total_streams": 0,
        "total_downloads": 0,
        "total_likes": 0,
        "created_by": current_user["id"],
        "created_date": datetime.now(timezone.utc).isoformat(),
    }
    await db.brand_media.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/admin/brand-media")
async def list_brand_media(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
    media = await db.brand_media.find({}, {"_id": 0}).sort("created_date", -1).to_list(500)
    return media


class BrandMediaUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    status: Optional[str] = None
    price_per_stream: Optional[float] = None
    price_per_download: Optional[float] = None


@router.put("/admin/brand-media/{media_id}")
async def update_brand_media(media_id: str, data: BrandMediaUpdate, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    update = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await db.brand_media.update_one({"id": media_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Media not found")
    return {"message": "Media updated"}


@router.delete("/admin/brand-media/{media_id}")
async def delete_brand_media(media_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    media = await db.brand_media.find_one({"id": media_id}, {"_id": 0})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    # Delete file if uploaded
    if media.get("filename"):
        file_path = MEDIA_UPLOAD_DIR / media["filename"]
        if file_path.exists():
            file_path.unlink()
    await db.brand_media.delete_one({"id": media_id})
    return {"message": "Media deleted"}


# ==================== PUBLIC MEDIA ENDPOINTS ====================

@router.get("/media")
async def list_all_media(current_user: dict = Depends(get_current_user)):
    """List all approved media items"""
    media = await db.brand_media.find({"status": "approved"}, {"_id": 0}).sort("created_date", -1).to_list(500)
    return media


@router.get("/media/student")
async def list_student_media(current_user: dict = Depends(get_current_user)):
    """List media accessible to students (approved, with student-safe filtering)"""
    media = await db.brand_media.find({"status": "approved"}, {"_id": 0}).sort("created_date", -1).to_list(500)
    # Return student-safe fields only
    return [
        {
            "id": m["id"],
            "title": m["title"],
            "artist": m.get("artist", ""),
            "media_type": m.get("media_type", "audio"),
            "source": m.get("source", ""),
            "file_url": m.get("file_url", ""),
            "youtube_url": m.get("youtube_url", ""),
            "brand_id": m.get("brand_id", ""),
            "price_per_stream": m.get("price_per_stream", 0.00),
            "price_per_download": m.get("price_per_download", 0.99),
        }
        for m in media
    ]


# ==================== MEDIA STREAMING ====================

from fastapi.responses import FileResponse

@router.get("/media/stream/{filename}")
async def stream_media(filename: str):
    """Stream uploaded media file"""
    file_path = MEDIA_UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Media file not found")
    ext = filename.rsplit(".", 1)[-1].lower()
    content_types = {"mp3": "audio/mpeg", "wav": "audio/wav", "ogg": "audio/ogg", "aac": "audio/aac",
                     "m4a": "audio/mp4", "mp4": "video/mp4", "webm": "video/webm"}
    return FileResponse(file_path, media_type=content_types.get(ext, "application/octet-stream"))


# ==================== STUDENT MEDIA LIBRARY ====================

@router.get("/students/{student_id}/media-library")
async def get_student_media_library(student_id: str, current_user: dict = Depends(get_current_user)):
    """Get all media a student has listened to / liked"""
    entries = await db.student_media_library.find({"student_id": student_id}, {"_id": 0}).sort("listened_date", -1).to_list(500)
    # Enrich with media details
    media_ids = list(set(e["media_id"] for e in entries))
    media_map = {}
    if media_ids:
        media_docs = await db.brand_media.find({"id": {"$in": media_ids}}, {"_id": 0}).to_list(500)
        media_map = {m["id"]: m for m in media_docs}

    result = []
    for e in entries:
        m = media_map.get(e["media_id"], {})
        result.append({
            "id": e["id"],
            "media_id": e["media_id"],
            "title": m.get("title", "Unknown"),
            "artist": m.get("artist", ""),
            "media_type": m.get("media_type", "audio"),
            "file_url": m.get("file_url", ""),
            "youtube_url": m.get("youtube_url", ""),
            "source": m.get("source", ""),
            "liked": e.get("liked", False),
            "downloaded": e.get("downloaded", False),
            "listen_count": e.get("listen_count", 1),
            "listened_date": e.get("listened_date", ""),
            "price_per_download": m.get("price_per_download", 0.99),
        })
    return result


@router.post("/students/{student_id}/media-listen")
async def record_media_listen(student_id: str, media_id: str = "", current_user: dict = Depends(get_current_user)):
    """Record that a student listened to a media item"""
    if not media_id:
        raise HTTPException(status_code=400, detail="media_id required")

    existing = await db.student_media_library.find_one({"student_id": student_id, "media_id": media_id})
    if existing:
        await db.student_media_library.update_one(
            {"student_id": student_id, "media_id": media_id},
            {"$inc": {"listen_count": 1}, "$set": {"listened_date": datetime.now(timezone.utc).isoformat()}}
        )
    else:
        doc = {
            "id": str(uuid.uuid4()),
            "student_id": student_id,
            "media_id": media_id,
            "liked": False,
            "downloaded": False,
            "listen_count": 1,
            "listened_date": datetime.now(timezone.utc).isoformat(),
        }
        await db.student_media_library.insert_one(doc)
    await db.brand_media.update_one({"id": media_id}, {"$inc": {"total_streams": 1}})
    return {"message": "Listen recorded"}


class MediaLikeRequest(BaseModel):
    media_id: str
    liked: bool


@router.post("/students/{student_id}/media-like")
async def toggle_media_like(student_id: str, data: MediaLikeRequest, current_user: dict = Depends(get_current_user)):
    """Toggle like on a media item"""
    existing = await db.student_media_library.find_one({"student_id": student_id, "media_id": data.media_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Media not in library. Listen to it first.")
    was_liked = existing.get("liked", False)
    await db.student_media_library.update_one(
        {"student_id": student_id, "media_id": data.media_id},
        {"$set": {"liked": data.liked}}
    )
    inc_val = 1 if data.liked and not was_liked else (-1 if not data.liked and was_liked else 0)
    if inc_val:
        await db.brand_media.update_one({"id": data.media_id}, {"$inc": {"total_likes": inc_val}})
    return {"message": "Like updated", "liked": data.liked}


class MediaDownloadRequest(BaseModel):
    media_id: str


@router.post("/students/{student_id}/media-download")
async def purchase_media_download(student_id: str, data: MediaDownloadRequest, current_user: dict = Depends(get_current_user)):
    """Purchase a media download — deducts from parent's wallet"""
    student = await db.students.find_one({"id": student_id}, {"_id": 0, "guardian_id": 1})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    media = await db.brand_media.find_one({"id": data.media_id}, {"_id": 0})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    price = media.get("price_per_download", 0.99)
    if price <= 0:
        # Free download
        await db.student_media_library.update_one(
            {"student_id": student_id, "media_id": data.media_id},
            {"$set": {"downloaded": True, "download_date": datetime.now(timezone.utc).isoformat()}},
            upsert=True,
        )
        await db.brand_media.update_one({"id": data.media_id}, {"$inc": {"total_downloads": 1}})
        return {"message": "Downloaded for free", "price": 0}

    guardian_id = student["guardian_id"]
    guardian = await db.users.find_one({"id": guardian_id}, {"_id": 0, "wallet_balance": 1})
    if not guardian:
        raise HTTPException(status_code=404, detail="Guardian not found")

    balance = guardian.get("wallet_balance", 0)
    if balance < price:
        raise HTTPException(status_code=400, detail=f"Insufficient wallet balance. Need ${price:.2f}, have ${balance:.2f}")

    # Deduct from wallet
    await db.users.update_one({"id": guardian_id}, {"$inc": {"wallet_balance": -price}})
    # Record download
    await db.student_media_library.update_one(
        {"student_id": student_id, "media_id": data.media_id},
        {"$set": {"downloaded": True, "download_date": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    await db.brand_media.update_one({"id": data.media_id}, {"$inc": {"total_downloads": 1}})
    # Record transaction
    txn = {
        "id": str(uuid.uuid4()),
        "user_id": guardian_id,
        "type": "media_download",
        "amount": -price,
        "description": f"Download: {media.get('title', 'Media')}",
        "media_id": data.media_id,
        "student_id": student_id,
        "created_date": datetime.now(timezone.utc).isoformat(),
    }
    await db.wallet_transactions.insert_one(txn)

    return {"message": "Download purchased", "price": price, "new_balance": round(balance - price, 2)}


# ==================== GUARDIAN: CHILDREN MEDIA ====================

@router.get("/guardian/children-media")
async def get_children_media(current_user: dict = Depends(get_current_guardian)):
    """Get all media children have listened to"""
    students = await db.students.find({"guardian_id": current_user["id"]}, {"_id": 0, "id": 1, "full_name": 1}).to_list(20)
    student_ids = [s["id"] for s in students]
    student_names = {s["id"]: s["full_name"] for s in students}

    if not student_ids:
        return []

    entries = await db.student_media_library.find({"student_id": {"$in": student_ids}}, {"_id": 0}).sort("listened_date", -1).to_list(500)
    media_ids = list(set(e["media_id"] for e in entries))
    media_map = {}
    if media_ids:
        media_docs = await db.brand_media.find({"id": {"$in": media_ids}}, {"_id": 0}).to_list(500)
        media_map = {m["id"]: m for m in media_docs}

    result = []
    for e in entries:
        m = media_map.get(e["media_id"], {})
        result.append({
            "student_id": e["student_id"],
            "student_name": student_names.get(e["student_id"], ""),
            "media_id": e["media_id"],
            "title": m.get("title", "Unknown"),
            "artist": m.get("artist", ""),
            "media_type": m.get("media_type", "audio"),
            "liked": e.get("liked", False),
            "downloaded": e.get("downloaded", False),
            "listen_count": e.get("listen_count", 1),
            "listened_date": e.get("listened_date", ""),
        })
    return result


# ==================== GUARDIAN: MEDIA TOGGLE ====================

@router.post("/students/{student_id}/media-preference")
async def update_media_preference(student_id: str, enabled: bool = True, current_user: dict = Depends(get_current_guardian)):
    """Toggle digital media on/off for a student"""
    query = {"id": student_id}
    if current_user.get("role") != "admin":
        query["guardian_id"] = current_user["id"]
    result = await db.students.update_one(query, {"$set": {"digital_media_enabled": enabled}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": f"Digital media {'enabled' if enabled else 'disabled'}", "enabled": enabled}


# ==================== PUBLIC: GET APPROVED MEDIA FOR STORIES ====================

@router.get("/brand-media/for-story/{student_id}")
async def get_media_for_story(student_id: str, current_user: dict = Depends(get_current_user)):
    """Get approved brand media that can be embedded in a student's story"""
    # Check system-level toggle
    config = await db.system_config.find_one({"key": "media_settings"}, {"_id": 0})
    settings = config.get("value", {}) if config else {}
    if not settings.get("digital_media_enabled", False):
        return {"media": [], "reason": "Digital media is disabled system-wide"}

    # Check student-level toggle
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        return {"media": [], "reason": "Student not found"}
    if not student.get("digital_media_enabled", True):
        return {"media": [], "reason": "Parent has disabled digital media for this student"}

    # Get approved media
    media = await db.brand_media.find({"status": "approved"}, {"_id": 0}).to_list(100)
    import random
    random.shuffle(media)
    # Return up to 3 media items for variety
    selected = media[:3]
    result = [{
        "id": m["id"],
        "title": m["title"],
        "artist": m.get("artist", ""),
        "media_type": m["media_type"],
        "source": m.get("source", ""),
        "file_url": m.get("file_url", ""),
        "youtube_url": m.get("youtube_url", ""),
        "brand_id": m.get("brand_id", ""),
    } for m in selected]
    return {"media": result}
