"""Semantic Vision API -- Main Application Entry Point (Refactored)

This file serves as the thin orchestrator that:
1. Creates the FastAPI application
2. Configures middleware (CORS, static files)
3. Imports and includes all route modules
4. Handles startup/shutdown lifecycle events

Route implementations are in /routes/*.py
Database connection is in database.py
Shared services are in services.py
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
import os, logging
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== APP CREATION ====================
app = FastAPI(title="Semantic Vision API", version="2.0.0")

# ==================== CORS MIDDLEWARE ====================
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== STATIC FILES ====================
_upload_root = Path(__file__).parent / "uploads"
_upload_root.mkdir(parents=True, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=str(_upload_root)), name="uploads")

# ==================== IMPORT ROUTE MODULES ====================
from routes.auth import router as auth_router
from routes.students import router as students_router
from routes.wordbanks import router as wordbanks_router
from routes.narratives import router as narratives_router
from routes.classroom import router as classroom_router
from routes.admin import router as admin_router
from routes.brands import router as brands_router
from routes.documents import router as documents_router
from routes.affiliates import router as affiliates_router
from routes.recordings import router as recordings_router
from routes.paypal import router as paypal_router
from routes.media import router as media_router
from routes.support import router as support_router
from routes.sessions import router as sessions_router
from routes.backup import router as backup_router

# ==================== INCLUDE ALL ROUTERS ====================
app.include_router(auth_router, prefix="/api")
app.include_router(students_router, prefix="/api")
app.include_router(wordbanks_router, prefix="/api")
app.include_router(narratives_router, prefix="/api")
app.include_router(classroom_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(brands_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(affiliates_router, prefix="/api")
app.include_router(recordings_router, prefix="/api")
app.include_router(paypal_router, prefix="/api")
app.include_router(media_router, prefix="/api")
app.include_router(support_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")
app.include_router(backup_router, prefix="/api")

# ==================== LIFECYCLE EVENTS ====================
from database import db, client

# ===== HEALTH CHECK (no auth required) =====
@app.get("/api/diagnostics")
async def diagnostics_check():
    """Public health check - shows DB status and bootstrap state."""
    try:
        user_count = await db.users.count_documents({})
        wb_count = await db.word_banks.count_documents({})
        admin_exists = await db.users.find_one({"email": "allen@songsforcenturies.com"}, {"_id": 0, "id": 1, "role": 1})
        collections = await db.list_collection_names()
        return {
            "status": "ok",
            "database": "connected",
            "users": user_count,
            "word_banks": wb_count,
            "admin_exists": bool(admin_exists),
            "admin_role": admin_exists.get("role") if admin_exists else None,
            "collections": len(collections),
        }
    except Exception as e:
        return {"status": "error", "database": "disconnected", "error": str(e)}


@app.on_event("startup")
async def startup_migrate():
    """Run startup migrations and bootstrap essential data if DB is empty."""
    try:
        from models import (
            generate_student_code, generate_referral_code, generate_uuid,
            User, UserRole, Subscription, SubscriptionPlan,
        )
        from auth import get_password_hash

        # ===== BOOTSTRAP: Create master admin if not exists =====
        master_email = "allen@songsforcenturies.com"
        master_user = await db.users.find_one({"email": master_email})
        if not master_user:
            logger.info(f"BOOTSTRAP: Master admin not found — creating {master_email}")
            admin_user = User(
                email=master_email,
                full_name="Allen",
                password_hash=get_password_hash("LexiAdmin2026!"),
                role=UserRole.ADMIN,
                is_delegated_admin=True,
            )
            user_dict = admin_user.model_dump()
            await db.users.insert_one(user_dict)
            logger.info(f"BOOTSTRAP: Admin user inserted with id={admin_user.id}")
            # Create subscription for admin
            sub = Subscription(
                guardian_id=admin_user.id,
                plan=SubscriptionPlan.FREE,
                student_seats=10,
                active_students=0,
            )
            await db.subscriptions.insert_one(sub.model_dump())
            logger.info(f"BOOTSTRAP: Created master admin + subscription: {master_email}")
        elif master_user.get("role") != "admin":
            await db.users.update_one(
                {"email": master_email},
                {"$set": {"role": "admin", "is_delegated_admin": True}}
            )
            logger.info(f"Promoted {master_email} to admin")
        else:
            logger.info(f"Master admin already exists: {master_email}")

        # ===== BOOTSTRAP: Seed word banks if none exist =====
        wb_count = await db.word_banks.count_documents({})
        if wb_count == 0:
            logger.info("BOOTSTRAP: No word banks found — seeding defaults...")
            from seed_word_banks import SAMPLE_WORD_BANKS
            for bank in SAMPLE_WORD_BANKS:
                bank["id"] = generate_uuid()
                await db.word_banks.insert_one(bank)
                logger.info(f"  Seeded word bank: {bank['name']}")
            logger.info(f"BOOTSTRAP: Seeded {len(SAMPLE_WORD_BANKS)} word banks.")
        else:
            logger.info(f"Word banks already exist: {wb_count}")

        # ===== MIGRATIONS: Ensure fields on existing data =====
        await db.users.update_many(
            {"wallet_balance": {"$exists": False}},
            {"$set": {"wallet_balance": 0.0}}
        )

        cursor_users = db.users.find({"referral_code": {"$exists": False}}, {"_id": 0, "id": 1})
        async for u in cursor_users:
            await db.users.update_one({"id": u["id"]}, {"$set": {"referral_code": generate_referral_code()}})

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

        # ===== ENSURE DB INDEXES =====
        try:
            await db.users.create_index("email", unique=True, background=True)
            await db.users.create_index("id", background=True)
            await db.students.create_index("guardian_id", background=True)
            await db.students.create_index("student_code", background=True)
            await db.students.create_index("id", background=True)
            await db.word_banks.create_index("id", background=True)
            await db.narratives.create_index("student_id", background=True)
            await db.session_logs.create_index("student_id", background=True)
            await db.session_logs.create_index([("student_id", 1), ("ended_at", 1)], background=True)
        except Exception as e:
            logger.warning(f"Index creation warning (non-fatal): {e}")

        logger.info("Startup migrations complete. All routers loaded.")

    except Exception as e:
        logger.error(f"STARTUP BOOTSTRAP FAILED: {e}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
