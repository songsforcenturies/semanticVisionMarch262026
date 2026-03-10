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
- **Payments:** Stripe
- **Email:** Resend
- **PDF:** ReportLab

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
- Wallet/payment system (Stripe)
- Multi-currency support (50+)
- Guided onboarding framework
- Student progress export (HTML/JSON)
- Brand story preview system
- Full mobile-responsive UI with softer color theme

### Documentation Suite (Completed March 10, 2026)
- **DEFINITIVE Provisional Patent Application v6** -- 98 claims, 31 screenshots, 1,000 technical specifications
- **Master User Manual v6.0** -- 1,424-line comprehensive guide for all 6 user roles with:
  - Detailed step-by-step instructions for every feature
  - Benefits tied to patent claims for each stakeholder POV
  - 105 FAQ questions across all roles (25 Parent, 20 Student, 15 Teacher, 20 Brand, 10 Affiliate, 15 Admin)
  - Complete glossary of 30+ platform-specific terms

### Download Endpoints
- `/api/patent/definitive-pdf` -- Patent PDF
- `/api/patent/definitive-md` -- Patent Markdown
- `/api/patent/definitive-bundle` -- Complete ZIP (patent + specs + manual + 31 screenshots)
- `/api/user-manual/master-pdf` -- User Manual PDF
- `/api/user-manual/master-md` -- User Manual Markdown

## Prioritized Backlog

### P0 (Critical)
- [x] ~~Finalize Provisional Patent~~ -- COMPLETED (v6, 98 claims, 31 screenshots)
- [x] ~~Master User Manual~~ -- COMPLETED (6 roles, 105 FAQs, benefits tied to claims)
- [x] ~~Refactor `server.py`~~ -- COMPLETED (March 2026). Split into 10 modular route files in backend/routes/. 37/37 regression tests passed.

### Go-Live Preparation (Next)
- [x] ~~Integrate PayPal alongside Stripe~~ -- COMPLETED (March 2026). PayPal routes in backend/routes/paypal.py, frontend WalletTab updated with payment method toggle. Auto-enables when keys are set.
- [x] ~~Configure email sending from @semanticvision.ai domain (Resend)~~ -- COMPLETED. SENDER_EMAIL updated to hello@semanticvision.ai across services.py, auth.py, affiliates.py.
- [x] ~~Update CORS/domain config for semanticvision.ai~~ -- COMPLETED. CORS_ORIGINS includes semanticvision.ai and www.semanticvision.ai.

### User Action Items (Required for Go-Live)
- [ ] Add PayPal sandbox/production keys via Admin Dashboard > Integrations tab
- [ ] Verify Resend domain: Add DNS records (SPF, DKIM, MX) in Porkbun for semanticvision.ai
- [ ] Switch PayPal mode from Sandbox to Live when ready (via Integrations tab)

### P1 (High)
- [x] ~~Chunked auto-save recording~~ -- COMPLETED (March 2026). Auto-saves every 15s to sessionStorage.
- [x] ~~Parent notification on audio memory creation~~ -- COMPLETED. Notification sent to parent on upload.
- [x] ~~Clearer "Allow for Audio Books" button~~ -- COMPLETED. Text + icon label.
- [x] ~~User ID / Invitation Cards~~ -- COMPLETED. Downloadable PNG for guardians (referral code) and students (student code).
- [ ] On-Device LLM Integration -- WebLLM or similar for offline story generation

### P2 (Medium)
- [ ] Dynamic Music Generation -- Replace MusicPlayer placeholder with actual logic
- [ ] Video Recording & Analysis -- Extend recording to include video
- [ ] User Demo Flow -- Streamlined demo mode

### P3 (Low/Future)
- [ ] Accessibility Features -- Text-to-sign-language AI
- [ ] Granular Admin Analytics -- Expanded admin dashboard
- [ ] AR Story Experience
- [ ] Gamification & Achievement System
- [ ] Family Shared Narratives
- [ ] AI-Generated Illustrations per chapter

## Key Credentials
- **Admin/Guardian:** allen@songsforcenturies.com / LexiAdmin2026!
