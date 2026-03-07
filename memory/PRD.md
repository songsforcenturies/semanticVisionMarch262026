# LexiMaster - Product Requirements Document

## Problem Statement
Build "LexiMaster," a high-quality educational platform for students, guardians, and teachers focusing on vocabulary building and character education through AI-generated stories.

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async driver) + JWT auth
- **Frontend:** React 18 + Tailwind CSS + Shadcn/UI + React Query + Neo-Brutalist design
- **AI:** OpenAI via Emergent LLM Key for story/assessment generation
- **Auth:** JWT for guardians, code+PIN for students (no JWT)

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

## DB Schema
- **User:** {id, email, hashed_password, full_name, role}
- **Student:** {id, guardian_id, full_name, student_code, access_pin, age, grade_level, interests, virtues, assigned_banks, mastered_tokens, status}
- **WordBank:** {id, name, description, category, words (baseline/target/stretch), price, owner_id}
- **Narrative:** {id, student_id, title, chapters, bank_ids, status}
- **Assessment:** {id, student_id, narrative_id, questions, score, status}

## Key API Endpoints
- POST /api/auth/register, /api/auth/login (guardian)
- POST /api/auth/student-login (student code+PIN)
- CRUD /api/students
- GET /api/word-banks, POST /api/word-banks/purchase
- POST /api/narratives (AI story gen)
- POST /api/assessments (AI assessment gen)

## Bug Fixes
- **2026-03-07:** Fixed student login failure — existing students missing student_code field and had 6-digit PINs. Added startup migration + relaxed PIN validation.

## Feature Additions
- **2026-03-07:** Reset PIN — Guardians can regenerate a student's PIN from the dashboard. New endpoint `POST /api/students/{id}/reset-pin`. Button on student card in guardian portal.
- **2026-03-07:** Student Progress Dashboard — Guardians can view detailed progress for each student including reading stats, vocabulary mastery (pie chart), assessment history (bar chart), story history, assigned word banks, and character education virtues. New endpoint `GET /api/students/{id}/progress`. Uses recharts for data visualizations.

## Backlog
- Refactor monolithic server.py into modular route/model/service files
- No outstanding feature requests
