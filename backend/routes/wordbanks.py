"""Word bank routes: CRUD, marketplace, purchase, assignment."""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid

from database import db, logger
from models import (
    WordBank, WordBankCreate, UserRole,
    WalletTransaction, WalletTransactionType,
    Subscription, SubscriptionPlan,
)
from auth import get_current_user, get_current_admin, get_current_guardian

router = APIRouter()

# ==================== SUBSCRIPTION ROUTES ====================

@router.get("/subscriptions/{guardian_id}", response_model=Subscription)
async def get_subscription(
    guardian_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get guardian's subscription — auto-creates a free plan if missing"""
    subscription = await db.subscriptions.find_one({"guardian_id": guardian_id}, {"_id": 0})
    if not subscription:
        # Auto-create a free subscription for guardians who don't have one
        active_students = await db.students.count_documents({"guardian_id": guardian_id})
        new_sub = Subscription(
            guardian_id=guardian_id,
            plan=SubscriptionPlan.FREE,
            student_seats=10,
            active_students=active_students,
        )
        await db.subscriptions.insert_one(new_sub.model_dump())
        subscription = new_sub.model_dump()
    return subscription


# ==================== WORD BANK ROUTES ====================

@router.post("/word-banks", response_model=WordBank)
async def create_word_bank(
    bank_data: WordBankCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new word bank (admin always, guardians if feature flag enabled)"""
    role = current_user.get("role")
    if role == "admin":
        pass  # admins can always create
    elif role == "guardian":
        flags = await db.system_config.find_one({"key": "feature_flags"}, {"_id": 0})
        enabled = flags.get("value", {}).get("parent_wordbank_creation_enabled", False) if flags else False
        if not enabled:
            raise HTTPException(status_code=403, detail="Word bank creation is currently disabled for parents. Contact your admin.")
    else:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_tokens = len(bank_data.baseline_words) + len(bank_data.target_words) + len(bank_data.stretch_words)
    
    bank_dict = bank_data.model_dump()
    # Force parent-created word banks to be private
    if role == "guardian":
        bank_dict["visibility"] = "private"
    
    word_bank = WordBank(
        **bank_dict,
        owner_id=current_user["id"],
        created_by_role=role,
        total_tokens=total_tokens
    )
    
    wb_dict = word_bank.model_dump()
    await db.word_banks.insert_one(wb_dict)
    
    return word_bank


@router.get("/word-banks")
async def get_word_banks(
    visibility: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "name",
    current_user: dict = Depends(get_current_user)
):
    """Get word banks with filtering. Parents see global banks + their own private banks only."""
    role = current_user.get("role")
    
    if role == "admin":
        # Admins see everything
        query = {}
    else:
        # Parents/others: see global/marketplace banks + their own private banks
        query = {"$or": [
            {"visibility": {"$in": ["global", "marketplace"]}},
            {"owner_id": current_user["id"], "visibility": "private"},
        ]}
    
    if visibility:
        if role == "admin":
            query["visibility"] = visibility
        # For non-admins, visibility filter is already handled above
    if category:
        query["category"] = category
    if search:
        search_filter = {"$or": [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"specialty": {"$regex": search, "$options": "i"}}
        ]}
        if query:
            query = {"$and": [query, search_filter]}
        else:
            query = search_filter
    
    sort_field = sort_by if sort_by in ["name", "category", "price", "created_date", "purchase_count"] else "name"
    word_banks = await db.word_banks.find(query, {"_id": 0}).sort(sort_field, 1).to_list(1000)
    return word_banks


@router.get("/word-banks/{bank_id}", response_model=WordBank)
async def get_word_bank(bank_id: str):
    """Get a specific word bank"""
    word_bank = await db.word_banks.find_one({"id": bank_id})
    if not word_bank:
        raise HTTPException(status_code=404, detail="Word bank not found")
    return word_bank


@router.delete("/word-banks/{bank_id}")
async def delete_word_bank(bank_id: str, current_user: dict = Depends(get_current_admin)):
    """Delete a word bank (admin only)"""
    result = await db.word_banks.delete_one({"id": bank_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Word bank not found")
    return {"message": "Word bank deleted"}


class WordBankUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    specialty: Optional[str] = None
    visibility: Optional[str] = None
    price: Optional[int] = None
    baseline_words: Optional[List[Dict[str, str]]] = None
    target_words: Optional[List[Dict[str, str]]] = None
    stretch_words: Optional[List[Dict[str, str]]] = None


@router.put("/word-banks/{bank_id}")
async def update_word_bank(bank_id: str, data: WordBankUpdate, current_user: dict = Depends(get_current_user)):
    """Edit a word bank. Admins can edit any. Parents can only edit their own private banks."""
    bank = await db.word_banks.find_one({"id": bank_id})
    if not bank:
        raise HTTPException(status_code=404, detail="Word bank not found")
    
    role = current_user.get("role")
    if role != "admin":
        if bank.get("owner_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to edit this word bank")
        if bank.get("created_by_role") != "guardian":
            raise HTTPException(status_code=403, detail="Can only edit your own word banks")
    
    update_fields = {k: v for k, v in data.model_dump().items() if v is not None}
    
    # Parents cannot change visibility from private
    if role == "guardian" and "visibility" in update_fields:
        update_fields["visibility"] = "private"
    
    # Recalculate total_tokens if words changed
    if any(k in update_fields for k in ["baseline_words", "target_words", "stretch_words"]):
        bl = update_fields.get("baseline_words", bank.get("baseline_words", []))
        tg = update_fields.get("target_words", bank.get("target_words", []))
        st = update_fields.get("stretch_words", bank.get("stretch_words", []))
        update_fields["total_tokens"] = len(bl) + len(tg) + len(st)
    
    if update_fields:
        await db.word_banks.update_one({"id": bank_id}, {"$set": update_fields})
    
    updated = await db.word_banks.find_one({"id": bank_id}, {"_id": 0})
    return updated


class PurchaseRequest(BaseModel):
    guardian_id: str
    bank_id: str


@router.post("/word-banks/purchase")
async def purchase_word_bank(
    request: PurchaseRequest,
    current_user: dict = Depends(get_current_guardian)
):
    """Purchase a word bank (add to subscription)"""
    # Verify bank exists
    word_bank = await db.word_banks.find_one({"id": request.bank_id})
    if not word_bank:
        raise HTTPException(status_code=404, detail="Word bank not found")
    
    # Get subscription
    subscription = await db.subscriptions.find_one({"guardian_id": request.guardian_id})
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Check if already purchased
    if request.bank_id in subscription.get("bank_access", []):
        raise HTTPException(status_code=400, detail="Word bank already purchased")
    
    # Add to subscription (for now, free - can add payment later)
    await db.subscriptions.update_one(
        {"guardian_id": request.guardian_id},
        {"$push": {"bank_access": request.bank_id}}
    )
    
    # Increment purchase count
    await db.word_banks.update_one(
        {"id": request.bank_id},
        {"$inc": {"purchase_count": 1}}
    )
    
    return {"message": "Word bank purchased successfully", "bank_id": request.bank_id}


class AssignBanksRequest(BaseModel):
    student_id: str
    bank_ids: List[str]


@router.post("/students/assign-banks")
async def assign_word_banks(
    request: AssignBanksRequest,
    current_user: dict = Depends(get_current_guardian)
):
    """Assign word banks to a student"""
    # Verify student exists
    student = await db.students.find_one({"id": request.student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get guardian's subscription to verify access
    subscription = await db.subscriptions.find_one({"guardian_id": student["guardian_id"]})
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Verify guardian has access to all requested banks
    available_banks = subscription.get("bank_access", [])
    for bank_id in request.bank_ids:
        if bank_id not in available_banks:
            bank = await db.word_banks.find_one({"id": bank_id})
            # Allow global/free banks
            if not bank or bank.get("visibility") not in ["global", "marketplace"]:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Guardian does not have access to bank {bank_id}"
                )
    
    # Update student's assigned banks
    await db.students.update_one(
        {"id": request.student_id},
        {"$set": {"assigned_banks": request.bank_ids}}
    )
    
    updated_student = await db.students.find_one({"id": request.student_id}, {"_id": 0})
    return updated_student


