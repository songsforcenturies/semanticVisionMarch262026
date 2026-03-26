#!/usr/bin/env python3
"""Generate comprehensive provisional patent application PDF for Semantic Vision - March 2026 Filing."""

import os
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, KeepTogether, HRFlowable
)
from io import BytesIO

NAVY = HexColor('#0A0F1E')
GOLD = HexColor('#D4A853')
GRAY = HexColor('#6B7280')
WATERMARK_COLOR = Color(0.83, 0.66, 0.33, alpha=0.06)
OUTPUT_PATH = "/app/PATENT_FILING_MARCH_2026.pdf"
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")

with open(LOGO_PATH, "rb") as f:
    logo_data = f.read()
logo_io = BytesIO(logo_data)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('PT', parent=styles['Title'], fontSize=22, textColor=NAVY, spaceAfter=12, alignment=TA_CENTER, fontName='Helvetica-Bold', leading=28)
h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, textColor=NAVY, spaceBefore=20, spaceAfter=8, fontName='Helvetica-Bold')
h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, textColor=HexColor('#1F2937'), spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold')
body = ParagraphStyle('B', parent=styles['Normal'], fontSize=10, textColor=black, alignment=TA_JUSTIFY, spaceAfter=6, leading=14)
claim = ParagraphStyle('CL', parent=body, leftIndent=24, spaceAfter=4)
center = ParagraphStyle('C', parent=body, alignment=TA_CENTER)
small = ParagraphStyle('S', parent=body, fontSize=8, textColor=GRAY)
bold = ParagraphStyle('BL', parent=body, fontName='Helvetica-Bold')

def wm(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 50)
    canvas.setFillColor(WATERMARK_COLOR)
    canvas.translate(letter[0]/2, letter[1]/2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "CONFIDENTIAL")
    canvas.restoreState()
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(GRAY)
    canvas.drawString(72, 36, "Semantic Vision - Provisional Patent Application - Allen Tyrone Johnson - Filed March 9, 2026")
    canvas.drawRightString(letter[0]-72, 36, f"Page {doc.page}")
    canvas.restoreState()

def hr():
    return HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=6, spaceAfter=6)

