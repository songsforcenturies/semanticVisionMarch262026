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
- Progress Tracking: Vocabulary Mastered, Agentic Reach Score, reading stats

### Global Dark Theme (March 8, 2026)
- Consistent dark theme across ALL pages via AppShell + sv-dark CSS

### Brand Portal Story Integrations (March 8, 2026)
- Story Integrations tab with real story excerpts, activation questions, student responses

### Provisional Patent & IP Strategy (March 8-9, 2026)
- 30-claim Provisional Patent Application, Strategic Analysis, Filing Cost Roadmap as watermarked PDFs

### Student Setup Wizard (March 9, 2026)
- 5-step wizard replacing old scrolling form, fixed font visibility

### Affiliate Link System (March 9, 2026)
- Full CRUD, referral tracking, email confirmation, admin management

### Brand Offers System (March 9, 2026)
- Brands create offers pushed to parent portal, toggle on/off, click tracking

### Age-Appropriate Vocabulary (March 9, 2026)
- 16 grade levels in AI story generation prompt

### First-Login Onboarding Wizards (March 9, 2026)
- Guardian Portal: 5 steps | Brand Portal: 5 steps | Student Academy: 4 steps
- localStorage tracking, skip/next/back navigation, dark theme with gold accents

### Unified Login & Registration Pages (March 9, 2026)
- Single login page (/login) with role selector icons at top: Parents, Students, Teachers, Brands
- Clicking icon dynamically switches form: Parent/Teacher/Brand = email+password, Student = code+pin
- Single register page (/register) with role selector: Parents, Teachers, Brands (students don't self-register)
- Referral code field only shown for Parent role
- Old routes (/student-login, /teacher-login, /teacher-register) redirect seamlessly via query params

### FAQ Sections (March 9, 2026)
- Reusable FAQSection accordion component with expand/collapse + chevron animation
- Guardian Portal: 6 FAQ items (tab-based)
- Brand Portal: 6 FAQ items (tab-based)
- Student Academy: 5 FAQ items (toggle button)
- Teacher Portal: 5 FAQ items (tab-based)

### Reset Onboarding / Tutorial Button (March 9, 2026)
- "Tutorial" button in portal headers (Guardian, Brand, Student)
- Clears localStorage onboarding key and re-shows wizard via key-based remount

### Brand Competition & Bidding System (March 10, 2026)
- Brand bidding: higher bid_amount = higher rotation priority ($0.04-$0.15 range)
- Weighted rotation: brands grouped by problem_category, weighted random selection
- Multiple brands per story: up to 2 brands per problem category, 4 total per story
- Opt-out analytics: /api/brands/opt-out-analytics shows student/guardian opt-in rates
- Competition endpoint: /api/brands/competition/{category} shows competing brands
- 34 real US brands seeded across 13 categories (education_tech, sports_active, healthy_food, etc.)
- 12 real brand offers to parents (LeapFrog, Nike, LEGO, Audible, Gabb, etc.)

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
