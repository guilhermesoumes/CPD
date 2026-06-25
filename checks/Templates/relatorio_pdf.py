"""Monta o Relatório da Avaliação de Completude (RAC) em PDF."""

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

import scripts.funcoes_comuns as fc

RAIZ_PROJETO = Path(fc.caminho_recurso("."))
ARQUIVO_CONFIGURACAO = RAIZ_PROJETO / "config.json"
DIRETORIO_FONTES = Path(__file__).resolve().parent / "fonts"


def _registrar_fontes() -> tuple[str, str]:
    """Registra as fontes distribuídas com o projeto e retorna seus nomes."""

    fonte_regular = DIRETORIO_FONTES / "LiberationSans-Regular.ttf"
    fonte_negrito = DIRETORIO_FONTES / "LiberationSans-Bold.ttf"
    if fonte_regular.exists() and fonte_negrito.exists():
        pdfmetrics.registerFont(TTFont("AppSans", str(fonte_regular)))
        pdfmetrics.registerFont(TTFont("AppSans-Bold", str(fonte_negrito)))
        return "AppSans", "AppSans-Bold"
    return "Helvetica", "Helvetica-Bold"


def _metadados_projeto() -> dict:
    """Carrega e organiza os metadados exibidos no relatório."""

    dados = fc.carregar_configuracao(str(ARQUIVO_CONFIGURACAO))
    return {
        "Processo": dados.get("processo", ""),
        "Edital": dados.get("edital", ""),
        "Contrato": dados.get("contrato", ""),
        "Modalidade de contratação": dados.get("modalidade-de-contratacao", ""),
        "Rodovia": f"BR {dados.get('rodovia', '')}".strip(),
        "Extensão": dados.get("extensao", ""),
        "Lote": dados.get("lote", ""),
        "Tipo de projeto": dados.get("tipo-de-projeto", ""),
        "Fase de projeto": dados.get("fase-de-projeto", ""),
        "Número da análise": dados.get("numero-analise", ""),
        "Número do último relatório": dados.get("numero-ult-relatorio", ""),
        "Analista": dados.get("analista", ""),
    }


def _situacao_resposta(resposta: str) -> str:
    """Obtém a última conclusão SIM ou NÃO presente na resposta."""

    correspondencias = re.findall(r"\b(SIM|NÃO|NAO)\b", resposta.upper())
    if not correspondencias:
        return "-"
    return "SIM" if correspondencias[-1] == "SIM" else "NÃO"


def _limpar_resposta(resposta: str) -> str:
    """Remove marcação Markdown e prepara quebras de linha para o PDF."""

    texto = re.sub(r"\*\*(.*?)\*\*", r"\1", resposta or "")
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip()
    return escape(texto).replace("\n", "<br/>")


