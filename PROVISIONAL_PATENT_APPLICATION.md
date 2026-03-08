# PROVISIONAL PATENT APPLICATION

## UNITED STATES PATENT AND TRADEMARK OFFICE

---

**Application Type:** Provisional Patent Application under 35 U.S.C. 111(b)

**Filing Date:** [TO BE COMPLETED BY ATTORNEY]

**Applicant(s):** [TO BE COMPLETED BY ATTORNEY]

**Correspondence Address:** [TO BE COMPLETED BY ATTORNEY]

---

## TITLE OF THE INVENTION

**System and Method for Real-Time, Contextual Integration of Brand Product Placements as Narrative Solutions Within AI-Generated, Personalized Educational Content Adapted to User Belief Systems, Cultural Contexts, Developmental Profiles, and Vocabulary Acquisition Goals, With Closed-Loop Brand Engagement Analytics**

---

## FIELD OF THE INVENTION

The present invention relates generally to artificial intelligence-driven educational content generation, and more particularly, to a computer-implemented system and method for dynamically integrating commercial brand products into personalized, multi-chapter educational narratives as organic, problem-solving story elements, while simultaneously providing real-time analytics on student engagement with said branded content back to brand sponsors.

---

## BACKGROUND OF THE INVENTION

### Technical Problem

The field of educational technology ("EdTech") has long faced three persistent and interrelated challenges:

**1. Static, One-Size-Fits-All Content.** Existing vocabulary and reading platforms (e.g., Duolingo, Khan Academy, Reading IQ, ABCmouse) rely on pre-authored, static content libraries. These platforms cannot dynamically personalize educational narratives to reflect a student's individual religion, cultural heritage, specific interests, character development goals, personal strengths, or areas of growth. The content is authored once and served identically to all students, regardless of their backgrounds.

**2. Intrusive, Educationally Disruptive Monetization.** The predominant monetization models in EdTech -- banner advertisements, interstitial video ads, and hard paywalls -- interrupt the learning experience. Banner ads are cognitively distracting. Video interstitials break the narrative flow. Paywalls create equity gaps. No existing system integrates brand messaging *within* educational content in a way that adds educational value rather than detracting from it.

**3. Absence of Measurable Brand-Education Feedback Loops.** Even in platforms that accept advertising, brands receive only surface-level metrics (click-through rates, impressions counted by page loads). No existing system provides brands with granular analytics showing: (a) the exact narrative context in which their product appeared, (b) specific comprehension questions generated about their product integration, (c) student pass/fail rates on those questions, or (d) the full text of the educational content where the product was featured.

### Prior Art Limitations

A survey of existing systems reveals no prior art combining all of the following capabilities in a single integrated platform:

| Capability | Status in Prior Art |
|---|---|
| AI-generated personalized educational narratives | Limited; no commercial system generates multi-chapter stories personalized across belief, culture, strengths/weaknesses, and vocabulary tiers simultaneously |
| Real-time brand product integration as narrative problem-solving elements | No known prior art |
| Consent-gated, guardian-controlled brand content in educational settings | No known prior art |
| Tiered vocabulary distribution (60/30/10 model) within AI-generated content | No known prior art |
| Closed-loop brand analytics with story excerpts, brand-specific questions, and student response data | No known prior art |
| Belief system and cultural context-aware AI content generation | No known prior art in educational narrative generation |

The present invention addresses all of the foregoing limitations through a novel, integrated system and method described herein.

---

## SUMMARY OF THE INVENTION

The present invention provides a computer-implemented platform ("Semantic Vision") comprising a real-time content generation pipeline that:

1. **Assembles a multi-dimensional student profile** from demographic, cultural, religious, linguistic, developmental, and interest-based data, including parent-authored descriptions of the child's strengths and growth areas.

2. **Selects vocabulary according to a novel three-tier distribution model** (60% Baseline / 30% Target / 10% Stretch) from dynamically assigned word banks, with randomized selection ensuring unique vocabulary combinations per generation event.

3. **Executes a real-time brand eligibility engine** that, at the instant of each content generation request, queries a live brand marketplace database, applies multi-factor filtering (age appropriateness, guardian consent, category restrictions, budget availability), and selects up to a configurable maximum number of eligible brand sponsors.

4. **Constructs a composite AI prompt** incorporating all of the foregoing elements -- student profile, vocabulary tiers, character education virtues, belief system alignment, cultural context, language specification, strengths/weaknesses directives, and brand integration instructions -- and directs a Large Language Model ("LLM") to generate a structured, multi-chapter educational narrative in which brand products appear as organic, problem-solving elements.

5. **Records brand impressions**, updates brand budgets, and logs economic data in real time upon narrative generation.

6. **Generates context-aware comprehension questions** per chapter, including questions that test the student's understanding of narrative elements involving the integrated brand products.

7. **Evaluates student responses** to comprehension questions and vocabulary assessments using a secondary LLM evaluation pipeline, tracking mastery of vocabulary tokens and comprehension performance.

