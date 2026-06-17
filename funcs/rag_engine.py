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


DEFAULT_API_BASE = "http://127.0.0.1:1234/v1"
DEFAULT_API_KEY = "lm-studio"
DEFAULT_EMBEDDING_MODEL = "text-embedding-qwen3-embedding-0.6b"
DEFAULT_CHAT_MODEL = "google/gemma-3n-e4b"


PROMPT_TEMPLATE = """
Voce e um especialista em analise de documentos tecnicos de engenharia.

Use exclusivamente as informacoes presentes no contexto.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}

INSTRUCOES:
- Nao invente informacoes.
- Nao utilize conhecimento externo.
- Se a informacao nao estiver claramente presente, responda que ela nao foi encontrada.
- Considere equivalencias semanticas e terminologias tecnicas relacionadas.

FORMATO DA RESPOSTA:

1. Informacao encontrada?
Responda apenas: SIM ou NAO

2. Trechos comprobatorios:
Apresente os trechos exatos e a pagina encontrados no documento no formato:
- Trecho: (trecho), na pagina: (pagina)

3. Conclusao:
Responda apenas:
SIM
ou
NAO
"""


def _sanitize_collection_name(path: str | Path) -> str:
    name = Path(path).stem
    name = re.sub(r"[^a-zA-Z0-9_-]+", "_", name).strip("_")
    return name or "documento"


def pdf_to_documents(pdf_path: str | Path, repeated_line_limit: int = 2) -> list[Document]:
    pages = pmp.to_markdown(
        str(pdf_path),
        header=False,
        footer=False,
        page_chunks=True,
        show_progress=False,
    )

    all_lines: list[str] = []
    for page in pages:
        all_lines.extend(line.strip() for line in page["text"].splitlines())

    counter = Counter(line for line in all_lines if line)
    documents: list[Document] = []

    for page in pages:
        page_number = page["metadata"]["page_number"]
        filtered_lines = [
            line.strip()
            for line in page["text"].splitlines()
            if line.strip()
            and counter[line.strip()] <= repeated_line_limit
            and len(line.strip()) > 3
        ]

        if not filtered_lines:
            continue

        page_text = "\n".join(filtered_lines)
        page_text = re.sub(r"\n{3,}", "\n\n", page_text)

        for chunk in (chunk.strip() for chunk in page_text.split("\n\n")):
            if chunk:
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={"page": page_number},
                    )
                )

    return documents


def build_retriever(pdf_path: str | Path, persist_root: str | Path = "vectorstores"):
    documents = pdf_to_documents(pdf_path)
    if not documents:
        raise ValueError(f"Nenhum texto util foi extraido de {pdf_path}.")

    persist_directory = Path(persist_root) / _sanitize_collection_name(pdf_path)
    shutil.rmtree(persist_directory, ignore_errors=True)
    persist_directory.mkdir(parents=True, exist_ok=True)

    embeddings = OpenAIEmbeddings(
        model=DEFAULT_EMBEDDING_MODEL,
        openai_api_base=DEFAULT_API_BASE,
        openai_api_key=DEFAULT_API_KEY,
        check_embedding_ctx_length=False,
    )

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(persist_directory),
    )

    return vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 8, "fetch_k": 24, "lambda_mult": 0.75},
    )


def answer_questions(pdf_path: str | Path, questions: list[str]) -> list[str]:
    retriever = build_retriever(pdf_path)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = ChatOpenAI(
        model=DEFAULT_CHAT_MODEL,
        openai_api_base=DEFAULT_API_BASE,
        openai_api_key=DEFAULT_API_KEY,
        temperature=0,
    )
    chain = prompt | llm | StrOutputParser()

    answers: list[str] = []
    for question in questions:
        results = retriever.invoke(question)
        context = "\n\n".join(
            f"Pagina: {doc.metadata.get('page')}; Conteudo: {doc.page_content}"
            for doc in results
        )
        answers.append(chain.invoke({"contexto": context, "pergunta": question}))

    return answers
