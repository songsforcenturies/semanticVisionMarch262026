# Semantic Vision - Product Requirements Document (PRD)

## Original Problem Statement
AI-powered personalized educational narrative platform with brand integration, digital media, support system, and comprehensive admin tools.

## Tech Stack
- **Frontend:** React 18, Tailwind CSS, Shadcn/UI, react-i18next
- **Backend:** Python FastAPI, Motor (async MongoDB)
- **Database:** MongoDB
- **AI:** OpenAI GPT-5.2 (via Emergent LLM Key), OpenAI Whisper
- **Payments:** Stripe, PayPal | **Email:** Resend | **Screen Share:** Daily.co
- **Media:** Server audio uploads, YouTube video streaming

## What's Been Implemented (as of March 2026)

### Core Platform
- Full auth system (JWT, role-based, code/PIN for students)
- AI story generation with 10+ personalization dimensions + media embedding
- Brand integration engine with competitive bidding + media analytics
- Brand Comprehension measurement
- 60/30/10 vocabulary distribution with mastery tracking
- Read-aloud recording with Whisper transcription and diction scoring
- Audio Memory Library and Peer Audio Book Section
- Parental control system with recording enforcement
- Admin messaging (direct to user by email + broadcast) with visible contrast
- Clickable notification messages with full detail view
- Spelling bee contests, Task reminders, PWA architecture
- Affiliate referral, Wallet/payments (Stripe + PayPal), Multi-currency

### Admin Features (20 tabs)
- User management, Delegated admin, Impersonation ("View as User")
- Screen share (Daily.co), Cost/income/ROI analytics
- API key management, Subscription plans, Word bank, Brand management
- Digital Media Management (upload audio/video, YouTube links, pricing, master toggle)
- **Support Tickets** — View user-submitted tickets (text, screenshots, audio, video), reply to users (auto-notifies), set status (open/in_progress/replied/resolved/closed)
- Brand media analytics per brand partner

### Digital Media System
- Admin: Upload audio, paste YouTube URLs, set stream/download pricing, system toggle, brand linking
- Story integration: AI embeds brand media as inline players
- Student: "My Music" library, like/download (wallet-deducted)
- Parent: Per-student media ON/OFF, children's media history

### User Support System (NEW)
- **Support Widget**: Floating button on all authenticated pages
- Users can send: text messages, screenshots (auto-capture), audio recordings, video/file attachments
- Admin can reply (notification sent to user), manage ticket status
- Users can view reply history

### Story Progress System (NEW)
- **Auto-save**: Progress saved on every chapter change
- **Save & Exit**: Students can save and resume later
- **Completion fix**: Stories only marked "completed" after ALL chapters read + assessment done
- Students cannot close story and skip assessments

### Security
- Assessment cheating prevention: Fully opaque overlay on assessments

### Guardian Features
- Student management, PIN changes, ID cards
- Heritage/culture multi-select, Culture learning preferences
- **Music & Media tab** — children's media history + per-student toggle
- Tab order: Students, Word Bank, Audio Memories, Audio Books, Music & Media, Progress, ID Cards, Invite & Earn, Subscription, Wallet, Offers, Affiliate, FAQ

## Prioritized Backlog

### P0 - ALL COMPLETED
- [x] All previous P0 items
- [x] Digital Media system (admin, student, parent, story integration) — iteration 49
- [x] Assessment cheating fix — iteration 49
- [x] Admin messaging contrast fix — iteration 50
- [x] Story completion bug fix — iteration 50
- [x] Support ticket system — iteration 50
- [x] Story progress auto-save — iteration 50
- [x] Brand media analytics — iteration 50

### P1 (High)
- [ ] Real-time world events in stories — Admin configures headlines, AI weaves into stories, parents can toggle off
- [ ] Dual Role (Parent/Student) Toggle — Users 15+ switch views
- [ ] Story randomization — Vary interests to avoid repetitive stories

### P2 (Medium)
- [ ] "Wheel of the World" Game — Interactive globe on student dashboard
- [ ] Dynamic Music Generation
- [ ] On-Device LLM Integration

### P3 (Low/Future)
- [ ] Video Recording & Analysis
- [ ] User Demo Flow
- [ ] Accessibility Features (text-to-sign-language AI)
- [ ] AR Story Experience, Gamification, Family Shared Narratives

## Key Credentials
- **Admin/Guardian:** allen@songsforcenturies.com / LexiAdmin2026!

## Key Backend Files
- `/app/backend/routes/media.py` — Digital media CRUD, streaming, student library
- `/app/backend/routes/support.py` — Support tickets, attachments, admin replies
- `/app/backend/routes/admin.py` — Impersonation, integrations, messaging
- `/app/backend/routes/narratives.py` — Story generation, progress save/resume
- `/app/backend/routes/brands.py` — Brand management, media analytics
- `/app/backend/story_service.py` — AI prompt with media integration
