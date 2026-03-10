# Semantic Vision - Product Requirements Document (PRD)

## Original Problem Statement
Build a comprehensive AI-powered personalized educational narrative platform ("Semantic Vision") with:
- AI-generated stories personalized across 10+ dimensions (belief, culture, virtues, emotions, strengths, weaknesses, vocabulary, age, grade, language)
- Brand integration with comprehension measurement ("Brand Comprehension")
- Competitive brand bidding marketplace
- 60/30/10 three-tier vocabulary distribution
- Multi-role platform (Admin, Guardian, Teacher, Student, Brand, Affiliate)
- Parental controls with recording enforcement
- Admin messaging, spelling bees, task reminders
- PWA architecture with offline caching
- Provisional patent filing

## Core Requirements
1. **AI Content Generation** - GPT-5.2 powered multi-chapter narrative generation
2. **Brand Comprehension Pipeline** - Novel metric measuring cognitive brand engagement
3. **Vocabulary System** - 60/30/10 tier distribution with mastery tracking
4. **Multi-Role Architecture** - Six-tier RBAC with purpose-built portals
5. **Read-Aloud Recording** - Whisper-powered diction analysis and Audio Memory Library
6. **Parental Controls** - Recording enforcement with chapter-threshold gating
7. **Admin Tools** - Messaging, spelling bees, analytics
8. **PWA** - Service worker, offline caching, installability
9. **Patent Protection** - Comprehensive provisional patent application

## Tech Stack
- **Frontend:** React 18, Tailwind CSS, Shadcn/UI, react-i18next
- **Backend:** Python FastAPI, Motor (async MongoDB)
- **Database:** MongoDB
- **AI:** OpenAI GPT-5.2 (via Emergent LLM Key), OpenAI Whisper
- **Payments:** Stripe
- **Email:** Resend
- **PDF:** ReportLab

## What's Been Implemented (as of March 2026)
- Full authentication system (JWT, role-based, code/PIN for students)
- AI story generation with all personalization dimensions
- Brand integration engine with competitive bidding
- Brand Comprehension measurement and analytics
- 60/30/10 vocabulary distribution with mastery tracking
- Read-aloud recording with Whisper transcription and diction scoring
- Audio Memory Library and Peer Audio Book Section
- Parental control system with recording enforcement
- Admin messaging with notification bell
- Spelling bee contest engine with leaderboard
- Task reminder system
- PWA architecture (service worker, manifest, offline caching)
- Music player placeholder in narrative reader
- Affiliate referral system
- Wallet/payment system (Stripe)
- Multi-currency support (50+)
- Guided onboarding framework
- Student progress export (HTML/JSON)
- Brand story preview system
- Full mobile-responsive UI with softer color theme
- **DEFINITIVE Provisional Patent Application v6** - 98 claims + 1,000 technical specifications

## Prioritized Backlog

### P0 (Critical)
- [x] ~~Finalize Provisional Patent~~ - COMPLETED (v6 Definitive, 98 claims)
- [ ] Refactor `server.py` - Break monolithic file into FastAPI APIRouter modules

### P1 (High)
- [ ] On-Device LLM Integration - WebLLM or similar for offline story generation
- [ ] Payment Gateway Integrations - Cash App, Zelle, Venmo, PayPal

### P2 (Medium)
- [ ] Dynamic Music Generation - Replace MusicPlayer placeholder with actual logic
- [ ] Video Recording & Analysis - Extend recording to include video
- [ ] User Demo Flow - Streamlined demo mode

### P3 (Low/Future)
- [ ] Accessibility Features - Text-to-sign-language AI
- [ ] Granular Admin Analytics - Expanded admin dashboard
- [ ] AR Story Experience
- [ ] Gamification & Achievement System
- [ ] Family Shared Narratives
- [ ] Seasonal Content Adaptation
- [ ] AI-Generated Illustrations per chapter

## Key Credentials
- **Admin/Guardian:** allen@songsforcenturies.com / LexiAdmin2026!

## Patent Filing Status
- **Document:** PROVISIONAL_PATENT_DEFINITIVE_v6.md / .pdf
- **Claims:** 98 total (11 Independent + 60 Dependent + 14 Future + 13 Specialized)
- **Technical Specs:** 1,000 specifications (TECHNICAL_SPECIFICATIONS_1000.md)
- **Screenshots:** 11 figures (patent_screenshots/)
- **Bundle:** patent_filing_definitive_v6.zip (ready for download)
- **Download Endpoints:**
  - `/api/patent/definitive-pdf` - PDF document
  - `/api/patent/definitive-md` - Markdown source
  - `/api/patent/definitive-bundle` - Complete ZIP bundle with all exhibits