8. **Closes the analytics loop** by providing brand sponsors with a detailed dashboard comprising: (a) exact story excerpts where their products were mentioned, (b) specific "brand activation questions" asked of students, (c) pass/fail statistics for those questions, (d) free-text student responses, and (e) the ability to read the full narrative text.

No single prior art system or obvious combination of prior art systems teaches or suggests this integrated approach.

---

## BRIEF DESCRIPTION OF THE DRAWINGS

The following figures are referenced throughout this specification:

- **FIG. 1** — System architecture overview showing the relationship between the frontend client application, backend API server, database layer, AI engine, and payment processor.
- **FIG. 2** — Detailed data flow diagram of the Real-Time Brand Integration Pipeline (Steps 1-6).
- **FIG. 3** — Entity relationship diagram showing key data models: Student Profile, Word Bank, Brand, Narrative, Brand Impression, Assessment, Written Answer, and Read Log.
- **FIG. 4** — Flowchart of the Brand Eligibility Engine showing multi-factor filtering logic.
- **FIG. 5** — Diagram of the Closed-Loop Brand Analytics Pipeline showing data flow from narrative generation through student interaction to brand dashboard presentation.
- **FIG. 6** — Screenshot representations of the Brand Analytics Dashboard showing story excerpts, activation questions, and student response data.

*Note: Formal drawings to be prepared by patent illustrator prior to non-provisional filing.*

---

## DETAILED DESCRIPTION OF THE PREFERRED EMBODIMENTS

### 1. System Architecture Overview (FIG. 1)

The preferred embodiment of the present invention comprises a distributed computing system with the following components:

**1.1 Backend Application Server.** A Python-based asynchronous web application server built on the FastAPI framework, providing RESTful API endpoints for all system operations. The server implements role-based access control ("RBAC") using JSON Web Tokens ("JWT") for five distinct user roles: Administrator, Guardian/Parent, Teacher, Student, and Brand Partner.

**1.2 Database Layer.** A MongoDB document-oriented database accessed via the Motor asynchronous driver, storing all user profiles, student records, word banks, brand records, narratives, assessments, brand impressions, read logs, written answers, and system configuration.

**1.3 AI Engine.** A Large Language Model integration layer supporting multiple providers (including OpenAI GPT-5.2 and configurable alternatives), used for two distinct functions: (a) multi-chapter educational narrative generation, and (b) student response evaluation for both comprehension questions and vocabulary assessments.

**1.4 Frontend Client Application.** A React 18 single-page application with role-specific portals for each user type, providing the user interface for all system interactions.

**1.5 Payment Processing Layer.** A Stripe API integration providing wallet top-up functionality for guardians and budget management for brand partners.

### 2. Multi-Dimensional Student Profile Assembly (FIG. 2, Step 1)

The system maintains a comprehensive student profile record comprising the following data fields, each of which contributes to the personalization of generated content:

**2.1 Demographic Data.** Full name, age (integer), and grade level (enumerated: pre-kindergarten, kindergarten, grades 1-12, college, adult).

**2.2 Interest Graph.** A list of student interests (e.g., "soccer," "robots," "animals") used to theme generated narratives.

**2.3 Character Education Virtues.** A list of virtues (e.g., "courage," "honesty," "perseverance") that the AI is instructed to model through character behavior in the narrative.

**2.4 Belief System Identifier.** A string identifier (e.g., "Christianity," "Islam," "Buddhism," "Secular Humanism") that directs the AI to reflect corresponding values, teachings, and moral frameworks in the generated content. Characters demonstrate behaviors and decision-making consistent with the specified belief system's principles.

**2.5 Cultural Context Identifier.** A string identifier (e.g., "African American," "South Asian," "Latin American") that directs the AI to incorporate culturally relevant names, settings, traditions, foods, and customs. This ensures respectful and authentic cultural representation in the narrative.

**2.6 Language Preference.** A language identifier supporting 20+ languages, directing the AI to generate the entire narrative -- including chapter titles, content, vocabulary explanations, and comprehension questions -- in the specified language.

**2.7 Strengths Description.** A free-text field authored by the student's parent or guardian describing the child's strengths. The AI is instructed to celebrate and reinforce these strengths by having the protagonist exhibit them as positive character attributes ("superpowers") used to help others and solve problems.

**2.8 Weaknesses/Growth Areas Description.** A free-text field authored by the student's parent or guardian describing the child's areas for growth. The AI is instructed to model growth in these areas through empathetic character development, showing the protagonist struggling with and gradually overcoming similar challenges -- never through shame or deficit framing. Practical strategies and small victories are woven into the narrative.

**2.9 Advertising Preferences.** A structured sub-object comprising:
- `allow_brand_stories` (Boolean): Whether the guardian has opted the student into brand-integrated content.
- `blocked_categories` (List of Strings): Categories of brands (e.g., "fast food," "electronics") that the guardian has blocked from appearing in the student's content.

