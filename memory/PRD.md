# LexiMaster - Product Requirements Document

## Problem Statement
Build "LexiMaster," an educational platform for students, guardians, and teachers focusing on vocabulary building and character education through AI-generated stories.

## Architecture
- **Backend:** FastAPI + MongoDB + JWT + WebSockets
- **Frontend:** React 18 + Tailwind CSS + Shadcn/UI + React Query + Recharts
- **AI:** Emergent LLM Key + OpenRouter (configurable) for story/assessment/evaluation
- **Auth:** JWT for guardians & teachers, code+PIN for students
- **Real-time:** WebSocket for live classroom session updates

## Core Features
- **Phase 1-5:** Auth, Student Management, Word Bank Marketplace, AI Story Generation, Vocabulary Assessment
- **Written Answer Evaluation:** Students type answers (words/phrases/sentences), AI evaluates correctness
- **Auto-Timer:** Starts automatically when student opens story, cannot be stopped
- **Spelling System:** Exact vs Phonetic mode (per student + system-wide), spellcheck disable, error tracking
- **Teacher Portal:** Classroom sessions, join codes, real-time roster (WebSocket), analytics
- **Admin Dashboard:** Cost tracking, LLM config (Emergent/OpenRouter), app settings (spelling, free limits)
- **Export:** JSON + printable HTML progress reports

## DB Schema
- User, Student (+ spellcheck_disabled, spelling_mode), WordBank, Narrative, Assessment
- ClassroomSession, CostLog, SpellingLog, SystemConfig

## Key API Endpoints
- Auth: register, login, student-login
- Students: CRUD, reset-pin, spellcheck, spelling-mode, spelling-logs, progress, export
- Word Banks: CRUD, purchase
- Narratives: generate (AI)
- Assessments: generate, evaluate, evaluate-written (AI)
- Classroom: CRUD sessions, join, start/end, analytics
- Admin: costs, models, settings
- WebSocket: /ws/session/{id}

## Backlog
- **P3: Payment Integration** — Stripe (cards + Apple Pay + Google Pay + Cash App) + PayPal
- Refactor monolithic server.py
- Student Gamification System (XP, badges, leaderboard)
