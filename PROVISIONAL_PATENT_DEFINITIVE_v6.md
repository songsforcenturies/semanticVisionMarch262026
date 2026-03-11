# UNITED STATES PROVISIONAL PATENT APPLICATION

---

## UNDER 35 U.S.C. Section 111(b)

---

**APPLICATION TYPE:** Provisional Patent Application

**FILING DATE:** March 2026

**INVENTOR:**
Allen Tyrone Johnson
5013 S. Louise Ave #1563
Sioux Falls, SD 57108
United States of America
Email: allen@songsforcenturies.com
Tel: 605-305-3099

**ASSIGNEE:** Allen Tyrone Johnson (Individual Inventor)

---

## THIRD-PARTY TECHNOLOGY DISCLAIMER

The following third-party technologies are used as infrastructure components in the implementation of this invention. No intellectual property claim is made over these technologies; they remain the property of their respective owners:

| Technology | Owner | Usage in System |
|---|---|---|
| OpenAI GPT-5.2 | OpenAI, Inc. | Underlying large language model for narrative generation and assessment evaluation |
| OpenAI Whisper | OpenAI, Inc. | Speech-to-text transcription for read-aloud analysis |
| Stripe | Stripe, Inc. | Payment processing for wallet and brand budget transactions |
| MongoDB | MongoDB, Inc. | Document-oriented database storage |
| React 18 | Meta Platforms, Inc. | Frontend client application framework |
| FastAPI | Sebastian Ramirez | Asynchronous Python backend framework |
| Resend | Resend, Inc. | Transactional email delivery |
| Tailwind CSS | Tailwind Labs | CSS utility framework |
| react-i18next | i18next contributors | Internationalization |
| Shadcn/UI | Shadcn contributors | UI component primitives |
| ReportLab | ReportLab, Inc. | PDF document generation |

**SCOPE OF CLAIMS:** All claims herein protect the novel **METHODS, SYSTEMS, ARCHITECTURES, DATA STRUCTURES, ALGORITHMS, USER INTERFACES, WORKFLOWS, and BUSINESS PROCESSES** created by the inventor. Specifically, the inventions include but are not limited to:

- The concept of dynamically generating personalized educational narratives using AI in which commercial brand products serve as organic problem-solving elements within the story
- The concept of measuring student comprehension of brand-integrated educational content through AI-generated questions and feeding those results back to brands as engagement analytics ("Brand Comprehension")
- The competitive brand bidding and weighted rotation system for story placement within AI-generated educational content
- The 60/30/10 three-tier vocabulary distribution model
- The real-time brand eligibility engine with multi-factor filtering including consent, age, budget, and category gates
- The closed-loop brand analytics pipeline with three-layer narrative discovery
- The four-condition brand activation question identification algorithm
- The Agentic Reach Score formula for holistic vocabulary mastery measurement
- The multi-dimensional student profile system with belief, cultural, strengths, weaknesses, and virtue dimensions
- The consent architecture with default-false opt-in and granular category blocking
- The unified multi-role authentication interface with dynamic credential-type switching
- The affiliate referral engine with configurable rewards and user-facing dashboard
- The guided onboarding framework with role-specific content and tutorial reset
- The 16-level age-calibrated vocabulary complexity system
- The brand opt-out analytics pipeline
- The parental control system with configurable recording enforcement, chapter-threshold gating, and skip/no-skip modes
- The admin-to-user targeted messaging system with audience segmentation and priority levels
- The spelling bee contest engine with timed word-level assessment, per-word scoring, and leaderboard ranking
- The automated task reminder system with pending-task detection and contextual notifications
- The progressive web application (PWA) architecture with service worker registration, offline story caching via IndexedDB, and installability
- The ambient music generation and playback system integrated into the narrative reader
- The notification infrastructure with real-time bell indicator, unread counts, and mark-as-read functionality
- The read-aloud recording and diction analysis pipeline with speech-to-text alignment, multi-dimensional scoring, Audio Memory Library, and Peer Audio Book Section
- The on-device LLM architecture for offline story generation
- The AI-generated video content and brand video integration pipeline
- The lifelong learning continuum from Pre-K through College with historical archive
- All original UI designs, data models, API architectures, algorithms, and business logic
- The overall concept of replacing static, printed educational content with infinite, AI-generated, culturally-aware, faith-aligned, brand-funded personalized educational narratives

---

## TITLE OF THE INVENTION

**System and Method for AI-Generated Personalized Educational Narratives With Brand Comprehension Analytics, Competitive Brand Bidding Engine, Multi-Dimensional Student Profiling Across Belief Systems, Cultural Contexts, and Developmental Characteristics, Three-Tier Vocabulary Distribution, Closed-Loop Brand Engagement Measurement, Parental Control and Recording Enforcement, Administrative Messaging and Spelling Contest Engine, Task Reminder Automation, Progressive Web Application Architecture, Ambient Music Integration, Multi-Stakeholder Platform Architecture, and Affiliate Referral System**

---

## CROSS-REFERENCE TO RELATED APPLICATIONS

This is an original provisional patent application. No prior related applications exist.

---

## INCORPORATED EXHIBITS

The following documents are incorporated by reference as exhibits to this provisional patent application:

1. **TECHNICAL_SPECIFICATIONS_1000.md** -- A comprehensive technical specification document containing 1,000 individually numbered technical specifications (TS-001 through TS-1000) organized across 17 sections, providing exhaustive implementation detail for every subsystem described herein.
2. **Patent Screenshots (Figures 1-31)** -- 31 actual screenshots from a working embodiment of the invention, capturing every major feature including: landing page, authentication interfaces, administrator dashboard with all management tabs (Statistics, Messaging, Spelling Bee, AI Costs, Users, Word Banks, Brands, Affiliates), guardian portal with all tabs (Students, Subscription, Marketplace, Wallet, Invite & Earn, Audio Memories, Audio Books, Progress, FAQ), parental controls configuration panel, student academy with task reminders and story library, narrative reader with read-aloud recording and vocabulary highlighting, spelling bee contests, and mobile-responsive layout.

---

## FIELD OF THE INVENTION

The present invention relates generally to AI-driven educational content generation, and more particularly to:

1. A computer-implemented system and method for dynamically generating personalized, multi-chapter educational narratives using large language models, wherein commercial brand products are integrated into the narrative as organic, problem-solving story elements rather than interstitial advertisements, and wherein the system measures student comprehension of the brand-integrated content through AI-generated questions and provides those comprehension metrics to brand sponsors as closed-loop engagement analytics;

2. A competitive brand marketplace for educational content, wherein multiple brands bid for placement within AI-generated narratives, with a weighted rotation algorithm ensuring proportional exposure based on bid amounts while maintaining cross-category diversity;

3. A platform for replacing static, pre-authored, mass-printed educational reading materials with dynamically generated, infinitely personalized AI content adapted across dimensions including belief systems, cultural heritage, character virtues, personal strengths, areas for growth, and vocabulary acquisition level;

4. A multi-stakeholder educational marketplace connecting parents, students, teachers, brand partners, affiliates, and administrators through role-specific portals with purpose-built capabilities and unified authentication;

5. Novel methods for vocabulary acquisition through tiered distribution within narrative content, age-calibrated complexity across 16 developmental levels, and holistic mastery measurement;

6. A parental control and recording enforcement system that enables guardians to mandate audio and/or video recording during reading sessions, with configurable chapter thresholds, skip/no-skip policies, and automatic recording activation;

7. An administrative communication and engagement platform comprising targeted messaging to user segments and competitive spelling bee contests with timed assessments and leaderboard rankings;

8. A progressive web application architecture enabling offline story caching, service worker-based asset management, and device installability; and

9. An automated task reminder and notification system that detects pending educational activities and delivers contextual reminders to students.

---

## BACKGROUND OF THE INVENTION

### The Problem: Static Education in a Dynamic World

Education, as delivered through printed books and pre-authored digital content, is fundamentally static. A textbook printed in 2025 is identical for every child who reads it, regardless of that child's faith, culture, language, interests, learning style, reading level, or personal challenges. This one-size-fits-all model has persisted for centuries because dynamically creating content personalized across multiple dimensions simultaneously was technically impossible -- until now.

The present invention recognizes that large language models, when directed by a sufficiently rich composite prompt incorporating multiple personalization dimensions, can generate educational narratives that are unique to each student, culturally authentic, faith-aligned, developmentally appropriate, and vocabulary-targeted -- and that this content can be generated on-the-fly, infinitely, at near-zero marginal cost.

This invention further recognizes a previously unexploited economic model: brands that solve real problems for families (educational technology companies, healthy food brands, physical activity products, digital wellness tools) can fund personalized education by having their products appear as organic, problem-solving elements within stories -- not as banner ads or video interruptions, but as integral narrative components that students actually comprehend and engage with. The system then measures that comprehension and reports it back to brands, creating a closed-loop engagement model that is fundamentally different from, and superior to, every existing digital advertising metric.

### The Eight Persistent Failures of Prior Art

**Failure 1: Content Rigidity.** Existing educational platforms (Duolingo, Khan Academy, Reading IQ, ABCmouse, Readability Tutor, Amira Learning, Epic!, Raz-Kids) rely on pre-authored content libraries. While some adjust difficulty levels adaptively, none generate entirely new narrative content personalized simultaneously across belief systems, cultural contexts, character virtues, personal strengths, growth areas, interests, vocabulary tiers, and age-calibrated complexity. Every child receives the same stories, merely re-ordered or difficulty-adjusted.

**Failure 2: Educationally Destructive Monetization.** Digital education monetizes through banner ads (cognitively distracting), video interstitials (narrative-breaking), hard paywalls (creating equity gaps), or subscription gates. No existing system monetizes by integrating brand messages *within* educational content in a way that *adds* educational value. The present invention is the first to create a model where the presence of a brand product in a story is itself an educational element -- teaching the student about a real-world product that solves a real-world problem, with comprehension of that integration measured and reported.

**Failure 3: Absence of Brand Comprehension Measurement.** Even platforms that display advertising provide brands with only surface metrics: impressions, clicks, view-through rates. No existing system: (a) embeds brand products as narrative elements in educational content; (b) generates AI-driven comprehension questions about those elements; (c) measures whether students actually understood and absorbed the brand's presence; and (d) reports those comprehension rates back to brands. The concept of "Brand Comprehension" -- measuring actual cognitive engagement with brand content through educational assessment -- is entirely novel.

**Failure 4: Fragmented Stakeholder Systems.** Existing EdTech platforms serve one or two user types. No platform provides purpose-built portals for six distinct roles (administrators, parents, teachers, students, brand partners, affiliates) with role-specific capabilities, unified authentication, and a shared data ecosystem.

**Failure 5: Cultural and Faith Blindness.** No patented system generates educational narratives simultaneously personalized for specific belief systems (Christianity, Islam, Buddhism, Hinduism, Judaism, Secular Humanism, etc.) and cultural contexts (African American, South Asian, Latin American, etc.) using LLM-driven content generation. Existing AI educational tools treat all students as culturally and spiritually identical.

**Failure 6: No Competitive Brand Marketplace for Education.** No existing system implements a marketplace where brands compete through bidding for placement within AI-generated educational narratives, with weighted rotation algorithms, cross-category diversity constraints, and real-time competition visibility.

**Failure 7: No Parental Recording Enforcement in Digital Reading.** No existing educational reading platform allows parents to mandate that their child record themselves reading aloud as a condition of progressing through content. Existing platforms treat reading as a passive, unobservable activity. The present invention enables parents to enforce accountability by requiring audio or video recordings after configurable chapter thresholds, with the ability to prevent chapter advancement until the recording requirement is satisfied.

**Failure 8: No Integrated Spelling Competition Within AI-Generated Content.** No existing platform combines AI-generated personalized narratives with competitive spelling assessments drawn from the same vocabulary the student is learning in their stories. Existing spelling bee platforms use static, predetermined word lists unrelated to the student's current reading material.

### Analysis of Prior Art

A comprehensive search reveals the following relevant prior art, none of which anticipates or renders obvious the present invention:

**US Patent Application 20250218307 (EZDucate Platform, 2024-2025):** AI system analyzing student data to generate personalized lessons and animated videos using LLMs and diffusion models. **Does not:** (a) integrate brand products as narrative elements, (b) measure brand comprehension through questions, (c) adapt to belief/cultural contexts, (d) implement tiered vocabulary distribution, (e) provide brand engagement analytics, (f) implement competitive brand bidding, (g) generate multi-chapter narratives for vocabulary acquisition, (h) implement parental recording enforcement, (i) implement spelling bee contests.

**CHI 2024 Research (POSTECH/Ewha Womans University):** GPT-4 and Stable Diffusion create personalized storybooks from IoT-monitored home vocabulary. **Does not:** (a) integrate brands, (b) support cultural/belief personalization, (c) implement multi-role access, (d) implement brand marketplace, (e) measure brand comprehension, (f) provide brand analytics, (g) implement parental controls, (h) implement offline caching. Research-only; no commercial implementation.

**US Patent 20250182639 (Personalized Learning Engine):** AI-generated personalized courses with adaptive simulation. **Does not:** (a) generate narrative stories, (b) integrate brand content, (c) support belief/cultural personalization, (d) provide brand engagement analytics, (e) measure brand comprehension, (f) implement recording enforcement.

**US Patent US11217110B2 (Adaptive Learning Assets):** Generates structured learning assets from user data. **Does not:** (a) generate narratives, (b) include brand integration, (c) support cultural/belief personalization, (d) measure brand comprehension, (e) implement parental controls, (f) implement task reminders.

**Google US10108988B2 (Video Ad Creatives):** Serves targeted video advertisements. **Does not:** (a) generate educational content, (b) embed brands within narratives, (c) provide comprehension-based engagement metrics, (d) implement competitive bidding for narrative placement.

### Novelty Statement: What Has Never Existed Before

The present invention introduces the following concepts that have never existed in any prior art, individually or in combination:

1. **Brand Comprehension** -- The measurement of student cognitive engagement with brand-integrated educational content through AI-generated comprehension questions, with results reported to brands as a closed-loop analytics metric.

