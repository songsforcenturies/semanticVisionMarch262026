# LexiMaster - Product Requirements Document

## Original Problem Statement
Build "LexiMaster," a high-quality educational platform for students, guardians, and teachers, focusing on vocabulary building and character education through AI-generated stories. Multi-role system (Guardian, Teacher, Student, Admin, Brand Partner), wallet/payment system, brand sponsorship model, and self-service brand partner portal.

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async), JWT Auth, WebSockets
- **Frontend:** React 18, TypeScript, Tailwind CSS, Shadcn/UI, React Router, React Query
- **AI:** OpenAI (Emergent LLM Key), OpenRouter
- **Payments:** Stripe
- **i18n:** react-i18next with 20 languages

## What's Been Implemented

### Core Platform (Complete)
- [x] Multi-role auth: Guardian, Teacher, Student, Admin, Brand Partner
- [x] AI-powered story generation (personalized with virtues, belief, culture, language)
- [x] AI-evaluated written assessments
- [x] Story reader with click-to-define words
- [x] Automated reading timer
- [x] 60/30/10 vocabulary learning system

### Guardian Portal (Complete)
- [x] Full CRUD student management
- [x] Spelling controls & ad preferences
- [x] Marketplace for word banks
- [x] Wallet system with Stripe
- [x] Referral program

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

### Brand Partner Portal (Enhanced - Mar 2026)
- [x] Self-service registration & auto-brand creation
- [x] 3-step onboarding wizard: Brand Info → Logo & Media → Targeting
- [x] Problem statement definition (woven into AI-generated stories)
- [x] Logo upload (max 10MB, PNG/JPG/WebP/SVG)
- [x] Product CRUD management (add/edit/delete products)
- [x] Geo-targeting with regions (country, state, city, zip)
- [x] Target language selection (20 languages)
- [x] Campaign management & analytics dashboard
- [x] Budget management with Stripe integration
- [x] Impression tracking & reporting

### Wallet & Payment System (Complete)
- [x] Wallet with Stripe top-up
- [x] Coupon redemption
- [x] Admin coupon/plan management

### Multi-lingual UI Support (Complete - Mar 2026)
- [x] 20 languages with language switcher
- [x] localStorage persistence
- [x] RTL support for Arabic

### Other Features (Complete)
- [x] Referral system with wallet rewards
- [x] Public donation page ("Sponsor a Reader")
- [x] Brand sponsorship in-story ads with parental controls

## Prioritized Backlog

### P0 - High Priority
- [ ] Refactor `backend/server.py` into modular FastAPI routers (3500+ lines monolith)

### P1 - Medium Priority
- [ ] Accessibility features (deaf/HoH users)
- [ ] Expand payment integrations (PayPal, Google/Apple Pay, CashApp/Venmo)
- [ ] Granular admin analytics

### P2 - Low Priority
- [ ] AdminPortal.jsx component extraction
- [ ] Student gamification (XP, badges, leaderboard)
- [ ] COPPA/FERPA compliance review
- [ ] Automated recurring subscription billing
- [ ] Regional feature delegation