**2.10 Vocabulary State.** A list of assigned word bank identifiers, a list of mastered vocabulary tokens (plain strings), and an Agentic Reach Score (float, 0-100) representing overall learning progress.

### 3. Three-Tier Vocabulary Distribution System (60/30/10 Model)

The present invention implements a novel vocabulary distribution model inspired by educational scaffolding theory. At each content generation event, the system:

**3.1** Retrieves all word banks assigned to the student. Each word bank contains three categorized lists: `baseline_words`, `target_words`, and `stretch_words`. Each word entry comprises the word itself, its definition, and an example sentence.

**3.2** Aggregates words from all assigned banks into three master lists.

**3.3** Randomly shuffles each master list to ensure non-repeating vocabulary sequences across generation events.

**3.4** Selects words according to the 60/30/10 distribution:
- **60% Baseline Words (18 words maximum):** Foundation-level vocabulary the student is expected to already know. Inclusion reinforces mastery and provides familiar anchor points within the narrative.
- **30% Target Words (9 words maximum):** Growth-level vocabulary slightly above the student's current competency level. These represent the primary learning objective.
- **10% Stretch Words (3 words maximum):** Challenge-level vocabulary significantly above the student's level. These introduce aspirational language and reward advanced comprehension.

**3.5** This distribution ensures each generated narrative contains a pedagogically sound mixture of reinforcement (baseline), primary instruction (target), and aspirational challenge (stretch), while the random shuffling guarantees that no two narratives present the same vocabulary sequence even when drawn from the same word banks.

### 4. Real-Time Brand Eligibility Engine (FIG. 4)

This subsystem represents a core novel aspect of the present invention. At the precise moment a content generation request is received, the system executes the following multi-factor filtering pipeline:

**4.1 System-Level Feature Gate.** The system checks a globally configurable feature flag (`brand_sponsorship_enabled`) stored in the system configuration database. If disabled by an administrator, no brand integration occurs for any student.

**4.2 Guardian Consent Check.** The system reads the student's `ad_preferences.allow_brand_stories` field. If the guardian has not explicitly opted in (Boolean `true`), no brand integration occurs for this student. This is a hard gate -- the system defaults to `false`, requiring affirmative guardian action.

**4.3 Active Brand Query.** The system queries the brand database for all brands with `is_active` set to `true`, returning up to 20 candidates.

**4.4 Age Appropriateness Filter.** For each candidate brand, the system checks if the brand has defined a `target_ages` list. If defined, the student's age must be present in this list. Brands without age restrictions pass this filter.

**4.5 Budget Availability Check.** The system verifies that the brand's `budget_spent` has not reached or exceeded its `budget_total`. Brands that have exhausted their campaign budget are excluded, preventing overspend.

**4.6 Category Block List Check.** The system cross-references each brand's `target_categories` against the guardian's `blocked_categories` list. If any category overlap exists, the brand is excluded.

**4.7 Selection and Limit.** Brands that pass all filters are selected, with a configurable maximum (default: 2 brands per narrative). The selected brands' names, products, problem statements, and logo URLs are extracted for inclusion in the AI prompt.

**4.8 Dynamic Composition.** Because the eligibility engine runs at each generation request against the live database state, every narrative has a potentially unique brand composition based on: (a) which brands are currently active, (b) which brands still have budget remaining, (c) the specific student's age and guardian preferences, and (d) the current system-wide feature flag state.

### 5. Composite AI Prompt Construction (FIG. 2, Step 4)

The system constructs a comprehensive prompt for the Large Language Model that synthesizes all dimensions of personalization into a single generation directive. The prompt comprises the following sections, assembled programmatically:

**5.1 Student Profile Section.** Injects the student's name, age, grade level, interests, and character education virtues.

**5.2 Vocabulary Distribution Section.** Lists the selected baseline, target, and stretch words with their tier designations.

**5.3 Character Education Directive.** Instructs the AI to weave lessons about specified virtues into the narrative through character behavior.

**5.4 Belief System Alignment Directive.** When a belief system is specified, instructs the AI to reflect corresponding values and teachings, and to show characters navigating challenges with wisdom and virtue consistent with those principles.

**5.5 Cultural Context Integration Directive.** When a cultural context is specified, instructs the AI to incorporate culturally relevant names, settings, traditions, foods, and customs with respectful and authentic representation.

**5.6 Language Directive.** When a non-English language is specified, instructs the AI to generate the entire narrative in the target language, including all chapter titles, content, and vocabulary explanations.

**5.7 Brand Integration Directive.** This is the key novel prompt section. When eligible brands have been selected by the Brand Eligibility Engine (Section 4), the prompt includes:

> "Naturally weave these brands into the story as helpful solutions to problems the characters face. Focus on how each brand's products solve a real problem relevant to the story. Make brand mentions feel organic and educational, not like advertisements."