2. **Brand-as-Narrative-Solution** -- The method of directing an AI to integrate brand products as organic problem-solving elements within educational narratives.

3. **Competitive Brand Bidding for Narrative Placement** -- A marketplace where brands bid for placement within AI-generated stories, with weighted rotation algorithms ensuring proportional exposure.

4. **Multi-Dimensional Student Profiling for Content Generation** -- A system that simultaneously personalizes AI-generated content across 10+ dimensions (belief system, cultural context, interests, virtues, strengths, weaknesses, vocabulary tiers, age, grade, language).

5. **Three-Tier Vocabulary Distribution in AI Narratives** -- The 60/30/10 model ensuring each generated story contains a scientifically-informed mix of reinforcement, growth, and aspiration vocabulary.

6. **Default-False Consent Architecture for Brand Content in Education** -- A system where no child receives brand-integrated content unless their parent/guardian affirmatively opts in, with granular category blocking.

7. **Parental Recording Enforcement with Chapter-Threshold Gating** -- A system where parents can mandate audio/video recording during reading, with configurable chapter thresholds and the ability to block chapter advancement until recording is completed.

8. **Spelling Bee Contest Engine Integrated with AI-Generated Vocabulary** -- A competitive spelling assessment system that draws words from the same vocabulary banks used in the student's personalized AI-generated narratives.

9. **Automated Task Reminder System for Educational Activities** -- A system that automatically detects pending educational tasks (unfinished stories, overdue assessments, recording requirements) and delivers contextual reminders.

10. **The End of Static Educational Content** -- The broader concept that AI-generated, culturally-aware, faith-aligned, brand-funded narratives can replace static, printed educational materials, providing every child with truly personalized reading experiences generated on demand.

---

## SUMMARY OF THE INVENTION

### The Vision

The present invention, commercially embodied as "Semantic Vision," represents a paradigm shift in educational content delivery. Instead of mass-producing identical books for millions of children, the system generates unique, personalized educational narratives for each individual child -- stories that reflect that child's faith, honor that child's cultural heritage, celebrate that child's strengths, gently address that child's growth areas, teach vocabulary at that child's precise developmental level, and feature real-world brands as organic problem-solving elements within the narrative.

### The System

The platform comprises fourteen interconnected pipelines:

**A. Content Generation Pipeline:** A real-time pipeline that (1) assembles a multi-dimensional student profile from 10+ data dimensions; (2) selects vocabulary according to the 60/30/10 three-tier distribution; (3) executes a brand eligibility engine with multi-factor filtering; (4) applies competitive brand selection with weighted bidding and rotation; (5) constructs a composite AI prompt; (6) generates structured multi-chapter educational narratives; (7) records brand impressions and economic data; and (8) generates context-aware comprehension questions.

**B. Brand Comprehension Pipeline:** A novel assessment system that (1) identifies comprehension questions related to brand-integrated content through a four-condition classification algorithm; (2) measures student performance on those specific questions; (3) computes Brand Comprehension Scores representing actual cognitive engagement with brand content; and (4) delivers these scores to brand partners as closed-loop engagement analytics.

**C. Assessment and Mastery Pipeline:** An AI-powered evaluation system that (1) evaluates student vocabulary responses across three dimensions (definition accuracy, contextual usage, spelling quality); (2) tracks mastery at 80% accuracy thresholds; and (3) computes an Agentic Reach Score measuring holistic learning progress.

**D. Closed-Loop Brand Analytics Pipeline:** A multi-layer search and analytics engine that identifies all narratives containing brand content through three-layer discovery (structured data, impression records, full-text search), extracts sentence-level story excerpts, and presents comprehensive engagement analytics.

**E. Competitive Brand Bidding Engine:** A marketplace system where brands compete for narrative placement through bidding, with weighted rotation ensuring proportional exposure, cross-category diversity, rotation tracking, competition visibility, and anonymized opt-out analytics.

**F. Multi-Role Platform Architecture:** A six-tier role-based access control system with purpose-built portals for Administrators, Parents/Guardians, Teachers, Students, Brand Partners, and Affiliates.

**G. Affiliate Referral Engine:** A closed-loop system with auto-generated codes, configurable rewards, user-facing dashboards, and administrative controls.

**H. Guided Onboarding Framework:** Role-specific, skippable onboarding wizards with persistent state management and on-demand reset.

**I. Read-Aloud Recording and Analysis Pipeline:** A system that (1) captures student audio while reading narratives aloud; (2) performs speech-to-text alignment comparing spoken words to the known narrative text; (3) computes multi-dimensional diction scores (pronunciation accuracy, fluency, completeness, prosody); (4) tracks diction improvement longitudinally across multiple sessions; (5) preserves all recordings as an Audio Memory Library for guardians; (6) enables contributed recordings to be shared in a Peer Audio Book Section where children listen to other children reading; and (7) feeds diction analysis back into narrative generation to create targeted pronunciation practice opportunities.

**J. Parental Control and Recording Enforcement Pipeline:** A system that (1) enables guardians to configure mandatory recording rules per student; (2) supports four recording modes (optional, audio-required, video-required, both-required); (3) implements chapter-threshold gating where recording becomes mandatory after a configurable number of chapters; (4) enforces recording requirements in the narrative reader by disabling chapter advancement until recording is completed; (5) supports auto-start recording when a chapter loads; and (6) provides configurable skip/no-skip policies determining whether students can bypass recording requirements.

**K. Administrative Communication and Engagement Pipeline:** A system comprising (1) an admin-to-user targeted messaging system with audience segmentation (all users, guardians, students, teachers, brands), priority levels (normal, important, urgent), and read-tracking per recipient; (2) a notification infrastructure with a real-time bell indicator showing unread message counts, mark-as-read functionality, and message detail views; and (3) a spelling bee contest engine with timed word-level assessments, configurable time limits, per-word scoring with correctness and timing metrics, leaderboard rankings, and automatic contest lifecycle management (upcoming, active, ended).

**L. Task Reminder and Notification Pipeline:** A system that (1) automatically detects pending educational activities for each student, including unfinished narratives, upcoming spelling contests, unread admin messages, and overdue assignments; (2) presents contextual task reminders in the student dashboard with priority indicators and due dates; (3) tracks task completion status; and (4) integrates with the notification bell for cross-cutting awareness.

**M. Progressive Web Application (PWA) Pipeline:** A system that (1) registers a service worker for offline asset caching and background sync; (2) provides a web app manifest enabling device installation (add to home screen); (3) implements IndexedDB-based story caching for offline reading; (4) provides a save-for-offline button within the narrative reader; and (5) maintains an offline library view showing all cached stories with sync status indicators.

**N. Ambient Music Integration Pipeline:** A system that (1) generates or selects ambient background music appropriate to narrative mood and genre; (2) provides a music player integrated into the narrative reader interface; (3) supports play/pause/volume controls without interrupting reading flow; and (4) adapts music selection to the student's cultural context and story theme.

**O. AI-Generated Video and Brand Video Integration Pipeline:** A system that generates AI-produced video content for narrative scenes, embeds brand products visually within generated video, and tracks video brand impressions separately.

**P. On-Device and Multi-Platform Architecture:** A native application with on-device LLM for offline story generation, local data storage, cloud synchronization, and multi-platform deployment.

**Q. Lifelong Learning Continuum:** A system maintaining a continuous educational record from Pre-K through College with automatic complexity recalibration, historical archive, and longitudinal analytics.

---

## BRIEF DESCRIPTION OF THE DRAWINGS

**FIG. 1** (fig01_landing_page.jpeg) -- Landing page showing public-facing interface with "Patent-Pending AI Technology" badge, hero messaging ("If glasses are for your eyes, words are vision for your mind"), 20+ language support badge, and multi-role navigation links (Parent/School Login, Student Login, Teacher Login, Sponsor a Reader, Brand Portal, Become an Affiliate).

**FIG. 2** (fig02_unified_login.jpeg) -- Unified Login Interface with Parent role selected, showing email/password authentication form with role-specific visual theming and four-icon role selector (Parents, Students, Teachers, Brands).

**FIG. 3** (fig03_unified_login_student.jpeg) -- Unified Login Interface with Student role selected, showing Student Code (STU-XXXXXX format) and six-digit PIN authentication form with distinct visual theming.

**FIG. 4** (fig04_guardian_portal.jpeg) -- Administrator Dashboard showing platform-wide statistics, user counts, and management interface.

**FIG. 5** (fig05_admin_brands.jpeg) -- Administrator Brand Management showing brand revenue tracking, impression counts, active brand listing with problem categories and bid amounts, and brand creation interface.

**FIG. 6** (fig06_admin_affiliates.jpeg) -- Administrator Affiliate Management showing program settings (reward type, rates, payout threshold, auto-approve), affiliate listing with codes, referral counts, earned amounts, and pending payouts.

**FIG. 7** (fig07_admin_wordbanks.jpeg) -- Administrator Word Bank Management showing the three-tier vocabulary input system (baseline/target/stretch words with definitions and example sentences).

**FIG. 8** (fig08_guardian_students.jpeg) -- Guardian/Parent Portal showing subscription status, student cards with unique codes (STU-XXXXXX format), PINs, ages, and grade levels. Tab bar showing all portal sections.

**FIG. 9** (fig09_guardian_affiliate.jpeg) -- Guardian/Parent Portal Affiliate Dashboard showing affiliate code (AFF-XXXXXXXX), referral link, Copy Code/Copy Link buttons, statistics grid (Referrals, Total Earned, Pending, Paid Out), and reward rate display.

**FIG. 10** (fig10_guardian_faq.jpeg) -- Guardian/Parent FAQ Tab showing expandable accordion interface with context-specific FAQ items.

**FIG. 11** (fig11_affiliate_signup.jpeg) -- Public Affiliate Signup Page showing registration form with name/email fields and benefit cards (Earn Per Referral, Help Families Learn, Track Your Impact).

**FIG. 12** (fig12_admin_statistics.jpeg) -- Administrator Statistics Dashboard showing platform-wide metrics: total users, active subscriptions, revenue, narrative generation counts, AI cost tracking, and user growth trends.

**FIG. 13** (fig13_admin_messaging.jpeg) -- Administrator Messaging System showing message composition form with Subject, Body, Target Audience selector (All Users, Guardians, Students, Teachers, Brands), Priority Level selector (Normal, Important, Urgent), and Send button. Full tab navigation visible: Statistics, Word Banks, AI Costs, Brands, Users, Coupons, Contests, Plans, Billing/ROI, Features, Affiliates, Audio Books, Messaging, Spelling Bee, LLM Config, App Settings.

**FIG. 14** (fig14_admin_spelling_bee.jpeg) -- Administrator Spelling Bee Contest Management showing contest creation form with Title, Description, Word List, Time Limit, Start/End Date fields, and listing of existing contests with participant counts and status indicators (Upcoming, Active, Ended).

**FIG. 15** (fig15_admin_ai_costs.jpeg) -- Administrator AI Cost Tracking Dashboard showing per-generation cost breakdown by model, total token usage (input/output), generation success rates, and cost optimization analytics.

**FIG. 16** (fig16_admin_users.jpeg) -- Administrator User Management showing Plan Membership Overview (Total Parents: 68, With Plans: 20, No Plan: 48, Total Students: 8), subscription tier breakdown (Free: 16, Starter: 2, Academy: 1, Family: 1), Create New User form, and Delegate Admin Privileges section.

**FIG. 17** (fig17_guardian_students_overview.jpeg) -- Guardian/Parent Portal Students Tab showing Family Plan subscription status (Active, 4/5 students), Student Seats progress bar (80%), "+ Add Student" button, and student cards displaying: student name, Student Code (STU-XXXXXX with copy button), PIN (6-digit with copy button), age, grade level, interests, virtues, Mastered vocabulary count, Word Banks count, Edit/Delete buttons, Assign Word Banks, Reset PIN, Spellcheck/Phonetic/Brand Stories toggle buttons, and collapsible "Reading Rules" parental controls section.

**FIG. 18** (fig18_parental_controls.jpeg) -- Parental Controls "Reading Rules" Panel expanded showing: Recording Requirement selector with four options (Optional, Audio Required, Video Required, Both Required) with "Optional" currently selected and highlighted, Chapter Threshold setting ("Require recording after this many chapters, 0 = every chapter"), Auto-Start Recording toggle ("Recording starts automatically when chapter opens"), and Require Confirmation toggle ("Student must confirm before they can proceed"). Multiple student cards visible with different virtues (Patience, Anger, Trustworthiness, Unity, Justice, Delayed Gratification).

**FIG. 19** (fig19_wallet.jpeg) -- Guardian/Parent Wallet showing Account Balance ($1,000.02), Add Funds section with preset amounts ($5.00, $10.00, $25.00, $50.00, $100.00), "+ Select An Amount" custom amount button, "Powered by Stripe. Secure card payments, Google Pay, Apple Pay" badge, and Redeem Coupon input field with Redeem button.

**FIG. 20** (fig20_marketplace.jpeg) -- Word Bank Marketplace showing searchable word bank catalog with category filter (All Categories), wallet balance ($1,000.02), Create Word Bank button, and word bank cards displaying: bank name, category badges (Academic, Professional, Science), description, word count, rating, user count, price (Free or $4.99), Preview button, and Add to Library/Buy buttons. Example banks: "3000 Core Words" (3065 words, Free), "Aviation Essentials" (10 words, $4.99), "College/Post-College" (284 words, Free).

**FIG. 21** (fig21_subscription.jpeg) -- Subscription Management showing current subscription (Family Plan, Active, 4/5 students), Redeem Coupon or Invitation Code section, and Available Plans comparison: Starter ($3.99/mo), Family ($9.99/mo, Current Plan highlighted), Academy ($19.99/mo).

**FIG. 22** (fig22_audio_memories.jpeg) -- Audio Memories Library showing per-student filter tabs for recording playback, chronological recording list with student name, narrative title, chapter, date, diction scores, and play/download controls.

**FIG. 23** (fig23_audio_books.jpeg) -- Peer Audio Book Collection showing community-contributed recordings organized by story, reader age, and rating with playback controls.

