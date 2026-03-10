#!/usr/bin/env python3
"""Generate PDF from the Master User Manual markdown."""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
from reportlab.platypus.tables import Table, TableStyle

NAVY = HexColor('#0A0F1E')
GOLD = HexColor('#D4A853')
GRAY = HexColor('#6B7280')
BLUE = HexColor('#1E40AF')
OUTPUT_PATH = "/app/SEMANTIC_VISION_MASTER_USER_MANUAL.pdf"
MD_PATH = "/app/SEMANTIC_VISION_MASTER_USER_MANUAL.md"

styles = getSampleStyleSheet()
title_style = ParagraphStyle('PT', parent=styles['Title'], fontSize=22, textColor=NAVY, spaceAfter=14, alignment=TA_CENTER, fontName='Helvetica-Bold', leading=28)
h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, textColor=NAVY, spaceBefore=20, spaceAfter=8, fontName='Helvetica-Bold')
h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, textColor=HexColor('#1F2937'), spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold')
h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=11, textColor=HexColor('#374151'), spaceBefore=10, spaceAfter=4, fontName='Helvetica-Bold')
body = ParagraphStyle('B', parent=styles['Normal'], fontSize=9.5, textColor=black, alignment=TA_JUSTIFY, spaceAfter=4, leading=13)
bold_body = ParagraphStyle('BB', parent=body, fontName='Helvetica-Bold')
code_style = ParagraphStyle('CODE', parent=body, fontName='Courier', fontSize=8.5, leftIndent=20, spaceAfter=4, leading=11, backColor=HexColor('#F3F4F6'))
center = ParagraphStyle('C', parent=body, alignment=TA_CENTER)
small = ParagraphStyle('S', parent=body, fontSize=8, textColor=GRAY)
qa_q = ParagraphStyle('QQ', parent=body, fontName='Helvetica-Bold', textColor=BLUE, spaceBefore=6)
qa_a = ParagraphStyle('QA', parent=body, leftIndent=12, spaceBefore=2)

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(GRAY)
    canvas.drawString(72, 36, "Semantic Vision - Master User Manual v6.0 - Allen Tyrone Johnson - March 2026 - CONFIDENTIAL")
    canvas.drawRightString(letter[0]-72, 36, f"Page {doc.page}")
    canvas.restoreState()

def hr():
    return HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=6, spaceAfter=6)

def escape_xml(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def md_to_elements(md_text):
    elements = []
    lines = md_text.split('\n')
    in_code = False
    code_buf = []
    table_rows = []
    i = 0
    while i < len(lines):
        line = lines[i]
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
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if all(set(c.strip()) <= set('-: ') for c in cells):
                i += 1
                continue
            table_rows.append(cells)
            if i + 1 < len(lines) and '|' in lines[i+1] and lines[i+1].strip().startswith('|'):
                i += 1
                continue
            else:
                if table_rows:
                    max_cols = max(len(r) for r in table_rows)
                    norm_rows = []
                    for r in table_rows:
                        while len(r) < max_cols:
                            r.append('')
                        norm_rows.append([Paragraph(escape_xml(c)[:120], small) for c in r])
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
                    except:
                        pass
                table_rows = []
                i += 1
                continue
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped == '---':
            elements.append(hr())
            i += 1
            continue
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
        if stripped.startswith('**Q') and ':**' in stripped:
            q_text = escape_xml(stripped.replace('**', ''))
            elements.append(Paragraph(q_text, qa_q))
            i += 1
            continue
        if stripped.startswith('A: '):
            a_text = escape_xml(stripped[3:])
            elements.append(Paragraph(a_text, qa_a))
            i += 1
            continue
        if stripped.startswith('**') and stripped.endswith('**'):
            text = escape_xml(stripped[2:-2])
            elements.append(Paragraph(text, bold_body))
            i += 1
            continue
        safe_text = escape_xml(stripped)
        try:
            elements.append(Paragraph(safe_text, body))
        except:
            elements.append(Paragraph(stripped[:200], body))
        i += 1
    return elements

def build():
    doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=letter, topMargin=72, bottomMargin=72, leftMargin=72, rightMargin=72)
    with open(MD_PATH, 'r') as f:
        md_text = f.read()
    elements = md_to_elements(md_text)
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    print(f"PDF generated: {OUTPUT_PATH}")

if __name__ == "__main__":
    build()