For each selected brand, the prompt includes: brand name, products and their descriptions, the brand's problem statement (what their products solve), and optionally, the brand's logo URL. The directive specifies inclusion of 1-2 natural brand mentions across the story where the brand's products solve a problem or help the character learn.

**5.8 Strengths and Growth Areas Directive.** When strengths are specified, instructs the AI to have the protagonist exhibit and celebrate these strengths as "superpowers." When growth areas are specified, instructs the AI to show the protagonist struggling with but growing through similar challenges using perseverance, support, and positive mindset -- explicitly prohibiting shame or deficit framing.

**5.9 Structural Requirements.** Specifies the output format: exactly 5 chapters, each 300-500 words, with natural vocabulary embedding, and one comprehension question per chapter with 4 multiple-choice options and a correct answer index.

**5.10 Output Schema.** Requires the AI to return a structured JSON object containing: story title, theme, and an array of chapter objects, each with: chapter number, title, full text content, embedded token annotations (word and tier), and a vision check object (question, four options, correct index).

### 6. AI Story Generation and Post-Processing (FIG. 2, Steps 5-6)

**6.1 LLM Invocation.** The composite prompt is transmitted to the configured LLM (default: OpenAI GPT-5.2 via the Emergent LLM integration layer). The system supports configurable model selection by the administrator, including fallback chains for alternative providers.

**6.2 Response Parsing and Validation.** The AI's response is parsed as JSON. Each chapter is validated for structural completeness. Embedded vocabulary tokens are verified against valid tiers (baseline, target, stretch). Vision check questions are validated for completeness, with default fallbacks applied for any missing or malformed entries.

**6.3 Narrative Persistence.** The validated narrative is stored in the database with all chapter content, embedded token annotations, comprehension questions, and a reference to the word banks used. If brand placements were included, the brand placement data (brand ID, name, products, problem statement) is stored directly on the narrative document.

**6.4 Brand Impression Recording.** For each brand placement in the generated narrative, the system:
- Creates a Brand Impression record linking the brand ID to the narrative ID, student ID, guardian ID, and the list of products featured.
- Assigns an economic cost per impression (configurable, default: $0.05).
- Atomically increments the brand's `total_impressions`, `total_stories`, and `budget_spent` counters in the brand database record.

**6.5 Cost Logging.** The system logs the LLM usage for each generation event, recording: model used, provider, estimated prompt tokens, estimated completion tokens, total tokens, estimated cost (using model-specific rate tables), generation duration, and success/failure status. This enables platform-wide cost monitoring and per-student cost attribution.

### 7. Student Interaction and Assessment Pipeline

**7.1 Narrative Reading.** Students access generated narratives through a reading interface. As the student completes each chapter, the system presents the chapter's vision check (comprehension question). The student's response is logged in a `read_log` record containing: narrative ID, chapter number, student ID, whether the vision check was passed, and a timestamp.

**7.2 Vocabulary Assessment Generation.** Upon completing all chapters, the system generates a vocabulary assessment comprising questions for each target-tier and stretch-tier word that appeared in the narrative (`tokens_to_verify`). Each question prompts the student to: (a) provide a definition for the word, and (b) use it in a sentence.

**7.3 AI-Powered Assessment Evaluation.** Student vocabulary responses are evaluated by a second LLM invocation. The evaluation prompt includes: the word being tested, the correct definition and example sentence (from the word bank), the student's submitted definition and sentence, and the student's configured spelling mode ("exact" or "phonetic"). The AI returns a per-word evaluation comprising: definition correctness, sentence correctness, overall correctness, encouraging feedback, and identified spelling errors.

**7.4 Written Answer Evaluation.** For free-text comprehension responses (as opposed to multiple-choice vision checks), the system uses a separate LLM evaluation pipeline that assesses: whether the answer demonstrates understanding, relevance to the question, and spelling quality. Each evaluation and the student's original answer are stored in a `written_answers` collection for subsequent analytics.

**7.5 Mastery Tracking.** When a student achieves 80% or greater accuracy on a vocabulary assessment, the system:
- Identifies which tokens were answered correctly.
- Normalizes all mastered tokens to lowercase plain strings for consistent tracking.
- Merges newly mastered tokens with the student's existing `mastered_tokens` set, preventing duplicates.
- Recalculates the student's Agentic Reach Score using the formula:

```
Agentic Reach Score = min(
    (|mastered_tokens| x 10 + completed_narratives x 50) / 
    max(total_narratives x 50, 1) x 100,
    100.0
)
```

This score provides a holistic measure of the student's vocabulary acquisition rate relative to their engagement volume.

### 8. Closed-Loop Brand Analytics Pipeline (FIG. 5)

This subsystem represents the second major novel aspect of the present invention: the ability to close the feedback loop between brand integration in educational content and measurable student engagement analytics presented back to the brand.

**8.1 Three-Layer Narrative Discovery.** When a brand partner requests analytics, the system identifies all narratives containing that brand's content using a three-layer search:

