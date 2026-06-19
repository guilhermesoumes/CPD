from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import scripts.common_functions as cf

PROJECT_ROOT = Path(cf.resource_path("."))
CONFIG_FILE = PROJECT_ROOT / "config.json"
FONT_DIR = Path(__file__).resolve().parent / "fonts"


def _register_fonts() -> tuple[str, str]:
    regular = FONT_DIR / "LiberationSans-Regular.ttf"
    bold = FONT_DIR / "LiberationSans-Bold.ttf"
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("AppSans", str(regular)))
        pdfmetrics.registerFont(TTFont("AppSans-Bold", str(bold)))
        return "AppSans", "AppSans-Bold"
    return "Helvetica", "Helvetica-Bold"


def _project_metadata() -> dict:
    data = cf.load_config(str(CONFIG_FILE))
    return {
        "Processo": data.get("processo", ""),
        "Edital": data.get("edital", ""),
        "Contrato": data.get("contrato", ""),
        "Modalidade de contratação": data.get("modalidade-de-contratacao", ""),
        "Rodovia": f"BR {data.get('rodovia', '')}".strip(),
        "Extensão": data.get("extensao", ""),
        "Lote": data.get("lote", ""),
        "Tipo de projeto": data.get("tipo-de-projeto", ""),
        "Fase de projeto": data.get("fase-de-projeto", ""),
        "Número da análise": data.get("numero-analise", ""),
        "Número do último relatório": data.get("numero-ult-relatorio", ""),
        "Analista": data.get("analista", ""),
    }


def _answer_status(answer: str) -> str:
    matches = re.findall(r"\b(SIM|NÃO|NAO)\b", answer.upper())
    if not matches:
        return "-"
    return "SIM" if matches[-1] == "SIM" else "NÃO"


def _clean_answer(answer: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", answer or "")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return escape(text).replace("\n", "<br/>")


def _table(rows: list[list], widths: list[float], header: bool = True) -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "AppSans"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#b7c3d0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        style.extend([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce7f3")),
            ("FONTNAME", (0, 0), (-1, 0), "AppSans-Bold"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ])
    table.setStyle(TableStyle(style))
    return table


def _rap_rows(rap_table, styles: dict) -> list[list] | None:
    if rap_table is None:
        return None
    rows = [["Disciplina", "Aprovado", "Aprovado com ressalva", "Reprovado"]]
    for _, row in rap_table.iterrows():
        approved, note, rejected = row["STATUS"]
        rows.append([
            Paragraph(escape(str(row["DISCIPLINA"])), styles["cell"]),
            approved,
            note,
            rejected,
        ])
    return rows


def _question_rows(questions: list[str], answers: list[str], styles: dict) -> list[list]:
    rows = [["Item verificado", "Status", "Evidências e resposta da IA"]]
    for question, answer in zip(questions or [], answers or []):
        rows.append([
            Paragraph(escape(question), styles["cell"]),
            _answer_status(answer),
            Paragraph(_clean_answer(answer), styles["cell"]),
        ])
    return rows


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("AppSans", 8)
    canvas.setFillColor(colors.HexColor("#5c6670"))
    canvas.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm, f"Página {doc.page}")
    canvas.restoreState()

def _page_background(canvas, doc):
    canvas.saveState()

    width, height = A4

    # Fundo azul-claro
    canvas.setFillColor(colors.HexColor("#e6ecf3"))
    canvas.rect(0, 0, width, height, fill=1, stroke=0)

    # Cartão branco central
    margin = 25
    canvas.setFillColor(colors.white)
    canvas.roundRect(
        margin,
        margin,
        width - 2 * margin,
        height - 2 * margin,
        radius=10,
        stroke=0,
        fill=1,
    )

    metadata = _project_metadata()
    # Cabeçalho
    canvas.setFont("AppSans", 8)
    canvas.setFillColor(colors.black)
    canvas.drawString(
        40,
        height - 35,
        "Relatório da Avaliação de Completude - SEI " + metadata['Processo']
    )

    # Rodapé
    canvas.setFont("AppSans", 8)
    canvas.setFillColor(colors.HexColor("#5c6670"))
    canvas.drawRightString(
        width - 40,
        35,
        f"Página {doc.page}"
    )

    canvas.restoreState()

def _summary_cards(rows: list[list], styles: dict) -> Table:
    table = Table(rows, colWidths=[4 * cm, 4 * cm, 4 * cm, 4 * cm])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ebf5fb")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#aed6f1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.8, colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "AppSans-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))

    return table


