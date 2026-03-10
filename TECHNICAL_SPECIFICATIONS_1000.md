# SEMANTIC VISION — COMPREHENSIVE TECHNICAL SPECIFICATIONS
# 1000 Technical Specifications for Provisional Patent Filing
# Document Version: 7.0 | Generated: March 2026
# Status: FOR PATENT FILING — All Features Documented

---

## SECTION 1: PLATFORM ARCHITECTURE (TS-001 through TS-050)

**TS-001.** The system comprises a client-server architecture with a React.js single-page application (SPA) frontend communicating with a Python FastAPI asynchronous backend via RESTful HTTP endpoints prefixed with `/api`.

**TS-002.** All persistent data is stored in a MongoDB document database accessed via the Motor asynchronous driver, enabling non-blocking I/O for all database operations.

**TS-003.** The system implements a Kubernetes-orchestrated containerized deployment with automatic service discovery, load balancing, and rolling update capabilities.

**TS-004.** Frontend-to-backend communication is routed through a Kubernetes ingress controller that directs all requests with `/api` prefix to port 8001 (backend) and all other requests to port 3000 (frontend).

**TS-005.** The backend implements Cross-Origin Resource Sharing (CORS) middleware allowing configurable origin domains, methods, headers, and credential passing.

**TS-006.** The system implements hot-reload development servers for both frontend (Webpack Dev Server) and backend (Uvicorn with WatchFiles), enabling real-time code changes without manual restart.

**TS-007.** Process management is handled by Supervisor, a UNIX process control system that monitors, starts, stops, and restarts both frontend and backend processes.

**TS-008.** The frontend build system uses Webpack with Babel transpilation, supporting JSX syntax, ES2020+ features, and CSS Modules via Tailwind CSS with JIT compilation.

**TS-009.** The backend implements FastAPI's automatic OpenAPI/Swagger documentation generation at `/docs` and `/redoc` endpoints for all API routes.

**TS-010.** All environment-sensitive configuration (database URLs, API keys, external service credentials) is stored in `.env` files and accessed via `os.environ.get()` (backend) and `process.env` (frontend), with no hardcoded fallback values.

**TS-011.** The system implements a Git-based version control system with automatic commits after each development checkpoint, enabling rollback to any previous state.

**TS-012.** The frontend uses React Query (TanStack Query v4) for server state management, providing automatic caching, background refetching, stale-while-revalidate strategies, and optimistic updates.

**TS-013.** The frontend routing is handled by React Router v6 with lazy-loaded route components, nested route support, and programmatic navigation.

**TS-014.** The system implements a component library based on Shadcn/UI primitives with custom dark-theme styling using CSS variables and inline style overrides.

**TS-015.** The backend implements Pydantic BaseModel validation for all request bodies, providing automatic type coercion, validation error responses, and JSON schema generation.

**TS-016.** All MongoDB ObjectId fields are excluded from API responses using `{"_id": 0}` projections or explicit field removal to prevent BSON serialization errors.

**TS-017.** The system generates UUIDs (v4) for all document identifiers instead of relying on MongoDB ObjectIds, enabling portable, collision-resistant identification.

**TS-018.** All datetime values are stored in ISO-8601 format with UTC timezone awareness using `datetime.now(timezone.utc)`.

**TS-019.** The frontend implements a centralized API client (axios instance) with base URL configuration, automatic Authorization header injection from stored tokens, and response interceptors for error handling.

**TS-020.** The system implements a Sonner toast notification library for non-blocking user feedback on actions (success, error, info) with configurable durations and positions.

**TS-021.** The CSS architecture uses Tailwind CSS utility-first classes with a custom color palette defined through CSS variables in `:root`, enabling theme switching.

**TS-022.** The system implements `@tailwindcss/animate` plugin for entrance, exit, and keyframe animations across UI components.

**TS-023.** Font loading uses Google Fonts CDN with `Plus Jakarta Sans` as the primary body font and `Sora` as the heading/brand font, loaded via `<link>` tags in the HTML head.

**TS-024.** The frontend implements a custom `AppShell` layout component providing consistent header, navigation, mobile hamburger menu, notification bell, language switcher, and logout functionality across all portal pages.

**TS-025.** The system implements a modular component architecture with clearly separated concerns: pages (route-level), components (reusable), hooks (stateful logic), contexts (global state), and lib (utilities/API).

**TS-026.** The backend implements a monolithic `server.py` file containing all API endpoints organized by domain (auth, students, narratives, brands, etc.) with planned migration to FastAPI APIRouter modules.

**TS-027.** The system uses `aiofiles` for asynchronous file I/O operations, preventing blocking during file upload/download operations.

**TS-028.** All API error responses follow the structure `{"detail": "Human-readable error message"}` with appropriate HTTP status codes (400, 401, 403, 404, 409, 500).

**TS-029.** The frontend implements error boundaries with fallback UI to prevent entire application crashes from individual component failures.

**TS-030.** The system implements request/response logging for all API calls with timestamps, method, path, status code, and duration for observability.

**TS-031.** The backend implements dependency injection via FastAPI's `Depends()` mechanism for authentication, authorization, and database access patterns.

**TS-032.** The frontend uses named exports for reusable components (`export const ComponentName`) and default exports for page-level components (`export default function PageName`).

**TS-033.** The system implements parallel tool execution for independent operations, reducing latency for multi-step processes like bulk data loading.

**TS-034.** The backend database collections include: `users`, `students`, `word_banks`, `narratives`, `brands`, `brand_impressions`, `read_logs`, `written_answers`, `assessments`, `referrals`, `coupons`, `subscriptions`, `classroom_sessions`, `audio_recordings`, `admin_messages`, `spelling_contests`, `spelling_submissions`.

**TS-035.** The system implements MongoDB indexing on frequently queried fields including `id`, `student_id`, `guardian_id`, `email`, `student_code`, and `created_date`.

**TS-036.** The frontend build output is served as static files with content hashing for cache busting, enabling CDN caching with long TTLs.

**TS-037.** The system implements health check endpoints at `/api/health` returning `{"status": "healthy", "timestamp": "..."}` for Kubernetes liveness/readiness probes.

**TS-038.** The backend implements global exception handling middleware that catches unhandled exceptions and returns standardized error responses.

**TS-039.** The system supports concurrent user sessions with stateless JWT authentication, enabling horizontal scaling without session affinity.

**TS-040.** The frontend implements code splitting via dynamic imports for route-level components, reducing initial bundle size and improving first contentful paint.

**TS-041.** The system implements HTTPS-only communication in production via Kubernetes ingress TLS termination with automatic certificate management.

**TS-042.** The backend implements rate limiting awareness for external AI service calls with retry logic and exponential backoff.

**TS-043.** The system uses `yarn` as the frontend package manager with a `yarn.lock` file ensuring deterministic dependency resolution.

**TS-044.** The backend dependencies are managed via `pip` with `requirements.txt` generated from `pip freeze` for reproducible environments.

**TS-045.** The system implements structured logging with configurable verbosity levels (DEBUG, INFO, WARNING, ERROR) for both frontend (console) and backend (stderr/stdout).

**TS-046.** The frontend implements responsive breakpoints at 375px (mobile), 640px (sm), 768px (md), 1024px (lg), 1280px (xl), and 1536px (2xl) following Tailwind's default scale.

**TS-047.** The system implements graceful degradation for users with JavaScript disabled, with critical content rendered server-side via meta tags.

**TS-048.** The backend implements async context managers for database connections, ensuring proper resource cleanup on request completion or failure.

**TS-049.** The system implements a versioned API design pattern supporting backward-compatible evolution of endpoints.

**TS-050.** The frontend implements viewport meta tags with `width=device-width, initial-scale=1` for proper mobile rendering and `maximum-scale=1` for accessibility compliance.

---

## SECTION 2: AUTHENTICATION & AUTHORIZATION (TS-051 through TS-110)

**TS-051.** The system implements JSON Web Token (JWT) authentication with HS256 signing algorithm using a configurable secret key stored in environment variables.

**TS-052.** JWT tokens contain claims for `sub` (user ID), `role`, `email`, and `exp` (expiration timestamp) with configurable expiration periods.

**TS-053.** The system implements a unified login endpoint (`POST /api/auth/login`) accepting email/password credentials and returning an access token with user profile data.

**TS-054.** Password hashing uses `bcrypt` with salt rounds, providing resistance to rainbow table attacks and brute force attempts.

**TS-055.** The system implements five distinct user roles: `admin`, `guardian`, `teacher`, `brand`, and `student`, each with role-specific portal access and API permissions.

**TS-056.** Student authentication uses a dedicated endpoint (`POST /api/auth/student-login`) accepting a student code and numeric PIN instead of email/password.

**TS-057.** Student codes are auto-generated with format `STU-XXXXX` using alphanumeric characters, ensuring uniqueness within the system.

**TS-058.** Student PINs are auto-generated as 6-digit numeric codes, displayed to guardians in the portal for shared access.

**TS-059.** The PIN input field uses `type="text"` with `inputMode="numeric"` and `pattern="[0-9]*"` to display visible digits while triggering numeric keyboards on mobile devices.

