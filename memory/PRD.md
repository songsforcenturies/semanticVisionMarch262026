# Semantic Vision - Product Requirements Document

## Original Problem Statement
Build "Semantic Vision," a high-quality educational platform — "Learning How to Read increases your vocabulary, which is VISION to your MIND." Multi-role system (Parent/School, Teacher, Student, Admin, Brand Partner), wallet/payment system, brand sponsorship model, and self-service brand partner portal.

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async), JWT Auth, WebSockets
- **Frontend:** React 18, Tailwind CSS, Shadcn/UI, React Router, React Query, Framer Motion
- **AI:** OpenAI GPT-5.2 (Emergent LLM Key), OpenRouter
- **Payments:** Stripe
- **Email:** Resend
- **Currency:** Open Exchange Rates API, ip-api.com
- **i18n:** react-i18next (20 languages)
- **Fonts:** Sora (headlines), Plus Jakarta Sans (body)

## Implemented Features

### Core: Multi-role platform with AI story generation, vocabulary system, brand integration
### Admin: Stats, Word Banks (CRUD + category filter + edit), AI Costs, Brands, Users, Coupons, Contests (create/edit/pause/delete), Plans, Billing/ROI, Features, LLM Config, Settings
### Parent Portal: Students, Marketplace, Wallet, Invite & Earn (leaderboard + contests), Progress
### Word Bank Compliance: Parent banks forced private, admin oversight, created_by_role tracking
### Currency: Auto-detect via IP, 50+ countries, live exchange rates, pegged to USD
### Rebrand: LexiMaster -> Semantic Vision (all 20 locales, backend, frontend, page title)

### NEW (Feb 2026):
- **Technical Specifications Document:** Comprehensive document at `/app/memory/TECHNICAL_SPECIFICATIONS.md` covering patentable features — real-time brand integration pipeline, belief-system awareness, 60/30/10 vocabulary system, consent-gated advertising model. Suitable for provisional patent application.
- **Landing Page Redesign:** Complete redesign of LandingPage.jsx from brutalist style to premium dark theme with gold/teal accents. Sections: Hero with brand narrative, Stats bar, Philosophy, How It Works (3 steps), Brand Integration innovation, Cultural Awareness, 60/30/10 Learning System, Role cards (For Everyone), CTA, Footer. Uses Framer Motion animations, AI-generated illustrations, Sora/Plus Jakarta Sans fonts. All navigation links verified working.

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Guardian: allen@ourfamily.contact / LexiAdmin2026!

## Backlog
- [ ] P0: Refactor server.py into modular routers
- [ ] P1: Finalize and verify Coupon & Credit system (brands creating coupons, admins adding credits)
- [ ] P1: Payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] P1: AI word content moderation
- [ ] P2: Student gamification, accessibility, COPPA/FERPA
- [ ] P2: User Demo Flow for presentations
- [ ] P2: Accessibility features (text-to-sign-language for deaf users)
- [ ] P2: Granular admin analytics dashboard
- [ ] P3: Extract AdminPortal.jsx tabs into dedicated components
