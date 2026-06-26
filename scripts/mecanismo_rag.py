"""Implementa a recuperação de contexto em PDF e a consulta ao modelo local."""

from __future__ import annotations

import re
import shutil
from collections import Counter
from pathlib import Path

import pymupdf4llm as pmp
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# configuração do LM Studio
URL_BASE_API_PADRAO = "http://127.0.0.1:1234/v1"
CHAVE_API_PADRAO = "lm-studio"
MODELO_VETORIZACAO_PADRAO = "text-embedding-qwen3-embedding-0.6b"
MODELO_CONVERSA_PADRAO = "google/gemma-3n-e4b"

# prompt
INSTRUCOES_MODELO = """
Você é um especialista em análise de documentos técnicos de engenharia.

Use exclusivamente as informações presentes no contexto.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}

INSTRUÇÕES:
- Não invente informações.
- Não utilize conhecimento externo.
- Se a informação não estiver claramente presente, responda que ela não foi encontrada.
- Considere equivalências semânticas e terminologias tácnicas relacionadas.

FORMATO DA RESPOSTA:

1. Informação encontrada?
Responda apenas: SIM ou NÃO

2. Trechos comprobatórios:
Apresente os trechos exatos e a página encontrados no documento no formato:
- Trecho: (trecho), na página: (pagina)

3. Conclusão:
Responda apenas:
SIM
ou
NÃO
"""


# normalizar o nome de coleção compatível com o armazenamento vetorial
def _normalizar_nome_vectorstore(caminho: str | Path) -> str:
    nome = Path(caminho).stem
    nome = re.sub(r"[^a-zA-Z0-9_-]+", "_", nome).strip("_")
    return nome or "documento"

# Alterar!!!!!!!!!
def pdf_para_documentos(caminho_pdf: str | Path, limite_linhas_repetidas: int = 2) -> list[Document]:
    """Extrai blocos úteis de um PDF, descartando cabeçalhos repetidos."""

    paginas = pmp.to_markdown(
        str(caminho_pdf),
        header=False,
        footer=False,
        page_chunks=True,
        show_progress=False,
    )

    todas_linhas: list[str] = []
    for pagina in paginas:
        todas_linhas.extend(linha.strip() for linha in pagina["text"].splitlines())

    contador = Counter(linha for linha in todas_linhas if linha)
    documentos: list[Document] = []

    for pagina in paginas:
        numero_pagina = pagina["metadata"]["page_number"]
        linhas_filtradas = [
            linha.strip()
            for linha in pagina["text"].splitlines()
            if linha.strip()
            and contador[linha.strip()] <= limite_linhas_repetidas
            and len(linha.strip()) > 3
        ]

        if not linhas_filtradas:
            continue

        texto_pagina = "\n".join(linhas_filtradas)
        texto_pagina = re.sub(r"\n{3,}", "\n\n", texto_pagina)

        for trecho in (trecho.strip() for trecho in texto_pagina.split("\n\n")):
            if trecho:
                documentos.append(
                    Document(
                        page_content=trecho,
                        metadata={"page": numero_pagina},
                    )
                )

    return documentos

# recebe doc langchain, define caminho do vectorstore e define os parâmetros do recuperador
def construir_recuperador(caminho_pdf: str | Path, raiz_persistencia: str | Path = "vectorstores"):
    # recebe texto do pdf
    documentos = pdf_para_documentos(caminho_pdf)
    if not documentos:
        raise ValueError(f"Nenhum texto util foi extraido de {caminho_pdf}.")

    # define caminho do vectorstore
    diretorio_persistencia = Path(raiz_persistencia) / _normalizar_nome_vectorstore(caminho_pdf)
    shutil.rmtree(diretorio_persistencia, ignore_errors=True)
    diretorio_persistencia.mkdir(parents=True, exist_ok=True)

    # cria os chunks
    vetores_representacao = OpenAIEmbeddings(
        model=MODELO_VETORIZACAO_PADRAO,
        openai_api_base=URL_BASE_API_PADRAO,
        openai_api_key=CHAVE_API_PADRAO,
        check_embedding_ctx_length=False,
    )

    # armazena os chunks no vectorstore
    armazenamento_vetorial = Chroma.from_documents(
        documents=documentos,
        embedding=vetores_representacao,
        persist_directory=str(diretorio_persistencia),
    )

    # retorna vectorstore com parâmetros
    return armazenamento_vetorial.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 20, "fetch_k": 40, "lambda_mult": 0.9},
    )

# recebe embeddings, define modelo de LLM, cria estrutura para perguntas e ativa o LLM
def responder_perguntas(caminho_pdf: str | Path, perguntas: list[str]) -> list[str]:
    # recebe o banco de vetores e passa o prompt
    recuperador = construir_recuperador(caminho_pdf)
    instrucoes = ChatPromptTemplate.from_template(INSTRUCOES_MODELO)

    # define modelo de LLM
    modelo_linguagem = ChatOpenAI(
        model=MODELO_CONVERSA_PADRAO,
        openai_api_base=URL_BASE_API_PADRAO,
        openai_api_key=CHAVE_API_PADRAO,
        temperature=0,
    )
    cadeia = instrucoes | modelo_linguagem | StrOutputParser()

    # faz as perguntas
    respostas: list[str] = []
    for pergunta in perguntas:
        resultados = recuperador.invoke(pergunta)

        contexto = "\n\n".join(
            f"Pagina: {documento.metadata.get('page')}; Conteúdo: {documento.page_content}"
            for documento in resultados
        )

        respostas.append(cadeia.invoke({"contexto": contexto, "pergunta": pergunta}))

    return respostas
