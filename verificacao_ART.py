from __future__ import annotations

import base64
import json
import mimetypes
import re
import tempfile

from pathlib import Path
from threading import Event
from typing import Any

import pymupdf
from openai import OpenAI

import scripts.funcoes_comuns as fc
from scripts.mecanismo_rag import construir_recuperador

# ============================================================
# CONFIGURAÇÃO DO LM STUDIO
# ============================================================

URL_BASE_API_PADRAO = "http://127.0.0.1:1234/v1"
CHAVE_API_PADRAO = "lm-studio"
MODELO_SCAN = "google/gemma-4-e2b"

client = OpenAI(
    base_url=URL_BASE_API_PADRAO,
    api_key=CHAVE_API_PADRAO,
)

# ============================================================
# PROMPT PARA IDENTIFICAÇÃO DE ART
# ============================================================

PROMPT_IDENTIFICAR_ART = """
Analise a imagem desta página de documento técnico.

Sua tarefa é verificar se a página pertence a uma:

ANOTAÇÃO DE RESPONSABILIDADE TÉCNICA - ART

Considere como indícios de ART elementos como:

- expressão "Anotação de Responsabilidade Técnica";
- sigla "ART";
- referência ao sistema CONFEA/CREA;
- número de ART;
- nome ou registro de profissional;
- número de registro profissional no CREA;
- dados do contratante;
- dados do proprietário;
- dados da obra ou serviço;
- atividade técnica;
- entidade de classe;
- assinatura do profissional;
- assinatura do contratante;
- valor da ART;
- código de barras;
- QR Code;
- comprovante de pagamento da ART;
- identificação de Conselho Regional de Engenharia e Agronomia;
- campos característicos de formulário de ART.

A presença isolada de um QR Code, assinatura, nome de engenheiro ou
referência ao CREA não é suficiente para afirmar que a página é uma ART.

FORMATO DA RESPOSTA:

1. Se os dados indicarem que a página é uma ART, responda apenas: SIM
2. Caso contrário, responda apenas: NÃO
"""


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def _verificar_interrupcao(
    cancelamento_evento: Event | None,
) -> None:
    if cancelamento_evento and cancelamento_evento.is_set():
        raise fc.ProcessamentoInterrompido(
            "Processamento interrompido pelo usuário."
        )


def imagem_para_data_url(caminho_imagem: str | Path) -> str:
    caminho = Path(caminho_imagem)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Imagem não encontrada: {caminho}"
        )

    mime_type, _ = mimetypes.guess_type(caminho)

    if mime_type is None:
        mime_type = "image/png"

    with caminho.open("rb") as arquivo:
        imagem_base64 = base64.b64encode(
            arquivo.read()
        ).decode("utf-8")

    return f"data:{mime_type};base64,{imagem_base64}"

# ============================================================
# CONSULTA AO MODELO
# ============================================================

def verificar_imagem_art(
    caminho_imagem: str | Path,
    numero_pagina: int,
    modelo: str = MODELO_SCAN,
    ) -> dict[str, Any]:
    """
    Envia uma imagem ao modelo e verifica se ela corresponde
    a uma página de ART.
    """

    caminho_imagem = Path(caminho_imagem)

    print(
        f"Verificando página {numero_pagina}: "
        f"{caminho_imagem.name}"
    )

    resposta = client.chat.completions.create(
        model=modelo,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você analisa documentos técnicos"
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": PROMPT_IDENTIFICAR_ART,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": imagem_para_data_url(
                                caminho_imagem
                            )
                        },
                    },
                ],
            },
        ],
        temperature=0,
    )

    conteudo = resposta.choices[0].message.content

    if not conteudo:
        raise ValueError(
            f"O modelo retornou uma resposta vazia "
            f"para a página {numero_pagina}."
        )

    return conteudo


# ============================================================
# TRATAMENTO DAS PÁGINAS SOLICITADAS
# ============================================================

def _normalizar_paginas(
    paginas: list[int],
    total_paginas: int,
    ) -> list[int]:
    """
    Valida, remove repetições e ordena os números de página.

    Os números recebidos são baseados em 1:
        página 1 = primeira página do PDF.
    """

    if not paginas:
        raise ValueError(
            "Informe pelo menos uma página para analisar."
        )

    paginas_normalizadas: set[int] = set()

    for pagina in paginas:
        if not isinstance(pagina, int):
            raise TypeError(
                f"O número da página deve ser inteiro: {pagina!r}"
            )

        if pagina < 1 or pagina > total_paginas:
            raise ValueError(
                f"Página {pagina} inválida. "
                f"O documento possui {total_paginas} páginas."
            )

        paginas_normalizadas.add(pagina)

    return sorted(paginas_normalizadas)


