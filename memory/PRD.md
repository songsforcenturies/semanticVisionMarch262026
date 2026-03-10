# Semantic Vision - Product Requirements Document

## Original Problem Statement
Semantic Vision is an AI-powered personalized reading platform replacing static educational materials with infinite, AI-generated, culturally-aware, faith-aligned, brand-funded narratives spanning Pre-K through College.

## What's Been Implemented

### Core Features (Previously Built)
- Onboarding Wizards, Unified Auth, FAQ Sections, Brand Competition, Affiliate & Coupon System

### Read-Aloud Recording & Audio System
- ReadAloudRecorder at TOP of each chapter (audio + video modes)
- Diction Analysis via OpenAI Whisper
- Audio Memories, Audio Book Collection, Admin moderation

### Parent Control System (March 10, 2026)
- **Reading Rules panel** per student in Guardian Portal (expandable section)
- **Recording modes**: Optional, Audio Required, Video Required, Both Required
- **Chapter threshold**: After N chapters, require recording (0 = every chapter)
- **Auto-start recording**: Recording auto-opens when chapter loads
- **Allow Skip**: Parent controls whether student can skip recording
- **NarrativeReader enforcement**: 
  - Purple banner: "Recording required by parent"
  - Yellow warning: "Complete recording before continuing"
  - Finish Chapter button disabled when recording not done + skip not allowed
- **Backend**: GET/PUT /api/students/{id}/parental-controls (GET is public for student portal, PUT requires auth)

### Admin Messaging System (March 10, 2026)
- Send messages to Everyone/Parents/Students/Teachers with priority levels
- NotificationBell in header with unread count badge
- Click-to-mark-read notification panel

### Spelling Bee Contests (March 10, 2026)
- Admin creates contests (word list, time limit, dates)
- Students participate with timer, hints, and auto-scoring
- Leaderboard ranked by score then time

### Expanded Virtues & Emotions (March 10, 2026)
- 32 Character Virtues + 30 Emotional Intelligence options
- Unlimited selection, search filter, custom input

### Softer Color Scheme (March 10, 2026)
- BrutalCards: warm beige (#f8f6f1) instead of pure white
- BrutalButtons: gentler colors with rounded corners
- BrutalBadges: softer pastel variants
- All borders softened from harsh black to black/20

### Mobile Responsiveness & PWA
- Fully responsive, PWA manifest + Service Worker, offline caching, ambient music

## Credentials
- Admin/Guardian: allen@songsforcenturies.com / LexiAdmin2026!
- Test Student: STU-DR40V7 / PIN: 914027

## Prioritized Backlog

### P0 (Next)
- [ ] Task reminder messages for children to complete readings
- [ ] Remember Me / save credentials with opt-in
- [ ] Push notifications for parents when child completes audio

### P1
- [ ] Server-side audio diction analysis with comparison over time
- [ ] On-Device LLM for offline story generation
- [ ] Refactor server.py into modular FastAPI routers (6000+ lines)

### P2
- [ ] Payment gateways (Cash App, Zelle, Venmo, PayPal)
- [ ] Video Recording & Analysis enhancements
- [ ] Dynamic Music Generation synced with audiobook energy
- [ ] Accessibility Features, Granular Admin Analytics
