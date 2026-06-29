from openai import OpenAI
from pathlib import Path
import base64
import mimetypes
import time
import re

import pymupdf
import tempfile
from pathlib import Path

from langchain_core.documents import Document
from collections import Counter

# configuração do LM Studio
URL_BASE_API_PADRAO = "http://127.0.0.1:1234/v1"
CHAVE_API_PADRAO = "lm-studio"
MODELO_SCAN = "glm-ocr"

client = OpenAI(
    base_url=URL_BASE_API_PADRAO,
    api_key=CHAVE_API_PADRAO  # pode ser qualquer texto no LM Studio local
)

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

def extrair_com_modelo(caminho_imagem: Path, numero_pagina: int, model: str):
    print(f"Processando página {numero_pagina}: {caminho_imagem}")
    #inicio = time.perf_counter()
    resposta = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Você é um motor de transcrição OCR. Sua saída deve conter apenas o texto transcrito, sem comentários."
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
    )
    #fim = time.perf_counter()
    #tempo_total = fim - inicio
    #print(f"\nO modelo {model} demorou {tempo_total:.2f}s")
    conteudo = resposta.choices[0].message.content
    #print(conteudo)
    #print("-"*25)
    return conteudo

def processar_pdf_com_imagens_temporarias(
    caminho_pdf: str,
    dpi: int = 200,
    formato: str = "png",
    model:str = MODELO_SCAN,
    ):
    pdf_path = Path(caminho_pdf)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")
    resultados = []
    with tempfile.TemporaryDirectory() as temp_dir:
        pasta_temp = Path(temp_dir)
        print(pasta_temp)
        doc = pymupdf.open(pdf_path)
        zoom = dpi / 72
        matriz = pymupdf.Matrix(zoom, zoom)
        for indice_pagina in range(len(doc)):
            numero_pagina = indice_pagina + 1
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
                model=model
            )
            resultados.append({
                "pagina": numero_pagina,
                #"imagem": str(caminho_imagem),
                "resultado": resultado
            })
        doc.close()
    return resultados


# Extrai blocos úteis de um PDF, descartando cabeçalhos repetidos
def pdf_para_documentos(caminho_pdf: str | Path) -> list[Document]:

    lista_resultados = processar_pdf_com_imagens_temporarias(caminho_pdf=caminho_pdf)

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


    # ===============================================================
    '''
    inicio_modelo = time.perf_counter()

    resultados = processar_pdf_com_imagens_temporarias(
        caminho_pdf=r"Relatório Volume 2 - Tomo III - Estudo de Traçado lote 2 (6525159).pdf",
        dpi=200,
        model=MODELO_SCAN
    )

    for item in resultados:
        print()
        print(f"Página: {item['pagina']}")
        print(f"Resultado: {item['resultado']}")
    
    fim_modelo = time.perf_counter()

    tempo_total_do_modelo = fim_modelo - inicio_modelo

    print(f"\n\n\n O tempo total para extrair o texto do documento foi de {tempo_total_do_modelo:.2f}s, que corresponde a {(tempo_total_do_modelo/60):.2f}min")
    '''

