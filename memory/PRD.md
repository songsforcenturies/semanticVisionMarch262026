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

## Implemented Features

### Core Platform
- Multi-role platform (Admin, Guardian, Teacher, Student, Brand Partner)
- AI story generation with brand integration, belief-system awareness, cultural context
- 60/30/10 vocabulary tier system, WebSocket-based live classroom sessions

### Student Profile — Strengths & Weaknesses (NEW)
- Free-text `strengths` and `weaknesses` fields in student profile
- Parents describe what their child excels at and where they need growth
- AI prompt uses strengths as the character's "superpowers" — abilities celebrated and reinforced
- AI prompt models growth in weak areas through empathetic character development, never shame
- Combined with interests, beliefs, culture, virtues, vocabulary, and brand products — every story is truly one-of-a-kind
- New patent claim added: Claim 5 in TECHNICAL_SPECIFICATIONS.md

### Subscription System
- Auto-creates free subscription (10 seats) for guardians missing one
- Parents can upgrade plans using wallet balance, redeem coupons
- Admin: create/edit/delete plans, assign plans to users, edit user subscriptions & wallets

### Admin Portal
- Plan Membership Overview stats, user search by name/email
- Per-user controls: edit profile, wallet, subscription, plan assignment, reset password, activate/deactivate

### Landing Page
- Premium dark theme (midnight navy + gold/teal), Sora + Plus Jakarta Sans fonts
- NEW: "Truly Personalized" section — "Stories that know your child's superpowers and help them grow"
- Shows example AI story snippet demonstrating strengths/weaknesses in action
- "20+ languages" callout badge

### Technical Specifications
- `/app/memory/TECHNICAL_SPECIFICATIONS.md` — 5 patent claims including new Claim 5: Strengths-and-Weaknesses-Aware Personalized Narrative Generation

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Guardian: allen@ourfamily.contact / LexiAdmin2026!

## Backlog
- [ ] P0: Refactor server.py into modular routers
- [ ] P1: Animated product demo on landing page
- [ ] P1: Payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] P2: Student gamification, accessibility, COPPA/FERPA
- [ ] P2: User Demo Flow, Accessibility features
- [ ] P2: Granular admin analytics dashboard
- [ ] P3: Extract AdminPortal.jsx tabs into dedicated components
