# Semantic Vision - Product Requirements Document

## Original Problem Statement
Semantic Vision is an AI-powered personalized reading platform for families. It generates stories that teach vocabulary, reflect cultural values, and weave real brands as problem-solving heroes. The platform includes portals for Parents/Guardians, Students, Teachers, Brands, Admins, and Affiliates.

## Core Architecture
- **Frontend:** React 18 (with i18n, react-query, framer-motion, Shadcn UI)
- **Backend:** FastAPI (Python) with MongoDB
- **Integrations:** OpenAI GPT-5.2 (via Emergent LLM Key), Stripe (payments), Resend (email), reportlab (PDFs)
- **Auth:** JWT-based with role-based access

## What's Been Implemented

### Completed Features
- Onboarding Wizards (Brand, Guardian, Student), Unified Auth, FAQ Sections
- Brand Competition System with bidding/rotation, 34 real US brands seeded
- Affiliate & Coupon System with user-facing dashboard in Guardian Portal
- "Patent-Pending AI Technology" badge on landing page
- Clear affiliate login instructions on signup success page

### Patent Filing v4.0 FINAL (March 10, 2026)
- **42 claims** (8 independent + 34 dependent)
- **Brand Comprehension** as named core innovation with dedicated independent claim
- **Claim 7**: Broader claim covering replacement of static educational content with AI-generated personalized narratives
- 11 actual UI screenshots as exhibits (FIGS. 1-11)
- Complete data model schemas, API reference, competitive landscape
- Files: `/api/patent-filing-2026/pdf`, `/api/patent-filing-2026/md`, `/api/patent-filing-2026/bundle` (ZIP with all files + screenshots)

## Credentials
- Admin/Guardian: `allen@songsforcenturies.com` / `LexiAdmin2026!`

## Prioritized Backlog

### P1 - Technical Debt
- [ ] Refactor `server.py` into modular FastAPI APIRouters

### P2 - Payment Integrations
- [ ] Cash App, Zelle, Venmo, PayPal

### P3 - Future Features
- [ ] User Demo Flow
- [ ] Accessibility Features (sign language AI)
- [ ] Granular Admin Analytics
- [ ] Affiliate Earnings Notifications
