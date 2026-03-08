# Semantic Vision — Technical Specification & Invention Disclosure

## Document Purpose
This document provides a detailed technical specification of the Semantic Vision platform's unique and novel features, intended to support a provisional patent application. It describes the system architecture, data flows, and innovative methods that distinguish Semantic Vision from all existing educational technology products.

---

## 1. INVENTION TITLE

**System and Method for Real-Time, Contextual Integration of Brand Products as Narrative Solutions Within AI-Generated, Personalized Educational Stories Adapted to User Belief Systems, Cultural Contexts, and Vocabulary Development Goals**

---

## 2. EXECUTIVE SUMMARY

Semantic Vision is an AI-powered educational platform that generates personalized, multi-chapter stories to teach vocabulary. Its core innovation lies in a **real-time pipeline** that:

1. Constructs a student profile from demographic, cultural, religious, linguistic, and interest-based data.
2. Dynamically selects vocabulary from a tiered 60/30/10 word bank system (Baseline / Target / Stretch).
3. Fetches eligible brand partner products from a live marketplace database at the moment of story generation.
4. Instructs a Large Language Model (LLM) to weave those products into the narrative as **organic, problem-solving elements** — not advertisements.
5. Records brand impressions, calculates cost-per-impression (CPI), and updates brand budgets in real time.

No other product on the market combines personalized, belief-aware educational content generation with a real-time, non-intrusive brand sponsorship model.

---

## 3. BACKGROUND & PROBLEM STATEMENT

### 3.1 Limitations of Existing Educational Platforms
- **Static Content:** Traditional vocabulary programs use fixed word lists and pre-written passages. They cannot personalize content to a student's religion, culture, or specific interests.
- **One-Size-Fits-All:** No existing platform dynamically adjusts story themes, character virtues, or cultural settings based on a user's profile.
- **Advertising vs. Education:** Current monetization models (banner ads, paywalls) interrupt the learning experience. There is no system that integrates brand messaging *within* the educational content itself as a natural, value-adding element.

### 3.2 The Semantic Vision Solution
Semantic Vision solves these problems with a **real-time, context-aware story generation pipeline** that produces unique, personalized content for every student, every time, while funding the platform through organic brand integrations that *enhance* the learning experience rather than detracting from it.

---

## 4. SYSTEM ARCHITECTURE

### 4.1 Technology Stack
| Component       | Technology                                      |
|-----------------|--------------------------------------------------|
| Backend API     | Python FastAPI, async/await architecture         |
| Database        | MongoDB (Motor async driver), document-oriented  |
| Frontend        | React 18, TypeScript, Tailwind CSS, Shadcn/UI    |
| AI Engine       | OpenAI GPT-5.2 via Emergent LLM Integration      |
| Payments        | Stripe API for wallet top-ups and donations       |
| Real-Time Comm  | WebSockets (FastAPI native)                       |
| Authentication  | JWT (JSON Web Tokens), role-based access control  |
| Internationalization | react-i18next (20 languages supported)       |
| Geolocation     | ip-api.com (IP-based location detection)          |
| Currency        | Open Exchange Rates API (50+ currencies)          |

### 4.2 Multi-Role Access Control System
The platform implements a five-tier role-based access control (RBAC) system:

| Role            | Capabilities                                                                 |
|-----------------|------------------------------------------------------------------------------|
| **Admin**       | Full platform control: user management, word bank CRUD, contest management, billing configuration, LLM model selection, feature flags, brand approval |
| **Guardian/Parent** | Student management, word bank assignment, wallet management, referral program, progress monitoring, ad preference controls |
| **Teacher**     | Classroom session management, real-time WebSocket-based group reading sessions, student performance tracking |
| **Student**     | Story reading, vocabulary assessments, spelling practice, progress tracking   |
| **Brand Partner** | Campaign creation, budget management, impression analytics, product catalog management |

---

## 5. CORE INNOVATION: REAL-TIME BRAND INTEGRATION PIPELINE

### 5.1 Overview
This is the **primary patentable invention**. At the moment a story is requested, the system executes a multi-step pipeline that dynamically selects, filters, and instructs the AI to integrate brand products as narrative solutions.

### 5.2 Detailed Data Flow

