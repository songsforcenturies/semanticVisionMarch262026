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

# ==================== LIFECYCLE EVENTS ====================
from database import db, client

@app.on_event("startup")
async def startup_migrate():
    """Run startup migrations"""
    from models import generate_student_code, generate_referral_code

    # Ensure master admin role
    master_email = "allen@songsforcenturies.com"
    master_user = await db.users.find_one({"email": master_email})
    if master_user and master_user.get("role") != "admin":
        await db.users.update_one(
            {"email": master_email},
            {"$set": {"role": "admin", "is_delegated_admin": True}}
        )
        logger.info(f"Promoted {master_email} to admin")

    # Ensure wallet_balance field on all users
    await db.users.update_many(
        {"wallet_balance": {"$exists": False}},
        {"$set": {"wallet_balance": 0.0}}
    )

    # Ensure referral_code on all users
    cursor_users = db.users.find({"referral_code": {"$exists": False}}, {"_id": 0, "id": 1})
    async for u in cursor_users:
        await db.users.update_one({"id": u["id"]}, {"$set": {"referral_code": generate_referral_code()}})

    # Migrate existing students that are missing student_code
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

    logger.info("Startup migrations complete. All routers loaded.")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
