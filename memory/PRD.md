# Semantic Vision - Product Requirements Document

## Original Problem Statement
Semantic Vision is an AI-powered personalized reading platform replacing static educational materials with infinite, AI-generated, culturally-aware, faith-aligned, brand-funded narratives spanning Pre-K through College.

## What's Been Implemented (March 10, 2026)

### Core Features (Previously Built)
- Onboarding Wizards, Unified Auth, FAQ Sections
- Brand Competition System (bidding/rotation, 34 brands)
- Affiliate & Coupon System with user-facing dashboard
- Patent-Pending badge, clear affiliate login instructions

### Read-Aloud Recording & Audio System (NEW - March 10, 2026)
- **ReadAloudRecorder** component in student NarrativeReader (audio + video modes)
- **Diction Analysis** via OpenAI Whisper: transcription → text comparison → 4-dimensional scoring (pronunciation, fluency, completeness, prosody)
- **Audio Memory Library** tab in Guardian Portal: browse/play/delete all recordings, share to collection
- **Audio Book Collection**: public page at `/audio-books`, also embedded in Guardian Portal as tab
- **Admin Audio Books** management: approve/reject submissions, settings (enable/disable, auto-approve, show on landing)
- **Diction Progress Tracking**: longitudinal improvement across recording sessions
- **19 backend endpoints** for recordings, audio books, admin controls
- **Recording Storage**: `/app/backend/uploads/recordings/`

### Patent Filing v4.0 (75 Claims)
- Filed March 10, 2026 with all audio/video/device/lifelong features claimed
- Download: `/api/patent-filing-2026/bundle`

## Key API Endpoints (NEW)
- `POST /api/recordings/upload` - Upload recording (multipart)
- `POST /api/recordings/{id}/analyze` - Whisper transcription + diction scoring
- `GET /api/recordings/guardian/all` - All recordings for guardian's students
- `GET /api/recordings/student/{id}/progress` - Diction improvement over time
- `GET /api/audio-books` - Public audio book collection
- `POST /api/audio-books/contribute` - Share recording to collection
- `GET/PUT /api/admin/audio-books/settings` - Admin controls

## Credentials
- Admin/Guardian: `allen@songsforcenturies.com` / `LexiAdmin2026!`

## Prioritized Backlog
### P1
- [ ] Refactor server.py into modular FastAPI routers (now 6000+ lines)
### P2
- [ ] Payment gateways (Cash App, Zelle, Venmo, PayPal)
- [ ] AI-generated background music for audio books
### P3
- [ ] User Demo Flow, Accessibility, Admin Analytics
