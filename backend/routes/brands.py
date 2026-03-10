"""Brand management, analytics, portal, campaigns, offers routes."""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Form, Request
from fastapi.responses import JSONResponse
from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid, os, json as json_lib, re, random

from database import db, logger
from models import (
    UserRole, Brand, BrandProduct, BrandImpression, BrandCampaign,
    BrandOffer, UserOfferPreference,
    ClassroomSponsorship, TargetRegion, PaymentTransaction,
)
from auth import get_current_user, get_current_admin, get_current_guardian, get_current_brand_partner
from story_service import story_service
import stripe

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

router = APIRouter()

# ==================== BRAND MANAGEMENT (ADMIN) ====================

class BrandCreate(BaseModel):
    name: str
    logo_url: str = ""
    website: str = ""
    description: str = ""
    products: list = []
    target_ages: list = []
    target_categories: list = []
    budget_total: float = 0.0
    cost_per_impression: float = 0.05


@router.post("/admin/brands")
async def create_brand(data: BrandCreate, current_user: dict = Depends(get_current_user)):
    """Create a brand sponsor"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    brand = Brand(
        name=data.name, logo_url=data.logo_url, website=data.website,
        description=data.description,
        products=[BrandProduct(**p) if isinstance(p, dict) else p for p in data.products],
        target_ages=data.target_ages, target_categories=data.target_categories,
        budget_total=data.budget_total, cost_per_impression=data.cost_per_impression,
        created_by=current_user["id"],
    )
    await db.brands.insert_one(brand.model_dump())
    result = brand.model_dump()
    return result


@router.get("/admin/brands")
async def list_brands(current_user: dict = Depends(get_current_user)):
    """List all brands"""
    if current_user.get("role") != "admin":
        user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
        if not user or not user.get("is_delegated_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
    brands = await db.brands.find({}, {"_id": 0}).sort("created_date", -1).to_list(100)
    return brands


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    products: Optional[list] = None
    target_ages: Optional[list] = None
    target_categories: Optional[list] = None
    budget_total: Optional[float] = None
    cost_per_impression: Optional[float] = None
    is_active: Optional[bool] = None


@router.put("/admin/brands/{brand_id}")
async def update_brand(brand_id: str, data: BrandUpdate, current_user: dict = Depends(get_current_user)):
    """Update a brand"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await db.brands.update_one({"id": brand_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {"message": "Brand updated"}


@router.delete("/admin/brands/{brand_id}")
async def delete_brand(brand_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a brand"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.brands.delete_one({"id": brand_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {"message": "Brand deleted"}


# ==================== BRAND ANALYTICS ====================

@router.get("/admin/brand-analytics")
async def get_brand_analytics(current_user: dict = Depends(get_current_user)):
    """Get brand sponsorship analytics"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    brands = await db.brands.find({}, {"_id": 0}).to_list(100)

    # Aggregate impressions per brand
    pipeline = [
        {"$group": {
            "_id": "$brand_id",
            "total_impressions": {"$sum": 1},
            "total_cost": {"$sum": "$cost"},
            "products_featured": {"$push": "$products_featured"},
        }}
    ]
    impressions_agg = await db.brand_impressions.aggregate(pipeline).to_list(100)
    impressions_map = {a["_id"]: a for a in impressions_agg}

    # Total revenue from sponsorships
    total_pipeline = [{"$group": {"_id": None, "total": {"$sum": "$cost"}, "count": {"$sum": 1}}}]
    total_agg = await db.brand_impressions.aggregate(total_pipeline).to_list(1)
    total_revenue = total_agg[0]["total"] if total_agg else 0
    total_impressions = total_agg[0]["count"] if total_agg else 0

    # Classroom sponsorships
    active_sponsorships = await db.classroom_sponsorships.count_documents({"is_active": True})
    total_sponsorship_amount = 0
    sponsorship_pipeline = [{"$match": {"is_active": True}}, {"$group": {"_id": None, "total": {"$sum": "$amount_paid"}}}]
    sp_agg = await db.classroom_sponsorships.aggregate(sponsorship_pipeline).to_list(1)
    total_sponsorship_amount = sp_agg[0]["total"] if sp_agg else 0

    brand_details = []
    for b in brands:
        imp = impressions_map.get(b["id"], {})
        brand_details.append({
            "id": b["id"], "name": b["name"], "is_active": b.get("is_active", True),
            "budget_total": b.get("budget_total", 0),
            "budget_spent": imp.get("total_cost", 0),
            "impressions": imp.get("total_impressions", 0),
            "cost_per_impression": b.get("cost_per_impression", 0.05),
            "budget_remaining": b.get("budget_total", 0) - imp.get("total_cost", 0),
        })

    return {
        "total_brand_revenue": round(total_revenue, 2),
        "total_impressions": total_impressions,
        "active_brands": sum(1 for b in brands if b.get("is_active")),
        "total_brands": len(brands),
        "active_classroom_sponsorships": active_sponsorships,
        "total_sponsorship_amount": round(total_sponsorship_amount, 2),
        "brands": brand_details,
    }


# ==================== CLASSROOM SPONSORSHIP ====================

class ClassroomSponsorshipCreate(BaseModel):
    brand_id: str
    classroom_session_id: Optional[str] = None
    teacher_id: Optional[str] = None
    school_name: str = ""
    stories_limit: int = -1
    amount_paid: float = 0.0


@router.post("/admin/classroom-sponsorships")
async def create_classroom_sponsorship(data: ClassroomSponsorshipCreate, current_user: dict = Depends(get_current_user)):
    """Create a classroom sponsorship"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    brand = await db.brands.find_one({"id": data.brand_id}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    sponsorship = ClassroomSponsorship(
        brand_id=data.brand_id, brand_name=brand["name"],
        classroom_session_id=data.classroom_session_id, teacher_id=data.teacher_id,
        school_name=data.school_name, stories_limit=data.stories_limit,
        amount_paid=data.amount_paid, badge_text=f"Sponsored by {brand['name']}",
    )
    await db.classroom_sponsorships.insert_one(sponsorship.model_dump())
    return sponsorship.model_dump()


