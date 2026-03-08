# Semantic Vision - Product Requirements Document

## Original Problem Statement
Build "Semantic Vision," an educational platform — "Learning How to Read increases your vocabulary, which is VISION to your MIND." Multi-role system (Parent/School, Teacher, Student, Admin, Brand Partner), wallet/payment system, brand sponsorship model, and self-service brand partner portal.

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async), JWT Auth, WebSockets
- **Frontend:** React 18, Tailwind CSS, Shadcn/UI, React Router, React Query, Framer Motion
- **AI:** OpenAI GPT-5.2 (Emergent LLM Key)
- **Payments:** Stripe | **Email:** Resend | **Currency:** Open Exchange Rates API, ip-api.com
- **i18n:** react-i18next (20 languages) — landing page fully translated

## Implemented Features

### Core: AI story generation with brand integration, belief-system & cultural awareness, strengths/weaknesses personalization, 60/30/10 vocabulary tiers
### Student Profile: Free-text strengths/weaknesses, interests, virtues, belief system, cultural context, language
### Subscription: Auto-create free plan, parent upgrade via wallet, coupon redemption, admin plan management & per-user subscription/wallet editing
### Admin: Plan stats, user search, plan CRUD with edit/active toggle, user subscription & wallet editing, contests, word banks, brands
### Landing Page: Fully i18n-translated (all text uses t() keys), premium dark theme, sections for brand integration, cultural awareness, strengths/weaknesses, 60/30/10, role cards
### Patent: 5 claims in TECHNICAL_SPECIFICATIONS.md including strengths-aware narrative generation

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Guardian: allen@ourfamily.contact / LexiAdmin2026!

## Backlog
- [ ] P0: Refactor server.py into modular routers
- [ ] P1: Translate remaining 18 locales for new landing page keys
- [ ] P1: Animated product demo on landing page
- [ ] P1: Payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] P2: Student gamification, accessibility, COPPA/FERPA
- [ ] P2: User Demo Flow, Growth Report feature
- [ ] P3: Extract AdminPortal.jsx tabs into dedicated components