**FIG. 24** (fig24_invite_earn.jpeg) -- Invite & Earn system showing March Madness Referral Blitz contest (Grand Prize: $200 Amazon Gift Card + 1 Year Premium, 2nd Place: $100 Gift Card, 3rd Place: 6 Months Premium, countdown timer showing 21d 16h left), Referral Code (REF-THYT3T), "$5.00 wallet credit" for both referrer and friend.

**FIG. 25** (fig25_student_progress.jpeg) -- Student Progress Dashboard showing all four children (SJ: Age 8, 9 mastered, Score 93.3, Target 4000; PJ: Age 11, 0 mastered, Score 0, Target 7500; TJ: Age 14, 30 mastered, Score 100, Target 15000; DJ: Age 10, 0 mastered) with "View Progress" buttons and Biological Vocabulary Targets.

**FIG. 26** (fig26_student_academy.jpeg) -- Student Academy Dashboard (student SJ logged in) showing Spelling Bee and Offline tabs, notification bell with unread count (2), and the personalized academy interface.

**FIG. 27** (fig27_student_stories.jpeg) -- Student Story Library showing AI-generated personalized story cards with progress indicators, chapter completion status, and continue reading buttons.

**FIG. 28** (fig28_student_spelling_bee.jpeg) -- Student Spelling Bee View showing available contests (TEST_Spelling_Bee_Contest: 5 words, 120s limit, 1 participant; March Spelling Bee: 10 words, 120s limit, 0 participants) with "Start" buttons, YOUR TASKS section showing "Continue SJ's Cosmic Race at 40%" and "Spelling Bee: March Spelling Bee waiting", stats cards (Vocabulary Mastered: 9, Target: 4000 words; Agentic Reach Score: 93, Initiate level; Reading Time: 26m, 61.4 WPM average), and Join Classroom input for 6-digit teacher code.

**FIG. 29** (fig29_narrative_reader.jpeg) -- Narrative Reader (NarrativeReader component) showing an AI-generated personalized story "SJ and the Star Dash" with the chapter header, "Read This Chapter Aloud" recording button at the top, the actual story narrative text featuring the student's name (SJ) as the protagonist, chapter navigation, and reading controls.

**FIG. 30** (fig30_story_text.jpeg) -- Narrative Reader Chapter Content showing the full AI-generated story text with personalized characters (SJ and Mia), virtue modeling (patience, teamwork, managing anger), culturally relevant setting, "Tap any word to see its definition" instruction, VOCABULARY section with tier-coded word badges ("orbit", "constellation", "gravity"), and chapter navigation buttons (Previous, Complete Story).

**FIG. 31** (fig31_mobile_landing.jpeg) -- Mobile-Responsive Landing Page (390x844 viewport) demonstrating the fully responsive mobile layout with "Patent-Pending AI Technology" badge, hero text, "Your child can learn in 20+ languages" badge, Start Free and Parent/School Login buttons, and navigation links. Confirms mobile-first design implementation.

*Note: All 31 figures are actual screenshots from a working embodiment of the invention captured from the live application at https://learning-portal-v1.preview.emergentagent.com. The referenced JPEG files accompany this application as exhibits.*

---

## DETAILED DESCRIPTION OF THE PREFERRED EMBODIMENTS

### 1. System Architecture Overview

The preferred embodiment comprises a distributed computing system:

**1.1 Backend Application Server.** A Python-based asynchronous web server built on FastAPI, providing RESTful API endpoints for all operations. Implements role-based access control using JWT for six user roles: Administrator, Guardian/Parent, Teacher, Student, Brand Partner, Affiliate. All requests processed asynchronously via Python's async/await pattern.

**1.2 Database Layer.** MongoDB document-oriented database accessed via Motor async driver. Collections include: users, students, word_banks, brands, brand_offers, brand_campaigns, brand_impressions, narratives, read_logs, written_answers, affiliates, affiliate_referrals, wallets, wallet_transactions, coupons, referral_codes, referral_contests, system_config, audio_recordings, parental_controls, messages, spelling_contests, spelling_submissions, tasks.

**1.3 AI Engine.** A Large Language Model integration layer (default: OpenAI GPT-5.2, configurable per admin) used for: (a) multi-chapter narrative generation with brand integration, (b) student response evaluation, and (c) contextual word definition generation. Abstracted behind a configurable service layer allowing model substitution without code changes.

**1.4 Speech Recognition Engine.** OpenAI Whisper integration for speech-to-text transcription of read-aloud recordings, enabling text-audio alignment and diction scoring.

**1.5 Frontend Client.** React 18 SPA with role-specific portals. Supports 20+ languages via react-i18next. Multi-currency display via IP-based geolocation and real-time exchange rates (50+ currencies). Built with Shadcn/UI component primitives, Tailwind CSS utility framework, and Sonner toast notifications.

**1.6 Payment Layer.** Stripe API integration for wallet top-ups, brand budget funding, and word bank purchases via Checkout sessions.

**1.7 Email Layer.** Resend API for password resets, email verification, affiliate confirmation with personalized links, and referral notifications.

**1.8 Progressive Web Application Layer.** Service worker registration for offline asset caching, web app manifest for device installability, and IndexedDB for local story persistence.

### 2. Multi-Dimensional Student Profile Assembly

Each student profile comprises 10+ personalization dimensions, all contributing to content generation:

**2.1 Demographic.** Name, age, grade level (16 levels: Pre-K through Adult).

**2.2 Interest Graph.** Student interests (e.g., "soccer," "robots," "cooking") used to theme narratives. Stories set in worlds the child cares about.

**2.3 Character Education Virtues.** 32 selectable virtues (Patience, Kindness, Honesty, Courage, Responsibility, Respect, Perseverance, Gratitude, Self-Control, Generosity, Humility, Empathy, Forgiveness, Fairness, Trustworthiness, Teamwork, Compassion, Integrity, Loyalty, Wisdom, Creativity, Diligence, Optimism, Resilience, Self-Discipline, Tolerance, Mindfulness, Adaptability, Curiosity, Independence, Cooperation, Determination). Students may select unlimited virtues. AI models these through character behavior and plot resolution.

**2.4 Emotional Intelligence Categories.** 30 predefined emotional categories (Joy, Love, Hope, Pride, Contentment, Excitement, Wonder, Confidence, Calm, Belonging, Sadness, Anger, Fear, Anxiety, Frustration, Loneliness, Jealousy, Embarrassment, Disappointment, Guilt, Grief, Confusion, Surprise, Sympathy, Trust, Awe, Relief, Nostalgia, Determination-Emotion, Acceptance). Students may select unlimited emotions. The AI weaves emotional intelligence themes into narrative character development.

**2.5 Belief System.** Identifier (Christianity, Islam, Buddhism, Hinduism, Judaism, Secular Humanism, etc.) directing AI to reflect consistent values, moral frameworks, and worldview. The system never proselytizes or denigrates other systems.

**2.6 Cultural Context.** Identifier (African American, South Asian, Latin American, East Asian, Middle Eastern, etc.) directing AI to incorporate authentic names, settings, traditions, foods, celebrations, and customs.

**2.7 Language.** 20+ languages supported. The entire narrative including titles, content, vocabulary explanations, and questions is generated in the student's preferred language.

**2.8 Strengths Description.** Free-text, guardian-authored. The AI celebrates these as protagonist superpowers.

**2.9 Growth Areas Description.** Free-text, guardian-authored. The AI models growth through empathetic character development. Explicitly prohibits shame, punishment, or deficit framing.

**2.10 Advertising Preferences.** Two critical fields:
- `allow_brand_stories` (Boolean, **default: false**): No student receives brand content without affirmative parental consent.
- `blocked_categories` (List): Granular category blocking.

**2.11 Vocabulary State.** Assigned word banks, mastered vocabulary tokens (normalized lowercase, 80% accuracy threshold), and Agentic Reach Score.

**2.12 Parental Control Settings.** Recording mode, chapter threshold, auto-start, skip policy, and confirmation requirements (detailed in Section 26).

### 3. Three-Tier Vocabulary Distribution System (60/30/10 Model)

Each narrative is generated with a scientifically-informed vocabulary mix:

**3.1 Word Banks.** Each bank contains three tiers: `baseline_words` (known/reinforcement), `target_words` (growth-level), `stretch_words` (aspirational).

**3.2 Distribution.** Words selected per narrative:
- **60% Baseline (up to 18 words):** Reinforcement. High familiarity builds confidence and fluency.
- **30% Target (up to 9 words):** Primary learning objective. AI provides in-narrative context clues.
- **10% Stretch (up to 3 words):** Aspiration. Exposure to advanced language.

**3.3 Mastered-Word Exclusion.** Words already in `mastered_tokens` are excluded, ensuring continuous vocabulary expansion.

**3.4 Randomization.** Tier pools are shuffled using random selection, ensuring non-repeating sequences across stories.

### 4. Age-Calibrated Vocabulary Complexity (16 Levels)

Every element of the generated narrative adheres to grade-specific complexity:

| Level | Sentence Length | Vocabulary | Narrative Style |
|---|---|---|---|
| Pre-K (3-4) | 3-5 words | Sight words, simple CVC | Action sequences, repetitive patterns |
| Kindergarten (5-6) | 5-8 words | Common sight words | Short stories, clear cause-effect |
| Grade 1 (6-7) | 6-10 words | Dolch sight words | Beginning chapters |
| Grade 2 (7-8) | 8-12 words | Grade-level, basic figurative | Developing plot complexity |
| Grades 3-4 (8-10) | 10-15 words | Multi-syllable, context clues | Multi-chapter with subplots |
| Grades 5-6 (10-12) | 12-18 words | Academic, literary devices | Complex character development |
| Grades 7-8 (12-14) | 15-20 words | Abstract, domain-specific | Multiple perspectives, ethical dilemmas |
| Grades 9-10 (14-16) | 15-25 words | SAT-prep, complex syntax | Sophisticated themes, symbolism |
| Grades 11-12 (16-18) | 18-30 words | AP-level, nuanced argumentation | Literary analysis depth |
| College (18+) | 20-35 words | Discipline-specific | Academic discourse |
| Adult | Unlimited | Professional/technical | Professional context |

### 5. Brand Eligibility Engine (Real-Time Multi-Factor Filtering)

At every content generation request, the system executes a filtering pipeline:

**5.1 System Feature Gate.** Global flag (`brand_sponsorship_enabled`). If disabled, no brands included.
**5.2 Guardian Consent Gate.** Checks `allow_brand_stories` field. Defaults to `false`.
**5.3 Active Brand Filter.** Only brands with `is_active == true`.
**5.4 Age Appropriateness.** Brand `target_ages` checked against student age.
**5.5 Budget Check.** `budget_spent < budget_total`.
**5.6 Category Block Filter.** Brand categories cross-referenced against guardian blocked categories.
**5.7 Problem Category Grouping.** Eligible brands grouped by `problem_category`.
**5.8 Competitive Selection.** The Bidding Engine (Section 6) selects from each category.
**5.9 Dynamic Composition.** Every narrative has a potentially unique brand composition.

### 6. Competitive Brand Bidding and Weighted Rotation Engine

**6.1 Problem Category Taxonomy.** Each brand assigned a `problem_category`.
**6.2 Bid Amount.** Each brand has a `bid_amount` (float, default $0.05/impression).
**6.3 Weighted Rotation Algorithm:**
```
weights = [brand_1.bid_amount, ..., brand_N.bid_amount]
P(brand_i) = brand_i.bid_amount / sum(weights)
selected_brand = weighted_random_choice(brands, probabilities)
```
**6.4 Cross-Category Diversity.** At most one brand per problem category per narrative.
**6.5 Rotation Count.** Atomically incremented per selection.
**6.6 Priority Sorting.** Selected brands sorted by bid amount descending.
**6.7 Competition Visibility.** Brands see their competitors, bid positions, and stats.
**6.8 Opt-Out Analytics.** Anonymized guardian consent rates by age group and category.

### 7. Composite AI Prompt Construction

The system synthesizes all dimensions into a single LLM prompt:

**7.1** Student profile (name, age, grade, interests)
**7.2** Tiered vocabulary with tier labels, definitions, example sentences
**7.3** Virtue modeling directives per selected virtue
**7.4** Emotional intelligence themes per selected emotion
**7.5** Belief system alignment directive
**7.6** Cultural context integration directive
**7.7** Language directive (entire narrative in specified language)
**7.8** Brand integration directive
**7.9** Strengths celebration directive
**7.10** Growth areas empathy directive (prohibit shame/deficit framing)
**7.11** Age-calibrated complexity specifications
**7.12** Structural requirements: 5 chapters, 300-500 words each, embedded vocabulary tokens with tier annotations, one comprehension question per chapter with 4 options and correct index
**7.13** Output JSON schema for deterministic parsing

### 8. AI Story Generation, Post-Processing, and Impression Economics

**8.1 LLM Invocation.** Prompt sent to configured LLM. System records: model name, input tokens, output tokens, duration, cost.
**8.2 Validation.** Response parsed as JSON. Structural integrity verified.
**8.3 Persistence.** Narrative stored with chapters, vocabulary annotations, comprehension questions, and brand placement metadata.
**8.4 Brand Impression Recording.** For each integrated brand, atomically: creates impression record, increments brand counters, debits brand budget, increments rotation_count.

### 9. Brand Comprehension: The Novel Measurement of Cognitive Brand Engagement

**This section describes the core novel contribution of the present invention.**

"Brand Comprehension" is defined herein as the measurable degree to which a student has cognitively engaged with and understood brand-integrated content within an AI-generated educational narrative.

**9.1 Brand Comprehension Question Identification (Four-Condition Algorithm).**
- **Condition A (Direct Mention):** Question text or answer option contains brand/product name.
- **Condition B (Category + Chapter):** Product category keyword in question AND question from brand-containing chapter.
- **Condition C (Product Derivatives):** Answer options contain derivatives of product names.
- **Condition D (Contextual Proximity):** Question keywords appear proximate to brand mentions.

A question is classified as a Brand Comprehension question if it satisfies **any** of these four conditions.

**9.2 Brand Comprehension Score Computation.**
```
Brand Comprehension Score = (total_correct_on_brand_questions / total_attempts_on_brand_questions) * 100
```

