# LexiMaster - Product Requirements Document

## Problem Statement
Build "LexiMaster," a high-quality educational platform for students, guardians, and teachers focusing on vocabulary building and character education through AI-generated stories.

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async driver) + JWT auth
- **Frontend:** React 18 + Tailwind CSS + Shadcn/UI + React Query + Neo-Brutalist design + Recharts
- **AI:** OpenAI via Emergent LLM Key for story/assessment generation
- **Auth:** JWT for guardians & teachers, code+PIN for students (no JWT)

## Core Features (All Phases Complete)
- **Phase 1:** Foundation & Auth (guardian email/password, student code+PIN)
- **Phase 2:** Student Management (CRUD, virtues/character education)
- **Phase 3:** Word Bank Marketplace (purchase, assign to students)
- **Phase 4:** AI Story Generation (OpenAI-powered narratives with vocabulary)
- **Phase 5:** Vocabulary Assessment (AI-driven post-reading quizzes)

## Additional Features
- Global header with home navigation on all pages
- Student 2FA: unique student_code + PIN
- Character Education: guardians add virtues woven into AI stories
- Startup migration: auto-assigns student_codes to legacy students
- Reset PIN: guardians regenerate student PINs
- Student Progress Dashboard: reading stats, vocabulary mastery charts, assessment history, story history
- Export Student Data: JSON download + printable HTML report
- Teacher Portal: classroom sessions, student join codes, class analytics/leaderboard

## DB Schema
- **User:** {id, email, hashed_password, full_name, role (guardian|teacher|admin)}
- **Student:** {id, guardian_id, full_name, student_code, access_pin, age, grade_level, interests, virtues, assigned_banks, mastered_tokens, status}
- **WordBank:** {id, name, description, category, words (baseline/target/stretch), price, owner_id}
- **Narrative:** {id, student_id, title, chapters, bank_ids, status}
- **Assessment:** {id, student_id, narrative_id, questions, score, status}
- **ClassroomSession:** {id, teacher_id, title, session_code, status, participating_students, bank_ids}

## Key API Endpoints
- POST /api/auth/register, /api/auth/login (guardian & teacher)
- POST /api/auth/student-login (student code+PIN)
- CRUD /api/students, POST /api/students/{id}/reset-pin
- GET /api/students/{id}/progress, GET /api/students/{id}/export
- GET /api/word-banks, POST /api/word-banks/purchase
- POST /api/narratives (AI story gen)
- POST /api/assessments (AI assessment gen)
- POST/GET /api/classroom-sessions, POST /api/classroom-sessions/join
- POST /api/classroom-sessions/{id}/start|end
- GET /api/classroom-sessions/{id}/analytics

## Bug Fixes
- **2026-03-07:** Fixed student login failure — existing students missing student_code field and had 6-digit PINs. Added startup migration + relaxed PIN validation.

## Feature Additions
- **2026-03-07:** Reset PIN — Guardians can regenerate a student's PIN from the dashboard.
- **2026-03-07:** Student Progress Dashboard — reading stats, vocabulary mastery (pie chart), assessment history (bar chart), story history, word banks, virtues. Uses recharts.
- **2026-03-07:** Export Student Data — JSON download + printable HTML report with Print/Save as PDF.
- **2026-03-07:** Teacher Portal — register/login, classroom sessions with 6-digit join codes, session lifecycle management, class roster, class-wide analytics with leaderboard.

## Backlog
- Refactor monolithic server.py into modular route/model/service files