@router.get("/admin/classroom-sponsorships")
async def list_classroom_sponsorships(current_user: dict = Depends(get_current_user)):
    """List all classroom sponsorships"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    sponsorships = await db.classroom_sponsorships.find({}, {"_id": 0}).sort("created_date", -1).to_list(100)
    return sponsorships


@router.delete("/admin/classroom-sponsorships/{sp_id}")
async def delete_classroom_sponsorship(sp_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a classroom sponsorship"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.classroom_sponsorships.delete_one({"id": sp_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Sponsorship deleted"}


# ==================== GUARDIAN AD PREFERENCES ====================

class AdPreferencesUpdate(BaseModel):
    allow_brand_stories: bool = False
    preferred_categories: List[str] = []
    blocked_categories: List[str] = []


@router.get("/students/{student_id}/ad-preferences")
async def get_ad_preferences(student_id: str, current_user: dict = Depends(get_current_guardian)):
    """Get a student's ad preferences"""
    query = {"id": student_id}
    if current_user.get("role") != "admin":
        query["guardian_id"] = current_user["id"]
    student = await db.students.find_one(query, {"_id": 0, "ad_preferences": 1})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student.get("ad_preferences", {"allow_brand_stories": False, "preferred_categories": [], "blocked_categories": []})


@router.post("/students/{student_id}/ad-preferences")
async def update_ad_preferences(student_id: str, data: AdPreferencesUpdate, current_user: dict = Depends(get_current_guardian)):
    """Update a student's ad preferences"""
    query = {"id": student_id}
    if current_user.get("role") != "admin":
        query["guardian_id"] = current_user["id"]
    result = await db.students.update_one(query, {"$set": {"ad_preferences": data.model_dump()}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Ad preferences updated", **data.model_dump()}


# ==================== BRAND STORY INTEGRATION ====================

@router.get("/brands/active-for-student/{student_id}")
async def get_active_brands_for_student(student_id: str, current_user: dict = Depends(get_current_user)):
    """Get brands eligible for a student's stories with bidding/rotation support"""
    import random

    # Check feature flag
    flags = await db.system_config.find_one({"key": "feature_flags"}, {"_id": 0})
    brand_enabled = True
    if flags and flags.get("value"):
        brand_enabled = flags["value"].get("brand_sponsorship_enabled", True)
    if not brand_enabled:
        return {"brands": [], "reason": "Brand sponsorship is disabled system-wide"}

    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        return {"brands": [], "reason": "Student not found"}

    ad_prefs = student.get("ad_preferences", {})
    if not ad_prefs.get("allow_brand_stories", False):
        return {"brands": [], "reason": "Guardian has not opted in to brand stories"}

    blocked = ad_prefs.get("blocked_categories", [])
    student_age = student.get("age", 10)

    brands = await db.brands.find({"is_active": True}, {"_id": 0}).to_list(100)

    # Filter eligible brands
    eligible = []
    for b in brands:
        if b.get("target_ages") and student_age not in b["target_ages"]:
            continue
        if b.get("budget_total", 0) > 0 and b.get("budget_spent", 0) >= b.get("budget_total", 0):
            continue
        brand_cats = b.get("target_categories", [])
        if any(c in blocked for c in brand_cats):
            continue
        eligible.append(b)

    # Group by problem_category for rotation
    by_category = {}
    uncategorized = []
    for b in eligible:
        cat = b.get("problem_category", "").strip()
        if cat:
            by_category.setdefault(cat, []).append(b)
        else:
            uncategorized.append(b)

    # Weighted rotation selection per category (bid_amount determines weight)
    selected = []
    for cat, cat_brands in by_category.items():
        if len(cat_brands) == 1:
            selected.append(cat_brands[0])
        else:
            # Weighted selection: higher bid = higher probability
            weights = [b.get("bid_amount", 0.05) for b in cat_brands]
            total_w = sum(weights) or 1
            probs = [w / total_w for w in weights]
            # Select up to 2 brands per category (allows competing brands in same story)
            n_select = min(2, len(cat_brands))
            try:
                picks = random.choices(cat_brands, weights=probs, k=n_select)
                # Deduplicate
                seen_ids = set()
                for p in picks:
                    if p["id"] not in seen_ids:
                        selected.append(p)
                        seen_ids.add(p["id"])
            except:
                selected.append(cat_brands[0])

    # Add uncategorized brands
    selected.extend(uncategorized)

    # Limit total brands per story to configurable max (default 4)
    max_brands = 4
    if len(selected) > max_brands:
        # Prioritize by bid amount
        selected.sort(key=lambda b: b.get("bid_amount", 0.05), reverse=True)
        selected = selected[:max_brands]

    # Update rotation counts
    for b in selected:
        await db.brands.update_one({"id": b["id"]}, {"$inc": {"rotation_count": 1}})

    result = [{
        "id": b["id"], "name": b["name"],
        "products": b.get("products", []),
        "categories": b.get("target_categories", []),
        "problem_statement": b.get("problem_statement", ""),
        "problem_category": b.get("problem_category", ""),
        "bid_amount": b.get("bid_amount", 0.05),
    } for b in selected]

    return {"brands": result, "total_eligible": len(eligible), "categories_matched": len(by_category)}



@router.get("/brands/opt-out-analytics")
async def get_brand_opt_out_analytics(current_user: dict = Depends(get_current_user)):
    """Get anonymized analytics on brand content opt-out rates"""
    total_students = await db.students.count_documents({})
    opted_in = await db.students.count_documents({"ad_preferences.allow_brand_stories": True})
    opted_out = total_students - opted_in

    # Offer preference stats
    total_guardians = await db.users.count_documents({"role": {"$in": ["guardian", "admin"]}})
    offers_disabled = await db.user_offer_preferences.count_documents({"offers_enabled": False})

    return {
        "total_students": total_students,
        "brand_stories_opted_in": opted_in,
        "brand_stories_opted_out": opted_out,
        "opt_in_rate": round(opted_in / max(total_students, 1) * 100, 1),
        "total_guardians": total_guardians,
        "offers_disabled_count": offers_disabled,
        "offers_enabled_rate": round((total_guardians - offers_disabled) / max(total_guardians, 1) * 100, 1),
    }

@router.get("/brands/competition/{problem_category}")
async def get_brand_competition(problem_category: str, current_user: dict = Depends(get_current_user)):
    """Get all brands competing in a problem category with bid info"""
    brands = await db.brands.find(
        {"problem_category": problem_category, "is_active": True}, {"_id": 0}
    ).to_list(50)
    brands.sort(key=lambda b: b.get("bid_amount", 0), reverse=True)
    return {
        "category": problem_category,
        "total_competitors": len(brands),
        "brands": [{
            "id": b["id"], "name": b["name"], "bid_amount": b.get("bid_amount", 0.05),
            "total_impressions": b.get("total_impressions", 0),
            "rotation_count": b.get("rotation_count", 0),
            "budget_remaining": max(b.get("budget_total", 0) - b.get("budget_spent", 0), 0),
        } for b in brands],
    }

# ==================== BRAND PARTNER PORTAL ====================

@router.get("/brand-portal/profile")
async def get_brand_partner_profile(current_user: dict = Depends(get_current_brand_partner)):
    """Get brand partner profile with linked brand info. Auto-creates brand if none linked."""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    brand = None
    if user.get("linked_brand_id"):
        brand = await db.brands.find_one({"id": user["linked_brand_id"]}, {"_id": 0})

    # Auto-create a brand if none linked yet
    if not brand:
        new_brand = Brand(
            name=user.get("full_name", "My Brand"),
            created_by=user["id"],
        )
        await db.brands.insert_one(new_brand.model_dump())
        await db.users.update_one({"id": user["id"]}, {"$set": {"linked_brand_id": new_brand.id}})
        brand = new_brand.model_dump()

    return {
        "user": {
            "id": user["id"], "email": user["email"], "full_name": user["full_name"],
            "wallet_balance": user.get("wallet_balance", 0.0),
            "brand_approved": user.get("brand_approved", False),
        },
        "brand": brand,
    }



# ==================== BRAND PORTAL: PROFILE UPDATE ====================

class BrandProfileUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    problem_statement: Optional[str] = None
    target_categories: Optional[list] = None
    target_ages: Optional[list] = None
    target_regions: Optional[list] = None
    target_languages: Optional[list] = None
    onboarding_completed: Optional[bool] = None


@router.put("/brand-portal/profile")
async def update_brand_profile(data: BrandProfileUpdate, current_user: dict = Depends(get_current_brand_partner)):
    """Update brand profile (problem statement, targeting, etc.)"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked to your account")

    update_data = {}
    for k, v in data.model_dump().items():
        if v is not None:
            if k == "target_regions":
                update_data[k] = [TargetRegion(**r).model_dump() if isinstance(r, dict) else r for r in v]
            else:
                update_data[k] = v

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.brands.update_one({"id": brand_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Brand not found")

    updated_brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    return updated_brand


# ==================== BRAND PORTAL: LOGO UPLOAD ====================

from fastapi import UploadFile, File, Form

# Ensure uploads directory exists
UPLOAD_DIR = Path(__file__).parent / "uploads" / "logos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_LOGO_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/brand-portal/logo-upload")
async def upload_brand_logo(file: UploadFile = File(...), current_user: dict = Depends(get_current_brand_partner)):
    """Upload brand logo (max 10MB, images only)"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked to your account")

    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/svg+xml"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: PNG, JPG, WebP, SVG")

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_LOGO_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")

    # Save file
    import uuid as _uuid
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"{brand_id}_{_uuid.uuid4().hex[:8]}.{ext}"
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        f.write(contents)

    logo_url = f"/api/uploads/logos/{filename}"
    await db.brands.update_one({"id": brand_id}, {"$set": {"logo_url": logo_url}})

    return {"logo_url": logo_url, "filename": filename}


