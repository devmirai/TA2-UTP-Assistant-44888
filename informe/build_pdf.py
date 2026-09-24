"""SPEC 008 F3 — Convierte informe/TA_U2_GRUPO_X.md a informe/TA_U2_GRUPO_X.pdf.

Uso:
    python informe/build_pdf.py

Lee el .md, genera caratula + indice textual + secciones 1-5 + anexos
usando reportlab (Platypus). No depende de F1/F2/F4.
"""
from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE = Path(__file__).resolve().parent
MD_PATH = BASE / "TA_U2_GRUPO_X.md"
PDF_PATH = BASE / "TA_U2_GRUPO_X.pdf"

W, H = A4

styles = getSampleStyleSheet()
sTitle = ParagraphStyle("F3Title", parent=styles["Title"], fontSize=22, leading=26, spaceAfter=6)
sSubtitle = ParagraphStyle("F3Subtitle", parent=styles["Normal"], fontSize=11, leading=15, textColor=colors.HexColor("#333333"))
sH1 = ParagraphStyle("F3H1", parent=styles["Heading1"], fontSize=16, leading=20, spaceBefore=14, spaceAfter=8, keepWithNext=True)
sH2 = ParagraphStyle("F3H2", parent=styles["Heading2"], fontSize=13, leading=17, spaceBefore=10, spaceAfter=6, keepWithNext=True)
sH3 = ParagraphStyle("F3H3", parent=styles["Heading3"], fontSize=11, leading=15, spaceBefore=8, spaceAfter=4, keepWithNext=True)
sBody = ParagraphStyle("F3Body", parent=styles["Normal"], fontSize=9.5, leading=14, spaceAfter=5, alignment=4)
sBullet = ParagraphStyle("F3Bullet", parent=sBody, leftIndent=18, bulletIndent=8, spaceAfter=3, alignment=0)
sQuote = ParagraphStyle("F3Quote", parent=sBody, leftIndent=14, textColor=colors.HexColor("#444444"), borderPadding=(4, 4, 4), spaceAfter=6, alignment=0)
sCell = ParagraphStyle("F3Cell", parent=styles["Normal"], fontSize=7.5, leading=10.5)
sCellH = ParagraphStyle("F3CellH", parent=sCell, textColor=colors.white, fontName="Helvetica-Bold")
sCode = ParagraphStyle("F3Code", parent=styles["Code"], fontSize=7.5, leading=10.5, spaceAfter=6)
sCaption = ParagraphStyle("F3Caption", parent=styles["Normal"], fontSize=8, leading=11, textColor=colors.HexColor("#666666"), spaceAfter=4)
sIndex = ParagraphStyle("F3Index", parent=styles["Normal"], fontSize=10, leading=15, spaceAfter=2)


def inline_md(text: str) -> str:
    """Convierte inline markdown minimo a etiquetas Paragraph."""
    t = escape(text)
    # codigo inline `x` -> mono
    t = re.sub(r"&#x60;(.+?)&#x60;", r'<font face="Courier">\1</font>', t)
    t = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', t)
    # bold **x** -> <b>
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    # italic *x* (evitar listas) — simple
    # links [txt](url) -> txt (url)
    t = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", t)
    return t


def is_table_sep(row: str) -> bool:
    cells = [c.strip() for c in row.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def split_row(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def styled_table(header: list[str], rows: list[list[str]]):
    data = [[Paragraph(inline_md(h) or " ", sCellH) for h in header]]
    for r in rows:
        # igualar columnas
        if len(r) < len(header):
            r = r + [""] * (len(header) - len(r))
        data.append([Paragraph(inline_md(c) or " ", sCell) for c in r[: len(header)]])
    ncols = len(header)
    # anchos: primera col mas angosta si es tabla de 2 cols tipo caratula/riesgo
    if ncols == 2:
        col_w = [5.2 * cm, 10.8 * cm]
    elif ncols == 3:
        col_w = [4.5 * cm, 5.5 * cm, 6.0 * cm]
    else:
        avail = 16.0 * cm
        col_w = [avail / ncols] * ncols
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9ca3af")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def parse_cover(md: str) -> list[tuple[str, str]]:
    """Extrae filas de la tabla bajo '## Caratula'."""
    lines = md.splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip().lower() == "## carátula".lower() or l.strip() == "## Carátula"), 0)
    rows: list[tuple[str, str]] = []
    for l in lines[start : start + 20]:
        if l.strip().startswith("|") and not is_table_sep(l):
            cells = split_row(l)
            if len(cells) >= 2 and cells[0].lower() != "campo":
                rows.append((cells[0], cells[1]))
    return rows


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(2 * cm, 1.4 * cm, "TA U2 — Asistente UTPConsult (SPEC 008 F3)")
    canvas.drawRightString(W - 2 * cm, 1.4 * cm, f"Pag. {doc.page}")
    canvas.restoreState()


def cover_header_footer(canvas, doc):
    # Solo numero de pagina en caratula
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawRightString(W - 2 * cm, 1.4 * cm, f"Pag. {doc.page}")
    canvas.restoreState()