- **Layer 1: Structured Brand Placements.** Queries the `brand_placements` field on narrative documents for the brand's ID. This catches narratives generated after the brand placement tracking feature was implemented.
- **Layer 2: Impression Records.** Queries the `brand_impressions` collection for the brand's ID and retrieves associated narrative IDs. This catches narratives where impressions were recorded but the `brand_placements` field may not be present.
- **Layer 3: Full-Text Content Search.** Performs a text search across all remaining narrative chapter content for the brand name and product names (case-insensitive). This catches historical narratives where neither structured brand placement data nor impression records exist.

This three-layer approach ensures comprehensive brand coverage regardless of when or how narratives were generated.

**8.2 Story Excerpt Extraction.** For each identified narrative, the system extracts specific sentences from chapter content where the brand name or product names appear. The extraction algorithm:
- Splits chapter content into sentences (splitting on `.`, `!`, `?`).
- Filters to retain only sentences containing brand or product name mentions (case-insensitive).
- Returns up to 5 excerpts per chapter, along with metadata: narrative title, chapter number/title, student name, matched brand terms, and creation date.

**8.3 Brand Activation Question Identification.** The system identifies comprehension questions ("vision checks") that are specifically related to the brand's presence in the narrative. A question is classified as "brand-related" if any of the following conditions are met:

- **Condition A (Direct Mention):** The brand or product name appears directly in the question text or expected answer.
- **Condition B (Product Category + Brand Context):** The question asks about a product-category keyword (e.g., "tool," "device," "tablet," "technology," "gadget") AND the chapter containing the question has brand content.
- **Condition C (Answer Proximity):** The expected answer contains terms derived from the brand's product names (including individual significant words from multi-word product names).
- **Condition D (Contextual Relevance):** For questions without explicit expected answers, if the chapter contains brand content and the question's keywords appear in sentences near brand mentions.

**8.4 Question Performance Analytics.** For each identified brand activation question, the system retrieves all `read_log` entries for that narrative and chapter, tallying:
- Total attempts (number of students who encountered the question).
- Passed count (students who answered correctly).
- Failed count (students who answered incorrectly).

**8.5 Student Written Response Aggregation.** The system retrieves free-text written answers from all students who interacted with brand-containing narratives, including: the question posed, the student's verbatim answer, pass/fail status, comprehension score, and timestamp.

**8.6 Summary Statistics.** The system computes aggregate metrics:
- Total stories featuring the brand.
- Total brand mentions (story excerpts).
- Total brand activation questions.
- Total question attempts across all students.
- Overall pass rate (passes / attempts x 100).
- Total written student responses.
- Unique students reached.
- Average comprehension score.

**8.7 Full Story Reader.** The brand partner can request the full text of any narrative where their product appeared. The system returns all chapters with content, along with metadata indicating which chapters contain brand mentions and the specific terms found.

### 9. Consent Architecture and Privacy Controls

**9.1 Parental Consent Gate.** Brand content integration is strictly opt-in. The `allow_brand_stories` flag in the student's `ad_preferences` defaults to `false`. A guardian must take affirmative action to enable brand-integrated content for their child. This consent can be revoked at any time.

**9.2 Granular Category Blocking.** Even after opting in, guardians maintain a `blocked_categories` list allowing them to exclude specific types of brands (e.g., "fast food," "sugary beverages," "electronics") from their child's content.

**9.3 Age-Appropriate Filtering.** Brands define `target_ages` ranges. The system automatically excludes brands whose target age ranges do not include the student's age.

**9.4 Budget-Limited Exposure.** Each brand's total impression capacity is bounded by its `budget_total`. Once `budget_spent` reaches the total, the brand is automatically excluded from further content generation, preventing unlimited student exposure.

**9.5 Student Authentication Isolation.** Student accounts are created and managed exclusively by guardians or teachers. Students authenticate with unique student codes and numeric PINs, not email/password combinations, minimizing the collection of personally identifiable information.

### 10. Multi-Role Access Control System

The platform implements a five-tier RBAC system, each role having distinct capabilities:

| Role | Capabilities |
|---|---|
| **Administrator** | Full platform control: user management, word bank CRUD, contest management, billing configuration, LLM model selection, feature flags, brand approval, system-wide analytics |
| **Guardian/Parent** | Student management, word bank assignment, wallet management, referral program participation, progress monitoring, advertising preference controls |
| **Teacher** | Classroom session management, real-time WebSocket-based group reading sessions, student performance tracking |
| **Student** | Story reading, vocabulary assessments, spelling practice, progress tracking |
| **Brand Partner** | Campaign creation, budget management, impression analytics, product catalog management, story integration analytics, coupon creation |

### 11. Additional Novel Features

**11.1 Multi-Tier Word Bank Ecosystem.** The system supports three tiers of word bank creation: (a) Admin-managed public word banks (categorized as included, free, paid, or specialized), (b) Parent-created private word banks (automatically set to private visibility, only accessible to the creator and their linked students), and (c) a marketplace for discovery and assignment.

