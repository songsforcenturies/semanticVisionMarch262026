# Semantic Vision — Complete Technical Specification
## Generated: March 12, 2026

---

## 1. APPLICATION OVERVIEW

**Name:** Semantic Vision  
**Type:** Full-stack educational platform (AI-powered storytelling & vocabulary)  
**Domain:** semanticvision.ai  
**Users:** Admins, Guardians (Parents), Students, Teachers, Brand Partners  

---

## 2. TECH STACK

### Frontend
- **Framework:** React 19 (Create React App with CRACO)
- **Styling:** Tailwind CSS + Shadcn/UI components
- **State:** React Query (TanStack Query) for data fetching
- **Charts:** Recharts
- **Routing:** React Router DOM v6
- **Internationalization:** react-i18next
- **Icons:** Lucide React
- **PDF/Image:** html2canvas
- **Package Manager:** Yarn

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Database:** MongoDB (Motor async driver)
- **Authentication:** JWT (python-jose) + Passlib/bcrypt
- **AI Integration:** OpenAI GPT (text generation), OpenAI Whisper (speech-to-text) via Emergent LLM Key
- **Email:** Resend API
- **Payments:** Stripe + PayPal
- **Video Calls:** Daily.co
- **PDF Generation:** ReportLab
- **Server:** Uvicorn

### Database
- **Type:** MongoDB
- **Collections:** 37+ collections
- **Key Collections:** users, students, word_banks, narratives, assessments, read_logs, subscriptions, payment_transactions, session_logs, support_tickets, admin_messages, brand_media, brands, etc.

---

## 3. ENVIRONMENT VARIABLES REQUIRED

### Backend (.env)
```
MONGO_URL=<mongodb_connection_string>
DB_NAME=leximaster_db
CORS_ORIGINS=*
JWT_SECRET_KEY=<secret_key>
EMERGENT_LLM_KEY=<emergent_universal_key>
RESEND_API_KEY=<resend_api_key>
SENDER_EMAIL="Semantic Vision <hello@semanticvision.ai>"
STRIPE_SECRET_KEY=<stripe_key>
PAYPAL_CLIENT_ID=<paypal_client_id>
PAYPAL_SECRET=<paypal_secret>
DAILY_CO_API_KEY=<daily_co_key>
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=<deployed_backend_url>
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

---

## 4. PROJECT STRUCTURE

```
/app/
├── backend/
│   ├── server.py              # Main FastAPI app, startup bootstrap, router registration
│   ├── auth.py                # JWT auth, password hashing, user dependency injection
│   ├── database.py            # MongoDB connection (Motor async client)
│   ├── models.py              # Pydantic models (User, Student, Narrative, etc.)
│   ├── services.py            # Shared services (email, WebSocket manager)
│   ├── seed_word_banks.py     # Default word bank data for bootstrap
│   ├── seed_brands.py         # Default brand data
│   ├── requirements.txt       # Python dependencies
│   ├── routes/
│   │   ├── admin.py           # Admin portal endpoints (stats, users, settings, impersonation)
│   │   ├── auth.py            # Auth routes (register, login, forgot password, email verify)
│   │   ├── backup.py          # Database backup & restore endpoints
│   │   ├── brands.py          # Brand management, campaigns, analytics
│   │   ├── documents.py       # Health check, root endpoint
│   │   ├── media.py           # Digital media upload, YouTube, approval
│   │   ├── narratives.py      # AI story generation, chapters, assessments, progress
│   │   ├── recordings.py      # Audio recording, read-aloud, messaging, spelling bee
│   │   ├── sessions.py        # Student session tracking (login time logs)
│   │   ├── students.py        # Student CRUD, progress reports, export
│   │   ├── support.py         # User-to-admin support ticket system
│   │   └── wordbanks.py       # Word bank CRUD, token management
│   ├── services/
│   │   └── story_service.py   # AI prompt construction with media injection
│   ├── uploads/               # File storage (recordings, media, screenshots)
│   └── tests/                 # Pytest test files
├── frontend/
│   ├── src/
│   │   ├── App.js             # Main app with routing, global SupportWidget
│   │   ├── lib/api.js         # All API client functions
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx # Auth state, session tracking, login/logout
│   │   ├── components/
│   │   │   ├── ui/            # Shadcn/UI base components
│   │   │   ├── brutal/        # Custom "brutal" design system components
│   │   │   ├── guardian/      # Guardian portal components (ProgressTab, etc.)
│   │   │   ├── admin/         # Admin portal tab components
│   │   │   ├── InlineMediaPlayer.jsx  # In-story media rendering
│   │   │   └── SupportWidget.jsx      # Global support ticket widget
│   │   ├── pages/
│   │   │   ├── AdminPortal.jsx         # 21-tab admin dashboard
│   │   │   ├── GuardianPortal.jsx      # Parent dashboard
│   │   │   ├── StudentAcademy/         # Student learning interface
│   │   │   ├── NarrativeReader/        # Story reading + assessments
│   │   │   └── ...                     # Login, Register, Landing, etc.
│   │   └── i18n/              # Translations
│   └── package.json
└── memory/
    └── PRD.md                 # Product requirements document