# ==================== BRAND PORTAL: PRODUCT CRUD ====================

class ProductCreate(BaseModel):
    name: str
    description: str = ""
    category: str = ""


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


@router.get("/brand-portal/products")
async def list_brand_products(current_user: dict = Depends(get_current_brand_partner)):
    """List all products for the brand"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        return []
    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    return brand.get("products", []) if brand else []


@router.post("/brand-portal/products")
async def add_brand_product(data: ProductCreate, current_user: dict = Depends(get_current_brand_partner)):
    """Add a product to the brand"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")

    product = BrandProduct(name=data.name, description=data.description, category=data.category)
    await db.brands.update_one({"id": brand_id}, {"$push": {"products": product.model_dump()}})

    return product.model_dump()


@router.put("/brand-portal/products/{product_id}")
async def update_brand_product(product_id: str, data: ProductUpdate, current_user: dict = Depends(get_current_brand_partner)):
    """Update a specific product"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")

    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    products = brand.get("products", [])
    updated = False
    for p in products:
        if p.get("id") == product_id:
            if data.name is not None:
                p["name"] = data.name
            if data.description is not None:
                p["description"] = data.description
            if data.category is not None:
                p["category"] = data.category
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.brands.update_one({"id": brand_id}, {"$set": {"products": products}})
    return {"message": "Product updated"}


@router.delete("/brand-portal/products/{product_id}")
async def delete_brand_product(product_id: str, current_user: dict = Depends(get_current_brand_partner)):
    """Delete a product from the brand"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")

    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    products = [p for p in brand.get("products", []) if p.get("id") != product_id]
    await db.brands.update_one({"id": brand_id}, {"$set": {"products": products}})
    return {"message": "Product deleted"}


