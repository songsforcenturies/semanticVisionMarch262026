# LexiMaster - Product Requirements Document

## Problem Statement
Build "LexiMaster," an educational platform for students, guardians, and teachers focusing on vocabulary building and character education through AI-generated stories. The platform supports multi-lingual content, religious/cultural personalization, brand sponsorship monetization, and robust payment/billing infrastructure.

## Architecture
- **Backend:** FastAPI + MongoDB + JWT + WebSockets + Stripe (via emergentintegrations)
- **Frontend:** React 18 + Tailwind CSS + Shadcn/UI + React Query + Recharts
- **AI:** Emergent LLM Key + OpenRouter (configurable) for story/assessment/word definitions
- **Auth:** JWT for guardians, teachers, admins; code+PIN for students
- **Payments:** Stripe for wallet top-ups and donations

## User Roles
- **Master Admin** (allen@songsforcenturies.com): Full system control
- **Delegated Admin**: Can create/edit word banks and manage subscriptions
- **Guardian**: Manages students, purchases word banks, sets preferences
- **Teacher**: Creates classroom sessions, views analytics
- **Student**: Reads stories, takes assessments

## Completed Features
- [x] JWT Authentication for all roles
- [x] Student Management (CRUD, PIN reset)
- [x] Word Bank Marketplace with wallet-based purchases
- [x] AI Story Generation with belief/culture/language/brand params
- [x] Written Answer Assessment with AI Evaluation
- [x] Automated Reading Timer
- [x] Guardian Spelling Controls
- [x] Teacher Portal & Live Classroom Sessions (WebSocket)
- [x] Admin Cost Tracking & LLM Configuration
- [x] Wallet System + Stripe Payments
- [x] Digital Coupon System (4 types)
- [x] Admin Delegation System
- [x] Subscription Plans Management
- [x] Comprehensive Admin Statistics Dashboard
- [x] Referral System (invite & earn)
- [x] Click-to-Define Words (AI dictionary)
- [x] Religious/Belief System Preferences (20+ denominations)
- [x] Cultural Context Settings (13 backgrounds)
- [x] Multi-Language Support (20 languages)
- [x] Admin Billing/ROI Configuration (3 pricing models)
- [x] Admin Feature Flags (9 toggles)
- [x] Sponsor a Reader Donation System
- [x] Brand Sponsorship System (admin CRUD, analytics, impressions)
- [x] Classroom Sponsorships (businesses sponsor schools)
- [x] Guardian Ad Preferences (opt-in/out per student)
- [x] Brand Integration in AI Stories (natural product placements)
- [x] Brand Analytics Dashboard (impressions, revenue, budget tracking)

## Key Collections
users, students, subscriptions, word_banks, narratives, assessments, read_logs, cost_logs, spelling_logs, system_config, classroom_sessions, wallet_transactions, payment_transactions, coupons, coupon_redemptions, subscription_plans, referrals, donations, brands, brand_impressions, classroom_sponsorships

## Backlog (P2/P3)
- [ ] Refactor monolithic server.py into modular routers
- [ ] PayPal/CashApp integration
- [ ] Student Gamification (XP, badges, leaderboard)
- [ ] COPPA/FERPA compliance review
- [ ] Automated recurring subscription billing
- [ ] Accessibility for deaf/HoH users
- [ ] Full multi-lingual UI (stories multilingual, UI English only)
- [ ] Regional feature delegation
