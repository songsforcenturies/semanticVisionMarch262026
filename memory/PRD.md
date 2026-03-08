# LexiMaster - Product Requirements Document

## Original Problem Statement
Build "LexiMaster," a high-quality educational platform for students, guardians, and teachers, focusing on vocabulary building and character education through AI-generated stories.

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async), JWT Auth, WebSockets
- **Frontend:** React 18, Tailwind CSS, Shadcn/UI, React Router, React Query
- **AI:** OpenAI GPT-5.2 (Emergent LLM Key), OpenRouter
- **Payments:** Stripe
- **Email:** Resend
- **Currency:** Open Exchange Rates API, ip-api.com geolocation
- **i18n:** react-i18next (20 languages)

## Implemented Features

### Admin Portal
- [x] Statistics, AI Costs, Brands, Users, Coupons, Plans, Billing/ROI, Features, LLM Config, App Settings
- [x] **Word Banks tab** — Create, Edit, Delete word banks with category filter (All/General/Academic/Professional/Specialized), visibility badges (PRIVATE/GLOBAL), Parent-Created tags
- [x] **Contests tab** — Create/manage referral contests with prizes (1st/2nd/3rd), date ranges, pause/activate/delete
- [x] Configurable referral reward amount (USD)
- [x] Parent Portal quick-nav link

### Parent / School Portal
- [x] Student management with toggle buttons (green=ON, red=OFF)
- [x] Word Bank Marketplace with currency-localized prices, category filter
- [x] **Parent word bank creation** (admin toggle) — **forced PRIVATE**, only visible to creator + their children
- [x] Wallet system with Stripe + currency-localized display
- [x] Referral system with total earnings, history, contest leaderboard with countdown
- [x] Currency auto-detection via IP (50+ countries)

### Word Bank Privacy & Compliance (Mar 8, 2026)
- [x] Parent-created banks forced to `visibility: private` server-side
- [x] Parents can only see: global/marketplace banks + their own private banks
- [x] Other parents CANNOT see another parent's private banks
- [x] Parents can only edit their own banks, cannot change visibility from private
- [x] Admin can see/edit ALL banks including private ones for oversight
- [x] `created_by_role` field tracks whether admin or guardian created the bank

### Referral Contest System (Mar 8, 2026)
- [x] Admin creates contests with prizes, dates, runner-up prizes
- [x] Live leaderboard ranked by referral count
- [x] Contest banner with countdown timer on Parent Portal
- [x] Privacy-masked display names

### Brand Partner Portal (Complete)
- [x] Self-service registration, onboarding, products, geo-targeting
- [x] AI Story Preview, Analytics, Campaign management, Coupons
- [x] Brand integration proven in story generation

### Auth & Email
- [x] JWT auth, Forgot Password (Resend), Email verification

## Bug Fixes (This Session)
- [x] P0: Backend crash (get_current_brand_partner NameError)
- [x] Toggle buttons not changing color
- [x] Admin blocked from toggle endpoints (guardian_id ownership check)

## Prioritized Backlog

### P0
- [ ] Refactor backend/server.py into modular FastAPI routers (4500+ lines)

### P1
- [ ] Payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] Word content moderation (AI-powered inappropriate word detection)
- [ ] Accessibility features

### P2
- [ ] Component extraction (AdminPortal.jsx, BrandPortal.jsx)
- [ ] Student gamification, manual currency picker, COPPA/FERPA compliance

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Guardian: allen@ourfamily.contact / LexiAdmin2026!
- Other Guardian: other@test.com / Test1234!
