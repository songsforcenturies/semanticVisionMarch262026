"""Narrative generation, reading, assessment, and read log routes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid, json as json_lib, random, os, pathlib

from database import db, logger
from models import (
    Narrative, NarrativeCreate, NarrativeStatus, UserRole,
    ReadLog, Assessment, Brand, BrandImpression, BrandProduct,
    SystemConfig, WordBank,
)
from auth import get_current_user, get_current_admin, get_current_guardian
from story_service import story_service

router = APIRouter()

# ==================== NARRATIVE ROUTES ====================

@router.post("/narratives")
@router.post("/narratives/generate")
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
    
    # Resolve bank_ids: use provided ones, or fall back to student's assigned banks
    effective_bank_ids = narrative_data.bank_ids if narrative_data.bank_ids else (student.get("assigned_banks") or [])

    # Fetch word banks
    word_banks = []
    for bank_id in effective_bank_ids:
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

        # Check for eligible brand media (songs/videos)
        media_placements = []
        media_config = await db.system_config.find_one({"key": "media_settings"}, {"_id": 0})
        media_enabled = media_config.get("value", {}).get("digital_media_enabled", False) if media_config else False
        student_media_ok = student.get("digital_media_enabled", True)
        force_media = student.get("force_media_in_stories", False)
        media_count = max(1, min(5, student.get("media_integration_count", 2)))
        preferred_media_ids = student.get("preferred_media_ids", [])
        # If force_media is True, include media even when global digital_media_enabled is False
        if (media_enabled and student_media_ok) or force_media:
            import random as rand_mod
            approved_media = await db.brand_media.find({"status": "approved"}, {"_id": 0}).to_list(50)
            # Prioritize preferred media IDs first
            preferred_items = []
            remaining_items = []
            if preferred_media_ids:
                preferred_set = set(preferred_media_ids)
                for m in approved_media:
                    if m["id"] in preferred_set:
                        preferred_items.append(m)
                    else:
                        remaining_items.append(m)
            else:
                remaining_items = approved_media
            rand_mod.shuffle(remaining_items)
            # Combine: preferred first, then random to fill up to media_count
            ordered_media = preferred_items + remaining_items
            media_placements = [{
                "id": m["id"], "title": m["title"], "artist": m.get("artist", ""),
                "media_type": m["media_type"], "source": m.get("source", ""),
                "file_url": m.get("file_url", ""), "youtube_url": m.get("youtube_url", ""),
            } for m in ordered_media[:media_count]]
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
        
        # When personalized=False, use empty/default values for profile fields
        use_personalization = getattr(narrative_data, 'personalized', True)

        story_data = await story_service.generate_story(
            student_name=student["full_name"],
            student_age=student.get("age", 10),
            grade_level=student.get("grade_level", "1-12"),
            interests=student.get("interests", []) if use_personalization else [],
            virtues=student.get("virtues", []) if use_personalization else [],
            prompt=narrative_data.prompt,
            baseline_words=baseline_words,
            target_words=target_words,
            stretch_words=stretch_words,
            student_id=student["id"],
            guardian_id=student.get("guardian_id", ""),
            guardian_name=guardian.get("full_name", "") if guardian else "",
            belief_system=student.get("belief_system", "") if use_personalization else "",
            cultural_context=student.get("cultural_context", "") if use_personalization else "",
            custom_heritage=student.get("custom_heritage", ""),
            culture_learning=student.get("culture_learning", []),
            language=student.get("language", "English"),
            brand_placements=brand_placements,
            media_placements=media_placements,
            strengths=student.get("strengths", "") if use_personalization else "",
            weaknesses=student.get("weaknesses", "") if use_personalization else "",
            media_count=media_count,
            force_media=force_media,
            illustrations_enabled=student.get("illustrations_enabled", False),
            illustration_style=student.get("illustration_style", "storybook"),
            life_characters=student.get("life_characters", []) if use_personalization else [],
            life_lessons=student.get("life_lessons", []) if use_personalization else [],
        )
        
        # Record brand impressions (after narrative creation so we have the real ID)
        # Brand impressions will be recorded below after narrative_dict is inserted
        
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
                vision_check=VisionCheck(**vc_data),
                illustration_description=ch_data.get("illustration_description"),
            )
            chapters.append(chapter)
        
        # Collect all target and stretch words for verification
        tokens_to_verify = [w["word"] for w in target_words] + [w["word"] for w in stretch_words]
        
        narrative = Narrative(
            title=story_data["title"],
            student_id=narrative_data.student_id,
            bank_ids=effective_bank_ids,
            theme=story_data.get("theme", narrative_data.prompt),
            chapters=chapters,
            total_word_count=story_data.get("total_word_count", 0),
            status=NarrativeStatus.READY,
            tokens_to_verify=tokens_to_verify
        )
        
        narrative_dict = narrative.model_dump()

        # Pre-generate illustration URLs so images are ready when student reads
        import urllib.parse
        for ch in narrative_dict.get("chapters", []):
            desc = ch.get("illustration_description")
            if desc:
                prompt = urllib.parse.quote(desc[:300] + ', children book illustration, colorful, safe for kids, no text')
                ch["illustration_url"] = f"https://image.pollinations.ai/prompt/{prompt}?width=768&height=432&nologo=true&seed={abs(hash(desc)) % 100000}"

        # Store brand placements on the narrative for brand portal story snippets
        if brand_placements:
            narrative_dict["brand_placements"] = brand_placements
        # Store media placements for rendering in the reader
        if media_placements:
            narrative_dict["media_placements"] = media_placements
        await db.narratives.insert_one(narrative_dict)
        
        # Record brand impressions with the real narrative ID
        if brand_placements:
            for bp in brand_placements:
                impression = BrandImpression(
                    brand_id=bp["id"], brand_name=bp["name"],
                    narrative_id=narrative.id, student_id=student["id"],
                    guardian_id=student.get("guardian_id", ""),
                    products_featured=[p.get("name", "") for p in bp.get("products", [])],
                    cost=0.05,
                )
                await db.brand_impressions.insert_one(impression.model_dump())
                await db.brands.update_one(
                    {"id": bp["id"]},
                    {"$inc": {"total_impressions": 1, "total_stories": 1, "budget_spent": 0.05}}
                )
        
        return narrative
        
    except Exception as e:
        logger.error(f"Story generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")


class NarrativeBatchCreate(BaseModel):
    student_ids: List[str]
    prompt: str
    bank_ids: List[str] = []
    personalized: bool = True


@router.post("/narratives/batch")
async def create_narratives_batch(batch_data: NarrativeBatchCreate, current_user: dict = Depends(get_current_user)):
    """Generate stories for one or multiple students at once."""
    results = []
    generated = 0
    failed = 0

    # Verify guardian owns all students (or user is admin)
    is_admin = current_user.get("role") == "admin"
    for sid in batch_data.student_ids:
        student = await db.students.find_one({"id": sid}, {"_id": 0, "guardian_id": 1, "full_name": 1})
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {sid} not found")
        if not is_admin and student.get("guardian_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail=f"Not authorized for student {student.get('full_name', sid)}")

    # Generate stories sequentially to avoid rate limits
    for sid in batch_data.student_ids:
        student = await db.students.find_one({"id": sid}, {"_id": 0})
        student_name = student.get("full_name", sid) if student else sid
        try:
            # Determine bank_ids: use provided ones, or fall back to student's assigned banks
            bank_ids = batch_data.bank_ids if batch_data.bank_ids else (student.get("assigned_banks") or [])
            if not bank_ids:
                results.append({"student_id": sid, "student_name": student_name, "narrative_id": None, "status": "failed", "error": "No word banks assigned"})
                failed += 1
                continue

            narrative_create = NarrativeCreate(
                student_id=sid,
                prompt=batch_data.prompt,
                bank_ids=bank_ids,
                personalized=batch_data.personalized,
            )
            narrative = await create_narrative(narrative_create)
            narrative_id = narrative.id if hasattr(narrative, "id") else (narrative.get("id") if isinstance(narrative, dict) else None)
            results.append({"student_id": sid, "student_name": student_name, "narrative_id": narrative_id, "status": "success"})
            generated += 1
        except Exception as e:
            logger.error(f"Batch story generation failed for student {sid}: {str(e)}")
            results.append({"student_id": sid, "student_name": student_name, "narrative_id": None, "status": "failed", "error": str(e)})
            failed += 1

    return {"generated": generated, "failed": failed, "results": results}


@router.get("/narratives")
async def get_narratives(student_id: Optional[str] = None, include_archived: bool = False):
    """Get narratives, optionally filtered by student. Archived stories hidden by default."""
    query = {}
    if student_id:
        query["student_id"] = student_id
    if not include_archived:
        query["status"] = {"$ne": "archived"}

    narratives = await db.narratives.find(query, {"_id": 0}).to_list(1000)
    return narratives


@router.get("/narratives/{narrative_id}")
async def get_narrative(narrative_id: str):
    """Get a specific narrative"""
    narrative = await db.narratives.find_one({"id": narrative_id}, {"_id": 0})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    return narrative


@router.post("/narratives/{narrative_id}/archive")
async def archive_narrative(narrative_id: str, current_user: dict = Depends(get_current_user)):
    """Archive a narrative (hide from student view but keep data)"""
    narrative = await db.narratives.find_one({"id": narrative_id}, {"_id": 0, "student_id": 1})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    # Guardian must own the student, or be admin
    if current_user.get("role") != "admin":
        student = await db.students.find_one({"id": narrative["student_id"]}, {"_id": 0, "guardian_id": 1})
        if not student or student.get("guardian_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
    await db.narratives.update_one({"id": narrative_id}, {"$set": {"status": "archived", "archived_date": datetime.now(timezone.utc).isoformat()}})
    return {"message": "Story archived successfully"}


@router.post("/narratives/{narrative_id}/unarchive")
async def unarchive_narrative(narrative_id: str, current_user: dict = Depends(get_current_user)):
    """Restore an archived narrative"""
    narrative = await db.narratives.find_one({"id": narrative_id}, {"_id": 0, "student_id": 1})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    if current_user.get("role") != "admin":
        student = await db.students.find_one({"id": narrative["student_id"]}, {"_id": 0, "guardian_id": 1})
        if not student or student.get("guardian_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
    await db.narratives.update_one({"id": narrative_id}, {"$set": {"status": "active"}, "$unset": {"archived_date": ""}})
    return {"message": "Story restored successfully"}


@router.delete("/narratives/{narrative_id}")
async def delete_narrative(narrative_id: str, current_user: dict = Depends(get_current_user)):
    """Permanently delete a narrative (guardian or admin only)"""
    narrative = await db.narratives.find_one({"id": narrative_id}, {"_id": 0, "student_id": 1})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    # Guardian must own the student, or be admin
    if current_user.get("role") != "admin":
        student = await db.students.find_one({"id": narrative["student_id"]}, {"_id": 0, "guardian_id": 1})
        if not student or student.get("guardian_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
    await db.narratives.delete_one({"id": narrative_id})
    # Also clean up related data
    await db.assessments.delete_many({"narrative_id": narrative_id})
    await db.read_logs.delete_many({"narrative_id": narrative_id})
    return {"message": "Story permanently deleted"}


# ==================== TEXT-TO-SPEECH ROUTES ====================

TTS_VOICES = {"alloy", "echo", "fable", "nova", "onyx", "shimmer"}
TTS_CACHE_DIR = pathlib.Path("uploads/tts")


async def _generate_tts_audio(narrative_id: str, chapter_number: int, voice: str = "nova"):
    """Generate or return cached TTS audio for a chapter"""
    if voice not in TTS_VOICES:
        raise HTTPException(status_code=400, detail=f"Invalid voice. Choose from: {', '.join(sorted(TTS_VOICES))}")

    # Ensure cache directory exists
    TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = TTS_CACHE_DIR / f"{narrative_id}_ch{chapter_number}_{voice}.mp3"

    # Return cached version if it exists
    if cache_path.exists():
        return cache_path

    # Fetch narrative and chapter content
    narrative = await db.narratives.find_one({"id": narrative_id}, {"_id": 0})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")

    chapters = narrative.get("chapters", [])
    chapter = None
    for ch in chapters:
        if ch.get("number") == chapter_number:
            chapter = ch
            break
    if not chapter:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_number} not found")

    chapter_text = chapter.get("content", "")
    if not chapter_text:
        raise HTTPException(status_code=400, detail="Chapter has no content")

    # Use OpenAI TTS via OpenRouter or direct OpenAI endpoint
    from story_service import story_service
    story_service.set_db(db)
    llm_config = await story_service._get_llm_config()
    api_key = llm_config.get("openrouter_key") or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="No API key configured for TTS")

    try:
        from openai import AsyncOpenAI

        # OpenAI TTS endpoint (OpenRouter proxies to OpenAI for TTS)
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={"HTTP-Referer": "https://semanticvision.ai"},
            max_retries=1,
            timeout=120.0,
        )

        # Truncate text if too long (TTS limit is ~4096 chars)
        tts_text = chapter_text[:4096]

        response = await client.audio.speech.create(
            model="openai/tts-1",
            voice=voice,
            input=tts_text,
            response_format="mp3",
        )

        # Save to cache file
        with open(cache_path, "wb") as f:
            async for chunk in response.aiter_bytes():
                f.write(chunk)

        return cache_path

    except Exception as e:
        logger.error(f"TTS generation failed: {str(e)}")
        # If the response object has a synchronous content attribute, try that
        try:
            content = response.content
            with open(cache_path, "wb") as f:
                f.write(content)
            return cache_path
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


class TTSRequest(BaseModel):
    voice: str = "nova"


@router.post("/narratives/{narrative_id}/chapters/{chapter_number}/tts")
async def generate_chapter_tts(narrative_id: str, chapter_number: int, data: TTSRequest):
    """Generate text-to-speech audio for a chapter"""
    cache_path = await _generate_tts_audio(narrative_id, chapter_number, data.voice)
    return FileResponse(
        path=str(cache_path),
        media_type="audio/mpeg",
        filename=f"{narrative_id}_ch{chapter_number}_{data.voice}.mp3",
    )


@router.get("/narratives/{narrative_id}/chapters/{chapter_number}/tts")
async def get_chapter_tts(
    narrative_id: str,
    chapter_number: int,
    voice: str = Query(default="nova", description="TTS voice"),
):
    """Get text-to-speech audio for a chapter (GET for easy audio element embedding)"""
    cache_path = await _generate_tts_audio(narrative_id, chapter_number, voice)
    return FileResponse(
        path=str(cache_path),
        media_type="audio/mpeg",
        filename=f"{narrative_id}_ch{chapter_number}_{voice}.mp3",
    )


# ==================== READ LOG ROUTES ====================

class ReadLogCreate(BaseModel):
    student_id: str
    narrative_id: str
    chapter_number: int
    session_start: datetime
    session_end: datetime
    words_read: int
    vision_check_passed: Optional[bool] = None


@router.post("/read-logs")
async def create_read_log(log_data: ReadLogCreate):
    """Create a reading session log"""
    from models import ReadLog
    
    # Calculate duration and WPM
    duration = (log_data.session_end - log_data.session_start).total_seconds()
    wpm = (log_data.words_read / (duration / 60)) if duration > 0 and log_data.words_read > 0 else 0
    
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
    if log_data.vision_check_passed is not None:
        log_dict["vision_check_passed"] = log_data.vision_check_passed
    await db.read_logs.insert_one(log_dict)

    # Update narrative progress (chapters_completed, current_chapter, status)
    narrative = await db.narratives.find_one({"id": log_data.narrative_id})
    if narrative:
        chapters_completed = narrative.get("chapters_completed", [])
        if log_data.chapter_number not in chapters_completed:
            chapters_completed.append(log_data.chapter_number)
            chapters_completed = sorted(set(chapters_completed))

        total_chapters = len(narrative.get("chapters", []))
        new_current = max(chapters_completed) if chapters_completed else 1
        
        # Only mark as "completed" when ALL chapters are read AND assessment is done
        # Stories remain "in_progress" even if all chapters are read, until assessment
        all_chapters_read = len(chapters_completed) >= total_chapters and total_chapters > 0
        assessment = await db.assessments.find_one({"narrative_id": log_data.narrative_id, "status": "completed"})
        
        if all_chapters_read and assessment:
            new_status = "completed"
        elif len(chapters_completed) > 0:
            new_status = "in_progress"
        else:
            new_status = narrative.get("status", "ready")

        await db.narratives.update_one(
            {"id": log_data.narrative_id},
            {"$set": {
                "chapters_completed": chapters_completed,
                "current_chapter": new_current,
                "status": new_status,
            }}
        )

        # When narrative is completed, credit vocabulary from embedded tokens
        if new_status == "completed":
            student = await db.students.find_one({"id": log_data.student_id})
            if student:
                # Normalize existing tokens to plain strings
                existing_mastered = set()
                for t in student.get("mastered_tokens", []):
                    if isinstance(t, str):
                        existing_mastered.add(t.lower().strip())
                    elif isinstance(t, dict):
                        existing_mastered.add(t.get("token", "").lower().strip())
                
                new_tokens = set()
                for ch in narrative.get("chapters", []):
                    for token in ch.get("embedded_tokens", []):
                        word = token.get("word", "").lower().strip()
                        if word and word not in existing_mastered:
                            new_tokens.add(word)
                
                if new_tokens:
                    all_mastered = list(existing_mastered | new_tokens)
                    # Calculate agentic reach score
                    total_narratives = await db.narratives.count_documents({"student_id": log_data.student_id})
                    completed_narratives = await db.narratives.count_documents({"student_id": log_data.student_id, "status": "completed"})
                    score = round((len(all_mastered) * 10 + completed_narratives * 50) / max(total_narratives * 50, 1) * 100, 1)
                    score = min(score, 100.0)
                    
                    await db.students.update_one(
                        {"id": log_data.student_id},
                        {"$set": {
                            "mastered_tokens": all_mastered,
                            "agentic_reach_score": score,
                        }}
                    )

    # Update student reading statistics
    if log_data.words_read > 0:
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


@router.get("/read-logs")
async def get_read_logs(student_id: Optional[str] = None):
    """Get read logs, optionally filtered by student"""
    query = {}
    if student_id:
        query["student_id"] = student_id
    
    logs = await db.read_logs.find(query, {"_id": 0}).to_list(1000)
    return logs



class SaveProgressRequest(BaseModel):
    narrative_id: str
    student_id: str
    current_chapter: int
    scroll_position: float = 0


@router.post("/narratives/save-progress")
async def save_narrative_progress(data: SaveProgressRequest, current_user: dict = Depends(get_current_user)):
    """Save reading progress so student can resume later"""
    narrative = await db.narratives.find_one({"id": data.narrative_id})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    
    await db.narratives.update_one(
        {"id": data.narrative_id},
        {"$set": {
            "current_chapter": data.current_chapter,
            "last_read_date": datetime.now(timezone.utc).isoformat(),
            "scroll_position": data.scroll_position,
        }}
    )
    return {"message": "Progress saved", "current_chapter": data.current_chapter}


@router.get("/narratives/{narrative_id}/progress")
async def get_narrative_progress(narrative_id: str, current_user: dict = Depends(get_current_user)):
    """Get saved reading progress for a narrative"""
    narrative = await db.narratives.find_one({"id": narrative_id}, {"_id": 0, "current_chapter": 1, "chapters_completed": 1, "scroll_position": 1, "status": 1})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    return {
        "current_chapter": narrative.get("current_chapter", 1),
        "chapters_completed": narrative.get("chapters_completed", []),
        "scroll_position": narrative.get("scroll_position", 0),
        "status": narrative.get("status", "ready"),
    }


class WrittenAnswerEval(BaseModel):
    student_id: str
    chapter_number: int
    question: str
    student_answer: str
    chapter_summary: str = ""
    spelling_mode: str = "phonetic"  # "exact" or "phonetic"


@router.post("/assessments/evaluate-written")
async def evaluate_written_answer(data: WrittenAnswerEval):
    """Evaluate a written comprehension answer using AI"""
    from story_service import story_service
    story_service.set_db(db)
    llm_config = await story_service._get_llm_config()
    provider = llm_config.get("provider", "openrouter")
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
        from openai import AsyncOpenAI
        api_key = llm_config.get("openrouter_key") or os.environ.get("OPENROUTER_API_KEY")
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1", api_key=api_key,
            default_headers={"HTTP-Referer": "https://semanticvision.ai"},
            max_retries=1, timeout=30.0,
        )
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=500,
        )
        text = response.choices[0].message.content or ""

        text = text.strip()
        if "```" in text:
            import re
            json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1).strip()
            else:
                text = text.replace("```json", "").replace("```", "").strip()

        try:
            result = json_lib.loads(text)
        except json_lib.JSONDecodeError:
            import re
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                cleaned = json_match.group(0)
                cleaned = re.sub(r',\s*}', '}', cleaned)
                cleaned = re.sub(r',\s*]', ']', cleaned)
                result = json_lib.loads(cleaned)
            else:
                raise ValueError(f"No valid JSON in response: {text[:200]}")

        # Log spelling errors for the student
        if result.get("spelling_errors"):
            await db.spelling_logs.insert_one({
                "student_id": data.student_id,
                "chapter_number": data.chapter_number,
                "errors": result["spelling_errors"],
                "answer_text": data.student_answer,
                "created_date": datetime.now(timezone.utc).isoformat(),
            })

        # Save written answer for brand analytics (shows student engagement with content)
        await db.written_answers.insert_one({
            "student_id": data.student_id,
            "chapter_number": data.chapter_number,
            "question": data.question,
            "student_answer": data.student_answer,
            "passed": result.get("passed", False),
            "comprehension_score": result.get("comprehension_score", 0),
            "feedback": result.get("feedback", ""),
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


class OralAnswerEval(BaseModel):
    student_id: str
    chapter_number: int
    question: str
    audio_transcription: str
    chapter_summary: str = ""


@router.post("/assessments/evaluate-oral")
async def evaluate_oral_answer(data: OralAnswerEval):
    """Evaluate an oral/spoken comprehension answer using AI (more lenient, no spelling checks)"""
    from story_service import story_service
    story_service.set_db(db)
    llm_config = await story_service._get_llm_config()
    provider = llm_config.get("provider", "openrouter")
    model = llm_config.get("model", "gpt-5.2")

    prompt = f"""Evaluate this student's ORAL (spoken) answer to a reading comprehension question.