**9.3 Brand Comprehension Analytics Dashboard.** Brand partners receive: Brand Comprehension Score, total questions generated, total attempts, per-question breakdown, story excerpts, unique student reach, average comprehension scores.

**9.4 Why Brand Comprehension Changes Everything.** A Brand Comprehension Score of 85% means 85% of students understood the brand's role in solving a character's problem. This is fundamentally different from a 0.3% click-through rate on a banner ad.

### 10. Three-Layer Narrative Discovery for Brand Analytics

**10.1 Layer 1 (Structured Data):** Queries `brand_placements` array.
**10.2 Layer 2 (Impression Records):** Queries `brand_impressions` collection.
**10.3 Layer 3 (Full-Text Search):** Case-insensitive search across chapter content.
**10.4 Deduplication.** Results deduplicated across all three layers.
**10.5 Excerpt Extraction.** Up to 5 sentence-level excerpts per chapter.

### 11. Student Assessment Pipeline

**11.1** Sequential chapter presentation with per-chapter comprehension questions.
**11.2** Vocabulary assessment after narrative completion for target/stretch words.
**11.3** AI-powered evaluation on three dimensions: definition accuracy, contextual usage, spelling quality.
**11.4** Written answer evaluation for free-text responses on 0-100 scale.
**11.5** Mastery tracking at 80%+ accuracy threshold.
**11.6 Agentic Reach Score:**
```
ARS = min((|mastered_tokens| * 10 + completed_narratives * 50) / max(total_narratives * 50, 1) * 100, 100.0)
```

### 12. Consent Architecture and Privacy Controls

**12.1 Default-False Consent.** `allow_brand_stories` defaults to `false`.
**12.2 Granular Category Blocking.** Guardians add categories to `blocked_categories`.
**12.3 Age Filtering.** Brands automatically excluded if target ages don't match.
**12.4 Budget-Limited Exposure.** Exhausted-budget brands excluded.
**12.5 Student Auth Isolation.** Students use code/PIN (not email/password).
**12.6 Anonymized Analytics.** Opt-out data reported as aggregates only.

### 13. Multi-Role Platform Architecture

| Role | Portal | Capabilities |
|---|---|---|
| Administrator | Admin Dashboard | User CRUD, word bank management, contest creation, billing config, LLM selection, feature flags, brand approval, affiliate program management, analytics, subscription plans, coupons, brand linking, messaging, spelling bee management |
| Guardian/Parent | Guardian Portal | Student management (wizard), word bank assignment/purchase, wallet/Stripe top-up, referral program/leaderboard, progress monitoring, ad preference controls, subscription, marketplace, offers, affiliate dashboard, parental controls, FAQ |
| Teacher | Teacher Portal | Classroom sessions, real-time WebSocket reading, student tracking, session codes, word bank browsing |
| Student | Student Academy | Story reading, vocabulary assessments, written comprehension, progress tracking, classroom joining, spelling bees, task reminders, notifications |
| Brand Partner | Brand Portal | Profile/logo, product catalog, campaigns, story preview, impression analytics, Brand Comprehension dashboard, story integration browser, offers, budget top-up, competition visibility |
| Affiliate | Guardian Portal (Tab) | Code/link display, copy-to-clipboard, stats, reward rate, referral history |

### 14. Affiliate Referral System

**14.1 Public Signup.** Dedicated page. Auto-generates AFF-XXXXXX code. Confirmation email.
**14.2 Configurable Rewards.** Admin sets: reward type, amounts, minimum payout, auto-approve.
**14.3 Registration-Integrated Tracking.** URL parameter triggers tracking pipeline.
**14.4 User-Facing Dashboard.** Active/pending badge, code, link, 4-metric stats grid.
**14.5 Post-Signup Instructions.** Success page with login button.
**14.6 Admin Controls.** Settings config, affiliate listing, approval, deactivation, payout recording.

### 15. Guided Onboarding Framework

**15.1 First-Login Detection.** localStorage key per-user, per-portal.
**15.2 Role-Specific Content.** Guardian (5 steps), Brand (5 steps), Student (4 steps).
**15.3 Skippable.** Progress bar, step counter, back/next, skip/dismiss.
**15.4 Tutorial Reset.** Removes localStorage key, forces component remount.

### 16. Unified Multi-Role Authentication

**16.1 Role Selector.** Four-icon selector (Parents, Students, Teachers, Brands).
**16.2 Dynamic Form Switching.** Role selection changes fields, theme, titles, button text, footer links, placeholders without page reload.
**16.3 Unified Registration.** Three-role selector, dynamic fields, referral code support.
**16.4 Legacy Redirects.** Old routes redirect to unified interface.

### 17. Additional Core Innovations

**17.1 Multi-Step Student Creation Wizard.** Four+ steps: Basic Info, Virtues & Emotions, Strengths/Weaknesses, Preferences.
**17.2 Real-Time Classroom Sessions.** WebSocket-based with teacher-generated codes.
**17.3 Wallet System.** Balance tracking, transaction history, Stripe Checkout top-ups, referral rewards, coupon redemptions.
**17.4 Coupon Engine.** Unique codes, percentage/fixed amounts, wallet credits, usage limits, expiration.
**17.5 Multi-Currency.** IP-based geolocation, real-time exchange rates, 50+ currencies.
**17.6 Brand Promotional Offers.** Create, display, toggle/dismiss, interaction tracking.
**17.7 Contextual FAQ.** Role-specific curated FAQ in accordion interface.
**17.8 Word Bank Ecosystem.** Admin public banks, guardian private banks, marketplace, purchase workflows.
**17.9 Referral Contests.** Time-bound with live leaderboard.

### 18. Biological Vocabulary Target System

**18.1 Developmental Target Mapping.** Age-mapped vocabulary targets (age 3 = 500 words through age 20+ = 50,000 words).
**18.2 Target Computation.** Per-student biological vocabulary target based on age.
**18.3 Mastery Percentage.** `(mastered_tokens_count / biological_target) * 100` for age-normalized progress.
**18.4 Progress Report Integration.** Displayed in student progress cards and guardian dashboards.

### 19. AI-Powered Contextual Word Definition

**19.1 On-Demand Vocabulary Assistance.** Student or guardian requests AI-generated definition for any word.
**19.2 Contextual Enhancement.** Surrounding sentence context included for context-specific definitions.
**19.3 Structured Response.** Definition, part of speech, example sentence, pronunciation hint, synonyms.

### 20. Student Progress Export System

**20.1 Multi-Format Export.** JSON data or printable HTML report.
**20.2 Comprehensive Report Content.** Profile data, biological target, reading statistics, vocabulary mastered, virtues, assessment history, story history, word banks.
**20.3 Print-Ready Design.** Print-optimized CSS with "Print / Save as PDF" button.

### 21. Brand Story Preview System

**21.1 Preview Generation.** Brand partners generate sample narratives without real student profile.
**21.2 Integration Demonstration.** Uses actual product catalog for realistic preview.
**21.3 Campaign Optimization.** Enables brands to refine before committing budgets.

### 22. Donation and Reader Sponsorship

**22.1 Community Funding Model.** Any user can donate to fund story generation for others.
**22.2 Cost-Based Calculation.** System calculates narratives fundable per donation.
**22.3 Educational Equity.** Community-funded model for disadvantaged students.

### 23. Classroom Sponsorship by Brands

**23.1 Brand-Funded Classrooms.** Brand partners sponsor entire classrooms.
**23.2 Aggregate Analytics.** Sponsors receive classroom-level Brand Comprehension analytics.

### 24. Configurable AI Model Selection

**24.1 Provider Abstraction.** Provider-agnostic interface supporting multiple LLM providers.
**24.2 Administrator Control.** Admin selects active model through settings interface.
**24.3 Cost and Quality Tracking.** Each generation logs the model used.

### 25. Subscription Plan Management

**25.1 Flexible Plan Creation.** Configurable parameters: price, student seat limits, word bank access, features.
**25.2 Self-Service Upgrade.** Guardians browse and upgrade subscriptions.

### 26. Parental Control and Recording Enforcement System

**This section describes a novel system for enabling parental oversight and accountability enforcement within a digital educational reading platform.**

**26.1 Recording Mode Configuration.** The system provides guardians with four recording mode options:
- **Optional:** Recording is available but never required. The student chooses whether to record.
- **Audio Required:** The student must submit an audio recording of themselves reading the chapter aloud before advancing.
- **Video Required:** The student must submit a video recording of themselves reading before advancing.
- **Both Required:** Both audio and video recordings must be submitted.

**26.2 Chapter Threshold Gating.** The guardian configures a `chapter_threshold` integer (0-5) that determines the chapter at which recording becomes mandatory. A threshold of 0 means recording is required for every chapter. A threshold of 3 means recording is required starting from chapter 3 onward. This allows students to begin reading freely and only face recording requirements as they progress deeper into the narrative.

**26.3 Auto-Start Recording.** When enabled, the recording interface opens automatically when a chapter loads that meets the recording threshold. This eliminates the need for the student to manually activate the recorder.

**26.4 Skip/No-Skip Policy.** The guardian configures whether the student can bypass the recording requirement:
- When `can_skip_recording` is **true**, the student sees the recording prompt but can dismiss it and proceed.
- When `can_skip_recording` is **false**, the "Finish Chapter" button is disabled (visually indicated by reduced opacity and a not-allowed cursor) until a recording is submitted. A warning banner reads "Complete the recording above before you can finish this chapter."

**26.5 Require Confirmation.** When enabled, the student must explicitly confirm before proceeding past a recording checkpoint, adding an additional accountability layer.

**26.6 UI Enforcement in Narrative Reader.** The narrative reader computes two boolean states at each chapter:
- `mustRecord = isRecordingRequired AND meetsThreshold` -- whether the current chapter requires recording
- `canProceed = NOT mustRecord OR recordingDone OR can_skip_recording` -- whether the Finish button should be enabled

A purple informational banner displays "Audio/Video recording required by parent" when recording is mandated.

**26.7 Recording Completion Callback.** When a recording is successfully submitted, the system:
- Sets `recordingDone` to true, enabling the Finish Chapter button
- Displays a success toast with the diction score percentage
- Resets `recordingDone` to false when the student navigates to a new chapter

**26.8 Per-Student Configuration.** Parental controls are stored per student, allowing different rules for different children within the same guardian's account (e.g., stricter requirements for a younger child).

**26.9 API Architecture.**
- `GET /api/students/{student_id}/parental-controls` -- Retrieves current settings (public endpoint for student portal).
- `PUT /api/students/{student_id}/parental-controls` -- Updates settings (authenticated, guardian-only).

**26.10 Guardian Portal UI.** The ParentalControlsPanel component provides an expandable "Reading Rules" section within each student card in the guardian portal, with toggle switches for boolean settings (auto-start, require confirmation, can skip) and a numeric input for chapter threshold.

### 27. Administrative Messaging System

**This section describes a novel system for one-to-many administrative communication within the educational platform.**

**27.1 Message Composition.** Administrators create messages with:
- **Subject:** Brief title for the message
- **Body:** Full message content
- **Target Audience:** Selectable from: all users, guardians only, students only, teachers only, brands only
- **Priority Level:** Normal, Important, or Urgent

**27.2 Message Distribution.** Messages are stored centrally and delivered to all users matching the target audience. The system does not create individual copies per user; instead, it queries messages relevant to the user's role at read time.

**27.3 Read Tracking.** Each user maintains a `read_notifications` array of message IDs they have read. The system computes unread counts as: total matching messages minus messages in the user's read list.

**27.4 Mark-as-Read.** When a user views a message, a `POST /api/messages/{message_id}/read` request adds the message ID to their `read_notifications` array.

**27.5 Message Retrieval.** `GET /api/messages` returns all messages matching the authenticated user's role, ordered by timestamp descending, with a `read` boolean per message computed from the user's read list.

**27.6 API Architecture.**
- `POST /api/admin/messages` -- Create message (admin-only)
- `GET /api/messages` -- Retrieve messages for current user
- `POST /api/messages/{message_id}/read` -- Mark message as read

### 28. Notification Bell Infrastructure

**28.1 Real-Time Indicator.** A NotificationBell component in the application header displays a bell icon with a red badge showing the count of unread messages.

**28.2 Unread Count Computation.** The bell queries the messages endpoint and counts messages where `read == false` for the current user.

**28.3 Dropdown Panel.** Clicking the bell opens a dropdown showing recent messages with subject, priority indicator, and timestamp. Unread messages are visually distinguished.

**28.4 Navigation.** Clicking a message in the dropdown navigates to the full message detail view and marks the message as read.

**28.5 Cross-Portal Support.** The NotificationBell is integrated into the AppShell component, making it available across all portal types (guardian, student, admin, teacher, brand).

### 29. Spelling Bee Contest Engine

**This section describes a novel competitive spelling assessment system integrated with the AI-generated vocabulary ecosystem.**

**29.1 Contest Creation.** Administrators create spelling bee contests with:
- **Title and Description:** Contest name and rules
- **Word List:** Array of words to be tested (drawn from platform word banks or custom entries)
- **Start and End Dates:** Contest time boundaries
- **Time Limit:** Minutes allowed for the entire contest

**29.2 Contest Lifecycle Management.**
- **Upcoming:** Contest is visible but start date has not arrived; participation is locked.
- **Active:** Current date is between start and end; students can participate.
- **Ended:** End date has passed; no new submissions accepted; final results displayed.

**29.3 Timed Assessment.** When a student begins a spelling contest:
- A countdown timer starts based on the configured time limit
- Words are presented one at a time
- The student types the spelling of each word
- Time remaining is displayed prominently
- Contest auto-submits when time expires

**29.4 Per-Word Scoring.** Each word response is scored for:
- **Correctness:** Exact match against the correct spelling (case-insensitive)
- **Time Taken:** Milliseconds from word presentation to response submission
- A combined score rewards both accuracy and speed

**29.5 Submission and Scoring.** Upon completion:
- The system computes: total correct, total attempted, accuracy percentage, total time
- Results are stored in the `spelling_submissions` collection
- The student receives immediate feedback showing correct/incorrect per word