def build():
    if not MD_PATH.exists():
        raise FileNotFoundError(f"No existe {MD_PATH}")
    md = MD_PATH.read_text(encoding="utf-8")
    cover_rows = parse_cover(md)

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=2 * cm,
        title="TA U2 GRUPO X — Asistente UTPConsult",
        author="Grupo X",
    )
    story = []

    # ---------- CARATULA ----------
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph("TA U2 — Asistente UTPConsult", sSubtitle))
    story.append(Paragraph("Correos &#8594; Jira / GCal / CRM", sSubtitle))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Informe del Trabajo Academico<br/>Unidad 2 — GRUPO X", sTitle))
    story.append(Spacer(1, 0.2 * cm))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#111827")))
    story.append(Spacer(1, 0.5 * cm))

    if cover_rows:
        story.append(Paragraph("Caratula", sH2))
        hdr = ["Campo", "Valor"]
        body = [[k, v] for k, v in cover_rows]
        story.append(styled_table(hdr, body))
        story.append(Spacer(1, 0.3 * cm))
        story.append(
            Paragraph(
                "Nota: los campos marcados [PENDIENTE] deben completarse antes de la entrega final (SPEC 008 F3). "
                "Runtime Production: Groq <font face=\"Courier\">openai/gpt-oss-120b</font> (principal), "
                "fallback <font face=\"Courier\">qwen/qwen3.8-27b</font>.",
                sCaption,
            )
        )
    story.append(Spacer(1, 0.4 * cm))
    story.append(
        Paragraph(
            "Fuente: <font face=\"Courier\">informe/TA_U2_GRUPO_X.md</font> — generado con reportlab (SPEC 008, solo F3).",
            sCaption,
        )
    )
    story.append(PageBreak())

    # ---------- INDICE TEXTUAL ----------
    story.append(Paragraph("Indice", sH1))
    indice = [
        "Caratula (pag. 1)",
        "1. Arquitectura General del Asistente — UTP Assistant (UTPConsult)",
        "2. System Prompt (texto plano de prompts/system.txt)",
        "3. Function Calling Tools (3 JSON de tools/*.json)",
        "4. Flujo Run — Caso Ana Torres / TechCorp (8 pasos)",
        "5. Riesgos y Etica (R1, R2 + matriz)",
        "Anexos y evidencias (F2 / F3 / F4 + link repo)",
    ]
    for i, item in enumerate(indice, start=1):
        story.append(Paragraph(f"{i}. {escape(item)}", sIndex))
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            "El contenido de las secciones 1 a 5 y anexos replica integro el archivo "
            "<font face=\"Courier\">informe/TA_U2_GRUPO_X.md</font> (tablas, prompt plano, JSON, flujo y matriz).",
            sCaption,
        )
    )

    # ---------- CUERPO: render del md desde "# 1." ----------
    lines = md.splitlines()
    # cortar desde la primera seccion "# 1."
    cut = next((i for i, l in enumerate(lines) if l.startswith("# 1.")), 0)
    body_lines = lines[cut:]

    story.append(Spacer(1, 0.2 * cm))

    i = 0
    in_code = False
    code_buf: list[str] = []
    code_lang = ""
    while i < len(body_lines):
        line = body_lines[i]
        s = line.strip()

        # bloques de codigo ``` — acumular y emitir como Preformatted
        if s.startswith("```"):
            if not in_code:
                in_code = True
                code_lang = s[3:].strip()
                code_buf = []
            else:
                in_code = False
                txt = "\n".join(code_buf)
                if code_lang:
                    story.append(Paragraph(f"Bloque {escape(code_lang)}:", sCaption))
                # Preformatted escapa solo si no se indica; pasar texto plano
                story.append(Preformatted(txt, sCode, maxLineLength=95))
                code_buf = []
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # tablas markdown
        if s.startswith("|") and i + 1 < len(body_lines) and is_table_sep(body_lines[i + 1]):
            header = split_row(s)
            i += 2
            rows: list[list[str]] = []
            while i < len(body_lines) and body_lines[i].strip().startswith("|"):
                rows.append(split_row(body_lines[i].strip()))
                i += 1
            story.append(styled_table(header, rows))
            story.append(Spacer(1, 0.15 * cm))
            continue

        if not s:
            story.append(Spacer(1, 0.12 * cm))
            i += 1
            continue
        if s == "---":
            story.append(Spacer(1, 0.15 * cm))
            story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#d1d5db")))
            story.append(Spacer(1, 0.15 * cm))
            i += 1
            continue
        if s.startswith("# "):
            story.append(Paragraph(inline_md(s[2:].strip()), sH1))
            i += 1
            continue
        if s.startswith("### "):
            story.append(Paragraph(inline_md(s[4:].strip()), sH3))
            i += 1
            continue
        if s.startswith("## "):
            story.append(Paragraph(inline_md(s[3:].strip()), sH2))
            i += 1
            continue
        if s.startswith("&gt;") or line.strip().startswith(">"):
            q = re.sub(r"^&gt;\s?", "", s)
            q = re.sub(r"^&gt;", "", q)
            raw = line.strip()
            if raw.startswith(">"):
                raw = raw[1:].strip()
                story.append(Paragraph(inline_md(raw), sQuote))
            else:
                story.append(Paragraph(inline_md(q), sQuote))
            i += 1
            continue
        m_ol = re.match(r"^(\d+)\.\s+(.*)", s)
        if m_ol:
            story.append(Paragraph(f"<b>{m_ol.group(1)}.</b> {inline_md(m_ol.group(2))}", sBullet, bulletText="•"))
            i += 1
            continue
        if s.startswith("- "):
            story.append(Paragraph(inline_md(s[2:]), sBullet, bulletText="•"))
            i += 1
            continue
        if s.startswith("<!--"):
            i += 1
            continue
        # parrafo normal
        story.append(Paragraph(inline_md(s), sBody))
        i += 1

    doc.build(story, onFirstPage=cover_header_footer, onLaterPages=header_footer)
    size = PDF_PATH.stat().st_size
    print(f"PDF OK: {PDF_PATH} ({size} bytes, {size/1024/1024:.2f} MB)")
    return PDF_PATH


if __name__ == "__main__":
    build()
