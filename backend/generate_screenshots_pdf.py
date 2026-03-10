#!/usr/bin/env python3
"""Generate a single PDF containing all patent screenshots with figure labels."""
import os, glob
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.platypus.tables import Table, TableStyle
from PIL import Image as PILImage

OUTPUT = "/app/PATENT_SCREENSHOTS_ALL_FIGURES.pdf"
IMG_DIR = "/app/patent_screenshots"
PAGE_W, PAGE_H = letter
MARGIN = 54  # 0.75 inch
USABLE_W = PAGE_W - 2 * MARGIN
USABLE_H = PAGE_H - 2 * MARGIN - 60  # leave room for header/footer

NAVY = HexColor('#0A0F1E')
GOLD = HexColor('#D4A853')
GRAY = HexColor('#6B7280')

title_style = ParagraphStyle('T', fontSize=20, textColor=NAVY, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=6, leading=26)
subtitle_style = ParagraphStyle('S', fontSize=10, textColor=GRAY, alignment=TA_CENTER, spaceAfter=20)
fig_label = ParagraphStyle('FL', fontSize=12, textColor=NAVY, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6)
fig_desc = ParagraphStyle('FD', fontSize=9, textColor=HexColor('#374151'), alignment=TA_CENTER, spaceAfter=8, leading=12)
footer_style = ParagraphStyle('FT', fontSize=7, textColor=GRAY, alignment=TA_CENTER)

FIGURES = [
    ("fig01_landing_page.jpeg", "FIG. 1", "Landing Page -- Public-facing interface with 'Patent-Pending AI Technology' badge, hero messaging, 20+ language support, and multi-role navigation"),
    ("fig02_unified_login.jpeg", "FIG. 2", "Unified Login Interface (Parent Mode) -- Email/password authentication with four-icon role selector"),
    ("fig03_unified_login_student.jpeg", "FIG. 3", "Unified Login Interface (Student Mode) -- Student Code (STU-XXXXXX) and 6-digit PIN authentication"),
    ("fig04_guardian_portal.jpeg", "FIG. 4", "Administrator Dashboard -- Platform-wide statistics and management overview"),
    ("fig05_admin_brands.jpeg", "FIG. 5", "Administrator Brand Management -- Brand revenue, impressions, bid amounts, and creation interface"),
    ("fig06_admin_affiliates.jpeg", "FIG. 6", "Administrator Affiliate Management -- Program settings, affiliate listing, referral counts, earnings"),
    ("fig07_admin_wordbanks.jpeg", "FIG. 7", "Administrator Word Bank Management -- Three-tier vocabulary input (baseline/target/stretch)"),
    ("fig08_guardian_students.jpeg", "FIG. 8", "Guardian Portal -- Student cards with codes, PINs, ages, grades, and full tab navigation"),
    ("fig09_guardian_affiliate.jpeg", "FIG. 9", "Guardian Affiliate Dashboard -- Code, link, statistics grid, reward rate display"),
    ("fig10_guardian_faq.jpeg", "FIG. 10", "Guardian FAQ -- Expandable accordion with context-specific help items"),
    ("fig11_affiliate_signup.jpeg", "FIG. 11", "Public Affiliate Signup -- Registration form with benefit cards"),
    ("fig12_admin_statistics.jpeg", "FIG. 12", "Administrator Statistics Dashboard -- Platform metrics, user counts, revenue, growth trends"),
    ("fig13_admin_messaging.jpeg", "FIG. 13", "Administrator Messaging System -- Audience targeting (All/Guardians/Students/Teachers/Brands), priority levels (Normal/Important/Urgent), full 18-tab admin navigation"),
    ("fig14_admin_spelling_bee.jpeg", "FIG. 14", "Administrator Spelling Bee Management -- Contest creation with word list, time limit, dates, and existing contest listing"),
    ("fig15_admin_ai_costs.jpeg", "FIG. 15", "Administrator AI Cost Tracking -- Per-generation cost breakdown by model, token usage, success rates"),
    ("fig16_admin_users.jpeg", "FIG. 16", "Administrator User Management -- Plan Membership Overview (68 parents, 8 students), tier breakdown, Create User, Delegate Admin"),
    ("fig17_guardian_students_overview.jpeg", "FIG. 17", "Guardian Students Overview -- Student cards with Student Code, PIN, age, grade, interests, virtues, word banks, and collapsible Reading Rules (Parental Controls)"),
    ("fig18_parental_controls.jpeg", "FIG. 18", "Parental Controls Panel -- Recording Requirement (Optional/Audio Required/Video Required/Both Required), Chapter Threshold, Auto-Start Recording, Require Confirmation toggles"),
    ("fig19_wallet.jpeg", "FIG. 19", "Guardian Wallet -- $1,000.02 balance, Stripe Add Funds ($5-$100 presets), Google Pay/Apple Pay, Coupon Redemption"),
    ("fig20_marketplace.jpeg", "FIG. 20", "Word Bank Marketplace -- Search, category filter, bank cards with pricing, ratings, word counts, Preview/Buy buttons"),
    ("fig21_subscription.jpeg", "FIG. 21", "Subscription Plans -- Starter ($3.99/mo), Family ($9.99/mo, current), Academy ($19.99/mo) with feature comparison"),
    ("fig22_audio_memories.jpeg", "FIG. 22", "Audio Memories Library -- Per-student recording tabs, chronological recordings with diction scores and playback"),
    ("fig23_audio_books.jpeg", "FIG. 23", "Peer Audio Book Collection -- Community-contributed recordings organized by story and reader age"),
    ("fig24_invite_earn.jpeg", "FIG. 24", "Invite & Earn -- March Madness Referral Blitz ($200 Grand Prize), referral code, $5 credit per referral"),
    ("fig25_student_progress.jpeg", "FIG. 25", "Student Progress Dashboard -- All children (SJ/PJ/TJ/DJ) with mastered words, scores, and Biological Vocabulary Targets"),
    ("fig26_student_academy.jpeg", "FIG. 26", "Student Academy Dashboard -- Personalized academy with Spelling Bee, Offline tabs, notification bell"),
    ("fig27_student_stories.jpeg", "FIG. 27", "Student Story Library -- AI-generated story cards with progress indicators and continue reading buttons"),
    ("fig28_student_spelling_bee.jpeg", "FIG. 28", "Student Spelling Bee + Task Reminders -- Contests with Start buttons, YOUR TASKS (unfinished stories, pending bees), stats (Vocab: 9, Score: 93, Time: 26m), Join Classroom"),
    ("fig29_narrative_reader.jpeg", "FIG. 29", "Narrative Reader -- AI-generated story with 'Read This Chapter Aloud' button, music player, chapter navigation"),
    ("fig30_story_text.jpeg", "FIG. 30", "Story Content with Vocabulary -- Full AI-generated text with student as protagonist, virtue modeling, 'Tap any word' definitions, vocabulary badges (orbit, constellation, gravity)"),
    ("fig31_mobile_landing.jpeg", "FIG. 31", "Mobile-Responsive Landing (390x844) -- Fully responsive layout confirming mobile-first design implementation"),
]