**29.6 Leaderboard Ranking.** Students are ranked by:
- Primary: Number of correct answers (descending)
- Secondary: Total time (ascending, for tiebreaking)
- The leaderboard is publicly viewable within the student portal for active and ended contests

**29.7 API Architecture.**
- `POST /api/admin/spelling-contests` -- Create contest (admin-only)
- `GET /api/spelling-contests` -- List active/upcoming contests
- `GET /api/spelling-contests/{id}` -- Contest detail with leaderboard
- `POST /api/spelling-contests/{contest_id}/submit` -- Submit results

**29.8 Integration with Vocabulary System.** Contest words can be drawn from the platform's three-tier word bank system, creating a direct connection between a student's daily vocabulary learning and competitive assessment.

### 30. Task Reminder System

**This section describes a novel automated system for detecting and presenting pending educational activities to students.**

**30.1 Pending Task Detection.** The system automatically identifies pending tasks for each student:
- **Unfinished Narratives:** Stories where `status != "completed"` (partially read stories)
- **Available Spelling Contests:** Active contests the student has not yet participated in
- **Unread Messages:** Admin messages the student has not yet read
- **Overdue Assignments:** Any tasks with past due dates

**30.2 Task Categories.** Each detected task is categorized with:
- **Title:** Human-readable description (e.g., "Continue Reading: The Adventure Begins")
- **Description:** Context about the task
- **Due Date:** When applicable (e.g., spelling contest end date)
- **Priority:** Computed from urgency (overdue = high, upcoming = medium, informational = low)
- **Type:** Enum (reading, contest, message, assignment)

**30.3 Dashboard Integration.** The TaskReminders component is prominently placed in the Student Academy dashboard, showing:
- Count of pending tasks
- Task cards with title, description, priority badge, and due date
- Action buttons to navigate directly to the relevant activity

**30.4 Completion Tracking.** Tasks are automatically removed from the reminder list when:
- A narrative is completed (all 5 chapters read with passing comprehension)
- A spelling contest submission is recorded
- A message is marked as read

**30.5 API Architecture.**
- `GET /api/tasks` -- Returns computed pending tasks for the authenticated student

### 31. Progressive Web Application (PWA) Architecture

**31.1 Service Worker Registration.** The application registers a service worker at application startup, enabling:
- Offline asset caching (HTML, CSS, JavaScript, images)
- Background sync for queued operations
- Push notification support (architectural provision)

**31.2 Web App Manifest.** A `manifest.json` file defines:
- Application name and short name
- Theme and background colors matching the application's visual identity
- Display mode (standalone) for app-like experience
- Icon set for home screen installation
- Start URL and scope

**31.3 Installability.** The combination of service worker and manifest enables the "Add to Home Screen" prompt on supported browsers and devices, allowing the application to be installed as a native-like app.

**31.4 IndexedDB Story Caching.** The `offlineCache.js` module provides:
- `saveStoryOffline(narrative)` -- Stores a complete narrative in IndexedDB
- `getOfflineStories()` -- Retrieves all cached stories
- `removeOfflineStory(id)` -- Removes a specific cached story
- `isStoryOffline(id)` -- Checks if a story is cached

**31.5 Save-for-Offline Button.** The `SaveOfflineButton` component within the NarrativeReader allows students to cache the current story for offline reading with a single tap. Visual feedback confirms the save operation.

**31.6 Offline Library.** The `OfflineLibrary` component in the Student Academy displays all locally cached stories with:
- Story title and chapter count
- Cached date
- Delete from cache option
- Sync status indicator

### 32. Ambient Music Integration

**32.1 Music Player Component.** The `MusicPlayer` component is integrated into the NarrativeReader interface, providing:
- Play/pause toggle
- Volume control
- Track display

**32.2 Genre-Appropriate Selection.** The music system selects ambient tracks appropriate to:
- The narrative's genre (adventure, mystery, fantasy, etc.)
- The student's cultural context
- The current chapter's mood (tension, resolution, discovery)

**32.3 Non-Intrusive Integration.** The music player is positioned in the reader header alongside the reading timer and chapter indicator, accessible without interrupting the reading experience.

**32.4 User Control.** Students can enable/disable music at any time. The preference is persisted per session.

### 33. Read-Aloud Recording and Diction Analysis System

**33.1 Recording Activation.** When a student begins reading, the ReadAloudRecorder component provides an option to record. The recorder is positioned at the top of the chapter view for maximum visibility.

**33.2 Speech-to-Text Alignment.** Recorded audio is processed through OpenAI Whisper for transcription, then aligned word-by-word against the known narrative text.

**33.3 Multi-Dimensional Diction Scoring.**
- **Pronunciation Accuracy (0-100):** Percentage of words correctly pronounced
- **Fluency (0-100):** Smoothness, pacing, absence of unnatural pauses
- **Completeness (0-100):** Percentage of narrative words spoken
- **Prosody (0-100):** Intonation, rhythm, stress patterns, expressiveness

**33.4 Composite Reading Proficiency Score.** Four diction scores combined with vocabulary mastery and comprehension scores.

**33.5 Audio Memory Library.** All recordings preserved chronologically, tagged with student name, age, narrative title, date, and diction scores. Parents can play back recordings from months or years earlier.

**33.6 Peer Audio Book Section.** Guardians who opt in contribute recordings to a shared library. Other students browse and listen to peer narrations organized by story, reader age, and rating.

**33.7 Diction Improvement Tracking.** Time-series diction scores with improvement rates per dimension. Persistent pronunciation challenges identified and fed back into narrative generation for targeted practice.

**33.8 Video Recording.** Optional video recording alongside audio, capturing the student's face and expressions.

**33.9 Configurable Recording Settings.** Audio format (AAC, MP3, OPUS), video format (H.264, H.265), quality/resolution with storage estimates.

### 34. On-Device Architecture and Offline Story Generation

**34.1 Native Multi-Platform Application.** Deployable on iOS, Android, macOS, Windows, ChromeOS.

**34.2 On-Device LLM.** Compressed, quantized LLM deployed locally for complete privacy, offline functionality, low-latency generation, and accessibility in connectivity-limited areas.

**34.3 Dual-Mode Operation.** Seamless switching between online (cloud LLM) and offline (on-device LLM) modes.

**34.4 Local Data Storage.** All student data stored locally with configurable storage allocation.

**34.5 Cloud Synchronization.** Automatic sync when connectivity available.

**34.6 Export Capabilities.** Download, email sharing, cloud upload, external storage export.

### 35. AI-Generated Video Content in Stories

**35.1 Scene Identification.** AI identifies chapters benefiting from video storytelling.
**35.2 Video Prompt Construction.** Incorporates scene descriptions, cultural context, brand products.
**35.3 Video Generation.** AI video generation engine produces 10-30 second clips.
**35.4 Brand Integration in Video.** Brand products visually represented as organic story elements.
**35.5 Multimedia Reader.** Integrated text-and-video presentation with synchronized navigation.

### 36. Lifelong Learning Continuum (Pre-K through College)

**36.1 Developmental Span.** Single continuous record from Pre-K (age 3, ~500 word target) through College (age 22+, ~50,000 word target).
**36.2 Automatic Recalibration.** All parameters recalibrate as student ages.
**36.3 Historical Archive as Touchstone in Time.** Every narrative, assessment, recording, and milestone preserved.
**36.4 Longitudinal Analytics.** Multi-year trend dashboards for vocabulary growth, reading fluency, comprehension progression.

---

## CLAIMS

### Independent Claims

**Claim 1.** A computer-implemented method for generating personalized educational content with integrated brand product placements and Brand Comprehension measurement, comprising:

(a) receiving, by a processor, a content generation request for a student;

(b) retrieving a student profile comprising at least: age, grade level, interests, belief system identifier, cultural context identifier, language preference, guardian-authored strengths description, guardian-authored growth areas description, advertising preferences including a brand content opt-in flag defaulting to false and a blocked categories list, assigned word bank identifiers, and mastered vocabulary tokens;

(c) retrieving vocabulary from assigned word banks, each bank comprising three tiers: baseline, target, and stretch words;

(d) selecting vocabulary according to a tiered distribution of approximately 60% baseline, 30% target, and 10% stretch words, excluding previously mastered words;

(e) executing a real-time brand eligibility engine comprising: checking a system feature flag, verifying guardian consent (opt-in flag must be true), querying active brands, filtering by age appropriateness, budget availability, and blocked categories;

(f) applying competitive brand selection wherein eligible brands are grouped by problem category and selected using a weighted random algorithm with selection probabilities proportional to bid amounts, with cross-category diversity enforcement and rotation count tracking;

(g) constructing a composite prompt for a Large Language Model incorporating the student profile, tiered vocabulary with definitions, belief system alignment directive, cultural context integration directive, language directive, age-calibrated complexity specifications, virtue modeling directives, emotional intelligence themes, strengths celebration directive, growth areas empathy directive, and for each selected brand a directive to integrate the brand's products as organic problem-solving narrative elements;

(h) transmitting the prompt to the LLM and receiving a structured response comprising multi-chapter educational narrative with vocabulary annotations and per-chapter comprehension questions;

(i) storing the narrative with all content, annotations, questions, and brand placement metadata;

(j) atomically recording brand impressions and updating brand counters and budgets;

(k) presenting the narrative to the student and collecting responses to comprehension questions;

(l) identifying Brand Comprehension questions -- questions whose content relates to brand-integrated narrative elements -- using a multi-condition classification algorithm; and

(m) computing Brand Comprehension metrics from student performance on identified Brand Comprehension questions, and providing those metrics to brand partners as closed-loop engagement analytics.

**Claim 2.** A computer-implemented method for measuring Brand Comprehension within AI-generated educational content, comprising:

(a) receiving an analytics request from a brand partner;

(b) identifying all educational narratives containing brand content using a three-layer search: querying structured brand placement data, querying brand impression records, and performing full-text search of narrative content for brand and product names;

(c) for each identified narrative, extracting sentence-level text excerpts containing brand or product mentions;

(d) identifying Brand Comprehension questions using a four-condition classification:
   (i) Condition A: question text or answer options contain brand or product name;
   (ii) Condition B: product category keyword in question AND question from chapter containing brand content;
   (iii) Condition C: answer options contain derivatives of product names;
   (iv) Condition D: question keywords appear proximate to brand mentions in chapter;

(e) for each Brand Comprehension question, tallying total attempts, correct responses, and incorrect responses;

(f) computing a Brand Comprehension Score as the ratio of correct responses to total attempts on Brand Comprehension questions;

(g) computing summary statistics: total stories, total mentions, total Brand Comprehension questions, total attempts, overall pass rate, unique students, average comprehension score; and

(h) presenting the Brand Comprehension analytics to the brand partner through a dedicated dashboard.

**Claim 3.** A computer-implemented system for generating personalized, brand-integrated educational content with Brand Comprehension analytics, comprising:

(a) a database storing multi-dimensional student profiles, three-tier word banks, brand records with bid amounts and problem categories, generated narratives with brand placement metadata, parental control configurations, administrative messages, spelling contest records, and task definitions;

(b) a student profile assembly module;

(c) a vocabulary selection module implementing 60/30/10 distribution with mastered-word exclusion;

(d) a brand eligibility engine with multi-factor filtering (consent, age, budget, category);

(e) a competitive brand bidding module with weighted random selection, cross-category diversity, and rotation tracking;

(f) a prompt construction module synthesizing all personalization dimensions into a composite LLM prompt;

(g) an AI generation module invoking a configurable LLM and parsing structured responses;

(h) an impression recording module atomically creating records and updating counters;

(i) a Brand Comprehension identification module applying a four-condition classification to identify brand-related comprehension questions;

(j) a Brand Comprehension analytics module computing per-question and aggregate comprehension scores and presenting them to brand partners;

(k) a parental control module enabling guardians to configure and enforce recording requirements per student;

(l) an administrative messaging module for targeted one-to-many communication with audience segmentation;

(m) a spelling contest module for timed, competitive vocabulary assessments with leaderboard ranking; and

(n) a task reminder module for automated detection and presentation of pending educational activities.

**Claim 4.** A computer-implemented method for managing a competitive brand marketplace within AI-generated educational content, comprising:

(a) maintaining brand records with problem categories and bid amounts;

(b) at each content generation for an authorized student, executing competitive selection: grouping eligible brands by problem category, computing selection probabilities proportional to bid amounts within each category, selecting one brand per category via weighted random selection, enforcing maximum brand count per narrative, sorting by bid for placement priority;

(c) atomically incrementing rotation counts;

(d) providing competition visibility to brands showing competitors, bid positions, impressions, and rotations; and

(e) providing anonymized opt-out analytics showing guardian consent behavior by age group and category.

**Claim 5.** A computer-implemented method for generating personalized educational narratives adapted to student belief systems and cultural contexts, comprising:

(a) receiving belief system and cultural context identifiers as part of a student profile;

(b) constructing directives for an LLM specifying: the belief system with instructions to reflect consistent values, moral frameworks, and worldview without proselytizing; and the cultural context with instructions to incorporate authentic names, settings, traditions, celebrations, foods, and customs;

(c) incorporating these directives into a composite prompt that simultaneously includes vocabulary tiers, age-calibrated complexity, interest theming, virtue modeling, emotional intelligence themes, and strengths/weaknesses adaptation;

(d) generating a multi-chapter narrative that simultaneously reflects all specified personalization dimensions; and

(e) generating comprehension questions that assess the student's understanding of narrative content, including content adapted to the specified cultural and belief dimensions.

**Claim 6.** A computer-implemented method for managing an affiliate referral program with a user-facing dashboard within an educational platform, comprising:

(a) receiving affiliate registration with name and email;

(b) generating a unique affiliate code and sending confirmation with code, referral link, and reward rate;

(c) during new user registration, detecting and validating an affiliate code in a URL parameter;

(d) upon validation, atomically recording the referral, incrementing counters, calculating reward, and updating balances;

(e) providing a user-facing affiliate dashboard within an existing portal, displaying: active/pending status, affiliate code and referral link with copy functionality, statistics grid (referrals, earned, pending, paid out), reward rate, and referral history; and

(f) providing administrative controls for reward configuration, affiliate approval, and payout management.

