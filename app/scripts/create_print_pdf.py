import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "app" / "page.tsx"
OUTPUT = ROOT.parents[1] / "교육학_한줄노트_저잉크_인쇄용.pdf"

pdfmetrics.registerFont(TTFont("Malgun", r"C:\Windows\Fonts\malgun.ttf"))
pdfmetrics.registerFont(TTFont("MalgunBold", r"C:\Windows\Fonts\malgunbd.ttf"))

text = SOURCE.read_text(encoding="utf-8")
category_re = re.compile(
    r"id:\s*'([^']+)',\s*label:\s*'([^']+)'.*?notes:\s*\[(.*?)\],\s*quizzes:\s*\[(.*?)\],",
    re.S,
)
note_re = re.compile(
    r"\{\s*term:\s*'([^']*)',\s*type:\s*'([^']*)',\s*summary:\s*'([^']*)',\s*page:\s*'([^']*)'\s*\}"
)
quiz_re = re.compile(r"\{\s*prompt:\s*'([^']*)',\s*answer:\s*'([^']*)'\s*\}")

categories = []
for _, label, notes_raw, quizzes_raw in category_re.findall(text):
    categories.append((label, note_re.findall(notes_raw), quiz_re.findall(quizzes_raw)))

if not categories:
    raise RuntimeError("교육학 자료를 읽지 못했습니다.")

styles = {
    "title": ParagraphStyle(
        "title", fontName="MalgunBold", fontSize=20, leading=26, alignment=TA_CENTER,
        textColor=colors.black, spaceAfter=5 * mm,
    ),
    "subtitle": ParagraphStyle(
        "subtitle", fontName="Malgun", fontSize=9, leading=13, alignment=TA_CENTER,
        textColor=colors.HexColor("#444444"), spaceAfter=8 * mm,
    ),
    "category": ParagraphStyle(
        "category", fontName="MalgunBold", fontSize=15, leading=20,
        textColor=colors.black, spaceAfter=3 * mm,
    ),
    "section": ParagraphStyle(
        "section", fontName="MalgunBold", fontSize=11, leading=15,
        textColor=colors.black, spaceBefore=2 * mm, spaceAfter=2 * mm,
    ),
    "cell": ParagraphStyle("cell", fontName="Malgun", fontSize=7.5, leading=10),
    "cell_bold": ParagraphStyle("cell_bold", fontName="MalgunBold", fontSize=7.5, leading=10),
    "small": ParagraphStyle("small", fontName="Malgun", fontSize=6.7, leading=9, textColor=colors.HexColor("#333333")),
}


def para(value, style="cell"):
    return Paragraph(html.escape(str(value)).replace("\n", "<br/>"), styles[style])


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#B5B5B5"))
    canvas.setLineWidth(0.35)
    canvas.line(14 * mm, 12 * mm, A4[0] - 14 * mm, 12 * mm)
    canvas.setFont("Malgun", 7)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(14 * mm, 8 * mm, "교육학 한 줄 노트 · 저잉크 인쇄용")
    canvas.drawRightString(A4[0] - 14 * mm, 8 * mm, str(doc.page))
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUTPUT), pagesize=A4, rightMargin=12 * mm, leftMargin=12 * mm,
    topMargin=13 * mm, bottomMargin=16 * mm, title="교육학 한 줄 노트 저잉크 인쇄용",
    author="교육학 한 줄 노트",
)

story = [
    Paragraph("교육학 한 줄 노트", styles["title"]),
    Paragraph(
        "10년 이상 교육학 기출 핵심 · 주장·방법·유형·장단점 한 줄 정리 + 빈칸 연습",
        styles["subtitle"],
    ),
]

for category_index, (label, notes, quizzes) in enumerate(categories):
    if category_index:
        story.append(PageBreak())
    story.append(Paragraph(label, styles["category"]))
    story.append(Paragraph("한 줄 정리", styles["section"]))

    rows = [[para("번호", "cell_bold"), para("구분·개념", "cell_bold"), para("꼭 알아야 할 한 줄", "cell_bold"), para("PDF", "cell_bold")]]
    for index, (term, kind, summary, page) in enumerate(notes, 1):
        rows.append([
            para(f"{index:02d}", "small"),
            Paragraph(f"<font size='6.5'>{html.escape(kind)}</font><br/><b>{html.escape(term)}</b>", styles["cell"]),
            para(summary),
            para(f"p.{page}", "small"),
        ])

    table = Table(rows, colWidths=[11 * mm, 34 * mm, 119 * mm, 21 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Malgun"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#888888")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (-1, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 1.7 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.7 * mm),
    ]))
    story.append(table)
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("빈칸 연습", styles["section"]))

    quiz_rows = [[para("문항", "cell_bold"), para("빈칸 문제", "cell_bold"), para("답 쓰기", "cell_bold")]]
    for index, (prompt, _) in enumerate(quizzes, 1):
        quiz_rows.append([para(f"Q{index}", "small"), para(prompt), para("________________", "small")])
    quiz_table = Table(quiz_rows, colWidths=[14 * mm, 132 * mm, 39 * mm], repeatRows=1)
    quiz_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#888888")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (-1, 1), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2 * mm),
    ]))
    story.append(KeepTogether(quiz_table))

doc.build(story, onFirstPage=page_number, onLaterPages=page_number)
print(OUTPUT)
