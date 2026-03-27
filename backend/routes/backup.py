"""Backup & Restore routes: Full database export/import for admin."""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
from bson import ObjectId
import json, io, re

from database import db, logger
from auth import get_current_admin

router = APIRouter()

# Collections to always back up (all app data)
BACKUP_COLLECTIONS = [
    "users", "students", "subscriptions", "subscription_plans",
    "word_banks", "narratives", "assessments", "read_logs",
    "brands", "brand_campaigns", "brand_impressions", "brand_media", "brand_offers", "brandoffers",
    "affiliates", "affiliate_referrals", "affiliate_payouts",
    "coupons", "coupon_redemptions",
    "payment_transactions", "wallet_transactions", "donations",
    "cost_logs", "system_config",
    "classroom_sessions", "classroom_sponsorships",
    "admin_messages", "support_tickets", "support_sessions",
    "referrals", "referral_contests",
    "spelling_contests", "spelling_submissions",
    "session_logs", "user_offer_preferences",
    "email_verifications", "password_resets",
]


class MongoJSONEncoder(json.JSONEncoder):
    """Handle MongoDB-specific types like ObjectId and datetime."""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def _default_backup_filename() -> str:
    """Generate the default backup filename with current UTC timestamp."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"semantic_vision_backup_{date_str}"


def _sanitize_filename(name: str) -> str:
    """Sanitize a user-provided filename (strip extension, remove unsafe chars)."""
    # Remove .json extension if user included it
    if name.lower().endswith(".json"):
        name = name[:-5]
    # Allow only alphanumeric, dashes, underscores, and dots
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    return name or _default_backup_filename()


@router.get("/admin/backup")
async def download_backup(
    current_user: dict = Depends(get_current_admin),
    filename: str = Query(None, description="Custom filename for the backup (without .json extension)"),
):
    """Download a full database backup as JSON."""
    logger.info(f"Backup requested by {current_user.get('email')}")

    backup_data = {
        "_meta": {
            "app": "Semantic Vision",
            "backup_date": datetime.now(timezone.utc).isoformat(),
            "backed_up_by": current_user.get("email", "admin"),
            "version": "2.0.0",
        },
        "collections": {},
    }

    total_docs = 0
    for collection_name in BACKUP_COLLECTIONS:
        try:
            collection = db[collection_name]
            docs = await collection.find({}).to_list(100000)
            # Convert ObjectId to string for JSON serialization
            clean_docs = []
            for doc in docs:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                clean_docs.append(doc)
            backup_data["collections"][collection_name] = clean_docs
            total_docs += len(clean_docs)
        except Exception as e:
            logger.warning(f"Backup: skipping {collection_name}: {e}")

    backup_data["_meta"]["total_documents"] = total_docs
    backup_data["_meta"]["total_collections"] = len(backup_data["collections"])

    logger.info(f"Backup complete: {total_docs} documents across {len(backup_data['collections'])} collections")

    # Stream as JSON download
    json_bytes = json.dumps(backup_data, cls=MongoJSONEncoder, indent=2).encode("utf-8")

    if filename:
        safe_name = _sanitize_filename(filename)
    else:
        safe_name = _default_backup_filename()
    download_filename = f"{safe_name}.json"

    return StreamingResponse(
        io.BytesIO(json_bytes),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={download_filename}"},
    )


@router.get("/admin/backup/info")
async def backup_info(current_user: dict = Depends(get_current_admin)):
    """Get the default backup filename and estimated file size so the frontend can preview before downloading."""
    default_name = _default_backup_filename()

    # Estimate size by counting documents and approximating bytes per doc
    total_docs = 0
    collection_counts = {}
    for collection_name in BACKUP_COLLECTIONS:
        try:
            count = await db[collection_name].count_documents({})
            if count > 0:
                collection_counts[collection_name] = count
                total_docs += count
        except Exception:
            pass

    # Rough estimate: ~500 bytes per document on average (JSON with indent)
    estimated_bytes = total_docs * 500
    if estimated_bytes < 1024:
        size_display = f"{estimated_bytes} B"
    elif estimated_bytes < 1024 * 1024:
        size_display = f"{estimated_bytes / 1024:.1f} KB"
    else:
        size_display = f"{estimated_bytes / (1024 * 1024):.1f} MB"

    return {
        "default_filename": f"{default_name}.json",
        "estimated_size_bytes": estimated_bytes,
        "estimated_size_display": size_display,
        "total_documents": total_docs,
        "total_collections": len(collection_counts),
    }


@router.get("/admin/backup/status")
async def backup_status(current_user: dict = Depends(get_current_admin)):
    """Get current database stats for backup preview."""
    stats = {}
    total = 0
    for collection_name in BACKUP_COLLECTIONS:
        try:
            count = await db[collection_name].count_documents({})
            if count > 0:
                stats[collection_name] = count
                total += count
        except Exception:
            pass

    return {
        "total_documents": total,
        "collections": stats,
        "total_collections": len(stats),
    }


@router.post("/admin/restore")
async def restore_backup(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_admin),
):
    """Restore database from a backup JSON file. Merges data (upsert by 'id' field)."""
    logger.info(f"Restore requested by {current_user.get('email')}")

    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json backup files are accepted")

    try:
        content = await file.read()
        backup_data = json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")

    if "collections" not in backup_data:
        raise HTTPException(status_code=400, detail="Invalid backup format: missing 'collections' key")

    results = {}
    total_restored = 0
    total_skipped = 0

    for collection_name, docs in backup_data["collections"].items():
        if collection_name.startswith("_"):
            continue  # skip metadata

        collection = db[collection_name]
        restored = 0
        skipped = 0

        for doc in docs:
            # Remove MongoDB _id to avoid conflicts
            doc.pop("_id", None)

            doc_id = doc.get("id")
            if doc_id:
                # Upsert: update if exists, insert if not
                existing = await collection.find_one({"id": doc_id})
                if existing:
                    await collection.replace_one({"id": doc_id}, doc)
                    skipped += 1  # updated existing
                else:
                    await collection.insert_one(doc)
                    restored += 1
            else:
                # No id field - just insert
                await collection.insert_one(doc)
                restored += 1

        results[collection_name] = {"restored": restored, "updated": skipped}
        total_restored += restored
        total_skipped += skipped

    logger.info(f"Restore complete: {total_restored} new, {total_skipped} updated")

    return {
        "status": "success",
        "total_new_documents": total_restored,
        "total_updated_documents": total_skipped,
        "details": results,
        "backup_meta": backup_data.get("_meta", {}),
    }
