# LexiMaster - Product Requirements Document

## Problem Statement
Build "LexiMaster," a high-quality educational platform for students, guardians, and teachers focusing on vocabulary building and character education through AI-generated stories.

## Architecture
- **Backend:** FastAPI + MongoDB (Motor async driver) + JWT auth + WebSockets
- **Frontend:** React 18 + Tailwind CSS + Shadcn/UI + React Query + Recharts + Neo-Brutalist design
- **AI:** Emergent LLM Key (OpenAI) + OpenRouter (configurable) for story/assessment generation
- **Auth:** JWT for guardians & teachers, code+PIN for students
- **Real-time:** WebSocket for live classroom session updates

## Core Features (All Phases Complete)
- **Phase 1:** Foundation & Auth (guardian email/password, student code+PIN)
- **Phase 2:** Student Management (CRUD, virtues/character education)
- **Phase 3:** Word Bank Marketplace (purchase, assign to students)
- **Phase 4:** AI Story Generation (OpenAI-powered narratives with vocabulary)
- **Phase 5:** Vocabulary Assessment (AI-driven post-reading quizzes)

## Additional Features
- Global header with home navigation
- Student 2FA: unique student_code + PIN
- Character Education: virtues woven into AI stories
- Reset PIN: guardians regenerate student PINs
- Student Progress Dashboard: charts, stats, story history, export
- Export Student Data: JSON + printable HTML
- Teacher Portal: classroom sessions, join codes, analytics
- Student Session Join: enter teacher's 6-digit code
- Admin Dashboard: cost tracking per story/user, LLM provider config
- WebSocket real-time roster updates for classroom sessions
- OpenRouter integration for free/cheap LLM models

## DB Schema
- **User:** {id, email, hashed_password, full_name, role}
- **Student:** {id, guardian_id, full_name, student_code, access_pin, age, grade_level, interests, virtues, assigned_banks, mastered_tokens, status}
- **WordBank:** {id, name, description, category, words, price, owner_id}
- **Narrative:** {id, student_id, title, chapters, bank_ids, status}
- **Assessment:** {id, student_id, narrative_id, questions, score, status}
- **ClassroomSession:** {id, teacher_id, title, session_code, status, participating_students, bank_ids}
- **CostLog:** {id, student_id, user_id, model, provider, tokens, estimated_cost, duration, success}
- **SystemConfig:** {key, value} (stores LLM provider config)

## Key API Endpoints
- POST /api/auth/register, /api/auth/login
- POST /api/auth/student-login
- CRUD /api/students, POST /api/students/{id}/reset-pin
- GET /api/students/{id}/progress, GET /api/students/{id}/export
- GET /api/word-banks, POST /api/word-banks/purchase
- POST /api/narratives, POST /api/assessments
- POST/GET /api/classroom-sessions, POST /api/classroom-sessions/join
- POST /api/classroom-sessions/{id}/start|end
- GET /api/classroom-sessions/{id}/analytics
- GET /api/admin/costs, GET/POST /api/admin/models
- WS /ws/session/{id}

## Bug Fixes
- **2026-03-07:** Fixed student login (missing student_code + PIN length)
- **2026-03-07:** Fixed story generation (missing virtues parameter)
- **2026-03-07:** Fixed story dialog (scrollable + sticky buttons)
- **2026-03-07:** Fixed Motor DB truth testing (`if self.db:` → `if self.db is not None:`)
- **2026-03-07:** Fixed OpenRouter integration (updated free model list, added fallback routing, lenient JSON parsing for AI responses, timeout/retry limits)

## Feature Additions
- **2026-03-07:** Reset PIN, Progress Dashboard, Export, Teacher Portal, Session Join, Admin Dashboard, WebSocket, OpenRouter support

## Backlog
- Refactor monolithic server.py into modular files
- Add balance to Emergent LLM Universal Key to enable story generation