```

---

## 5. KEY FEATURES IMPLEMENTED

### Admin Portal (21 Tabs)
- Platform statistics & analytics
- Word bank management (CRUD + token editing)
- User management with role assignment
- Delegated admin system
- User impersonation ("View as User")
- Direct messaging (individual + broadcast, with email)
- AI cost tracking & model configuration
- Stripe + PayPal payment integration management
- Subscription plan management
- Coupon system
- Affiliate program management
- Spelling bee contests
- Brand partner management
- Digital media management (audio/video/YouTube)
- Screen sharing via Daily.co
- Support ticket management
- **Backup & Restore** (full database export/import)
- Storage settings (per-user limits, recording duration)
- App settings (feature flags, parental controls)

### Guardian/Parent Portal
- Student management (add, edit, PIN changes)
- Student ID cards
- Progress reports with charts (vocabulary, reading, assessments)
- **Cumulative Time Log** (daily hours, total days, avg/day)
- Parental controls (recording mode, media settings)
- Digital media settings per student
- Subscription & billing management
- Wallet system (top-up, transactions)
- Referral system with rewards

### Student Portal
- AI-generated narrative stories with vocabulary integration
- Interactive reading with word definitions on click
- Vision check & written answer assessments
- Audio recording (read-aloud) with compliance modal
- Music library (liked/heard media)
- Personal dashboard with progress

### Story Generation (AI)
- OpenAI GPT-powered narrative generation
- Dynamic media injection (audio/video placeholders in stories)
- Smart chapter-based structure with assessments
- Auto-save progress on chapter change
- Recording compliance (blur story until recording starts)

### Authentication & Security
- JWT-based authentication
- Email verification (Resend API)
- Password reset flow
- Student PIN-based login
- Admin impersonation with proper JWT handling
- Self-bootstrapping (auto-create admin on empty DB)

---

## 6. DATABASE SCHEMA (KEY COLLECTIONS)

### users
- id, email, full_name, password_hash, role (admin/guardian/teacher/brand_partner)
- is_delegated_admin, wallet_balance, referral_code, is_active

### students
- id, guardian_id, full_name, age, grade_level, student_code, session_code
- interests, heritage, learning_language, virtues, agentic_reach_score

### word_banks
- id, name, description, difficulty, owner_id, tokens (array of word objects)

### narratives
- id, student_id, title, chapters (array), bank_ids, status, last_completed_chapter_index

### assessments
- id, narrative_id, student_id, type, questions, answers, accuracy_percentage, status

### subscriptions
- id, guardian_id, plan, student_seats, active_students, stripe_subscription_id

### session_logs (NEW)
- id, student_id, started_at, last_active, ended_at, duration_seconds, date

### support_tickets
- id, user_id, message, status, attachments, replies, created_at

### brand_media
- id, brand_id, title, type, source, url, status, price_stream, price_download

---

## 7. API ENDPOINTS (KEY ROUTES)

### Auth (/api/auth/*)
- POST /register, /login, /student-login, /forgot-password, /reset-password, /verify-email

### Students (/api/students/*)
- GET/POST /students, GET/PUT/DELETE /students/{id}
- GET /students/{id}/progress, /time-log, /parental-controls
- GET /students/{id}/export-progress (HTML report)

### Narratives (/api/narratives/*)
- POST /narratives/generate (AI story generation)
- POST /narratives/{id}/save_progress
- GET /narratives/{id}/chapters

### Sessions (/api/sessions/*)
- POST /sessions/start, /heartbeat, /end

### Admin (/api/admin/*)
- GET /stats, /costs, /settings, /users, /messages
- POST /admin/messages, /admin/impersonate/{user_id}
- GET /admin/backup, POST /admin/restore
- GET /admin/backup/status

### Word Banks (/api/word-banks/*)
- GET/POST /word-banks, PUT/DELETE /word-banks/{id}

### Support (/api/support/*)
- POST /support/ticket, GET /support/tickets
- POST /support/ticket/{id}/reply

### Media (/api/media/*)
- POST /media/upload, /media/youtube
- GET /media, /media/student
- PUT /media/{id}/status

---

## 8. 3RD PARTY INTEGRATIONS

| Service | Purpose | Key Required |
|---------|---------|--------------|
| OpenAI GPT | AI story generation | Emergent LLM Key |
| OpenAI Whisper | Speech-to-text | Emergent LLM Key |
| Stripe | Payment processing | STRIPE_SECRET_KEY |
| PayPal | Payment processing | PAYPAL_CLIENT_ID + SECRET |
| Resend | Transactional emails | RESEND_API_KEY |
| Daily.co | Screen sharing/video | DAILY_CO_API_KEY |
| ReportLab | PDF generation | None (Python lib) |

---

## 9. STARTUP BOOTSTRAP

On empty database, server.py automatically:
1. Creates master admin user (allen@songsforcenturies.com)
2. Creates admin subscription
3. Seeds 5 default word banks
4. Creates database indexes for performance

---

## 10. RUNNING LOCALLY

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend
```bash
cd frontend
yarn install
yarn start  # runs on port 3000
```

### Database
```bash
mongod --dbpath /data/db  # MongoDB on port 27017
```
