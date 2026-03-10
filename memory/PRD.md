# Semantic Vision - Product Requirements Document

## Original Problem Statement
Semantic Vision is an AI-powered personalized reading platform for families. It generates stories that teach vocabulary, reflect cultural values, and weave real brands as problem-solving heroes. The platform includes portals for Parents/Guardians, Students, Teachers, Brands, Admins, and Affiliates.

## Core Architecture
- **Frontend:** React 18 (with i18n, react-query, framer-motion, Shadcn UI)
- **Backend:** FastAPI (Python) with MongoDB
- **Integrations:** OpenAI GPT-5.2 (via Emergent LLM Key), Stripe (payments), Resend (email), reportlab (PDFs)
- **Auth:** JWT-based with role-based access (parent, student, teacher, brand_partner, admin, affiliate)

## What's Been Implemented

### Completed Features
- **Onboarding Wizards:** Reusable `OnboardingWizard.jsx` for Brand, Guardian, Student portals (skippable, resettable)
- **Unified Auth:** `UnifiedLogin.jsx` and `UnifiedRegister.jsx` consolidating all login/register flows
- **FAQ Sections:** Dedicated FAQ tabs in all user portals via shared `faqContent.js`
- **Brand Competition System:** Bidding/rotation model for brand placement in stories. 34 real US brands seeded.
- **Affiliate & Coupon System:** Public affiliate signup, admin management, wallet credit coupons, user-facing affiliate dashboard in Guardian Portal
- **IP Documentation:** Provisional patent application v3.0, user manual, strategic analysis (MD + watermarked PDF)
- **Landing Page:** Multi-language support (20+ languages), "Patent-Pending AI Technology" badge

### P0 Fixes (Completed - March 10, 2026)
- Fixed "PATENTED" → "PATENT-PENDING AI TECHNOLOGY" across all locale files
- Created AffiliateTab.jsx in Guardian Portal with full affiliate dashboard
- Added clear login instructions on AffiliateSignup success page

### Patent Filing v3.0 (Completed - March 10, 2026)
- Strengthened from 30 claims → 38 claims (7 independent + 31 dependent)
- Added Competitive Brand Bidding Engine as new independent claim (Claim 4)
- Added user-facing Affiliate Dashboard as new independent claim detail (Claim 5)
- Added 10 new data model schemas in appendices (up from 7)
- Added API Endpoint Reference appendix (Appendix D)
- Expanded technical specifications throughout all sections
- Updated competitive landscape table with 7 new differentiating features
- Available at: `/api/patent-filing-2026/pdf` and `/api/patent-filing-2026/md`

## Credentials
- Admin/Guardian: `allen@songsforcenturies.com` / `LexiAdmin2026!`

## Prioritized Backlog

### P1 - Technical Debt
- [ ] **Refactor `server.py`** - Break 5800+ line monolithic file into modular FastAPI APIRouters

### P2 - Payment Integrations
- [ ] **Additional Payment Gateways** - Cash App, Zelle, Venmo, PayPal

### P3 - Future Features
- [ ] **User Demo Flow** - Streamlined demo mode
- [ ] **Accessibility Features** - Text-to-sign-language AI for deaf users
- [ ] **Granular Admin Analytics** - Expanded admin stats dashboard
- [ ] **Affiliate Earnings Notifications** - Email affiliates when they get new referrals