**Claim 7.** A computer-implemented method for dynamically replacing static educational reading materials with AI-generated, personalized educational narratives, comprising:

(a) maintaining a student profile with multiple personalization dimensions including at least belief system, cultural context, developmental level, interests, character virtues, emotional intelligence categories, personal strengths, growth areas, and vocabulary acquisition state;

(b) at each content request, dynamically generating a unique multi-chapter educational narrative using a Large Language Model directed by a composite prompt incorporating all personalization dimensions simultaneously;

(c) incorporating commercially-sponsored brand products as organic, problem-solving narrative elements within the generated content;

(d) distributing vocabulary across the narrative according to a tiered system with reinforcement, growth, and aspiration tiers;

(e) calibrating narrative complexity to the student's developmental level across a multi-level system;

(f) generating per-chapter comprehension questions for assessment;

(g) measuring student vocabulary mastery through AI-powered evaluation; and

(h) providing each student with a continuously expanding library of personalized narratives that evolve as the student grows.

**Claim 8.** A computer-implemented method for providing a unified multi-role authentication interface for an educational platform, comprising:

(a) displaying a role selector with distinct visual indicators for multiple user roles;

(b) upon role selection, dynamically modifying without page reload: form fields (email/password for adults, code/PIN for students), color theme, title/subtitle, button text, footer links, and placeholders;

(c) processing authentication through role-appropriate verification; and

(d) providing automatic redirects from legacy role-specific URLs.

**Claim 9.** A computer-implemented method for enforcing parental recording requirements within an AI-generated educational narrative reading platform, comprising:

(a) providing a parental control configuration interface wherein a guardian selects, for each student, a recording mode from a set comprising at least: optional, audio-required, video-required, and both-required;

(b) receiving from the guardian a chapter threshold integer specifying the chapter number at or after which recording becomes mandatory;

(c) receiving from the guardian a skip policy flag indicating whether the student can bypass the recording requirement;

(d) storing the recording mode, chapter threshold, and skip policy as parental control settings associated with the specific student;

(e) at each chapter presentation within the narrative reader, computing whether the current chapter meets the recording threshold by comparing the chapter number to the stored threshold;

(f) when the chapter meets the threshold and recording is required, displaying a recording interface with visual indicators that recording is mandated by the parent;

(g) when the skip policy prohibits skipping, disabling the chapter advancement control (the "Finish Chapter" button) until a recording is submitted, thereby preventing the student from progressing through the narrative without fulfilling the recording requirement;

(h) upon recording submission, enabling the chapter advancement control and displaying a success notification; and

(i) resetting the recording completion state when the student navigates to a subsequent chapter.

**Claim 10.** A computer-implemented method for conducting competitive spelling assessments within an AI-generated educational platform, comprising:

(a) receiving, by a processor, a spelling contest definition comprising a word list, a time limit, start and end dates, and descriptive metadata;

(b) managing a contest lifecycle with at least three states: upcoming (visible but locked), active (accepting submissions), and ended (no new submissions);

(c) presenting the word list to participating students one word at a time with a countdown timer;

(d) collecting the student's typed spelling for each word and recording the time taken per word;

(e) scoring each response for correctness via case-insensitive exact match against the correct spelling;

(f) computing an aggregate score comprising at least: total correct answers, total attempted, accuracy percentage, and total time;

(g) storing the submission with per-word results and aggregate scores;

(h) computing a leaderboard ranking students by primary key of correct answers descending and secondary key of total time ascending; and

(i) presenting the leaderboard to all participating students.

**Claim 11.** A computer-implemented method for providing targeted administrative messaging with notification tracking within an educational platform, comprising:

(a) receiving from an administrator a message comprising subject, body, target audience identifier (specifying one or more user roles), and priority level;

(b) storing the message in a central collection without creating per-recipient copies;

(c) upon a user requesting their messages, querying all messages matching the user's role, computing a read status per message by checking the user's read notification list against message identifiers;

(d) displaying unread message count via a notification bell indicator in the application header;

(e) upon user viewing a message, recording the message identifier in the user's read notification list; and

(f) presenting messages in reverse chronological order with visual distinction between read and unread states and priority level indicators.

### Dependent Claims

**Claim 12.** The method of Claim 1, wherein the brand content opt-in flag defaults to false for every newly created student profile, requiring affirmative guardian action before any brand content appears.

**Claim 13.** The method of Claim 1, wherein the strengths celebration directive instructs the LLM to showcase guardian-authored strengths through protagonist abilities and achievements.

**Claim 14.** The method of Claim 1, wherein the growth areas empathy directive instructs the LLM to model growth through empathetic character development, explicitly prohibiting shame, punishment, or deficit framing.

**Claim 15.** The method of Claim 1, further comprising computing an Agentic Reach Score using a formula combining mastered vocabulary count and completed narrative count relative to total narratives.

**Claim 16.** The method of Claim 1, wherein the age-calibrated complexity specifications comprise a system spanning pre-kindergarten through adult (16 or more levels), each specifying sentence length range, vocabulary complexity, and narrative style.

**Claim 17.** The method of Claim 2, wherein the three-layer search ensures comprehensive discovery of narratives generated both before and after implementation of structured tracking metadata.

**Claim 18.** The method of Claim 2, further comprising extracting significant individual words from multi-word product names as additional search terms.

**Claim 19.** The method of Claim 2, further comprising providing brand partners with full narrative text access with visual indicators marking brand-containing paragraphs.

**Claim 20.** The method of Claim 2, further comprising aggregating free-text written student responses with evaluation scores for brand partners' qualitative analysis.

**Claim 21.** The method of Claim 4, wherein the weighted random selection probability for each brand within a category is: P(brand_i) = bid_amount_i / sum(bid_amount_j for all j in category).

**Claim 22.** The method of Claim 4, further comprising sorting selected brands by bid amount descending, with highest bidder receiving primary narrative integration.

**Claim 23.** The method of Claim 4, further comprising a competition visibility API returning competitors, bid amounts, impression counts, rotation counts, and relative positions.

**Claim 24.** The method of Claim 4, further comprising treating brands with empty target age arrays as having universal age eligibility.

**Claim 25.** The method of Claim 5, wherein the belief system directive directs the LLM to generate character behaviors, moral lessons, and resolution patterns consistent with the specified belief system.

**Claim 26.** The method of Claim 5, wherein the cultural context directive directs the LLM to incorporate culturally relevant character names, geographic settings, holiday celebrations, traditional foods, and social customs.

**Claim 27.** The method of Claim 6, wherein the affiliate code format comprises a fixed prefix "AFF-" followed by a randomly generated alphanumeric string.

**Claim 28.** The method of Claim 6, wherein non-affiliate users accessing the dashboard see a call-to-action directing them to the public signup page.

**Claim 29.** The method of Claim 6, wherein the post-signup success page displays login instructions and a direct navigation button.

**Claim 30.** The method of Claim 7, wherein the system generates all narrative content including titles, chapter text, vocabulary explanations, and comprehension questions in any of 20 or more languages based on student preference.

**Claim 31.** The method of Claim 7, further comprising a multi-step student profile creation wizard presenting profile creation across four or more discrete steps to reduce cognitive load.

**Claim 32.** The method of Claim 7, wherein the student profile includes unlimited selectable character virtues from a predefined list of 32 or more virtues and unlimited selectable emotional intelligence categories from a predefined list of 30 or more categories.

**Claim 33.** The system of Claim 3, further comprising a cost logging module recording for each AI generation: model name, input tokens, output tokens, duration, cost, and success status.

**Claim 34.** The system of Claim 3, further comprising a guided onboarding module with role-specific step content, persistent client-side state, skip/dismiss capability, and on-demand tutorial reset.

**Claim 35.** The system of Claim 3, further comprising a real-time classroom module with WebSocket connections, teacher-generated session codes, synchronized chapter progression, and real-time response collection.

**Claim 36.** The system of Claim 3, further comprising a digital wallet system with balance tracking, Stripe Checkout top-ups, referral rewards, coupon redemptions, and transaction history.

**Claim 37.** The system of Claim 3, further comprising a coupon engine with unique codes, percentage/fixed discount types, wallet credit amounts, usage limits, and expiration dates.

**Claim 38.** The system of Claim 3, further comprising a brand promotional offers module with offer creation, guardian-facing display with toggle/dismiss controls, and interaction tracking.

**Claim 39.** The system of Claim 3, further comprising a multi-currency module using IP-based geolocation, real-time exchange rates, cached rates, and display in 50+ currencies.

**Claim 40.** The system of Claim 3, further comprising a contextual FAQ module with role-specific curated content in an interactive accordion interface.

**Claim 41.** The system of Claim 3, further comprising a word bank ecosystem with admin public banks, guardian private banks, marketplace discovery, and wallet-based purchase workflows.

**Claim 42.** The system of Claim 3, further comprising a referral contest module with configurable time bounds, prize descriptions, live leaderboard, and automatic expiration.

**Claim 43.** The method of Claim 1, wherein vocabulary assessment evaluates three dimensions: definition accuracy, contextual usage, and spelling quality in a configurable mode (exact match or phonetic approximation).

**Claim 44.** The method of Claim 1, wherein mastery is determined at an 80% accuracy threshold, and mastered words are stored as normalized lowercase tokens.

**Claim 45.** The method of Claim 7, wherein generated narrative content is funded by brand sponsors whose products appear as organic story elements, creating an economic model where personalized education is provided to students at reduced or no cost.

**Claim 46.** The method of Claim 7, wherein the system maintains a record of all narratives generated for each student, forming a continuously expanding personalized library.

**Claim 47.** The method of Claim 1, further comprising a Biological Vocabulary Target system that:
(a) maintains a mapping of student ages to scientifically-derived expected vocabulary counts;
(b) computes a target vocabulary count for each student based on their age;
(c) presents the target alongside actual mastered vocabulary count for gap analysis; and
(d) uses the Biological Vocabulary Target as a denominator in mastery percentage calculations.

**Claim 48.** The system of Claim 3, further comprising an AI-powered contextual word definition module wherein:
(a) a student requests a definition for any word encountered within a narrative;
(b) the system transmits the word with narrative context to a Large Language Model;
(c) the LLM returns a structured response comprising definition, part of speech, example sentence, pronunciation hint, and synonyms; and
(d) the definition is presented inline within the reading interface.

**Claim 49.** The system of Claim 3, further comprising a student progress export module that:
(a) aggregates all student data including vocabulary mastery, reading statistics, assessment history, and narrative completion records;
(b) generates a formatted, printable HTML progress report; and
(c) supports export in multiple formats including JSON and browser-printable HTML.

**Claim 50.** The system of Claim 3, further comprising a brand story preview module wherein:
(a) a brand partner requests a preview narrative using their product catalog without a real student profile;
(b) the system generates a sample narrative demonstrating organic brand integration; and
(c) the brand partner can review and adjust before committing budgets.

**Claim 51.** The system of Claim 3, further comprising a donation and reader sponsorship module creating a community-funded educational equity model.

**Claim 52.** The system of Claim 3, further comprising a classroom sponsorship module where brand partners fund entire classrooms and receive aggregate Brand Comprehension analytics.

**Claim 53.** The system of Claim 3, further comprising a configurable AI model selection module with provider-agnostic interface, administrator control, and cost/quality tracking.

**Claim 54.** The system of Claim 3, further comprising an administrative subscription plan management module with configurable parameters, guardian self-service upgrade, and plan limit enforcement.

**Claim 55.** The method of Claim 9, wherein the parental control configuration further comprises an auto-start recording flag that, when enabled, causes the recording interface to open automatically when a chapter meeting the threshold loads.

**Claim 56.** The method of Claim 9, wherein the parental control configuration further comprises a require-confirmation flag that, when enabled, requires the student to explicitly confirm before proceeding past a recording checkpoint.

**Claim 57.** The method of Claim 9, wherein the recording completion callback displays a success notification including the computed diction score percentage for the recording.

**Claim 58.** The method of Claim 9, wherein parental controls are stored per individual student, allowing different recording rules for different children within the same guardian account.

**Claim 59.** The method of Claim 9, wherein the visual indicator of recording requirement comprises a colored banner within the chapter view stating that recording is required by the parent.

**Claim 60.** The method of Claim 9, wherein the disabled chapter advancement control displays with reduced visual opacity and a not-allowed cursor, accompanied by a warning message instructing the student to complete the recording.

**Claim 61.** The method of Claim 10, wherein contest words are drawn from the platform's three-tier word bank system, creating a direct connection between daily vocabulary learning and competitive assessment.

**Claim 62.** The method of Claim 10, wherein the per-word scoring includes both correctness (binary) and response time (milliseconds), enabling combined accuracy-speed ranking.

**Claim 63.** The method of Claim 10, wherein the contest auto-submits when the countdown timer expires, preventing indefinite test-taking.

**Claim 64.** The method of Claim 10, wherein the leaderboard is publicly viewable within the student portal for both active and ended contests.

**Claim 65.** The method of Claim 11, wherein the target audience identifier supports at least: all users, guardians only, students only, teachers only, and brand partners only.

**Claim 66.** The method of Claim 11, wherein the priority level comprises at least: normal, important, and urgent, with each priority rendered with distinct visual styling in the notification interface.

**Claim 67.** The method of Claim 11, wherein the notification bell indicator is integrated into a shared application header component accessible across all portal types.

**Claim 68.** The method of Claim 11, further comprising a dropdown panel accessible from the notification bell showing recent messages with subject, priority indicator, timestamp, and read/unread visual distinction.

**Claim 69.** The system of Claim 3, further comprising a progressive web application module with:
(a) a service worker for offline asset caching;
(b) a web app manifest enabling device installation;
(c) IndexedDB-based story caching for offline reading;
(d) a save-for-offline button within the narrative reader; and
(e) an offline library view showing cached stories with sync status.

**Claim 70.** The system of Claim 3, further comprising an ambient music module integrated into the narrative reader with genre-appropriate selection, play/pause/volume controls, and cultural context adaptation.

### Read-Aloud Recording, Audio Analysis, and Audio Memory System Claims

**Claim 71.** A computer-implemented method for recording, analyzing, and preserving student read-aloud sessions within an AI-generated personalized educational narrative platform, comprising:

(a) presenting, on a computing device, an AI-generated educational narrative to a student;

(b) activating an audio recording module that captures the student's voice as the student reads the narrative text aloud;

(c) transmitting the recorded audio to a speech recognition and analysis engine;

(d) performing text-audio alignment by comparing the recognized speech output against the known narrative text, identifying: correctly pronounced words, mispronounced words, omitted words, inserted words, and hesitation patterns;

(e) computing a diction score comprising at least:
   (i) a pronunciation accuracy score measuring the percentage of words correctly pronounced at the phoneme level;
   (ii) a fluency score measuring smoothness, pacing, and absence of unnatural pauses;
   (iii) a completeness score measuring the percentage of narrative words that were spoken; and
   (iv) a prosody score measuring intonation, rhythm, and expressiveness;

(f) storing the recorded audio, the computed scores, and the text-audio alignment data as a read-aloud session record associated with the student, the specific narrative, and a timestamp;

(g) maintaining a chronological history of all read-aloud sessions for each student, enabling longitudinal analysis of diction improvement over time;

(h) presenting diction improvement trends to the student's guardian; and

(i) generating a composite reading proficiency assessment by combining the diction scores with vocabulary mastery data and comprehension question performance.

**Claim 72.** The method of Claim 71, further comprising an Audio Memory Library wherein all recorded read-aloud audio sessions are preserved as a persistent, chronologically organized collection with playback, export, and download capabilities.

**Claim 73.** The method of Claim 71, further comprising a Peer Audio Book Section wherein guardians opt in to contribute recordings to a shared library, creating a community-driven audio book ecosystem narrated by children.

**Claim 74.** The method of Claim 71, further comprising a diction improvement analytics module identifying persistent pronunciation challenges and feeding them back into narrative generation for targeted practice.

**Claim 75.** The method of Claim 71, further comprising a video recording module capturing the student's face and expressions during reading, stored alongside audio in the Memory Library.

### On-Device and Multi-Platform Claims

**Claim 76.** A computer-implemented system for generating personalized educational narratives on a local computing device without requiring network connectivity, comprising:

(a) a native application installable on tablets, smartphones, laptop computers, desktop computers, and educational devices;

(b) an on-device Large Language Model configured to generate multi-chapter educational narratives incorporating student profile personalization, tiered vocabulary distribution, and brand integration directives;

(c) a local data store maintaining student profiles, word banks, narratives, recordings, and assessment history;

(d) an offline content generation module invoking the on-device LLM without transmitting data to external servers;

(e) a synchronization module for cloud sync when connectivity is available; and

(f) a storage management module with configurable options for local allocation, cloud backup, export, and compression format selection.

**Claim 77.** The system of Claim 76, further comprising a multi-platform deployment architecture with cross-device synchronization and platform-optimized on-device LLM models.

### AI-Generated Video Content and Brand Video Integration Claims

**Claim 78.** A computer-implemented method for generating and integrating AI-produced video content within personalized educational narratives, comprising:

(a) identifying scenes or chapters benefiting from visual storytelling;
(b) constructing video generation prompts with scene descriptions, cultural context, and brand products;
(c) generating video clips via AI video generation engine;
(d) embedding clips within corresponding chapters;
(e) presenting combined text-and-video narrative in an integrated reader; and
(f) tracking video viewing as a distinct engagement metric.

**Claim 79.** The method of Claim 78, further comprising brand integration within generated video content with contextually appropriate visual representation, distinct impression tracking, and measurable Brand Comprehension from video content.

### Lifelong Learning and Historical Archive Claims

**Claim 80.** The method of Claim 7, further comprising a lifelong learning continuum system with:
(a) continuous educational record from pre-kindergarten through college;
(b) automatic parameter recalibration as the student ages;
(c) preserved historical archive of all narratives, assessments, recordings, and milestones;
(d) personal "touchstone in time" feature; and
(e) longitudinal analytics dashboard with multi-year trends.

**Claim 81.** The method of Claim 80, wherein the lifelong learning continuum covers the full developmental spectrum from ~500 word Pre-K target through ~50,000 word College/Adult target.

### Media Storage and Export Claims

**Claim 82.** The system of Claim 76, further comprising a media management module with configurable compression formats, multiple export mechanisms, cloud-independent access, and storage analytics.

### Future Embodiment Claims

The following claims describe additional embodiments contemplated and within the scope of this disclosure:

**Claim 83.** The method of Claim 1, further comprising an AI-generated illustration module with culturally-appropriate chapter illustrations.

**Claim 84.** The method of Claim 7, further comprising a text-to-speech narration module with selectable voices, synchronized word highlighting, and adjustable speed.

**Claim 85.** The method of Claim 7, further comprising an adaptive mid-narrative difficulty adjustment module with real-time comprehension monitoring and automatic complexity recalibration.

**Claim 86.** The system of Claim 3, further comprising an augmented reality (AR) story experience module with 3D character/setting rendering and interactive brand product displays.

**Claim 87.** The system of Claim 3, further comprising a gamification and achievement module with badges, experience points, level progressions, and anonymized leaderboards.

**Claim 88.** The system of Claim 3, further comprising a parent-child shared reading module with synchronized sessions, annotations, and collaborative comprehension.

**Claim 89.** The method of Claim 2, further comprising a brand A/B testing module with variant assignment, comparative Brand Comprehension measurement, and optimization selection.

**Claim 90.** The method of Claim 7, further comprising a sign language companion module supporting multiple sign language systems (ASL, BSL).

**Claim 91.** The method of Claim 7, further comprising a seasonal and temporal content adaptation module incorporating current events filtered through the student's cultural/belief profile.

**Claim 92.** The system of Claim 3, further comprising a family shared narrative module where multiple students within the same guardian account appear as distinct characters in a single narrative.

**Claim 93.** The method of Claim 1, further comprising an offline reading module with local caching, queued responses, and offline progress tracking.

**Claim 94.** The method of Claim 1, further comprising a guardian notification module with real-time milestone notifications via push, email, or in-app messaging.

**Claim 95.** The method of Claim 2, further comprising a brand visual placement module with AI-generated illustrations containing brand products and distinct visual impression tracking.

### Task Automation and Intelligent Reminder Claims

**Claim 96.** The method of Claim 1, further comprising an automated task detection module that:
(a) periodically scans the student's activity history to identify: unfinished narratives, available but unparticipated spelling contests, unread administrative messages, and overdue educational assignments;
(b) generates task objects with computed priority levels based on urgency (overdue tasks receiving highest priority);
(c) presents tasks in the student dashboard with actionable navigation links; and
(d) automatically removes tasks upon completion detection.

**Claim 97.** The system of Claim 3, further comprising an integrated PDF generation module that compiles patent documents, progress reports, and intellectual property disclosures from platform data into portable document format files using automated layout and formatting.

**Claim 98.** The method of Claim 7, further comprising a multi-format content delivery system that presents the same AI-generated narrative as: interactive web reader, downloadable PDF, offline-cached PWA content, and peer-shared audio book.

---

## ABSTRACT

A computer-implemented system and method for generating AI-driven personalized educational narratives with integrated Brand Comprehension measurement, replacing static printed educational materials with infinite, dynamically generated content spanning from pre-kindergarten through college. The system assembles multi-dimensional student profiles (belief system, cultural context, interests, 32 character virtues, 30 emotional intelligence categories, strengths, weaknesses, vocabulary level, biological vocabulary targets) and generates unique multi-chapter educational stories using a Large Language Model, with vocabulary distributed across a novel 60/30/10 three-tier system (reinforcement/growth/aspiration) calibrated across 16 developmental levels. Commercial brand products are integrated as organic, problem-solving narrative elements through a competitive bidding marketplace where brands grouped by problem category compete via weighted rotation algorithms. The system introduces "Brand Comprehension" -- a novel metric measuring students' cognitive engagement with brand content through a four-condition question classification algorithm, delivering comprehension scores to brand partners as closed-loop analytics.

The system implements a parental control and recording enforcement pipeline enabling guardians to mandate audio/video recording during reading with configurable chapter thresholds and skip/no-skip policies. An administrative messaging system provides targeted one-to-many communication with audience segmentation, priority levels, and notification bell tracking. A spelling bee contest engine enables timed competitive vocabulary assessments with per-word scoring and leaderboard rankings. An automated task reminder system detects pending educational activities and presents contextual reminders.

A read-aloud recording and analysis system captures students reading narratives aloud, performs text-audio alignment, computes multi-dimensional diction scores (pronunciation accuracy, fluency, completeness, prosody), tracks diction improvement over time, and preserves recordings in an Audio Memory Library. A Peer Audio Book Section allows children to listen to other children's narrations. The system supports progressive web application architecture with service worker-based offline caching, IndexedDB story persistence, and device installability. An ambient music integration provides genre-appropriate background music during reading.

The system supports on-device deployment with a local LLM for offline story generation on tablets, phones, and computers, with configurable media compression and cloud synchronization. AI-generated video content with brand integration is embedded within narratives. A lifelong learning continuum maintains a historical archive from pre-K through college, serving as a personal educational touchstone in time. The platform implements six-tier role-based access, guardian-controlled default-false consent, affiliate referral engine, guided onboarding, real-time classroom sessions, donation-funded reader sponsorship, and multi-currency support.

---

## OATH/DECLARATION

I hereby declare that all statements made herein of my own knowledge are true and that all statements made on information and belief are believed to be true; and further that these statements were made with the knowledge that willful false statements and the like so made are punishable by fine or imprisonment, or both, under 18 U.S.C. 1001 and that such willful false statements may jeopardize the validity of the application or any patent issued thereon.

**Signature:** ____________________________________

**Date:** ____________________________________

**Printed Name:** Allen Tyrone Johnson

**Address:** 5013 S. Louise Ave #1563, Sioux Falls, SD 57108

---

## APPENDIX A: KEY DATA MODEL SCHEMAS

### A.1 Student Profile
```json
{
  "id": "UUID", "full_name": "string", "age": "integer",
  "grade_level": "enum(pre-k..adult)",
  "interests": ["string"], "virtues": ["string (unlimited, from 32 predefined)"],
  "emotions": ["string (unlimited, from 30 predefined)"],
  "strengths": "string (guardian-authored)", "weaknesses": "string (guardian-authored)",
  "belief_system": "string", "cultural_context": "string", "language": "string",
  "assigned_banks": ["bank_id"],
  "ad_preferences": { "allow_brand_stories": "boolean (default: false)", "blocked_categories": ["string"] },
  "mastered_tokens": ["string (normalized lowercase)"], "agentic_reach_score": "float (0-100)",
  "spelling_mode": "enum(exact, phonetic)",
  "student_code": "string (STU-XXXXX)", "pin": "string (6-digit numeric)",
  "guardian_id": "UUID",
  "parental_controls": {
    "recording_mode": "enum(optional, audio_required, video_required, both_required)",
    "chapter_threshold": "integer (0-5)",
    "auto_start_recording": "boolean",
    "require_confirmation": "boolean",
    "can_skip_recording": "boolean"
  }
}
```

### A.2 Word Bank
```json
{
  "id": "UUID", "name": "string", "category": "enum(included, free, paid, specialized)",
  "visibility": "enum(public, private)", "created_by": "user_id",
  "baseline_words": [{"word":"string","definition":"string","example_sentence":"string"}],
  "target_words": [{"word":"string","definition":"string","example_sentence":"string"}],
  "stretch_words": [{"word":"string","definition":"string","example_sentence":"string"}],
  "price": "float"
}
```

### A.3 Brand
```json
{
  "id": "UUID", "name": "string", "logo_url": "string", "website": "string",
  "description": "string", "problem_statement": "string", "problem_category": "string",
  "bid_amount": "float (default: 0.05)",
  "products": [{"name":"string","description":"string"}],
  "target_ages": ["integer (empty=universal)"], "target_categories": ["string"],
  "budget_total": "float", "budget_spent": "float", "cost_per_impression": "float",
  "is_active": "boolean", "total_impressions": "integer", "total_stories": "integer",
  "rotation_count": "integer"
}
```

### A.4 Narrative
```json
{
  "id": "UUID", "title": "string", "student_id": "UUID", "bank_ids": ["UUID"],
  "theme": "string", "total_word_count": "integer",
  "chapters": [{"number":"int","title":"string","content":"string (300-500 words)",
    "embedded_tokens":[{"word":"string","tier":"enum(baseline,target,stretch)"}],
    "vision_check":{"question":"string","options":["string x4"],"correct_index":"int"}}],
  "brand_placements": [{"id":"UUID","name":"string","products":[{}],
    "problem_category":"string","bid_amount":"float"}],
  "status": "enum(generating, ready, in_progress, completed)",
  "tokens_to_verify": ["string"],
  "chapters_completed": ["integer"]
}
```

### A.5 Brand Impression
```json
{
  "id": "UUID", "brand_id":"UUID","brand_name":"string","narrative_id":"UUID",
  "student_id":"UUID","guardian_id":"UUID","campaign_id":"UUID",
  "products_featured":["string"],"cost":"float","created_date":"ISO-8601"
}
```

### A.6 Affiliate
```json
{
  "id": "UUID", "full_name":"string","email":"string",
  "affiliate_code":"string (AFF-XXXXXX)",
  "reward_type":"enum(flat_fee, percentage, wallet_credits)",
  "flat_fee_amount":"float","total_referrals":"int","total_earned":"float",
  "pending_balance":"float","total_paid":"float",
  "confirmed":"boolean","is_active":"boolean"
}
```

### A.7 Administrative Message
```json
{
  "id": "UUID", "subject": "string", "body": "string",
  "target_audience": "enum(all, guardians, students, teachers, brands)",
  "priority": "enum(normal, important, urgent)",
  "sender_id": "UUID", "timestamp": "ISO-8601"
}
```

### A.8 Spelling Contest
```json
{
  "id": "UUID", "title": "string", "description": "string",
  "words": ["string"],
  "start_date": "ISO-8601", "end_date": "ISO-8601",
  "time_limit_minutes": "integer",
  "created_by": "UUID", "created_date": "ISO-8601"
}
```

