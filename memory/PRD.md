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
- 60/30/10 vocabulary tier system, WebSocket-based live classroom sessions

### Subscription System (Complete)
- Auto-creates free subscription (10 seats) for guardians missing one
- Plans: Free, Starter, Family, Academy (admin-configurable)
- Parents can upgrade plans using wallet balance (with discount support)
- Parents can redeem coupons/invitation codes for credits, seats, stories, discounts
- Admin can assign plans directly to users
- Admin can directly edit user subscriptions (plan name, seats, status)
- Admin can directly set user wallet balance

### Admin Portal
- **Plan Membership Overview:** Stats card showing total parents, users with/without plans, students, breakdown by plan type
- **User Search:** Filter users by name or email in real-time
- **Per-User Controls:** Edit profile, edit wallet (set balance), assign plan from dropdown, edit subscription (plan/seats/status), reset password, activate/deactivate, delete
- **Plans Management:** Create, edit (name, price, seats, active toggle), delete subscription plans
- Stats, Word Banks (CRUD + category filter + edit), AI Costs, Brands, Coupons, Contests, Billing/ROI, Features, LLM Config, Settings

### Parent (Guardian) Portal
- Students, **Subscription Tab**, Marketplace, Wallet, Invite & Earn, Progress
- **Subscription Tab:** Current plan display, available plans with upgrade, coupon redemption

### Landing Page
- Premium dark theme (midnight navy + gold/teal), Sora + Plus Jakarta Sans fonts
- Sections: Hero, Stats, Philosophy, How It Works, Brand Integration, Cultural Awareness, 60/30/10 System, Role Cards, CTA, Footer
- Framer Motion scroll animations, AI-generated illustrations, "20+ languages" callout badge

### Technical Specifications Document
- Comprehensive patent-support document at `/app/memory/TECHNICAL_SPECIFICATIONS.md`

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Guardian: allen@ourfamily.contact / LexiAdmin2026!

## Key API Endpoints
- `GET /api/subscriptions/{guardian_id}` — Auto-creates free plan if missing
- `GET /api/subscription-plans/available` — Public, returns active plans
- `POST /api/subscriptions/upgrade` — Parent upgrades plan (wallet payment)
- `GET /api/admin/plan-stats` — User counts per plan type
- `GET /api/admin/users?search=term` — Search users by name/email
- `PUT /api/admin/plans/{plan_id}` — Admin edits plan
- `POST /api/admin/users/{user_id}/assign-subscription` — Assign plan from dropdown
- `PUT /api/admin/users/{user_id}/subscription` — Edit user subscription directly
- `PUT /api/admin/users/{user_id}/wallet` — Set user wallet balance

## Backlog
- [ ] P0: Refactor server.py into modular routers
- [ ] P1: Animated product demo on landing page
- [ ] P1: Payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] P2: Student gamification, accessibility, COPPA/FERPA
- [ ] P2: User Demo Flow, Accessibility features
- [ ] P2: Granular admin analytics dashboard
- [ ] P3: Extract AdminPortal.jsx tabs into dedicated components
