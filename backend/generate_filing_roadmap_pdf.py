"""Generate Global Patent Filing Strategy & Cost Roadmap PDF"""
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

NOW = datetime.now(timezone.utc)
DATETIME_STR = NOW.strftime("%B %d, %Y at %I:%M %p UTC")
PAGE_W, PAGE_H = letter
USABLE = PAGE_W - 1.5 * inch


def add_watermark(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 64)
    canvas.setFillColor(Color(0.88, 0.88, 0.88, alpha=0.25))
    canvas.translate(PAGE_W/2, PAGE_H/2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "CONFIDENTIAL")
    canvas.rotate(-45)
    canvas.translate(-PAGE_W/2, -PAGE_H/2)
    canvas.setFillColor(HexColor("#CC0000"))
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.drawString(0.75*inch, PAGE_H-0.38*inch, "CONFIDENTIAL — FILING COST ROADMAP")
    canvas.drawRightString(PAGE_W-0.75*inch, PAGE_H-0.38*inch, DATETIME_STR)
    canvas.setFillColor(HexColor("#888888"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(0.75*inch, 0.38*inch, f"CONFIDENTIAL — {DATETIME_STR}")
    canvas.drawRightString(PAGE_W-0.75*inch, 0.38*inch, f"Page {doc.page}")
    canvas.restoreState()


def _p(text, style):
    return Paragraph(text, style)


def build():
    path = "/app/Semantic_Vision_Filing_Cost_Roadmap.pdf"
    doc = SimpleDocTemplate(path, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.7*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
    ss = getSampleStyleSheet()

    title_s = ParagraphStyle("T", parent=ss["Title"], fontSize=22, leading=26, textColor=HexColor("#1a1a2e"), alignment=TA_CENTER)
    h1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=16, leading=20, spaceBefore=18, spaceAfter=10, textColor=HexColor("#1a1a2e"))
    h2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=13, leading=16, spaceBefore=14, spaceAfter=6, textColor=HexColor("#2d2d5e"))
    h3 = ParagraphStyle("H3", parent=ss["Heading3"], fontSize=11, leading=14, spaceBefore=10, spaceAfter=4, textColor=HexColor("#3a3a7a"))
    body = ParagraphStyle("B", parent=ss["Normal"], fontSize=10, leading=14, spaceAfter=7, alignment=TA_JUSTIFY)
    bullet = ParagraphStyle("BL", parent=body, leftIndent=22, bulletIndent=8, spaceAfter=5)
    bullet2 = ParagraphStyle("BL2", parent=bullet, leftIndent=40, bulletIndent=26, fontSize=9.5, leading=13)
    center = ParagraphStyle("C", parent=body, alignment=TA_CENTER)
    red = ParagraphStyle("R", parent=body, textColor=HexColor("#CC0000"), fontSize=11, alignment=TA_CENTER)
    verdict = ParagraphStyle("V", parent=body, fontSize=11, leading=15, textColor=HexColor("#006600"), backColor=HexColor("#f0fff0"), borderPadding=10, spaceBefore=10, spaceAfter=12, alignment=TA_CENTER)
    tc = ParagraphStyle("TC", parent=ss["Normal"], fontSize=9, leading=12, alignment=TA_LEFT)
    tc_b = ParagraphStyle("TCB", parent=tc, fontName="Helvetica-Bold")
    tc_h = ParagraphStyle("TCH", parent=tc, fontName="Helvetica-Bold", textColor=HexColor("#ffffff"))
    tc_r = ParagraphStyle("TCR", parent=tc_b, textColor=HexColor("#CC0000"))
    tc_g = ParagraphStyle("TCG", parent=tc_b, textColor=HexColor("#006600"))

    def hr():
        return HRFlowable(width="100%", thickness=0.5, color=HexColor("#cccccc"), spaceBefore=4, spaceAfter=8)

    def make_table(header, rows, widths):
        data = [[_p(h, tc_h) for h in header]]
        for row in rows:
            cells = []
            for i, cell in enumerate(row):
                if isinstance(cell, Paragraph):
                    cells.append(cell)
                else:
                    cells.append(_p(cell, tc_b if i == 0 else tc))
            data.append(cells)
        t = Table(data, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), HexColor("#1a1a2e")),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("GRID", (0,0), (-1,-1), 0.5, HexColor("#cccccc")),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [HexColor("#ffffff"), HexColor("#f7f7fa")]),
        ]))
        return t

    e = []

    # COVER
    e.append(Spacer(1, 1.4*inch))
    e.append(Paragraph("<b>CONFIDENTIAL</b>", red))
    e.append(Spacer(1, 0.25*inch))
    e.append(Paragraph("GLOBAL PATENT FILING STRATEGY", title_s))
    e.append(Paragraph("& COST ROADMAP", ParagraphStyle("Sub", parent=title_s, fontSize=16, textColor=HexColor("#555555"))))
    e.append(Spacer(1, 0.3*inch))
    e.append(Paragraph("Semantic Vision Platform", center))
    e.append(Paragraph(f"Generated: <b>{DATETIME_STR}</b>", center))
    e.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 1 — KEY ANSWER
    # ══════════════════════════════════════════════════════════════════
    e.append(Paragraph("1. THE KEY ANSWER: ONE FILING, ALL 30 CLAIMS", h1))
    e.append(Paragraph(
        "<b>You file ONE provisional patent application containing all 30 claims.</b>",
        verdict
    ))
    e.append(Paragraph("Here's why:", h3))
    reasons = [
        "Provisional patents have <b>NO per-claim fees</b>. Whether you file 1 claim or 100, the USPTO filing fee is the same.",
        "Provisionals are <b>not examined</b>. The USPTO does not review the claims for patentability — they simply establish your <b>priority date</b>.",
        "The priority date applies to ALL subject matter disclosed in the provisional. All 30 claims get the same priority date.",
        "You have <b>12 months</b> from the provisional filing to convert to a non-provisional (utility) application. During that 12 months, you can refine, expand, or split claims into multiple utility applications.",
        "If needed, you can later split into multiple utility patents during the non-provisional phase — but the provisional itself should contain EVERYTHING.",
    ]
    for r in reasons:
        e.append(Paragraph(r, bullet, bulletText="\u2022"))

    e.append(hr())
    e.append(Paragraph("<b>Bottom line:</b> One provisional filing ($65-$320) protects all 30 claims and establishes priority for the entire patent family.", body))

    # ══════════════════════════════════════════════════════════════════
    # 2 — US FILING COSTS
    # ══════════════════════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("2. UNITED STATES FILING COSTS", h1))

    e.append(Paragraph("2.1 Entity Size Classification", h2))
    entity_items = [
        ("<b>Micro Entity</b> — You qualify if: (a) you meet Small Entity requirements, AND (b) you have not been named as inventor on more than 4 previously filed patent applications, AND (c) your gross income did not exceed 3x the US median household income (~$250K) in the prior year. <b>75% fee discount.</b>",),
        ("<b>Small Entity</b> — You qualify if: fewer than 500 employees and have not assigned/licensed the patent to a large entity. <b>50% fee discount.</b>",),
        ("<b>Large Entity</b> — Everyone else. Full fees.",),
    ]
    for item in entity_items:
        e.append(Paragraph(item[0], bullet, bulletText="\u2022"))

    e.append(Paragraph("2.2 Phase 1: Provisional Patent Application (File NOW)", h2))
    e.append(make_table(
        ["Cost Item", "Micro Entity", "Small Entity", "Large Entity"],
        [
            ["USPTO Filing Fee", "$65", "$130", "$325"],
            ["Patent Attorney Prep\n(recommended)", "$2,000 - $4,000", "$2,000 - $4,000", "$3,000 - $6,000"],
            ["TOTAL", _p("<b>$2,065 - $4,065</b>", tc_g), _p("<b>$2,130 - $4,130</b>", tc_g), _p("<b>$3,325 - $6,325</b>", tc_b)],
        ],
        [1.8*inch, 1.3*inch, 1.3*inch, 1.3*inch],
    ))
    e.append(Paragraph("<i>Note: You can file the provisional yourself (pro se) for just $65-$325 using the document we've prepared. Attorney review is strongly recommended but not required.</i>", ParagraphStyle("Note", parent=body, fontSize=9, textColor=HexColor("#666666"))))

    e.append(Paragraph("2.3 Phase 2: Non-Provisional Utility Application (Within 12 months)", h2))
    e.append(make_table(
        ["Cost Item", "Micro Entity", "Small Entity", "Large Entity"],
        [
            ["USPTO Basic Filing", "$80", "$160", "$320"],
            ["USPTO Search Fee", "$175", "$350", "$700"],
            ["USPTO Examination Fee", "$200", "$400", "$800"],
            ["Excess Claims (over 20)\n10 extra claims x fee each", "$200 total", "$400 total", "$800 total"],
            ["Patent Attorney Drafting", "$5,000 - $10,000", "$5,000 - $10,000", "$8,000 - $15,000"],
            ["USPTO Issue Fee (if granted)", "$300", "$600", "$1,200"],
            ["TOTAL (estimated)", _p("<b>$5,955 - $10,955</b>", tc_g), _p("<b>$6,910 - $11,910</b>", tc_b), _p("<b>$11,820 - $18,820</b>", tc_b)],
        ],
        [1.8*inch, 1.3*inch, 1.3*inch, 1.3*inch],
    ))

    e.append(Paragraph("2.4 Phase 3: Maintenance Fees (to keep patent alive)", h2))
    e.append(make_table(
        ["Maintenance Due", "Micro Entity", "Small Entity", "Large Entity"],
        [
            ["3.5 years after grant", "$475", "$950", "$1,900"],
            ["7.5 years after grant", "$1,225", "$2,450", "$4,900"],
            ["11.5 years after grant", "$2,050", "$4,100", "$8,200"],
            ["Total over 20-year life", _p("<b>$3,750</b>", tc_g), _p("<b>$7,500</b>", tc_b), _p("<b>$15,000</b>", tc_b)],
        ],
        [1.8*inch, 1.3*inch, 1.3*inch, 1.3*inch],
    ))

    # ══════════════════════════════════════════════════════════════════
    # 3 — INTERNATIONAL STRATEGY
    # ══════════════════════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("3. INTERNATIONAL FILING STRATEGY", h1))

    e.append(Paragraph("3.1 The PCT Route (Recommended)", h2))
    e.append(Paragraph("The Patent Cooperation Treaty (PCT) lets you file ONE international application that preserves your rights in 150+ countries. Here's how it works:", body))
    pct_steps = [
        "<b>Month 0:</b> File US Provisional (establishes priority date for all 30 claims) — <b>$65-$325</b>",
        "<b>Month 12:</b> File PCT International Application (claims priority from provisional) — <b>$3,500-$5,500</b>",
        "<b>Month 12:</b> Also file US Non-Provisional (claims priority from provisional) — <b>$6K-$12K</b>",
        "<b>Month 30:</b> Enter 'National Phase' in selected countries (this is when you pay per-country fees) — <b>varies by country</b>",
    ]
    for s in pct_steps:
        e.append(Paragraph(s, bullet, bulletText="\u2192"))

    e.append(Paragraph(
        "<b>Key advantage:</b> The PCT buys you 30 months from your priority date to decide WHICH countries to enter. "
        "You don't pay per-country fees until Month 30. This gives you time to assess which markets matter most.",
        body
    ))

    e.append(Paragraph("3.2 PCT Filing Costs", h2))
    e.append(make_table(
        ["PCT Cost Component", "Small Entity Estimate", "Notes"],
        [
            ["Transmittal Fee", "$240 - $300", "Paid to USPTO as 'receiving office'"],
            ["International Filing Fee", "$1,500 - $1,600", "Based on page count; e-filing discount ~$100-$300"],
            ["Search Fee (EPO)", "$1,800 - $2,000", "If using EPO as search authority; USPTO search ~$1,200"],
            ["Attorney Fees", "$1,200 - $2,000", "For PCT-specific formatting and filing"],
            ["TOTAL PCT International Phase", _p("<b>$3,500 - $5,500</b>", tc_g), "One-time cost for 150+ country coverage"],
        ],
        [2*inch, 1.5*inch, USABLE - 3.5*inch],
    ))

    # ══════════════════════════════════════════════════════════════════
    # 4 — WHERE TO FILE
    # ══════════════════════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("4. WHERE TO FILE: PRIORITY COUNTRIES", h1))
    e.append(Paragraph(
        "Based on Semantic Vision's target markets (EdTech, AdTech, children's media), here are the recommended filing jurisdictions ranked by strategic value:",
        body
    ))

    e.append(Paragraph("TIER 1 — File Immediately (Largest Markets + Strongest IP Enforcement)", h2))
    tier1 = [
        ("<b>United States</b>", "$400B EdTech + $500B AdTech market. Strongest patent enforcement. First-to-file priority. <b>File provisional NOW, non-provisional by Month 12.</b>", "$65 provisional / $6K-$12K non-provisional"),
        ("<b>European Patent Office (EPO)</b>", "Covers 39 countries with ONE filing (Germany, France, UK post-Brexit needs separate, Netherlands, Italy, Spain, etc.). $340B+ combined EdTech/AdTech. Strong enforcement via Unified Patent Court (effective 2023).", "$4,000-$8,000 national phase entry"),
        ("<b>United Kingdom</b>", "Post-Brexit requires separate filing from EPO. Major EdTech market. Strong IP enforcement. London is a global advertising hub.", "$2,000-$4,000 national phase entry"),
    ]
    for title, desc, cost in tier1:
        e.append(Paragraph(title, bullet, bulletText="\u2022"))
        e.append(Paragraph(desc, bullet2))
        e.append(Paragraph(f"<i>Est. cost: {cost}</i>", bullet2))

    e.append(Paragraph("TIER 2 — File Within 30 Months (Large Markets, Growing IP Systems)", h2))
    tier2 = [
        ("<b>China</b>", "70% of global AI patent filings. Massive EdTech market ($100B+). Filing here is DEFENSIVE — prevents Chinese companies from patenting similar tech. Patent examination takes 2-3 years.", "$3,000-$6,000 (including translation)"),
        ("<b>India</b>", "26,000 AI patent applications in 2024. Exploding EdTech market ($10B+ and growing 30%/year). 1.4B population, massive children's education need. Government pushing digital education.", "$2,000-$4,000 (including translation)"),
        ("<b>Japan</b>", "3rd largest patent filer globally. Strong enforcement. $15B+ EdTech market. Key for licensing to Japanese tech companies (Sony, NTT, Rakuten).", "$3,000-$5,000 (including translation)"),
        ("<b>South Korea</b>", "4th largest patent filer. Samsung, LG, Naver are major players in EdTech and content platforms. Strong enforcement.", "$2,500-$4,500 (including translation)"),
    ]
    for title, desc, cost in tier2:
        e.append(Paragraph(title, bullet, bulletText="\u2022"))
        e.append(Paragraph(desc, bullet2))
        e.append(Paragraph(f"<i>Est. cost: {cost}</i>", bullet2))

    e.append(Paragraph("TIER 3 — Consider Based on Business Development", h2))
    tier3 = [
        ("<b>Canada</b> — Close US market alignment, NLP expertise hub — $2,000-$3,500",),
        ("<b>Australia</b> — Strong IP enforcement, English-language market — $2,000-$3,500",),
        ("<b>Brazil</b> — Largest Latin American market, growing EdTech — $2,500-$4,000",),
        ("<b>Nigeria / South Africa</b> — Emerging African EdTech markets — $1,500-$3,000 each",),
        ("<b>UAE / Saudi Arabia</b> — High-value education investment markets — $2,000-$4,000 each",),
    ]
    for item in tier3:
        e.append(Paragraph(item[0], bullet, bulletText="\u2022"))

    # ══════════════════════════════════════════════════════════════════
    # 5 — TOTAL COST SCENARIOS
    # ══════════════════════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("5. TOTAL COST SCENARIOS", h1))
    e.append(Paragraph("Three filing strategies from conservative to maximum coverage:", body))

    e.append(Paragraph("SCENARIO A: US Only (Minimum Viable Protection)", h2))
    scen_a = [
        ["Phase", "Timeline", "Cost (Small Entity)"],
        ["Provisional Patent (30 claims)", "NOW", "$130 (DIY) or $2,000-$4,000 (with attorney)"],
        ["Non-Provisional Utility", "Month 12", "$6,000 - $12,000"],
        ["Maintenance (20 years)", "Years 3.5-11.5", "$7,500"],
        ["TOTAL", "", _p("<b>$13,630 - $23,500</b>", tc_g)],
    ]
    e.append(make_table(scen_a[0], [r[:] for r in scen_a[1:]], [2*inch, 1.2*inch, USABLE - 3.2*inch]))

    e.append(Paragraph("SCENARIO B: US + PCT + Key Countries (Recommended)", h2))
    scen_b = [
        ["Phase", "Timeline", "Cost (Small Entity)"],
        ["US Provisional (30 claims)", "NOW", "$130 - $4,000"],
        ["PCT International Application", "Month 12", "$3,500 - $5,500"],
        ["US Non-Provisional", "Month 12", "$6,000 - $12,000"],
        ["National Phase: EPO (39 countries)", "Month 30", "$4,000 - $8,000"],
        ["National Phase: UK", "Month 30", "$2,000 - $4,000"],
        ["National Phase: China", "Month 30", "$3,000 - $6,000"],
        ["National Phase: India", "Month 30", "$2,000 - $4,000"],
        ["Ongoing prosecution + maintenance", "Years 1-5", "$15,000 - $30,000"],
        ["TOTAL", "", _p("<b>$35,630 - $73,500</b>", tc_b)],
    ]
    e.append(make_table(scen_b[0], [r[:] for r in scen_b[1:]], [2.3*inch, 1*inch, USABLE - 3.3*inch]))

    e.append(Paragraph("SCENARIO C: Maximum Global Coverage (8-10 Countries)", h2))
    scen_c = [
        ["Phase", "Timeline", "Cost (Small Entity)"],
        ["US Provisional (30 claims)", "NOW", "$130 - $4,000"],
        ["PCT International Application", "Month 12", "$3,500 - $5,500"],
        ["US Non-Provisional", "Month 12", "$6,000 - $12,000"],
        ["National Phase: EPO, UK, China, India,\nJapan, S. Korea, Canada, Australia", "Month 30", "$20,000 - $40,000"],
        ["Translations (non-English countries)", "Month 28-30", "$8,000 - $15,000"],
        ["Ongoing prosecution + maintenance\n(all countries, 5 years)", "Years 1-5", "$30,000 - $60,000"],
        ["TOTAL", "", _p("<b>$67,630 - $136,500</b>", tc_r)],
    ]
    e.append(make_table(scen_c[0], [r[:] for r in scen_c[1:]], [2.3*inch, 1*inch, USABLE - 3.3*inch]))

    # ══════════════════════════════════════════════════════════════════
    # 6 — TIMELINE
    # ══════════════════════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("6. RECOMMENDED TIMELINE", h1))

    timeline = [
        ("<b>NOW (Week 1)</b>", [
            "File US Provisional Patent Application with all 30 claims — <b>$65-$325</b>",
            "This establishes your WORLDWIDE priority date",
            "You can file the document we prepared (pro se) right now at USPTO.gov",
        ]),
        ("<b>Week 2-4</b>", [
            "Engage a patent attorney specializing in software/AI patents",
            "Attorney reviews and strengthens claims for non-provisional",
            "Begin formal freedom-to-operate (FTO) search",
        ]),
        ("<b>Month 3-6</b>", [
            "Attorney prepares non-provisional application with professional claims",
            "Consider filing additional provisional for any NEW features built after initial filing",
            "Begin PCT application preparation",
        ]),
        ("<b>Month 11-12 (CRITICAL DEADLINE)</b>", [
            "File US Non-Provisional Utility Application (claiming priority from provisional)",
            "File PCT International Application (claiming priority from provisional)",
            "Both MUST be filed within 12 months of provisional or you lose priority",
        ]),
        ("<b>Month 18-22</b>", [
            "Receive PCT International Search Report and Written Opinion",
            "Evaluate which national phase countries to enter",
            "Assess market traction to determine filing budget",
        ]),
        ("<b>Month 28-30 (CRITICAL DEADLINE)</b>", [
            "Enter National Phase in selected countries",
            "File translations for non-English jurisdictions",
            "Pay national phase entry fees",
        ]),
        ("<b>Year 2-4</b>", [
            "Respond to patent examiner office actions (US and international)",
            "Prosecution and claim amendments as needed",
            "Estimated US patent grant: Year 2.5-4",
        ]),
    ]
    for phase, items in timeline:
        e.append(Paragraph(phase, h3))
        for item in items:
            e.append(Paragraph(item, bullet, bulletText="\u2022"))

    # ══════════════════════════════════════════════════════════════════
    # 7 — KEY RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("7. KEY RECOMMENDATIONS", h1))

    recs = [
        "<b>FILE THE PROVISIONAL THIS WEEK.</b> The $65-$325 filing fee is trivial compared to the risk of a competitor filing first. Your prepared document is attorney-ready — it can be filed pro se at USPTO.gov right now.",
        "<b>The provisional protects ALL 30 claims for 12 months.</b> Use those 12 months to engage an attorney, refine claims, and assess which international markets matter.",
        "<b>Start with Scenario B</b> (US + PCT + 4 key countries = $35K-$73K). This covers the vast majority of your addressable market at a manageable cost.",
        "<b>Use the PCT to buy time.</b> You don't need to decide on international countries until Month 30. By then, you'll have 30 months of market data to inform your decisions.",
        "<b>If budget is tight:</b> File the US provisional NOW ($65-$325), then the PCT at Month 12 ($3,500-$5,500). Total Year 1 cost: under $6,000 for worldwide protection.",
        "<b>Do NOT publicly disclose</b> the specific technical methods described in the patent before filing. Conference talks, blog posts, or published code showing the brand eligibility algorithm or prompt construction method could be used as prior art against you.",
        "<b>The document you have is ready to file.</b> The 30-claim provisional patent application can be submitted to the USPTO Electronic Filing System (EFS-Web) immediately.",
    ]
    for rec in recs:
        e.append(Paragraph(rec, bullet, bulletText="\u2022"))
        e.append(Spacer(1, 0.05*inch))

    e.append(Spacer(1, 0.4*inch))
    e.append(Paragraph(
        f"CONFIDENTIAL — Generated {DATETIME_STR}",
        ParagraphStyle("End", parent=body, fontSize=9, alignment=TA_CENTER, textColor=HexColor("#CC0000"))
    ))

    doc.build(e, onFirstPage=add_watermark, onLaterPages=add_watermark)
    print(f"PDF generated: {path}")
    return path


if __name__ == "__main__":
    build()
