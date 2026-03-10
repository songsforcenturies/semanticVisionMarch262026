# Semantic Vision - Product Requirements Document

## Original Problem Statement
Semantic Vision is an AI-powered personalized reading platform for families. It generates stories that teach vocabulary, reflect cultural values, and weave real brands as problem-solving heroes. The platform includes portals for Parents/Guardians, Students, Teachers, Brands, and Admins.

## Core Architecture
- **Frontend:** React (with i18n, react-query, framer-motion, Shadcn UI)
- **Backend:** FastAPI (Python) with MongoDB
- **Integrations:** OpenAI GPT (via Emergent LLM Key), Stripe (payments), Resend (email), reportlab (PDFs)
- **Auth:** JWT-based with role-based access (parent, student, teacher, brand_partner, admin)

## What's Been Implemented

### Completed Features
- **Onboarding Wizards:** Reusable `OnboardingWizard.jsx` for Brand, Guardian, and Student portals (skippable, resettable)
- **Unified Auth:** `UnifiedLogin.jsx` and `UnifiedRegister.jsx` consolidating all login/register flows
- **FAQ Sections:** Dedicated FAQ tabs in all user portals via shared `faqContent.js`
- **Brand Competition System:** Bidding/rotation model for brand placement in stories. 34 real US brands seeded.
- **Affiliate & Coupon System:** Public affiliate signup (`/affiliate`), admin management, wallet credit coupons (end-to-end verified)
- **IP Documentation:** Provisional patent application, user manual, strategic analysis (MD + watermarked PDF)
- **Landing Page:** Multi-language support (20+ languages), brand showcase, affiliate link

### P0 Fixes (Completed - March 2026)
- **Patent-Pending Text:** Changed "PATENTED AI TECHNOLOGY" to "PATENT-PENDING AI TECHNOLOGY" across all locale files (en.json, es.json)
- **Affiliate Login Flow:** 
  - Added clear instructions on AffiliateSignup success page directing users to Parent/Guardian Portal → Affiliate tab
  - Created `AffiliateTab.jsx` component in Guardian Portal showing affiliate dashboard (code, link, stats, referral history)
  - Updated success page button to "Login to Parent Portal"

## Key Database Collections
- `users`, `students`, `brands`, `brand_offers`, `stories`
- `affiliates`, `affiliate_referrals`
- `wallets`, `wallet_transactions`, `coupons`
- `referral_codes`, `referrals`, `referral_contests`
- `system_config`

## Credentials
- Admin/Guardian: `allen@songsforcenturies.com` / `LexiAdmin2026!`

## Prioritized Backlog

### P1 - Technical Debt
- [ ] **Refactor `server.py`** - Break monolithic 5800+ line file into modular FastAPI APIRouters (auth, stories, brands, affiliates, admin, etc.)

### P1 - Feature Updates
- [ ] **Update IP Documents** - Regenerate patent application and user manual with latest features (brand bidding, affiliate portal)

### P2 - Payment Integrations
- [ ] **Additional Payment Gateways** - Cash App, Zelle, Venmo, PayPal

### P3 - Future Features
- [ ] **User Demo Flow** - Streamlined demo mode or test scenarios
- [ ] **Accessibility Features** - Text-to-sign-language AI for deaf users
- [ ] **Granular Admin Analytics** - Expanded admin stats dashboard
