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

import scripts.common_functions as fc

PROJECT_ROOT = Path(fc.resource_path("."))
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
    data = fc.load_config(str(CONFIG_FILE))
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
    rows = [["Disciplina", "Aprovado", "Ressalva", "Reprovado"]]
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
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"RAC - {discipline_name}",
    )

    metadata = _project_metadata()
    story = [
        Paragraph(f"{discipline_name}", styles["TitleCenter"]),
        Paragraph(f"Relatório da Avaliação de Completude - {report_kind}", styles["SubtitleCenter"]),
        Paragraph(escape(analyzed_report), styles["SubtitleCenter"]),
        Spacer(1, 0.35 * cm),
    ]

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

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
