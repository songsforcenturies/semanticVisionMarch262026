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
- **ReadAloudRecorder** component in student NarrativeReader (audio + video modes)
- **Diction Analysis** via OpenAI Whisper: transcription, text comparison, 4-dimensional scoring
- **Audio Memory Library** tab in Guardian Portal
- **Audio Book Collection**: public page at `/audio-books`
- **Admin Audio Books** management: approve/reject submissions
- **19 backend endpoints** for recordings, audio books, admin controls

### Patent Filing v6.0 (81 Claims)
- Filed with all audio/video/device/lifelong features claimed
- Download: `/api/patent-filing/v6/zip`

### Mobile Responsiveness & PWA (March 10, 2026)
- **Mobile-responsive design** across all pages (tested at 375px, 768px, 1920px)
- **AppShell** with hamburger menu on mobile, responsive header
- **Guardian Portal** with horizontally scrollable tabs on mobile
- **NarrativeReader** fully responsive with compact header controls
- **Modals** (OnboardingWizard, WrittenAnswerModal, StoryGenerationDialog) fit mobile without horizontal overflow
- **PWA manifest.json** with standalone display mode
- **Service Worker** registered for offline caching
- **PIN input fix**: Visible digits with large monospace font (type=text, inputMode=numeric)

### Offline Story Caching (March 10, 2026)
- **IndexedDB-based** offline storage (`offlineCache.js`)
- **SaveOfflineButton** integrated in NarrativeReader header (compact mode)
- **OfflineLibrary** section accessible from StudentAcademy via "Offline" button
- **Service Worker** for PWA caching at `/service-worker.js`
- Dark theme styling consistent with app

### Ambient Background Music (March 10, 2026)
- **MusicPlayerWidget** integrated in NarrativeReader header
- **Web Audio API** generates mood-based ambient sounds (8 moods: adventurous, calm, mysterious, joyful, emotional, exciting, peaceful, inspiring)
- Auto-mood detection from story text content
- Volume control and mood selector

### Dark Theme Consistency (March 10, 2026)
- ReadAloudRecorder, SaveOfflineButton, MusicPlayerWidget, OfflineLibrary all updated to dark theme (#1A2236 card, #F8F5EE cream text)

## Key API Endpoints
- `POST /api/recordings/upload` - Upload recording (multipart)
- `POST /api/recordings/{id}/analyze` - Whisper transcription + diction scoring
- `GET /api/recordings/guardian/all` - All recordings for guardian's students
- `GET /api/recordings/student/{id}/progress` - Diction improvement over time
- `GET /api/audio-books` - Public audio book collection
- `POST /api/audio-books/contribute` - Share recording to collection
- `GET/PUT /api/admin/audio-books/settings` - Admin controls

## Credentials
- Admin/Guardian: `allen@songsforcenturies.com` / `LexiAdmin2026!`
- Test Student: `STU-DR40V7` / PIN: `914027`

## Prioritized Backlog

### P0 (User Requested - Next)
- [ ] Parent Control System: mandatory read-aloud/video, chapter thresholds, settings in parent portal
- [ ] Video recording at top of story with auto-start/confirm (parent-controlled)
- [ ] Task reminder messages for children to complete audiobook readings
- [ ] Remember Me / save credentials with opt-in

### P1
- [ ] Server-side audio diction analysis with comparison over time
- [ ] Audio Memories background upload improvements
- [ ] On-Device LLM for offline story generation
- [ ] Refactor server.py into modular FastAPI routers (6000+ lines)

### P2
- [ ] Payment gateways (Cash App, Zelle, Venmo, PayPal)
- [ ] Video Recording & Analysis enhancements
- [ ] Dynamic Music Generation synced with audiobook energy
- [ ] Accessibility Features (text-to-sign-language AI)
- [ ] User Demo Flow
- [ ] Granular Admin Analytics
