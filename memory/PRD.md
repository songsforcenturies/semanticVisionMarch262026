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
  1. **Brand In Stories**: Real story excerpts where brand/products appear in chapter text, highlighted brand terms, mention counts
  2. **Brand Activation Questions**: Questions asked to students about brand content, with pass/fail data from read_logs (e.g., "What tool did SJ use to research how to make her car faster?" - 0 passed, 6 failed)
  3. **Student Activation Responses**: Free-text responses from students (written_answers collection, populated going forward)
- **Summary Stats**: Stories Featuring Brand (5), Brand Mentions (5), Activation Questions (5), Question Attempts (10), Pass Rate (0%)
- **3-layer narrative search**: brand_placements field → brand_impressions → full-text content search
- **Backend**: Narratives store brand_placements, written answers saved to written_answers collection, impressions use real narrative IDs

### Login/Register UX (March 8, 2026)
- "Access Your Portal" section: Parents (gold), Brands (pink), Students (teal) with icons

## Bug Fixes
- P0: Vocabulary Mastered/Agentic Reach Score ZERO → normalized mastered_tokens to plain strings
- Fixed 6 stuck in_progress assessments
- Fixed brand impression narrative_id (was "pending")

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Student SJ: STU-DR40V7 / 914027

## Backlog
- [ ] P1: Complete end-to-end flow (parent signup → student reads → brand activation → progress → brand portal)
- [ ] P1: Finalize Coupon & Credit System
- [ ] P1: Refactor server.py (~5000 lines) into modular APIRouter
- [ ] P1: Payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] P2: Brand Engagement Score metric
- [ ] P2: Translate remaining locales
- [ ] P2: Student gamification, COPPA/FERPA
- [ ] P2: User Demo Flow
- [ ] P3: Extract AdminPortal.jsx into component modules
