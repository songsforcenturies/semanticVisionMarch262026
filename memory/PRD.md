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
- AI story generation with brand integration, belief-system awareness, strengths/weaknesses personalization, 60/30/10 vocabulary tiers
- Student Profile: strengths/weaknesses, interests, virtues, belief system, cultural context
- Subscription: Free plan auto-create, parent upgrade, coupons, admin plan management
- Admin: Plan stats, user search, plan CRUD, wallet editing, contests, word banks, brands
- Landing Page: Fully i18n-translated, premium dark theme, Brand CTA button
- Progress Tracking: Vocabulary Mastered, Agentic Reach Score, reading stats — all working

### Global Dark Theme (March 8, 2026)
- Consistent #0A0F1E dark theme across ALL pages
- AppShell component with Semantic Vision logo (Eye icon) on every page
- sv-dark CSS overrides for brutal components
- NarrativeReader warm reading color (#E8E0D0) for eye comfort
- Admin route protection (role-based allowedRoles)
- Brand portal requires brand_partner or admin role
- Child-friendly brand image (replaced cigarette-looking one)

### Brand Portal Story Integrations (March 8, 2026)
- **Story Integrations tab**: Shows actual story excerpts where brand products appear, highlighted in context
- **Student Activation Responses**: Shows student written answers to comprehension questions about brand stories
- **Summary stats**: Stories Featuring Brand, Brand Mentions, Student Responses, Avg Comprehension
- **Backend**: Narratives now store brand_placements, written answers saved to written_answers collection
- **API**: /api/brand-portal/story-integrations works for both brand_partner and admin roles

### Login/Register UX (March 8, 2026)
- "Access Your Portal" section on login and register pages
- Three clear pathways: Parents (gold), Brands (pink), Students (teal) with icons
- Brand Partner registration via /register?role=brand_partner

## Bug Fixes
- **P0 FIXED**: Vocabulary Mastered/Agentic Reach Score showing ZERO → normalized mastered_tokens to plain strings
- Fixed 6 stuck in_progress assessments
- Fixed brand impression narrative_id (was "pending", now uses real narrative ID)

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Student SJ: STU-DR40V7 / 914027

## Backlog
- [ ] P1: Complete end-to-end flow (parent signup → student reads → brand activation → progress → brand portal)
- [ ] P1: Finalize Coupon & Credit System end-to-end
- [ ] P1: Refactor server.py (~5000 lines) into modular APIRouter
- [ ] P1: Payment integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] P2: Translate remaining locales
- [ ] P2: Student gamification, accessibility, COPPA/FERPA
- [ ] P2: User Demo Flow
- [ ] P3: Extract AdminPortal.jsx into component modules
