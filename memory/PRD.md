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

### Brand Portal Story Integrations (March 8, 2026)
- Story Integrations tab with real story excerpts, activation questions, student responses
- 3-layer narrative search, brand placements on narratives

### Provisional Patent & IP Strategy (March 8-9, 2026)
- 30-claim Provisional Patent Application (5 independent + 25 expanded)
- Strategic Patent Analysis (6 inventions, 12+ industries, $1.5T+ TAM)
- Filing Cost Roadmap (3 scenarios: $13K-$137K)
- All served as CONFIDENTIAL PDFs with watermarks

### Student Setup Wizard (March 9, 2026)
- Replaced scrolling form with 5-step wizard: Basic Info > Virtues > Strengths & Growth > Faith & Culture > Word Banks
- Virtues section: 16 selectable virtues with descriptions
- Strengths/Weaknesses: Fixed font visibility (white text on dark bg)
- Dark-themed inputs throughout with proper text contrast

### Affiliate Link System (March 9, 2026)
- Public affiliate signup: POST /api/affiliates/signup (auto-generates AFF-XXXXXX codes)
- Automated confirmation email via Resend with affiliate link
- Referral tracking: AFF- codes handled during user registration at /api/auth/register
- Earnings: Flat fee, percentage, or wallet credits (admin-configurable)
- Admin portal: Affiliates tab with settings management, approve/deactivate, payout recording
- Affiliate stats endpoint for logged-in affiliates

### Brand Offers System (March 9, 2026)
- Brands create offers (free + paid) with external links or platform promo codes
- Target all users or specific users
- Parent portal: "Offers" tab with toggle to turn off all offers
- Offer dismissal, click tracking, view counting
- CRUD endpoints: /api/brands/offers, /api/offers, /api/offers/preferences

### Age-Appropriate Vocabulary (March 9, 2026)
- Grade-level complexity guide added to AI story generation prompt
- 16 grade levels (pre-K through adult) with specific language complexity instructions
- Brand Comprehension questions + surrounding narrative matches grade level

### Landing Page Religion Fix (March 9, 2026)
- Removed specific religion mentions, replaced with generalized faith/cultural references

### Brand Target Market (March 9, 2026)
- Brands with empty target_ages default to ALL markets

### First-Login Onboarding Wizards (March 9, 2026)
- Reusable OnboardingWizard component with step indicators, skip/next/back navigation
- Guardian Portal: 5-step wizard (Welcome, Student Setup, Subscription, Marketplace, Progress)
- Brand Portal: 5-step wizard (Welcome, Campaigns, Story Integrations, Offers, Analytics)
- Student Academy: 4-step wizard (Welcome, Read Stories, Answer Questions, Growth Tracking)
- Uses localStorage tracking (sv_onboarding_{portalType}_{userId}) — wizard only shows once per user
- Dark theme with gold accents, blurred backdrop overlay, animated transitions
- Fully tested: all portals, all steps, skip/dismiss/persistence verified

## Bug Fixes
- P0: Vocabulary Mastered/Agentic Reach Score ZERO -> normalized mastered_tokens
- Fixed strengths/weaknesses font visibility (dark theme input styling)

## Credentials
- Admin: allen@songsforcenturies.com / LexiAdmin2026!
- Student SJ: STU-DR40V7 / 914027

## Backlog
- [ ] P1: Finalize Coupon & Credit System end-to-end verification
- [ ] P1: Refactor server.py (~5600 lines) into modular APIRouter
- [ ] P2: Payment gateway integrations (Cash App, Zelle, Venmo, PayPal)
- [ ] P2: Brand Engagement Score metric
- [ ] P2: Translate remaining i18n locales
- [ ] P2: Student gamification, COPPA/FERPA compliance
- [ ] P2: User Demo Flow for presentations
- [ ] P3: Extract AdminPortal.jsx into component modules
