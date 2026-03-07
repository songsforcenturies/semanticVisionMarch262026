# LexiMaster - Product Requirements Document

## Problem Statement
Build "LexiMaster," an educational platform for students, guardians, and teachers focusing on vocabulary building and character education through AI-generated stories. The platform must meet government/school standards, support multi-lingual content, religious/cultural personalization, and robust payment/billing infrastructure.

## Architecture
- **Backend:** FastAPI + MongoDB + JWT + WebSockets + Stripe (via emergentintegrations)
- **Frontend:** React 18 + Tailwind CSS + Shadcn/UI + React Query + Recharts
- **AI:** Emergent LLM Key + OpenRouter (configurable) for story/assessment/word definitions
- **Auth:** JWT for guardians, teachers, admins; code+PIN for students
- **Real-time:** WebSocket for live classroom sessions
- **Payments:** Stripe for wallet top-ups and donations

## User Roles
- **Master Admin** (allen@songsforcenturies.com): Full system control, delegation, billing, feature flags
- **Delegated Admin**: Can create/edit word banks and manage subscriptions (granted by master admin)
- **Guardian**: Manages students, purchases word banks, sets preferences
- **Teacher**: Creates classroom sessions, views analytics
- **Student**: Reads stories, takes assessments

## Completed Features
- [x] JWT Authentication for all roles
- [x] Student Management (CRUD, PIN reset)
- [x] Word Bank Marketplace with wallet-based purchases
- [x] AI Story Generation (Emergent + OpenRouter) with belief/culture/language params
- [x] Written Answer Assessment with AI Evaluation
- [x] Automated Reading Timer
- [x] Guardian Spelling Controls (phonetic vs exact)
- [x] Teacher Portal & Live Classroom Sessions (WebSocket)
- [x] Admin Cost Tracking & LLM Configuration
- [x] Admin App Settings (spelling, free limits)
- [x] Progress Dashboard & Export Reports
- [x] Wallet System (balance, top-up packages via Stripe)
- [x] Digital Coupon System (4 types: wallet_credit, free_stories, free_students, free_days)
- [x] Admin Delegation System (grant/revoke admin privileges)
- [x] Subscription Plans Management
- [x] Comprehensive Admin Statistics Dashboard
- [x] Referral System (invite & earn $5 for both parties)
- [x] Click-to-Define Words (AI-powered dictionary in story reader)
- [x] Religious/Belief System Preferences (20+ denominations)
- [x] Cultural Context Settings (13 cultural backgrounds)
- [x] Multi-Language Support (20 world languages for story generation)
- [x] Admin Billing/ROI Configuration (per-seat, markup, flat-fee models)
- [x] Admin Feature Flags (system-wide feature toggles)
- [x] Sponsor a Reader Donation System (Stripe checkout)
- [x] Master Admin auto-promotion on startup

## Key API Endpoints
- Auth: register (with referral), login, student-login
- Students: CRUD, reset-pin, spellcheck, spelling-mode, progress, export
- Word Banks: CRUD, purchase (wallet-based)
- Narratives: generate (AI with belief/culture/language)
- Assessments: generate, evaluate, evaluate-written (AI)
- Words: POST /api/words/define (AI dictionary)
- Classroom: CRUD sessions, join, start/end, analytics, WebSocket
- Wallet: balance, packages, topup, transactions, purchase-bank
- Referrals: my-code, my-referrals
- Coupons: redeem
- Donations: create, status, stats
- Payments: status/{session_id}
- Admin: costs, models, settings, stats, users, delegate, coupons, plans, billing-config, feature-flags, word-banks
- Webhook: POST /api/webhook/stripe

## DB Collections
users, students, subscriptions, word_banks, narratives, assessments, read_logs, cost_logs, spelling_logs, system_config, classroom_sessions, wallet_transactions, payment_transactions, coupons, coupon_redemptions, subscription_plans, referrals, donations

## Backlog (P2/P3)
- [ ] Refactor monolithic server.py into modular routers
- [ ] PayPal integration as additional payment method
- [ ] CashApp Pay integration
- [ ] Student Gamification System (XP, badges, leaderboard)
- [ ] Government/school compliance review (COPPA, FERPA)
- [ ] Automated recurring subscription billing
- [ ] Accessibility enhancements for deaf/HoH users (visual-first design, captions)
- [ ] Full multi-lingual UI (currently stories only; UI remains English)
- [ ] Regional feature delegation (per-region feature flags)
