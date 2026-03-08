# Semantic Vision - Product Requirements Document

## Original Problem Statement
Build "Semantic Vision," a high-quality educational platform — "Learning How to Read increases your vocabulary, which is VISION to your MIND." Multi-role system (Parent/School, Teacher, Student, Admin, Brand Partner), wallet/payment system, brand sponsorship model, and self-service brand partner portal.

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async), JWT Auth, WebSockets
- **Frontend:** React 18, Tailwind CSS, Shadcn/UI, React Router, React Query
- **AI:** OpenAI GPT-5.2 (Emergent LLM Key), OpenRouter
- **Payments:** Stripe
- **Email:** Resend
- **Currency:** Open Exchange Rates API, ip-api.com
- **i18n:** react-i18next (20 languages)

## Implemented Features

### Core: Multi-role platform with AI story generation, vocabulary system, brand integration
### Admin: Stats, Word Banks (CRUD + category filter + edit), AI Costs, Brands, Users, Coupons, Contests (create/edit/pause/delete), Plans, Billing/ROI, Features, LLM Config, Settings
### Parent Portal: Students, Marketplace, Wallet, Invite & Earn (leaderboard + contests), Progress
### Word Bank Compliance: Parent banks forced private, admin oversight, created_by_role tracking
### Currency: Auto-detect via IP, 50+ countries, live exchange rates, pegged to USD
### Rebrand: LexiMaster → Semantic Vision (all 20 locales, backend, frontend, page title)

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Guardian: allen@ourfamily.contact / LexiAdmin2026!

## Backlog
- [ ] P0: Refactor server.py into modular routers
- [ ] P1: Payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] P1: AI word content moderation
- [ ] P2: Student gamification, accessibility, COPPA/FERPA