# ==================== BRAND PORTAL: STORY PREVIEW ====================

@router.get("/brand-portal/story-preview")
async def get_story_preview(current_user: dict = Depends(get_current_brand_partner)):
    """Get cached story preview for the brand"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")
    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {
        "preview": brand.get("story_preview", ""),
        "generated_at": brand.get("story_preview_generated_at"),
    }


@router.post("/brand-portal/story-preview")
async def generate_story_preview(current_user: dict = Depends(get_current_brand_partner)):
    """Generate a short AI story snippet showcasing how the brand is woven into a story"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")
    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_name = brand.get("name", "Brand")
    problem = brand.get("problem_statement", "")
    products = brand.get("products", [])
    prod_names = [p.get("name", "") for p in products if p.get("name")]

    if not problem and not prod_names:
        raise HTTPException(status_code=400, detail="Please add a problem statement or products first")

    # Build the prompt
    prod_text = f"Products: {', '.join(prod_names)}" if prod_names else ""
    problem_text = f"Problem they solve: {problem}" if problem else ""

    prompt = f"""Write a short educational story snippet (about 150-200 words, one scene) for children aged 8-12.
The story should naturally feature the brand "{brand_name}" as a helpful solution.
{problem_text}
{prod_text}

Requirements:
- The brand mention must feel organic, not like an advertisement
- Show how the brand/product helps a child character solve a real problem
- Keep it engaging, warm, and educational
- Write it as a single cohesive paragraph/scene
- Do NOT include any JSON formatting, just the story text"""

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import time as _time
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")

        story_service.set_db(db)
        llm_config = await story_service._get_llm_config()
        provider = llm_config.get("provider", "emergent")
        model = llm_config.get("model", "gpt-5.2")

        if provider == "openrouter":
            openrouter_key = llm_config.get("openrouter_key") or os.environ.get("OPENROUTER_API_KEY")
            if not openrouter_key:
                raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
            # OpenRouter path - use direct API
            import httpx
            headers = {"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"}
            body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
            async with httpx.AsyncClient(timeout=60) as client_http:
                resp = await client_http.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=headers)
                resp.raise_for_status()
                preview_text = resp.json()["choices"][0]["message"]["content"].strip()
        else:
            chat = LlmChat(
                api_key=api_key,
                session_id=f"brand_preview_{brand_id}_{int(_time.time())}",
                system_message="You are an expert educational story writer for children."
            )
            chat.with_model("openai", model)
            message = UserMessage(text=prompt)
            preview_text = await chat.send_message(message)
            preview_text = preview_text.strip()

        # Cache it
        now_iso = datetime.now(timezone.utc).isoformat()
        await db.brands.update_one(
            {"id": brand_id},
            {"$set": {"story_preview": preview_text, "story_preview_generated_at": now_iso}}
        )

        return {"preview": preview_text, "generated_at": now_iso}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Story preview generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate story preview. Please try again.")




