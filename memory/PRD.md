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
- [x] Spelling controls & ad preferences (brand stories toggle)
- [x] Word Bank Marketplace (browse, preview, purchase, add to library)
- [x] Word bank assignment to students
- [x] Parent word bank creation (admin-controlled toggle)
- [x] Wallet system with Stripe
- [x] Referral program

### Teacher Portal (Complete)
- [x] Classroom session management
- [x] Real-time student tracking

### Admin Portal (Complete)
- [x] Statistics dashboard (parents, teachers, students, word banks, stories, revenue, AI cost)
- [x] Word Banks tab - create/delete/list word banks with baseline/target/stretch words
- [x] AI Costs tracking
- [x] Brands management with analytics (impressions, revenue, active brands)
- [x] User management (CRUD, password reset, deactivate, credits)
- [x] Coupon management (create/delete, wallet credit type)
- [x] Plans management
- [x] Billing/ROI configuration
- [x] Feature flags (10 toggles including parent word bank creation, brand sponsorship)
- [x] LLM Config (Emergent vs OpenRouter)
- [x] App Settings (spellcheck, story/assessment limits)

### Brand Partner Portal (Complete)
- [x] Self-service registration & auto-brand creation
- [x] 3-step onboarding wizard
- [x] Problem statement definition (woven into AI-generated stories)
- [x] Logo upload, product management, geo-targeting
- [x] AI Story Preview (cached snippet)
- [x] Analytics Dashboard (impressions, revenue, campaigns)
- [x] Campaign management
- [x] Coupon creation (percentage-based)
- [x] Budget management with Stripe

### Brand Story Integration (Verified Working)
- [x] Active brands with products are automatically integrated into student stories
- [x] Brand problem statements are used to make product mentions organic
- [x] Impressions tracked per brand per story generation
- [x] Controlled by: feature flag (admin), ad_preferences (parent per-student)

### Authentication & Email (Complete)
- [x] JWT auth with role-based routing
- [x] Forgot Password with 6-digit code via Resend
- [x] Email verification

### Wallet & Payment System (Complete)
- [x] Wallet with Stripe top-up
- [x] Coupon redemption (fixed amount & percentage)
- [x] Admin coupon/plan management, credit addition

### Multi-lingual UI (Complete)
- [x] 20 languages, localStorage persistence, RTL Arabic support

## Bug Fixes
- [x] P0: Fixed backend crash - `get_current_brand_partner` NameError (used before defined) - Mar 7, 2026
- [x] Admin Word Banks tab missing - added full CRUD UI - Mar 7, 2026

## Prioritized Backlog

### P0 - High Priority
- [ ] Refactor `backend/server.py` into modular FastAPI routers (4300+ lines monolith)

### P1 - Medium Priority
- [ ] Expand payment integrations (Cash App, Zelle, Venmo, PayPal) - user requested
- [ ] Accessibility features (deaf/HoH users)
- [ ] Granular admin analytics

### P2 - Low Priority
- [ ] AdminPortal.jsx and BrandPortal.jsx component extraction
- [ ] Student gamification (XP, badges, leaderboard)
- [ ] COPPA/FERPA compliance review
- [ ] Automated recurring subscription billing

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Guardian: allen@ourfamily.contact / LexiAdmin2026!