def build():
    doc = SimpleDocTemplate(OUTPUT, pagesize=letter, topMargin=MARGIN, bottomMargin=MARGIN, leftMargin=MARGIN, rightMargin=MARGIN)
    elements = []

    # Cover page
    elements.append(Spacer(1, 100))
    elements.append(Paragraph("SEMANTIC VISION", title_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("PROVISIONAL PATENT APPLICATION", ParagraphStyle('ST2', fontSize=14, textColor=NAVY, alignment=TA_CENTER, fontName='Helvetica-Bold')))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("EXHIBIT: APPLICATION SCREENSHOTS", ParagraphStyle('ST3', fontSize=16, textColor=GOLD, alignment=TA_CENTER, fontName='Helvetica-Bold')))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("31 Figures from Working Embodiment", subtitle_style))
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("Inventor: Allen Tyrone Johnson", ParagraphStyle('INV', fontSize=11, textColor=black, alignment=TA_CENTER)))
    elements.append(Paragraph("5013 S. Louise Ave #1563, Sioux Falls, SD 57108", ParagraphStyle('ADDR', fontSize=9, textColor=GRAY, alignment=TA_CENTER)))
    elements.append(Paragraph("allen@songsforcenturies.com | 605-305-3099", ParagraphStyle('CONT', fontSize=9, textColor=GRAY, alignment=TA_CENTER)))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("March 2026", ParagraphStyle('DT', fontSize=10, textColor=GRAY, alignment=TA_CENTER)))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("CONFIDENTIAL -- PATENT-PENDING TECHNOLOGY", ParagraphStyle('CONF', fontSize=9, textColor=HexColor('#DC2626'), alignment=TA_CENTER, fontName='Helvetica-Bold')))
    elements.append(PageBreak())

    # Table of Figures
    elements.append(Paragraph("TABLE OF FIGURES", ParagraphStyle('TOF', fontSize=14, textColor=NAVY, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=12)))
    tof_data = [["Figure", "Description"]]
    for fname, label, desc in FIGURES:
        short_desc = desc.split(" -- ")[0] if " -- " in desc else desc[:60]
        tof_data.append([label, short_desc])
    tof_table = Table(tof_data, colWidths=[60, USABLE_W - 70])
    tof_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#F3F4F6')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#D1D5DB')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(tof_table)
    elements.append(PageBreak())

    # Each figure on its own page
    for fname, label, desc in FIGURES:
        img_path = os.path.join(IMG_DIR, fname)
        if not os.path.exists(img_path):
            print(f"SKIP: {fname} not found")
            continue

        # Get image dimensions
        pil_img = PILImage.open(img_path)
        img_w, img_h = pil_img.size
        aspect = img_h / img_w

        # Scale to fit page
        display_w = USABLE_W
        display_h = display_w * aspect

        # If too tall, scale by height instead
        max_img_h = USABLE_H - 80  # leave room for label and description
        if display_h > max_img_h:
            display_h = max_img_h
            display_w = display_h / aspect

        elements.append(Paragraph(label, fig_label))
        elements.append(Paragraph(desc, fig_desc))

        img = Image(img_path, width=display_w, height=display_h)
        elements.append(img)
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(f"Source: Live application screenshot ({fname})", footer_style))
        elements.append(PageBreak())

    def page_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(GRAY)
        canvas.drawString(MARGIN, 30, "Semantic Vision - Patent Screenshots Exhibit - Allen Tyrone Johnson - March 2026 - CONFIDENTIAL")
        canvas.drawRightString(PAGE_W - MARGIN, 30, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=page_footer, onLaterPages=page_footer)
    print(f"PDF generated: {OUTPUT} ({os.path.getsize(OUTPUT) / 1024:.0f} KB)")

if __name__ == "__main__":
    build()
