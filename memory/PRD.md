# LexiMaster - Product Requirements Document

## Problem Statement
Build "LexiMaster," an educational platform for students, guardians, and teachers focusing on vocabulary building and character education through AI-generated stories.

## Architecture
- **Backend:** FastAPI + MongoDB + JWT + WebSockets + Stripe
- **Frontend:** React 18 + Tailwind CSS + Shadcn/UI + React Query + Recharts
- **AI:** Emergent LLM Key + OpenRouter (configurable) for story/assessment/evaluation
- **Auth:** JWT for guardians & teachers, code+PIN for students
- **Real-time:** WebSocket for live classroom session updates
- **Payments:** Stripe (via emergentintegrations) for wallet top-ups

## Core Features
- **Phase 1-5:** Auth, Student Management, Word Bank Marketplace, AI Story Generation, Vocabulary Assessment
- **Written Answer Evaluation:** Students type answers, AI evaluates correctness
- **Auto-Timer:** Starts automatically when student opens story, cannot be stopped
- **Spelling System:** Exact vs Phonetic mode (per student + system-wide), spellcheck disable, error tracking
- **Teacher Portal:** Classroom sessions, join codes, real-time roster (WebSocket), analytics
- **Admin Dashboard:** Cost tracking, LLM config (Emergent/OpenRouter), app settings, comprehensive statistics
- **Wallet & Payments:** Stripe checkout for wallet top-ups, wallet balance for word bank purchases
- **Coupon System:** Digital coupons for wallet credits, free stories, free students, free premium days
- **Admin Delegation:** Master admin can delegate word bank creation and subscription management
- **Subscription Plans:** Admin-defined plans with custom pricing, seats, and story limits
- **Export:** JSON + printable HTML progress reports

## DB Schema
- User (+ wallet_balance, is_delegated_admin)
- Student (+ spellcheck_disabled, spelling_mode)
- WordBank, Narrative, Assessment
- ClassroomSession, CostLog, SpellingLog, SystemConfig
- WalletTransaction, PaymentTransaction
- Coupon, CouponRedemption
- AdminSubscriptionPlan

## Key API Endpoints
- Auth: register, login, student-login
- Students: CRUD, reset-pin, spellcheck, spelling-mode, spelling-logs, progress, export
- Word Banks: CRUD, purchase
- Narratives: generate (AI)
- Assessments: generate, evaluate, evaluate-written (AI)
- Classroom: CRUD sessions, join, start/end, analytics
- Admin: costs, models, settings, stats, users, delegate, coupons, plans, word-banks
- Wallet: balance, packages, topup, transactions, purchase-bank
- Coupons: redeem
- Payments: status/{session_id}
- Webhook: /api/webhook/stripe
- WebSocket: /ws/session/{id}

## Completed Features
- [x] JWT Authentication for all roles
- [x] Student Management (CRUD, PIN reset)
- [x] Word Bank Marketplace
- [x] AI Story Generation (Emergent + OpenRouter)
- [x] Written Answer Assessment with AI Evaluation
- [x] Automated Reading Timer
- [x] Guardian Spelling Controls
- [x] Teacher Portal & Live Classroom Sessions
- [x] Admin Cost Tracking & LLM Configuration
- [x] Admin App Settings (spelling, free limits)
- [x] Progress Dashboard & Reports
- [x] Wallet System (balance, top-up packages)
- [x] Stripe Payment Integration (checkout sessions)
- [x] Digital Coupon System (4 types)
- [x] Admin Delegation System
- [x] Subscription Plans Management
- [x] Comprehensive Admin Statistics Dashboard
- [x] Admin User Management

## Backlog
- Refactor monolithic server.py into modular routers
- PayPal integration as additional payment method
- CashApp Pay integration
- Student Gamification System (XP, badges, leaderboard)
- Government/school compliance review (COPPA, FERPA)
- Automated billing/recurring subscriptions
