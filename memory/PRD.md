# Semantic Vision - Product Requirements Document (PRD)

## Original Problem Statement
AI-powered personalized educational narrative platform with brand integration, digital media, recording enforcement, support system, and comprehensive admin tools.

## Tech Stack
- **Frontend:** React 18, Tailwind CSS, Shadcn/UI, react-i18next
- **Backend:** Python FastAPI, Motor (async MongoDB)
- **Database:** MongoDB
- **AI:** OpenAI GPT-5.2 (via Emergent LLM Key), OpenAI Whisper
- **Payments:** Stripe, PayPal | **Email:** Resend | **Screen Share:** Daily.co
- **Media:** Server audio/video uploads, YouTube streaming

## What's Been Implemented (as of March 2026)

### Core Platform
- Full auth system (JWT, role-based, code/PIN for students)
- AI story generation with 10+ personalization dimensions + media embedding
- Brand integration with competitive bidding + media analytics
- 60/30/10 vocabulary distribution, Whisper transcription, diction scoring
- Audio Memory Library, Peer Audio Books, Spelling Bee, Task Reminders
- PWA, Wallet/Payments (Stripe + PayPal), Multi-currency, Affiliate system

### Admin Features (20 tabs)
- Statistics, Word Banks, Brands, Users, Coupons, Contests, Plans, Features
- AI Costs, Billing/ROI, Affiliates, Audio Books, Messaging, Spelling Bee
- LLM Config, Integrations, Screen Share, **Digital Media**, **Support Tickets**, App Settings
- User management, Delegated admin, Impersonation, Direct messaging by email

### Recording Enforcement System (NEW)
- **Compliance modal**: Blocks story text (blurred) until recording starts
- **Mode enforcement**: ReadAloudRecorder locks to parent-required mode (audio/video/both)
- **Clear instructions**: Modal explains requirements before story access
- **Chapter-by-chapter**: Recording resets each chapter, auto-saves progress

### Digital Media System
- Admin: Upload audio, YouTube URLs, pricing, master toggle, brand linking
- Story integration: AI embeds brand media as inline players
- Student: "My Music" library, like/download (wallet-deducted)
- Parent: Per-student media ON/OFF, children's media history

### Storage Management (NEW)
- **Admin settings**: Max storage per user (MB), max recording duration (sec), auto-delete after (days)
- **Storage dashboard**: Real-time breakdown by category (Total, Recordings, Media, Support Files)
- **Endpoint**: GET /api/admin/storage-stats

### User Support System
- **Support Widget**: Floating button on all authenticated pages
- Users send: text, screenshots (auto-capture), audio recordings, file attachments
- Admin: Reply (auto-notifies user), manage ticket status (open/in_progress/replied/resolved/closed)
- Status filters, attachment viewer, conversation thread

### Story Progress System
- Auto-save on chapter change, Save & Exit button
- Stories only marked "completed" after ALL chapters read + assessment done
- Compliance modal enforces recording before story access

### Security
- Assessment cheating prevention: Fully opaque overlay
- Admin messaging: Dark text on white background (CSS specificity fix)

### Guardian Features
- Student management, PIN changes, ID cards, heritage/culture multi-select
- Music & Media tab, Culture learning preferences
- Per-student recording mode and media controls

## Prioritized Backlog

### P0 - ALL COMPLETED
- [x] All previous P0 items including digital media, support tickets, storage management
- [x] Recording enforcement with compliance modal — iteration 51
- [x] Storage settings + dashboard — iteration 51
- [x] Messaging contrast fix — iteration 51

### P1 (High)
- [ ] Real-time world events in stories — Admin configures headlines, AI weaves into stories, parents can toggle
- [ ] Dual Role (Parent/Student) Toggle — Users 15+ switch views
- [ ] Story randomization — Vary interests to avoid repetitive stories

### P2 (Medium)
- [ ] "Wheel of the World" Game — Interactive globe on student dashboard
- [ ] Dynamic Music Generation
- [ ] On-Device LLM Integration

### P3 (Low/Future)
- [ ] Video Recording & Analysis, User Demo Flow
- [ ] Accessibility Features, AR, Gamification, Family Narratives

## Key Credentials
- **Admin/Guardian:** allen@songsforcenturies.com / LexiAdmin2026!

## Key Backend Files
- `/app/backend/routes/media.py` — Digital media + storage stats
- `/app/backend/routes/support.py` — Support tickets + attachments
- `/app/backend/routes/admin.py` — Impersonation, integrations, messaging
- `/app/backend/routes/narratives.py` — Story generation, progress save, completion logic
- `/app/backend/routes/brands.py` — Brand management, media analytics
- `/app/backend/story_service.py` — AI prompt with media integration
