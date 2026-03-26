#!/usr/bin/env python3
"""Generate Semantic Vision User Manual PDF."""

import os
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, HRFlowable
)
from io import BytesIO

NAVY = HexColor('#0A0F1E')
GOLD = HexColor('#D4A853')
GRAY = HexColor('#6B7280')
WM = Color(0.83, 0.66, 0.33, alpha=0.06)
OUT = "/app/SEMANTIC_VISION_USER_MANUAL.pdf"
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")

with open(LOGO_PATH, "rb") as f:
    logo_data = f.read()
logo_io = BytesIO(logo_data)

sty = getSampleStyleSheet()
title = ParagraphStyle('T', parent=sty['Title'], fontSize=24, textColor=NAVY, spaceAfter=12, alignment=TA_CENTER, fontName='Helvetica-Bold', leading=30)
h1 = ParagraphStyle('H1', parent=sty['Heading1'], fontSize=16, textColor=NAVY, spaceBefore=20, spaceAfter=8, fontName='Helvetica-Bold')
h2 = ParagraphStyle('H2', parent=sty['Heading2'], fontSize=13, textColor=HexColor('#1F2937'), spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold')
h3 = ParagraphStyle('H3', parent=sty['Heading3'], fontSize=11, textColor=HexColor('#374151'), spaceBefore=10, spaceAfter=4, fontName='Helvetica-Bold')
body = ParagraphStyle('B', parent=sty['Normal'], fontSize=10, textColor=black, alignment=TA_JUSTIFY, spaceAfter=6, leading=14)
center = ParagraphStyle('C', parent=body, alignment=TA_CENTER)
small = ParagraphStyle('S', parent=body, fontSize=8, textColor=GRAY)
bold = ParagraphStyle('BL', parent=body, fontName='Helvetica-Bold')
bullet = ParagraphStyle('BU', parent=body, leftIndent=20, bulletIndent=8, spaceBefore=2, spaceAfter=2)

def wm(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(GRAY)
    canvas.drawString(72, 36, "Semantic Vision User Manual - Allen Tyrone Johnson - Version 1.0 - March 2026")
    canvas.drawRightString(letter[0]-72, 36, f"Page {doc.page}")
    canvas.restoreState()

def hr():
    return HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=6, spaceAfter=6)

def tbl(data, widths=None):
    if not widths:
        widths = [150, 300]
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY), ('TEXTCOLOR', (0,0), (-1,0), white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, GRAY), ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, HexColor('#F9FAFB')]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