**11.2 Real-Time Classroom Sessions.** Teachers can initiate live reading sessions via WebSocket connections. Students join in real time, with the teacher controlling pacing and broadcasting comprehension questions.

**11.3 Dynamic Currency and Geolocation.** The platform detects the user's country via IP geolocation and displays all monetary values in the user's local currency using live exchange rates from an external API.

**11.4 Referral Contest System.** Administrators can create time-bound referral contests with configurable prizes and a live leaderboard.

**11.5 Brand Impression Economics.** Brands set campaign budgets and cost-per-impression rates. Each story generation event that includes brand content debits the brand's budget and records a monetizable impression.

---

## CLAIMS

### Independent Claims

**Claim 1.** A computer-implemented method for generating personalized educational content with integrated brand product placements, comprising:

(a) receiving, by a processor, a content generation request associated with a student identifier;

(b) retrieving, from a database, a student profile associated with the student identifier, the student profile comprising at least: age, grade level, interests, a belief system identifier, a cultural context identifier, a language preference, advertising preferences including a brand content opt-in flag and a blocked categories list, and at least one assigned word bank identifier;

(c) retrieving, from the database, vocabulary data from each assigned word bank, the vocabulary data comprising baseline words, target words, and stretch words;

(d) selecting vocabulary according to a tiered distribution comprising approximately 60% baseline words, approximately 30% target words, and approximately 10% stretch words, with randomized selection from the retrieved vocabulary data;

(e) determining, based on the advertising preferences, whether brand integration is authorized for the student;

(f) when brand integration is authorized, executing a real-time brand eligibility engine comprising:
   (i) querying the database for active brand records;
   (ii) filtering the active brand records based on at least: the student's age relative to each brand's target age range, the student's blocked categories relative to each brand's target categories, and each brand's remaining campaign budget;
   (iii) selecting a subset of eligible brand records not exceeding a configurable maximum;

(g) constructing a composite prompt for a Large Language Model, the composite prompt incorporating: the student profile data, the selected tiered vocabulary, the belief system identifier, the cultural context identifier, the language preference, character education directives, and, when brand integration is authorized, brand integration directives specifying that selected brand products are to be integrated as organic, problem-solving elements within the narrative;

(h) transmitting the composite prompt to the Large Language Model and receiving a structured response comprising a multi-chapter educational narrative with embedded vocabulary annotations and per-chapter comprehension questions;

(i) storing the generated narrative in the database with associated brand placement data; and

(j) recording, for each integrated brand, a brand impression record linking the brand to the narrative, the student, and the products featured, and updating the brand's campaign budget accordingly.

**Claim 2.** A computer-implemented method for providing closed-loop brand engagement analytics from AI-generated educational content, comprising:

(a) receiving, by a processor, an analytics request from a brand partner associated with a brand identifier;

(b) identifying, from a database, all educational narratives containing content related to the brand, using a multi-layer search comprising:
   (i) querying structured brand placement data stored on narrative records;
   (ii) querying brand impression records to identify additional narrative associations; and
   (iii) performing full-text search across narrative chapter content for the brand name and product names;

(c) extracting, from each identified narrative, specific text excerpts from chapter content where the brand name or product names appear;

(d) identifying comprehension questions within the identified narratives that are related to the brand, based on at least one of: direct appearance of brand or product names in the question text, direct appearance of brand or product names in the expected answer, the question pertaining to a product category and the corresponding chapter containing brand content, or contextual proximity of question keywords to brand mentions in chapter content;

(e) retrieving student interaction data for each identified brand-related comprehension question, comprising at least: total student attempts, number of correct responses, and number of incorrect responses;

(f) computing summary statistics comprising at least: total stories featuring the brand, total brand mentions, total brand-related questions, total question attempts, pass rate, and unique students reached; and

(g) transmitting the extracted excerpts, identified questions with performance data, and summary statistics to the brand partner.

**Claim 3.** A computer-implemented system for generating personalized, brand-integrated educational content, comprising:

(a) a database storing student profiles, word banks, brand records, and generated narratives;

(b) a student profile assembly module configured to retrieve and aggregate a multi-dimensional student profile comprising demographic data, interests, belief system identifier, cultural context identifier, language preference, strengths description, weaknesses description, and advertising preferences;

(c) a vocabulary selection module configured to retrieve words from assigned word banks and select vocabulary according to a 60/30/10 tiered distribution with randomized ordering;

(d) a brand eligibility engine configured to, at the time of each content generation request, query the database for active brands and apply multi-factor filtering comprising age appropriateness, guardian consent verification, category restriction enforcement, and budget availability verification;

(e) a prompt construction module configured to synthesize the student profile, selected vocabulary, and eligible brand data into a composite Large Language Model prompt that directs generation of a multi-chapter educational narrative with brand products integrated as organic, problem-solving story elements;

(f) an AI generation module configured to transmit the composite prompt to a Large Language Model and parse the structured response;

(g) an impression recording module configured to create brand impression records and update brand campaign budgets for each brand integration; and

