# LexiMaster - Product Requirements Document

## Original Problem Statement
Build "LexiMaster," a high-quality educational platform for students, guardians, and teachers, focusing on vocabulary building and character education through AI-generated stories. Multi-role system (Guardian/Parent/School, Teacher, Student, Admin, Brand Partner), wallet/payment system, brand sponsorship model, and self-service brand partner portal.

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async), JWT Auth, WebSockets
- **Frontend:** React 18, TypeScript, Tailwind CSS, Shadcn/UI, React Router, React Query
- **AI:** OpenAI GPT-5.2 (Emergent LLM Key), OpenRouter
- **Payments:** Stripe
- **Email:** Resend (transactional emails)
- **i18n:** react-i18next with 20 languages
- **Currency:** Open Exchange Rates API (open.er-api.com), ip-api.com geolocation

## What's Been Implemented

### Core Platform (Complete)
- [x] Multi-role auth: Parent/School, Teacher, Student, Admin, Brand Partner
- [x] AI-powered story generation with brand integration (GPT-5.2)
- [x] AI-evaluated written assessments
- [x] Story reader with click-to-define words
- [x] Automated reading timer
- [x] 60/30/10 vocabulary learning system

### Parent / School Portal (Complete)
- [x] Full CRUD student management (name, age, grade, interests, virtues, belief, culture, language)
- [x] Spelling controls & ad preferences toggle buttons (green=ON, red=OFF)
- [x] Word Bank Marketplace with currency-localized prices
- [x] Word bank assignment to students
- [x] Parent word bank creation (admin-controlled toggle)
- [x] Wallet system with Stripe + currency-localized display
- [x] Referral program with total earnings display + referral history
- [x] Currency auto-detection based on user's IP/country

### Teacher Portal (Complete)
- [x] Classroom session management
- [x] Real-time student tracking

### Admin Portal (Complete)
- [x] Statistics dashboard
- [x] Word Banks tab - create/delete/list word banks
- [x] AI Costs tracking
- [x] Brands management with analytics
- [x] User management (CRUD, password reset, deactivate, credits)
- [x] Coupon management
- [x] Plans management
- [x] Billing/ROI configuration (including configurable referral reward amount in USD)
- [x] Feature flags (10 toggles)
- [x] LLM Config (Emergent vs OpenRouter)
- [x] App Settings

### Brand Partner Portal (Complete)
- [x] Self-service registration, onboarding wizard
- [x] Problem statement, logo, products, geo-targeting
- [x] AI Story Preview, Analytics Dashboard
- [x] Campaign management, coupon creation
- [x] Budget management with Stripe

### Currency Localization (New - Mar 8, 2026)
- [x] Auto-detect user's country via IP geolocation (ip-api.com)
- [x] Map country to local currency (50+ countries supported)
- [x] Live exchange rates from Open Exchange Rates API (6-hour cache)
- [x] All wallet, marketplace, referral amounts displayed in local currency
- [x] All money internally pegged to USD

### Referral System Enhanced (Mar 8, 2026)
- [x] Total referral earnings displayed prominently on Invite & Earn tab
- [x] Referral count + total earned + friends saved stats
- [x] Referral history with per-referral reward amounts
- [x] Admin-configurable referral reward amount (Billing/ROI tab)
- [x] Dynamic reward amount displayed (not hardcoded)

### Authentication & Email (Complete)
- [x] JWT auth with role-based routing
- [x] Forgot Password with 6-digit code via Resend
- [x] Email verification

### Multi-lingual UI (Complete)
- [x] 20 languages, localStorage persistence, RTL Arabic support

## Bug Fixes
- [x] P0: Backend crash - `get_current_brand_partner` NameError - Mar 7, 2026
- [x] Admin Word Banks tab missing - Mar 7, 2026
- [x] Toggle buttons (Spellcheck/Phonetic/Brand Stories) not changing color - Mar 8, 2026
  - Root cause 1: Admin couldn't toggle because guardian_id ownership check blocked them
  - Root cause 2: Student model missing spellcheck_disabled/spelling_mode fields (stripped from API response)

## Prioritized Backlog

### P0 - High Priority
- [ ] Refactor `backend/server.py` into modular FastAPI routers (4300+ lines monolith)

### P1 - Medium Priority
- [ ] Expand payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] Accessibility features (deaf/HoH users)
- [ ] Granular admin analytics

### P2 - Low Priority
- [ ] AdminPortal.jsx and BrandPortal.jsx component extraction
- [ ] Student gamification (XP, badges, leaderboard)
- [ ] COPPA/FERPA compliance review
- [ ] Manual currency picker (currently auto-detect only)

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Guardian: allen@ourfamily.contact / LexiAdmin2026!