def analisar_paginas_art(
    caminho_pdf: str | Path,
    paginas: list[int],
    dpi: int = 200,
    modelo: str = MODELO_SCAN,
    cancelamento_evento: Event | None = None,
    ) -> list[dict[str, Any]]:
    """
    Transforma apenas as páginas informadas em imagens temporárias
    e consulta o modelo para verificar se elas são páginas de ART.

    Parâmetros
    ----------
    caminho_pdf:
        Caminho do documento PDF.

    paginas:
        Lista de páginas baseada em 1.
        Exemplo: [19, 20, 21, 22].

    dpi:
        Resolução utilizada para gerar as imagens.

    modelo:
        Nome do modelo carregado no LM Studio.

    Retorno
    -------
    Lista de dicionários, um para cada página analisada.
    """

    _verificar_interrupcao(cancelamento_evento)

    pdf_path = Path(caminho_pdf)

    resultados: list[dict[str, Any]] = []
    paginas_com_art: list[dict[str, Any]] = []

    with pymupdf.open(pdf_path) as documento:
        paginas_validas = _normalizar_paginas(
            paginas=paginas,
            total_paginas=len(documento),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            pasta_temporaria = Path(temp_dir)

            for numero_pagina in paginas_validas:
                _verificar_interrupcao(
                    cancelamento_evento
                )

                # PyMuPDF usa índice iniciado em zero.
                indice_pagina = numero_pagina - 1
                pagina_pdf = documento[indice_pagina]

                caminho_imagem = (
                    pasta_temporaria
                    / f"pagina_{numero_pagina:04d}.png"
                )

                pixmap = pagina_pdf.get_pixmap(
                    dpi=dpi,
                    colorspace=pymupdf.csRGB,
                    alpha=False,
                    annots=True,
                )

                try:
                    pixmap.save(caminho_imagem)
                finally:
                    pixmap = None

                resultado = verificar_imagem_art(
                    caminho_imagem=caminho_imagem,
                    numero_pagina=numero_pagina,
                    modelo=modelo,
                )

                if resultado.strip().upper() == "SIM":
                    paginas_com_art.append(numero_pagina)

                resultados.append(resultado)

                _verificar_interrupcao(
                    cancelamento_evento
                )

                # se sim: adiciona a página à lista de ARTs
                # se não: ignora a página

    # retorna lista com aspáginas de art
    # print(paginas_com_art)
    return paginas_com_art

def verificar_art(caminho_pdf: str | Path, cancelamento_evento: Event | None = None, recuperador: Any | None = None) -> bool:
    caminho_pdf = r"C:\Users\guilherme.smesquita\Downloads\1079-BR-365MG-REL.PRELIMINAR-EST.GEOLÓGICO-LOTE 01_recortado.pdf"

    fc.carregar_modelo(MODELO_SCAN)

    pergunta = "O documento apresenta Anotação de Responsabilidade Técnica? \nBusque por informações como:\n1. Responsável técnico\n2. Dados do contrato\n3. Dados da Obra/Serviço\n4. Atividade Técnica"

    trechos_recuperados = recuperador.invoke(pergunta)

    paginas_para_verificar = [documento.metadata.get('page') for documento in trechos_recuperados]
    paginas_para_verificar = set(paginas_para_verificar)
    paginas_para_verificar = list(paginas_para_verificar)

    try:
        paginas_art = analisar_paginas_art(
            caminho_pdf=caminho_pdf,
            paginas=paginas_para_verificar,
            dpi=200,
            modelo=MODELO_SCAN,
        )
        print("Resultados da análise das páginas:")
        print(paginas_art)
    finally:
        try:
            fc.descarregar_modelo(MODELO_SCAN)
        except Exception as erro:
            print(
                f"Não foi possível descarregar o modelo: {erro}"
            )

    return paginas_art

if __name__ == "__main__":
    caminho_pdf = r"C:\Users\guilherme.smesquita\Downloads\1079-BR-365MG-REL.PRELIMINAR-EST.GEOLÓGICO-LOTE 01_recortado.pdf"

    #paginas_para_verificar = [5, 10, 11, 12, 17, 19, 20, 21, 22, 24]

    fc.carregar_modelo(MODELO_SCAN)

    # aqui insiro as páginas que quero verificar, e o modelo vai me retornar se é uma ART ou não

    recuperador, pasta_vectorstore = construir_recuperador(
        caminho_pdf,
        cancelamento_evento=None)

    pergunta = "O documento apresenta Anotação de Responsabilidade Técnica? \nBusque por informações como:\n1. Responsável técnico\n2. Dados do contrato\n3. Dados da Obra/Serviço\n4. Atividade Técnica"

    trechos_recuperados = recuperador.invoke(pergunta)

    paginas_para_verificar = [documento.metadata.get('page') for documento in trechos_recuperados]
    paginas_para_verificar = set(paginas_para_verificar)
    paginas_para_verificar = list(paginas_para_verificar)

    try:
        paginas_art = analisar_paginas_art(
            caminho_pdf=caminho_pdf,
            paginas=paginas_para_verificar,
            dpi=200,
            modelo=MODELO_SCAN,
        )
        #print("Resultados da análise das páginas:")
        #print(paginas_art)
    finally:
        try:
            fc.descarregar_modelo(MODELO_SCAN)
        except Exception as erro:
            print(
                f"Não foi possível descarregar o modelo: {erro}"
            )
    '''
    for index, resultado in enumerate(resultados):
        print("\n" + "=" * 60)
        print(f"Resultado {index + 1}:")
        print('resultado da página', paginas_para_verificar[index])
        print(resultado)

        if "erro" in resultado:
            print(f"Erro: {resultado['erro']}")
    '''