def build():
    doc = SimpleDocTemplate(OUT, pagesize=letter, topMargin=72, bottomMargin=72, leftMargin=72, rightMargin=72)
    s = []

    # Cover
    s.append(Spacer(1, 40))
    s.append(Image(logo_io, width=140, height=140))
    s.append(Spacer(1, 20))
    s.append(Paragraph("SEMANTIC VISION", title))
    s.append(Paragraph("Comprehensive User Manual", ParagraphStyle('Sub', parent=title, fontSize=16, textColor=GOLD)))
    s.append(Spacer(1, 20))
    s.append(hr())
    info = [
        ["Version:", "1.0"], ["Date:", "March 9, 2026"],
        ["Author:", "Allen Tyrone Johnson"],
        ["Contact:", "allen@songsforcenturies.com | 605-305-3099"],
    ]
    t = Table(info, colWidths=[100, 350])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (0,-1), 'RIGHT'), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    s.append(t)
    s.append(Spacer(1, 30))
    s.append(hr())

    # IP Notice
    s.append(Paragraph("INTELLECTUAL PROPERTY NOTICE", ParagraphStyle('IP', parent=bold, fontSize=10, textColor=HexColor('#DC2626'))))
    s.append(Paragraph("This manual documents the Semantic Vision platform, a proprietary work product of Allen Tyrone Johnson. Third-party technologies (OpenAI, Stripe, MongoDB, React, FastAPI, Resend, Tailwind CSS) are used as infrastructure components and remain the intellectual property of their respective owners. <b>No IP claim is made over these third-party technologies.</b>", body))
    s.append(Spacer(1, 8))
    s.append(Paragraph("<b>What IS claimed as original work product:</b> The novel METHOD of combining these technologies; the 60/30/10 vocabulary model; the brand eligibility engine; the brand-in-narrative integration; closed-loop brand analytics; the Agentic Reach Score; the 10-dimension student profile system; the consent architecture; the affiliate referral engine; the onboarding framework; the unified authentication interface; and all UI designs, data models, API architectures, and business logic.", body))
    s.append(PageBreak())

    # TOC
    s.append(Paragraph("TABLE OF CONTENTS", h1))
    toc = ["1. Getting Started", "2. Parent/Guardian Guide", "3. Student Guide",
           "4. Teacher Guide", "5. Brand Partner Guide", "6. Administrator Guide", "7. Glossary"]
    for item in toc:
        s.append(Paragraph(item, bold))
    s.append(hr())

    # === SECTION 1: GETTING STARTED ===
    s.append(Paragraph("1. GETTING STARTED", h1))

    s.append(Paragraph("1.1 Unified Login System", h2))
    s.append(Paragraph("Semantic Vision uses a single login page for all user types. Four icons at the top represent different portals:", body))
    s.append(tbl([
        ["Icon / Role", "Authentication"],
        ["Heart - Parents", "Email + Password"],
        ["Graduation Cap - Students", "Student Code + PIN"],
        ["Book - Teachers", "Email + Password"],
        ["Megaphone - Brands", "Email + Password"],
    ]))
    s.append(Paragraph("Click an icon to switch the login form. Students use a code/PIN (no email required).", body))

    s.append(Paragraph("1.2 Creating an Account", h2))
    s.append(Paragraph("Click 'Register Here' from the login page. Three account types are available: Parents, Teachers, and Brands. <b>Student accounts are created BY parents</b> through the Parent Portal.", body))
    s.append(Paragraph("If you received a referral code (REF-XXXXXX or AFF-XXXXXX), enter it during parent registration to receive rewards.", body))

    s.append(Paragraph("1.3 First-Login Onboarding", h2))
    s.append(Paragraph("A guided tutorial wizard appears on first login to each portal (4-5 steps). Click 'Next' to advance, 'Skip' to dismiss. Click the 'Tutorial' button in the portal header to replay it anytime.", body))
    s.append(hr())

    # === SECTION 2: PARENT GUIDE ===
    s.append(PageBreak())
    s.append(Paragraph("2. PARENT/GUARDIAN GUIDE", h1))

    s.append(Paragraph("2.1 Dashboard Tabs", h2))
    s.append(tbl([
        ["Tab", "Purpose"],
        ["Students", "Add and manage student profiles"],
        ["Subscription", "View/upgrade your plan"],
        ["Marketplace", "Browse and assign word banks"],
        ["Wallet", "Manage digital wallet balance"],
        ["Invite & Earn", "Share referral codes for rewards"],
        ["Offers", "View brand partner promotions"],
        ["Progress", "Track children's reading growth"],
        ["FAQ", "Frequently asked questions"],
    ]))

    s.append(Paragraph("2.2 Adding a Student (5-Step Wizard)", h2))
    steps = [
        "<b>Step 1 - Basic Info:</b> Name, age, grade level (Pre-K through Adult). Grade controls vocabulary complexity.",
        "<b>Step 2 - Virtues:</b> Select from 16 character virtues (Courage, Honesty, Kindness, etc.). These are woven into story character behavior.",
        "<b>Step 3 - Strengths & Growth:</b> Describe strengths (celebrated as 'superpowers') and growth areas (modeled through empathetic character development, never shame).",
        "<b>Step 4 - Faith & Culture:</b> Select belief system and cultural context. Stories reflect corresponding values and traditions.",
        "<b>Step 5 - Word Banks:</b> Assign vocabulary word banks with three tiers: Baseline (60%), Target (30%), Stretch (10%).",
    ]
    for step in steps:
        s.append(Paragraph(step, body))
    s.append(Paragraph("After creation, you receive a <b>Student Code</b> (e.g., STU-DR40V7) and <b>PIN</b> (e.g., 914027). Keep these safe.", bold))

    s.append(Paragraph("2.3 Subscription & Wallet", h2))
    s.append(Paragraph("<b>Free Plan:</b> Basic story generation. <b>Premium Plans:</b> Unlimited stories, advanced analytics, premium features. Top up your wallet via Stripe. Apply coupon codes for discounts.", body))

    s.append(Paragraph("2.4 Marketplace", h2))
    s.append(Paragraph("Browse word banks (Included, Free, Paid, Specialized). Assign to students. Create your own private word banks with custom baseline/target/stretch words.", body))

    s.append(Paragraph("2.5 Referral Program", h2))
    s.append(Paragraph("Share your unique referral code. When friends register with your code, you both earn rewards (wallet credits, discounts, or flat fees — configured by admin).", body))

    s.append(Paragraph("2.6 Offers", h2))
    s.append(Paragraph("View promotional offers from brand partners. Dismiss individual offers or toggle ALL offers off. Offers link to external sites or platform promos.", body))

    s.append(Paragraph("2.7 Progress Tracking", h2))
    s.append(Paragraph("Per-student metrics: <b>Vocabulary Mastered</b> (unique words learned), <b>Stories Read</b>, <b>Agentic Reach Score</b> (0-100), <b>Word Banks</b> assigned, <b>Target</b> goal.", body))

    s.append(Paragraph("2.8 Brand Content Preferences", h2))
    s.append(Paragraph("By default, stories do NOT include brand content. To enable: edit student profile > Advertising Preferences > toggle 'Allow Brand Stories.' You can also block specific categories.", body))
    s.append(hr())

    # === SECTION 3: STUDENT GUIDE ===
    s.append(PageBreak())
    s.append(Paragraph("3. STUDENT GUIDE", h1))

    s.append(Paragraph("3.1 Logging In", h2))
    s.append(Paragraph("Click the 'Students' graduation cap icon on the login page. Enter your <b>Student Code</b> (STU-XXXXX) and <b>PIN</b>. Click 'Enter Academy.'", body))

    s.append(Paragraph("3.2 Reading Stories", h2))
    s.append(Paragraph("Click 'Create New Story' to generate a personalized 5-chapter story. Highlighted words are your vocabulary targets. After each chapter, answer a comprehension question (4 choices). After all chapters, take a vocabulary quiz — define words and use them in sentences. Score 80%+ to master them.", body))

    s.append(Paragraph("3.3 Classroom Sessions", h2))
    s.append(Paragraph("Ask your teacher for the 6-digit session code. Enter it to join a live reading session where the teacher controls the pace.", body))

    s.append(Paragraph("3.4 Progress", h2))
    s.append(Paragraph("Dashboard shows: Vocabulary Mastered count, Stories Read, Agentic Reach Score (0-100). All stories are saved for re-reading.", body))

    s.append(Paragraph("3.5 FAQ", h2))
    s.append(Paragraph("Click the FAQ button in the header for answers about stories, vocabulary, sessions, and scores.", body))
    s.append(hr())

    # === SECTION 4: TEACHER GUIDE ===
    s.append(Paragraph("4. TEACHER GUIDE", h1))

    s.append(Paragraph("4.1 Getting Started", h2))
    s.append(Paragraph("Register as a Teacher. Your portal has three tabs: Sessions, Analytics, and FAQ.", body))

    s.append(Paragraph("4.2 Classroom Sessions", h2))
    s.append(Paragraph("Click 'New Session' to get a 6-digit code. Share with students. You control reading pace and can broadcast questions in real-time via WebSocket.", body))

    s.append(Paragraph("4.3 Analytics", h2))
    s.append(Paragraph("View per-student vocabulary mastered, stories read, comprehension scores, and class-wide averages.", body))
    s.append(hr())

    # === SECTION 5: BRAND GUIDE ===
    s.append(PageBreak())
    s.append(Paragraph("5. BRAND PARTNER GUIDE", h1))

    s.append(Paragraph("5.1 How Brand Integration Works", h2))
    s.append(Paragraph("Your brand is NOT shown as a traditional ad. Instead, when a student requests a story, the AI checks brand eligibility and weaves your products into the narrative as <b>organic, problem-solving elements</b>. You then receive analytics on student engagement.", body))

    s.append(Paragraph("5.2 Eligibility Rules", h2))
    s.append(Paragraph("Your brand appears ONLY when: (1) Campaign is active, (2) Budget remains, (3) Guardian opted in, (4) Categories not blocked, (5) Student age matches targets, (6) Admin-enabled globally.", body))

    s.append(Paragraph("5.3 Dashboard Tabs", h2))
    s.append(tbl([
        ["Tab", "Purpose"],
        ["Dashboard", "Performance overview"],
        ["Campaigns", "Create/manage campaigns"],
        ["Budget", "Spending and top-up"],
        ["Story Integrations", "See brand in stories, excerpts, questions, student responses"],
        ["Offers", "Create promotions for parents"],
        ["FAQ", "Common brand questions"],
        ["Analytics", "Detailed engagement metrics"],
    ]))

    s.append(Paragraph("5.4 Creating a Campaign", h2))
    s.append(Paragraph("Enter: campaign name, products/descriptions, problem statement, target ages/countries/languages, daily budget, cost-per-impression, logo URL. Leave target ages empty to reach ALL markets.", body))

    s.append(Paragraph("5.5 Story Integrations (Your Key Analytics)", h2))
    s.append(Paragraph("View: (1) Actual story excerpts mentioning your brand, (2) Brand activation questions and student pass/fail rates, (3) Written student responses, (4) Full story text access. This closed-loop analytics is unique to Semantic Vision.", body))

    s.append(Paragraph("5.6 Promotional Offers", h2))
    s.append(Paragraph("Create offers pushed to parents: title, description, offer type (internal/external), link. Track views, clicks, and dismissals.", body))
    s.append(hr())

    # === SECTION 6: ADMIN GUIDE ===
    s.append(PageBreak())
    s.append(Paragraph("6. ADMINISTRATOR GUIDE", h1))

    s.append(Paragraph("6.1 Dashboard", h2))
    s.append(Paragraph("Platform-wide stats: Total Parents, Teachers, Students, Signups, Word Banks, Stories, AI cost tracking.", body))

    s.append(Paragraph("6.2 Admin Tabs", h2))
    s.append(tbl([
        ["Tab", "Purpose"],
        ["Statistics", "Platform metrics"],
        ["Users", "Search/manage accounts, edit wallets"],
        ["Plans", "Create subscription plans"],
        ["Word Banks", "Create 3-tier vocabulary banks"],
        ["Contests", "Referral contests with prizes"],
        ["Brands", "Approve/manage brand partners"],
        ["Affiliates", "Manage affiliate program"],
    ]))

    s.append(Paragraph("6.3 Word Bank Creation", h2))
    s.append(Paragraph("Name, category (Included/Free/Paid/Specialized), then add words to 3 tiers: Baseline (60% of story), Target (30%), Stretch (10%). Each word needs: word, definition, example sentence.", body))

    s.append(Paragraph("6.4 Affiliate Program", h2))
    s.append(Paragraph("Configure: reward type (Flat Fee/Percentage/Wallet Credits), amounts, minimum payout threshold, auto-approve toggle. View all affiliates, approve/deactivate, record payouts.", body))

    s.append(Paragraph("6.5 Brand Management", h2))
    s.append(Paragraph("Approve new brand applications. View brand revenue, impressions, products. Toggle active/inactive. Create new brand profiles.", body))

    s.append(Paragraph("6.6 System Controls", h2))
    s.append(Paragraph("LLM model selection, brand sponsorship feature flag (enable/disable platform-wide), default cost per impression, plan management.", body))
    s.append(hr())

    # === SECTION 7: GLOSSARY ===
    s.append(PageBreak())
    s.append(Paragraph("7. GLOSSARY", h1))
    glossary = [
        ["Term", "Definition"],
        ["Agentic Reach Score", "0-100 metric: vocabulary mastery relative to reading engagement"],
        ["Baseline Words", "Foundation vocabulary (60%) reinforcing existing knowledge"],
        ["Target Words", "Growth vocabulary (30%) as primary learning objective"],
        ["Stretch Words", "Challenge vocabulary (10%) for aspirational engagement"],
        ["Brand Activation Question", "Comprehension question related to brand product usage in story"],
        ["Brand Impression", "Single instance of brand appearing in a student story"],
        ["Vision Check", "Per-chapter multiple-choice comprehension question"],
        ["Word Bank", "Curated vocabulary collection (baseline/target/stretch tiers)"],
        ["Student Code", "Unique login ID (e.g., STU-DR40V7)"],
        ["Affiliate Code", "Referral code (e.g., AFF-XXXXXX)"],
        ["Narrative", "AI-generated, personalized 5-chapter educational story"],
        ["Cost Per Impression", "Amount debited from brand budget per story inclusion"],
        ["Consent Gate", "Default-false opt-in for brand content"],
        ["60/30/10 Model", "Tiered vocabulary distribution in story generation"],
    ]
    s.append(tbl(glossary, widths=[140, 310]))
    s.append(Spacer(1, 20))
    s.append(hr())
    s.append(Paragraph("<i>Document Version 1.0 | March 9, 2026 | Allen Tyrone Johnson</i>", small))
    s.append(Paragraph("<i>Copyright 2026 Allen Tyrone Johnson. All rights reserved.</i>", small))
    s.append(Paragraph("<b>END OF USER MANUAL</b>", center))

    doc.build(s, onFirstPage=wm, onLaterPages=wm)
    print(f"PDF: {OUT}")
    print(f"Size: {os.path.getsize(OUT):,} bytes")

if __name__ == "__main__":
    build()