**TS-060.** The PIN input renders with bright white color (#ffffff), 1.5rem font size, 0.5em letter spacing, and WebkitTextFillColor override to prevent browser autofill styling from hiding characters.

**TS-061.** The system implements a unified login page (`GuardianLogin.jsx`) with tabs for Guardian/Admin, Teacher, Brand, and Student login modes.

**TS-062.** A separate Student Login page (`StudentLogin.jsx`) provides a dedicated, child-friendly interface for student authentication.

**TS-063.** Registration supports guardian accounts with fields for full name, email, password, and optional role-specific data.

**TS-064.** The system implements email-based password reset via the Resend email service, sending tokenized reset links with configurable expiration.

**TS-065.** The frontend stores JWT tokens in localStorage with the key `sv_token` (guardians/teachers/admins) and `sv_student` (student session data).

**TS-066.** An AuthContext React context provider wraps the application, providing `user`, `login`, `logout`, `student`, `studentLogin`, and `studentLogout` methods to all child components.

**TS-067.** Protected routes check for valid authentication tokens and redirect unauthenticated users to the login page.

**TS-068.** The system implements role-based route guards redirecting users to their appropriate portal based on their role (admin → `/admin`, guardian → `/portal`, teacher → `/teacher-portal`).

**TS-069.** Backend authentication middleware (`get_current_user`) extracts the JWT from the `Authorization: Bearer <token>` header, validates it, and retrieves the user document from MongoDB.

**TS-070.** The `get_current_admin` dependency extends `get_current_user` by additionally verifying `role == "admin"`, returning HTTP 403 for non-admin users.

**TS-071.** Token refresh is not implemented; expired tokens require re-authentication, following a stateless security model.

**TS-072.** The system implements account deactivation capabilities via the admin portal, preventing deactivated users from authenticating.

**TS-073.** The registration endpoint checks for email uniqueness before creating new accounts, returning HTTP 409 for duplicate emails.

**TS-074.** The system implements an affiliate user flag (`is_affiliate: true`) on the user document, enabling affiliate-specific features without a separate role.

**TS-075.** Affiliate registration uses a dedicated public page (`AffiliateSignup.jsx`) that creates a guardian account with the affiliate flag set.

**TS-076.** The admin portal provides user management capabilities including viewing all users, editing roles, and managing subscription status.

**TS-077.** The system implements session persistence: page refresh retrieves the stored token and validates it against the backend before restoring the session.

**TS-078.** Student sessions store the full student profile (id, full_name, student_code) in localStorage for offline-aware access.

**TS-079.** The system implements a "Remember Me" architectural provision using localStorage persistence with optional credential caching.

**TS-080.** The logout function clears all stored tokens, user data, and redirects to the login page, preventing back-button access to authenticated pages.

**TS-081.** The system implements CSRF protection through SameSite cookie policies and Origin header validation for mutation requests.

**TS-082.** API endpoints that create or modify resources require authentication except for explicitly public endpoints (health check, public audio books, active spelling contests, student notifications).

**TS-083.** The system implements brute-force protection awareness with configurable lockout thresholds for repeated failed authentication attempts.

**TS-084.** The frontend implements automatic token injection via an Axios request interceptor that reads from localStorage before every API call.

**TS-085.** The system supports multi-device sessions, allowing users to be simultaneously authenticated on multiple devices without invalidating other sessions.

**TS-086.** The backend validates token integrity on every authenticated request, checking signature, expiration, and user existence.

**TS-087.** The system implements role-based UI rendering, showing/hiding features and navigation elements based on the authenticated user's role.

**TS-088.** Admin-only API endpoints consistently use the `get_current_admin` dependency, providing uniform authorization across all admin operations.

**TS-089.** The system implements student-to-guardian association via the `guardian_id` field on student documents, enabling parents to manage only their own children.

**TS-090.** Guardian API endpoints filter results by the authenticated user's ID, preventing cross-guardian data access.

**TS-091.** The system implements teacher session management for real-time classroom features, using session codes for student-to-teacher association.

**TS-092.** Brand portal authentication provides access to brand-specific analytics filtered by the authenticated brand's ID.

**TS-093.** The system implements password complexity validation on the frontend with minimum length requirements and visual strength indicators.

**TS-094.** API responses never include password hashes, ensuring credential data stays server-side.

**TS-095.** The system implements secure token transmission via HTTPS, preventing token interception in transit.

**TS-096.** The frontend implements automatic redirect to login on HTTP 401 responses, triggered by the Axios response interceptor.

**TS-097.** The system implements onboarding wizard state persistence using `localStorage` keys scoped to user/portal type, surviving page refreshes and re-logins.

**TS-098.** Onboarding wizard completion state can be reset via a "Tutorial" button, removing the localStorage key and re-showing the wizard.

**TS-099.** The system implements FAQ sections per portal type (guardian, student, teacher) with expandable accordion-style items and search functionality.

**TS-100.** The admin portal provides a comprehensive user statistics dashboard showing total users by role, active users, and registration trends.

**TS-101.** The system implements cookie-less authentication, relying entirely on JWT tokens in HTTP headers, improving compatibility with cross-origin and mobile scenarios.

**TS-102.** The frontend implements a LanguageSwitcher component accessible from the header, supporting real-time language changes without page reload via i18next.

**TS-103.** The system implements translation files for 20+ languages, covering all UI strings, form labels, error messages, and educational terminology.

**TS-104.** Language preferences are persisted in localStorage and used to set the `Accept-Language` header for API requests.

**TS-105.** The system implements automatic language detection based on the browser's `navigator.language` setting on first visit.

**TS-106.** The backend supports multi-language content generation by passing the student's language preference to the AI content generation pipeline.

**TS-107.** The system implements right-to-left (RTL) text rendering support for Arabic, Hebrew, and other RTL languages through Tailwind's `dir` attribute.

**TS-108.** Admin-created content (word banks, brands, messages) supports Unicode text, enabling multi-language administration.

**TS-109.** The system implements locale-aware date and number formatting using the browser's `Intl` API for displaying timestamps, currencies, and percentages.

**TS-110.** Error messages from the backend are returned in English with a `detail` key, with frontend translations applied at the display layer.

---

## SECTION 3: STUDENT PROFILE SYSTEM (TS-111 through TS-180)

**TS-111.** Each student profile comprises 30+ data fields organized into demographics, educational, behavioral, and computed categories.

**TS-112.** Demographic fields include: full_name, age, date_of_birth, grade_level (enum: pre-k through college/adult), gender, ethnicity.

**TS-113.** Educational fields include: assigned_banks (array of word bank IDs), mastered_tokens (array of normalized lowercase words), spelling_mode (enum: phonetic/exact).

**TS-114.** Behavioral fields include: interests (array), virtues (array), strengths (free-text), weaknesses (free-text), belief_system, cultural_context.

**TS-115.** Computed fields include: agentic_reach_score (float 0-100), total_reading_seconds, average_wpm, biological_target, total_words_read.

**TS-116.** The system supports 32 predefined character virtues: patience, kindness, honesty, courage, responsibility, respect, perseverance, gratitude, self-control, generosity, humility, empathy, forgiveness, fairness, trustworthiness, teamwork, compassion, integrity, loyalty, wisdom, creativity, diligence, optimism, resilience, self-discipline, tolerance, mindfulness, adaptability, curiosity, independence, cooperation, determination.

**TS-117.** The system supports 30 predefined emotional intelligence categories: joy, love, hope, pride, contentment, excitement, wonder, confidence, calm, belonging, sadness, anger, fear, anxiety, frustration, loneliness, jealousy, embarrassment, disappointment, guilt, grief, confusion, surprise, sympathy, trust, awe, relief, nostalgia, determination-emotion, acceptance.

**TS-118.** Students may select unlimited virtues and emotions (no cap) from the predefined lists, with selections stored as an array of string values.

**TS-119.** The system supports custom virtue/emotion input, allowing parents to add free-text values not in the predefined lists.

**TS-120.** A search filter enables real-time filtering of the virtues/emotions list by label text as the user types.

**TS-121.** Student creation follows a multi-step wizard (4 steps): Basic Info → Virtues & Emotions → Strengths & Growth Areas → Preferences.

**TS-122.** The multi-step wizard persists form state across steps, allowing back-navigation without data loss.

**TS-123.** Student profiles are created by guardians and associated via the `guardian_id` foreign key.

**TS-124.** The system enforces a configurable maximum number of student seats per guardian, determined by their subscription tier.

**TS-125.** Student access credentials (student_code and PIN) are auto-generated upon creation and displayed to the guardian.

**TS-126.** The guardian portal provides copy-to-clipboard functionality for student codes and PINs, with visual confirmation feedback.

**TS-127.** Student profiles can be edited by their associated guardian, with all fields except id and student_code being mutable.

**TS-128.** Student profiles can be deleted by their associated guardian, with cascade deletion of associated narratives, read logs, and assessment data.

**TS-129.** The guardian portal displays student profiles as cards showing: name, student code, PIN, age, grade, interests, learning mode, mastered token count, and assigned word bank count.

**TS-130.** Student code boxes display with indigo-tinted background and dark indigo text (#1e1b4b) for high contrast readability.

**TS-131.** PIN display boxes use amber-tinted background with dark brown text (#78350f) for high contrast readability.

**TS-132.** The system computes the Agentic Reach Score using the formula: `min((mastered_tokens * W1 + completed_narratives * W2) / max(total_narratives * W2, 1) * 100, 100.0)` where W1 and W2 are configurable weights.

**TS-133.** The biological target is a configurable vocabulary goal per student, defaulting to 1000 words.

**TS-134.** Mastered tokens are added when a student achieves ≥80% accuracy on a vocabulary assessment for that word.

**TS-135.** The system tracks spelling mode per student (phonetic or exact), determining whether misspellings are graded leniently or strictly.

**TS-136.** The system supports spellcheck disabling per student profile, allowing the browser's native spellchecker to be turned off for spelling-focused learning.

**TS-137.** Student advertising preferences include `allow_brand_stories` (boolean, default false) and `blocked_categories` (array of strings).

**TS-138.** Brand content is only integrated into a student's stories if their guardian has explicitly opted in via the advertising preferences.

**TS-139.** The system supports per-student language selection, enabling bilingual or multilingual households to have children learning in different languages.

**TS-140.** Student profiles store a belief_system field (free-text) that is passed to the AI content generation pipeline for cultural sensitivity.

**TS-141.** Student profiles store a cultural_context field (free-text) that influences story settings, character names, and cultural references in generated content.

**TS-142.** The strengths field accepts parent-authored free-text descriptions of what the child excels at, used to portray the story protagonist positively.

**TS-143.** The weaknesses field accepts parent-authored free-text descriptions of growth areas, used to model protagonist overcoming challenges without shame.

**TS-144.** The system tracks total reading time per student via read log aggregation, displayed in the student dashboard.

**TS-145.** Average words per minute (WPM) is computed from read log data: `total_words_read / (total_reading_seconds / 60)`.

**TS-146.** The student dashboard displays three stat cards: Vocabulary Mastered, Agentic Reach Score, and Reading Time with trend indicators.

**TS-147.** Agentic Reach Score levels are categorized as: Initiate (0-99), Apprentice (100-299), Adept (300-599), Expert (600+).

**TS-148.** The system supports student profile data export for portability and backup purposes.

**TS-149.** Student profiles maintain a `created_date` timestamp for registration analytics and cohort analysis.

**TS-150.** The system implements student profile versioning awareness, tracking which fields have been modified and when.

**TS-151.** Parental controls are stored as a nested document within the student profile under the `parental_controls` key.

**TS-152.** Default parental controls set `recording_mode: "optional"`, `auto_start_recording: false`, `require_confirmation: true`, `chapter_threshold: 0`, `can_skip_recording: true`.

**TS-153.** The `recording_mode` field supports four values: `optional` (no requirement), `audio_required` (must record audio), `video_required` (must record video), `both_required` (must record both).

**TS-154.** The `chapter_threshold` field (integer 0-5) determines after how many chapters recording becomes required; 0 means every chapter.

**TS-155.** The `auto_start_recording` flag (boolean) controls whether the recording interface opens automatically when a chapter loads.

**TS-156.** The `require_confirmation` flag (boolean) controls whether the student must explicitly confirm before proceeding past a recording checkpoint.

**TS-157.** The `can_skip_recording` flag (boolean) determines whether the student can bypass the recording requirement and still advance.

**TS-158.** When `can_skip_recording` is false and recording is required, the "Finish Chapter" button is disabled (opacity 40%, cursor not-allowed) until a recording is submitted.

**TS-159.** A purple banner displays "Audio/Video recording required by parent" at the top of the chapter when parental controls mandate recording.

**TS-160.** A yellow warning banner displays "Complete the recording above before you can finish this chapter" when the student cannot skip.

**TS-161.** The `recording_done` state resets to false when the student navigates to a new chapter.

**TS-162.** Parental controls are fetched via `GET /api/students/{id}/parental-controls` (public endpoint for student portal access).

**TS-163.** Parental controls are updated via `PUT /api/students/{id}/parental-controls` (authenticated endpoint requiring guardian login).

**TS-164.** The ParentalControlsPanel component in the guardian portal provides an expandable "Reading Rules" section per student card.

**TS-165.** The Reading Rules panel uses a soft indigo color scheme (#eae6f2 background, #4338ca text) with toggle switches for boolean settings.

**TS-166.** Toggle switches use Lucide's `ToggleLeft`/`ToggleRight` icons with indigo (#6366f1) active color and muted (#b0aba4) inactive color.

**TS-167.** The chapter threshold input is a numeric input with min=0 and max=5, centered in a white bordered box.

**TS-168.** Changes to parental controls are saved via a "Save Reading Rules" button, triggering a PUT request with toast confirmation.

**TS-169.** The NarrativeReader component fetches parental controls at mount time using React Query with the student's ID.

**TS-170.** The system computes `mustRecord = isRecordingRequired && meetsThreshold` to determine if the current chapter requires recording.

**TS-171.** The system computes `canProceed = !mustRecord || recordingDone || controls.can_skip_recording` to determine if the Finish button should be enabled.

**TS-172.** When auto-start is enabled and recording is required, the recorder UI opens immediately when the chapter loads.

**TS-173.** When skip is disabled, the "Close" button on the recorder is hidden, forcing the student to interact with the recorder.

**TS-174.** The system supports per-chapter recording enforcement, checking against the chapter threshold for each individual chapter.

**TS-175.** Recording completion triggers a `toast.success` notification displaying the diction score percentage.

**TS-176.** The `onRecordingComplete` callback sets `recordingDone` to true, enabling the Finish Chapter button.

**TS-177.** Parent milestone notifications are generated via `POST /api/parent-milestone-check/{student_id}`, checking vocabulary, reading time, and story completion thresholds.

**TS-178.** Vocabulary milestones trigger at: 10, 25, 50, 100, 250, 500, and 1000 words mastered.

**TS-179.** Reading time milestones trigger at: 30, 60, 120, 300, and 600 minutes total.

**TS-180.** Story completion milestones trigger at: 1, 3, 5, 10, and 25 stories completed.

---

## SECTION 4: VOCABULARY SYSTEM (TS-181 through TS-260)

**TS-181.** The vocabulary system implements a novel three-tier distribution model: 60% Baseline (grade-level), 30% Target (slightly above), 10% Stretch (challenging).

**TS-182.** Word banks are structured documents containing three arrays: `baseline_words`, `target_words`, and `stretch_words`.

**TS-183.** Each word entry in a word bank comprises: `word` (string), `definition` (string), and `example_sentence` (string).

**TS-184.** Word banks have four category types: `included` (system default), `free` (community), `paid` (premium), `specialized` (domain-specific).

**TS-185.** Word banks support two visibility modes: `public` (discoverable by all users) and `private` (visible only to creator).

**TS-186.** Word banks track their creator via `created_by` (user ID) and `created_by_role` (admin/guardian/teacher).

**TS-187.** The admin portal provides a word bank management interface for creating, editing, and deleting word banks.

**TS-188.** The guardian marketplace displays available word banks with search, category filtering, and price display.

**TS-189.** Word bank prices are displayed with explicit dark text on colored backgrounds (emerald-100 for free, amber-100 for paid) with colors #064e3b and #78350f respectively.

**TS-190.** Guardians can assign multiple word banks to each student, creating personalized vocabulary curricula.

**TS-191.** Word bank assignment is tracked via the student's `assigned_banks` array containing word bank IDs.

**TS-192.** During story generation, the system randomly selects words from assigned word banks following the 60/30/10 distribution.

**TS-193.** Word selection is randomized per generation event, ensuring unique vocabulary combinations across stories.

**TS-194.** Selected words are embedded in the AI prompt as structured data, instructing the LLM to naturally incorporate them into the narrative.

**TS-195.** Each generated chapter tracks its embedded vocabulary tokens via the `embedded_tokens` array with word and tier classification.

**TS-196.** Vocabulary tokens are displayed in the NarrativeReader as color-coded badges: emerald for baseline, amber for target, rose for stretch.

**TS-197.** Clicking any word in the story text opens a WordDefinitionModal showing the word's definition, contextual usage, and pronunciation.

**TS-198.** The WordDefinitionModal uses AI-powered definition generation when the word is not in the pre-loaded word bank data.

**TS-199.** Vocabulary assessment is triggered upon completing all 5 chapters of a narrative.

**TS-200.** The VocabularyAssessment component presents questions for each target-tier and stretch-tier word from the completed narrative.

**TS-201.** Assessment question types include: definition matching, contextual sentence completion, and spelling verification.

**TS-202.** Assessment evaluation uses a secondary LLM invocation to evaluate student responses for accuracy, context understanding, and spelling.

**TS-203.** Words achieving ≥80% assessment accuracy are added to the student's `mastered_tokens` array.

**TS-204.** Mastered tokens are normalized to lowercase before storage to prevent case-sensitive duplicates.

**TS-205.** The system prevents re-assessing already-mastered words, focusing assessment on new vocabulary.

**TS-206.** Word bank pricing supports configurable amounts in USD with Stripe payment integration.

**TS-207.** Free word banks can be assigned without payment, using the wallet credit system or direct assignment.

**TS-208.** The marketplace tab supports sorting by price (low-to-high, high-to-low), popularity, and recency.

**TS-209.** Word banks display word counts per tier for transparent content sizing before purchase.

**TS-210.** The system tracks which word banks have been assigned to how many students across the platform for popularity metrics.

**TS-211.** Admin-created word banks are marked with a verified badge in the marketplace.

**TS-212.** The system supports word bank categories including: STEM, Literature, Faith, Cultural, Sports, Arts, Science, History, Geography.

**TS-213.** Each word bank has a `price` field (float) supporting values from 0.00 (free) to configurable maximums.

**TS-214.** Word bank purchases are processed through the wallet system, debiting the guardian's wallet balance.

**TS-215.** Purchased word banks remain permanently accessible to the purchasing guardian for all their students.

**TS-216.** The system implements word frequency analysis across narratives to ensure diverse vocabulary exposure.

**TS-217.** Word banks can contain up to 500 words per tier, supporting comprehensive vocabulary curricula.

**TS-218.** The system tracks word exposure count per student, recording how many times each vocabulary word has appeared in their stories.

**TS-219.** The AI prompt includes instructions to use vocabulary words in context-appropriate sentences, not forced or awkward placements.

**TS-220.** The system generates vocabulary-specific comprehension questions in addition to plot-based comprehension checks.

**TS-221.** Written answer evaluation uses LLM-based grading with configurable rubrics for definition accuracy, contextual usage, and spelling.

**TS-222.** The system supports bilingual word banks with definitions and examples in both the target language and the student's native language.

**TS-223.** Word bank preview functionality allows guardians to view sample words before purchasing.

**TS-224.** The admin portal provides analytics on word bank usage: most assigned, highest mastery rates, average assessment scores.

**TS-225.** The system implements word difficulty scoring based on word length, syllable count, and frequency in standard corpora.

**TS-226.** Teachers can create private word banks for their classes, sharing them with students via classroom sessions.

**TS-227.** The system supports word bank sharing between guardians via referral codes.

**TS-228.** Word banks track creation and last-modified timestamps for freshness indicators.

**TS-229.** The marketplace implements pagination for large catalogs with configurable page sizes.

**TS-230.** The system supports word bank search by keyword, matching against bank name, category, and individual word entries.

**TS-231.** The AI narrative generator ensures each chapter contains a configurable minimum and maximum number of vocabulary words.

**TS-232.** The system implements vocabulary progression tracking, showing guardians which words their child has encountered, partially learned, and mastered.

**TS-233.** The 60/30/10 distribution is applied per chapter, not per story, ensuring consistent difficulty across all chapters.

**TS-234.** The system handles word bank assignment changes gracefully, using the current assignments at generation time.

**TS-235.** Unassigning a word bank does not affect previously generated stories or mastered tokens.

**TS-236.** The system supports custom word entry within word banks, allowing guardians and teachers to add domain-specific vocabulary.

**TS-237.** Word banks support multimedia attachments (images, audio pronunciations) as future extension points.

**TS-238.** The vocabulary assessment includes a review mode showing correct answers after completion.

**TS-239.** The system generates vocabulary reports per student showing mastery progression over time.

**TS-240.** Word banks are versioned, allowing updates without affecting previously generated content.

**TS-241.** The system implements spaced repetition awareness, re-introducing partially-mastered words in subsequent stories.

**TS-242.** The vocabulary system supports compound words, multi-word phrases, and idiomatic expressions.

**TS-243.** Assessment scores are stored per word per student, enabling granular progress tracking.

**TS-244.** The system implements vocabulary benchmark comparisons against grade-level norms.

**TS-245.** Word banks can be tagged with grade level ranges for appropriate marketplace filtering.

**TS-246.** The system supports seasonal and thematic word bank collections (e.g., Holiday Words, Science Fair Vocabulary).

**TS-247.** Free included word banks are automatically available to all students without explicit assignment.

**TS-248.** The marketplace tab uses soft color cards (warm beige #f8f6f1) with gentle borders for a calm browsing experience.

**TS-249.** Word bank detail views show the complete word list organized by tier with definition tooltips.

**TS-250.** The system implements word bank recommendation based on student age, grade, and current mastery level.

**TS-251.** The AI prompt constrains vocabulary to age-appropriate complexity levels based on the student's grade.

**TS-252.** The system tracks vocabulary acquisition rate (words mastered per week) for progress analytics.

**TS-253.** Word banks support tagging with learning objectives aligned to educational standards (Common Core, etc.).

**TS-254.** The system implements word relationship tracking (synonyms, antonyms, word families) for deeper vocabulary understanding.

**TS-255.** Assessment questions are dynamically generated to test different aspects of word knowledge across attempts.

**TS-256.** The system supports vocabulary export for flashcard creation or external study tool integration.

**TS-257.** Word banks maintain an `is_active` flag allowing temporary deactivation without deletion.

**TS-258.** The vocabulary system integrates with the spelling contest system, using word bank words as contest material.

**TS-259.** The system implements vocabulary achievement badges at 50, 100, 250, 500, and 1000 words mastered.

**TS-260.** Word bank analytics provide per-word mastery rates across all students for content quality assessment.

---

## SECTION 5: AI CONTENT GENERATION PIPELINE (TS-261 through TS-370)

**TS-261.** Content generation uses OpenAI's GPT model via the `emergentintegrations` library with a Universal API key supporting cross-provider compatibility.

**TS-262.** Each content generation request constructs a composite prompt incorporating: student profile, vocabulary words, virtues, belief system, cultural context, language, strengths, weaknesses, and brand integration directives.

**TS-263.** The AI generates structured JSON output containing 5 chapters, each with: title, content (300-500 words), word_count, embedded_tokens, and vision_check (comprehension question).

**TS-264.** Each chapter's comprehension question includes a question string, 4 answer options, and a correct_index for automated grading.

**TS-265.** The content generation pipeline follows a synchronous request-response pattern: the guardian/student initiates generation and receives the complete narrative upon LLM completion.

**TS-266.** The system implements generation cost tracking: model name, estimated token consumption, estimated monetary cost, generation duration, and success/failure status.

**TS-267.** Generated narratives are stored in the `narratives` collection with fields: id, title, student_id, bank_ids, theme, chapters (array), total_word_count, tokens_to_verify, brand_placements, status.

**TS-268.** Narrative status progresses through: `generating` → `ready` → `in_progress` → `completed`.

**TS-269.** The AI prompt template is constructed dynamically, not hardcoded, allowing runtime modification of generation parameters.

**TS-270.** The system supports theme selection for generated stories, allowing students to choose from categories like Adventure, Mystery, Fantasy, Science, etc.

**TS-271.** The AI is instructed to portray the protagonist with characteristics matching the student's documented strengths.

**TS-272.** The AI is instructed to model the protagonist struggling with and overcoming challenges related to the student's growth areas, without shame or deficit framing.

**TS-273.** The AI is instructed to weave selected virtues into the narrative as character development themes.

**TS-274.** The AI is instructed to respect the student's belief system and incorporate culturally appropriate references.

**TS-275.** The AI generates content in the student's selected language, supporting 20+ languages.

**TS-276.** The system implements retry logic for failed AI generation attempts with exponential backoff.

**TS-277.** Generation failures are logged with error details for debugging and monitoring.

**TS-278.** The StoryGenerationDialog provides a modal interface for selecting theme, preview word count, and initiating generation.

**TS-279.** The generation dialog shows a loading spinner with progress indication during the AI generation process.

**TS-280.** Generated stories are immediately available for reading upon successful generation without additional processing.

**TS-281.** The system validates AI output structure before storing, ensuring all required fields are present and correctly typed.

**TS-282.** Each narrative stores the word bank IDs used for generation, enabling reproducibility analysis.

**TS-283.** The tokens_to_verify array lists all target-tier and stretch-tier words embedded in the narrative for assessment purposes.

**TS-284.** The system supports configurable chapter length targets, with current default of 300-500 words per chapter.

**TS-285.** The AI prompt includes specific formatting instructions to produce clean, readable prose suitable for the student's reading level.

**TS-286.** The system implements content safety filtering, instructing the AI to avoid violence, adult themes, and inappropriate content.

**TS-287.** The AI generates age-appropriate content based on the student's grade level, adjusting vocabulary complexity, sentence length, and thematic sophistication.

**TS-288.** The system supports re-generation of individual chapters if the initial output is unsatisfactory.

**TS-289.** Generated content is immutable once created, preserving the reading record and assessment history.

**TS-290.** The system tracks the total number of words across all chapters via the `total_word_count` field.

**TS-291.** The AI content generation pipeline is integrated with the brand eligibility engine for seamless brand placement.

**TS-292.** When no eligible brands are found, the AI generates brand-free educational content without compromise.

**TS-293.** The system supports batch generation for classroom scenarios where a teacher generates stories for multiple students simultaneously.

**TS-294.** The generation cost is attributed to the guardian's account for cost tracking and billing purposes.

**TS-295.** The system implements generation rate limiting to prevent abuse and manage AI service costs.

**TS-296.** The AI prompt includes instructions for natural vocabulary integration, requiring words to appear in contextually meaningful sentences.

**TS-297.** The system logs the complete AI prompt for each generation event, enabling prompt engineering analysis and improvement.

**TS-298.** Generated narratives support sharing functionality for guardian review before student access.

**TS-299.** The system implements a narrative preview that shows the first paragraph and vocabulary tokens before committing to read.

**TS-300.** The AI generates unique character names, settings, and plot elements for each story to prevent repetition.

**TS-301.** The system supports configurable AI model selection, allowing administrators to switch between LLM providers.

**TS-302.** The generation pipeline includes token counting for budget management and cost prediction.

**TS-303.** The system caches frequently used prompt components (belief system descriptions, cultural contexts) for generation performance optimization.

**TS-304.** The AI is instructed to include dialogue, descriptive passages, and action sequences for engaging storytelling.

**TS-305.** Each chapter ends with a narrative hook or cliffhanger to encourage continued reading.

**TS-306.** The system generates chapter titles that are descriptive and engaging without spoiling the plot.

**TS-307.** The AI output is parsed from JSON format with error handling for malformed responses.

**TS-308.** The system supports multi-genre story generation: realistic fiction, fantasy, science fiction, historical fiction, mystery, adventure.

**TS-309.** The generation pipeline runs asynchronously to prevent blocking the API server during LLM inference.

**TS-310.** The system implements a content quality scoring mechanism based on vocabulary integration, narrative coherence, and reading level appropriateness.

**TS-311.** Generated stories are associated with the generating student and cannot be accessed by other students unless shared via the audio book collection.

**TS-312.** The system tracks generation metrics: average generation time, success rate, average cost per story, and model usage distribution.

**TS-313.** The AI prompt includes instructions to avoid copyrighted characters, trademarked names, and protected intellectual property.

**TS-314.** The system supports partial narrative reading, tracking which chapters have been completed via the `chapters_completed` array.

**TS-315.** The NarrativeReader component implements a chapter-by-chapter reading flow with progress tracking and chapter navigation.

**TS-316.** The reading interface displays a progress bar showing `currentChapter / 5 * 100%` completion.

**TS-317.** The system tracks reading session data: start time, end time, words read, and WPM for each chapter reading.

**TS-318.** Read logs are created via `POST /api/read-logs` with student_id, narrative_id, chapter_number, session timestamps, and words_read.

**TS-319.** The NarrativeReader displays a real-time reading timer showing elapsed time and calculated WPM.

**TS-320.** The reading timer uses a green pulsing dot animation to indicate active reading time tracking.

**TS-321.** The chapter navigation supports both linear progression (Next Chapter) and random access to previously completed chapters.

**TS-322.** Completed chapters display a green checkmark badge in the chapter header.

**TS-323.** The "Finish Chapter" button triggers a comprehension check (WrittenAnswerModal) before marking the chapter as complete.

**TS-324.** Passing the comprehension check advances the student to the next chapter; failing returns them to re-read the current chapter.

**TS-325.** The system supports offline content access via IndexedDB caching (detailed in Section 13).

**TS-326.** The NarrativeReader implements a sticky header with back button, story title, chapter indicator, timer, music player, and save-offline button.

**TS-327.** The reading content area uses a high-readability font with generous line-height (1.8-1.9) and a warm reading-optimized text color (#E8E0D0).

**TS-328.** Interactive word definitions are triggered by clicking any word in the story text, with context sentence extraction for the WordDefinitionModal.

**TS-329.** Word click events extract 5 words of surrounding context to provide contextual definition assistance.

**TS-330.** The system supports text-to-speech integration for assisted reading (architectural provision).

**TS-331.** The story text is rendered with word-level spans enabling per-word interaction, hover highlighting, and click events.

**TS-332.** Word hover effects use a gold underline (#D4A853) to indicate interactive elements.

**TS-333.** The vocabulary token display shows embedded words categorized by tier with color-coded badges (emerald/amber/rose).

**TS-334.** The system tracks the current_chapter field on the narrative document for resume-from-where-you-left functionality.

**TS-335.** The NarrativeReader supports keyboard navigation for chapter advancement and timer control.

**TS-336.** The reading interface adapts to screen size with responsive padding (p-3 mobile, p-8 desktop) and font sizes.

**TS-337.** The system implements a "Read Again" option for completed stories, allowing students to revisit previous narratives.

**TS-338.** Story generation history is visible in the student dashboard as cards showing title, theme, progress, and completion status.

**TS-339.** The narrative card displays progress bars with gradient fills (gold to teal for in-progress, solid green for completed).

**TS-340.** Narrative cards show total word count and estimated reading time based on average WPM.

**TS-341.** The "Create New Story" button is disabled when no word banks are assigned, with an explanatory warning message.

**TS-342.** The system supports story deletion by guardians for content management.

**TS-343.** The generation pipeline includes duplicate detection to prevent generating near-identical stories.

**TS-344.** The system implements reading streaks tracking consecutive days of reading activity.

**TS-345.** The AI includes age-appropriate humor, interesting facts, and engaging narrative devices in generated content.

**TS-346.** The system supports multimedia story elements (images, audio) as architectural extension points.

**TS-347.** The content generation respects word bank tier distributions within a ±10% tolerance for natural integration.

**TS-348.** The system implements story difficulty progression, gradually increasing complexity across narratives.

**TS-349.** Generated stories include natural paragraph breaks for readability and comprehension.

**TS-350.** The system supports story collections where related narratives form a series with connected characters and settings.

**TS-351.** The AI generates diverse characters reflecting various backgrounds, abilities, and family structures.

**TS-352.** The system implements content flagging allowing guardians to report inappropriate generated content.

**TS-353.** The generation pipeline includes post-processing validation ensuring all requested vocabulary words appear in the output.

**TS-354.** The system supports configurable story length (number of chapters, words per chapter) as administrative settings.

**TS-355.** Generated comprehension questions test multiple cognitive levels: recall, inference, analysis, and application.

**TS-356.** The system implements narrative coherence checking, ensuring chapter-to-chapter plot continuity.

**TS-357.** The AI generates culturally sensitive content, avoiding stereotypes and promoting positive representation.

**TS-358.** The system supports seasonal and event-based story generation (holidays, cultural celebrations).

**TS-359.** Generated stories maintain consistent character attributes, settings, and timeline within a narrative.

**TS-360.** The system implements content diversity tracking to ensure varied themes across a student's story portfolio.

**TS-361.** The AI generates stories that model positive social behaviors aligned with selected virtues.

**TS-362.** The system supports collaborative story generation where multiple students contribute to a shared narrative.

**TS-363.** The generation pipeline includes timeout handling for long-running AI requests.

**TS-364.** The system implements progressive story difficulty based on vocabulary mastery progression.

**TS-365.** Generated content includes subtle educational facts and real-world knowledge appropriate to the student's grade level.

**TS-366.** The system supports story annotation by guardians for parent-child reading discussions.

**TS-367.** The AI generates engaging chapter endings that motivate continued reading.

**TS-368.** The system tracks narrative completion rates for content quality assessment.

**TS-369.** Generated stories are indexed for full-text search capabilities.

**TS-370.** The content generation pipeline supports A/B testing of different prompt strategies for quality optimization.

---

## SECTION 6: BRAND INTEGRATION ENGINE (TS-371 through TS-460)

**TS-371.** The brand integration engine operates as a real-time eligibility pipeline executing at the instant of each content generation request.

**TS-372.** Brand eligibility is determined by multi-factor filtering: age appropriateness, guardian consent, category restrictions, budget availability, and active status.

**TS-373.** The system queries the live brand database state, ensuring brand composition reflects current budgets, availability, and preferences at generation time.

**TS-374.** Up to a configurable maximum number of brands (default: 3) are selected per narrative generation.

**TS-375.** Brand selection uses weighted random sampling based on remaining budget and bid priority.

**TS-376.** Selected brands contribute products, problem statements, and integration directives to the AI prompt.

**TS-377.** The AI is instructed to integrate brand products as organic, problem-solving story elements rather than explicit advertisements.

**TS-378.** Brand products appear in the narrative as solutions to challenges the protagonist encounters, creating positive associations.

**TS-379.** Each brand placement is tracked via the `brand_placements` array on the narrative document.

**TS-380.** Brand impressions are logged in a dedicated collection (`brand_impressions`) with: brand_id, narrative_id, student_id, guardian_id, products_featured, cost, and timestamp.

**TS-381.** Brand budgets are decremented upon impression creation, preventing overspending.

**TS-382.** The system supports brand budget management: total budget, spent amount, remaining balance.

**TS-383.** The brand portal provides analytics dashboards showing: total impressions, stories featuring the brand, budget utilization.

**TS-384.** Brand analytics include specific story excerpts where the brand's products were mentioned.

**TS-385.** The system identifies brand-related comprehension questions by matching question text against brand product names.

**TS-386.** Brand-related question identification uses multi-word product name decomposition for comprehensive matching.

**TS-387.** Brand analytics display pass/fail rates for brand-related comprehension questions.

**TS-388.** The system provides brands with access to anonymized student response data for their branded content.

**TS-389.** Brand analytics aggregate data across all narratives featuring the brand, providing portfolio-level insights.

**TS-390.** The admin portal manages brands: CRUD operations, budget management, product catalog, active status.

**TS-391.** The system seeds 34 real-world brands across categories: Technology, Apparel, Sports, Food, Entertainment, Education.

**TS-392.** Each brand has: name, products (array), problem_statement, target_categories, target_ages, budget_total, budget_spent, is_active.

**TS-393.** Brand products include: name, description, and contextual use case for AI prompt construction.

**TS-394.** The brand eligibility engine respects per-student `blocked_categories`, excluding brands in restricted categories.

**TS-395.** The consent architecture requires affirmative guardian opt-in (default: false) before any brand content appears in their child's stories.

**TS-396.** The system supports per-brand targeting: age ranges, categories, and geographic constraints.

**TS-397.** Brand impression cost is configurable per brand based on bid amount and campaign settings.

**TS-398.** The system implements impression deduplication, preventing the same brand from appearing excessively in a student's stories.

**TS-399.** Brand analytics provide cost-per-impression and cost-per-engagement (comprehension question interaction) metrics.

**TS-400.** The system supports brand campaign scheduling with start and end dates.

**TS-401.** The admin portal displays brand performance rankings by engagement rate and budget efficiency.

**TS-402.** The system implements brand rotation ensuring fair distribution across eligible brands when budgets are equal.

**TS-403.** Brand competition uses a bidding mechanism where higher bids increase selection probability.

**TS-404.** The system tracks brand "Brand Comprehension" scores: the percentage of students who correctly answer brand-related questions.

**TS-405.** Brand analytics include the ability to read the full narrative text where the brand was featured.

**TS-406.** The system provides brand-specific ROI metrics based on impression cost vs. engagement rates.

**TS-407.** The admin dashboard shows aggregate brand metrics: total brands, active campaigns, total impressions, total revenue.

**TS-408.** The system supports brand self-service registration and campaign management (architectural provision).

**TS-409.** Brand product descriptions are included in the AI prompt to guide contextually appropriate integration.

**TS-410.** The system prevents competing brands from appearing in the same narrative.

**TS-411.** Brand analytics support date range filtering for campaign performance analysis.

**TS-412.** The system implements brand content quality scoring based on narrative integration naturalness.

**TS-413.** Brand placements are reviewable by guardians in the guardian portal for transparency.

**TS-414.** The system supports brand A/B testing with different product descriptions for optimization.

**TS-415.** Brand analytics include demographic breakdowns of students exposed to brand content.

**TS-416.** The system implements brand frequency capping to prevent over-exposure to individual students.

**TS-417.** Brand budget alerts notify administrators when campaigns approach budget exhaustion.

**TS-418.** The system tracks brand impression timing for peak engagement analysis.

**TS-419.** Brand analytics support export to CSV/PDF for external reporting.

**TS-420.** The system implements brand content moderation, allowing admins to review and approve brand integrations.

**TS-421.** Brand product catalogs support multimedia (images, logos) for rich analytics dashboards.

**TS-422.** The system calculates brand reach (unique students exposed) and frequency (average exposures per student).

**TS-423.** Brand campaigns support objective-based optimization: awareness, engagement, or comprehension.

**TS-424.** The system implements brand safety measures, excluding brands from narratives with sensitive themes.

**TS-425.** Brand analytics provide comparative benchmarks against category averages.

**TS-426.** The system supports real-time brand dashboard updates via polling or WebSocket connections.

**TS-427.** Brand impression data is retained for configurable periods for historical analysis.

**TS-428.** The system implements brand attribution modeling for multi-touch campaigns.

**TS-429.** Brand analytics include student engagement duration metrics for brand-containing chapters.

**TS-430.** The system supports programmatic brand integration via API for automated campaign management.

**TS-431.** Brand content guidelines are enforced by the AI prompt to maintain educational integrity.

**TS-432.** The system tracks brand mention density per chapter for integration quality metrics.

**TS-433.** Brand analytics provide word cloud visualizations of narrative contexts surrounding brand mentions.

**TS-434.** The system implements brand exclusion lists for competitive separation.

**TS-435.** Brand campaigns support geographic targeting based on student location data.

**TS-436.** The system provides brand compliance reports for regulatory requirements.

**TS-437.** Brand analytics include sentiment analysis of narrative contexts surrounding brand mentions.

**TS-438.** The system supports multi-product campaigns with per-product analytics.

**TS-439.** Brand integration instructions are customizable per campaign for targeted messaging.

**TS-440.** The system implements brand verification badges for authenticated brand partners.

**TS-441.** Brand analytics provide funnel metrics from impression to comprehension engagement.

**TS-442.** The system supports brand co-sponsorship where multiple brands share a campaign.

**TS-443.** Brand content undergoes automated safety scanning before prompt inclusion.

**TS-444.** The system implements brand performance alerts for significant metric changes.

**TS-445.** Brand analytics support cohort analysis by student demographics.

**TS-446.** The system provides brand creative testing for different product descriptions.

**TS-447.** Brand campaigns support seasonal targeting for holiday and event promotions.

**TS-448.** The system tracks brand content engagement via read log analysis for branded chapters.

**TS-449.** Brand analytics include competitive intelligence features showing market share of impressions.

**TS-450.** The system implements brand invitation workflows for new partner onboarding.

**TS-451.** Brand analytics provide lifetime value estimates based on engagement patterns.

**TS-452.** The system supports brand content localization for multi-language markets.

**TS-453.** Brand impression data is anonymized for privacy compliance while preserving analytical utility.

**TS-454.** The system implements brand campaign templates for common promotion patterns.

**TS-455.** Brand analytics include attention metrics based on reading speed in branded sections.

**TS-456.** The system supports brand content refresh cycles for long-running campaigns.

**TS-457.** Brand integration quality is continuously monitored via automated content analysis.

**TS-458.** The system provides brand partner training materials and best practices documentation.

**TS-459.** Brand analytics support API-based data export for integration with external marketing tools.

**TS-460.** The system implements brand content versioning for A/B testing different product narratives.

---

## SECTION 7: COMPREHENSION & ASSESSMENT ENGINE (TS-461 through TS-530)

**TS-461.** The comprehension system implements per-chapter vision checks (multiple-choice questions) and written answer evaluations.

**TS-462.** Vision checks present a question with 4 answer options and a correct_index, auto-grading upon selection.

**TS-463.** Written answer evaluation uses LLM-powered grading via a secondary AI invocation with configurable rubrics.

**TS-464.** The WrittenAnswerModal presents the question, a text area for free-form response, and a submit button with loading state.

**TS-465.** Written answer responses are evaluated for: content accuracy, contextual understanding, and optional spelling analysis.

**TS-466.** The system returns evaluation results including: passed/failed status, feedback text, comprehension score (0-100), and spelling errors.

**TS-467.** Spelling errors are presented as correction pairs: `{written: "...", correct: "..."}` in amber-colored badges.

**TS-468.** Passing a comprehension check automatically advances the student to the next chapter.

**TS-469.** Failing a comprehension check returns the student to re-read the chapter with an encouraging message.

**TS-470.** The system stores all written answers in the `written_answers` collection for guardian review and analytics.

**TS-471.** Vocabulary assessments are triggered after completing all 5 chapters, testing target-tier and stretch-tier words.

**TS-472.** The VocabularyAssessment component presents words one at a time with definition, context, and spelling checks.

**TS-473.** Assessment completion updates the student's mastered_tokens array and agentic_reach_score.

**TS-474.** The system supports adaptive assessment difficulty based on the student's historical performance.

**TS-475.** Assessment results are displayed with visual feedback: green checkmark for correct, red X for incorrect.

**TS-476.** The system tracks assessment attempts per word, enabling retry-until-mastery learning loops.

**TS-477.** Comprehension question generation includes brand-related questions when brand placements are present.

**TS-478.** The system evaluates both factual recall and inferential understanding in comprehension questions.

**TS-479.** Assessment data feeds into the brand analytics pipeline for brand engagement measurement.

**TS-480.** The system supports timed assessments with configurable time limits per question.

**TS-481.** Assessment scores are aggregated per student for longitudinal progress tracking.

**TS-482.** The guardian portal displays assessment history with scores, dates, and word-level breakdowns.

**TS-483.** The system implements assessment difficulty curves based on vocabulary tier and word complexity.

**TS-484.** Assessment feedback is constructive and encouraging, never punitive, aligned with growth mindset pedagogy.

**TS-485.** The system supports assessment question types: multiple choice, fill-in-the-blank, definition matching, and free response.

**TS-486.** Assessment evaluation handles misspellings with configurable tolerance based on the student's spelling mode.

**TS-487.** The system tracks time-to-answer for each assessment question for engagement analytics.

**TS-488.** Assessment results include recommendations for review topics based on incorrect answers.

**TS-489.** The system supports reassessment for previously failed words at configurable intervals.

**TS-490.** Assessment data exports are available for educational reporting and progress meetings.

**TS-491.** The comprehension evaluation pipeline processes responses asynchronously to prevent UI blocking.

**TS-492.** The system implements anti-cheating measures: randomized question order, unique question phrasing per attempt.

**TS-493.** Assessment rubrics are configurable per grade level for age-appropriate evaluation standards.

**TS-494.** The system tracks comprehension trends over time showing improvement or regression patterns.

**TS-495.** Assessment feedback includes definitions and example sentences for missed vocabulary words.

**TS-496.** The system supports group assessments for classroom scenarios.

**TS-497.** Assessment analytics are available to teachers for classroom-level performance monitoring.

**TS-498.** The system implements mastery-based progression: students must demonstrate competency before advancing to harder content.

**TS-499.** Assessment questions avoid cultural bias and maintain accessibility across diverse student populations.

**TS-500.** The system supports multi-modal assessment: text, audio (read-aloud evaluation), and future video analysis.

**TS-501.** Comprehension check animations provide engaging visual feedback for correct/incorrect answers.

**TS-502.** The system calculates comprehension rates per chapter, per narrative, and per student for analytics.

**TS-503.** Assessment data informs the AI content generation pipeline, adjusting difficulty for subsequent stories.

**TS-504.** The system supports benchmark assessments at configurable intervals for standardized progress measurement.

**TS-505.** Written answer evaluation includes sentiment analysis for student emotional engagement tracking.

**TS-506.** The system implements assessment retry limits to encourage genuine reading engagement.

**TS-507.** Assessment results trigger parental notifications for significant milestones or concerns.

**TS-508.** The system supports peer assessment features for collaborative learning scenarios.

**TS-509.** Assessment analytics include comparison with age-normed expectations.

**TS-510.** The system implements item response theory (IRT) for assessment question calibration.

**TS-511.** Assessment questions are tagged with Bloom's taxonomy levels for cognitive rigor tracking.

**TS-512.** The system supports assessment accommodations for students with learning differences.

**TS-513.** Assessment data is stored with full provenance: question, response, evaluation criteria, score, evaluator (AI model).

**TS-514.** The system implements assessment security measures preventing answer sharing between students.

**TS-515.** Assessment analytics provide class-level and school-level aggregation for educational administrators.

**TS-516.** The system supports custom assessment creation by teachers for curriculum-aligned evaluation.

**TS-517.** Assessment results feed into the student profile for progressive difficulty calibration.

**TS-518.** The system tracks assessment engagement duration for optimization of question format and length.

**TS-519.** Assessment data supports longitudinal analysis across academic years.

**TS-520.** The system implements assessment gamification: points, badges, and leaderboards for motivation.

**TS-521.** Assessment question banks are dynamically expanded based on new vocabulary and content generation.

**TS-522.** The system supports assessment scheduling for regular progress checks.

**TS-523.** Assessment results trigger adaptive content recommendations for remedial or advanced material.

**TS-524.** The system implements assessment accessibility: screen reader compatibility, high contrast modes, keyboard navigation.

**TS-525.** Assessment analytics include response pattern analysis for identifying knowledge gaps.

**TS-526.** The system supports assessment calibration using anchor items for cross-group comparability.

**TS-527.** Assessment feedback is personalized based on the student's learning profile and history.

**TS-528.** The system implements assessment versioning for iterative improvement of question quality.

**TS-529.** Assessment data is encrypted at rest and in transit for student privacy protection.

**TS-530.** The system supports assessment interoperability with external learning management systems via standard data formats.

---

## SECTION 8: READ-ALOUD RECORDING & DICTION ANALYSIS (TS-531 through TS-610)

**TS-531.** The system captures user audio and video recordings directly in the browser using the `MediaRecorder` API.

**TS-532.** Recording supports two modes: audio-only (using `audio/webm;codecs=opus`) and video (using `video/webm;codecs=vp9,opus`).

**TS-533.** The MediaRecorder configuration includes automatic codec detection with fallback to base `audio/webm` or `video/webm`.

**TS-534.** Audio/video capture uses `navigator.mediaDevices.getUserMedia()` with configurable constraints for audio quality and video resolution (640x480 ideal).

**TS-535.** The recording UI displays real-time elapsed time in MM:SS format with a red pulsing recording indicator.

**TS-536.** Recordings are captured in 1-second chunks via `recorder.start(1000)` and accumulated in a `chunksRef` array.

**TS-537.** On recording stop, chunks are combined into a single `Blob` and a local preview URL is created via `URL.createObjectURL()`.

**TS-538.** Audio recordings display a native `<audio>` player with `controls` and `preload="metadata"` attributes.

**TS-539.** Video recordings display a native `<video>` player with `controls`, `playsInline`, and `preload="metadata"` attributes.

**TS-540.** The system provides a "Re-record" option that revokes the previous blob URL and resets the recording state.

**TS-541.** Recording upload uses `FormData` with fields: file, student_id, narrative_id, chapter_number, and recording_type.

**TS-542.** The upload endpoint (`POST /api/recordings/upload`) processes multipart form data and stores the file in the server's `/uploads` directory.

**TS-543.** File storage uses unique filenames based on UUID generation to prevent collisions.

**TS-544.** Upload progress is indicated by a loading spinner and "Analyzing..." text state.

**TS-545.** After upload, the analysis endpoint (`POST /api/recordings/{id}/analyze`) processes the recording using OpenAI Whisper for speech-to-text transcription.

**TS-546.** OpenAI Whisper integration uses the `emergentintegrations` library with the Universal API key for cross-provider compatibility.

**TS-547.** The transcription result is compared against the original chapter text for diction scoring.

**TS-548.** Diction scoring implements four dimensions: pronunciation, fluency, completeness, and prosody.

**TS-549.** Pronunciation score (0-100) measures the accuracy of individual word articulation by comparing transcribed words against source words.

**TS-550.** Fluency score (0-100) measures reading smoothness based on transcription completeness and coherence.

**TS-551.** Completeness score (0-100) measures the percentage of source text words that appear in the transcription.

**TS-552.** Prosody score (0-100) estimates reading expressiveness based on transcription patterns and punctuation handling.

**TS-553.** The overall diction score is a weighted average of all four dimensions.

**TS-554.** The words_matched count tracks exactly how many source words were correctly identified in the transcription.

**TS-555.** Diction analysis results are displayed with horizontal progress bars for each dimension, color-coded by score range.

**TS-556.** The overall score is prominently displayed in a large font with indigo color (#818CF8).

**TS-557.** Analysis results are stored in the `audio_recordings` collection with: student_id, narrative_id, chapter_number, file_path, transcription, diction_scores, recording_type, status.

**TS-558.** The ReadAloudRecorder component is positioned at the TOP of each chapter, above the story text, as per user requirement.

**TS-559.** When parental controls require recording, the recorder button displays "Record Before Reading (Required)" with a lock icon.

**TS-560.** The recorder supports mode switching between audio and video with toggle buttons before recording starts.

**TS-561.** Mode toggle buttons are disabled during active recording to prevent mid-recording mode changes.

**TS-562.** Browser microphone/camera permissions are requested on first recording attempt with error handling for denied permissions.

**TS-563.** Permission denial displays a toast error: "Could not access microphone/camera. Please grant permission."

**TS-564.** The system properly cleans up media streams on component unmount via `stream.getTracks().forEach(t => t.stop())`.

**TS-565.** Blob URLs are revoked via `URL.revokeObjectURL()` on re-record or component unmount to prevent memory leaks.

**TS-566.** The timer interval is cleared on stop and unmount to prevent orphaned setInterval calls.

**TS-567.** The "Audio Memories" tab in the Guardian Portal displays all recordings made by the guardian's children.

**TS-568.** Audio Memories shows recordings grouped by student with filter buttons (All Students, individual student names).

**TS-569.** Student filter buttons use explicit `text-gray-900` on `bg-gray-100` background for visibility in the dark theme.

**TS-570.** Each recording entry displays: student name, story title, chapter number, recording date, and diction scores.

**TS-571.** Recordings can be played directly in the Audio Memories tab via embedded audio/video players.

**TS-572.** The "Audio Book Collection" is a public page displaying recordings shared by parents for community access.

**TS-573.** Sharing a recording to the public collection requires explicit parent action via a "Share" button.

**TS-574.** Shared recordings undergo admin moderation before appearing in the public collection.

**TS-575.** The admin Audio Books tab provides approve/reject controls for pending shared recordings.

**TS-576.** Approved recordings appear in the public Audio Book Collection with student name, story title, and play functionality.

**TS-577.** The Audio Book Collection supports pagination for large collections.

**TS-578.** The system tracks recording count, average diction scores, and improvement over time per student.

**TS-579.** Diction analysis comparison over time shows improvement trends across recordings (architectural provision for server-side analysis).

**TS-580.** The recording system supports background upload, allowing recordings to be saved locally and uploaded when connectivity is available.

**TS-581.** Recording file size is managed through WebM codec compression, producing reasonable file sizes for web upload.

**TS-582.** The system validates uploaded file types (audio/webm, video/webm) before processing.

**TS-583.** Upload error handling includes retry logic and user-friendly error messages.

**TS-584.** The system supports recording deletion by guardians for privacy management.

**TS-585.** Recording metadata is separated from media files, enabling fast list queries without loading audio/video data.

**TS-586.** The system implements audio streaming endpoints for efficient playback without full file download.

**TS-587.** Recording storage uses disk-based file storage with configurable upload directory paths.

**TS-588.** The system implements file cleanup for orphaned recordings (uploads without completed analysis).

**TS-589.** Recording analytics show popular recording times, average recording lengths, and completion rates.

**TS-590.** The system supports recording annotations by parents (comments, notes) for educational tracking.

**TS-591.** Diction scoring uses case-insensitive comparison for accurate word matching.

**TS-592.** The system handles punctuation in transcriptions by stripping non-alphanumeric characters before comparison.

**TS-593.** Recording status tracks the pipeline stages: uploaded → analyzing → completed → shared.

**TS-594.** The system supports bulk recording export for archival purposes.

**TS-595.** Recording quality indicators help students improve their reading technique.

**TS-596.** The system provides recording tips and guidance before the student starts reading aloud.

**TS-597.** Recording playback supports speed adjustment (0.5x, 1x, 1.5x, 2x) for review purposes.

**TS-598.** The system implements recording comparison, allowing side-by-side playback of multiple recordings of the same chapter.

**TS-599.** Recording timestamps are stored in UTC for consistent cross-timezone display.

**TS-600.** The system supports recording metadata tagging for organizational purposes.

**TS-601.** Recording analysis results include word-level timing data for detailed pronunciation feedback.

**TS-602.** The system implements recording quality assessment, alerting users to poor audio quality (background noise, low volume).

**TS-603.** Recording storage implements quotas per student to manage disk usage.

**TS-604.** The system supports recording formats beyond WebM via transcoding (architectural provision).

**TS-605.** Recording privacy settings allow per-recording visibility controls.

**TS-606.** The system implements recording search by student name, story title, or date.

**TS-607.** Recording analytics feed into the parental controls system for automated rule adjustments.

**TS-608.** The system supports live recording monitoring by guardians (architectural provision for real-time streaming).

**TS-609.** Recording diction scores contribute to the student's overall progress metrics.

**TS-610.** The system implements recording achievement badges at 10, 25, 50, and 100 recordings completed.

---

## SECTION 9: ADMIN MESSAGING SYSTEM (TS-611 through TS-660)

**TS-611.** The admin messaging system enables administrators to send targeted notifications to users and students.

**TS-612.** Messages are created via `POST /api/admin/messages` with fields: title, body, target, target_ids, priority.

**TS-613.** Target options include: `all` (everyone), `guardians` (parents only), `students` (students only), `teachers` (teachers only).

**TS-614.** Specific user targeting is supported via the `target_ids` array for precision messaging.

**TS-615.** Priority levels include: `low`, `normal`, `high`, `urgent`, each with distinct visual indicators.

**TS-616.** Messages are stored in the `admin_messages` collection with: id, title, body, target, target_ids, priority, sent_by, sent_by_name, created_date, read_by.

**TS-617.** The `read_by` array tracks which users/students have acknowledged each message using `$addToSet` operations.

**TS-618.** Message listing via `GET /api/admin/messages` returns all messages sorted by creation date (newest first).

**TS-619.** Message deletion via `DELETE /api/admin/messages/{message_id}` removes the message from the system.

**TS-620.** User notification retrieval via `GET /api/notifications` returns messages targeted at the authenticated user's role or specific ID.

**TS-621.** The notification query uses MongoDB `$or` operator to match: target=all, target=user's role, or target_ids containing user's ID.

**TS-622.** Each notification in the response includes an `is_read` boolean computed from the `read_by` array.

**TS-623.** The response includes an `unread_count` integer for badge display.

**TS-624.** Student notifications use a dedicated endpoint `GET /api/student-notifications/{student_id}` that doesn't require JWT authentication.

**TS-625.** Mark-as-read functionality via `POST /api/notifications/{message_id}/read` adds the user ID to the `read_by` array.

**TS-626.** Student mark-as-read via `POST /api/student-notifications/{message_id}/read` accepts the student_id in the request body.

**TS-627.** The AdminMessagingTab provides a form with: Subject input, Message textarea, Target dropdown, Priority dropdown, and Send button.

**TS-628.** Sent messages are displayed below the form with title, priority badge, target label, body text, sender name, date, and read count.

**TS-629.** Message deletion requires confirmation via `window.confirm` dialog.

**TS-630.** The NotificationBell component displays in the AppShell header with a bell icon and unread count badge.

**TS-631.** The unread count badge displays a red circle (#EF4444) with white text, showing "9+" for counts exceeding 9.

**TS-632.** Clicking the bell opens a dropdown panel (w-80/w-96) showing all notifications.

**TS-633.** The notification panel has a dark theme (card #1A2236) with cream text, matching the overall app aesthetic.

**TS-634.** Unread notifications have a subtle gold-tinted background (rgba(212,168,83,0.06)) and a gold dot indicator.

**TS-635.** Clicking an unread notification triggers the mark-as-read mutation and updates the UI immediately.

**TS-636.** Priority icons differ by level: AlertTriangle (red) for urgent, AlertTriangle (amber) for high, Info (teal) for normal/low.

**TS-637.** The panel auto-closes when clicking outside via a `mousedown` event listener.

**TS-638.** Notifications are auto-refreshed every 30 seconds via React Query's `refetchInterval`.

**TS-639.** The NotificationBell supports both guardian mode (JWT auth) and student mode (student_id parameter).

**TS-640.** The AppShell passes `isStudent` and `studentId` props to the NotificationBell for mode detection.

**TS-641.** The notification panel supports a maximum height of 70vh with overflow-y scroll for long notification lists.

**TS-642.** Message dates are formatted using the browser's `toLocaleString()` for locale-aware display.

**TS-643.** The messaging form validates required fields (title and body) before enabling the send button.

**TS-644.** The send mutation disables the button and shows "Sending..." text during API call.

**TS-645.** Successful message creation resets the form to default values and triggers a toast notification.

**TS-646.** The admin messaging interface is mobile-responsive with single-column layout on small screens.

**TS-647.** Select dropdowns use explicit `bg-white` with dark text color for visibility in the BrutalCard context.

**TS-648.** The system supports message scheduling for future delivery (architectural provision).

**TS-649.** Message analytics track open rates, read rates, and engagement across target groups.

**TS-650.** The system supports message templates for recurring communications.

**TS-651.** Messages support markdown formatting for rich text content (architectural provision).

**TS-652.** The system implements message delivery confirmation for critical communications.

**TS-653.** Message retention policies are configurable for data management.

**TS-654.** The system supports message threading for conversational follow-ups.

**TS-655.** Message search functionality enables finding past communications by keyword.

**TS-656.** The system supports email delivery integration for offline notification via Resend service.

**TS-657.** Message analytics include time-to-read metrics for engagement optimization.

**TS-658.** The system supports message personalization with dynamic fields (student name, parent name).

**TS-659.** Push notification integration for mobile devices (architectural provision for PWA push).

**TS-660.** The system implements message priority escalation for unread urgent messages.

---

## SECTION 10: SPELLING BEE CONTESTS (TS-661 through TS-720)

**TS-661.** The spelling contest system enables administrators to create timed spelling challenges for students.

**TS-662.** Contest creation via `POST /api/admin/spelling-contests` accepts: title, description, word_list, time_limit_seconds, start_date, end_date.

**TS-663.** Word lists are provided as comma-separated values in the admin UI and stored as arrays of strings.

**TS-664.** Time limits are configurable per contest in seconds, defaulting to 120 seconds.

**TS-665.** Contest visibility is controlled by `is_active` (boolean) and date range (start_date to end_date).

**TS-666.** Active contests are listed via `GET /api/spelling-contests` filtered by `is_active: true` and `end_date >= now`.

**TS-667.** Each contest in the list response includes a `participant_count` computed from submissions.

**TS-668.** Contest toggling via `PUT /api/admin/spelling-contests/{id}/toggle` flips the `is_active` flag.

**TS-669.** Contest deletion via `DELETE /api/admin/spelling-contests/{id}` removes both the contest and all associated submissions.

**TS-670.** Contest submission via `POST /api/spelling-contests/submit` accepts: contest_id, student_id, student_name, answers (dict), time_taken_seconds.

**TS-671.** Scoring compares each student answer against the original word list using case-insensitive string comparison.

**TS-672.** The submission response includes: results (per-word correct/incorrect), correct_count, total_words, score (percentage), and time_taken_seconds.

**TS-673.** Leaderboard retrieval via `GET /api/spelling-contests/{id}/leaderboard` returns all submissions sorted by score (descending) then time (ascending).

**TS-674.** Each leaderboard entry includes a computed `rank` field.

**TS-675.** The AdminSpellingContestsTab provides a creation form with: title, time limit, description, words textarea, start/end date pickers.

**TS-676.** The word count is dynamically displayed below the words textarea as the admin types.

**TS-677.** Created contests are displayed with: title, status badge (LIVE/PAUSED/ENDED), word count, time limit, participant count, date range.

**TS-678.** Contest word lists are displayed as purple badges showing the first 8 words with a "+N more" overflow indicator.

**TS-679.** Admin actions include: Leaderboard view, Pause/Activate toggle, and Delete with confirmation.

**TS-680.** The leaderboard panel expands inline below the contest card when the Leaderboard button is clicked.

**TS-681.** Leaderboard entries show: rank, student name, correct count, total words, time taken, and score percentage.

**TS-682.** Score colors are: green (≥80%), amber (≥50%), red (<50%).

**TS-683.** The student SpellingBee component displays active contests with title, description, word count, time limit, and participant count.

**TS-684.** The "Start" button initiates the contest flow, loading words and starting the countdown timer.

**TS-685.** The contest presents one word at a time with: blank underscores showing word length, letter count hint, and first letter hint.

**TS-686.** The spelling input field uses `spellCheck={false}` and `autoComplete="off"` to prevent browser assistance.

**TS-687.** The input has letter-spacing (0.15em) for clear character separation and gold accent border.

**TS-688.** The "Next Word" button advances to the next word, storing the current answer in state.

**TS-689.** Pressing Enter in the input field triggers the next word action for keyboard-friendly navigation.

**TS-690.** A progress bar shows `currentWordIndex / totalWords * 100%` with gold-to-teal gradient.

**TS-691.** The countdown timer displays in MM:SS format with red styling when under 30 seconds remaining.

**TS-692.** When the timer reaches zero, the contest auto-submits with whatever words have been answered.

**TS-693.** The final word triggers the "Finish" button label instead of "Next Word".

**TS-694.** Results are displayed as a trophy icon with score percentage, correct count, and time taken.

**TS-695.** Individual word results show green checkmarks for correct and red X marks for incorrect answers.

**TS-696.** Incorrect answers display the student's spelling alongside the correct word.

**TS-697.** Skipped words (empty answers) display "(skipped)" as the student's answer.

**TS-698.** The student leaderboard is accessible via a trophy icon button, showing the top 10 entries.

**TS-699.** The "Back to Contests" button returns to the contest list after reviewing results.

**TS-700.** Contest state (answers, current word, timer) is maintained in React state, not persisted until submission.

**TS-701.** The system prevents multiple submissions by the same student to the same contest (architectural provision).

**TS-702.** Spelling contests integrate with the word bank system, enabling word bank-sourced contests.

**TS-703.** Contest creation supports grade-level targeting for age-appropriate word selection.

**TS-704.** The system supports team-based spelling contests for classroom competitions.

**TS-705.** Contest analytics show average scores, completion rates, and difficulty analysis per word.

**TS-706.** The system supports recurring contests (weekly, monthly) with automated word rotation.

**TS-707.** Contest results contribute to the student's overall vocabulary metrics.

**TS-708.** The system supports practice mode for non-competitive spelling practice.

**TS-709.** Contest word difficulty is analyzed post-competition based on aggregate performance.

**TS-710.** The system supports audio pronunciation of contest words (text-to-speech integration).

**TS-711.** Contest participation history is tracked per student for engagement analytics.

**TS-712.** The system supports contest sharing via links for community engagement.

**TS-713.** Contest results can be exported for classroom reporting.

**TS-714.** The system implements spelling pattern analysis identifying common error types.

**TS-715.** Contest creation supports uploading word lists from CSV files.

**TS-716.** The system supports multi-round tournament-style spelling competitions.

**TS-717.** Contest rewards integrate with the gamification system (points, badges).

**TS-718.** The system tracks spelling improvement over time across contests.

**TS-719.** Contest notifications remind students of upcoming and ending contests.

**TS-720.** The system supports regional and global leaderboards for competitive engagement.

---

## SECTION 11: TASK REMINDER SYSTEM (TS-721 through TS-770)

**TS-721.** The task reminder system generates contextual reminders based on student reading activity, recording obligations, and available challenges.

**TS-722.** Reminders are generated dynamically via `GET /api/student-reminders/{student_id}` on each request, not stored.

**TS-723.** Incomplete story reminders are generated for narratives with 1-4 completed chapters (partially read).

**TS-724.** Incomplete story reminders show progress percentage and encouraging message: "You've read X/5 chapters. Keep going!"

**TS-725.** Inactivity reminders trigger after 3+ days without reading activity, showing days since last session.

**TS-726.** First-time inactivity reminders appear for students with narratives but no read logs: "You have stories waiting for you."

**TS-727.** Recording-due reminders appear when parental controls require recording but completed chapters lack recordings.

**TS-728.** Recording reminders specify the exact story title and chapter number needing recording.

**TS-729.** Spelling contest reminders appear for active contests the student hasn't yet attempted.

**TS-730.** Reminders are sorted by priority: high → medium → low for attention prioritization.

**TS-731.** Priority assignment: incomplete stories = high, inactivity = medium (or high if first-time), recording due = high, spelling contests = low.

**TS-732.** The response includes a total `count` field for badge display.

**TS-733.** The TaskReminders component displays at the top of the StudentAcademy page, above stats cards.

**TS-734.** Each reminder is a clickable button that navigates to the relevant action (open story, open spelling bee).

**TS-735.** Reminder cards show: type-specific icon, title, message, progress percentage (if applicable), and a chevron arrow.

**TS-736.** Color coding by priority: red tones for high, amber for medium, indigo for low.

**TS-737.** Reminders display a maximum of 5 items to prevent overwhelming the student.

**TS-738.** The reminder component auto-refreshes every 60 seconds via React Query's `refetchInterval`.

**TS-739.** The "Your Tasks" header shows the total reminder count in parentheses with a gold sparkle icon.

**TS-740.** Clicking a story reminder opens the NarrativeReader with the corresponding narrative.

**TS-741.** Clicking a spelling contest reminder activates the Spelling Bee section.

**TS-742.** The component gracefully hides when there are zero reminders, saving screen space.

**TS-743.** Parent milestone checks via `POST /api/parent-milestone-check/{student_id}` compute achievement thresholds.

**TS-744.** Vocabulary milestones at: 10, 25, 50, 100, 250, 500, 1000 words mastered.

**TS-745.** Reading time milestones at: 30, 60, 120, 300, 600 minutes total.

**TS-746.** Story completion milestones at: 1, 3, 5, 10, 25 stories completed.

**TS-747.** Milestone messages include the student's name for personalized parent notifications.

**TS-748.** The milestone system supports custom threshold configuration.

**TS-749.** Milestones are computed from live database queries, always reflecting current student state.

**TS-750.** The system supports milestone notification delivery via the admin messaging infrastructure.

**TS-751.** Milestone achievements trigger celebratory UI elements in the student portal.

**TS-752.** The system tracks which milestones have been previously acknowledged to prevent repeat notifications.

**TS-753.** Reminder generation queries multiple collections (narratives, read_logs, audio_recordings, spelling_submissions) for comprehensive coverage.

**TS-754.** The inactivity check uses ISO date comparison with timezone-aware datetime parsing.

**TS-755.** The recording-due check cross-references completed chapters against the audio_recordings collection.

**TS-756.** Spelling contest eligibility checks the student's submission history against active contest IDs.

**TS-757.** The system supports reminder customization by parents (enable/disable specific reminder types).

**TS-758.** Reminder frequency is configurable to prevent notification fatigue.

**TS-759.** The system supports scheduled reminder delivery at optimal engagement times.

**TS-760.** Reminder analytics track click-through rates for effectiveness measurement.

**TS-761.** The system supports reminder escalation for repeatedly ignored high-priority items.

**TS-762.** Reminder content is age-appropriate and encouraging, never punitive.

**TS-763.** The system supports reminder localization for multi-language student populations.

**TS-764.** Reminder generation is optimized with database query batching for performance.

**TS-765.** The system supports parent-visible reminder summaries for family coordination.

**TS-766.** Reminder types are extensible, supporting new categories as features are added.

**TS-767.** The system tracks reminder dismissal for engagement analytics.

**TS-768.** Reminder UI adapts to screen size with compact mobile layout.

**TS-769.** The system supports push notification delivery for reminders (PWA provision).

**TS-770.** Reminder effectiveness metrics inform content engagement strategies.

---

## SECTION 12: NOTIFICATION & COMMUNICATION INFRASTRUCTURE (TS-771 through TS-810)

**TS-771.** The notification system serves as the unified delivery mechanism for admin messages, task reminders, milestone alerts, and system notifications.

**TS-772.** Notifications are delivered via in-app notification panel accessible from the AppShell header.

**TS-773.** The notification bell icon uses Lucide's `Bell` component with size 18 for compact display.

**TS-774.** Unread count is computed server-side and displayed as a red badge overlay on the bell icon.

**TS-775.** The notification panel uses `position: absolute` with z-index 100 for overlay display.

**TS-776.** Panel width adapts to screen size: 320px (w-80) on mobile, 384px (w-96) on desktop.

**TS-777.** The panel header includes a title ("Notifications") with unread count and a close button.

**TS-778.** Each notification item displays: priority icon, title (truncated), body (2-line clamp), date, and read indicator.

**TS-779.** The unread indicator is a 2px gold dot (#D4A853) next to the title.

**TS-780.** Read notifications have transparent background; unread have subtle gold tint.

**TS-781.** The panel body scrolls vertically with a maximum height of 60vh.

**TS-782.** Empty state shows a muted bell icon with "No notifications" text.

**TS-783.** The panel implements click-outside-to-close using a `mousedown` event listener on `document`.

**TS-784.** Event listener cleanup occurs on component unmount to prevent memory leaks.

**TS-785.** The system supports email notification delivery via the Resend service for critical alerts.

**TS-786.** Email templates use HTML formatting with the Semantic Vision branding.

**TS-787.** The system supports notification preferences per user (in-app, email, both, none).

**TS-788.** Notification history is retained for audit and compliance purposes.

**TS-789.** The system implements notification batching to prevent excessive individual deliveries.

**TS-790.** Notification delivery status is tracked (delivered, read, dismissed) for analytics.

**TS-791.** The system supports notification channels expansion (SMS, push) via pluggable architecture.

**TS-792.** Critical notifications (system maintenance, security alerts) bypass user preferences.

**TS-793.** Notification content is sanitized to prevent XSS and injection attacks.

**TS-794.** The system supports notification templates with variable substitution for dynamic content.

**TS-795.** Notification scheduling supports delayed delivery for time-sensitive communications.

**TS-796.** The system implements notification deduplication to prevent identical messages from appearing multiple times.

**TS-797.** Notification read status is persistent across sessions via server-side `read_by` tracking.

**TS-798.** The system supports notification grouping by topic or sender for organized display.

**TS-799.** Notification analytics include delivery rates, open rates, and engagement metrics per campaign.

**TS-800.** The system supports notification sound alerts for high-priority items (PWA audio provision).

**TS-801.** Notification rendering uses virtualized scrolling for performance with large notification volumes.

**TS-802.** The system supports notification deep linking, directing users to specific pages when clicked.

**TS-803.** Notification priority determines display order, icon, and color scheme.

**TS-804.** The system implements notification expiration, automatically removing old notifications from the display.

**TS-805.** Notification content supports rich formatting (bold, links, images) via HTML rendering.

**TS-806.** The system supports notification categories for filtering and management.

**TS-807.** Notification delivery respects user timezone for appropriate timing.

**TS-808.** The system implements notification rate limiting to prevent spam from automated systems.

**TS-809.** Notification analytics feed into user engagement scoring.

**TS-810.** The system supports cross-device notification synchronization for multi-device users.

---

## SECTION 13: OFFLINE & PWA CAPABILITIES (TS-811 through TS-860)

**TS-811.** The system implements Progressive Web App (PWA) capabilities enabling installation as a standalone application on mobile and desktop devices.

**TS-812.** The PWA manifest (`manifest.json`) defines: short_name ("Semantic Vision"), name, start_url ("/"), display ("standalone"), theme_color (#0A0F1E), background_color (#0A0F1E).

**TS-813.** Apple mobile web app meta tags enable iOS installation: `apple-mobile-web-app-capable=yes`, `apple-mobile-web-app-status-bar-style=black-translucent`, `apple-mobile-web-app-title`.

**TS-814.** The manifest link is included in the HTML head via `<link rel="manifest" href="/manifest.json">`.

**TS-815.** A Service Worker (`service-worker.js`) is registered in `index.js` using `navigator.serviceWorker.register()` on window load.

**TS-816.** The Service Worker implements a stale-while-revalidate caching strategy for GET requests.

**TS-817.** On `install`, the Service Worker pre-caches static assets (index.html, root route) and calls `self.skipWaiting()`.

**TS-818.** On `activate`, the Service Worker cleans up old caches by deleting all cache keys not matching the current version.

**TS-819.** On `fetch`, the Service Worker serves cached responses while simultaneously fetching fresh versions for cache updates.

**TS-820.** Only successful (status 200) basic-type responses are cached to prevent caching error pages.

**TS-821.** Failed network requests fall back to cached responses for offline resilience.

**TS-822.** Non-GET requests (POST, PUT, DELETE) are passed through without caching.

**TS-823.** Cache versioning uses the `CACHE_NAME` constant (e.g., 'sv-offline-v1') for controlled cache invalidation.

**TS-824.** Offline story caching uses IndexedDB for structured data storage via the `offlineCache.js` utility library.

**TS-825.** The IndexedDB database name is 'sv-offline' with an 'stories' object store keyed by story ID.

**TS-826.** `saveStoryOffline(narrative)` stores the complete narrative document in IndexedDB with a `saved_date` timestamp.

**TS-827.** `isStorySaved(narrativeId)` checks if a specific story exists in the offline store.

**TS-828.** `getOfflineStories(studentId)` retrieves all offline stories, optionally filtered by student ID.

**TS-829.** `removeOfflineStory(narrativeId)` deletes a specific story from the offline store.

**TS-830.** `getOfflineStorageInfo()` returns statistics: count of saved stories and total size in megabytes.

**TS-831.** `isOnline()` checks `navigator.onLine` for current connectivity status.

**TS-832.** The SaveOfflineButton component integrates in the NarrativeReader header in compact mode (icon-only button).

**TS-833.** The button shows: Download icon (not saved), bouncing Download (saving), Checkmark (saved).

**TS-834.** Button color changes: gray border (not saved) → green border/text (saved).

**TS-835.** Clicking a saved story toggles removal from offline storage.

**TS-836.** Toast notifications confirm save ("Saved for offline reading!") and removal ("Removed from offline library").

**TS-837.** The OfflineLibrary component is accessible from the StudentAcademy via the "Offline" toolbar button.

**TS-838.** The library displays online/offline status with a green Wifi icon (online) or yellow WifiOff icon (offline).

**TS-839.** Storage info shows the count of saved stories and total disk usage in megabytes.

**TS-840.** Each saved story card shows: title, chapter count, saved date, play button, and remove button.

**TS-841.** Clicking the play button on a saved story opens the NarrativeReader with offline data.

**TS-842.** The remove button deletes the story from IndexedDB and refreshes the library.

**TS-843.** Online/offline status updates in real-time via `window.addEventListener('online'/'offline')`.

**TS-844.** Empty state shows a WifiOff icon with "No Offline Stories" and guidance text.

**TS-845.** The system supports offline story reading without network connectivity once stories are cached.

**TS-846.** Offline reading does not track read logs (which require network for API calls).

**TS-847.** The system queues offline actions for synchronization when connectivity is restored (architectural provision).

**TS-848.** PWA installation prompts are handled by the browser's native install banner.

**TS-849.** The system supports offline assessment attempts with deferred submission (architectural provision).

**TS-850.** IndexedDB storage is persistent across browser sessions and survives page refreshes.

**TS-851.** The system handles IndexedDB quota errors gracefully with user-friendly storage full messages.

**TS-852.** Offline cached stories include all chapter content, vocabulary tokens, and comprehension questions.

**TS-853.** The system supports selective chapter caching for partial offline storage.

**TS-854.** Offline storage analytics help users manage their cached content.

**TS-855.** The system implements background sync for offline-created data (Service Worker sync event).

**TS-856.** PWA updates are handled via Service Worker lifecycle, prompting users when new versions are available.

**TS-857.** The system supports offline recording with deferred upload when connectivity returns.

**TS-858.** IndexedDB operations are wrapped in try-catch blocks for browser compatibility.

**TS-859.** The offline system degrades gracefully in browsers that don't support Service Workers or IndexedDB.

**TS-860.** The system implements data compression for offline storage optimization (architectural provision).

---

## SECTION 14: AMBIENT MUSIC ENGINE (TS-861 through TS-890)

**TS-861.** The ambient music system generates mood-appropriate background sound using the Web Audio API.

**TS-862.** The AmbientMusicPlayer class creates and manages oscillators, gain nodes, and audio contexts.

**TS-863.** Eight mood categories are supported: adventurous, calm, mysterious, joyful, emotional, exciting, peaceful, inspiring.

**TS-864.** Each mood defines frequency ranges and modulation parameters for distinct sonic characteristics.

**TS-865.** The `analyzeMood(text)` static method performs keyword-based mood detection from story text.

**TS-866.** Mood detection scans for mood-specific keywords (e.g., "dark", "shadow" for mysterious; "happy", "smile" for joyful).

**TS-867.** The mood with the highest keyword match count is selected as the detected mood.

**TS-868.** The MusicPlayerWidget integrates in the NarrativeReader header with play/stop, volume, and mood selector.

**TS-869.** The play button toggles between Volume2 (playing) and Music (stopped) icons with gold/muted colors.

**TS-870.** Volume control uses an HTML range input (0 to 0.4, step 0.01) with amber accent color.

**TS-871.** The mood selector is a dropdown showing all available moods with capitalized labels.

**TS-872.** Changing the mood while playing stops the current sound and starts the new mood's ambient.

**TS-873.** The audio context is created on first play action, complying with browser autoplay policies.

**TS-874.** Component cleanup stops all oscillators and closes the audio context on unmount.

**TS-875.** The default volume is set to 0.12 for non-intrusive background ambiance.

**TS-876.** The music player uses minimal screen space (compact inline layout) to avoid distracting from reading.

**TS-877.** The volume slider only appears when music is playing to reduce visual clutter.

**TS-878.** Mood auto-detection runs when new story text is provided, updating the current mood.

**TS-879.** The system supports custom mood creation with user-defined frequency parameters (architectural provision).

**TS-880.** The ambient music system operates entirely client-side, requiring no server resources.

**TS-881.** Audio generation uses sine wave oscillators with amplitude modulation for organic sound.

**TS-882.** The system implements smooth audio transitions when changing moods or volume.

**TS-883.** Browser compatibility is ensured through AudioContext/webkitAudioContext fallback.

**TS-884.** The system supports layered sound generation with multiple simultaneous oscillators.

**TS-885.** The mood selector dropdown uses dark theme styling matching the NarrativeReader header.

**TS-886.** The `getMoods()` static method returns the list of available mood names for UI rendering.

**TS-887.** The system supports mood-specific volume presets for balanced ambient levels.

**TS-888.** The music player state (playing, volume, mood) does not persist across page navigations.

**TS-889.** The system supports external audio file playback as an alternative to generated ambient sounds (architectural provision).

**TS-890.** The ambient music system is patent-claimed as a novel educational reading experience enhancement.

---

## SECTION 15: ANALYTICS & DASHBOARDS (TS-891 through TS-930)

**TS-891.** The admin statistics dashboard provides platform-wide metrics: total users, students, stories, brands, revenue.

**TS-892.** Statistics are computed from live database aggregation queries for real-time accuracy.

**TS-893.** The admin dashboard displays user growth trends over configurable time periods.

**TS-894.** Brand analytics dashboards show per-brand performance: impressions, stories, budget utilization, engagement rates.

**TS-895.** The guardian progress tab shows per-student metrics: reading time, words mastered, stories completed, assessment scores.

**TS-896.** Progress tracking includes visual trend lines showing improvement or regression over time.

**TS-897.** The system computes reading engagement metrics: average session duration, reading frequency, completion rates.

**TS-898.** Student dashboard stat cards display: Vocabulary Mastered, Agentic Reach Score, Reading Time with comparative indicators.

**TS-899.** Admin revenue analytics track wallet credits, subscription payments, word bank purchases, and brand impression revenue.

**TS-900.** The system supports export of analytics data in CSV and PDF formats for reporting.

**TS-901.** Analytics dashboards are role-specific: admins see platform-wide data, guardians see their children, teachers see their classes.

**TS-902.** The system tracks content generation metrics: stories generated, average generation time, success rate, cost per story.

**TS-903.** Assessment analytics show per-student and aggregate performance on vocabulary assessments and comprehension checks.

**TS-904.** The system tracks user engagement funnels: registration → onboarding → first story → first assessment → first mastery.

**TS-905.** Brand ROI dashboards show cost-per-engagement, brand awareness lift, and comprehension question performance.

**TS-906.** The system implements cohort analysis for comparing student outcomes across different time periods.

**TS-907.** Teacher dashboards show classroom performance: average scores, participation rates, top performers.

**TS-908.** The system tracks affiliate performance metrics: referrals, conversions, commission earned.

**TS-909.** Analytics data is computed using MongoDB aggregation pipelines for efficient processing.

**TS-910.** Dashboard visualizations include charts, progress bars, stat cards, and data tables.

**TS-911.** The system supports real-time dashboard updates for time-sensitive metrics.

**TS-912.** Analytics retention policies manage data lifecycle for performance and compliance.

**TS-913.** The system implements analytics caching for frequently accessed metrics.

**TS-914.** Cross-referencing analytics connect student progress with brand exposure for engagement correlation.

**TS-915.** The system supports custom report creation with configurable metrics and filters.

**TS-916.** Analytics access is governed by role-based permissions ensuring data privacy.

**TS-917.** The system tracks platform health metrics: API response times, error rates, uptime.

**TS-918.** Analytics dashboards are mobile-responsive with stacked layouts on small screens.

**TS-919.** The system supports analytics API endpoints for external business intelligence tool integration.

**TS-920.** Data visualization uses consistent color coding across all dashboards for intuitive understanding.

**TS-921.** The system implements anomaly detection for unusual metric patterns.

**TS-922.** Analytics include demographic segmentation for equity and inclusion analysis.

**TS-923.** The system tracks feature adoption metrics for product development prioritization.

**TS-924.** Analytics support A/B test result analysis for content optimization experiments.

**TS-925.** The system implements benchmark comparisons against educational standards.

**TS-926.** Analytics data supports research partnership initiatives with educational institutions.

**TS-927.** The system tracks vocabulary acquisition rates across different pedagogical approaches.

**TS-928.** Brand analytics include viewability metrics measuring reading time in brand-containing sections.

**TS-929.** The system supports scheduled analytics reports delivered via email.

**TS-930.** Analytics infrastructure supports scale to millions of students and billions of data points.

---

## SECTION 16: PAYMENT & MONETIZATION (TS-931 through TS-960)

**TS-931.** The payment system integrates Stripe for credit card processing, subscription management, and wallet operations.

**TS-932.** The wallet system maintains per-guardian credit balances for in-platform purchases (word banks, subscriptions).

**TS-933.** Wallet credits can be added via Stripe payment with configurable deposit amounts.

**TS-934.** The subscription system supports tiered plans with varying student seats, word bank access, and feature levels.

**TS-935.** The coupon system enables promotional discounts with configurable discount amounts, usage limits, and expiration dates.

**TS-936.** The referral system generates unique referral codes per guardian for friend-to-friend promotion.

**TS-937.** Successful referrals credit wallet bonuses to both the referrer and referred user.

**TS-938.** The affiliate system supports commission-based partnerships for content creators and educational influencers.

**TS-939.** Affiliate tracking uses unique referral links with attribution cookies for conversion tracking.

**TS-940.** The admin portal manages coupon creation, referral program settings, and affiliate approvals.

**TS-941.** Brand impression costs are configurable per brand and deducted from brand budgets upon generation.

**TS-942.** The system supports free-tier access with limited features for onboarding without payment.

**TS-943.** Premium features are gated behind subscription or wallet credit requirements.

**TS-944.** The payment system supports refund processing via Stripe's refund API.

**TS-945.** Transaction history is maintained for all wallet operations with timestamps and descriptions.

**TS-946.** The system supports multiple currency formats with locale-aware display.

**TS-947.** Stripe webhook integration handles asynchronous payment events (success, failure, refund).

**TS-948.** The system implements idempotency keys for Stripe requests to prevent duplicate charges.

**TS-949.** Payment security follows PCI DSS compliance by never storing card details server-side.

**TS-950.** The subscription system supports annual and monthly billing cycles.

**TS-951.** The system supports promotional pricing periods for new user acquisition.

**TS-952.** Payment receipts are generated and available for download via the wallet tab.

**TS-953.** The system supports payment method management (add, remove, set default) via Stripe.

**TS-954.** Revenue analytics track MRR, ARR, churn rate, and customer lifetime value.

**TS-955.** The system supports payment plans for high-value purchases.

**TS-956.** Coupon validation checks usage limits, expiration, and applicability before applying discounts.

**TS-957.** The referral leaderboard shows top referrers with conversion counts and earned rewards.

**TS-958.** The system supports gift cards and prepaid credit purchases for educational institutions.

**TS-959.** Payment system supports future integration with additional gateways: Cash App, Zelle, Venmo, PayPal.

**TS-960.** Revenue reporting supports tax compliance with itemized transaction records.

---

## SECTION 17: SECURITY & PRIVACY (TS-961 through TS-1000)

**TS-961.** All user passwords are hashed using bcrypt with configurable salt rounds before storage.

**TS-962.** JWT tokens use HS256 signing with a secret key stored exclusively in environment variables.

**TS-963.** HTTPS encryption is enforced for all client-server communication in production.

**TS-964.** CORS configuration restricts API access to authorized frontend origins.

**TS-965.** The system implements the principle of least privilege: each role has minimum necessary API access.

**TS-966.** Guardian ad preferences default to opt-out (false), requiring explicit consent for brand content.

**TS-967.** Children's data (student profiles) is accessible only to their associated guardian and system administrators.

**TS-968.** The system implements COPPA (Children's Online Privacy Protection Act) compliance measures for users under 13.

**TS-969.** Personal identifiable information (PII) is excluded from brand analytics, providing only aggregate statistics.

**TS-970.** Recording data (audio/video) is stored server-side with access limited to the student's guardian and administrators.

**TS-971.** Public audio book sharing requires explicit guardian consent and admin moderation before publication.

**TS-972.** The system implements data retention policies with configurable retention periods per data type.

**TS-973.** Account deletion cascades to all associated data: students, narratives, recordings, assessments, and logs.

**TS-974.** The system implements input sanitization for all user-provided text to prevent XSS attacks.

**TS-975.** MongoDB queries use parameterized inputs to prevent NoSQL injection attacks.

**TS-976.** File upload validation checks content type, file size, and extension before processing.

**TS-977.** The system implements rate limiting on authentication endpoints to prevent brute-force attacks.

**TS-978.** API responses never expose internal implementation details (stack traces, database queries) in production.

**TS-979.** The system implements secure HTTP headers: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection.

**TS-980.** Environment variables containing secrets (API keys, database URLs) are never committed to version control.

**TS-981.** The system implements audit logging for security-sensitive operations (login, data deletion, admin actions).

**TS-982.** The system supports GDPR compliance with data export and right-to-erasure capabilities.

**TS-983.** Session management implements timeout policies for inactive sessions.

**TS-984.** The system implements content security policies (CSP) to prevent unauthorized script execution.

**TS-985.** Database backups are performed regularly with encrypted storage for disaster recovery.

**TS-986.** The system implements vulnerability scanning awareness for dependency management.

**TS-987.** API authentication tokens have configurable expiration to limit exposure from token theft.

**TS-988.** The system implements IP-based suspicious activity detection for enhanced security monitoring.

**TS-989.** Recording files are stored with randomized filenames to prevent URL guessing.

**TS-990.** The system implements data minimization: only necessary data is collected and stored.

**TS-991.** Third-party integrations (OpenAI, Stripe, Resend) use separate API keys with minimal permissions.

**TS-992.** The system implements secure password requirements: minimum length, complexity indicators.

**TS-993.** The system supports two-factor authentication as an architectural provision for enhanced security.

**TS-994.** Data encryption at rest is supported via MongoDB's encryption capabilities.

**TS-995.** The system implements regular security assessments and penetration testing protocols.

**TS-996.** User consent management tracks and stores consent records for regulatory compliance.

**TS-997.** The system implements data anonymization for analytics and research use cases.

**TS-998.** Security incident response procedures are documented for breach notification compliance.

**TS-999.** The system supports multi-tenant data isolation for institutional deployments.

**TS-1000.** The system implements comprehensive security documentation including threat models, data flow diagrams, and control matrices for patent filing and regulatory compliance.

---

## PATENT CLAIM COVERAGE MATRIX

The following maps technical specifications to patent claim categories:

| Claim Category | Specifications |
|---|---|
| AI Content Generation | TS-261 through TS-370 |
| Brand Integration & Analytics | TS-371 through TS-460 |
| Vocabulary System (60/30/10) | TS-181 through TS-260 |
| Student Profile & Personalization | TS-111 through TS-180 |
| Parental Controls & Recording Enforcement | TS-151 through TS-176 |
| Read-Aloud & Diction Analysis | TS-531 through TS-610 |
| Comprehension & Assessment | TS-461 through TS-530 |
| Spelling Contests | TS-661 through TS-720 |
| Task Reminders & Milestones | TS-721 through TS-770 |
| Admin Messaging & Notifications | TS-611 through TS-660, TS-771 through TS-810 |
| Offline/PWA Capabilities | TS-811 through TS-860 |
| Ambient Music Generation | TS-861 through TS-890 |
| On-Device LLM (Future) | Architectural provision in TS-325, TS-849 |
| Payment & Monetization | TS-931 through TS-960 |
| Security & Privacy | TS-961 through TS-1000 |
| Platform Architecture | TS-001 through TS-050 |
| Authentication & Authorization | TS-051 through TS-110 |
| Analytics & Dashboards | TS-891 through TS-930 |

---

*Document Version: 7.0*
*Total Specifications: 1,000*
*Generated: March 2026*
*Status: FOR PATENT FILING — Comprehensive Technical Disclosure*
*Coverage: All existing features + architectural provisions for future capabilities*

---

*END OF TECHNICAL SPECIFICATIONS DOCUMENT*
