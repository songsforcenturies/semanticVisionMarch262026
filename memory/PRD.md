# Semantic Vision - Product Requirements Document (PRD)

## Original Problem Statement
Build a comprehensive AI-powered personalized educational narrative platform ("Semantic Vision") with:
- AI-generated stories personalized across 10+ dimensions
- Brand integration with comprehension measurement
- Multi-role platform (Admin, Guardian, Teacher, Student, Brand, Affiliate)
- Digital media (music/video) integration in stories
- PWA architecture with offline caching

## Tech Stack
- **Frontend:** React 18, Tailwind CSS, Shadcn/UI, react-i18next
- **Backend:** Python FastAPI, Motor (async MongoDB)
- **Database:** MongoDB
- **AI:** OpenAI GPT-5.2 (via Emergent LLM Key), OpenAI Whisper
- **Payments:** Stripe, PayPal
- **Email:** Resend
- **PDF:** ReportLab
- **Screen Share:** Daily.co (API key configured)
- **Media:** Server-side audio uploads, YouTube video streaming

## What's Been Implemented (as of March 2026)

### Core Platform
- Full authentication system (JWT, role-based, code/PIN for students)
- AI story generation with 10+ personalization dimensions
- Brand integration engine with competitive bidding
- Brand Comprehension measurement and analytics
- 60/30/10 vocabulary distribution with mastery tracking
- Read-aloud recording with Whisper transcription and diction scoring
- Audio Memory Library and Peer Audio Book Section
- Parental control system with recording enforcement
- Admin messaging (direct to user by email + broadcast)
- Clickable notification messages with full detail view
- Spelling bee contest engine with leaderboard
- Task reminder system
- PWA architecture (service worker, manifest, offline caching)
- Affiliate referral system
- Wallet/payment system (Stripe + PayPal)
- Multi-currency support (50+)
- Student progress export (HTML/JSON)

### Admin Features
- 19-tab admin dashboard
- User management with delegated admin access
- Admin impersonation ("View as User") - WORKING
- Screen share/remote support (Daily.co) - LIVE
- Cost/income/ROI analytics with family-level breakdown
- API key management (Stripe, PayPal, Resend, Daily.co)
- Direct messaging to specific users by email
- **Digital Media Management** - Upload audio/video, add YouTube links, set per-item pricing, master ON/OFF toggle, link media to brands
- Subscription plan management, Word bank CRUD, Coupon system, Feature flags

### Digital Media System (NEW)
- **Admin Controls**: Upload audio files, paste YouTube video URLs, set price per stream/download, master system toggle, link media to brands
- **Story Integration**: AI stories embed approved brand media as inline players ([MEDIA:id:title] tags)
- **Student Library**: "My Music" section with all heard songs/videos, like button, download option (wallet-deducted)
- **Parent Controls**: Per-student media ON/OFF toggle, view children's media history and likes
- **Pricing**: Admin sets global stream/download prices, per-item override available

### Guardian Features
- Student management with PIN changes
- Downloadable user/student ID cards
- Multi-select heritage/culture with custom write-in
- Culture learning preferences (16 topics)
- **Music & Media tab** - See children's media, toggle per student
- Tab order: Students, Word Bank, Audio Memories, Audio Books, Music & Media, Progress, ID Cards, Invite & Earn, Subscription, Wallet, Offers, Affiliate, FAQ

### Security Fix
- **Assessment cheating prevention**: Fully opaque overlay (bg-black) on WrittenAnswerModal and VisionCheckModal so students cannot read story text during assessments

## Prioritized Backlog

### P0 (Critical) - ALL COMPLETED
- [x] All P0 items from previous sessions - COMPLETED
- [x] Digital Media system (admin, student, parent, story integration) - COMPLETED (iteration 49)
- [x] Assessment cheating fix - COMPLETED

### P1 (High)
- [ ] Dual Role (Parent/Student) Toggle - Users 15+ can switch between parent and student views
- [ ] Story randomization - Vary interest/culture/theme selection to avoid repetitive stories
- [ ] On-Device LLM Integration

### P2 (Medium)
- [ ] "Wheel of the World" Game - Interactive spinning globe on student dashboard
- [ ] Dynamic Music Generation - Replace MusicPlayer placeholder
- [ ] Video Recording & Analysis
- [ ] User Demo Flow

### P3 (Low/Future)
- [ ] Accessibility Features - Text-to-sign-language AI
- [ ] AR Story Experience, Gamification, Family Shared Narratives
- [ ] AI-Generated Illustrations per chapter

## Key Credentials
- **Admin/Guardian:** allen@songsforcenturies.com / LexiAdmin2026!

## 3rd Party Integrations
- OpenAI GPT (Emergent LLM Key), OpenAI Whisper (Emergent LLM Key)
- Stripe, PayPal, Resend (User API Keys)
- Daily.co (API key configured)
- reportlab, html2canvas

## Key Backend Files
- `/app/backend/routes/media.py` - Digital media CRUD, streaming, student library, guardian endpoints
- `/app/backend/routes/admin.py` - Impersonation, support, integrations
- `/app/backend/routes/narratives.py` - Story generation with media embedding
- `/app/backend/story_service.py` - AI prompt with media integration