The answer was transcribed from speech, so ignore any spelling errors, grammatical mistakes,
or informal language. Focus ONLY on whether the student demonstrates comprehension of the content.

Question: {data.question}
Student's Spoken Answer (transcribed): {data.audio_transcription}
Chapter Context (first 500 chars): {data.chapter_summary}

Evaluation criteria (lenient — this is a spoken answer):
1. Does the answer demonstrate understanding of the chapter content?
2. Is the answer relevant to the question?
3. Do NOT check spelling — this was transcribed from speech.
4. Accept informal language, incomplete sentences, and filler words.
5. Be encouraging — oral answers are harder for some students.

Return ONLY valid JSON:
{{
  "passed": true/false,
  "feedback": "brief encouraging feedback",
  "comprehension_score": 0-100
}}"""

    try:
        from openai import AsyncOpenAI
        api_key = llm_config.get("openrouter_key") or os.environ.get("OPENROUTER_API_KEY")
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1", api_key=api_key,
            default_headers={"HTTP-Referer": "https://semanticvision.ai"},
            max_retries=1, timeout=30.0,
        )
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=500,
        )
        text = response.choices[0].message.content or ""

        text = text.strip()
        if "```" in text:
            import re
            json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1).strip()
            else:
                text = text.replace("```json", "").replace("```", "").strip()

        try:
            result = json_lib.loads(text)
        except json_lib.JSONDecodeError:
            import re
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                cleaned = json_match.group(0)
                cleaned = re.sub(r',\s*}', '}', cleaned)
                cleaned = re.sub(r',\s*]', ']', cleaned)
                result = json_lib.loads(cleaned)
            else:
                raise ValueError(f"No valid JSON in response: {text[:200]}")

        # Ensure no spelling_errors key in oral responses
        result.pop("spelling_errors", None)

        # Save oral answer for analytics
        await db.oral_answers.insert_one({
            "student_id": data.student_id,
            "chapter_number": data.chapter_number,
            "question": data.question,
            "audio_transcription": data.audio_transcription,
            "passed": result.get("passed", False),
            "comprehension_score": result.get("comprehension_score", 0),
            "feedback": result.get("feedback", ""),
            "created_date": datetime.now(timezone.utc).isoformat(),
        })

        return result

    except Exception as e:
        logger.error(f"Oral answer evaluation failed: {str(e)}")
        # Lenient fallback — pass if transcription has enough words
        word_count = len(data.audio_transcription.split())
        return {
            "passed": word_count >= 3,
            "feedback": "Great job speaking your answer! Keep reading!" if word_count >= 3 else "Try to say a bit more about what you read.",
            "comprehension_score": 65 if word_count >= 3 else 30,
        }


# ==================== ADMIN SPELLING & LIMITS CONFIG ====================

@router.get("/admin/settings")
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


@router.post("/admin/settings")
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


@router.post("/students/{student_id}/spellcheck")
async def update_student_spellcheck(
    student_id: str,
    current_user: dict = Depends(get_current_guardian)
):
    """Toggle spellcheck for a specific student"""
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if current_user.get("role") != "admin" and student["guardian_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    current = student.get("spellcheck_disabled", False)
    await db.students.update_one(
        {"id": student_id},
        {"$set": {"spellcheck_disabled": not current}}
    )
    return {"spellcheck_disabled": not current}


@router.post("/students/{student_id}/spelling-mode")
async def update_student_spelling_mode(
    student_id: str,
    current_user: dict = Depends(get_current_guardian)
):
    """Toggle spelling mode between exact and phonetic for a student"""
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if current_user.get("role") != "admin" and student["guardian_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    current = student.get("spelling_mode", "phonetic")
    new_mode = "exact" if current == "phonetic" else "phonetic"
    await db.students.update_one(
        {"id": student_id},
        {"$set": {"spelling_mode": new_mode}}
    )
    return {"spelling_mode": new_mode}


@router.get("/students/{student_id}/spelling-logs")
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


@router.post("/assessments")
async def create_assessment(assessment_data: AssessmentCreate):
    """Create a vocabulary assessment for a completed narrative"""
    from models import Assessment, AssessmentQuestion, AssessmentType, QuestionType
    
    # Get narrative
    narrative = await db.narratives.find_one({"id": assessment_data.narrative_id})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")
    
    # Clean up any stuck in_progress assessments for this narrative+student
    await db.assessments.delete_many({
        "student_id": assessment_data.student_id,
        "narrative_id": assessment_data.narrative_id,
        "status": "in_progress",
    })
    
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


@router.post("/assessments/{assessment_id}/evaluate")
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
        provider = llm_config.get("provider", "openrouter")
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

        from openai import AsyncOpenAI
        api_key = llm_config.get("openrouter_key") or os.environ.get("OPENROUTER_API_KEY")
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1", api_key=api_key,
            default_headers={"HTTP-Referer": "https://semanticvision.ai"},
            max_retries=1, timeout=60.0,
        )
        response_obj = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=4000,
        )
        response = response_obj.choices[0].message.content or ""

        # Parse response — robust JSON extraction
        text = response.strip()
        # Strip markdown code blocks
        if "```" in text:
            import re
            json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1).strip()
            else:
                text = text.replace("```json", "").replace("```", "").strip()

        # Try to extract JSON object
        try:
            evaluation = json_lib.loads(text)
        except json_lib.JSONDecodeError:
            # Try to find JSON object within text
            import re
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                try:
                    evaluation = json_lib.loads(json_match.group(0))
                except json_lib.JSONDecodeError:
                    # Last resort: truncate at the last valid closing brace
                    raw = json_match.group(0)
                    # Fix common LLM JSON issues: trailing commas, unescaped quotes
                    raw = re.sub(r',\s*}', '}', raw)
                    raw = re.sub(r',\s*]', ']', raw)
                    evaluation = json_lib.loads(raw)
            else:
                raise ValueError(f"No valid JSON found in LLM response: {text[:200]}")
        
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
                # Normalize existing tokens to plain strings
                existing_tokens = set()
                for t in student.get("mastered_tokens", []):
                    if isinstance(t, str):
                        existing_tokens.add(t.lower().strip())
                    elif isinstance(t, dict):
                        existing_tokens.add(t.get("token", "").lower().strip())
                
                new_tokens = []
                for word in tokens_mastered:
                    w = word.lower().strip()
                    if w and w not in existing_tokens:
                        new_tokens.append(w)
                
                if new_tokens:
                    # Store all tokens as plain strings consistently
                    all_mastered = list(existing_tokens | set(new_tokens))
                    
                    # Recalculate agentic reach score
                    total_narratives = await db.narratives.count_documents({"student_id": assessment["student_id"]})
                    completed_narratives = await db.narratives.count_documents({"student_id": assessment["student_id"], "status": "completed"})
                    agentic_score = round((len(all_mastered) * 10 + completed_narratives * 50) / max(total_narratives * 50, 1) * 100, 1)
                    agentic_score = min(agentic_score, 100.0)
                    
                    await db.students.update_one(
                        {"id": assessment["student_id"]},
                        {"$set": {
                            "mastered_tokens": all_mastered,
                            "agentic_reach_score": agentic_score,
                        }}
                    )
        
        # Return updated assessment
        updated_assessment = await db.assessments.find_one({"id": assessment_id}, {"_id": 0})
        return updated_assessment
        
    except Exception as e:
        logger.error(f"Assessment evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/assessments")
async def get_assessments(student_id: Optional[str] = None, narrative_id: Optional[str] = None):
    """Get assessments with optional filters"""
    query = {}
    if student_id:
        query["student_id"] = student_id
    if narrative_id:
        query["narrative_id"] = narrative_id
    
    assessments = await db.assessments.find(query, {"_id": 0}).to_list(1000)
    return assessments


@router.get("/assessments/{assessment_id}")
async def get_assessment(assessment_id: str):
    """Get a specific assessment"""
    assessment = await db.assessments.find_one({"id": assessment_id}, {"_id": 0})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


# ==================== DIFFICULTY ADJUSTMENT ROUTES ====================

# Grade ordering for difficulty comparison
GRADE_ORDER = [
    "pre-k", "k", "1", "2", "3", "4", "5", "6",
    "7", "8", "9", "10", "11", "12", "college", "adult",
]


def _grade_to_index(grade_str: str) -> int:
    """Convert a grade string to a numeric index for comparison."""
    grade_str = str(grade_str).lower().strip()
    try:
        return GRADE_ORDER.index(grade_str)
    except ValueError:
        # If it looks numeric, try matching
        for i, g in enumerate(GRADE_ORDER):
            if g == grade_str:
                return i
        return 99  # Unknown grades sort to the end


def _bank_difficulty_score(bank: dict) -> int:
    """Score a word bank's difficulty based on its grade_range and word counts."""
    grade_range = bank.get("grade_range", {})
    min_grade = grade_range.get("min", "1")
    max_grade = grade_range.get("max", "12")
    # Use the average of min and max grade index as the primary score
    min_idx = _grade_to_index(min_grade)
    max_idx = _grade_to_index(max_grade)
    # Secondary: more stretch words = harder
    stretch_count = len(bank.get("stretch_words", []))
    return (min_idx + max_idx) * 100 + stretch_count