```
[Student/Guardian Requests Story]
            │
            ▼
┌─────────────────────────────────────────┐
│  STEP 1: STUDENT PROFILE ASSEMBLY       │
│  - Fetch student record from DB          │
│  - Extract: name, age, grade, interests, │
│    virtues, belief_system,               │
│    cultural_context, language,            │
│    ad_preferences                         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  STEP 2: VOCABULARY SELECTION           │
│  - Fetch assigned word banks            │
│  - Separate into tiers:                 │
│    * 60% Baseline (18 words)            │
│    * 30% Target (9 words)               │
│    * 10% Stretch (3 words)              │
│  - Randomize selection per generation   │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  STEP 3: BRAND ELIGIBILITY CHECK        │
│  (THE KEY INNOVATION)                   │
│  a. Check system feature flag:           │
│     brand_sponsorship_enabled            │
│  b. Check student's ad_preferences:      │
│     - allow_brand_stories (boolean)      │
│     - blocked_categories (list)          │
│  c. Query active brands from database    │
│  d. For each brand, apply filters:       │
│     - Age appropriateness filter         │
│     - Budget availability check          │
│     - Category block list check          │
│  e. Select up to 2 eligible brands       │
│  f. Extract: brand name, products,       │
│     problem_statement, logo_url          │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  STEP 4: PROMPT CONSTRUCTION            │
│  Assemble a composite AI prompt:        │
│  - Student profile section              │
│  - Vocabulary tier distribution         │
│  - Character education virtues          │
│  - Belief system alignment              │
│  - Cultural context integration         │
│  - Language specification               │
│  - BRAND INTEGRATION DIRECTIVE:         │
│    "Naturally weave these brands into   │
│     the story as helpful solutions to   │
│     problems the characters face."      │
│  - Per-brand: name, products solved,    │
│    problem statement                    │
│  - JSON output schema requirement       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  STEP 5: AI STORY GENERATION            │
│  - Send prompt to LLM (GPT-5.2 or      │
│    configurable model via admin panel)   │
│  - Receive structured JSON response:     │
│    * 5 chapters (300-500 words each)     │
│    * Embedded vocabulary tokens per ch.  │
│    * Comprehension questions per ch.     │
│    * Brand mentions woven naturally      │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  STEP 6: POST-GENERATION PROCESSING     │
│  - Parse and validate JSON structure     │
│  - Record brand impressions in DB        │
│  - Update brand budget_spent             │
│  - Log LLM usage cost (model, tokens,   │
│    duration, success/failure)            │
│  - Store narrative with chapter data     │
│  - Make story available to student       │
└─────────────────────────────────────────┘
```

### 5.3 Key Novel Aspects

#### 5.3.1 Consent-Based, Non-Intrusive Brand Integration
Unlike traditional advertising:
- **Guardian Consent Required:** Brand stories only appear if the student's guardian has explicitly enabled `allow_brand_stories` in ad preferences.
- **Category Blocking:** Guardians can block specific brand categories (e.g., "fast food," "electronics").
- **No Banners or Pop-ups:** Brand products appear as natural plot elements — a character uses a specific product to solve a problem in the story.
- **Educational Value Added:** The brand mention is framed as a "solution," teaching the student about real-world problem-solving.

#### 5.3.2 Real-Time Eligibility Engine
At the instant of each story request, the system dynamically:
- Queries the live brand database for active sponsors.
- Applies age-appropriateness filters.
- Checks budget availability (prevents overspend).
- Applies guardian-set category restrictions.
- Limits to a maximum of 2 brands per story.

This means every story generated has a potentially different brand composition, based on the current state of the brand marketplace.

#### 5.3.3 Belief System and Cultural Context Awareness
The AI prompt is constructed with awareness of:
- **Belief System:** The story reflects values and teachings of the student's specified religion or philosophy (e.g., Christianity, Islam, Buddhism, Secular Humanism). Characters demonstrate behaviors consistent with these principles.
- **Cultural Context:** Incorporates culturally relevant names, settings, traditions, foods, and customs. Ensures respectful and authentic representation.
- **Language:** Stories can be generated in 20+ languages, with all content including vocabulary explanations in the target language.

This makes the brand integration culturally sensitive — a brand product might be woven into a Diwali celebration story for an Indian student or a Thanksgiving story for an American student, always respecting the cultural and religious context.