@router.get("/brand-portal/dashboard")
async def get_brand_dashboard(current_user: dict = Depends(get_current_brand_partner)):
    """Get brand partner dashboard data"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")

    # Auto-create brand if none linked
    if not brand_id:
        new_brand = Brand(name=user.get("full_name", "My Brand"), created_by=user["id"])
        await db.brands.insert_one(new_brand.model_dump())
        await db.users.update_one({"id": user["id"]}, {"$set": {"linked_brand_id": new_brand.id}})
        brand_id = new_brand.id

    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})

    # Get campaigns
    campaigns = await db.brand_campaigns.find({"brand_id": brand_id}, {"_id": 0}).sort("created_date", -1).to_list(50)

    # Get impression stats
    pipeline = [
        {"$match": {"brand_id": brand_id}},
        {"$group": {"_id": None, "total": {"$sum": 1}, "cost": {"$sum": "$cost"}}}
    ]
    imp_agg = await db.brand_impressions.aggregate(pipeline).to_list(1)
    total_impressions = imp_agg[0]["total"] if imp_agg else 0
    total_spent = imp_agg[0]["cost"] if imp_agg else 0

    # Recent impressions
    recent_impressions = await db.brand_impressions.find(
        {"brand_id": brand_id}, {"_id": 0}
    ).sort("created_date", -1).to_list(20)

    # Sponsorships
    sponsorships = await db.classroom_sponsorships.find(
        {"brand_id": brand_id}, {"_id": 0}
    ).to_list(20)

    return {
        "brand": brand,
        "campaigns": campaigns,
        "sponsorships": sponsorships,
        "stats": {
            "total_impressions": total_impressions,
            "total_spent": round(total_spent, 2),
            "budget_total": brand.get("budget_total", 0) if brand else 0,
            "budget_remaining": round((brand.get("budget_total", 0) - total_spent), 2) if brand else 0,
            "active_campaigns": sum(1 for c in campaigns if c.get("status") == "active"),
            "active_sponsorships": sum(1 for s in sponsorships if s.get("is_active")),
        },
        "recent_impressions": recent_impressions,
    }



# ==================== BRAND PORTAL: ANALYTICS DASHBOARD ====================

@router.get("/brand-portal/analytics")
async def get_brand_analytics_dashboard(current_user: dict = Depends(get_current_brand_partner)):
    """Get comprehensive analytics for the brand partner dashboard"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        return {"daily_impressions": [], "campaign_breakdown": [], "product_breakdown": [],
                "region_breakdown": [], "metrics": {}}

    brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    if not brand:
        return {"daily_impressions": [], "campaign_breakdown": [], "product_breakdown": [],
                "region_breakdown": [], "metrics": {}}

    # 1. Daily impressions over last 30 days
    from datetime import timedelta
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    daily_pipeline = [
        {"$match": {"brand_id": brand_id, "created_date": {"$gte": thirty_days_ago.isoformat()}}},
        {"$addFields": {
            "date_parsed": {"$dateFromString": {"dateString": "$created_date", "onError": "$created_date"}}
        }},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date_parsed"}},
            "impressions": {"$sum": 1},
            "cost": {"$sum": "$cost"},
        }},
        {"$sort": {"_id": 1}},
    ]
    try:
        daily_data = await db.brand_impressions.aggregate(daily_pipeline).to_list(31)
    except Exception:
        daily_data = []

    daily_impressions = [{"date": d["_id"], "impressions": d["impressions"], "cost": round(d["cost"], 3)} for d in daily_data]

    # 2. Campaign breakdown
    campaigns = await db.brand_campaigns.find({"brand_id": brand_id}, {"_id": 0}).to_list(50)
    campaign_breakdown = []
    for c in campaigns:
        camp_pipeline = [
            {"$match": {"brand_id": brand_id, "campaign_id": c["id"]}},
            {"$group": {"_id": None, "impressions": {"$sum": 1}, "cost": {"$sum": "$cost"}}},
        ]
        camp_agg = await db.brand_impressions.aggregate(camp_pipeline).to_list(1)
        imp_count = camp_agg[0]["impressions"] if camp_agg else 0
        imp_cost = camp_agg[0]["cost"] if camp_agg else 0
        campaign_breakdown.append({
            "id": c["id"],
            "name": c["name"],
            "status": c.get("status", "active"),
            "budget": c.get("budget", 0),
            "budget_spent": round(c.get("budget_spent", 0), 2),
            "impressions": imp_count,
            "cost": round(imp_cost, 2),
            "cpi": round(imp_cost / imp_count, 3) if imp_count > 0 else 0,
        })

    # 3. Product breakdown
    product_pipeline = [
        {"$match": {"brand_id": brand_id}},
        {"$unwind": "$products_featured"},
        {"$group": {
            "_id": "$products_featured",
            "impressions": {"$sum": 1},
            "cost": {"$sum": "$cost"},
        }},
        {"$sort": {"impressions": -1}},
    ]
    try:
        product_data = await db.brand_impressions.aggregate(product_pipeline).to_list(50)
    except Exception:
        product_data = []
    product_breakdown = [{"product": p["_id"], "impressions": p["impressions"], "cost": round(p["cost"], 3)} for p in product_data if p["_id"]]

    # 4. Overall metrics
    total_pipeline = [
        {"$match": {"brand_id": brand_id}},
        {"$group": {"_id": None, "total": {"$sum": 1}, "cost": {"$sum": "$cost"}}},
    ]
    total_agg = await db.brand_impressions.aggregate(total_pipeline).to_list(1)
    total_impressions = total_agg[0]["total"] if total_agg else 0
    total_cost = total_agg[0]["cost"] if total_agg else 0

    budget_total = brand.get("budget_total", 0)
    budget_utilization = round((total_cost / budget_total * 100), 1) if budget_total > 0 else 0
    avg_cpi = round(total_cost / total_impressions, 3) if total_impressions > 0 else 0

    # Impressions last 7 days vs previous 7 days for velocity
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    fourteen_days_ago = datetime.now(timezone.utc) - timedelta(days=14)
    recent_pipeline = [
        {"$match": {"brand_id": brand_id, "created_date": {"$gte": seven_days_ago.isoformat()}}},
        {"$group": {"_id": None, "count": {"$sum": 1}}},
    ]
    prev_pipeline = [
        {"$match": {"brand_id": brand_id, "created_date": {"$gte": fourteen_days_ago.isoformat(), "$lt": seven_days_ago.isoformat()}}},
        {"$group": {"_id": None, "count": {"$sum": 1}}},
    ]
    try:
        recent_agg = await db.brand_impressions.aggregate(recent_pipeline).to_list(1)
        prev_agg = await db.brand_impressions.aggregate(prev_pipeline).to_list(1)
    except Exception:
        recent_agg = []
        prev_agg = []
    recent_count = recent_agg[0]["count"] if recent_agg else 0
    prev_count = prev_agg[0]["count"] if prev_agg else 0
    velocity_change = round(((recent_count - prev_count) / prev_count * 100), 1) if prev_count > 0 else (100.0 if recent_count > 0 else 0)

    metrics = {
        "total_impressions": total_impressions,
        "total_cost": round(total_cost, 2),
        "budget_total": budget_total,
        "budget_remaining": round(budget_total - total_cost, 2),
        "budget_utilization": budget_utilization,
        "avg_cpi": avg_cpi,
        "impressions_last_7d": recent_count,
        "impressions_prev_7d": prev_count,
        "velocity_change": velocity_change,
        "total_campaigns": len(campaigns),
        "active_campaigns": sum(1 for c in campaigns if c.get("status") == "active"),
        "total_products_featured": len(product_breakdown),
        "total_stories": brand.get("total_stories", 0),
    }

    return {
        "daily_impressions": daily_impressions,
        "campaign_breakdown": campaign_breakdown,
        "product_breakdown": product_breakdown,
        "metrics": metrics,
    }



# ==================== BRAND STORY INTEGRATIONS ====================