class DifficultyFeedbackRequest(BaseModel):
    feedback: str  # "too_hard", "too_easy", "just_right"


@router.post("/narratives/{narrative_id}/difficulty-feedback")
async def submit_difficulty_feedback(
    narrative_id: str,
    data: DifficultyFeedbackRequest,
    current_user: dict = Depends(get_current_user),
):
    """Record difficulty feedback without regenerating the story."""
    if data.feedback not in ("too_hard", "too_easy", "just_right"):
        raise HTTPException(status_code=400, detail="feedback must be 'too_hard', 'too_easy', or 'just_right'")

    narrative = await db.narratives.find_one({"id": narrative_id}, {"_id": 0, "student_id": 1})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")

    await db.difficulty_feedback.insert_one({
        "id": str(uuid.uuid4()),
        "student_id": narrative["student_id"],
        "narrative_id": narrative_id,
        "feedback": data.feedback,
        "created_date": datetime.now(timezone.utc).isoformat(),
    })

    return {"message": "Feedback recorded", "feedback": data.feedback}


@router.post("/narratives/{narrative_id}/too-hard")
async def report_too_hard(
    narrative_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Student reports story is too hard. Find an easier word bank and regenerate."""
    # Get the narrative
    narrative = await db.narratives.find_one({"id": narrative_id}, {"_id": 0})
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found")

    student_id = narrative["student_id"]
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get all word banks assigned to this student
    assigned_bank_ids = student.get("assigned_banks", [])
    if not assigned_bank_ids:
        raise HTTPException(status_code=400, detail="Student has no assigned word banks")

    # Fetch all assigned banks
    assigned_banks = []
    for bid in assigned_bank_ids:
        bank = await db.word_banks.find_one({"id": bid}, {"_id": 0})
        if bank:
            assigned_banks.append(bank)

    if not assigned_banks:
        raise HTTPException(status_code=400, detail="No valid word banks found")

    # Sort banks by difficulty score
    assigned_banks.sort(key=lambda b: _bank_difficulty_score(b))

    # Determine which banks the current narrative used
    current_bank_ids = set(narrative.get("bank_ids", []))
    current_scores = [_bank_difficulty_score(b) for b in assigned_banks if b["id"] in current_bank_ids]
    min_current_score = min(current_scores) if current_scores else 0

    # Find an easier bank (lower difficulty score than the easiest currently used)
    easier_bank = None
    for bank in assigned_banks:
        if _bank_difficulty_score(bank) < min_current_score and bank["id"] not in current_bank_ids:
            easier_bank = bank
            break

    # If no strictly easier bank, check if the easiest assigned bank is not already in use
    if not easier_bank:
        easiest = assigned_banks[0]
        if easiest["id"] not in current_bank_ids:
            easier_bank = easiest

    if not easier_bank:
        # Record the feedback anyway
        await db.difficulty_feedback.insert_one({
            "id": str(uuid.uuid4()),
            "student_id": student_id,
            "narrative_id": narrative_id,
            "feedback": "too_hard",
            "action": "no_easier_bank",
            "created_date": datetime.now(timezone.utc).isoformat(),
        })
        return {
            "message": "You're already at the easiest level. Keep trying — you've got this!",
            "new_narrative_id": None,
            "already_easiest": True,
        }

    # Mark original narrative as difficulty-adjusted
    await db.narratives.update_one(
        {"id": narrative_id},
        {"$set": {"difficulty_adjusted": True}}
    )

    # Generate a NEW story with the easier bank, same theme/prompt
    theme = narrative.get("theme", "an adventure story")
    try:
        new_narrative_data = NarrativeCreate(
            student_id=student_id,
            prompt=theme,
            bank_ids=[easier_bank["id"]],
            personalized=True,
        )
        new_narrative = await create_narrative(new_narrative_data)
        new_narrative_id = new_narrative.id if hasattr(new_narrative, "id") else (new_narrative.get("id") if isinstance(new_narrative, dict) else None)
    except Exception as e:
        logger.error(f"Easier story generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate easier story: {str(e)}")

    # Record difficulty feedback with the action taken
    await db.difficulty_feedback.insert_one({
        "id": str(uuid.uuid4()),
        "student_id": student_id,
        "narrative_id": narrative_id,
        "feedback": "too_hard",
        "action": "regenerated",
        "new_narrative_id": new_narrative_id,
        "easier_bank_id": easier_bank["id"],
        "created_date": datetime.now(timezone.utc).isoformat(),
    })

    # Notify guardian that student found story too hard
    guardian_id = student.get("guardian_id")
    if guardian_id:
        student_name = student.get("full_name", "Your child")
        await db.notifications.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": guardian_id,
            "type": "difficulty_report",
            "title": "Difficulty Adjustment",
            "message": f"{student_name} found their story too hard and requested an easier version.",
            "read": False,
            "created_date": datetime.now(timezone.utc).isoformat(),
        })

    return {
        "message": "An easier version of this story has been created!",
        "new_narrative_id": new_narrative_id,
        "already_easiest": False,
    }


