# Semantic Vision - Product Requirements Document

## Original Problem Statement
Build "Semantic Vision," an educational platform — "Learning How to Read increases your vocabulary, which is VISION to your MIND." Multi-role system (Parent/School, Teacher, Student, Admin, Brand Partner), wallet/payment system, brand sponsorship model, and self-service brand partner portal.

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async), JWT Auth
- **Frontend:** React 18, Tailwind CSS, Shadcn/UI, React Router, React Query
- **AI:** OpenAI GPT-5.2 (Emergent LLM Key)
- **Payments:** Stripe | **Email:** Resend | **Currency:** Open Exchange Rates API, ip-api.com
- **i18n:** react-i18next (20 languages)

## Implemented Features

### Core Platform
- AI story generation with brand integration, belief-system awareness, strengths/weaknesses personalization
- Student Profile: strengths/weaknesses, interests, virtues, belief system, cultural context
- Subscription: Free plan auto-create, parent upgrade, coupons, admin plan management
- Admin: Plan stats, user search, plan CRUD, wallet editing, contests, word banks, brands
- Landing Page: Fully i18n, premium dark theme, Brand CTA button
- Progress Tracking: Vocabulary Mastered, Agentic Reach Score, reading stats — all working

### Global Dark Theme (March 8, 2026)
- Consistent dark theme across ALL pages via AppShell + sv-dark CSS
- Semantic Vision logo (Eye icon) on every page
- NarrativeReader eye-friendly warm reading color
- Admin route protection (role-based)
- Brand portal requires brand_partner or admin role

### Brand Portal Story Integrations (March 8, 2026)
- **Story Integrations tab** with 3 sections:
  1. **Brand In Stories**: Real story excerpts where brand/products appear in chapter text
  2. **Brand Activation Questions**: Questions asked to students about brand content, with pass/fail data
  3. **Student Activation Responses**: Free-text responses from students
- **Summary Stats**: Stories Featuring Brand, Brand Mentions, Activation Questions, Question Attempts, Pass Rate
- **3-layer narrative search**: brand_placements field, brand_impressions, full-text content search
- **Backend**: Narratives store brand_placements, written answers saved to written_answers collection

### Provisional Patent & IP Strategy (March 8-9, 2026)
- **Provisional Patent Application** — 30 claims (5 independent + 25 dependent/expanded)
  - Original 15 claims covering core platform innovations
  - 15 expanded claims covering: RTB for AI content, A/B testing, therapeutic narratives, corporate training, Brand Comprehension Rate metric, dynamic pricing, cross-platform delivery, multilingual brand content, federated analytics, brand safety scoring, brand marketplace, QA system, guardian dashboard, predictive analytics, attribution modeling
- **Strategic Patent Analysis** — 6 independent inventions identified, 12+ industries mapped ($1.5T+ TAM)
- **Filing Cost Roadmap** — 3 scenarios (US Only $13-24K, Recommended $36-74K, Maximum $68-137K)
- All documents served as PDFs with CONFIDENTIAL watermarks and timestamps
- API endpoints: `/api/patent-document/pdf`, `/api/patent-strategy/pdf`, `/api/patent-filing-roadmap/pdf`

## Bug Fixes
- P0: Vocabulary Mastered/Agentic Reach Score ZERO -> normalized mastered_tokens to plain strings
- Fixed 6 stuck in_progress assessments
- Fixed brand impression narrative_id (was "pending")

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Student SJ: STU-DR40V7 / 914027

## Backlog
- [ ] P1: Complete end-to-end flow (parent signup -> student reads -> brand activation -> progress -> brand portal)
- [ ] P1: Finalize Coupon & Credit System
- [ ] P1: Refactor server.py (~5000 lines) into modular APIRouter
- [ ] P1: Payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] P2: Brand Engagement Score metric
- [ ] P2: Translate remaining locales
- [ ] P2: Student gamification, COPPA/FERPA
- [ ] P2: User Demo Flow
- [ ] P3: Extract AdminPortal.jsx into component modules