---

## 6. SECONDARY INNOVATIONS

### 6.1 The 60/30/10 Vocabulary Tier System
A scientifically-inspired vocabulary distribution model:
- **60% Baseline Words:** Foundation-level vocabulary the student should already know, reinforcing mastery.
- **30% Target Words:** Growth-level vocabulary slightly above the student's current level, promoting learning.
- **10% Stretch Words:** Challenge-level vocabulary significantly above level, introducing aspirational language.

Each story dynamically selects and shuffles words from assigned word banks, ensuring no two stories repeat the same vocabulary sequence.

### 6.2 Multi-Tier Word Bank Ecosystem
- **Admin Word Banks:** Centrally managed, available to all users. Can be categorized as Included, Free, Paid, or Specialized.
- **Parent-Created Word Banks:** Automatically set to `private` visibility. Only visible to the creator and their linked students. Tracked via `created_by` and `created_by_role` fields.
- **Marketplace:** Parents and teachers can discover and assign word banks from a curated marketplace.

### 6.3 Real-Time Classroom Sessions (WebSocket)
Teachers can initiate live reading sessions:
- Students join via WebSocket connection.
- The teacher controls pacing and can broadcast comprehension questions in real time.
- All participating students' results are tracked per session.

### 6.4 Dynamic Currency & Geolocation System
- On first load, the platform detects the user's country via IP geolocation.
- All monetary values (wallet balances, referral rewards, donation amounts) are displayed in the user's local currency using live exchange rates.
- Exchange rates are fetched from a free API and cached.

### 6.5 Referral Contest System
- Admins can create time-bound referral contests with configurable prizes.
- A live leaderboard displays top referrers.
- Referral reward amounts are admin-configurable.
- Currency-aware: prizes and earnings displayed in the user's local currency.

### 6.6 Brand Impression Economics
- Brands set a total campaign budget and a cost-per-impression (CPI).
- Each time a brand's products appear in a generated story, the system records an impression and debits the brand's budget.
- Brands receive analytics: total impressions, total stories, products featured, and budget utilization.
- The admin can view aggregate ROI metrics.

---

## 7. DATA MODELS (Key Schemas)

### 7.1 Student Profile
```json
{
  "id": "uuid",
  "full_name": "string",
  "age": "integer",
  "grade_level": "enum (pre-k, k, 1-12, college, adult)",
  "interests": ["string"],
  "virtues": ["string"],
  "belief_system": "string",
  "cultural_context": "string",
  "language": "string",
  "assigned_banks": ["word_bank_id"],
  "ad_preferences": {
    "allow_brand_stories": "boolean",
    "blocked_categories": ["string"]
  },
  "spellcheck_disabled": "boolean",
  "spelling_mode": "string"
}
```

### 7.2 Word Bank
```json
{
  "id": "uuid",
  "name": "string",
  "category": "enum (included, free, paid, specialized)",
  "visibility": "enum (public, private)",
  "created_by": "user_id",
  "created_by_role": "enum (admin, guardian, teacher)",
  "baseline_words": [{"word": "string", "definition": "string"}],
  "target_words": [{"word": "string", "definition": "string"}],
  "stretch_words": [{"word": "string", "definition": "string"}]
}
```

### 7.3 Brand
```json
{
  "id": "uuid",
  "name": "string",
  "products": [{"name": "string", "description": "string"}],
  "problem_statement": "string",
  "target_categories": ["string"],
  "target_ages": ["integer"],
  "budget_total": "float",
  "budget_spent": "float",
  "total_impressions": "integer",
  "total_stories": "integer",
  "is_active": "boolean"
}
```

### 7.4 Brand Impression
```json
{
  "id": "uuid",
  "brand_id": "string",
  "brand_name": "string",
  "narrative_id": "string",
  "student_id": "string",
  "guardian_id": "string",
  "products_featured": ["string"],
  "cost": "float",
  "created_date": "datetime"
}
```

### 7.5 Narrative (Generated Story)
```json
{
  "id": "uuid",
  "title": "string",
  "student_id": "string",
  "bank_ids": ["string"],
  "theme": "string",
  "chapters": [{
    "number": "integer",
    "title": "string",
    "content": "string (300-500 words)",
    "word_count": "integer",
    "embedded_tokens": [{"word": "string", "tier": "enum (baseline, target, stretch)"}],
    "vision_check": {
      "question": "string",
      "options": ["string x4"],
      "correct_index": "integer"
    }
  }],
  "total_word_count": "integer",
  "status": "enum (generating, ready, in_progress, completed)"
}
```