def generate_pdf_report(
    pdf_path: str,
    discipline_name: str,
    analyzed_report: str,
    general_score: str | None,
    questions: list[str] | None,
    answers: list[str] | None,
    report_kind: str,
    rap_table=None,
    rap_approved: int = 0,
    rap_total: int = 0,
    rap_with_notes: int = 0,
    rap_rejected: int = 0,
    rap_percent: float | None = None,
) -> None:
    regular_font, bold_font = _register_fonts()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("TitleCenter", fontName=bold_font, fontSize=20, leading=24, alignment=TA_CENTER, textColor=colors.HexColor("#1d3557")))
    styles.add(ParagraphStyle("SubtitleCenter", fontName=regular_font, fontSize=10, leading=13, alignment=TA_CENTER, textColor=colors.HexColor("#3d4b59")))
    styles.add(ParagraphStyle("Section", fontName=bold_font, fontSize=12, leading=15, spaceBefore=14, spaceAfter=8, textColor=colors.HexColor("#1d3557")))
    styles.add(ParagraphStyle("BodySmall", fontName=regular_font, fontSize=8.5, leading=11, alignment=TA_LEFT))
    styles.add(ParagraphStyle("cell", fontName=regular_font, fontSize=8, leading=10, alignment=TA_LEFT))

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2.0 * cm,
        leftMargin=2.0 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.0 * cm,
        title=f"RAC - {discipline_name}",
        )

    metadata = _project_metadata()
    story = [
        Paragraph(f"{discipline_name}", styles["TitleCenter"]),
        Paragraph(f"Relatório da Avaliação de Completude - {report_kind}", styles["SubtitleCenter"]),
        Paragraph(escape(analyzed_report), styles["SubtitleCenter"]),
        Spacer(1, 0.35 * cm),
    ]

    cards = [[
        Paragraph(f"<b>{general_score or '-'}</b><br/>Conformidade Geral", styles["cell"]),
        Paragraph(f"<b>{rap_approved + rap_with_notes} / {rap_total}</b><br/>Disciplinas antecessoras", styles["cell"]),
        Paragraph(f"<b>{len(questions or [])}</b><br/>Itens verificados", styles["cell"]),
        Paragraph(f"<b>{rap_percent if rap_percent is not None else '-'}%</b><br/>Percentual RAP", styles["cell"]),
    ]]

    story.append(_summary_cards(cards, styles))

    summary_rows = [
        ["Indicador", "Resultado"],
        ["Conformidade geral", general_score or "-"],
        ["Itens de conteúdo verificados", str(len(questions or []))],
        ["Disciplinas antecessoras no RAP", f"{rap_approved + rap_with_notes} / {rap_total}" if rap_table is not None else "Não informado"],
        ["Percentual RAP", f"{rap_percent}%" if rap_percent is not None else "Não informado"],
    ]
    story.append(_table(summary_rows, [8 * cm, 8 * cm]))

    story.append(Paragraph("Dados do projeto", styles["Section"]))
    metadata_rows = [["Campo", "Valor"]] + [[key, Paragraph(escape(str(value)), styles["cell"])] for key, value in metadata.items()]
    story.append(_table(metadata_rows, [6 * cm, 10 * cm]))

    rap_rows = _rap_rows(rap_table, styles)
    if rap_rows:
        story.append(PageBreak())
        story.append(Paragraph("Disciplinas antecessoras", styles["Section"]))
        story.append(_table(rap_rows, [8 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm]))

    story.append(PageBreak())
    story.append(Paragraph("Conteúdo mínimo verificado por IA", styles["Section"]))
    story.append(_table(_question_rows(questions or [], answers or [], styles), [5.2 * cm, 2.0 * cm, 9.0 * cm]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "Observação: esta análise usa Inteligência Artificial como ferramenta de apoio. As conclusões finais e decisões técnicas permanecem sob responsabilidade humana.",
        styles["BodySmall"],
    ))

    doc.build(
        story,
        onFirstPage=_page_background,
        onLaterPages=_page_background
        )
    

def generate_pdf_report_sem_rap(
    pdf_path: str,
    discipline_name: str,
    analyzed_report: str,
    general_score: str | None,
    questions: list[str] | None,
    answers: list[str] | None,
    report_kind: str,
    rap_table=None,
    rap_approved: int = 0,
    rap_total: int = 0,
    rap_with_notes: int = 0,
    rap_rejected: int = 0,
    rap_percent: float | None = None,
) -> None:

    regular_font, bold_font = _register_fonts()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("TitleCenter", fontName=bold_font, fontSize=20, leading=24, alignment=TA_CENTER, textColor=colors.HexColor("#1d3557")))
    styles.add(ParagraphStyle("SubtitleCenter", fontName=regular_font, fontSize=10, leading=13, alignment=TA_CENTER, textColor=colors.HexColor("#3d4b59")))
    styles.add(ParagraphStyle("Section", fontName=bold_font, fontSize=12, leading=15, spaceBefore=14, spaceAfter=8, textColor=colors.HexColor("#1d3557")))
    styles.add(ParagraphStyle("BodySmall", fontName=regular_font, fontSize=8.5, leading=11, alignment=TA_LEFT))
    styles.add(ParagraphStyle("cell", fontName=regular_font, fontSize=8, leading=10, alignment=TA_LEFT))

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2.0 * cm,
        leftMargin=2.0 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.0 * cm,
        title=f"RAC - {discipline_name}",
    )

    metadata = _project_metadata()

    story = [
        Paragraph(discipline_name, styles["TitleCenter"]),
        Paragraph(f"Relatório da Avaliação de Completude - {report_kind}", styles["SubtitleCenter"]),
        Paragraph(escape(analyzed_report), styles["SubtitleCenter"]),
        Spacer(1, 0.35 * cm),
    ]

    summary_rows = [
        ["Indicador", "Resultado"],
        ["Conformidade geral", general_score or "-"],
        ["Itens de conteúdo verificados", str(len(questions or []))],
    ]

    story.append(_table(summary_rows, [8 * cm, 8 * cm]))

    story.append(Paragraph("Dados do projeto", styles["Section"]))

    metadata_rows = [["Campo", "Valor"]] + [
        [key, Paragraph(escape(str(value)), styles["cell"])]
        for key, value in metadata.items()
    ]

    story.append(_table(metadata_rows, [6 * cm, 10 * cm]))

    story.append(PageBreak())

    story.append(Paragraph("Conteúdo mínimo verificado por IA", styles["Section"]))

    story.append(
        _table(
            _question_rows(questions or [], answers or [], styles),
            [5.2 * cm, 2.0 * cm, 9.0 * cm],
        )
    )

    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(
        "Observação: esta análise usa Inteligência Artificial como ferramenta de apoio. As conclusões finais e decisões técnicas permanecem sob responsabilidade humana.",
        styles["BodySmall"],
    ))

    doc.build(
        story,
        onFirstPage=_page_background,
        onLaterPages=_page_background,
    )