#!/usr/bin/env python3
"""Generate PDF from the v3 patent filing markdown."""
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
from reportlab.platypus.tables import Table, TableStyle

NAVY = HexColor('#0A0F1E')
GOLD = HexColor('#D4A853')
GRAY = HexColor('#6B7280')
WATERMARK_COLOR = Color(0.83, 0.66, 0.33, alpha=0.06)
OUTPUT_PATH = "/app/PATENT_FILING_MARCH_2026_v3.pdf"
MD_PATH = "/app/PATENT_FILING_MARCH_2026_v3.md"

styles = getSampleStyleSheet()
title_style = ParagraphStyle('PT', parent=styles['Title'], fontSize=20, textColor=NAVY, spaceAfter=12, alignment=TA_CENTER, fontName='Helvetica-Bold', leading=26)
h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=15, textColor=NAVY, spaceBefore=18, spaceAfter=6, fontName='Helvetica-Bold')
h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, textColor=HexColor('#1F2937'), spaceBefore=12, spaceAfter=4, fontName='Helvetica-Bold')
h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=10.5, textColor=HexColor('#374151'), spaceBefore=10, spaceAfter=4, fontName='Helvetica-Bold')
body = ParagraphStyle('B', parent=styles['Normal'], fontSize=9.5, textColor=black, alignment=TA_JUSTIFY, spaceAfter=4, leading=13)
code_style = ParagraphStyle('CODE', parent=body, fontName='Courier', fontSize=8, leftIndent=20, spaceAfter=4, leading=11, backColor=HexColor('#F3F4F6'))
center = ParagraphStyle('C', parent=body, alignment=TA_CENTER)
small = ParagraphStyle('S', parent=body, fontSize=7.5, textColor=GRAY)
bold_body = ParagraphStyle('BB', parent=body, fontName='Helvetica-Bold')

def watermark(canvas, doc):
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
    canvas.drawString(72, 36, "Semantic Vision - Provisional Patent Application v3.0 - Allen Tyrone Johnson - Filed March 10, 2026")
    canvas.drawRightString(letter[0]-72, 36, f"Page {doc.page}")
    canvas.restoreState()

def hr():
    return HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=4, spaceAfter=4)

def escape_xml(text):
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def md_to_elements(md_text):
    elements = []
    lines = md_text.split('\n')
    in_code = False
    code_buf = []
    in_table = False
    table_rows = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if in_code:
                code_text = '<br/>'.join(escape_xml(l) for l in code_buf)
                if code_text.strip():
                    elements.append(Paragraph(code_text, code_style))
                code_buf = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Table handling
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            # Skip separator rows
            if all(set(c.strip()) <= set('-: ') for c in cells):
                i += 1
                continue
            table_rows.append(cells)
            # Check if next line is still a table
            if i + 1 < len(lines) and '|' in lines[i+1] and lines[i+1].strip().startswith('|'):
                i += 1
                continue
            else:
                # Render table
                if table_rows:
                    max_cols = max(len(r) for r in table_rows)
                    norm_rows = []
                    for r in table_rows:
                        while len(r) < max_cols:
                            r.append('')
                        norm_rows.append([Paragraph(escape_xml(c)[:80], small) for c in r])
                    try:
                        col_width = (letter[0] - 144) / max_cols
                        t = Table(norm_rows, colWidths=[col_width]*max_cols)
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#F3F4F6')),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
                            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#D1D5DB')),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                        ]))
                        elements.append(t)
                        elements.append(Spacer(1, 6))
                    except Exception:
                        pass
                table_rows = []
                i += 1
                continue

        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if stripped == '---':
            elements.append(hr())
            i += 1
            continue

        # Headers
        if stripped.startswith('# ') and not stripped.startswith('## '):
            text = escape_xml(stripped[2:].strip().replace('**', ''))
            elements.append(Paragraph(text, title_style))
            i += 1
            continue
        if stripped.startswith('## '):
            text = escape_xml(stripped[3:].strip().replace('**', ''))
            elements.append(Paragraph(text, h1))
            i += 1
            continue
        if stripped.startswith('### '):
            text = escape_xml(stripped[4:].strip().replace('**', ''))
            elements.append(Paragraph(text, h2))
            i += 1
            continue

        # Skip image lines
        if stripped.startswith('!['):
            i += 1
            continue

        # Bold lines
        if stripped.startswith('**') and stripped.endswith('**'):
            text = escape_xml(stripped[2:-2])
            elements.append(Paragraph(text, bold_body))
            i += 1
            continue

        # Regular paragraph - handle markdown bold inline
        text = escape_xml(stripped)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>'))
        text = escape_xml(text).replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        # Simpler approach: just use escaped text
        safe_text = escape_xml(stripped)
        try:
            elements.append(Paragraph(safe_text, body))
        except Exception:
            elements.append(Paragraph(stripped[:200], body))

        i += 1

    return elements

def build():
    doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=letter, topMargin=72, bottomMargin=72, leftMargin=72, rightMargin=72)
    
    with open(MD_PATH, 'r') as f:
        md_text = f.read()

    elements = md_to_elements(md_text)
    doc.build(elements, onFirstPage=watermark, onLaterPages=watermark)
    print(f"PDF generated: {OUTPUT_PATH}")

if __name__ == "__main__":
    build()
