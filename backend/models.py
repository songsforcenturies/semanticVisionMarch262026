"""
LexiMaster Data Models
MongoDB document models using Pydantic with UUID-based IDs
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


def generate_uuid():
    return str(uuid.uuid4())


def generate_pin():
    """Generate a unique 9-digit PIN"""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(9)])


def generate_student_code():
    """Generate a unique student code like STU-ABC123"""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=6))
    return f"STU-{code}"


def generate_referral_code():
    """Generate a unique referral code like REF-ABCD12"""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=6))
    return f"REF-{code}"


# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    GUARDIAN = "guardian"
    TEACHER = "teacher"
    BRAND_PARTNER = "brand_partner"


class GradeLevel(str, Enum):
    PRE_K = "pre-k"
    K = "k"
    GRADE_1_12 = "1-12"
    COLLEGE = "college"
    ADULT = "adult"


class SubscriptionPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    FAMILY = "family"
    ACADEMY = "academy"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"


class StudentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class NarrativeStatus(str, Enum):
    GENERATING = "generating"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class AssessmentStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class AssessmentType(str, Enum):
    VISION_CHECK = "vision_check"
    TOKEN_VERIFICATION = "token_verification"
    SPELLING = "spelling"
    DEFINITION = "definition"
    TEST_OUT = "test_out"
    CONTRACT = "contract"
    CLASSROOM_SESSION = "classroom_session"


class QuestionType(str, Enum):
    SPELLING = "spelling"
    DEFINITION = "definition"
    USAGE = "usage"
    COMPREHENSION = "comprehension"


class VocabularyTier(str, Enum):
    BASELINE = "baseline"
    TARGET = "target"
    STRETCH = "stretch"


class WordBankVisibility(str, Enum):
    GLOBAL = "global"
    PRIVATE = "private"
    MARKETPLACE = "marketplace"


class WordBankCategory(str, Enum):
    GENERAL = "general"
    ACADEMIC = "academic"
    PROFESSIONAL = "professional"
    SPECIALIZED = "specialized"


class GiftStatus(str, Enum):
    PENDING = "pending"
    CLAIMED = "claimed"
    EXPIRED = "expired"


class SessionStatus(str, Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"


# Base Models
class MongoBaseModel(BaseModel):
    """Base model for MongoDB documents"""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


# User Entity
class User(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    email: str
    full_name: str
    password_hash: str
    role: UserRole = UserRole.GUARDIAN
    wallet_balance: float = 0.0
    is_delegated_admin: bool = False
    referral_code: str = Field(default_factory=generate_referral_code)
    referred_by: Optional[str] = None  # referral code of referrer
    linked_brand_id: Optional[str] = None  # for brand_partner role
    brand_approved: bool = False  # admin must approve
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str
    role: UserRole = UserRole.GUARDIAN


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(MongoBaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    created_date: datetime


# Token Mastery Tracking
class MasteredToken(BaseModel):
    token: str
    source_type: str  # "narrative" | "bank" | "test_out"
    source_id: str
    mastered_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Student Entity
class Student(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    full_name: str
    student_code: str = Field(default_factory=generate_student_code)
    access_pin: str = Field(default_factory=generate_pin)
    guardian_id: str
    age: Optional[int] = None
    grade_level: Optional[GradeLevel] = None
    interests: List[str] = Field(default_factory=list)
    virtues: List[str] = Field(default_factory=list)  # Character traits/lessons to develop
    assigned_banks: List[str] = Field(default_factory=list)  # WordBank IDs
    mastered_tokens: List[MasteredToken] = Field(default_factory=list)
    agentic_reach_score: float = 0.0
    biological_target: int = 0  # Age-based expected vocabulary
    total_reading_seconds: int = 0
    total_words_read: int = 0
    average_wpm: float = 0.0
    status: StudentStatus = StudentStatus.ACTIVE
    avatar_url: Optional[str] = None
    # Belief system & culture
    belief_system: str = ""  # e.g. "Christian - Methodist", "Baha'i", "Buddhist", "Hindu"
    cultural_context: str = ""  # e.g. "African American", "Hispanic/Latino", "East Asian"
    language: str = "English"  # Story generation language
    ad_preferences: Dict[str, Any] = Field(default_factory=lambda: {
        "allow_brand_stories": False,
        "preferred_categories": [],
        "blocked_categories": [],
    })
    spellcheck_disabled: bool = False
    spelling_mode: str = "phonetic"  # "exact" or "phonetic"
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StudentCreate(BaseModel):
    full_name: str
    guardian_id: str
    age: Optional[int] = None
    grade_level: Optional[GradeLevel] = None
    interests: List[str] = Field(default_factory=list)


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    grade_level: Optional[GradeLevel] = None
    interests: Optional[List[str]] = None
    virtues: Optional[List[str]] = None
    assigned_banks: Optional[List[str]] = None
    status: Optional[StudentStatus] = None
    belief_system: Optional[str] = None
    cultural_context: Optional[str] = None
    language: Optional[str] = None


# Subscription Entity
class SubscriptionFeatures(BaseModel):
    voice_mentor: bool = False
    contracts: bool = False
    advanced_analytics: bool = False
    custom_narratives: bool = False


class Subscription(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    guardian_id: str
    plan: SubscriptionPlan = SubscriptionPlan.FREE
    student_seats: int = 10
    active_students: int = 0
    bank_access: List[str] = Field(default_factory=list)  # Purchased WordBank IDs
    price_monthly: int = 0  # in cents
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    trial_ends: Optional[datetime] = None
    billing_cycle_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    coupon_code: Optional[str] = None
    features: SubscriptionFeatures = Field(default_factory=SubscriptionFeatures)
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Word Bank Entity
class VocabularyWord(BaseModel):
    word: str
    definition: str
    part_of_speech: str
    example_sentence: str


class WordBank(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    description: str
    category: WordBankCategory = WordBankCategory.GENERAL
    specialty: Optional[str] = None
    visibility: WordBankVisibility = WordBankVisibility.GLOBAL
    grade_range: Dict[str, str] = Field(default_factory=dict)  # {"min": "k", "max": "12"}
    baseline_words: List[VocabularyWord] = Field(default_factory=list)
    target_words: List[VocabularyWord] = Field(default_factory=list)
    stretch_words: List[VocabularyWord] = Field(default_factory=list)
    total_tokens: int = 0
    price: int = 0  # in cents, 0 = free
    owner_id: str
    created_by_role: str = "admin"  # "admin" or "guardian"
    purchase_count: int = 0
    rating: float = 0.0
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WordBankCreate(BaseModel):
    name: str
    description: str
    category: WordBankCategory = WordBankCategory.GENERAL
    specialty: Optional[str] = None
    visibility: WordBankVisibility = WordBankVisibility.GLOBAL
    baseline_words: List[VocabularyWord] = Field(default_factory=list)
    target_words: List[VocabularyWord] = Field(default_factory=list)
    stretch_words: List[VocabularyWord] = Field(default_factory=list)
    price: int = 0


# Narrative Entity
class EmbeddedToken(BaseModel):
    word: str
    tier: VocabularyTier


class VisionCheck(BaseModel):
    question: str
    options: List[str]
    correct_index: int


class Chapter(BaseModel):
    number: int
    title: str
    content: str
    word_count: int
    embedded_tokens: List[EmbeddedToken] = Field(default_factory=list)
    vision_check: VisionCheck


class Narrative(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    title: str
    student_id: str
    bank_ids: List[str] = Field(default_factory=list)
    theme: str
    chapters: List[Chapter] = Field(default_factory=list)
    total_word_count: int = 0
    status: NarrativeStatus = NarrativeStatus.GENERATING
    current_chapter: int = 1
    chapters_completed: List[int] = Field(default_factory=list)
    tokens_to_verify: List[str] = Field(default_factory=list)
    difficulty_level: str = "medium"
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NarrativeCreate(BaseModel):
    student_id: str
    prompt: str
    bank_ids: List[str]


# Assessment Entity
class AssessmentQuestion(BaseModel):
    word: str
    question_type: QuestionType
    prompt: str
    correct_answer: str
    options: Optional[List[str]] = None
    student_answer: Optional[str] = None
    student_definition: Optional[str] = None
    student_sentence: Optional[str] = None
    is_correct: Optional[bool] = None
    feedback: Optional[str] = None
    audio_url: Optional[str] = None


class MisspelledWord(BaseModel):
    word: str
    misspelled_as: str


class Assessment(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    student_id: str
    narrative_id: Optional[str] = None
    type: AssessmentType
    questions: List[AssessmentQuestion] = Field(default_factory=list)
    total_questions: int = 0
    correct_count: int = 0
    accuracy_percentage: float = 0.0
    tokens_mastered: List[str] = Field(default_factory=list)
    misspelled_words: List[MisspelledWord] = Field(default_factory=list)
    status: AssessmentStatus = AssessmentStatus.IN_PROGRESS
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    duration_seconds: int = 0


# ReadLog Entity
class ReadLog(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    student_id: str
    narrative_id: str
    chapter_number: int
    session_start: datetime
    session_end: Optional[datetime] = None
    duration_seconds: int = 0
    words_read: int = 0
    wpm: float = 0.0
    tokens_encountered: List[str] = Field(default_factory=list)
    vision_check_passed: bool = False
    notes: Optional[str] = None
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# WordBank Gift Entity
class WordBankGift(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    bank_id: str
    sender_id: str
    recipient_email: str
    recipient_id: Optional[str] = None
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: GiftStatus = GiftStatus.PENDING
    claimed_at: Optional[datetime] = None
    message: Optional[str] = None
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GiftCreate(BaseModel):
    bank_id: str
    recipient_email: str
    message: Optional[str] = None


# Classroom Session Entity
class ParticipatingStudent(BaseModel):
    student_id: str
    student_name: str
    joined_at: datetime
    progress: Dict[str, Any] = Field(default_factory=dict)


class ClassroomSession(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    teacher_id: str
    narrative_id: str
    session_code: str = Field(default_factory=generate_pin)
    status: SessionStatus = SessionStatus.WAITING
    current_chapter: int = 1
    participating_students: List[ParticipatingStudent] = Field(default_factory=list)
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# System Config Entity
class SystemConfig(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    config_key: str
    config_type: str  # "pricing" | "coupon" | "notification" | "biological_mapping" | "general"
    value: Dict[str, Any]
    is_active: bool = True
    description: Optional[str] = None
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Biological Target Mapping
BIOLOGICAL_TARGETS = {
    3: 1000, 4: 1500, 5: 2000, 6: 2500, 7: 3000,
    8: 4000, 9: 5000, 10: 6000, 11: 7500, 12: 10000,
    13: 12000, 14: 15000, 15: 18000, 16: 20000,
    17: 25000, 18: 30000, 19: 35000, 20: 35000
}


# ==================== WALLET & PAYMENT MODELS ====================

class WalletTransactionType(str, Enum):
    CREDIT = "credit"       # Money added (top-up, refund)
    DEBIT = "debit"         # Money spent (purchase)
    COUPON = "coupon"       # Free credit from coupon


class WalletTransaction(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    user_id: str
    type: WalletTransactionType
    amount: float  # positive for credit, positive amount for debit
    description: str
    reference_id: Optional[str] = None  # payment session or purchase id
    balance_after: float = 0.0
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaymentTransaction(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    user_id: str
    session_id: str  # Stripe checkout session ID
    amount: float
    currency: str = "usd"
    payment_status: str = "pending"  # pending, paid, failed, expired
    status: str = "initiated"        # initiated, completed, failed, expired
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_date: Optional[datetime] = None


# ==================== COUPON MODEL ====================

class CouponType(str, Enum):
    FREE_DAYS = "free_days"
    FREE_STORIES = "free_stories"
    FREE_STUDENTS = "free_students"
    WALLET_CREDIT = "wallet_credit"
    PERCENTAGE_DISCOUNT = "percentage_discount"  # Discount by percentage (0-100%)


class Coupon(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    code: str
    coupon_type: CouponType
    value: float  # days, story count, student count, dollar amount, or percentage (0-100)
    max_uses: int = 0  # 0 = unlimited
    uses_count: int = 0
    is_active: bool = True
    expires_at: Optional[datetime] = None
    created_by: str = ""
    created_by_brand_id: str = ""  # If created by a brand partner
    description: str = ""
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CouponRedemption(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    coupon_id: str
    coupon_code: str
    user_id: str
    coupon_type: CouponType
    value: float
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== ADMIN SUBSCRIPTION PLAN MODEL ====================

class AdminSubscriptionPlan(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    description: str = ""
    price_monthly: float = 0.0  # dollars
    student_seats: int = 10
    story_limit: int = -1  # -1 = unlimited
    features: Dict[str, bool] = Field(default_factory=dict)
    is_active: bool = True
    created_by: str = ""
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== REFERRAL MODEL ====================

class Referral(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    referrer_id: str
    referred_id: str
    referral_code: str
    reward_amount: float = 5.0  # default reward
    reward_given: bool = False
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== DONATION MODEL ====================

class Donation(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    donor_id: Optional[str] = None
    donor_name: str = "Anonymous"
    amount: float
    stories_funded: int = 0  # calculated from amount
    stories_used: int = 0
    payment_session_id: Optional[str] = None
    payment_status: str = "pending"
    message: str = ""
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== BRAND SPONSORSHIP MODELS ====================

class BrandProduct(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    description: str = ""
    category: str = ""


class TargetRegion(BaseModel):
    country: str = ""
    state: str = ""
    city: str = ""
    zip_code: str = ""


class Brand(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    logo_url: str = ""
    website: str = ""
    description: str = ""
    problem_statement: str = ""  # The problem this brand solves
    products: List[BrandProduct] = Field(default_factory=list)
    target_ages: List[int] = Field(default_factory=list)
    target_categories: List[str] = Field(default_factory=list)
    target_regions: List[TargetRegion] = Field(default_factory=list)
    target_languages: List[str] = Field(default_factory=list)
    budget_total: float = 0.0
    budget_spent: float = 0.0
    cost_per_impression: float = 0.05
    is_active: bool = True
    total_impressions: int = 0
    total_stories: int = 0
    onboarding_completed: bool = False
    story_preview: str = ""  # Cached AI-generated story snippet
    story_preview_generated_at: Optional[datetime] = None
    created_by: str = ""
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BrandImpression(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    brand_id: str
    brand_name: str
    narrative_id: str
    student_id: str
    guardian_id: str
    campaign_id: Optional[str] = None
    products_featured: List[str] = Field(default_factory=list)
    cost: float = 0.0
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BrandCampaign(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    brand_id: str
    name: str
    description: str = ""
    products: List[BrandProduct] = Field(default_factory=list)
    target_ages: List[int] = Field(default_factory=list)
    target_categories: List[str] = Field(default_factory=list)
    budget: float = 0.0
    budget_spent: float = 0.0
    cost_per_impression: float = 0.05
    status: str = "active"  # active, paused, completed, pending_approval
    total_impressions: int = 0
    created_by: str = ""
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClassroomSponsorship(MongoBaseModel):
    id: str = Field(default_factory=generate_uuid)
    brand_id: str
    brand_name: str
    classroom_session_id: Optional[str] = None
    teacher_id: Optional[str] = None
    school_name: str = ""
    stories_limit: int = -1
    stories_used: int = 0
    amount_paid: float = 0.0
    is_active: bool = True
    badge_text: str = ""
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StudentAdPreferences(BaseModel):
    allow_brand_stories: bool = False
    preferred_categories: List[str] = Field(default_factory=list)
    blocked_categories: List[str] = Field(default_factory=list)


def get_biological_target(age: int) -> int:
    """Get expected vocabulary target based on age"""
    if age < 3:
        return 500
    elif age > 20:
        return 50000  # Polymath level
    return BIOLOGICAL_TARGETS.get(age, 35000)