def _tabela(linhas: list[list], larguras: list[float], cabecalho: bool = True) -> Table:
    """Cria uma tabela com a identidade visual padrão do RAC."""

    tabela = Table(linhas, colWidths=larguras, repeatRows=1 if cabecalho else 0)
    estilo = [
        ("FONTNAME", (0, 0), (-1, -1), "AppSans"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#b7c3d0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if cabecalho:
        estilo.extend([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce7f3")),
            ("FONTNAME", (0, 0), (-1, 0), "AppSans-Bold"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ])
    tabela.setStyle(TableStyle(estilo))
    return tabela


def _linhas_perguntas(perguntas: list[str], respostas: list[str], estilos: dict) -> list[list]:
    """Combina perguntas, situação e evidências em linhas de relatório."""

    linhas = [["Pergunta", "Resposta", "Trecho que comprova"]]
    
    for pergunta, resposta in zip(perguntas or [], respostas or []): # passando o par (pergunta, trecho que comprova)
        #print('pergunta, resposta:')
        #print(pergunta, resposta)

        lista_resposta = re.findall(r"\d+\s*.\s*(.*?)(?=\n\d+\s*.|$)", resposta, re.S)

        col2 = "Sim" if 'sim' in lista_resposta[-1].lower() else "Não"

        linhas.append([
            Paragraph(escape(pergunta), estilos["cell"]),
            Paragraph(col2),
            Paragraph(_limpar_resposta(lista_resposta[-2]), estilos["cell"]),
        ])
    return linhas


def _fundo_pagina(tela_pdf, documento):
    """Desenha o fundo, o cabeçalho e o rodapé de cada página."""

    tela_pdf.saveState()

    largura, altura = A4

    # Fundo azul-claro
    tela_pdf.setFillColor(colors.HexColor("#e6ecf3"))
    tela_pdf.rect(0, 0, largura, altura, fill=1, stroke=0)

    # Cartão branco central
    margem = 25
    tela_pdf.setFillColor(colors.white)
    tela_pdf.roundRect(
        margem,
        margem,
        largura - 2 * margem,
        altura - 2 * margem,
        radius=10,
        stroke=0,
        fill=1,
    )

    metadados = _metadados_projeto()
    # Cabeçalho
    tela_pdf.setFont("AppSans", 8)
    tela_pdf.setFillColor(colors.black)
    tela_pdf.drawString(
        40,
        altura - 35,
        "Relatório da Avaliação de Completude - SEI " + metadados['Processo']
    )

    # Rodapé
    tela_pdf.setFont("AppSans", 8)
    tela_pdf.setFillColor(colors.HexColor("#5c6670"))
    tela_pdf.drawRightString(
        largura - 40,
        35,
        f"Página {documento.page}"
    )

    tela_pdf.restoreState()

def gerar_relatorio_pdf(
    caminho_pdf: str,
    nome_disciplina: str,
    relatorio_analisado: str,
    pontuacao_geral: str | None,
    perguntas: list[str] | None,
    respostas: list[str] | None,
    tipo_relatorio: str,
) -> None:
    """Gera um RAC com os resultados da análise de conteúdo por RAG."""

    fonte_regular, fonte_negrito = _registrar_fontes()
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle("TitleCenter", fontName=fonte_negrito, fontSize=20, leading=24, alignment=TA_CENTER, textColor=colors.HexColor("#1d3557")))
    estilos.add(ParagraphStyle("SubtitleCenter", fontName=fonte_regular, fontSize=10, leading=13, alignment=TA_CENTER, textColor=colors.HexColor("#3d4b59")))
    estilos.add(ParagraphStyle("Section", fontName=fonte_negrito, fontSize=12, leading=15, spaceBefore=14, spaceAfter=8, textColor=colors.HexColor("#1d3557")))
    estilos.add(ParagraphStyle("BodySmall", fontName=fonte_regular, fontSize=8.5, leading=11, alignment=TA_LEFT))
    estilos.add(ParagraphStyle("cell", fontName=fonte_regular, fontSize=8, leading=10, alignment=TA_LEFT))

    documento = SimpleDocTemplate(
        caminho_pdf,
        pagesize=A4,
        rightMargin=2.0 * cm,
        leftMargin=2.0 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.0 * cm,
        title=f"RAC - {nome_disciplina}",
        )

    metadados = _metadados_projeto()
    conteudo_relatorio = [
        Paragraph(f"{nome_disciplina}", estilos["TitleCenter"]),
        Paragraph(f"Relatório da Avaliação de Completude - {tipo_relatorio}", estilos["SubtitleCenter"]),
        Paragraph(escape(relatorio_analisado), estilos["SubtitleCenter"]),
        Spacer(1, 0.35 * cm),
    ]

    # =========================================================
    # TABELA 1
    # =========================================================

    linhas_resumo = [
        ["Indicador", "Resultado"],
        ["Conformidade geral", pontuacao_geral or "-"],
        ["Itens de conteúdo verificados", str(len(perguntas or []))],
    ]
    conteudo_relatorio.append(_tabela(linhas_resumo, [8 * cm, 8 * cm]))

    conteudo_relatorio.append(Paragraph("Dados do projeto", estilos["Section"]))

    # =========================================================
    # TABELA 2
    # =========================================================
    linhas_metadados = [["Campo", "Valor"]] + [[chave, Paragraph(escape(str(valor)), estilos["cell"])] for chave, valor in metadados.items()]
    conteudo_relatorio.append(_tabela(linhas_metadados, [6 * cm, 10 * cm]))

    conteudo_relatorio.append(PageBreak())

    # =========================================================
    # PÁGINA 2
    # =========================================================

    conteudo_relatorio.append(Paragraph("Conteúdo mínimo verificado por IA", estilos["Section"]))
    # =========================================================
    # TABELA 3
    # =========================================================
    conteudo_relatorio.append(_tabela(_linhas_perguntas(perguntas, respostas, estilos), [5.2 * cm, 2.0 * cm, 9.0 * cm]))
    conteudo_relatorio.append(Spacer(1, 0.4 * cm))
    conteudo_relatorio.append(Paragraph(
        "Observação: esta análise usa Inteligência Artificial como ferramenta de apoio. As conclusões finais e decisões técnicas permanecem sob responsabilidade humana.",
        estilos["BodySmall"],
    ))

    documento.build(
        conteudo_relatorio,
        onFirstPage=_fundo_pagina,
        onLaterPages=_fundo_pagina,
    )
