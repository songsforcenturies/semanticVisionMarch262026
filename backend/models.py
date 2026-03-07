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


# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    GUARDIAN = "guardian"
    TEACHER = "teacher"


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
    assigned_banks: List[str] = Field(default_factory=list)  # WordBank IDs
    mastered_tokens: List[MasteredToken] = Field(default_factory=list)
    agentic_reach_score: float = 0.0
    biological_target: int = 0  # Age-based expected vocabulary
    total_reading_seconds: int = 0
    total_words_read: int = 0
    average_wpm: float = 0.0
    status: StudentStatus = StudentStatus.ACTIVE
    avatar_url: Optional[str] = None
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
    assigned_banks: Optional[List[str]] = None
    status: Optional[StudentStatus] = None


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


def get_biological_target(age: int) -> int:
    """Get expected vocabulary target based on age"""
    if age < 3:
        return 500
    elif age > 20:
        return 50000  # Polymath level
    return BIOLOGICAL_TARGETS.get(age, 35000)
