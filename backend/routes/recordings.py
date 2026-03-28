"""Audio recording, read-aloud, diction analysis, audio books, parental controls, messaging, spelling bee routes."""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Body
from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid, os, json as json_lib

from database import db, logger, fs_bucket
from bson import ObjectId
from io import BytesIO
from models import UserRole, generate_uuid
from auth import get_current_user, get_current_admin, get_current_guardian
from services import send_email

router = APIRouter()

# ==================== READ-ALOUD RECORDING SYSTEM ====================

@router.post("/recordings/upload")
async def upload_recording(
    file: UploadFile = File(...),
    student_id: str = Form(...),
    narrative_id: str = Form(...),
    chapter_number: int = Form(0),
    recording_type: str = Form("audio"),
    current_user=Depends(get_current_user)
):
    """Upload a read-aloud audio or video recording"""
    try:
        allowed_audio = {"audio/webm", "audio/mp3", "audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4", "audio/x-m4a"}
        allowed_video = {"video/webm", "video/mp4"}
        allowed = allowed_audio | allowed_video

        if file.content_type not in allowed:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

        student = await db.students.find_one({"id": student_id}, {"_id": 0})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        narrative = await db.narratives.find_one({"id": narrative_id}, {"_id": 0})
        if not narrative:
            raise HTTPException(status_code=404, detail="Narrative not found")

        ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "webm"
        recording_id = str(uuid.uuid4())
        filename = f"{recording_id}.{ext}"

        content = await file.read()
        file_size = len(content)

        # Save to GridFS instead of ephemeral filesystem
        gridfs_id = await fs_bucket.upload_from_stream(
            filename,
            BytesIO(content),
            metadata={"content_type": file.content_type, "recording_id": recording_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recording upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    chapter_text = ""
    if narrative and narrative.get("chapters"):
        for ch in narrative["chapters"]:
            if ch.get("number") == chapter_number:
                chapter_text = ch.get("content", "")
                break

    recording = {
        "id": recording_id,
        "student_id": student_id,
        "student_name": student.get("full_name", ""),
        "student_age": student.get("age", 0),
        "narrative_id": narrative_id,
        "narrative_title": narrative.get("title", ""),
        "chapter_number": chapter_number,
        "chapter_text": chapter_text,
        "recording_type": recording_type,
        "file_path": "",
        "gridfs_id": str(gridfs_id),
        "file_name": filename,
        "file_size": file_size,
        "content_type": file.content_type,
        "guardian_id": current_user["id"],
        "diction_scores": None,
        "transcription": None,
        "analysis_status": "pending",
        "shared_to_audiobooks": False,
        "created_date": datetime.now(timezone.utc).isoformat()
    }
    
    await db.reading_recordings.insert_one({**recording, "_id": None})
    await db.reading_recordings.update_one({"id": recording_id}, {"$unset": {"_id": ""}})
    
    # Notify parent that a new audio memory was created
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "type": "audio_memory",
        "title": "New Audio Memory",
        "message": f"{student.get('full_name', 'Your child')} just created a new audio memory reading \"{narrative.get('title', 'a story')}\" (Ch. {chapter_number})",
        "read": False,
        "data": {"recording_id": recording_id, "student_id": student_id, "narrative_id": narrative_id},
        "created_date": datetime.now(timezone.utc).isoformat(),
    }
    await db.messages.insert_one({**notification, "_id": None})
    await db.messages.update_one({"id": notification["id"]}, {"$unset": {"_id": ""}})
    
    return {"id": recording_id, "status": "uploaded", "file_size": file_size}


@router.post("/recordings/{recording_id}/analyze")
async def analyze_recording(recording_id: str, current_user=Depends(get_current_user)):
    """Analyze a recording: transcribe with Whisper and score diction"""
    from openai import OpenAI

    recording = await db.reading_recordings.find_one({"id": recording_id}, {"_id": 0})
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    chapter_text = recording.get("chapter_text", "")

    try:
        # Read file from GridFS (or fall back to filesystem for legacy recordings)
        gridfs_id = recording.get("gridfs_id")
        if gridfs_id:
            grid_out = await fs_bucket.open_download_stream(ObjectId(gridfs_id))
            file_bytes = await grid_out.read()
            audio_file = BytesIO(file_bytes)
            audio_file.name = recording.get("file_name", "recording.webm")
        else:
            filepath = recording["file_path"]
            audio_file = open(filepath, "rb")

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
        )

        try:
            response = client.audio.transcriptions.create(
                file=audio_file,
                model="openai/whisper-1",
                response_format="verbose_json",
                language="en",
                temperature=0.0,
            )
        finally:
            audio_file.close()

        transcribed_text = ""
        if hasattr(response, 'text'):
            transcribed_text = response.text.strip()
        elif isinstance(response, dict):
            transcribed_text = response.get("text", "").strip()
        elif isinstance(response, str):
            transcribed_text = response.strip()
        else:
            transcribed_text = str(response).strip()
        
        # Compute diction scores by comparing transcription to source text
        scores = compute_diction_scores(transcribed_text, chapter_text)
        
        await db.reading_recordings.update_one(
            {"id": recording_id},
            {"$set": {
                "transcription": transcribed_text,
                "diction_scores": scores,
                "analysis_status": "completed",
                "analyzed_date": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "id": recording_id,
            "transcription": transcribed_text,
            "diction_scores": scores,
            "status": "completed"
        }
    except Exception as e:
        logger.error(f"Recording analysis failed: {e}")
        await db.reading_recordings.update_one(
            {"id": recording_id},
            {"$set": {"analysis_status": "failed", "analysis_error": str(e)}}
        )
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def compute_diction_scores(transcribed: str, source: str) -> dict:
    """Compare transcribed text against source text and compute diction scores"""
    import difflib
    
    if not source.strip():
        return {"pronunciation": 0, "fluency": 0, "completeness": 0, "prosody": 0, "overall": 0, "word_details": []}
    
    source_words = source.lower().split()
    trans_words = transcribed.lower().split()
    
    # Completeness: what % of source words appear in transcription
    source_set = set(source_words)
    trans_set = set(trans_words)
    matched_words = source_set & trans_set
    completeness = (len(matched_words) / max(len(source_set), 1)) * 100
    
    # Pronunciation accuracy via sequence matching
    matcher = difflib.SequenceMatcher(None, source_words, trans_words)
    ratio = matcher.ratio()
    pronunciation = min(ratio * 100, 100)
    
    # Fluency: based on how close the word count and ordering match
    word_count_ratio = min(len(trans_words), len(source_words)) / max(len(source_words), 1)
    fluency = min(word_count_ratio * 100, 100)
    
    # Prosody: estimate from how well words follow the source order
    # Using longest common subsequence ratio
    lcs_blocks = matcher.get_matching_blocks()
    lcs_len = sum(b.size for b in lcs_blocks)
    prosody = (lcs_len / max(len(source_words), 1)) * 100
    
    # Word-level details
    word_details = []
    for i, word in enumerate(source_words[:50]):
        found = word in trans_set
        word_details.append({"word": word, "correct": found, "position": i})
    
    overall = (pronunciation * 0.35 + fluency * 0.25 + completeness * 0.25 + prosody * 0.15)
    
    return {
        "pronunciation": round(pronunciation, 1),
        "fluency": round(fluency, 1),
        "completeness": round(completeness, 1),
        "prosody": round(prosody, 1),
        "overall": round(overall, 1),
        "words_in_source": len(source_words),
        "words_transcribed": len(trans_words),
        "words_matched": len(matched_words),
        "word_details": word_details
    }


@router.get("/recordings/student/{student_id}")
async def get_student_recordings(student_id: str, current_user=Depends(get_current_user)):
    """Get all recordings for a student (Audio Memory Library)"""
    recordings = await db.reading_recordings.find(
        {"student_id": student_id},
        {"_id": 0, "file_path": 0}
    ).sort("created_date", -1).to_list(200)
    return {"recordings": recordings}


@router.get("/recordings/{recording_id}/stream")
async def stream_recording(recording_id: str):
    """Stream a recording file"""
    from starlette.responses import StreamingResponse
    from fastapi.responses import FileResponse
    recording = await db.reading_recordings.find_one({"id": recording_id}, {"_id": 0})
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    content_type = recording.get("content_type", "audio/webm")
    gridfs_id = recording.get("gridfs_id")

    if gridfs_id:
        # Stream from GridFS
        grid_out = await fs_bucket.open_download_stream(ObjectId(gridfs_id))

        async def gridfs_iterator():
            while True:
                chunk = await grid_out.readchunk()
                if not chunk:
                    break
                yield chunk

        return StreamingResponse(gridfs_iterator(), media_type=content_type)
    else:
        # Legacy: stream from filesystem
        filepath = recording.get("file_path", "")
        if not filepath or not Path(filepath).exists():
            raise HTTPException(status_code=404, detail="Recording file not found")
        return FileResponse(filepath, media_type=content_type)


@router.get("/recordings/guardian/all")
async def get_guardian_recordings(current_user=Depends(get_current_user)):
    """Get all recordings for all students under this guardian (Memory Library)"""
    students = await db.students.find(
        {"guardian_id": current_user["id"]},
        {"_id": 0, "id": 1, "full_name": 1}
    ).to_list(50)
    
    student_ids = [s["id"] for s in students]
    recordings = await db.reading_recordings.find(
        {"student_id": {"$in": student_ids}},
        {"_id": 0, "file_path": 0}
    ).sort("created_date", -1).to_list(500)
    
    return {"recordings": recordings, "students": students}


@router.delete("/recordings/{recording_id}")
async def delete_recording(recording_id: str, current_user=Depends(get_current_user)):
    """Delete a recording"""
    recording = await db.reading_recordings.find_one({"id": recording_id}, {"_id": 0})
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    if recording["guardian_id"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete from GridFS if stored there
    gridfs_id = recording.get("gridfs_id")
    if gridfs_id:
        try:
            await fs_bucket.delete(ObjectId(gridfs_id))
        except Exception as e:
            logger.warning(f"Failed to delete GridFS file {gridfs_id}: {e}")
    else:
        # Legacy: delete from filesystem
        filepath = recording.get("file_path", "")
        if filepath and Path(filepath).exists():
            Path(filepath).unlink()

    await db.reading_recordings.delete_one({"id": recording_id})
    await db.audio_books.delete_many({"recording_id": recording_id})
    return {"deleted": True}


# ==================== AUDIO BOOK COLLECTION ====================

@router.post("/audio-books/contribute")
async def contribute_to_audiobooks(data: dict = Body(...), current_user=Depends(get_current_user)):
    """Parent contributes a recording to the public audio book collection"""
    recording_id = data.get("recording_id")
    display_name = data.get("display_name", "Anonymous Reader")
    
    recording = await db.reading_recordings.find_one({"id": recording_id}, {"_id": 0})
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    if recording["guardian_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    settings = await db.system_config.find_one({"key": "audio_book_settings"}, {"_id": 0})
    auto_approve = settings.get("value", {}).get("auto_approve", False) if settings else False
    
    audio_book = {
        "id": str(uuid.uuid4()),
        "recording_id": recording_id,
        "narrative_id": recording["narrative_id"],
        "narrative_title": recording.get("narrative_title", ""),
        "student_name": display_name,
        "student_age": recording.get("student_age", 0),
        "chapter_number": recording.get("chapter_number", 0),
        "diction_scores": recording.get("diction_scores"),
        "duration_estimate": recording.get("file_size", 0) / 16000,
        "recording_type": recording.get("recording_type", "audio"),
        "guardian_id": current_user["id"],
        "status": "approved" if auto_approve else "pending",
        "is_visible": auto_approve,
        "listens": 0,
        "likes": 0,
        "created_date": datetime.now(timezone.utc).isoformat()
    }
    
    await db.audio_books.insert_one({**audio_book, "_id": None})
    await db.audio_books.update_one({"id": audio_book["id"]}, {"$unset": {"_id": ""}})
    
    await db.reading_recordings.update_one(
        {"id": recording_id},
        {"$set": {"shared_to_audiobooks": True}}
    )
    
    return {"id": audio_book["id"], "status": audio_book["status"]}


@router.get("/audio-books")
async def get_audio_books(page: int = 1, limit: int = 20):
    """Browse the public audio book collection"""
    settings = await db.system_config.find_one({"key": "audio_book_settings"}, {"_id": 0})
    enabled = settings.get("value", {}).get("enabled", True) if settings else True
    
    if not enabled:
        return {"audio_books": [], "total": 0, "enabled": False}
    
    skip = (page - 1) * limit
    total = await db.audio_books.count_documents({"is_visible": True, "status": "approved"})
    audio_books = await db.audio_books.find(
        {"is_visible": True, "status": "approved"},
        {"_id": 0}
    ).sort("created_date", -1).skip(skip).limit(limit).to_list(limit)
    
    return {"audio_books": audio_books, "total": total, "enabled": True}


@router.get("/audio-books/{book_id}/stream")
async def stream_audio_book(book_id: str):
    """Stream an audio book recording"""
    book = await db.audio_books.find_one({"id": book_id}, {"_id": 0})
    if not book or not book.get("is_visible"):
        raise HTTPException(status_code=404, detail="Audio book not found")
    
    recording = await db.reading_recordings.find_one({"id": book["recording_id"]}, {"_id": 0})
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    await db.audio_books.update_one({"id": book_id}, {"$inc": {"listens": 1}})

    content_type = recording.get("content_type", "audio/webm")
    gridfs_id = recording.get("gridfs_id")

    if gridfs_id:
        from starlette.responses import StreamingResponse
        grid_out = await fs_bucket.open_download_stream(ObjectId(gridfs_id))

        async def gridfs_iterator():
            while True:
                chunk = await grid_out.readchunk()
                if not chunk:
                    break
                yield chunk

        return StreamingResponse(gridfs_iterator(), media_type=content_type)
    else:
        from fastapi.responses import FileResponse
        filepath = recording.get("file_path", "")
        if not filepath or not Path(filepath).exists():
            raise HTTPException(status_code=404, detail="Recording file not found")
        return FileResponse(filepath, media_type=content_type)


@router.post("/audio-books/{book_id}/like")
async def like_audio_book(book_id: str):
    """Like an audio book"""
    await db.audio_books.update_one({"id": book_id}, {"$inc": {"likes": 1}})
    return {"liked": True}


# ==================== AUDIO BOOK ADMIN ====================

@router.get("/admin/audio-books")
async def admin_get_audio_books(current_user=Depends(get_current_user)):
    """Admin: Get all audio books including pending"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    books = await db.audio_books.find({}, {"_id": 0}).sort("created_date", -1).to_list(500)
    return {"audio_books": books}


@router.put("/admin/audio-books/{book_id}")
async def admin_update_audio_book(book_id: str, data: dict = Body(...), current_user=Depends(get_current_user)):
    """Admin: Approve, reject, or toggle visibility of an audio book"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    update = {}
    if "status" in data:
        update["status"] = data["status"]
    if "is_visible" in data:
        update["is_visible"] = data["is_visible"]
    
    if update:
        if update.get("status") == "approved":
            update["is_visible"] = True
        await db.audio_books.update_one({"id": book_id}, {"$set": update})
    
    return {"updated": True}


@router.delete("/admin/audio-books/{book_id}")
async def admin_delete_audio_book(book_id: str, current_user=Depends(get_current_user)):
    """Admin: Delete an audio book entry"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    book = await db.audio_books.find_one({"id": book_id}, {"_id": 0})
    if book:
        await db.reading_recordings.update_one(
            {"id": book["recording_id"]},
            {"$set": {"shared_to_audiobooks": False}}
        )
    await db.audio_books.delete_one({"id": book_id})
    return {"deleted": True}


@router.get("/admin/audio-books/settings")
async def get_audio_book_settings(current_user=Depends(get_current_user)):
    """Get audio book collection settings"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    settings = await db.system_config.find_one({"key": "audio_book_settings"}, {"_id": 0})
    defaults = {"enabled": True, "auto_approve": False, "show_on_landing": True}
    return settings.get("value", defaults) if settings else defaults


@router.put("/admin/audio-books/settings")
async def update_audio_book_settings(data: dict = Body(...), current_user=Depends(get_current_user)):
    """Update audio book collection settings"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    await db.system_config.update_one(
        {"key": "audio_book_settings"},
        {"$set": {"key": "audio_book_settings", "value": data}},
        upsert=True
    )
    return {"updated": True}


# ==================== DICTION PROGRESS ====================

@router.get("/recordings/student/{student_id}/progress")
async def get_diction_progress(student_id: str, current_user=Depends(get_current_user)):
    """Get diction improvement over time for a student"""
    recordings = await db.reading_recordings.find(
        {"student_id": student_id, "analysis_status": "completed"},
        {"_id": 0, "id": 1, "diction_scores": 1, "created_date": 1, "narrative_title": 1}
    ).sort("created_date", 1).to_list(200)
    
    progress = []
    for r in recordings:
        if r.get("diction_scores"):
            progress.append({
                "date": r["created_date"],
                "title": r.get("narrative_title", ""),
                "scores": r["diction_scores"]
            })
    
    # Compute improvement
    improvement = {}
    if len(progress) >= 2:
        first = progress[0]["scores"]
        last = progress[-1]["scores"]
        for key in ["pronunciation", "fluency", "completeness", "prosody", "overall"]:
            improvement[key] = round(last.get(key, 0) - first.get(key, 0), 1)
    
    return {"progress": progress, "improvement": improvement, "total_sessions": len(progress)}



# ==================== PARENTAL CONTROLS ====================

class ParentalControlsUpdate(BaseModel):
    recording_mode: str = "none"  # "none", "audio_video", "audio_only"
    auto_start_recording: bool = False
    require_confirmation: bool = True
    chapter_threshold: int = 0  # 0 = every chapter, N = after N chapters
    can_skip_recording: bool = True

DEFAULT_PARENTAL_CONTROLS = {
    "recording_mode": "none",
    "auto_start_recording": False,
    "require_confirmation": True,
    "chapter_threshold": 0,
    "can_skip_recording": True,
}

@router.get("/students/{student_id}/parental-controls")
async def get_parental_controls(student_id: str):
    """Get parental controls for a student - no auth required for read-only access"""
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(404, "Student not found")
    controls = student.get("parental_controls", DEFAULT_PARENTAL_CONTROLS)
    return controls

@router.put("/students/{student_id}/parental-controls")
async def update_parental_controls(student_id: str, data: ParentalControlsUpdate, current_user=Depends(get_current_user)):
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(404, "Student not found")
    
    controls = data.dict()
    await db.students.update_one({"id": student_id}, {"$set": {"parental_controls": controls}})
    return controls




# ==================== TASK REMINDERS ====================

@router.get("/student-reminders/{student_id}")
async def get_student_reminders(student_id: str):
    """Generate contextual reminders for a student based on reading activity."""
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(404, "Student not found")
    
    reminders = []
    
    # Check for incomplete narratives
    narratives = await db.narratives.find(
        {"student_id": student_id, "status": {"$ne": "completed"}}, {"_id": 0}
    ).to_list(20)
    
    for n in narratives:
        chapters_done = len(n.get("chapters_completed", []))
        if chapters_done > 0 and chapters_done < 5:
            reminders.append({
                "id": f"incomplete-{n['id']}",
                "type": "incomplete_story",
                "priority": "high",
                "title": f"Continue \"{n.get('title', 'Your Story')}\"",
                "message": f"You've read {chapters_done}/5 chapters. Keep going — you're almost there!",
                "narrative_id": n["id"],
                "progress": chapters_done / 5,
            })
    
    # Check last reading activity
    last_log = await db.read_logs.find(
        {"student_id": student_id}, {"_id": 0}
    ).sort("session_end", -1).to_list(1)
    
    if last_log:
        last_date = last_log[0].get("session_end", "")
        try:
            last_dt = datetime.fromisoformat(last_date.replace("Z", "+00:00"))
            days_since = (datetime.now(timezone.utc) - last_dt).days
            if days_since >= 3:
                reminders.append({
                    "id": "inactivity",
                    "type": "inactivity",
                    "priority": "medium",
                    "title": "Time to Read!",
                    "message": f"It's been {days_since} days since your last reading session. Your vocabulary misses you!",
                    "days_inactive": days_since,
                })
        except Exception:
            pass
    elif not last_log and narratives:
        reminders.append({
            "id": "never-read",
            "type": "inactivity",
            "priority": "high",
            "title": "Start Reading!",
            "message": "You have stories waiting for you. Open one and start your reading journey!",
            "days_inactive": 999,
        })
    
    # Check for unrecorded chapters (parental controls)
    controls = student.get("parental_controls", {})
    if controls.get("recording_mode", "none") != "none":
        recordings = await db.audio_recordings.find(
            {"student_id": student_id}, {"_id": 0}
        ).to_list(100)
        recorded_chapters = set()
        for r in recordings:
            recorded_chapters.add(f"{r.get('narrative_id')}-{r.get('chapter_number')}")
        
        for n in narratives:
            for ch_num in n.get("chapters_completed", []):
                key = f"{n['id']}-{ch_num}"
                if key not in recorded_chapters:
                    reminders.append({
                        "id": f"unrecorded-{key}",
                        "type": "recording_due",
                        "priority": "high",
                        "title": "Recording Needed",
                        "message": f"Chapter {ch_num} of \"{n.get('title', 'your story')}\" needs a read-aloud recording.",
                        "narrative_id": n["id"],
                        "chapter_number": ch_num,
                    })
    
    # Check spelling contests available
    now = datetime.now(timezone.utc).isoformat()
    active_contests = await db.spelling_contests.find(
        {"is_active": True, "end_date": {"$gte": now}}, {"_id": 0}
    ).to_list(5)
    
    student_submissions = await db.spelling_submissions.find(
        {"student_id": student_id}, {"_id": 0, "contest_id": 1}
    ).to_list(100)
    submitted_ids = {s["contest_id"] for s in student_submissions}
    
    for c in active_contests:
        if c["id"] not in submitted_ids:
            reminders.append({
                "id": f"contest-{c['id']}",
                "type": "spelling_contest",
                "priority": "low",
                "title": f"Spelling Bee: {c.get('title', 'New Contest')}",
                "message": f"A spelling contest with {len(c.get('word_list', []))} words is waiting for you!",
                "contest_id": c["id"],
            })
    
    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    reminders.sort(key=lambda r: priority_order.get(r["priority"], 3))
    
    return {"reminders": reminders, "count": len(reminders)}


@router.post("/parent-milestone-check/{student_id}")
async def check_parent_milestones(student_id: str):
    """Check and generate milestone notifications for parents."""
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(404)
    
    milestones = []
    mastered = len(student.get("mastered_tokens", []))
    total_reading = student.get("total_reading_seconds", 0)
    
    # Word milestones
    for threshold in [10, 25, 50, 100, 250, 500, 1000]:
        if mastered >= threshold:
            milestones.append({
                "type": "vocabulary",
                "threshold": threshold,
                "message": f"{student.get('full_name', 'Your child')} has mastered {mastered} words!",
            })
    
    # Reading time milestones (in minutes)
    minutes = total_reading // 60
    for threshold in [30, 60, 120, 300, 600]:
        if minutes >= threshold:
            milestones.append({
                "type": "reading_time",
                "threshold": threshold,
                "message": f"{student.get('full_name', 'Your child')} has read for {minutes} minutes total!",
            })
    
    # Completed stories
    completed = await db.narratives.count_documents({"student_id": student_id, "status": "completed"})
    for threshold in [1, 3, 5, 10, 25]:
        if completed >= threshold:
            milestones.append({
                "type": "stories_completed",
                "threshold": threshold,
                "message": f"{student.get('full_name', 'Your child')} has completed {completed} stories!",
            })
    
    return {"milestones": milestones, "student_name": student.get("full_name")}




# ==================== ADMIN MESSAGING ====================

class AdminMessageCreate(BaseModel):
    title: str
    body: str
    target: str = "all"  # "all", "guardians", "students", "teachers", "specific_user"
    target_ids: Optional[List[str]] = None  # specific user/student IDs
    target_email: Optional[str] = None  # email of specific user to message
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    send_email: bool = False  # also send via email

@router.post("/admin/messages")
async def create_admin_message(msg: AdminMessageCreate, current_user=Depends(get_current_admin)):
    target_ids = msg.target_ids or []
    target_user_name = None
    target_email_address = None

    # If targeting a specific user by email, look them up
    if msg.target_email and msg.target_email.strip():
        email = msg.target_email.strip().lower()
        user = await db.users.find_one({"email": email}, {"_id": 0, "id": 1, "full_name": 1, "email": 1})
        if not user:
            raise HTTPException(status_code=404, detail=f"No user found with email: {email}")
        target_ids = [user["id"]]
        target_user_name = user.get("full_name", email)
        target_email_address = user["email"]

    doc = {
        "id": str(uuid.uuid4()),
        "title": msg.title,
        "body": msg.body,
        "target": "specific_user" if msg.target_email else msg.target,
        "target_ids": target_ids,
        "target_email": target_email_address,
        "target_user_name": target_user_name,
        "priority": msg.priority,
        "sent_by": current_user["id"],
        "sent_by_name": current_user.get("full_name", "Admin"),
        "created_date": datetime.now(timezone.utc).isoformat(),
        "read_by": [],
        "email_sent": False,
    }
    await db.admin_messages.insert_one(doc)
    doc.pop("_id", None)

    # Send email if requested
    if msg.send_email and target_email_address:
        try:
            html = f"""<div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;">
                <h2 style="color:#1a1a2e;margin-bottom:8px;">{msg.title}</h2>
                <p style="color:#444;font-size:15px;line-height:1.6;white-space:pre-wrap;">{msg.body}</p>
                <hr style="border:none;border-top:1px solid #eee;margin:24px 0;" />
                <p style="color:#999;font-size:12px;">From Semantic Vision Admin — <a href="https://semanticvision.ai">semanticvision.ai</a></p>
            </div>"""
            await send_email(target_email_address, msg.title, html)
            await db.admin_messages.update_one({"id": doc["id"]}, {"$set": {"email_sent": True}})
            doc["email_sent"] = True
        except Exception as e:
            logger.error(f"Failed to send email to {target_email_address}: {e}")
            doc["email_error"] = str(e)
    elif msg.send_email and not target_email_address:
        # Broadcast email to all users in the target group
        email_query = {}
        if msg.target == "guardians":
            email_query = {"role": "guardian"}
        elif msg.target == "teachers":
            email_query = {"role": "teacher"}
        elif msg.target == "all":
            email_query = {"role": {"$in": ["guardian", "teacher"]}}

        if email_query:
            users_to_email = await db.users.find(email_query, {"_id": 0, "email": 1}).to_list(500)
            sent_count = 0
            for u in users_to_email:
                try:
                    html = f"""<div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;">
                        <h2 style="color:#1a1a2e;margin-bottom:8px;">{msg.title}</h2>
                        <p style="color:#444;font-size:15px;line-height:1.6;white-space:pre-wrap;">{msg.body}</p>
                        <hr style="border:none;border-top:1px solid #eee;margin:24px 0;" />
                        <p style="color:#999;font-size:12px;">From Semantic Vision Admin — <a href="https://semanticvision.ai">semanticvision.ai</a></p>
                    </div>"""
                    await send_email(u["email"], msg.title, html)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send email to {u['email']}: {e}")
            await db.admin_messages.update_one({"id": doc["id"]}, {"$set": {"email_sent": True, "emails_sent_count": sent_count}})
            doc["email_sent"] = True
            doc["emails_sent_count"] = sent_count

    return doc

@router.get("/admin/messages")
async def list_admin_messages(current_user=Depends(get_current_admin)):
    msgs = await db.admin_messages.find({}, {"_id": 0}).sort("created_date", -1).to_list(200)
    return msgs

@router.delete("/admin/messages/{message_id}")
async def delete_admin_message(message_id: str, current_user=Depends(get_current_admin)):
    await db.admin_messages.delete_one({"id": message_id})
    return {"status": "deleted"}

@router.get("/notifications")
async def get_user_notifications(current_user=Depends(get_current_user)):
    user_role = current_user.get("role", "guardian")
    user_id = current_user["id"]
    
    # Get messages targeted at this user's role or specific IDs or "all"
    query = {
        "$or": [
            {"target": "all"},
            {"target": user_role + "s"},
            {"target_ids": user_id},
        ]
    }
    msgs = await db.admin_messages.find(query, {"_id": 0}).sort("created_date", -1).to_list(50)
    
    for m in msgs:
        m["is_read"] = user_id in (m.get("read_by") or [])
    
    unread_count = sum(1 for m in msgs if not m["is_read"])
    return {"messages": msgs, "unread_count": unread_count}

@router.get("/student-notifications/{student_id}")
async def get_student_notifications(student_id: str):
    query = {
        "$or": [
            {"target": "all"},
            {"target": "students"},
            {"target_ids": student_id},
        ]
    }
    msgs = await db.admin_messages.find(query, {"_id": 0}).sort("created_date", -1).to_list(50)
    
    for m in msgs:
        m["is_read"] = student_id in (m.get("read_by") or [])
    
    unread_count = sum(1 for m in msgs if not m["is_read"])
    return {"messages": msgs, "unread_count": unread_count}

@router.post("/notifications/{message_id}/read")
async def mark_notification_read(message_id: str, current_user=Depends(get_current_user)):
    await db.admin_messages.update_one(
        {"id": message_id},
        {"$addToSet": {"read_by": current_user["id"]}}
    )
    return {"status": "read"}

@router.post("/student-notifications/{message_id}/read")
async def mark_student_notification_read(message_id: str, student_id: str = Body(..., embed=True)):
    await db.admin_messages.update_one(
        {"id": message_id},
        {"$addToSet": {"read_by": student_id}}
    )
    return {"status": "read"}


# ==================== SPELLING CONTESTS ====================

class SpellingContestCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    word_list: List[str]  # words for the contest
    time_limit_seconds: int = 120
    start_date: str
    end_date: str
    grade_levels: Optional[List[str]] = None

@router.post("/admin/spelling-contests")
async def create_spelling_contest(data: SpellingContestCreate, current_user=Depends(get_current_admin)):
    doc = {
        "id": str(uuid.uuid4()),
        "title": data.title,
        "description": data.description,
        "word_list": data.word_list,
        "time_limit_seconds": data.time_limit_seconds,
        "start_date": data.start_date,
        "end_date": data.end_date,
        "grade_levels": data.grade_levels or [],
        "is_active": True,
        "created_by": current_user["id"],
        "created_date": datetime.now(timezone.utc).isoformat(),
        "participants": [],
    }
    await db.spelling_contests.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.get("/admin/spelling-contests")
async def list_spelling_contests_admin(current_user=Depends(get_current_admin)):
    contests = await db.spelling_contests.find({}, {"_id": 0}).sort("created_date", -1).to_list(100)
    return contests

@router.put("/admin/spelling-contests/{contest_id}/toggle")
async def toggle_spelling_contest(contest_id: str, current_user=Depends(get_current_admin)):
    contest = await db.spelling_contests.find_one({"id": contest_id})
    if not contest:
        raise HTTPException(404, "Contest not found")
    new_status = not contest.get("is_active", True)
    await db.spelling_contests.update_one({"id": contest_id}, {"$set": {"is_active": new_status}})
    return {"is_active": new_status}

@router.delete("/admin/spelling-contests/{contest_id}")
async def delete_spelling_contest(contest_id: str, current_user=Depends(get_current_admin)):
    await db.spelling_contests.delete_one({"id": contest_id})
    await db.spelling_submissions.delete_many({"contest_id": contest_id})
    return {"status": "deleted"}

@router.get("/spelling-contests")
async def list_active_spelling_contests():
    now = datetime.now(timezone.utc).isoformat()
    contests = await db.spelling_contests.find(
        {"is_active": True, "end_date": {"$gte": now}}, {"_id": 0}
    ).sort("start_date", -1).to_list(50)
    
    for c in contests:
        subs = await db.spelling_submissions.count_documents({"contest_id": c["id"]})
        c["participant_count"] = subs
    return contests

class SpellingSubmission(BaseModel):
    contest_id: str
    student_id: str
    student_name: str
    answers: Dict[str, str]  # {word: student_spelling}
    time_taken_seconds: int

@router.post("/spelling-contests/submit")
async def submit_spelling_contest(data: SpellingSubmission):
    contest = await db.spelling_contests.find_one({"id": data.contest_id})
    if not contest:
        raise HTTPException(404, "Contest not found")
    
    # Score the submission
    correct = 0
    results = []
    for word in contest["word_list"]:
        student_answer = data.answers.get(word, "").strip().lower()
        is_correct = student_answer == word.lower()
        if is_correct:
            correct += 1
        results.append({"word": word, "answer": student_answer, "correct": is_correct})
    
    total = len(contest["word_list"])
    score = round((correct / total) * 100) if total > 0 else 0
    
    doc = {
        "id": str(uuid.uuid4()),
        "contest_id": data.contest_id,
        "student_id": data.student_id,
        "student_name": data.student_name,
        "answers": data.answers,
        "results": results,
        "correct_count": correct,
        "total_words": total,
        "score": score,
        "time_taken_seconds": data.time_taken_seconds,
        "submitted_date": datetime.now(timezone.utc).isoformat(),
    }
    await db.spelling_submissions.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.get("/spelling-contests/{contest_id}/leaderboard")
async def get_spelling_leaderboard(contest_id: str):
    subs = await db.spelling_submissions.find(
        {"contest_id": contest_id}, {"_id": 0}
    ).sort([("score", -1), ("time_taken_seconds", 1)]).to_list(100)
    
    for i, s in enumerate(subs):
        s["rank"] = i + 1
    return subs