### A.9 Spelling Submission
```json
{
  "id": "UUID", "contest_id": "UUID", "student_id": "UUID",
  "student_name": "string",
  "answers": [{"word": "string", "answer": "string", "correct": "boolean", "time_ms": "integer"}],
  "total_correct": "integer", "total_attempted": "integer",
  "accuracy": "float", "total_time_ms": "integer",
  "submitted_date": "ISO-8601"
}
```

### A.10 Task
```json
{
  "id": "UUID", "user_id": "UUID",
  "title": "string", "description": "string",
  "type": "enum(reading, contest, message, assignment)",
  "due_date": "ISO-8601",
  "priority": "enum(low, medium, high)",
  "completed": "boolean"
}
```

### A.11 Parental Controls
```json
{
  "student_id": "UUID",
  "recording_mode": "enum(optional, audio_required, video_required, both_required)",
  "chapter_threshold": "integer (0-5)",
  "auto_start_recording": "boolean",
  "require_confirmation": "boolean",
  "can_skip_recording": "boolean",
  "last_updated": "ISO-8601"
}
```

### A.12 Audio Recording
```json
{
  "id": "UUID", "student_id": "UUID", "narrative_id": "UUID",
  "chapter_number": "integer",
  "file_url": "string", "duration_seconds": "float",
  "transcription": "string",
  "diction_score": {"pronunciation": "float", "fluency": "float",
    "completeness": "float", "prosody": "float", "overall": "float"},
  "is_public": "boolean", "created_date": "ISO-8601"
}
```

### A.13 Wallet Transaction
```json
{
  "id": "UUID", "user_id":"UUID",
  "type":"enum(credit,debit,topup,referral_reward,coupon_redemption)",
  "amount":"float","description":"string","created_date":"ISO-8601"
}
```

### A.14 Coupon
```json
{
  "id": "UUID", "code":"string",
  "type":"enum(percentage,fixed,wallet_credit)",
  "value":"float","wallet_credit_amount":"float",
  "max_uses":"int","current_uses":"int","expiration_date":"ISO-8601"
}
```

### A.15 Brand Offer
```json
{
  "id": "UUID", "brand_id":"UUID","title":"string","description":"string",
  "offer_type":"enum(internal,external)","link":"string",
  "is_active":"boolean","views":"int","clicks":"int","dismissals":"int"
}
```

---

## APPENDIX B: COMPETITIVE LANDSCAPE

| Capability | Semantic Vision | Duolingo | Khan Academy | Reading IQ | ABCmouse | EZDucate | Epic! |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| AI-Generated Personalized Multi-Chapter Stories | YES | No | No | No | No | Partial | No |
| Brand Comprehension Measurement | YES | No | No | No | No | No | No |
| Brand Products as Narrative Problem-Solving Elements | YES | No | No | No | No | No | No |
| Competitive Brand Bidding for Story Placement | YES | No | No | No | No | No | No |
| 60/30/10 Tiered Vocabulary Distribution | YES | No | No | No | No | No | No |
| Belief System Content Adaptation | YES | No | No | No | No | No | No |
| Cultural Context Content Integration | YES | No | No | No | No | No | No |
| Strengths/Weaknesses-Aware Narrative | YES | No | No | No | No | No | No |
| Default-False Consent for Brand Content | YES | N/A | N/A | N/A | N/A | N/A | N/A |
| Closed-Loop Brand Analytics with Story Excerpts | YES | No | No | No | No | No | No |
| Four-Condition Brand Question Classification | YES | No | No | No | No | No | No |
| Three-Layer Narrative Discovery | YES | No | No | No | No | No | No |
| Six-Role Platform Architecture | YES | No | Partial | No | Partial | No | No |
| Parental Recording Enforcement | YES | No | No | No | No | No | No |
| Spelling Bee Contest Engine | YES | No | No | No | No | No | No |
| Admin-to-User Targeted Messaging | YES | No | No | No | No | No | No |
| Automated Task Reminders | YES | No | No | No | No | No | No |
| PWA with Offline Story Caching | YES | Partial | No | No | No | No | No |
| Ambient Music in Narrative Reader | YES | No | No | No | No | No | No |
| User-Facing Affiliate Dashboard | YES | No | No | No | No | No | No |
| 16-Level Age-Calibrated Vocabulary | YES | No | No | Partial | No | No | No |
| Agentic Reach Score | YES | No | No | No | No | No | No |
| Brand Opt-Out Analytics | YES | No | No | No | No | No | No |
| Unified Multi-Role Authentication | YES | No | No | No | No | No | No |
| 20+ Language Narrative Generation | YES | Yes | No | No | No | No | No |
| Real-Time WebSocket Classroom Sessions | YES | No | No | No | No | No | No |
| Multi-Currency Support (50+) | YES | Partial | No | No | No | No | No |
| Brand-Funded Free Education Model | YES | No | No | No | No | No | No |
| Infinite Non-Repeating Content | YES | No | No | No | No | Partial | No |
| Read-Aloud Recording & Diction Analysis | YES | No | No | No | No | No | No |
| Audio Memory Library | YES | No | No | No | No | No | No |
| Peer Audio Book Section | YES | No | No | No | No | No | No |
| On-Device LLM for Offline Generation | YES | No | No | No | No | No | No |
| AI-Generated Video in Stories | YES | No | No | No | No | Partial | No |
| Lifelong Learning Continuum (Pre-K to College) | YES | No | No | No | No | No | No |
| 32 Character Virtues + 30 Emotional Categories | YES | No | No | No | No | No | No |

---

## APPENDIX C: UI SCREENSHOTS (EXHIBITS)

| Figure | Filename | Description |
|---|---|---|
| FIG. 1 | fig01_landing_page.jpeg | Public landing page with "Patent-Pending AI Technology" badge |
| FIG. 2 | fig02_unified_login.jpeg | Unified Login, Parent mode (email/password) |
| FIG. 3 | fig03_unified_login_student.jpeg | Unified Login, Student mode (code/PIN) |
| FIG. 4 | fig04_guardian_portal.jpeg | Administrator Dashboard with platform statistics |
| FIG. 5 | fig05_admin_brands.jpeg | Brand Management with revenue, impressions, bid amounts |
| FIG. 6 | fig06_admin_affiliates.jpeg | Affiliate Management with program settings and listing |
| FIG. 7 | fig07_admin_wordbanks.jpeg | Word Bank Management with three-tier vocabulary input |
| FIG. 8 | fig08_guardian_students.jpeg | Guardian Portal showing student cards and all portal tabs |
| FIG. 9 | fig09_guardian_affiliate.jpeg | Affiliate Dashboard with code, link, stats, and earnings |
| FIG. 10 | fig10_guardian_faq.jpeg | FAQ Tab with expandable items |
| FIG. 11 | fig11_affiliate_signup.jpeg | Public Affiliate Signup with registration and benefits |
| FIG. 12 | fig12_admin_statistics.jpeg | Admin Statistics Dashboard with platform metrics |
| FIG. 13 | fig13_admin_messaging.jpeg | Admin Messaging with audience targeting and priority levels |
| FIG. 14 | fig14_admin_spelling_bee.jpeg | Admin Spelling Bee contest creation and management |
| FIG. 15 | fig15_admin_ai_costs.jpeg | Admin AI Cost Tracking per model and generation |
| FIG. 16 | fig16_admin_users.jpeg | Admin User Management with Plan Membership Overview |
| FIG. 17 | fig17_guardian_students_overview.jpeg | Guardian Students with codes, PINs, virtues, Reading Rules |
| FIG. 18 | fig18_parental_controls.jpeg | Parental Controls: Recording Requirement, Chapter Threshold, Auto-Start |
| FIG. 19 | fig19_wallet.jpeg | Wallet with $1,000.02 balance, Stripe Add Funds, Coupon Redemption |
| FIG. 20 | fig20_marketplace.jpeg | Word Bank Marketplace with search, categories, pricing |
| FIG. 21 | fig21_subscription.jpeg | Subscription Plans (Starter $3.99, Family $9.99, Academy $19.99) |
| FIG. 22 | fig22_audio_memories.jpeg | Audio Memories Library with per-student recordings |
| FIG. 23 | fig23_audio_books.jpeg | Peer Audio Book Collection |
| FIG. 24 | fig24_invite_earn.jpeg | Invite & Earn with March Madness Referral Blitz ($200 Grand Prize) |
| FIG. 25 | fig25_student_progress.jpeg | Student Progress: SJ/PJ/TJ/DJ with scores and biological targets |
| FIG. 26 | fig26_student_academy.jpeg | Student Academy Dashboard |
| FIG. 27 | fig27_student_stories.jpeg | Student Story Library with AI-generated story cards |
| FIG. 28 | fig28_student_spelling_bee.jpeg | Student Spelling Bee with contests, tasks, stats, classroom join |
| FIG. 29 | fig29_narrative_reader.jpeg | Narrative Reader with "Read Aloud" button and AI story |
| FIG. 30 | fig30_story_text.jpeg | Story content with vocabulary badges and chapter navigation |
| FIG. 31 | fig31_mobile_landing.jpeg | Mobile-responsive landing page (390x844 viewport) |

---

## APPENDIX D: API ENDPOINT REFERENCE

### Authentication
- `POST /api/auth/register` - Registration with optional referral/affiliate code
- `POST /api/auth/login` - JWT login
- `POST /api/auth/student-login` - Code/PIN student auth
- `POST /api/auth/forgot-password` - Email password reset
- `GET /api/auth/me` - Current user profile

### Content Generation
- `POST /api/narratives` - AI story generation with full personalization
- `GET /api/narratives` - List narratives (filterable)
- `GET /api/narratives/{id}` - Full narrative content

### Assessment
- `POST /api/read-logs` - Chapter reading + comprehension responses
- `POST /api/assessments/evaluate-written` - AI written answer evaluation

### Brand Analytics (Brand Comprehension)
- `GET /api/brand-portal/dashboard` - Brand dashboard with impression stats
- `GET /api/brand-portal/analytics` - Comprehensive Brand Comprehension analytics
- `GET /api/brand-portal/story-integrations` - Narratives featuring brand with excerpts
- `GET /api/brands/competition/{category}` - Competition visibility
- `GET /api/brands/opt-out-analytics` - Anonymized consent data

### Affiliate
- `POST /api/affiliates/signup` - Public registration
- `GET /api/affiliates/my-stats` - User-facing dashboard data
- `GET /api/affiliates/track/{code}` - Code validation

### Parental Controls
- `GET /api/students/{student_id}/parental-controls` - Get recording rules
- `PUT /api/students/{student_id}/parental-controls` - Update recording rules

### Administrative Messaging
- `POST /api/admin/messages` - Create targeted message (admin-only)
- `GET /api/messages` - Retrieve messages for current user
- `POST /api/messages/{message_id}/read` - Mark message as read

### Spelling Contests
- `POST /api/admin/spelling-contests` - Create contest (admin-only)
- `GET /api/spelling-contests` - List active/upcoming contests
- `GET /api/spelling-contests/{id}` - Contest detail with leaderboard
- `POST /api/spelling-contests/{contest_id}/submit` - Submit results

### Task Reminders
- `GET /api/tasks` - Computed pending tasks for authenticated student

### Administration
- `GET /api/admin/affiliates` - All affiliates
- `PUT /api/admin/affiliates/settings` - Program configuration
- `PUT /api/admin/affiliates/{id}` - Approve/deactivate
- `POST /api/admin/affiliates/{id}/payout` - Record payout

### Audio Recordings
- `POST /api/audio/upload` - Upload audio recording
- `GET /api/audio/recordings/{student_id}` - Student recordings
- `GET /api/audio/public` - Public audio book collection

### Student Management
- `POST /api/students` - Create student
- `GET /api/students` - List guardian's students
- `PUT /api/students/{id}` - Update student profile
- `DELETE /api/students/{id}` - Delete student

### Word Banks
- `GET /api/word-banks` - List word banks
- `POST /api/word-banks` - Create word bank
- `PUT /api/word-banks/{id}` - Update word bank
- `GET /api/word-banks/marketplace` - Public marketplace

### Wallet & Payments
- `GET /api/wallet/balance` - Current balance
- `POST /api/wallet/topup` - Stripe checkout session
- `GET /api/wallet/transactions` - Transaction history

### Health
- `GET /api/health` - System health check

---

## APPENDIX E: INCORPORATED TECHNICAL SPECIFICATIONS

The document titled "SEMANTIC VISION -- COMPREHENSIVE TECHNICAL SPECIFICATIONS" (file: TECHNICAL_SPECIFICATIONS_1000.md) containing 1,000 individually numbered technical specifications (TS-001 through TS-1000) is incorporated by reference in its entirety. This document provides exhaustive implementation detail organized across the following 17 sections:

1. Platform Architecture (TS-001 through TS-050)
2. Authentication & Authorization (TS-051 through TS-110)
3. Student Profile System (TS-111 through TS-180)
4. Vocabulary System (TS-181 through TS-260)
5. AI Content Generation Pipeline (TS-261 through TS-370)
6. Brand Integration Engine (TS-371 through TS-460)
7. Comprehension & Assessment Engine (TS-461 through TS-530)
8. Read-Aloud Recording & Diction Analysis (TS-531 through TS-610)
9. Admin Messaging System (TS-611 through TS-660)
10. Spelling Bee Contests (TS-661 through TS-720)
11. Task Reminder System (TS-721 through TS-770)
12. Notification & Communication Infrastructure (TS-771 through TS-810)
13. Offline & PWA Capabilities (TS-811 through TS-860)
14. Ambient Music Engine (TS-861 through TS-890)
15. Analytics & Dashboards (TS-891 through TS-930)
16. Payment & Monetization (TS-931 through TS-960)
17. Security & Privacy (TS-961 through TS-1000)

---

*Document Version: 6.0 (Definitive Filing Version)*
*Inventor: Allen Tyrone Johnson*
*Status: READY FOR FILING -- DEFINITIVE VERSION*
*Total Claims: 98 (11 Independent + 60 Dependent + 14 Future Embodiment + 13 Audio/Video/Device/Lifelong/Task)*
*Incorporated Exhibits: 1,000 Technical Specifications + 31 UI Screenshots*

---

*END OF PROVISIONAL PATENT APPLICATION*