def build():
    doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=letter, topMargin=72, bottomMargin=72, leftMargin=72, rightMargin=72)
    s = []

    # Cover
    s.append(Spacer(1, 60))
    s.append(Image(logo_io, width=150, height=150))
    s.append(Spacer(1, 20))
    s.append(Paragraph("UNITED STATES", title_style))
    s.append(Paragraph("PROVISIONAL PATENT APPLICATION", title_style))
    s.append(Paragraph("Under 35 U.S.C. &sect; 111(b)", center))
    s.append(Spacer(1, 30))
    s.append(hr())

    info = [
        ["Application Type:", "Provisional Patent Application"],
        ["Filing Date:", "March 9, 2026"],
        ["Inventor:", "Allen Tyrone Johnson"],
        ["Address:", "5013 S. Louise Ave #1563, Sioux Falls, SD 57108"],
        ["Email:", "allen@songsforcenturies.com"],
        ["Telephone:", "605-305-3099"],
        ["Assignee:", "Allen Tyrone Johnson (Individual Inventor)"],
    ]
    t = Table(info, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10), ('TEXTCOLOR', (0,0), (-1,-1), black),
        ('ALIGN', (0,0), (0,-1), 'RIGHT'), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    s.append(t)
    s.append(Spacer(1, 30))
    s.append(hr())
    s.append(Paragraph("CONFIDENTIAL - ATTORNEY-CLIENT PRIVILEGED", ParagraphStyle('Conf', parent=center, fontSize=9, textColor=HexColor('#DC2626'), fontName='Helvetica-Bold')))
    s.append(PageBreak())

    # Title
    s.append(Paragraph("TITLE OF THE INVENTION", h1))
    s.append(Paragraph("<b>System and Method for Real-Time, Contextual Integration of Brand Product Placements as Narrative Solutions Within AI-Generated, Personalized Educational Content Adapted to User Belief Systems, Cultural Contexts, Developmental Profiles, and Vocabulary Acquisition Goals, With Closed-Loop Brand Engagement Analytics, Multi-Role Platform Architecture, Affiliate Referral Engine, and Guided Onboarding Framework</b>", body))
    s.append(hr())

    # Field
    s.append(Paragraph("FIELD OF THE INVENTION", h1))
    s.append(Paragraph("The present invention relates generally to AI-driven educational content generation, and more particularly to: (1) dynamically integrating brand products into personalized educational narratives as organic story elements; (2) providing real-time brand engagement analytics; (3) generating content adapted across belief systems, cultural heritage, developmental profiles, and age-calibrated vocabulary; (4) managing a multi-stakeholder marketplace with five distinct roles; (5) implementing a closed-loop affiliate referral system; and (6) providing guided role-specific onboarding.", body))
    s.append(hr())

    # Background
    s.append(Paragraph("BACKGROUND OF THE INVENTION", h1))
    s.append(Paragraph("Technical Problem", h2))
    for p in [
        "<b>1. Static Content.</b> Existing platforms (Duolingo, Khan Academy, ABCmouse, etc.) use pre-authored content. None personalizes narratives across religion, culture, interests, virtues, strengths, and growth areas simultaneously.",
        "<b>2. Disruptive Monetization.</b> Banner ads and paywalls interrupt learning. No system integrates brand messaging <i>within</i> educational content as value-adding narrative elements.",
        "<b>3. No Brand Feedback Loops.</b> Existing platforms provide only surface metrics. None gives brands: exact narrative context, comprehension questions, student pass/fail rates, or full story text.",
        "<b>4. Fragmented Ecosystems.</b> No single platform serves five roles (Admin, Parent, Teacher, Student, Brand) with purpose-built portals.",
        "<b>5. No Cultural/Faith Personalization.</b> No patented system generates narratives personalized for specific belief systems AND cultural contexts via LLM.",
    ]:
        s.append(Paragraph(p, body))

    s.append(Paragraph("Prior Art Analysis", h2))
    for p in [
        "<b>US 20250218307 (EZDucate):</b> AI lessons via LLMs. No brand integration, no belief/cultural adaptation, no 60/30/10 vocabulary, no brand analytics.",
        "<b>CHI 2024 (POSTECH):</b> AI storybooks via IoT. Research-only, no brands, no cultural/belief personalization, no multi-role access.",
        "<b>US 20250182639:</b> AI courses. No narrative stories, no brand content, no belief/cultural personalization.",
        "<b>US 11217110B2:</b> Structured learning assets. Not narrative, no brands, no cultural personalization.",
        "<b>Google US 10108988B2:</b> Video ad targeting. Standalone ads, not narrative integration.",
    ]:
        s.append(Paragraph(p, body))

    # Novelty Table
    s.append(Paragraph("Novelty Statement", h2))
    novelty = [
        ["Capability", "Invention", "Prior Art"],
        ["AI personalized multi-chapter stories", "YES", "None"],
        ["Brand integration as narrative elements", "YES", "None"],
        ["Consent-gated brand content", "YES", "None"],
        ["60/30/10 vocabulary distribution", "YES", "None"],
        ["Closed-loop brand analytics", "YES", "None"],
        ["Belief/cultural-aware generation", "YES", "None"],
        ["Five-role platform", "YES", "None"],
        ["Affiliate engine with configurable rewards", "YES", "None"],
        ["16-level age-calibrated vocabulary", "YES", "None"],
        ["Agentic Reach Score", "YES", "None"],
        ["Unified multi-role authentication", "YES", "None"],
        ["Guided onboarding with reset", "YES", "None"],
    ]
    t = Table(novelty, colWidths=[250, 70, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY), ('TEXTCOLOR', (0,0), (-1,0), white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'), ('GRID', (0,0), (-1,-1), 0.5, GRAY),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, HexColor('#F9FAFB')]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    s.append(t)
    s.append(hr())

    # Summary
    s.append(Paragraph("SUMMARY OF THE INVENTION", h1))
    for p in [
        "<b>A. Content Generation Pipeline:</b> Real-time pipeline: student profile assembly, 60/30/10 vocabulary selection, brand eligibility filtering, composite AI prompt construction, multi-chapter narrative generation.",
        "<b>B. Assessment Pipeline:</b> AI-powered vocabulary evaluation, mastery tracking, Agentic Reach Score.",
        "<b>C. Brand Analytics:</b> Three-layer narrative discovery, excerpt extraction, brand activation questions, engagement metrics.",
        "<b>D. Multi-Role Architecture:</b> Five-tier RBAC with purpose-built portals.",
        "<b>E. Affiliate Engine:</b> Auto-generated codes, configurable rewards (flat fee/percentage/credits), email confirmation, registration tracking.",
        "<b>F. Onboarding Framework:</b> Role-specific wizards, localStorage persistence, tutorial reset.",
        "<b>G. Unified Authentication:</b> Role selector dynamically switching between email/password and code/PIN.",
    ]:
        s.append(Paragraph(p, body))
    s.append(hr())

    # Figures
    s.append(Paragraph("BRIEF DESCRIPTION OF THE DRAWINGS", h1))
    for f in [
        "FIG. 1: Landing page", "FIG. 2: Unified Login (Parent)", "FIG. 3: Unified Login (Student)",
        "FIG. 4: Admin Dashboard", "FIG. 5: Word Bank Management", "FIG. 6: Brand Management",
        "FIG. 7: Affiliate Management", "FIG. 8: Parent Onboarding Wizard", "FIG. 9: Parent Students Tab",
        "FIG. 10: Student Progress", "FIG. 11: FAQ Section", "FIG. 12: Brand Onboarding Wizard",
        "FIGS. 13-16: Technical diagrams (to be prepared by illustrator)",
    ]:
        s.append(Paragraph(f"<b>{f.split(':')[0]}:</b>{f.split(':')[1] if ':' in f else ''}", body))
    s.append(Paragraph("<i>FIGS. 1-12 are screenshots from a working embodiment captured March 9, 2026.</i>", small))
    s.append(hr())

    # Detailed Description
    s.append(PageBreak())
    s.append(Paragraph("DETAILED DESCRIPTION OF THE PREFERRED EMBODIMENTS", h1))

    for title, desc in [
        ("1. System Architecture", "Python FastAPI async server, MongoDB (Motor), OpenAI GPT-5.2 LLM, React 18 SPA, Stripe payments, Resend email, IP geolocation, 20+ language i18n."),
        ("2. Student Profile (10 dimensions)", "Name, age, grade; interest graph; 16 selectable virtues; belief system; cultural context; language (20+); parent-authored strengths; growth areas (no deficit framing); ad preferences (default-false opt-in + blocked categories); vocabulary state (banks, mastered tokens, Agentic Reach Score)."),
        ("3. Vocabulary Distribution (60/30/10)", "60% baseline (18 max) for reinforcement, 30% target (9 max) as primary learning, 10% stretch (3 max) for aspiration. Random shuffling ensures unique sequences per generation."),
        ("4. Age-Calibrated Vocabulary", "16-level system: Pre-K (3-5 words, sight words) through Adult (unlimited, technical). All content including brand prose is developmentally appropriate."),
        ("5. Brand Eligibility Engine", "Multi-factor real-time pipeline: system feature gate, guardian consent (default-false), active brand query, age filter, budget check, category block check, selection with configurable max."),
        ("6. Composite AI Prompt", "Synthesizes all 10+ personalization dimensions plus brand directives into single LLM prompt. Brands integrated as organic problem-solving narrative elements."),
        ("7. Generation and Post-Processing", "LLM invocation, JSON parsing, validation, persistence, impression recording, budget updates, cost logging."),
        ("8. Assessment Pipeline", "Per-chapter comprehension, vocabulary assessment, AI evaluation (definition + context + spelling), mastery at 80%+, Agentic Reach Score formula."),
        ("9. Brand Analytics (Closed-Loop)", "Three-layer discovery (structured + impressions + full-text), excerpt extraction, 4-condition question identification, performance analytics, summary stats."),
        ("10. Consent Architecture", "Default-false opt-in, category blocking, age filtering, budget limits, code/PIN student auth."),
        ("11. Affiliate System", "AFF-XXXXXX codes, rewards (flat/percentage/credits), email confirmation, registration tracking, admin controls."),
        ("12. Brand Offers", "Brand-created offers, guardian toggle/dismiss, view/click/dismissal tracking."),
        ("13. Onboarding Framework", "Guardian 5 steps, Brand 5 steps, Student 4 steps. localStorage persistence. Skip/reset/re-trigger."),
        ("14. Unified Authentication", "Icon-based role selector, dynamic form switching, role-specific theming, conditional registration fields."),
        ("15. Student Creation Wizard", "5 steps: Basic Info, Virtues (16), Strengths/Growth, Faith/Culture, Word Banks."),
        ("16. Classroom Sessions", "WebSocket-based live sessions, 6-digit codes, synchronized reading, real-time question broadcast."),
        ("17. Wallet/Payment", "Stripe wallets, coupon engine, multi-currency (50+ via live exchange rates)."),
        ("18. FAQ System", "Role-specific content (Parent 6, Brand 6, Student 5, Teacher 5), interactive accordion."),
    ]:
        s.append(Paragraph(title, h2))
        s.append(Paragraph(desc, body))

    s.append(hr())

    # Claims
    s.append(PageBreak())
    s.append(Paragraph("CLAIMS", h1))
    s.append(Paragraph("Independent Claims", h2))

    s.append(Paragraph("<b>Claim 1.</b> Method for generating personalized educational content with integrated brand placements: (a) receive request; (b) retrieve student profile (age, grade, interests, belief, culture, language, ad prefs, word banks); (c) retrieve vocabulary (baseline/target/stretch); (d) select per 60/30/10 distribution; (e) check brand authorization; (f) execute brand eligibility engine (query, filter by age/categories/budget, select); (g) construct composite LLM prompt with all dimensions + brand directives; (h) generate multi-chapter narrative; (i) store with brand data; (j) record impressions and update budgets.", bold))
    s.append(Spacer(1, 6))
    s.append(Paragraph("<b>Claim 2.</b> Method for closed-loop brand analytics: (a) receive brand request; (b) identify narratives via 3-layer search (structured + impressions + full-text); (c) extract brand excerpts; (d) identify brand questions (4 conditions); (e) retrieve student interaction data; (f) compute summary stats; (g) transmit analytics.", bold))
    s.append(Spacer(1, 6))
    s.append(Paragraph("<b>Claim 3.</b> System comprising: database, profile assembly, 60/30/10 vocabulary selection, brand eligibility engine, prompt construction, AI generation, impression recording, and brand analytics modules.", bold))
    s.append(Spacer(1, 6))
    s.append(Paragraph("<b>Claim 4.</b> Method for affiliate referral: (a) generate AFF-XXXXXX codes; (b) automated confirmation email; (c) detect codes during registration; (d) validate; (e) record referrals; (f) calculate rewards (flat fee/percentage/wallet credits); (g) update earnings.", bold))
    s.append(Spacer(1, 6))
    s.append(Paragraph("<b>Claim 5.</b> Method for guided onboarding: (a) detect first login per portal; (b) display role-specific modal guidance; (c) provide navigation; (d) persist completion state; (e) provide tutorial reset.", bold))

    s.append(Paragraph("Dependent Claims (6-30)", h2))
    deps = [
        "6: Belief system directs LLM character behaviors/morals.",
        "7: Cultural context directs LLM names/settings/traditions.",
        "8: Vocabulary assessment with AI evaluation + mastery at 80%.",
        "9: Agentic Reach Score computation formula.",
        "10: Strengths/growth directives (no deficit framing).",
        "11: 16-level age-calibrated vocabulary complexity.",
        "12: Multi-layer search covers pre/post structured tracking.",
        "13: Multi-word product name decomposition for question matching.",
        "14: Default-false advertising opt-in.",
        "15: Cost logging per generation event.",
        "16: Full narrative access with brand indicators.",
        "17: Written response aggregation for brand review.",
        "18: 20+ language narrative generation.",
        "19: Multi-tier word bank ecosystem.",
        "20: Real-time WebSocket classroom sessions.",
        "21: Admin-configurable affiliate reward structures.",
        "22: Per-portal customized onboarding content.",
        "23: Unified authentication with dynamic form switching.",
        "24: Unified registration with conditional referral field.",
        "25: Brand promotional offers with guardian controls.",
        "26: Contextual FAQ system with role-specific accordion.",
        "27: Default 'every market' brand targeting.",
        "28: Dynamic currency/geolocation (50+ currencies).",
        "29: Time-bound referral contests with leaderboard.",
        "30: Multi-step student creation wizard (5 steps).",
    ]
    for d in deps:
        s.append(Paragraph(f"<b>Claim {d}</b>", body))

    s.append(hr())

    # Abstract
    s.append(PageBreak())
    s.append(Paragraph("ABSTRACT", h1))
    s.append(Paragraph(
        "A computer-implemented system and method for generating personalized, AI-driven educational "
        "narratives that dynamically integrate brand product placements as organic, problem-solving story "
        "elements. The system assembles a multi-dimensional student profile (demographic, cultural, religious, "
        "linguistic, developmental, interest-based). A real-time brand eligibility engine applies multi-factor "
        "filtering (age, consent, categories, budget). A composite prompt synthesizes the profile, 60/30/10 "
        "vocabulary distribution, age-calibrated complexity (16 levels), and brand directives for an LLM. "
        "A closed-loop analytics pipeline provides brand partners with story excerpts, comprehension questions, "
        "and engagement metrics. Five-tier RBAC provides purpose-built portals. Additional innovations: "
        "affiliate referral engine (flat fee/percentage/wallet credits), guided onboarding wizards with reset, "
        "unified multi-role authentication, contextual FAQ, multi-step student wizard, WebSocket classroom "
        "sessions, and 50+ currency support.", body))
    s.append(hr())

    # Oath
    s.append(Paragraph("OATH / DECLARATION", h1))
    s.append(Paragraph("I hereby declare that all statements made herein of my own knowledge are true and that all statements made on information and belief are believed to be true; and further that these statements were made with the knowledge that willful false statements and the like so made are punishable by fine or imprisonment, or both, under 18 U.S.C. 1001.", body))
    s.append(Spacer(1, 30))
    for line in ["Signature: ____________________________________", "Date: March 9, 2026", "Printed Name: Allen Tyrone Johnson", "Address: 5013 S. Louise Ave #1563, Sioux Falls, SD 57108"]:
        s.append(Paragraph(line, body))
    s.append(hr())

    # Competitive Landscape
    s.append(PageBreak())
    s.append(Paragraph("APPENDIX B: COMPETITIVE LANDSCAPE", h1))
    comp = [
        ["Feature", "SV", "Duolingo", "Khan", "ABCmouse", "EZDucate"],
        ["AI Multi-Chapter Stories", "YES", "No", "No", "No", "Partial"],
        ["Belief/Cultural Adaptation", "YES", "No", "No", "No", "No"],
        ["Brand Narrative Integration", "YES", "No", "No", "No", "No"],
        ["60/30/10 Vocabulary", "YES", "No", "No", "No", "No"],
        ["Brand Analytics Loop", "YES", "No", "No", "No", "No"],
        ["Five-Role Platform", "YES", "No", "Partial", "Partial", "No"],
        ["20+ Language Generation", "YES", "Yes", "No", "No", "No"],
        ["Affiliate Referral Engine", "YES", "No", "No", "No", "No"],
        ["Guided Onboarding", "YES", "Partial", "No", "Partial", "No"],
        ["Unified Auth Interface", "YES", "No", "No", "No", "No"],
        ["Agentic Reach Score", "YES", "No", "No", "No", "No"],
    ]
    t = Table(comp, colWidths=[170, 45, 55, 45, 55, 55])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY), ('TEXTCOLOR', (0,0), (-1,0), white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 7),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'), ('GRID', (0,0), (-1,-1), 0.5, GRAY),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, HexColor('#F9FAFB')]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3), ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    s.append(t)

    s.append(Spacer(1, 30))
    s.append(Paragraph("<i>Document Version 2.0 | Filed March 9, 2026 | Inventor: Allen Tyrone Johnson</i>", small))
    s.append(Paragraph("<b>END OF PROVISIONAL PATENT APPLICATION</b>", center))

    doc.build(s, onFirstPage=wm, onLaterPages=wm)
    print(f"PDF generated: {OUTPUT_PATH}")
    print(f"Size: {os.path.getsize(OUTPUT_PATH):,} bytes")

if __name__ == "__main__":
    build()
