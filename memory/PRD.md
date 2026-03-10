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
- Provisional patent filing with comprehensive documentation

## Tech Stack
- **Frontend:** React 18, Tailwind CSS, Shadcn/UI, react-i18next
- **Backend:** Python FastAPI, Motor (async MongoDB)
- **Database:** MongoDB
- **AI:** OpenAI GPT-5.2 (via Emergent LLM Key), OpenAI Whisper
- **Payments:** Stripe, PayPal
- **Email:** Resend
- **PDF:** ReportLab
- **Screen Share:** Daily.co (API key configured)

## What's Been Implemented (as of March 2026)

### Core Platform
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
- Wallet/payment system (Stripe + PayPal)
- Multi-currency support (50+)
- Guided onboarding framework
- Student progress export (HTML/JSON)
- Brand story preview system
- Full mobile-responsive UI with softer color theme

### Admin Features
- Comprehensive admin dashboard with 18 tabs
- User management (create, edit, deactivate, delete, reset password)
- Delegated admin access (grant/revoke)
- Cost/income/ROI analytics with family-level breakdown
- API key management (Stripe, PayPal, Resend, Daily.co)
- Admin impersonation ("View as User") - FIXED & WORKING
- Screen share/remote support (Daily.co) - LIVE with API key
- Subscription plan management
- Word bank CRUD
- Brand & sponsorship management
- Coupon system
- Feature flags
- Billing/ROI configuration
- Direct messaging to specific users by email (in-app + optional email delivery)
- Clickable notification messages with full detail view

### Guardian Features
- Student management with PIN changes
- Downloadable user/student ID cards with PINs
- Multi-select heritage/culture with custom write-in
- Culture learning preferences (16 topics influencing AI stories)
- Tab order: Students, Word Bank, Audio Memories, Audio Books, Progress, ID Cards, Invite & Earn, Subscription, Wallet, Offers, Affiliate, FAQ

## Prioritized Backlog

### P0 (Critical) - ALL COMPLETED
- [x] Admin Impersonation ("View as User") -- FIXED: JWT secret mismatch bug + 401 interceptor now restores admin session
- [x] Daily.co Screen Share -- COMPLETED & API key configured
- [x] Direct user messaging by email -- COMPLETED
- [x] Clickable notification messages -- COMPLETED
- [x] Student "Change My PIN" route fix -- COMPLETED

### P1 (High)
- [ ] Dual Role (Parent/Student) Toggle -- Users 15+ can switch between parent and student views
- [ ] On-Device LLM Integration -- WebLLM or similar for offline story generation

### P2 (Medium)
- [ ] "Wheel of the World" Game -- Interactive spinning globe on student dashboard
- [ ] Dynamic Music Generation -- Replace MusicPlayer placeholder
- [ ] Video Recording & Analysis
- [ ] User Demo Flow

### P3 (Low/Future)
- [ ] Accessibility Features -- Text-to-sign-language AI
- [ ] Granular Admin Analytics
- [ ] AR Story Experience
- [ ] Gamification & Achievement System
- [ ] Family Shared Narratives
- [ ] AI-Generated Illustrations per chapter

## Key Credentials
- **Admin/Guardian:** allen@songsforcenturies.com / LexiAdmin2026!

## 3rd Party Integrations
- **OpenAI GPT** (Text Generation) -- uses Emergent LLM Key
- **OpenAI Whisper** (Speech-to-Text) -- uses Emergent LLM Key
- **Stripe** (Payments) -- requires User API Key
- **PayPal** (Payments) -- requires User API Key
- **Resend** (Transactional Emails) -- requires User API Key
- **Daily.co** (Screen Sharing / Video) -- API key configured
- **reportlab** (Python library for PDF generation)
- **html2canvas** (JS library for image generation)
