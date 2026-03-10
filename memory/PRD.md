# Semantic Vision - Product Requirements Document

## Original Problem Statement
Semantic Vision is an AI-powered personalized reading platform replacing static educational materials with infinite, AI-generated, culturally-aware, faith-aligned, brand-funded narratives spanning Pre-K through College.

## What's Been Implemented

### Core Features (Previously Built)
- Onboarding Wizards, Unified Auth, FAQ Sections
- Brand Competition System (bidding/rotation, 34 brands)
- Affiliate & Coupon System with user-facing dashboard
- Patent-Pending badge, clear affiliate login instructions

### Read-Aloud Recording & Audio System
- ReadAloudRecorder at TOP of each chapter (audio + video modes)
- Diction Analysis via OpenAI Whisper: transcription + 4D scoring
- Audio Memory Library, Audio Book Collection, Admin moderation

### Patent Filing v6.0 (81 Claims)

### Mobile Responsiveness & PWA (March 10, 2026)
- Fully responsive across 375px/768px/1920px
- AppShell hamburger menu, scrollable tabs, no horizontal overflow
- PWA manifest.json + Service Worker

### Offline Story Caching + Ambient Music (March 10, 2026)
- IndexedDB offline storage, SaveOfflineButton, OfflineLibrary
- MusicPlayerWidget with 8 moods via Web Audio API

### Font/Text Visibility Fixes (March 10, 2026)
- BrutalCard: inline styles for bg + text color
- PIN input: bright white text, gold accent, 1.5rem font
- Student codes, PINs, Audio Memories filter buttons all visible
- Global CSS rule for light-bg elements in dark theme

### Admin Messaging System (March 10, 2026)
- Admin creates messages targeted to: Everyone, Parents, Students, Teachers
- Priority levels: Low, Normal, High, Urgent
- NotificationBell in AppShell header with unread count badge
- Click-to-mark-read notification panel dropdown
- Both guardian and student portals receive notifications
- Backend: POST/GET/DELETE /api/admin/messages, GET /api/notifications

### Spelling Bee Contests (March 10, 2026)
- Admin creates contests: title, word list (comma-separated), time limit, dates
- Admin can pause/activate/delete contests, view leaderboard
- Students see active contests, start timed challenge, submit answers
- Scoring: case-insensitive comparison, results with correct/incorrect per word
- Leaderboard ranked by score then time
- Backend: Full CRUD + submit + leaderboard endpoints

### Expanded Virtues & Emotions (March 10, 2026)
- 32 Character Virtues (patience, kindness, honesty, courage, etc.)
- 30 Emotional Intelligence options (joy, love, hope, sadness, anger, etc.)
- Unlimited selection (no cap), search filter, custom virtue input
- Search across both categories

## Key API Endpoints
- POST/GET/DELETE /api/admin/messages - Admin messaging CRUD
- GET /api/notifications - User notifications with unread count
- POST /api/admin/spelling-contests - Create spelling contest
- GET /api/spelling-contests - List active contests
- POST /api/spelling-contests/submit - Submit contest answers
- GET /api/spelling-contests/{id}/leaderboard - Contest leaderboard

## Credentials
- Admin/Guardian: allen@songsforcenturies.com / LexiAdmin2026!
- Test Student: STU-DR40V7 / PIN: 914027

## Prioritized Backlog

### P0 (User Requested - Next)
- [ ] Parent Control System: mandatory read-aloud/video, chapter thresholds, blocking
- [ ] Video recording at top of story with auto-start/confirm (parent-controlled)
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
- [ ] Accessibility Features (text-to-sign-language AI)
- [ ] Granular Admin Analytics
