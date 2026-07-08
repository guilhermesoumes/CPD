from __future__ import annotations

from pathlib import Path
from threading import Event
import re

import pymupdf

import scripts.funcoes_comuns as fc


PERGUNTA_ART = "anotação de responsabilidade técnica"


def _verificar_interrupcao(cancelamento_evento: Event | None) -> None:
    if cancelamento_evento and cancelamento_evento.is_set():
        raise fc.ProcessamentoInterrompido("Processamento interrompido pelo usuario.")


def _eh_pergunta_art(pergunta: str) -> bool:
    return PERGUNTA_ART in pergunta.lower()


def _paginas_citadas(resposta: str) -> list[int]:
    paginas = set()

    padrao_pagina = r"p(?:á|a|Ã¡)gina"
    for pagina in re.findall(rf"{padrao_pagina}:\s*([^\n\r;]+)", resposta or "", flags=re.I):
        for numero in re.findall(r"\d+", pagina):
            paginas.add(int(numero))

    return sorted(paginas)


def pagina_tem_qrcode(
    caminho_pdf: str | Path,
    numero_pagina: int,
    zoom: int = 3,
) -> tuple[bool, str, str]:
    """Verifica QR Code em uma pagina de PDF usando indice humano, iniciado em 1."""

    try:
        import cv2
        import numpy as np
    except ImportError:
        return False, "", "OpenCV/NumPy nao instalado"

    caminho_pdf = Path(caminho_pdf)
    with pymupdf.open(caminho_pdf) as documento:
        if numero_pagina < 1 or numero_pagina > len(documento):
            return False, "", "pagina inexistente"

        pagina = documento[numero_pagina - 1]
        matriz = pymupdf.Matrix(zoom, zoom)
        pix = pagina.get_pixmap(matrix=matriz)

    imagem = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        pix.height,
        pix.width,
        pix.n,
    )

    if pix.n == 4:
        imagem = cv2.cvtColor(imagem, cv2.COLOR_RGBA2BGR)
    elif pix.n == 3:
        imagem = cv2.cvtColor(imagem, cv2.COLOR_RGB2BGR)

    detector = cv2.QRCodeDetector()
    conteudo, pontos, _ = detector.detectAndDecode(imagem)

    return bool(pontos is not None), conteudo or "", ""


def _mapear_qrcode_por_pagina(
    caminho_pdf: str | Path,
    paginas: list[int],
    cancelamento_evento: Event | None = None,
) -> dict[int, tuple[bool, str, str]]:
    resultados = {}

    for pagina in paginas:
        _verificar_interrupcao(cancelamento_evento)
        resultados[pagina] = pagina_tem_qrcode(caminho_pdf, pagina)

    return resultados


def _formatar_status_qrcode(pagina: int, resultado: tuple[bool, str, str] | None) -> str:
    if resultado is None:
        return f"QR Code na pagina {pagina}: nao verificado"

    tem_qrcode, conteudo, erro = resultado
    if erro:
        return f"QR Code na pagina {pagina}: nao verificado ({erro})"

    if not tem_qrcode:
        return f"QR Code na pagina {pagina}: NAO"

    if conteudo:
        return f"QR Code na pagina {pagina}: SIM; conteudo: {conteudo}"

    return f"QR Code na pagina {pagina}: SIM"


def _inserir_status_qrcode(resposta: str, qrcode_por_pagina: dict[int, tuple[bool, str, str]]) -> str:
    padrao = re.compile(
        r"(?P<linha>-\s*Trecho:\s*(?P<trecho>.*?)\s*,\s*na\s+p(?:á|a|Ã¡)gina:\s*(?P<pagina>[^\n\r]+))",
        flags=re.I,
    )

    def substituir(match: re.Match) -> str:
        trecho = match.group("trecho").strip()
        pagina_texto = match.group("pagina").strip()
        paginas = [int(numero) for numero in re.findall(r"\d+", pagina_texto)]
        status = [
            _formatar_status_qrcode(pagina, qrcode_por_pagina.get(pagina))
            for pagina in paginas
        ]

        if not status:
            return match.group("linha")

        return f"- Trecho: {trecho} | {'; '.join(status)}, na página: {pagina_texto}"

    return padrao.sub(substituir, resposta)


def enriquecer_respostas_art_com_qrcode(
    caminho_pdf: str | Path,
    perguntas: list[dict],
    respostas: list[str],
    cancelamento_evento: Event | None = None) -> list[str]:

    respostas_enriquecidas = list(respostas)

    for indice, pergunta in enumerate(perguntas):
        texto_pergunta = pergunta.get("pergunta", "") if isinstance(pergunta, dict) else str(pergunta)
        if not _eh_pergunta_art(texto_pergunta) or indice >= len(respostas_enriquecidas):
            continue

        paginas = _paginas_citadas(respostas_enriquecidas[indice])
        if not paginas:
            continue

        qrcode_por_pagina = _mapear_qrcode_por_pagina(
            caminho_pdf,
            paginas,
            cancelamento_evento=cancelamento_evento,
        )
        respostas_enriquecidas[indice] = _inserir_status_qrcode(
            respostas_enriquecidas[indice],
            qrcode_por_pagina,
        )

    return respostas_enriquecidas