---

## 8. CLAIMS OF NOVELTY

### Claim 1: Real-Time Brand Product Integration in Personalized Educational Content
A computer-implemented method for dynamically integrating brand product information into AI-generated educational narratives, comprising:
- Receiving a content generation request associated with a student profile;
- Querying a brand database to identify eligible brand products based on real-time filtering criteria including student age, guardian consent preferences, category restrictions, and brand budget availability;
- Constructing a composite prompt that directs a large language model to weave the selected brand products as organic, problem-solving narrative elements within a personalized educational story;
- Recording each brand integration as a measurable impression with associated cost.

### Claim 2: Belief-System and Cultural Context Awareness in AI Content Generation
A method for generating educational content that adapts to a user's specified belief system and cultural context, comprising:
- Storing belief system and cultural context identifiers in a student profile;
- Incorporating these identifiers into AI prompt instructions that direct character behavior, story settings, cultural references, and moral lessons to align with the specified belief system and cultural context;
- Generating multi-chapter narratives where vocabulary learning is contextualized within the student's own cultural and religious framework.

### Claim 3: Tiered Vocabulary Distribution System (60/30/10)
A method for distributing vocabulary across AI-generated educational content using a three-tier system:
- 60% Baseline (reinforcement);
- 30% Target (growth);
- 10% Stretch (aspiration);
With dynamic random selection from assigned word banks, ensuring unique vocabulary combinations per story generation.

### Claim 4: Consent-Gated, Non-Intrusive Educational Advertising
A system for delivering brand messaging within educational content that requires:
- Explicit guardian consent (opt-in per student);
- Guardian-controlled category blocking;
- Age-appropriateness filtering;
- Budget-limited exposure;
- Integration as narrative problem-solving elements rather than display advertisements.

---

## 9. COMPETITIVE DIFFERENTIATION

| Feature                              | Semantic Vision | Duolingo | Khan Academy | Reading IQ | ABCmouse |
|--------------------------------------|:--------------:|:--------:|:------------:|:----------:|:--------:|
| AI-Generated Personalized Stories     | Yes            | No       | No           | No         | No       |
| Belief System Adaptation             | Yes            | No       | No           | No         | No       |
| Cultural Context Integration         | Yes            | No       | No           | No         | No       |
| Real-Time Brand Integration          | Yes            | No       | No           | No         | No       |
| 60/30/10 Vocabulary Tiers            | Yes            | No       | No           | No         | No       |
| Multi-Role Platform                  | Yes            | No       | Partial      | No         | Partial  |
| 20+ Language Support                 | Yes            | Yes      | No           | No         | No       |
| Guardian Ad Consent Controls         | Yes            | N/A      | N/A          | N/A        | N/A      |
| Real-Time Classroom Sessions         | Yes            | No       | No           | No         | No       |
| Brand Impression Economics           | Yes            | No       | No           | No         | No       |

---

## 10. SECURITY & COMPLIANCE CONSIDERATIONS

- **COPPA Awareness:** Student accounts are created and managed exclusively by guardians or teachers. Students authenticate with codes and PINs, not email/password.
- **Data Minimization:** Student profiles contain only educational and preference data necessary for story generation.
- **Consent Architecture:** Brand integration requires explicit opt-in at the guardian level, with granular category controls.
- **JWT Authentication:** All API endpoints are protected with role-based JWT authentication.
- **Private Word Banks:** Parent-created word banks are automatically set to private, preventing data leakage between families.

---

## 11. CONCLUSION

Semantic Vision's core innovation — the real-time, contextual integration of brand products as narrative solutions within AI-generated, personalized educational stories — represents a novel intersection of educational technology, AI content generation, and digital advertising. No existing product combines these capabilities in a single system. The platform's additional innovations in belief-system adaptation, cultural context awareness, and consent-gated advertising further distinguish it as a unique and protectable invention.

---

*Document Version: 1.0*  
*Date: February 2026*  
*Prepared for: Provisional Patent Application Support*