(h) a brand analytics module configured to: identify all narratives containing a brand's content using multi-layer search, extract brand-mention excerpts, identify brand-related comprehension questions, retrieve student interaction data for those questions, and present the aggregated data to the brand partner.

### Dependent Claims

**Claim 4.** The method of Claim 1, wherein the belief system identifier directs the Large Language Model to generate character behaviors, moral lessons, and decision-making frameworks consistent with the specified belief system.

**Claim 5.** The method of Claim 1, wherein the cultural context identifier directs the Large Language Model to incorporate culturally relevant names, settings, traditions, foods, and customs in the generated narrative.

**Claim 6.** The method of Claim 1, further comprising:

(k) receiving, from the student, responses to the per-chapter comprehension questions;

(l) logging each response with an indication of correctness;

(m) generating a vocabulary assessment comprising questions for each target-tier and stretch-tier word appearing in the narrative;

(n) evaluating student assessment responses using a second Large Language Model invocation configured to assess definition accuracy, contextual sentence usage, and spelling quality; and

(o) updating the student profile with newly mastered vocabulary tokens when assessment accuracy meets or exceeds a threshold (80%).

**Claim 7.** The method of Claim 6, further comprising computing an Agentic Reach Score for the student based on the formula:

```
Score = min((|mastered_tokens| x W1 + completed_narratives x W2) / max(total_narratives x W2, 1) x 100, 100.0)
```

where W1 and W2 are configurable weighting factors.

**Claim 8.** The method of Claim 1, wherein the composite prompt further incorporates a strengths directive instructing the Large Language Model to portray the narrative protagonist as exhibiting the student's documented strengths, and a growth areas directive instructing the Large Language Model to model the protagonist struggling with and gradually overcoming challenges related to the student's documented growth areas without shame or deficit framing.

**Claim 9.** The method of Claim 2, wherein the multi-layer search of step (b) ensures comprehensive coverage of narratives generated before and after implementation of structured brand placement tracking, by combining database field queries, cross-reference table queries, and full-text content search.

**Claim 10.** The method of Claim 2, wherein the identification of brand-related comprehension questions in step (d) further comprises:

extracting individual significant words from multi-word brand product names and using those extracted words as additional search terms when matching question text and expected answers.

**Claim 11.** The method of Claim 1, wherein the real-time brand eligibility engine of step (f) operates against the live state of the brand database such that the brand composition of each generated narrative reflects: currently active brands, current budget availability, and current guardian preferences at the instant of the generation request.

**Claim 12.** The method of Claim 1, wherein the advertising preferences further comprise a default-false brand content opt-in flag requiring affirmative guardian action before any brand content is integrated into the student's educational narratives.

**Claim 13.** The system of Claim 3, further comprising a cost logging module configured to record, for each content generation event, the AI model used, estimated token consumption, estimated monetary cost, generation duration, and success status, enabling per-student and per-brand cost attribution.

**Claim 14.** The method of Claim 2, further comprising:

(h) providing the brand partner with access to the full text of any identified narrative, with indications of which chapters contain brand mentions and the specific terms found therein.

**Claim 15.** The system of Claim 3, wherein the brand analytics module further aggregates free-text written student responses from students who interacted with brand-containing narratives, each response comprising the question posed, the student's verbatim answer, pass/fail status, and a comprehension score, and presents these aggregated responses to the brand partner.

---

## ABSTRACT

A computer-implemented system and method for generating personalized, AI-driven educational narratives that dynamically integrate brand product placements as organic, problem-solving story elements. The system assembles a multi-dimensional student profile comprising demographic, cultural, religious, linguistic, developmental, and interest-based data. At the time of each content generation request, a real-time brand eligibility engine queries a live brand marketplace database and applies multi-factor filtering based on student age, guardian consent, category restrictions, and brand budget availability. A composite prompt synthesizes the student profile, a three-tier (60/30/10) vocabulary distribution, and brand integration directives for a Large Language Model, which generates a structured multi-chapter educational narrative. The system records brand impressions and updates campaign budgets in real time. A closed-loop analytics pipeline identifies all narratives containing a brand's content through multi-layer search, extracts specific story excerpts with brand mentions, identifies brand-related comprehension questions, retrieves student interaction data (attempts, pass/fail rates), and presents comprehensive engagement analytics to the brand partner. The system further includes AI-powered vocabulary assessment evaluation, mastery tracking with an Agentic Reach Score, and a consent-gated privacy architecture requiring affirmative guardian opt-in for brand content.

---

## OATH/DECLARATION

I hereby declare that all statements made herein of my own knowledge are true and that all statements made on information and belief are believed to be true; and further that these statements were made with the knowledge that willful false statements and the like so made are punishable by fine or imprisonment, or both, under 18 U.S.C. 1001 and that such willful false statements may jeopardize the validity of the application or any patent issued thereon.

**Signature:** ____________________________________

**Date:** ____________________________________

