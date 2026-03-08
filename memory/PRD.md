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

### Core Platform
- AI story generation with brand integration, belief-system & cultural awareness, strengths/weaknesses personalization, 60/30/10 vocabulary tiers
- Student Profile: Free-text strengths/weaknesses, interests, virtues, belief system, cultural context, language
- Subscription: Auto-create free plan, parent upgrade via wallet, coupon redemption, admin plan management
- Admin: Plan stats, user search, plan CRUD, user subscription/wallet editing, contests, word banks, brands
- Landing Page: Fully i18n-translated, premium dark theme, brand CTA button
- Patent: 5 claims in TECHNICAL_SPECIFICATIONS.md
- Progress Tracking: Vocabulary Mastered count, Agentic Reach Score, reading stats — all working

### Dark Theme (March 8, 2026)
- **Global dark theme** applied across ALL pages — landing, login, register, student-login, teacher-login, forgot-password, admin dashboard, parent portal, student academy, teacher portal, brand portal, donate page
- **AppShell component** provides consistent header with Semantic Vision logo (Eye icon + "Semantic Vision" text) on every page
- **sv-dark CSS class** overrides brutal component styles for dark backgrounds
- **NarrativeReader** uses eye-friendly warm reading color (#E8E0D0) on dark background
- **Admin route protection**: Only admin role users can access `/admin` (role-based `allowedRoles`)
- **Brand portal authentication**: Requires brand_partner or admin role
- **Brand CTA button** prominently placed on landing page
- **Child-friendly brand image** replaces previous image that looked like cigarettes

## Bug Fixes
- **P0 FIXED (March 8):** Vocabulary Mastered and Agentic Reach Score showing as ZERO. Root cause: Pydantic model `mastered_tokens` typed as `List[MasteredToken]` but narrative completion stored plain strings → 500 error. Fixed by normalizing to plain strings everywhere.
- Fixed 6 stuck `in_progress` assessments → marked as `failed` so users can retake.

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Student SJ: STU-DR40V7 / 914027

## Backlog
- [ ] P1: Complete end-to-end flow (parent signup → student reads story with brand solutions → brand questions → parent sees progress → brand portal sees snippets)
- [ ] P1: Finalize and verify Coupon & Credit System end-to-end
- [ ] P1: Refactor server.py into modular routers (APIRouter)
- [ ] P1: Payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] P2: Translate remaining locales for new landing page keys
- [ ] P2: Student gamification, accessibility, COPPA/FERPA
- [ ] P2: User Demo Flow, Growth Report feature
- [ ] P3: Extract AdminPortal.jsx tabs into dedicated components
