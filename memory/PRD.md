# Semantic Vision - Product Requirements Document

## Original Problem Statement
Build "Semantic Vision," an educational platform — "Learning How to Read increases your vocabulary, which is VISION to your MIND." Multi-role system (Parent/School, Teacher, Student, Admin, Brand Partner), wallet/payment system, brand sponsorship model, and self-service brand partner portal.

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

### Core Platform
- Multi-role platform (Admin, Guardian, Teacher, Student, Brand Partner)
- AI story generation with brand integration, belief-system awareness, cultural context
- 60/30/10 vocabulary tier system
- WebSocket-based live classroom sessions

### Admin Portal
- Stats, Word Banks (CRUD + category filter + edit), AI Costs, Brands, Users, Coupons
- Contests (create/edit/pause/delete), Plans, Billing/ROI, Features, LLM Config, Settings
- **Plan Management:** Create, edit (name, price, seats, active/inactive toggle), delete subscription plans
- **User Subscription Assignment:** Admin can assign any subscription plan to any guardian user

### Parent (Guardian) Portal
- Students, Marketplace, **Subscription Tab**, Wallet, Invite & Earn (leaderboard + contests), Progress
- **Subscription Tab:** View current plan, see all available plans, upgrade (pay with wallet), redeem coupons/invitation codes

### Subscription System
- Plans: Free, Starter, Family, Academy (admin-configurable)
- Parents can upgrade plans using wallet balance (with discount support)
- Admin can assign plans directly to users
- Coupon/invitation code redemption for credits, free stories, free seats, discounts

### Other Features
- Word Bank Compliance: Parent banks forced private, admin oversight, created_by_role tracking
- Currency: Auto-detect via IP, 50+ countries, live exchange rates
- Rebrand: LexiMaster -> Semantic Vision (all 20 locales)
- Referral Contest System with live leaderboard
- Technical Specifications Document for provisional patent

### Landing Page (Redesigned)
- Premium dark theme with gold/teal accents, Sora + Plus Jakarta Sans fonts
- Sections: Hero, Stats, Philosophy, How It Works, Brand Integration, Cultural Awareness, 60/30/10 System, Role Cards, CTA, Footer
- Framer Motion scroll animations, AI-generated illustrations
- "20+ languages" callout badge in hero section

### Bug Fixes
- Language dropdown text invisible (white on white) — fixed with explicit text-black
- Missing SubscriptionFeatures import — fixed
- Login loop bug — resolved (backend NameError)
- Toggle button state — resolved (Pydantic model)

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Guardian: allen@ourfamily.contact / LexiAdmin2026!

## Key API Endpoints (Subscription)
- `GET /api/subscription-plans/available` — Public, returns active plans
- `POST /api/subscriptions/upgrade` — Parent upgrades plan (wallet payment)
- `PUT /api/admin/plans/{plan_id}` — Admin edits plan
- `POST /api/admin/users/{user_id}/assign-subscription` — Admin assigns plan to user

## Backlog
- [ ] P0: Refactor server.py into modular routers
- [ ] P1: Animated product demo on landing page
- [ ] P1: Payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] P1: AI word content moderation
- [ ] P2: Student gamification, accessibility, COPPA/FERPA
- [ ] P2: User Demo Flow for presentations
- [ ] P2: Accessibility features (text-to-sign-language for deaf users)
- [ ] P2: Granular admin analytics dashboard
- [ ] P3: Extract AdminPortal.jsx tabs into dedicated components