@router.get("/brand-portal/story-integrations")
async def get_brand_story_integrations(brand_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Get actual story excerpts where brand appeared + student responses"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    
    # Admin can query any brand, brand_partner sees their own
    if user.get("role") == "admin":
        if not brand_id:
            # Get the first active brand for admin viewing
            brand = await db.brands.find_one({"is_active": True}, {"_id": 0})
        else:
            brand = await db.brands.find_one({"id": brand_id}, {"_id": 0})
    elif user.get("role") == "brand_partner":
        linked_brand_id = user.get("linked_brand_id")
        if not linked_brand_id:
            return {"story_snippets": [], "student_responses": [], "summary": {}}
        brand = await db.brands.find_one({"id": linked_brand_id}, {"_id": 0})
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not brand:
        return {"story_snippets": [], "student_responses": [], "summary": {}}

    brand_name = brand.get("name", "")
    product_names = [p.get("name", "") for p in brand.get("products", []) if p.get("name")]

    # 1. Find all narratives that have this brand in brand_placements
    narratives_with_brand = await db.narratives.find(
        {"brand_placements.id": brand_id},
        {"_id": 0, "id": 1, "title": 1, "student_id": 1, "chapters": 1, "brand_placements": 1, "created_date": 1}
    ).to_list(50)

    # Also find narratives via brand_impressions (for older narratives)
    impression_narrative_ids = []
    impressions = await db.brand_impressions.find(
        {"brand_id": brand_id},
        {"_id": 0, "narrative_id": 1, "student_id": 1, "created_date": 1}
    ).to_list(200)
    for imp in impressions:
        if imp.get("narrative_id") and imp["narrative_id"] != "pending":
            impression_narrative_ids.append(imp["narrative_id"])

    # Get narratives from impressions that aren't already found
    found_ids = {n["id"] for n in narratives_with_brand}
    missing_ids = [nid for nid in set(impression_narrative_ids) if nid not in found_ids]
    if missing_ids:
        extra_narratives = await db.narratives.find(
            {"id": {"$in": missing_ids}},
            {"_id": 0, "id": 1, "title": 1, "student_id": 1, "chapters": 1, "created_date": 1}
        ).to_list(50)
        narratives_with_brand.extend(extra_narratives)

    # Also search ALL narratives by content (catches older narratives without brand_placements field)
    found_ids = {n["id"] for n in narratives_with_brand}
    search_terms_lower = [brand_name.lower()] + [p.lower() for p in product_names if p]
    
    all_narratives = await db.narratives.find(
        {"id": {"$nin": list(found_ids)}},
        {"_id": 0, "id": 1, "title": 1, "student_id": 1, "chapters": 1, "created_date": 1}
    ).to_list(100)
    
    for narr in all_narratives:
        for ch in narr.get("chapters", []):
            content_lower = ch.get("content", "").lower()
            if any(t in content_lower for t in search_terms_lower if t):
                narratives_with_brand.append(narr)
                break

    # 2. Extract story snippets where brand/products are mentioned
    story_snippets = []
    all_student_ids = set()
    search_terms = [brand_name.lower()] + [p.lower() for p in product_names if p]

    for narrative in narratives_with_brand:
        all_student_ids.add(narrative["student_id"])
        for chapter in narrative.get("chapters", []):
            content = chapter.get("content", "")
            content_lower = content.lower()

            # Check if any brand/product name appears in chapter
            found_terms = [t for t in search_terms if t and t in content_lower]
            if not found_terms:
                continue

            # Extract the relevant sentences containing the brand mention
            sentences = content.replace(".", ".|").replace("!", "!|").replace("?", "?|").split("|")
            relevant_sentences = []
            for sentence in sentences:
                sentence_lower = sentence.lower().strip()
                if any(term in sentence_lower for term in found_terms):
                    relevant_sentences.append(sentence.strip())

            if relevant_sentences:
                story_snippets.append({
                    "narrative_id": narrative["id"],
                    "narrative_title": narrative.get("title", "Untitled"),
                    "chapter_number": chapter.get("number", 0),
                    "chapter_title": chapter.get("title", ""),
                    "student_id": narrative["student_id"],
                    "excerpts": relevant_sentences[:5],  # Max 5 excerpts per chapter
                    "brand_terms_found": found_terms,
                    "created_date": narrative.get("created_date", ""),
                })

    # 3. Get student names for display
    student_names = {}
    if all_student_ids:
        students = await db.students.find(
            {"id": {"$in": list(all_student_ids)}},
            {"_id": 0, "id": 1, "full_name": 1}
        ).to_list(100)
        student_names = {s["id"]: s["full_name"] for s in students}

    # Add student names to snippets
    for snippet in story_snippets:
        snippet["student_name"] = student_names.get(snippet["student_id"], "Student")

    # 4. Get vision check questions that specifically relate to the brand/product
    #    Only include if the question or expected answer references the brand,
    #    or the question asks about a tool/product and the answer is the brand product
    activation_questions = []
    # Build broader search: brand name, products, and contextual terms from product descriptions
    brand_answer_terms = set(search_terms)
    for p in brand.get("products", []):
        name = p.get("name", "").lower().strip()
        if name:
            # Add individual words from product name (e.g., "Smart Learning Tablet" -> "tablet")
            for word in name.split():
                if len(word) > 3:
                    brand_answer_terms.add(word)

    for narrative in narratives_with_brand:
        for chapter in narrative.get("chapters", []):
            vision_check = chapter.get("vision_check", {})
            question = vision_check.get("question", "")
            expected_answer = vision_check.get("answer", "")
            if not question:
                continue

            ch_num = chapter.get("number", 0)
            content = chapter.get("content", "")
            content_lower = content.lower()
            question_lower = question.lower()
            answer_lower = expected_answer.lower() if expected_answer else ""

            # Strategy: A question is brand-related if:
            # 1. Brand/product name appears directly in the question or expected answer
            brand_in_q = any(t in question_lower for t in search_terms if t)
            brand_in_a = any(t in answer_lower for t in search_terms if t)

            # 2. Question asks about a tool/device/product AND the chapter has brand content
            import re
            product_keywords = ["tool", "device", "tablet", "product", "technology", "gadget"]
            asks_about_product = any(re.search(r'\b' + kw + r'\b', question_lower) for kw in product_keywords)
            has_brand_content = any(t in content_lower for t in search_terms if t)

            # 3. Expected answer (if present) contains brand-adjacent terms
            answer_has_brand_term = any(t in answer_lower for t in brand_answer_terms if t)

            # 4. If no expected_answer, check if nearby content around brand mention answers the question
            contextual_match = False
            if not expected_answer and has_brand_content:
                # Find sentences with brand mention — if question word appears near brand mention
                sentences = content.replace(".", ".|").replace("!", "!|").replace("?", "?|").split("|")
                for sentence in sentences:
                    s_lower = sentence.lower().strip()
                    if any(t in s_lower for t in search_terms if t):
                        # Check if this sentence could answer the question
                        q_keywords = [w for w in question_lower.split() if len(w) > 3 and w not in {"what", "does", "that", "this", "have", "with", "from", "were", "when", "they", "their", "about"}]
                        if any(kw in s_lower for kw in q_keywords):
                            contextual_match = True
                            break

            is_brand_related = brand_in_q or brand_in_a or (asks_about_product and has_brand_content) or answer_has_brand_term

            if is_brand_related:
                activation_questions.append({
                    "narrative_id": narrative["id"],
                    "narrative_title": narrative.get("title", "Untitled"),
                    "chapter_number": ch_num,
                    "chapter_title": chapter.get("title", ""),
                    "student_id": narrative["student_id"],
                    "student_name": student_names.get(narrative["student_id"], "Student"),
                    "question": question,
                    "expected_answer": expected_answer,
                    "brand_in_question": brand_in_q,
                })
    
    # Get read_log pass/fail data for these activation questions
    if activation_questions:
        narrative_ids_for_logs = list(set(q["narrative_id"] for q in activation_questions))
        read_logs = await db.read_logs.find(
            {"narrative_id": {"$in": narrative_ids_for_logs}},
            {"_id": 0, "narrative_id": 1, "chapter_number": 1, "vision_check_passed": 1, "student_id": 1, "created_date": 1}
        ).to_list(500)
        
        for aq in activation_questions:
            matching_logs = [
                rl for rl in read_logs 
                if rl.get("narrative_id") == aq["narrative_id"] 
                and rl.get("chapter_number") == aq["chapter_number"]
            ]
            aq["total_attempts"] = len(matching_logs)
            aq["passed_count"] = sum(1 for rl in matching_logs if rl.get("vision_check_passed") == True)
            aq["failed_count"] = sum(1 for rl in matching_logs if rl.get("vision_check_passed") == False)
    
    # 5. Get written answers from students who read these narratives (free-text responses)
    student_responses = []
    if all_student_ids:
        answers = await db.written_answers.find(
            {"student_id": {"$in": list(all_student_ids)}},
            {"_id": 0}
        ).sort("created_date", -1).to_list(100)

        for ans in answers:
            student_responses.append({
                "student_name": student_names.get(ans["student_id"], "Student"),
                "question": ans.get("question", ""),
                "student_answer": ans.get("student_answer", ""),
                "passed": ans.get("passed", False),
                "comprehension_score": ans.get("comprehension_score", 0),
                "chapter_number": ans.get("chapter_number", 0),
                "created_date": ans.get("created_date", ""),
            })

    # 6. Summary stats
    total_attempts = sum(q["total_attempts"] for q in activation_questions) if activation_questions else 0
    total_passes = sum(q["passed_count"] for q in activation_questions) if activation_questions else 0
    summary = {
        "total_stories_with_brand": len(narratives_with_brand),
        "total_snippets": len(story_snippets),
        "total_activation_questions": len(activation_questions),
        "total_question_attempts": total_attempts,
        "total_question_passes": total_passes,
        "pass_rate": round(total_passes / total_attempts * 100, 1) if total_attempts > 0 else 0,
        "total_student_responses": len(student_responses),
        "unique_students_reached": len(all_student_ids),
        "avg_comprehension_score": round(
            sum(r["comprehension_score"] for r in student_responses) / len(student_responses), 1
        ) if student_responses else 0,
    }

    return {
        "story_snippets": story_snippets[:30],
        "activation_questions": activation_questions[:50],
        "student_responses": student_responses[:50],
        "summary": summary,
    }



@router.get("/brand-portal/story/{narrative_id}")
async def get_brand_story_detail(narrative_id: str, current_user: dict = Depends(get_current_user)):
    """Get full story for brand to read with brand mentions highlighted"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    if user.get("role") not in ("brand_partner", "admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    narrative = await db.narratives.find_one({"id": narrative_id}, {"_id": 0})
    if not narrative:
        raise HTTPException(status_code=404, detail="Story not found")

    student = await db.students.find_one({"id": narrative["student_id"]}, {"_id": 0, "id": 1, "full_name": 1})

    chapters = []
    for ch in narrative.get("chapters", []):
        chapters.append({
            "number": ch.get("number", 0),
            "title": ch.get("title", ""),
            "content": ch.get("content", ""),
            "word_count": ch.get("word_count", 0),
            "vision_check": ch.get("vision_check", {}),
            "embedded_tokens": ch.get("embedded_tokens", []),
        })

    return {
        "id": narrative["id"],
        "title": narrative.get("title", ""),
        "theme": narrative.get("theme", ""),
        "student_name": student["full_name"] if student else "Student",
        "total_word_count": narrative.get("total_word_count", 0),
        "status": narrative.get("status", ""),
        "chapters": chapters,
        "created_date": narrative.get("created_date", ""),
    }



# ==================== BRAND PARTNER CAMPAIGN MANAGEMENT ====================

class CampaignCreate(BaseModel):
    name: str
    description: str = ""
    products: list = []
    target_ages: list = []
    target_categories: list = []
    budget: float = 0.0
    cost_per_impression: float = 0.05


@router.post("/brand-portal/campaigns")
async def create_campaign(data: CampaignCreate, current_user: dict = Depends(get_current_brand_partner)):
    """Create a brand campaign"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    if not user.get("brand_approved"):
        raise HTTPException(status_code=403, detail="Your brand account is pending approval")
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked to your account")

    campaign = BrandCampaign(
        brand_id=brand_id, name=data.name, description=data.description,
        products=[BrandProduct(**p) if isinstance(p, dict) else p for p in data.products],
        target_ages=data.target_ages, target_categories=data.target_categories,
        budget=data.budget, cost_per_impression=data.cost_per_impression,
        status="active", created_by=current_user["id"],
    )
    await db.brand_campaigns.insert_one(campaign.model_dump())
    return campaign.model_dump()


@router.get("/brand-portal/campaigns")
async def list_my_campaigns(current_user: dict = Depends(get_current_brand_partner)):
    """List brand partner's campaigns"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        return []
    campaigns = await db.brand_campaigns.find({"brand_id": brand_id}, {"_id": 0}).sort("created_date", -1).to_list(50)
    return campaigns


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    products: Optional[list] = None
    target_ages: Optional[list] = None
    target_categories: Optional[list] = None
    budget: Optional[float] = None
    cost_per_impression: Optional[float] = None
    status: Optional[str] = None


@router.put("/brand-portal/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, data: CampaignUpdate, current_user: dict = Depends(get_current_brand_partner)):
    """Update a campaign"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await db.brand_campaigns.update_one(
        {"id": campaign_id, "brand_id": brand_id}, {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign updated"}


@router.delete("/brand-portal/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str, current_user: dict = Depends(get_current_brand_partner)):
    """Delete a campaign"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    result = await db.brand_campaigns.delete_one({"id": campaign_id, "brand_id": brand_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign deleted"}


# ==================== BRAND PARTNER BUDGET TOP-UP ====================

class BrandTopupRequest(BaseModel):
    amount: float
    origin_url: str


@router.post("/brand-portal/topup")
async def brand_topup(data: BrandTopupRequest, request: Request, current_user: dict = Depends(get_current_brand_partner)):
    """Top up brand campaign budget via Stripe"""
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    brand_id = user.get("linked_brand_id")
    if not brand_id:
        raise HTTPException(status_code=400, detail="No brand linked")
    if data.amount < 5:
        raise HTTPException(status_code=400, detail="Minimum top-up is $5")

    stripe_key = os.environ.get("STRIPE_API_KEY")
    if not stripe_key:
        raise HTTPException(status_code=500, detail="Payment not configured")

    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    origin = data.origin_url.rstrip("/")
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_key, webhook_url=webhook_url)

    metadata = {"user_id": current_user["id"], "brand_id": brand_id, "type": "brand_topup"}

    checkout_req = CheckoutSessionRequest(
        amount=data.amount, currency="usd",
        success_url=f"{origin}/brand-portal?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{origin}/brand-portal?payment=cancelled",
        metadata=metadata, payment_methods=["card"],
    )
    session = await stripe_checkout.create_checkout_session(checkout_req)

    txn = PaymentTransaction(
        user_id=current_user["id"], session_id=session.session_id,
        amount=data.amount, currency="usd", metadata=metadata,
    )
    await db.payment_transactions.insert_one(txn.model_dump())

    return {"url": session.url, "session_id": session.session_id}


@router.get("/brand-portal/topup-status/{session_id}")
async def brand_topup_status(session_id: str, request: Request, current_user: dict = Depends(get_current_brand_partner)):
    """Check brand top-up payment status and credit brand budget"""
    txn = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Payment not found")
    if txn.get("payment_status") == "paid":
        return {"status": "paid", "amount": txn["amount"]}

    stripe_key = os.environ.get("STRIPE_API_KEY")
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    host_url = str(request.base_url).rstrip("/")
    stripe_checkout = StripeCheckout(api_key=stripe_key, webhook_url=f"{host_url}/api/webhook/stripe")
    checkout_status = await stripe_checkout.get_checkout_status(session_id)

    if checkout_status.payment_status == "paid" and txn.get("payment_status") != "paid":
        already = await db.payment_transactions.find_one({"session_id": session_id, "payment_status": "paid"})
        if not already:
            amount = txn["amount"]
            brand_id = txn.get("metadata", {}).get("brand_id")
            now_iso = datetime.now(timezone.utc).isoformat()

            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": "paid", "status": "completed", "updated_date": now_iso}}
            )
            if brand_id:
                await db.brands.update_one({"id": brand_id}, {"$inc": {"budget_total": amount}})

        return {"status": "paid", "amount": txn["amount"]}

    return {"status": txn.get("status", "initiated"), "amount": txn["amount"]}


# ==================== ADMIN: APPROVE/REJECT BRAND PARTNERS ====================

@router.post("/admin/approve-brand-partner/{user_id}")
async def approve_brand_partner(user_id: str, current_user: dict = Depends(get_current_user)):
    """Approve a brand partner application"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    target = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not target or target.get("role") != "brand_partner":
        raise HTTPException(status_code=404, detail="Brand partner not found")

    await db.users.update_one({"id": user_id}, {"$set": {"brand_approved": True}})
    return {"message": f"Brand partner {target['email']} approved"}


@router.post("/admin/reject-brand-partner/{user_id}")
async def reject_brand_partner(user_id: str, current_user: dict = Depends(get_current_user)):
    """Reject/suspend a brand partner"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    await db.users.update_one({"id": user_id}, {"$set": {"brand_approved": False}})
    return {"message": "Brand partner suspended"}


@router.post("/admin/link-brand/{user_id}/{brand_id}")
async def link_brand_to_partner(user_id: str, brand_id: str, current_user: dict = Depends(get_current_user)):
    """Link a brand to a partner account"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    brand = await db.brands.find_one({"id": brand_id})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    await db.users.update_one({"id": user_id}, {"$set": {"linked_brand_id": brand_id}})
    return {"message": f"Brand '{brand['name']}' linked to user"}


