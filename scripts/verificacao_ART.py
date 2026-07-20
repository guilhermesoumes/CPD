from __future__ import annotations

import base64
import mimetypes
import tempfile

from pathlib import Path
from threading import Event
from typing import Any

import pymupdf
from openai import OpenAI

import scripts.funcoes_comuns as fc
from scripts.configuracao import CHAVE_API, MODELO_ART, URL_API_OPENAI
from scripts.mecanismo_rag import construir_recuperador

# ============================================================
# CONFIGURAÇÃO DO LM STUDIO
# ============================================================

client = OpenAI(
    base_url=URL_API_OPENAI,
    api_key=CHAVE_API,
)

# ============================================================
# PROMPT PARA IDENTIFICAÇÃO DE ART
# ============================================================

PROMPT_IDENTIFICAR_ART = """
Classifique a imagem como uma página de ART ou não.

Uma ART é um formulário oficial de Anotação de Responsabilidade Técnica
do sistema CONFEA/CREA.

REGRA ELIMINATÓRIA:

Primeiro, procure na própria página pelo menos uma destas expressões
claramente legíveis:

- "Anotação de Responsabilidade Técnica"
- "ART de Obra ou Serviço"
- "Número da ART"
- "Nº da ART"
- "Registro de ART"

Se NENHUMA dessas expressões estiver visível, responda imediatamente:

NÃO

Não continue a análise e não use o contexto de engenharia para inferir
que o documento é uma ART.

Somente quando houver pelo menos uma das expressões acima, verifique se
também existem todos estes grupos:

1. Responsável técnico, com nome e registro CREA;
2. Contratante;
3. Obra ou serviço;
4. Atividade técnica.

Responda SIM somente quando:

- existir uma identificação textual explícita de ART; E
- os quatro grupos estiverem visíveis na página.

REGRAS DE NÃO CONFUSÃO:

- A palavra "engenharia" não é evidência de ART.
- Um contrato de engenharia não é uma ART.
- Uma apresentação de projeto não é uma ART.
- Um relatório técnico não é uma ART.
- Um edital ou ordem de serviço não é uma ART.
- Nome de engenheiro não é suficiente.
- Dados de empresa não são dados do responsável técnico.
- Objeto do contrato não é o quadro de atividade técnica da ART.
- Número de contrato, edital ou processo não é número de ART.
- Não interprete a sigla "ART" dentro de outra palavra.
- Não aceite letras separadas ou parcialmente reconhecidas como "ART".
- Não deduza campos que não estejam escritos.
- Em caso de texto pequeno, dúvida ou baixa legibilidade, responda NÃO.

EXEMPLO NEGATIVO:

Uma página com o título "APRESENTAÇÃO", contendo empresa de engenharia,
edital, número de contrato, objeto do contrato, rodovia, segmento,
extensão, prazo e ordem de serviço.

Essa página é uma apresentação contratual, não uma ART.

Resposta: NÃO

Retorne exclusivamente:
SIM
ou
NÃO
"""


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def _verificar_interrupcao(
    cancelamento_evento: Event | None,
) -> None:
    fc.verificar_interrupcao(cancelamento_evento)


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
    modelo: str = MODELO_ART,
    ) -> str:
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
    modelo: str = MODELO_ART,
    cancelamento_evento: Event | None = None,
    ) -> list[int]:
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

    paginas_com_art: list[int] = []

    with pymupdf.open(pdf_path) as documento:
        paginas_validas = paginas

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

                _verificar_interrupcao(
                    cancelamento_evento
                )

                # se sim: adiciona a página à lista de ARTs
                # se não: ignora a página

    # retorna lista com aspáginas de art
    # print(paginas_com_art)
    return paginas_com_art

def verificar_art(
    caminho_pdf: str | Path,
    cancelamento_evento: Event | None = None,
    recuperador: Any | None = None,
) -> list[int]:
    #caminho_pdf = r"C:\Users\guilherme.smesquita\Downloads\1079-BR-365MG-REL.PRELIMINAR-EST.GEOLÓGICO-LOTE 01_recortado.pdf"

    fc.carregar_modelo(MODELO_ART)

    if recuperador is None:
        recuperador, _ = construir_recuperador(
            caminho_pdf,
            cancelamento_evento=cancelamento_evento,
        )

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
            modelo=MODELO_ART,
            cancelamento_evento=cancelamento_evento,
        )
        print("Resultados da análise das páginas:")
        print(paginas_art)
    finally:
        try:
            fc.descarregar_modelo(MODELO_ART)
        except Exception as erro:
            print(
                f"Não foi possível descarregar o modelo: {erro}"
            )

    return paginas_art
