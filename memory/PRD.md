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
- ReadAloudRecorder component (audio + video modes) - positioned AT TOP of each chapter
- Diction Analysis via OpenAI Whisper: transcription, text comparison, 4-dimensional scoring
- Audio Memory Library tab in Guardian Portal with student filter buttons
- Audio Book Collection: public page at /audio-books
- Admin Audio Books management: approve/reject submissions

### Patent Filing v6.0 (81 Claims)
- Download: /api/patent-filing/v6/zip

### Mobile Responsiveness & PWA (March 10, 2026)
- Mobile-responsive design across all pages (tested at 375px, 768px, 1920px)
- AppShell with hamburger menu on mobile
- Guardian Portal with horizontally scrollable tabs
- NarrativeReader fully responsive with compact header
- All modals fit mobile without horizontal overflow
- PWA manifest.json + Service Worker registered

### Offline Story Caching (March 10, 2026)
- IndexedDB-based offline storage (offlineCache.js)
- SaveOfflineButton integrated in NarrativeReader header
- OfflineLibrary section accessible from StudentAcademy

### Ambient Background Music (March 10, 2026)
- MusicPlayerWidget in NarrativeReader header
- Web Audio API with 8 mood-based ambient sounds
- Auto-mood detection from story text

### Font/Text Visibility Fixes (March 10, 2026)
- BrutalCard: inline styles for backgroundColor + color (prevents dark theme inheritance)
- PIN input: type=text, inputMode=numeric, white text with gold border, 1.5rem font
- Student code boxes: explicit dark-indigo text (#1e1b4b) on indigo-100 bg
- PIN display boxes: explicit dark-brown text (#78350f) on yellow-100 bg
- Audio Memories filter buttons: text-gray-900 on gray-100 bg
- Global CSS rule: .sv-dark .bg-white/.bg-gray-50/.bg-gray-100 { color: #111827 }

## Key API Endpoints
- POST /api/recordings/upload
- POST /api/recordings/{id}/analyze
- GET /api/recordings/guardian/all
- GET /api/audio-books
- GET/PUT /api/admin/audio-books/settings

## Credentials
- Admin/Guardian: allen@songsforcenturies.com / LexiAdmin2026!
- Test Student: STU-DR40V7 / PIN: 914027

## Prioritized Backlog

### P0 (User Requested - Next)
- [ ] Parent Control System: mandatory read-aloud/video per child, chapter thresholds
- [ ] Video recording at top of story with auto-start/confirm (parent-controlled)
- [ ] Task reminder messages for children to complete readings
- [ ] Remember Me / save credentials with opt-in
- [ ] Push notifications for parents when child completes audio

### P1
- [ ] Server-side audio diction analysis with comparison over time
- [ ] Audio Memories background upload
- [ ] On-Device LLM for offline story generation
- [ ] Refactor server.py into modular FastAPI routers (6000+ lines)

### P2
- [ ] Payment gateways (Cash App, Zelle, Venmo, PayPal)
- [ ] Video Recording & Analysis enhancements
- [ ] Dynamic Music Generation synced with audiobook energy
- [ ] Accessibility Features (text-to-sign-language AI)
- [ ] User Demo Flow
- [ ] Granular Admin Analytics
