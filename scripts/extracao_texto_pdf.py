import base64
import mimetypes
import re
import tempfile
from collections import Counter
from pathlib import Path
from threading import Event

import pymupdf
from langchain_core.documents import Document
from openai import OpenAI

import scripts.funcoes_comuns as fc
from scripts.status_processamento import informar
from scripts.configuracao import CHAVE_API, MODELO_OCR, URL_API_OPENAI

# configuração do LM Studio
client = OpenAI(
    base_url=URL_API_OPENAI,
    api_key=CHAVE_API,
)


def _verificar_interrupcao(cancelamento_evento: Event | None) -> None:
    fc.verificar_interrupcao(cancelamento_evento)

def imagem_para_data_url(caminho_imagem: str) -> str:
    caminho = Path(caminho_imagem)

    mime_type, _ = mimetypes.guess_type(caminho)
    if mime_type is None:
        mime_type = "image/png"

    with open(caminho, "rb") as f:
        imagem_base64 = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{imagem_base64}"


PROMPT = """
Transcreva apenas o conteúdo visível da imagem.

Regras obrigatórias:
- Retorne somente a transcrição.
- Não escreva introdução.
- Não escreva conclusão.
- Não explique o que está fazendo.
- Não use frases como "Aqui está a transcrição".
- Não adicione comentários.
- Preserve a ordem de leitura do documento.
- Preserve quebras de linha, títulos, listas e tabelas quando possível.
- Se algum trecho estiver ilegível, escreva [ilegível].
"""

def extrair_com_modelo(caminho_imagem: Path, numero_pagina: int, modelo: str) -> str:
    print(f"Processando página {numero_pagina}: {caminho_imagem}")
    
    
    resposta = client.chat.completions.create(
        model=modelo,
        messages=[
            {
                "role": "system",
                "content": "Sua saída deve conter apenas o texto transcrito, sem comentários."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": PROMPT
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": imagem_para_data_url(caminho_imagem)
                        }
                    }
                ]
            }
        ],
        temperature=0,
        max_tokens=10000

    )
    '''
    inicio = time.perf_counter()
    duracao = time.perf_counter() - inicio
    usage = resposta.usage

    print(
    f"Página {numero_pagina} | "
    f"tempo={duracao:.2f}s | "
    f"entrada={getattr(usage, 'prompt_tokens', None)} | "
    f"saída={getattr(usage, 'completion_tokens', None)} | "
    f"total={getattr(usage, 'total_tokens', None)}"
    )

    #fim = time.perf_counter()
    #tempo_total = fim - inicio
    #print(f"\nO modelo {model} demorou {tempo_total:.2f}s")
    #if numero_pagina in [19, 20, 21, 22]:
    #    print(conteudo)
    #print("-"*25)
    '''
    conteudo = resposta.choices[0].message.content
    return conteudo

def processar_pdf_com_imagens_temporarias(
    caminho_pdf: str,
    dpi: int = 200,
    formato: str = "png",
    modelo: str = MODELO_OCR,
    cancelamento_evento: Event | None = None,
    ):
    pdf_path = Path(caminho_pdf)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")
    resultados = []
    with tempfile.TemporaryDirectory() as temp_dir:
        pasta_temp = Path(temp_dir)
        print(pasta_temp)
        doc = pymupdf.open(pdf_path)
        try:
            total_paginas = len(doc)
            zoom = dpi / 72
            matriz = pymupdf.Matrix(zoom, zoom)
            for indice_pagina in range(len(doc)):
                _verificar_interrupcao(cancelamento_evento)
                numero_pagina = indice_pagina + 1
                informar(
                    "Leitura visual do PDF",
                    f"Lendo página {numero_pagina} de {total_paginas}",
                    arquivo=pdf_path.name,
                    pagina=numero_pagina,
                    total_paginas=total_paginas,
                )
                pagina = doc[indice_pagina]
                pix = pagina.get_pixmap(
                    matrix=matriz,
                    alpha=False
                )
                caminho_imagem = pasta_temp / f"pagina_{numero_pagina:04d}.png"
                pix.save(caminho_imagem)
                resultado = extrair_com_modelo(
                    caminho_imagem=caminho_imagem,
                    numero_pagina=numero_pagina,
                    modelo=modelo,
                )
                resultados.append({
                    "pagina": numero_pagina,
                    #"imagem": str(caminho_imagem),
                    "resultado": resultado
                })
                _verificar_interrupcao(cancelamento_evento)

                #print(resultado)
        finally:
            doc.close()
    return resultados


# Extrai blocos úteis de um PDF, descartando cabeçalhos repetidos
def pdf_para_documentos(caminho_pdf: str | Path, cancelamento_evento: Event | None = None) -> list[Document]:
    _verificar_interrupcao(cancelamento_evento)

    fc.carregar_modelo(MODELO_OCR)

    try:
        lista_resultados = processar_pdf_com_imagens_temporarias(
            caminho_pdf=caminho_pdf,
            cancelamento_evento=cancelamento_evento,
        )
    finally:
        try:
            fc.descarregar_modelo(MODELO_OCR)
        except Exception as erro:
            print(f"Nao foi possivel descarregar o modelo de extracao: {erro}")

    _verificar_interrupcao(cancelamento_evento)


    todas_linhas: list[str] = []
    
    for pagina in lista_resultados:
        todas_linhas.extend(linha.strip() for linha in pagina["resultado"].splitlines())
    

    contador = Counter(linha for linha in todas_linhas if linha)
    documentos: list[Document] = []

    for pagina in lista_resultados:
        numero_pagina = pagina["pagina"]

        linhas_filtradas = [
            linha.strip()
            for linha in pagina["resultado"].splitlines()
            if linha.strip()
            and contador[linha.strip()] <= 3
            and len(linha.strip()) > 3
        ]

        if not linhas_filtradas:
            continue
        
        texto_pagina = "\n".join(linhas_filtradas)
        texto_pagina = re.sub(r"\n{3,}", "\n\n", texto_pagina)

        for trecho in (trecho.strip() for trecho in texto_pagina.split("\n")):
            if trecho:
                documentos.append(
                    Document(
                        page_content=trecho,
                        metadata={"page": numero_pagina},
                    )
                )

    return documentos

