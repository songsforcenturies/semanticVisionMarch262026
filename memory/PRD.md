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

### Brand Partner Portal (Complete - Feb 2026)
- [x] Self-service registration & approval workflow
- [x] Campaign management & analytics dashboard
- [x] Budget management with Stripe integration
- [x] Impression tracking & reporting

### Wallet & Payment System (Complete)
- [x] Wallet with Stripe top-up
- [x] Coupon redemption
- [x] Admin coupon/plan management

### Multi-lingual UI Support (Complete - Mar 2026)
- [x] 20 languages: English, Spanish, French, Chinese, Hindi, Arabic, Bengali, Portuguese, Russian, Japanese, German, Korean, Turkish, Vietnamese, Italian, Thai, Polish, Dutch, Swahili, Malay
- [x] Language switcher component on all public & portal pages
- [x] localStorage persistence (leximaster_lang)
- [x] RTL support for Arabic
- [x] Translation coverage: Landing, Auth (all login/register pages), Guardian Portal, Teacher Portal, Brand Portal, Donate Page

### Other Features (Complete)
- [x] Referral system with wallet rewards
- [x] Public donation page ("Sponsor a Reader")
- [x] Brand sponsorship in-story ads with parental controls

## Prioritized Backlog

### P0 - High Priority
- [ ] Accessibility features (deaf/HoH users)
- [ ] Refactor `backend/server.py` into modular FastAPI routers

### P1 - Medium Priority
- [ ] Expand payment integrations (PayPal, Google/Apple Pay, CashApp/Venmo)
- [ ] Granular admin analytics

### P2 - Low Priority
- [ ] AdminPortal.jsx component extraction
- [ ] Student gamification (XP, badges, leaderboard)
- [ ] COPPA/FERPA compliance review
- [ ] Automated recurring subscription billing
- [ ] Regional feature delegation
