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
- [x] 60/30/10 vocabulary learning system

### Parent / School Portal (Complete)
- [x] Full CRUD student management
- [x] Spelling controls & ad preferences toggle buttons (green=ON, red=OFF)
- [x] Word Bank Marketplace with currency-localized prices
- [x] Parent word bank creation (admin-controlled toggle)
- [x] Wallet system with Stripe + currency-localized display
- [x] Referral program with total earnings, referral history
- [x] Referral contest leaderboard with countdown timer and ranked users
- [x] Currency auto-detection based on user's IP/country

### Admin Portal (Complete)
- [x] Statistics, Word Banks, AI Costs, Brands, Users, Coupons tabs
- [x] **Contests tab** — Create/manage referral contests with configurable prizes (1st, 2nd, 3rd place), date ranges, pause/activate/delete
- [x] Plans, Billing/ROI (configurable referral reward USD amount), Features, LLM Config, App Settings
- [x] Parent Portal link in header for quick navigation

### Referral Contest System (New - Mar 8, 2026)
- [x] Admin creates contests: title, description, grand prize, prize value, start/end dates
- [x] Runner-up prizes (2nd, 3rd place) configurable
- [x] LIVE/PAUSED/ENDED status badges
- [x] Pause/Activate/Delete contest controls
- [x] Purple gradient contest banner on Parent Portal with countdown timer
- [x] Live leaderboard ranking users by referral count
- [x] Privacy-masked display names (e.g. "Allen A.")
- [x] "Your Rank" indicator when user appears on leaderboard
- [x] Leaderboard filtered by contest date range

### Currency Localization (Mar 8, 2026)
- [x] Auto-detect country via IP geolocation
- [x] 50+ countries mapped to currencies with symbols
- [x] Live exchange rates (6-hour cache)
- [x] All wallet, marketplace, referral amounts in local currency
- [x] All money internally pegged to USD

### Brand Partner Portal (Complete)
- [x] Self-service registration, onboarding, products, geo-targeting
- [x] AI Story Preview, Analytics Dashboard, Campaign management
- [x] Coupon creation, Budget management with Stripe

### Authentication & Email (Complete)
- [x] JWT auth, Forgot Password with Resend, Email verification

## Bug Fixes (This Session)
- [x] P0: Backend crash - get_current_brand_partner NameError
- [x] Toggle buttons not changing color (model fields + admin auth bypass)

## Prioritized Backlog

### P0
- [ ] Refactor backend/server.py into modular FastAPI routers (4500+ lines)

### P1
- [ ] Payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] Accessibility features (deaf/HoH users)

### P2
- [ ] Component extraction (AdminPortal.jsx, BrandPortal.jsx)
- [ ] Student gamification (XP, badges)
- [ ] Manual currency picker
- [ ] COPPA/FERPA compliance

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Guardian: allen@ourfamily.contact / LexiAdmin2026!
