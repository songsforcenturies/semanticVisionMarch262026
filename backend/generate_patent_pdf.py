"""Generate PDF of Provisional Patent Application with CONFIDENTIAL watermark"""
import os
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# Timestamp for the document
NOW = datetime.now(timezone.utc)
DATE_STR = NOW.strftime("%B %d, %Y")
TIME_STR = NOW.strftime("%I:%M %p UTC")
DATETIME_STR = f"{DATE_STR} at {TIME_STR}"


def add_watermark_and_footer(canvas, doc):
    """Draw CONFIDENTIAL watermark and date/time footer on every page"""
    canvas.saveState()
    
    # --- CONFIDENTIAL watermark (diagonal, semi-transparent) ---
    canvas.setFont("Helvetica-Bold", 72)
    canvas.setFillColor(Color(0.85, 0.85, 0.85, alpha=0.35))
    canvas.translate(letter[0] / 2, letter[1] / 2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "CONFIDENTIAL")
    canvas.rotate(-45)
    canvas.translate(-letter[0] / 2, -letter[1] / 2)

    # --- Second smaller CONFIDENTIAL near top ---
    canvas.setFont("Helvetica-Bold", 36)
    canvas.setFillColor(Color(0.85, 0.85, 0.85, alpha=0.25))
    canvas.translate(letter[0] / 2, letter[1] * 0.82)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "CONFIDENTIAL")
    canvas.rotate(-45)
    canvas.translate(-letter[0] / 2, -letter[1] * 0.82)

    # --- Third smaller CONFIDENTIAL near bottom ---
    canvas.translate(letter[0] / 2, letter[1] * 0.22)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "CONFIDENTIAL")
    canvas.rotate(-45)
    canvas.translate(-letter[0] / 2, -letter[1] * 0.22)

    # --- Footer with date, time, and page number ---
    canvas.setFillColor(HexColor("#666666"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(0.75 * inch, 0.4 * inch, f"CONFIDENTIAL — Generated: {DATETIME_STR}")
    canvas.drawRightString(letter[0] - 0.75 * inch, 0.4 * inch, f"Page {doc.page}")

    # --- Top header bar ---
    canvas.setFillColor(HexColor("#CC0000"))
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(0.75 * inch, letter[1] - 0.4 * inch, "CONFIDENTIAL — PRIVILEGED & PROPRIETARY")
    canvas.drawRightString(letter[0] - 0.75 * inch, letter[1] - 0.4 * inch, DATETIME_STR)

    canvas.restoreState()


def build_pdf():
    output_path = "/app/Semantic_Vision_Provisional_Patent_Application.pdf"
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "PatentTitle", parent=styles["Title"],
        fontSize=18, leading=22, spaceAfter=6,
        textColor=HexColor("#1a1a2e"), alignment=TA_CENTER
    )
    h1_style = ParagraphStyle(
        "H1", parent=styles["Heading1"],
        fontSize=16, leading=20, spaceBefore=20, spaceAfter=8,
        textColor=HexColor("#1a1a2e"), borderWidth=1,
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontSize=13, leading=16, spaceBefore=14, spaceAfter=6,
        textColor=HexColor("#2d2d5e"),
    )
    h3_style = ParagraphStyle(
        "H3", parent=styles["Heading3"],
        fontSize=11, leading=14, spaceBefore=10, spaceAfter=4,
        textColor=HexColor("#3a3a7a"),
    )
    body_style = ParagraphStyle(
        "PatentBody", parent=styles["Normal"],
        fontSize=10, leading=13.5, spaceAfter=6,
        alignment=TA_JUSTIFY, textColor=black,
    )
    body_indent = ParagraphStyle(
        "PatentBodyIndent", parent=body_style,
        leftIndent=24, spaceAfter=4,
    )
    claim_style = ParagraphStyle(
        "ClaimStyle", parent=body_style,
        leftIndent=12, spaceAfter=4,
    )
    sub_claim_style = ParagraphStyle(
        "SubClaimStyle", parent=body_style,
        leftIndent=36, spaceAfter=3,
    )
    code_style = ParagraphStyle(
        "CodeStyle", parent=styles["Code"],
        fontSize=8, leading=10, spaceAfter=6,
        leftIndent=18, backColor=HexColor("#f5f5f5"),
    )
    center_style = ParagraphStyle(
        "Center", parent=body_style, alignment=TA_CENTER,
    )
    confidential_banner = ParagraphStyle(
        "ConfBanner", parent=styles["Normal"],
        fontSize=14, leading=18, alignment=TA_CENTER,
        textColor=HexColor("#CC0000"), spaceBefore=4, spaceAfter=4,
    )

    elements = []

    # ===== COVER PAGE =====
    elements.append(Spacer(1, 1.5 * inch))
    elements.append(Paragraph(
        '<b>CONFIDENTIAL</b>', confidential_banner
    ))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(
        "PROVISIONAL PATENT APPLICATION", title_style
    ))
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Paragraph(
        "UNITED STATES PATENT AND TRADEMARK OFFICE", center_style
    ))
    elements.append(Spacer(1, 0.4 * inch))
    elements.append(Paragraph(
        '<b>System and Method for Real-Time, Contextual Integration of Brand Product Placements '
        'as Narrative Solutions Within AI-Generated, Personalized Educational Content Adapted to '
        'User Belief Systems, Cultural Contexts, Developmental Profiles, and Vocabulary Acquisition '
        'Goals, With Closed-Loop Brand Engagement Analytics</b>',
        ParagraphStyle("TitleBlock", parent=body_style, fontSize=12, leading=16, alignment=TA_CENTER, spaceBefore=12, spaceAfter=12)
    ))
    elements.append(Spacer(1, 0.5 * inch))
    
    cover_data = [
        ["Application Type:", "Provisional Patent Application under 35 U.S.C. 111(b)"],
        ["Filing Date:", "[TO BE COMPLETED BY ATTORNEY]"],
        ["Applicant(s):", "[TO BE COMPLETED BY ATTORNEY]"],
        ["Document Generated:", DATETIME_STR],
        ["Status:", "DRAFT — For Attorney Review and Filing"],
    ]
    cover_table = Table(cover_data, colWidths=[2 * inch, 4.5 * inch])
    cover_table.setStyle(TableStyle([
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 10),
        ("FONT", (1, 0), (1, -1), "Helvetica", 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
    ]))
    elements.append(cover_table)
    elements.append(Spacer(1, 1 * inch))
    elements.append(Paragraph(
        f'<b>CONFIDENTIAL — PRIVILEGED &amp; PROPRIETARY</b><br/>'
        f'This document contains confidential information. Unauthorized reproduction or distribution is prohibited.',
        ParagraphStyle("ConfNote", parent=body_style, fontSize=9, alignment=TA_CENTER, textColor=HexColor("#CC0000"))
    ))
    elements.append(PageBreak())

    # ===== TABLE OF CONTENTS =====
    elements.append(Paragraph("TABLE OF CONTENTS", h1_style))
    elements.append(Spacer(1, 0.15 * inch))
    toc_items = [
        "1. Field of the Invention",
        "2. Background of the Invention",
        "3. Summary of the Invention",
        "4. Brief Description of Drawings",
        "5. Detailed Description of Preferred Embodiments",
        "    5.1 System Architecture Overview",
        "    5.2 Multi-Dimensional Student Profile Assembly",
        "    5.3 Three-Tier Vocabulary Distribution (60/30/10)",
        "    5.4 Real-Time Brand Eligibility Engine",
        "    5.5 Composite AI Prompt Construction",
        "    5.6 AI Story Generation and Post-Processing",
        "    5.7 Student Interaction and Assessment Pipeline",
        "    5.8 Closed-Loop Brand Analytics Pipeline",
        "    5.9 Consent Architecture and Privacy Controls",
        "    5.10 Multi-Role Access Control System",
        "    5.11 Additional Novel Features",
        "6. Claims (30 total: 5 Independent + 25 Dependent/Expanded)",
        "7. Abstract",
        "Appendix A: Key Data Model Schemas",
        "Appendix B: Competitive Landscape Analysis",
    ]
    for item in toc_items:
        indent = 24 if item.startswith("    ") else 0
        elements.append(Paragraph(
            item.strip(),
            ParagraphStyle("TOC", parent=body_style, leftIndent=indent, spaceAfter=3)
        ))
    elements.append(PageBreak())

    # ===== FIELD OF THE INVENTION =====
    elements.append(Paragraph("1. FIELD OF THE INVENTION", h1_style))
    elements.append(Paragraph(
        "The present invention relates generally to artificial intelligence-driven educational content generation, "
        "and more particularly, to a computer-implemented system and method for dynamically integrating commercial "
        "brand products into personalized, multi-chapter educational narratives as organic, problem-solving story "
        "elements, while simultaneously providing real-time analytics on student engagement with said branded content "
        "back to brand sponsors.",
        body_style
    ))

    # ===== BACKGROUND =====
    elements.append(Paragraph("2. BACKGROUND OF THE INVENTION", h1_style))
    elements.append(Paragraph("2.1 Technical Problem", h2_style))
    elements.append(Paragraph(
        "The field of educational technology (\"EdTech\") has long faced three persistent and interrelated challenges:",
        body_style
    ))
    
    bg_problems = [
        ("<b>Static, One-Size-Fits-All Content.</b> Existing vocabulary and reading platforms (e.g., Duolingo, Khan Academy, "
         "Reading IQ, ABCmouse) rely on pre-authored, static content libraries. These platforms cannot dynamically personalize "
         "educational narratives to reflect a student's individual religion, cultural heritage, specific interests, character "
         "development goals, personal strengths, or areas of growth."),
        ("<b>Intrusive, Educationally Disruptive Monetization.</b> The predominant monetization models in EdTech — banner "
         "advertisements, interstitial video ads, and hard paywalls — interrupt the learning experience. No existing system "
         "integrates brand messaging <i>within</i> educational content in a way that adds educational value rather than detracting from it."),
        ("<b>Absence of Measurable Brand-Education Feedback Loops.</b> Even in platforms that accept advertising, brands receive "
         "only surface-level metrics (click-through rates, impressions counted by page loads). No existing system provides brands "
         "with granular analytics showing the exact narrative context in which their product appeared, specific comprehension "
         "questions generated about their product integration, student pass/fail rates on those questions, or the full text of the "
         "educational content where the product was featured."),
    ]
    for p in bg_problems:
        elements.append(Paragraph(p, body_indent))

    elements.append(Paragraph("2.2 Prior Art Limitations", h2_style))
    elements.append(Paragraph(
        "A survey of existing systems reveals no prior art combining all of the following capabilities in a single integrated platform:",
        body_style
    ))
    
    prior_art_data = [
        ["Capability", "Status in Prior Art"],
        ["AI-generated personalized educational narratives", "No commercial system generates multi-chapter stories personalized across belief, culture, strengths/weaknesses, and vocabulary tiers simultaneously"],
        ["Real-time brand product integration as narrative elements", "No known prior art"],
        ["Consent-gated, guardian-controlled brand content in education", "No known prior art"],
        ["Tiered vocabulary distribution (60/30/10)", "No known prior art"],
        ["Closed-loop brand analytics with story excerpts", "No known prior art"],
        ["Belief system and cultural context-aware AI generation", "No known prior art in educational narrative generation"],
    ]
    pa_table = Table(prior_art_data, colWidths=[3 * inch, 3.5 * inch])
    pa_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f8f8f8")]),
    ]))
    elements.append(pa_table)

    # ===== SUMMARY =====
    elements.append(PageBreak())
    elements.append(Paragraph("3. SUMMARY OF THE INVENTION", h1_style))
    elements.append(Paragraph(
        "The present invention provides a computer-implemented platform (\"Semantic Vision\") comprising a real-time "
        "content generation pipeline that:",
        body_style
    ))
    
    summary_items = [
        "<b>(1)</b> Assembles a multi-dimensional student profile from demographic, cultural, religious, linguistic, "
        "developmental, and interest-based data, including parent-authored descriptions of the child's strengths and growth areas.",
        
        "<b>(2)</b> Selects vocabulary according to a novel three-tier distribution model (60% Baseline / 30% Target / "
        "10% Stretch) from dynamically assigned word banks, with randomized selection ensuring unique vocabulary combinations "
        "per generation event.",
        
        "<b>(3)</b> Executes a real-time brand eligibility engine that, at the instant of each content generation request, "
        "queries a live brand marketplace database, applies multi-factor filtering (age appropriateness, guardian consent, "
        "category restrictions, budget availability), and selects up to a configurable maximum number of eligible brand sponsors.",
        
        "<b>(4)</b> Constructs a composite AI prompt incorporating all of the foregoing elements and directs a Large Language "
        "Model to generate a structured, multi-chapter educational narrative in which brand products appear as organic, "
        "problem-solving elements.",
        
        "<b>(5)</b> Records brand impressions, updates brand budgets, and logs economic data in real time.",
        
        "<b>(6)</b> Generates context-aware comprehension questions per chapter, including questions that test the student's "
        "understanding of narrative elements involving the integrated brand products.",
        
        "<b>(7)</b> Evaluates student responses using a secondary LLM evaluation pipeline, tracking mastery of vocabulary tokens "
        "and comprehension performance.",
        
        "<b>(8)</b> Closes the analytics loop by providing brand sponsors with a detailed dashboard comprising: exact story excerpts "
        "where their products were mentioned, specific \"brand activation questions\" asked of students, pass/fail statistics, "
        "free-text student responses, and the ability to read the full narrative text.",
    ]
    for item in summary_items:
        elements.append(Paragraph(item, body_indent))
    
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(
        "<b>No single prior art system or obvious combination of prior art systems teaches or suggests this integrated approach.</b>",
        body_style
    ))

    # ===== BRIEF DESCRIPTION OF DRAWINGS =====
    elements.append(Paragraph("4. BRIEF DESCRIPTION OF THE DRAWINGS", h1_style))
    figures = [
        "<b>FIG. 1</b> — System architecture overview showing the relationship between the frontend client application, backend API server, database layer, AI engine, and payment processor.",
        "<b>FIG. 2</b> — Detailed data flow diagram of the Real-Time Brand Integration Pipeline (Steps 1-6).",
        "<b>FIG. 3</b> — Entity relationship diagram showing key data models: Student Profile, Word Bank, Brand, Narrative, Brand Impression, Assessment, Written Answer, and Read Log.",
        "<b>FIG. 4</b> — Flowchart of the Brand Eligibility Engine showing multi-factor filtering logic.",
        "<b>FIG. 5</b> — Diagram of the Closed-Loop Brand Analytics Pipeline showing data flow from narrative generation through student interaction to brand dashboard presentation.",
        "<b>FIG. 6</b> — Screenshot representations of the Brand Analytics Dashboard showing story excerpts, activation questions, and student response data.",
    ]
    for fig in figures:
        elements.append(Paragraph(fig, body_indent))
    elements.append(Paragraph(
        "<i>Note: Formal drawings to be prepared by patent illustrator prior to non-provisional filing.</i>",
        ParagraphStyle("Note", parent=body_style, fontSize=9, textColor=HexColor("#666666"))
    ))

    # ===== DETAILED DESCRIPTION =====
    elements.append(PageBreak())
    elements.append(Paragraph("5. DETAILED DESCRIPTION OF THE PREFERRED EMBODIMENTS", h1_style))

    # 5.1 System Architecture
    elements.append(Paragraph("5.1 System Architecture Overview (FIG. 1)", h2_style))
    elements.append(Paragraph(
        "The preferred embodiment comprises a distributed computing system with the following components:",
        body_style
    ))
    arch_items = [
        "<b>Backend Application Server.</b> A Python-based asynchronous web application server built on the FastAPI framework, providing RESTful API endpoints. Implements role-based access control (RBAC) using JWT for five distinct user roles: Administrator, Guardian/Parent, Teacher, Student, and Brand Partner.",
        "<b>Database Layer.</b> A MongoDB document-oriented database accessed via the Motor asynchronous driver, storing all user profiles, student records, word banks, brand records, narratives, assessments, brand impressions, read logs, written answers, and system configuration.",
        "<b>AI Engine.</b> A Large Language Model integration layer supporting multiple providers (including OpenAI GPT-5.2 and configurable alternatives), used for: (a) multi-chapter educational narrative generation, and (b) student response evaluation.",
        "<b>Frontend Client Application.</b> A React 18 single-page application with role-specific portals for each user type.",
        "<b>Payment Processing Layer.</b> A Stripe API integration providing wallet top-up and budget management functionality.",
    ]
    for item in arch_items:
        elements.append(Paragraph(item, body_indent))

    # 5.2 Student Profile
    elements.append(Paragraph("5.2 Multi-Dimensional Student Profile Assembly (FIG. 2, Step 1)", h2_style))
    elements.append(Paragraph(
        "The system maintains a comprehensive student profile record comprising the following data fields, each contributing to content personalization:",
        body_style
    ))
    profile_fields = [
        "<b>Demographic Data:</b> Full name, age (integer), grade level (pre-K through adult).",
        "<b>Interest Graph:</b> List of student interests used to theme generated narratives.",
        "<b>Character Education Virtues:</b> List of virtues (e.g., \"courage,\" \"honesty\") modeled through character behavior.",
        "<b>Belief System Identifier:</b> Directs AI to reflect corresponding values, teachings, and moral frameworks. Characters demonstrate behaviors consistent with the specified belief system's principles.",
        "<b>Cultural Context Identifier:</b> Directs AI to incorporate culturally relevant names, settings, traditions, foods, and customs with respectful and authentic representation.",
        "<b>Language Preference:</b> Supports 20+ languages for full narrative generation including titles, content, vocabulary explanations, and comprehension questions.",
        "<b>Strengths Description:</b> Free-text parent-authored field. AI celebrates these as protagonist \"superpowers.\"",
        "<b>Weaknesses/Growth Areas:</b> Free-text parent-authored field. AI models growth through empathetic character development — never shame or deficit framing.",
        "<b>Advertising Preferences:</b> Boolean opt-in flag (<i>allow_brand_stories</i>, default: false) and guardian-controlled <i>blocked_categories</i> list.",
        "<b>Vocabulary State:</b> Assigned word banks, mastered tokens (normalized strings), and Agentic Reach Score (0-100).",
    ]
    for field in profile_fields:
        elements.append(Paragraph(field, body_indent))

    # 5.3 Vocabulary Tiers
    elements.append(Paragraph("5.3 Three-Tier Vocabulary Distribution System (60/30/10 Model)", h2_style))
    elements.append(Paragraph(
        "The invention implements a novel vocabulary distribution model inspired by educational scaffolding theory. At each content generation event:",
        body_style
    ))
    vocab_steps = [
        "Retrieves all word banks assigned to the student. Each bank contains three categorized lists: baseline_words, target_words, and stretch_words.",
        "Aggregates words from all assigned banks into three master lists.",
        "Randomly shuffles each master list to ensure non-repeating vocabulary sequences.",
        "Selects words: <b>60% Baseline (18 words max)</b> — reinforcement; <b>30% Target (9 words max)</b> — primary learning; <b>10% Stretch (3 words max)</b> — aspirational challenge.",
    ]
    for i, step in enumerate(vocab_steps, 1):
        elements.append(Paragraph(f"({i}) {step}", body_indent))
    elements.append(Paragraph(
        "This distribution ensures each narrative contains a pedagogically sound mixture of reinforcement, primary instruction, "
        "and aspirational challenge. Random shuffling guarantees no two narratives present the same vocabulary sequence even from the same word banks.",
        body_style
    ))

    # 5.4 Brand Eligibility Engine
    elements.append(PageBreak())
    elements.append(Paragraph("5.4 Real-Time Brand Eligibility Engine (FIG. 4)", h2_style))
    elements.append(Paragraph(
        "This subsystem represents a <b>core novel aspect</b> of the present invention. At the precise moment a content generation "
        "request is received, the system executes the following multi-factor filtering pipeline:",
        body_style
    ))
    brand_steps = [
        "<b>System-Level Feature Gate:</b> Checks a globally configurable feature flag (brand_sponsorship_enabled). If disabled, no brand integration occurs.",
        "<b>Guardian Consent Check:</b> Reads the student's ad_preferences.allow_brand_stories field. Defaults to false — requires affirmative guardian opt-in.",
        "<b>Active Brand Query:</b> Queries the brand database for all brands with is_active = true (up to 20 candidates).",
        "<b>Age Appropriateness Filter:</b> Checks if the student's age falls within each brand's target_ages range.",
        "<b>Budget Availability Check:</b> Verifies that budget_spent has not reached budget_total, preventing overspend.",
        "<b>Category Block List Check:</b> Cross-references brand target_categories against guardian's blocked_categories. Excludes on any overlap.",
        "<b>Selection and Limit:</b> Selects up to 2 eligible brands per narrative (configurable maximum).",
        "<b>Dynamic Composition:</b> Because the engine runs against live database state at each request, every narrative has a potentially unique brand composition.",
    ]
    for step in brand_steps:
        elements.append(Paragraph(step, body_indent))

    # 5.5 Prompt Construction
    elements.append(Paragraph("5.5 Composite AI Prompt Construction (FIG. 2, Step 4)", h2_style))
    elements.append(Paragraph(
        "The system constructs a comprehensive prompt synthesizing all dimensions of personalization:",
        body_style
    ))
    prompt_sections = [
        "<b>Student Profile Section:</b> Name, age, grade level, interests, virtues.",
        "<b>Vocabulary Distribution Section:</b> Baseline, target, stretch words with tier designations.",
        "<b>Character Education Directive:</b> Weave lessons about virtues through character behavior.",
        "<b>Belief System Alignment Directive:</b> Reflect corresponding values and teachings.",
        "<b>Cultural Context Integration Directive:</b> Incorporate culturally relevant elements.",
        "<b>Language Directive:</b> Generate entire narrative in specified language.",
        "<b>Brand Integration Directive (KEY NOVEL SECTION):</b> \"Naturally weave these brands into the story as helpful solutions to problems the characters face. Focus on how each brand's products solve a real problem relevant to the story. Make brand mentions feel organic and educational, not like advertisements.\" Per-brand data includes: name, products, problem statement, logo URL.",
        "<b>Strengths/Growth Areas Directive:</b> Protagonist exhibits child's strengths; models growth in weak areas without shame.",
        "<b>Structural Requirements:</b> 5 chapters, 300-500 words each, vocabulary embedding, comprehension questions.",
        "<b>Output Schema:</b> Structured JSON with chapters, embedded token annotations, and vision checks.",
    ]
    for section in prompt_sections:
        elements.append(Paragraph(section, body_indent))

    # 5.6 Generation & Post-Processing
    elements.append(Paragraph("5.6 AI Story Generation and Post-Processing (FIG. 2, Steps 5-6)", h2_style))
    gen_items = [
        "<b>LLM Invocation:</b> Composite prompt transmitted to configured LLM (default: GPT-5.2). Supports configurable model selection and fallback chains.",
        "<b>Response Parsing:</b> JSON response parsed and validated. Embedded tokens verified against valid tiers. Vision checks validated with fallbacks.",
        "<b>Narrative Persistence:</b> Stored with all chapter content, token annotations, questions, word bank references, and brand placement data.",
        "<b>Brand Impression Recording:</b> For each brand placement: creates impression record, assigns configurable cost ($0.05 default), atomically updates brand counters (impressions, stories, budget_spent).",
        "<b>Cost Logging:</b> Records model used, provider, token estimates, cost estimate, duration, and success status for platform-wide cost monitoring.",
    ]
    for item in gen_items:
        elements.append(Paragraph(item, body_indent))

    # 5.7 Assessment Pipeline
    elements.append(Paragraph("5.7 Student Interaction and Assessment Pipeline", h2_style))
    assess_items = [
        "<b>Narrative Reading:</b> Per-chapter vision check (comprehension question). Response logged with pass/fail status.",
        "<b>Vocabulary Assessment Generation:</b> Creates questions for each target-tier and stretch-tier word. Student provides definition and contextual sentence.",
        "<b>AI-Powered Assessment Evaluation:</b> Second LLM invocation evaluates: definition accuracy, sentence correctness, spelling quality (configurable exact/phonetic mode). Returns per-word feedback.",
        "<b>Written Answer Evaluation:</b> Free-text comprehension responses evaluated by separate LLM pipeline. Stored in written_answers collection for brand analytics.",
        "<b>Mastery Tracking:</b> At 80%+ accuracy, mastered tokens merged into student profile (normalized lowercase strings). Agentic Reach Score recalculated: min((|mastered_tokens| x 10 + completed_narratives x 50) / max(total_narratives x 50, 1) x 100, 100.0).",
    ]
    for item in assess_items:
        elements.append(Paragraph(item, body_indent))

    # 5.8 Closed-Loop Analytics
    elements.append(PageBreak())
    elements.append(Paragraph("5.8 Closed-Loop Brand Analytics Pipeline (FIG. 5)", h2_style))
    elements.append(Paragraph(
        "This subsystem represents the <b>second major novel aspect</b> of the present invention: closing the feedback loop "
        "between brand integration in educational content and measurable student engagement analytics.",
        body_style
    ))
    analytics_items = [
        "<b>Three-Layer Narrative Discovery:</b> (1) Structured brand_placements field query; (2) brand_impressions cross-reference; (3) Full-text content search for brand/product names. Ensures comprehensive coverage regardless of when narratives were generated.",
        "<b>Story Excerpt Extraction:</b> Splits chapter content into sentences, filters for brand/product mentions, returns up to 5 excerpts per chapter with metadata.",
        "<b>Brand Activation Question Identification:</b> Multi-condition classification: (A) brand name in question/answer text; (B) product-category keywords + brand content in chapter; (C) answer contains brand-derived terms; (D) contextual proximity of question keywords to brand mentions.",
        "<b>Question Performance Analytics:</b> Per-question: total attempts, passed count, failed count from read_log entries.",
        "<b>Student Written Response Aggregation:</b> Free-text answers from all students who interacted with brand-containing narratives.",
        "<b>Summary Statistics:</b> Total stories, mentions, activation questions, attempts, pass rate, unique students reached, average comprehension score.",
        "<b>Full Story Reader:</b> Brand partner can access complete narrative text with brand mention indicators.",
    ]
    for item in analytics_items:
        elements.append(Paragraph(item, body_indent))

    # 5.9 Consent Architecture
    elements.append(Paragraph("5.9 Consent Architecture and Privacy Controls", h2_style))
    consent_items = [
        "<b>Parental Consent Gate:</b> Brand content is strictly opt-in (default: false). Guardian must take affirmative action. Revocable at any time.",
        "<b>Granular Category Blocking:</b> Guardian-maintained blocked_categories list excludes specific brand types.",
        "<b>Age-Appropriate Filtering:</b> Brands define target age ranges; system auto-excludes mismatches.",
        "<b>Budget-Limited Exposure:</b> Campaign budget caps prevent unlimited student exposure.",
        "<b>Student Authentication Isolation:</b> Students use codes and PINs, not email/password, minimizing PII collection.",
    ]
    for item in consent_items:
        elements.append(Paragraph(item, body_indent))

    # 5.10 Multi-Role Access Control
    elements.append(Paragraph("5.10 Multi-Role Access Control System", h2_style))
    role_data = [
        ["Role", "Capabilities"],
        ["Administrator", "Full platform control: user/word bank/brand/contest management, billing config, LLM model selection, feature flags, system analytics"],
        ["Guardian/Parent", "Student management, word bank assignment, wallet management, referral program, progress monitoring, ad preference controls"],
        ["Teacher", "Classroom session management, real-time WebSocket group reading sessions, student performance tracking"],
        ["Student", "Story reading, vocabulary assessments, spelling practice, progress tracking"],
        ["Brand Partner", "Campaign creation, budget management, impression analytics, product catalog, story integration analytics, coupon creation"],
    ]
    role_table = Table(role_data, colWidths=[1.5 * inch, 5 * inch])
    role_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
        ("FONT", (0, 1), (0, -1), "Helvetica-Bold", 8),
        ("FONT", (1, 1), (-1, -1), "Helvetica", 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f8f8f8")]),
    ]))
    elements.append(role_table)

    # 5.11 Additional Features
    elements.append(Paragraph("5.11 Additional Novel Features", h2_style))
    additional = [
        "<b>Multi-Tier Word Bank Ecosystem:</b> Admin-managed public banks (included/free/paid/specialized), parent-created private banks, and a discovery marketplace.",
        "<b>Real-Time Classroom Sessions:</b> WebSocket-based live reading sessions with teacher-controlled pacing.",
        "<b>Dynamic Currency and Geolocation:</b> IP-based country detection with live exchange rate conversion for all monetary displays.",
        "<b>Referral Contest System:</b> Time-bound contests with configurable prizes and live leaderboard.",
        "<b>Brand Impression Economics:</b> Per-impression budgets with real-time debit and ROI metrics.",
    ]
    for item in additional:
        elements.append(Paragraph(item, body_indent))

    # ===== CLAIMS =====
    elements.append(PageBreak())
    elements.append(Paragraph("6. CLAIMS (30 Total: 5 Independent + 25 Dependent/Expanded)", h1_style))
    elements.append(Paragraph("Independent Claims (Claims 1-3)", h2_style))

    # Claim 1
    elements.append(Paragraph("<b>Claim 1.</b> A computer-implemented method for generating personalized educational content with integrated brand product placements, comprising:", claim_style))
    claim1_steps = [
        "(a) receiving, by a processor, a content generation request associated with a student identifier;",
        "(b) retrieving, from a database, a student profile comprising at least: age, grade level, interests, belief system identifier, cultural context identifier, language preference, advertising preferences including a brand content opt-in flag and blocked categories list, and assigned word bank identifiers;",
        "(c) retrieving vocabulary data from each assigned word bank, comprising baseline words, target words, and stretch words;",
        "(d) selecting vocabulary according to a tiered distribution comprising approximately 60% baseline, 30% target, and 10% stretch words, with randomized selection;",
        "(e) determining, based on advertising preferences, whether brand integration is authorized;",
        "(f) when authorized, executing a real-time brand eligibility engine comprising: (i) querying for active brands; (ii) filtering based on age appropriateness, category restrictions, and budget availability; (iii) selecting eligible brands not exceeding a configurable maximum;",
        "(g) constructing a composite LLM prompt incorporating: student profile, tiered vocabulary, belief system, cultural context, language, character education directives, and brand integration directives specifying products are to be integrated as organic, problem-solving narrative elements;",
        "(h) transmitting the prompt to a Large Language Model and receiving a structured multi-chapter educational narrative with embedded vocabulary annotations and per-chapter comprehension questions;",
        "(i) storing the narrative with associated brand placement data; and",
        "(j) recording brand impression records and updating brand campaign budgets accordingly.",
    ]
    for step in claim1_steps:
        elements.append(Paragraph(step, sub_claim_style))

    # Claim 2
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Paragraph("<b>Claim 2.</b> A computer-implemented method for providing closed-loop brand engagement analytics from AI-generated educational content, comprising:", claim_style))
    claim2_steps = [
        "(a) receiving an analytics request from a brand partner associated with a brand identifier;",
        "(b) identifying all educational narratives containing brand content using multi-layer search: (i) structured brand placement data; (ii) brand impression cross-references; (iii) full-text content search for brand/product names;",
        "(c) extracting specific text excerpts from chapter content where brand/product names appear;",
        "(d) identifying brand-related comprehension questions based on: direct brand name appearance in question/answer text, product category relevance with brand content in chapter, or contextual proximity of question keywords to brand mentions;",
        "(e) retrieving student interaction data for each brand-related question: total attempts, correct responses, incorrect responses;",
        "(f) computing summary statistics: total stories, brand mentions, questions, attempts, pass rate, unique students reached; and",
        "(g) transmitting the extracted excerpts, identified questions with performance data, and summary statistics to the brand partner.",
    ]
    for step in claim2_steps:
        elements.append(Paragraph(step, sub_claim_style))

    # Claim 3
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Paragraph("<b>Claim 3.</b> A computer-implemented system for generating personalized, brand-integrated educational content, comprising:", claim_style))
    claim3_parts = [
        "(a) a database storing student profiles, word banks, brand records, and generated narratives;",
        "(b) a student profile assembly module for multi-dimensional profiles (demographic, interests, belief, culture, strengths, weaknesses, ad preferences);",
        "(c) a vocabulary selection module implementing 60/30/10 tiered distribution with randomized ordering;",
        "(d) a brand eligibility engine applying multi-factor filtering (age, consent, categories, budget) at each request;",
        "(e) a prompt construction module synthesizing all data into a composite LLM prompt with brand integration directives;",
        "(f) an AI generation module for LLM invocation and structured response parsing;",
        "(g) an impression recording module for brand impression creation and budget updates; and",
        "(h) a brand analytics module for multi-layer narrative search, excerpt extraction, brand-related question identification, student interaction data retrieval, and aggregated analytics presentation.",
    ]
    for part in claim3_parts:
        elements.append(Paragraph(part, sub_claim_style))

    # Dependent Claims (4-15)
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Dependent Claims (Claims 4-15)", h2_style))
    
    dependent_claims = [
        "<b>Claim 4.</b> The method of Claim 1, wherein the belief system identifier directs the LLM to generate character behaviors, moral lessons, and decision-making frameworks consistent with the specified belief system.",
        "<b>Claim 5.</b> The method of Claim 1, wherein the cultural context identifier directs the LLM to incorporate culturally relevant names, settings, traditions, foods, and customs.",
        "<b>Claim 6.</b> The method of Claim 1, further comprising: generating vocabulary assessments for target and stretch words; evaluating responses via a second LLM invocation assessing definition accuracy, contextual usage, and spelling; and updating mastered tokens when accuracy meets or exceeds 80%.",
        "<b>Claim 7.</b> The method of Claim 6, further comprising computing an Agentic Reach Score: min((|mastered_tokens| x W1 + completed_narratives x W2) / max(total_narratives x W2, 1) x 100, 100.0) where W1 and W2 are configurable weights.",
        "<b>Claim 8.</b> The method of Claim 1, wherein the composite prompt further incorporates strengths directives (protagonist exhibits child's strengths) and growth areas directives (protagonist overcomes similar challenges without shame or deficit framing).",
        "<b>Claim 9.</b> The method of Claim 2, wherein the multi-layer search ensures coverage of narratives generated before and after implementation of structured brand placement tracking.",
        "<b>Claim 10.</b> The method of Claim 2, wherein brand-related question identification includes extracting individual significant words from multi-word product names as additional search terms.",
        "<b>Claim 11.</b> The method of Claim 1, wherein the brand eligibility engine operates against live database state such that brand composition reflects current active brands, budgets, and preferences at each generation instant.",
        "<b>Claim 12.</b> The method of Claim 1, wherein advertising preferences include a default-false opt-in flag requiring affirmative guardian action before any brand content integration.",
        "<b>Claim 13.</b> The system of Claim 3, further comprising a cost logging module recording AI model, token consumption, cost, duration, and success status per generation event.",
        "<b>Claim 14.</b> The method of Claim 2, further comprising providing brand partners access to full narrative text with chapter-level brand mention indicators.",
        "<b>Claim 15.</b> The system of Claim 3, wherein the analytics module aggregates free-text student responses (question, verbatim answer, pass/fail, comprehension score) and presents them to the brand partner.",
    ]
    for claim in dependent_claims:
        elements.append(Paragraph(claim, claim_style))
        elements.append(Spacer(1, 0.05 * inch))

    # ===== EXPANDED CLAIMS (16-30) =====
    elements.append(PageBreak())
    elements.append(Paragraph("Expanded Method Claims (Claims 16-25)", h2_style))
    elements.append(Paragraph(
        "The following claims extend the core inventions to additional industries and applications:",
        body_style
    ))

    expanded_method_claims = [
        "<b>Claim 16.</b> A computer-implemented method for real-time bidding on placement positions within AI-generated content, comprising: receiving bids from multiple brand advertisers for their products to be woven into AI-generated narratives targeting specific audience segments; ranking bids based on bid price, brand-audience relevance score, and content-context compatibility; selecting winning bids not exceeding a configurable maximum per content generation event; and incorporating the winning brands' product information into the AI content generation prompt as organic narrative elements.",

        "<b>Claim 17.</b> The method of Claim 1, further comprising: A/B testing brand integration approaches by varying brand integration directives across multiple content generation events for comparable audience segments; measuring differential engagement metrics including brand comprehension rate, narrative completion rate, and sentiment scores across test variants; and selecting the integration approach yielding the highest brand comprehension rate for subsequent content generation events.",

        "<b>Claim 18.</b> A computer-implemented method for generating therapeutic narratives with integrated health product recommendations, comprising: receiving a content generation request associated with a patient profile comprising at least: medical condition, treatment plan, cultural context, and language preference; querying a health product database for eligible products matching the patient's condition and treatment context; constructing a composite AI prompt directing a Large Language Model to generate a therapeutic narrative in which the health products appear as organic, problem-solving elements that the narrative protagonist uses to manage their condition; and recording product impression data for analytics presentation to the health product sponsor.",

        "<b>Claim 19.</b> A computer-implemented method for generating corporate training content with integrated tool and product placements, comprising: receiving a training content generation request associated with an employee profile comprising at least: role, department, skill level, and identified skill gaps; querying an employer-configured product catalog for software tools, processes, or products relevant to the employee's role and skill gaps; constructing a composite AI prompt directing a Large Language Model to generate a training narrative in which the selected tools and products appear as solutions the protagonist uses to solve workplace challenges; generating comprehension assessments testing the employee's understanding of the tool usage; and recording tool engagement metrics for presentation to the employer and tool vendor.",

        "<b>Claim 20.</b> A computer-implemented method for computing a Brand Comprehension Rate metric, comprising: generating AI content with embedded brand product elements; automatically generating comprehension questions that test user understanding of the brand-integrated content elements; collecting user quiz responses to said comprehension questions; computing a Brand Comprehension Rate as the ratio of correct responses to total attempts on brand-related questions; and presenting said metric to the brand sponsor as a verified measure of brand content effectiveness, wherein the metric is distinguished from traditional advertising metrics by being verified through objective quiz responses rather than self-reported survey data.",

        "<b>Claim 21.</b> The method of Claim 16, further comprising dynamic pricing of AI content placements based on: historical Brand Comprehension Rates for similar placements, audience demographic value scores, content category premiums, competitive bid density, and time-of-day demand factors, wherein the system computes a recommended bid floor for each placement opportunity.",

        "<b>Claim 22.</b> The method of Claim 1, further comprising cross-platform delivery of brand-integrated AI content across multiple modalities including: text-based narratives, AI-generated audio narration of the narrative content, and AI-generated visual illustrations depicting scenes including brand products, while maintaining consistent brand integration and brand safety controls across all modalities.",

        "<b>Claim 23.</b> The method of Claim 1, further comprising generating multilingual brand-integrated educational content wherein: the AI content generation prompt includes language-specific cultural localization directives; brand products are contextualized within the cultural norms, customs, and traditions of the target language locale; and brand safety is evaluated against locale-specific sensitivities in addition to global brand safety criteria.",

        "<b>Claim 24.</b> A computer-implemented method for federated brand analytics across multiple brand campaigns, comprising: aggregating Brand Comprehension Rate data, content engagement metrics, and audience demographic data across multiple brand campaigns without exposing individual brand performance data; computing industry benchmark metrics for brand comprehension, engagement, and audience reach; identifying cross-brand audience overlap patterns; and presenting aggregate benchmark data to individual brand partners to contextualize their campaign performance relative to industry norms.",

        "<b>Claim 25.</b> The method of Claim 1, further comprising brand safety scoring of AI-generated content, comprising: analyzing the generated narrative content for sentiment, topic sensitivity, and contextual appropriateness prior to brand placement confirmation; computing a brand safety score based on: absence of negative sentiment near brand mentions, appropriate narrative context for the brand category, and alignment between brand values and narrative themes; and automatically excluding brand placements from content that scores below a configurable brand safety threshold.",
    ]
    for claim in expanded_method_claims:
        elements.append(Paragraph(claim, claim_style))
        elements.append(Spacer(1, 0.08 * inch))

    elements.append(PageBreak())
    elements.append(Paragraph("Expanded System Claims (Claims 26-30)", h2_style))

    expanded_system_claims = [
        "<b>Claim 26.</b> A computer-implemented system for operating a brand marketplace for AI-generated content placements, comprising: a brand registration module for brands to create product listings, set campaign budgets, define cost-per-impression rates, and specify audience targeting criteria; a real-time auction module that, at each content generation event, solicits eligible brands, ranks them by bid price and relevance score, and selects winning placements; a content integration module that incorporates winning brand products into AI content generation prompts as organic narrative elements; an impression tracking module that records each brand placement, debits campaign budgets, and computes ROI metrics; and a brand analytics dashboard presenting story excerpts, comprehension question performance, and campaign metrics to each brand partner.",

        "<b>Claim 27.</b> The system of Claim 3, further comprising an automated brand-content quality assurance module that, after AI content generation and before content delivery to the user: verifies that brand products appear in contextually appropriate narrative scenarios; confirms that brand mentions carry positive or neutral sentiment; validates that products serve a genuine problem-solving function in the narrative; checks age-appropriateness of the brand-content combination against the user's profile; and flags or rejects content that fails any quality criterion for regeneration.",

        "<b>Claim 28.</b> The system of Claim 3, further comprising a guardian advertising preference dashboard providing: per-child opt-in and opt-out controls for brand-integrated content; category-level blocking allowing guardians to exclude specific brand categories; brand-specific blocking allowing guardians to exclude individual brands; exposure frequency caps limiting how often any single brand appears in a child's content within a configurable time window; opt-in reward mechanisms providing incentives (credits, premium features, or reduced subscription costs) to guardians who enable brand-integrated content; and a transparency log showing guardians which brands appeared in their child's content and when.",

        "<b>Claim 29.</b> The system of Claim 26, further comprising a predictive analytics module that: analyzes historical Brand Comprehension Rate data across multiple campaigns, audience segments, and content categories; builds predictive models estimating expected brand comprehension, engagement, and recall for proposed new campaigns; recommends optimal brand integration strategies (narrative placement density, product-problem pairing, content genre) to maximize predicted Brand Comprehension Rate; and provides brands with expected performance ranges before campaign commitment.",

        "<b>Claim 30.</b> The system of Claim 26, further comprising an attribution modeling module that: tracks user interactions with brand-integrated AI content through unique impression identifiers; integrates with advertiser customer relationship management (CRM) systems via secure API connections; correlates content engagement events with downstream brand outcomes including: brand awareness survey lift, website visit attribution, product trial initiation, and purchase conversion; computes content-to-outcome attribution scores using multi-touch attribution models; and presents attributed ROI metrics to brand partners linking specific AI content placements to verified business outcomes.",
    ]
    for claim in expanded_system_claims:
        elements.append(Paragraph(claim, claim_style))
        elements.append(Spacer(1, 0.08 * inch))

    # ===== ABSTRACT =====
    elements.append(PageBreak())
    elements.append(Paragraph("7. ABSTRACT", h1_style))
    elements.append(Paragraph(
        "A computer-implemented system and method for generating personalized, AI-driven educational narratives that dynamically "
        "integrate brand product placements as organic, problem-solving story elements. The system assembles a multi-dimensional "
        "student profile comprising demographic, cultural, religious, linguistic, developmental, and interest-based data. At the time "
        "of each content generation request, a real-time brand eligibility engine queries a live brand marketplace database and applies "
        "multi-factor filtering based on student age, guardian consent, category restrictions, and brand budget availability. A composite "
        "prompt synthesizes the student profile, a three-tier (60/30/10) vocabulary distribution, and brand integration directives for a "
        "Large Language Model, which generates a structured multi-chapter educational narrative. The system records brand impressions and "
        "updates campaign budgets in real time. A closed-loop analytics pipeline identifies all narratives containing a brand's content "
        "through multi-layer search, extracts specific story excerpts with brand mentions, identifies brand-related comprehension questions, "
        "retrieves student interaction data (attempts, pass/fail rates), and presents comprehensive engagement analytics to the brand partner "
        "including a novel Brand Comprehension Rate metric verified by objective quiz data. The invention further encompasses: a real-time "
        "bidding system for AI content placements; methods for generating therapeutic narratives with health product integration and corporate "
        "training content with tool/product integration; cross-platform multi-modal delivery; multilingual culturally-contextualized brand "
        "content; federated brand analytics with industry benchmarks; brand safety scoring; a guardian advertising preference dashboard with "
        "granular controls; predictive analytics for placement effectiveness; and attribution modeling linking content engagement to downstream "
        "brand outcomes. The system includes AI-powered vocabulary assessment evaluation, mastery tracking with an Agentic Reach Score, and a "
        "consent-gated privacy architecture requiring affirmative guardian opt-in for brand content.",
        body_style
    ))

    # ===== OATH =====
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("OATH / DECLARATION", h2_style))
    elements.append(Paragraph(
        "I hereby declare that all statements made herein of my own knowledge are true and that all statements made on information "
        "and belief are believed to be true; and further that these statements were made with the knowledge that willful false "
        "statements and the like so made are punishable by fine or imprisonment, or both, under 18 U.S.C. 1001.",
        body_style
    ))
    elements.append(Spacer(1, 0.4 * inch))
    sig_data = [
        ["Signature:", "________________________________________"],
        ["Date:", "________________________________________"],
        ["Printed Name:", "________________________________________"],
    ]
    sig_table = Table(sig_data, colWidths=[1.5 * inch, 4 * inch])
    sig_table.setStyle(TableStyle([
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 10),
        ("FONT", (1, 0), (1, -1), "Helvetica", 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(sig_table)

    # ===== APPENDIX A =====
    elements.append(PageBreak())
    elements.append(Paragraph("APPENDIX A: KEY DATA MODEL SCHEMAS", h1_style))
    
    schemas = [
        ("A.1 Student Profile", "id, full_name, age, grade_level, interests[], virtues[], strengths, weaknesses, belief_system, cultural_context, language, assigned_banks[], ad_preferences{allow_brand_stories, blocked_categories[]}, mastered_tokens[], agentic_reach_score"),
        ("A.2 Word Bank", "id, name, category(included/free/paid/specialized), visibility(public/private), created_by, baseline_words[{word, definition, example}], target_words[], stretch_words[]"),
        ("A.3 Brand", "id, name, products[{name, description}], problem_statement, target_categories[], target_ages[], budget_total, budget_spent, total_impressions, total_stories, is_active"),
        ("A.4 Narrative", "id, title, student_id, bank_ids[], theme, chapters[{number, title, content, word_count, embedded_tokens[{word, tier}], vision_check{question, options[], correct_index}}], tokens_to_verify[], brand_placements[], status"),
        ("A.5 Brand Impression", "id, brand_id, brand_name, narrative_id, student_id, guardian_id, products_featured[], cost, created_date"),
        ("A.6 Written Answer", "student_id, chapter_number, question, student_answer, passed, comprehension_score, feedback, created_date"),
        ("A.7 Read Log", "narrative_id, chapter_number, student_id, vision_check_passed, created_date"),
    ]
    for title, fields in schemas:
        elements.append(Paragraph(f"<b>{title}</b>", h3_style))
        elements.append(Paragraph(fields, code_style))

    # ===== APPENDIX B =====
    elements.append(PageBreak())
    elements.append(Paragraph("APPENDIX B: COMPETITIVE LANDSCAPE ANALYSIS", h1_style))
    
    comp_data = [
        ["Feature", "Semantic\nVision", "Duolingo", "Khan\nAcademy", "Reading\nIQ", "ABC\nmouse"],
        ["AI-Generated Personalized Stories", "YES", "No", "No", "No", "No"],
        ["Belief System Adaptation", "YES", "No", "No", "No", "No"],
        ["Cultural Context Integration", "YES", "No", "No", "No", "No"],
        ["Real-Time Brand Integration", "YES", "No", "No", "No", "No"],
        ["60/30/10 Vocabulary Tiers", "YES", "No", "No", "No", "No"],
        ["Consent-Gated Brand Content", "YES", "N/A", "N/A", "N/A", "N/A"],
        ["Closed-Loop Brand Analytics", "YES", "No", "No", "No", "No"],
        ["Multi-Role Platform (5 roles)", "YES", "No", "Partial", "No", "Partial"],
        ["20+ Language Generation", "YES", "Yes", "No", "No", "No"],
        ["Guardian Ad Controls", "YES", "N/A", "N/A", "N/A", "N/A"],
        ["Strengths/Weaknesses Narrative", "YES", "No", "No", "No", "No"],
        ["Real-Time Classroom Sessions", "YES", "No", "No", "No", "No"],
        ["AI Assessment Evaluation", "YES", "Partial", "Partial", "No", "No"],
        ["Brand Impression Economics", "YES", "No", "No", "No", "No"],
        ["Per-Brand Story Excerpt Analytics", "YES", "No", "No", "No", "No"],
        ["Brand Activation Question Tracking", "YES", "No", "No", "No", "No"],
    ]
    comp_table = Table(comp_data, colWidths=[2.2 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch])
    comp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7),
        ("FONT", (0, 1), (0, -1), "Helvetica", 7),
        ("FONT", (1, 1), (-1, -1), "Helvetica", 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f8f8f8")]),
        # Highlight "YES" cells
        ("TEXTCOLOR", (1, 1), (1, -1), HexColor("#006600")),
        ("FONT", (1, 1), (1, -1), "Helvetica-Bold", 8),
    ]))
    elements.append(comp_table)

    # Final confidential notice
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(
        "<b>END OF PROVISIONAL PATENT APPLICATION</b>",
        ParagraphStyle("End", parent=body_style, alignment=TA_CENTER, fontSize=11)
    ))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(
        f"CONFIDENTIAL — Document generated {DATETIME_STR}",
        ParagraphStyle("EndConf", parent=body_style, alignment=TA_CENTER, fontSize=9, textColor=HexColor("#CC0000"))
    ))

    # Build PDF
    doc.build(elements, onFirstPage=add_watermark_and_footer, onLaterPages=add_watermark_and_footer)
    print(f"PDF generated: {output_path}")
    print(f"Timestamp: {DATETIME_STR}")
    return output_path


if __name__ == "__main__":
    build_pdf()
