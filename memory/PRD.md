# LexiMaster - Product Requirements Document

## Original Problem Statement
Build "LexiMaster," a high-quality educational platform for students, guardians, and teachers, focusing on vocabulary building and character education through AI-generated stories. Multi-role system (Guardian/Parent/School, Teacher, Student, Admin, Brand Partner), wallet/payment system, brand sponsorship model, and self-service brand partner portal.

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async), JWT Auth, WebSockets
- **Frontend:** React 18, TypeScript, Tailwind CSS, Shadcn/UI, React Router, React Query
- **AI:** OpenAI (Emergent LLM Key), OpenRouter
- **Payments:** Stripe
- **Email:** Resend (transactional emails)
- **i18n:** react-i18next with 20 languages

## What's Been Implemented

### Core Platform (Complete)
- [x] Multi-role auth: Parent/School, Teacher, Student, Admin, Brand Partner
- [x] AI-powered story generation (personalized with virtues, belief, culture, language)
- [x] AI-evaluated written assessments
- [x] Story reader with click-to-define words
- [x] Automated reading timer
- [x] 60/30/10 vocabulary learning system

### Parent / School Portal (Complete)
- [x] Full CRUD student management
- [x] Spelling controls & ad preferences
- [x] Marketplace for word banks
- [x] Wallet system with Stripe
- [x] Referral program
- [x] Parent word bank creation (admin-controlled toggle) - Mar 7, 2026

### Teacher Portal (Complete)
- [x] Classroom session management
- [x] Real-time student tracking

### Admin Portal (Complete)
- [x] System-wide settings & feature flags
- [x] AI provider config (Emergent vs OpenRouter)
- [x] Cost tracking, coupons, subscription plans
- [x] Billing/ROI configuration
- [x] Brand sponsorship management
- [x] User role management
- [x] Full user CRUD: create (with temp password), edit, reset password, deactivate/reactivate, delete
- [x] Delegated admin privileges
- [x] Parent Word Bank Creation toggle (feature flag) - Mar 7, 2026

### UI Naming (Updated - Mar 2026)
- [x] "Guardian" renamed to "Parent / School" across all UI, translations (20 languages)
- [x] Role-based login routing: admin->/admin, teacher->/teacher-portal, brand->/brand-portal, parent->/portal

### Brand Partner Portal (Enhanced - Mar 2026)
- [x] Self-service registration & auto-brand creation
- [x] 3-step onboarding wizard: Brand Info -> Logo & Media -> Targeting
- [x] Problem statement definition (woven into AI-generated stories)
- [x] Logo upload (max 10MB, PNG/JPG/WebP/SVG)
- [x] Product CRUD management (add/edit/delete products)
- [x] Geo-targeting with regions (country, state, city, zip)
- [x] Target language selection (20 languages)
- [x] AI Story Preview (cached short story snippet showing brand integration)
- [x] Analytics Dashboard (impression trends, campaign/product breakdown, velocity metrics)
- [x] Campaign management & analytics dashboard
- [x] Budget management with Stripe integration
- [x] Impression tracking & reporting
- [x] Brand coupon creation (percentage-based, unlimited redemptions)

### Authentication & Email (Mar 2026)
- [x] Forgot Password with 6-digit code via Resend email (15-min expiry)
- [x] Email verification on registration (30-min expiry)
- [x] "Forgot Password?" link on login page with 3-step wizard
- [x] Resend email integration (test mode - needs domain verification for production)

### Wallet & Payment System (Complete)
- [x] Wallet with Stripe top-up
- [x] Coupon redemption (fixed amount & percentage)
- [x] Admin coupon/plan management
- [x] Admin credit addition to any user's wallet

### Multi-lingual UI Support (Complete - Mar 2026)
- [x] 20 languages with language switcher
- [x] localStorage persistence
- [x] RTL support for Arabic

### Other Features (Complete)
- [x] Referral system with wallet rewards
- [x] Public donation page ("Sponsor a Reader")
- [x] Brand sponsorship in-story ads with parental controls

## Bug Fixes (Mar 7, 2026)
- [x] P0: Fixed critical backend crash - `get_current_brand_partner` function used before definition causing NameError, crashing entire FastAPI server with 502 on all requests. This was the root cause of the Parent/School login loop bug.

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
- [ ] Regional feature delegation

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Guardian: allen@ourfamily.contact / LexiAdmin2026!