**Printed Name:** ____________________________________

---

*Document Version: 1.0*
*Prepared: February 2026*
*Status: DRAFT — For Attorney Review and Filing*

---

## APPENDIX A: KEY DATA MODEL SCHEMAS

### A.1 Student Profile Schema
```json
{
  "id": "UUID",
  "full_name": "string",
  "age": "integer",
  "grade_level": "enum (pre-k, k, 1-12, college, adult)",
  "interests": ["string"],
  "virtues": ["string"],
  "strengths": "string (free-text, parent-authored)",
  "weaknesses": "string (free-text, parent-authored)",
  "belief_system": "string",
  "cultural_context": "string",
  "language": "string",
  "assigned_banks": ["word_bank_id"],
  "ad_preferences": {
    "allow_brand_stories": "boolean (default: false)",
    "blocked_categories": ["string"]
  },
  "mastered_tokens": ["string (normalized lowercase)"],
  "agentic_reach_score": "float (0-100)"
}
```

### A.2 Word Bank Schema
```json
{
  "id": "UUID",
  "name": "string",
  "category": "enum (included, free, paid, specialized)",
  "visibility": "enum (public, private)",
  "created_by": "user_id",
  "created_by_role": "enum (admin, guardian, teacher)",
  "baseline_words": [{"word": "string", "definition": "string", "example_sentence": "string"}],
  "target_words": [{"word": "string", "definition": "string", "example_sentence": "string"}],
  "stretch_words": [{"word": "string", "definition": "string", "example_sentence": "string"}]
}
```

### A.3 Brand Schema
```json
{
  "id": "UUID",
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

### A.4 Narrative Schema
```json
{
  "id": "UUID",
  "title": "string",
  "student_id": "UUID",
  "bank_ids": ["UUID"],
  "theme": "string",
  "chapters": [{
    "number": "integer",
    "title": "string",
    "content": "string (300-500 words)",
    "word_count": "integer",
    "embedded_tokens": [{"word": "string", "tier": "enum (baseline, target, stretch)"}],
    "vision_check": {
      "question": "string",
      "options": ["string (4 options)"],
      "correct_index": "integer"
    }
  }],
  "total_word_count": "integer",
  "tokens_to_verify": ["string"],
  "brand_placements": [{
    "id": "UUID",
    "name": "string",
    "products": [{"name": "string", "description": "string"}],
    "problem_statement": "string"
  }],
  "status": "enum (generating, ready, in_progress, completed)"
}
```

### A.5 Brand Impression Schema
```json
{
  "id": "UUID",
  "brand_id": "UUID",
  "brand_name": "string",
  "narrative_id": "UUID",
  "student_id": "UUID",
  "guardian_id": "UUID",
  "products_featured": ["string"],
  "cost": "float",
  "created_date": "ISO-8601 datetime"
}
```

### A.6 Written Answer Schema
```json
{
  "student_id": "UUID",
  "chapter_number": "integer",
  "question": "string",
  "student_answer": "string",
  "passed": "boolean",
  "comprehension_score": "integer (0-100)",
  "feedback": "string",
  "created_date": "ISO-8601 datetime"
}
```

### A.7 Read Log Schema
```json
{
  "narrative_id": "UUID",
  "chapter_number": "integer",
  "student_id": "UUID",
  "vision_check_passed": "boolean",
  "created_date": "ISO-8601 datetime"
}
```

---

## APPENDIX B: COMPETITIVE LANDSCAPE ANALYSIS

| Feature | Semantic Vision (Present Invention) | Duolingo | Khan Academy | Reading IQ | ABCmouse |
|---|:---:|:---:|:---:|:---:|:---:|
| AI-Generated Personalized Multi-Chapter Stories | YES | No | No | No | No |
| Belief System Adaptation in Content | YES | No | No | No | No |
| Cultural Context Integration | YES | No | No | No | No |
| Real-Time Brand Product Integration in Narrative | YES | No | No | No | No |
| 60/30/10 Tiered Vocabulary Distribution | YES | No | No | No | No |
| Consent-Gated, Non-Intrusive Brand Content | YES | N/A | N/A | N/A | N/A |
| Closed-Loop Brand Engagement Analytics | YES | No | No | No | No |
| Multi-Role Platform (5 roles) | YES | No | Partial | No | Partial |
| 20+ Language Support for Generated Content | YES | Yes | No | No | No |
| Guardian Ad Preference Controls | YES | N/A | N/A | N/A | N/A |
| Strengths/Weaknesses-Aware Narrative | YES | No | No | No | No |
| Real-Time Classroom WebSocket Sessions | YES | No | No | No | No |
| AI-Powered Assessment Evaluation | YES | Partial | Partial | No | No |
| Brand Impression Economics | YES | No | No | No | No |
| Per-Brand Story Excerpt Analytics | YES | No | No | No | No |
| Brand Activation Question Tracking | YES | No | No | No | No |

---

*END OF PROVISIONAL PATENT APPLICATION*
