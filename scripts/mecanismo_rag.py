"""Implementa a recuperação de contexto em PDF e a consulta ao modelo local."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from threading import Event
from typing import Any


from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from scripts.extracao_texto_pdf import pdf_para_documentos

import scripts.funcoes_comuns as fc
from scripts.status_processamento import informar
from scripts.configuracao import (
    CHAVE_API,
    MODELO_CONVERSA,
    MODELO_EMBEDDING,
    URL_API_OPENAI,
)

# configuração do LM Studio
# prompt
PROMPT = """
Você é um especialista em análise de documentos técnicos de engenharia.

Use exclusivamente as informações presentes no contexto.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}
{informacao_adicional}

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


def _verificar_interrupcao(cancelamento_evento: Event | None) -> None:
    fc.verificar_interrupcao(cancelamento_evento)

# recebe doc langchain, define caminho do vectorstore e define os parâmetros do recuperador
def construir_recuperador(
    caminho_pdf: str | Path,
    raiz_persistencia: str | Path = "vectorstores",
    cancelamento_evento: Event | None = None,
):
    nome_arquivo = Path(caminho_pdf).name
    informar("Leitura visual do PDF", "Preparando páginas para leitura", arquivo=nome_arquivo)
    # recebe texto do pdf
    documentos = pdf_para_documentos(caminho_pdf, cancelamento_evento=cancelamento_evento)
    _verificar_interrupcao(cancelamento_evento)

    if not documentos:
        raise ValueError(f"Nenhum texto util foi extraido de {caminho_pdf}.")
    
    # define caminho do vectorstore
    #diretorio_persistencia = Path(raiz_persistencia)
    diretorio_persistencia = Path(raiz_persistencia) / _normalizar_nome_vectorstore(caminho_pdf)
    shutil.rmtree(diretorio_persistencia, ignore_errors=True)
    diretorio_persistencia.mkdir(parents=True, exist_ok=True)

    # cria os chunks
    vetores_representacao = OpenAIEmbeddings(
        model=MODELO_EMBEDDING,
        openai_api_base=URL_API_OPENAI,
        openai_api_key=CHAVE_API,
        check_embedding_ctx_length=False,
    )

    # armazena os chunks no vectorstore
    informar("Embedding", f"Criando embeddings de {len(documentos)} trechos", arquivo=nome_arquivo)
    armazenamento_vetorial = Chroma.from_documents(
        documents=documentos,
        embedding=vetores_representacao,
        persist_directory=str(diretorio_persistencia),
    )

    _verificar_interrupcao(cancelamento_evento)
    informar("Embedding", "Embeddings concluídos", arquivo=nome_arquivo)

    recuperador = armazenamento_vetorial.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 25, "fetch_k": 50, "lambda_mult": 0.9},
    )

    # retorna vectorstore com parâmetros
    return recuperador, diretorio_persistencia

# recebe embeddings, define modelo de LLM, cria estrutura para perguntas e ativa o LLM
def responder_perguntas(
    caminho_pdf: str | Path,
    perguntas: list[dict[str, str]],
    cancelamento_evento: Event | None = None,
    ) -> tuple[list[str], Any]:
    # recebe o banco de vetores e passa o prompt
    recuperador, pasta_vectorstore = construir_recuperador(
        caminho_pdf,
        cancelamento_evento=cancelamento_evento,
    )
    instrucoes = ChatPromptTemplate.from_template(PROMPT)

    # define modelo de LLM
    modelo_linguagem = ChatOpenAI(
        model=MODELO_CONVERSA,
        openai_api_base=URL_API_OPENAI,
        openai_api_key=CHAVE_API,
        temperature=0,
    )
    cadeia = instrucoes | modelo_linguagem | StrOutputParser()

    # faz as perguntas
    respostas = []
    print("\nembedding ok\n")

    try:
        total_perguntas = len(perguntas)
        for indice_pergunta, pergunta in enumerate(perguntas, start=1):
            _verificar_interrupcao(cancelamento_evento)
            informar(
                "Análise das perguntas",
                f"Processando pergunta {indice_pergunta} de {total_perguntas}",
                arquivo=Path(caminho_pdf).name,
            )
            resultados = recuperador.invoke(pergunta['pergunta'] + "\n" + pergunta['informacao_adicional'])
            _verificar_interrupcao(cancelamento_evento)
            contexto = "\n\n".join(
                f"Página: {documento.metadata.get('page')}; Conteúdo: {documento.page_content}"
                for documento in resultados
            )

            respostas.append(cadeia.invoke({"contexto": contexto, "pergunta": pergunta["pergunta"], "informacao_adicional": pergunta["informacao_adicional"]}))
            _verificar_interrupcao(cancelamento_evento)
            informar(
                "Análise das perguntas",
                f"Pergunta {indice_pergunta} de {total_perguntas} concluída",
                arquivo=Path(caminho_pdf).name,
                perguntas_concluidas=indice_pergunta,
                total_perguntas=total_perguntas,
            )
    finally:
        try:
            fc.descarregar_modelo(MODELO_EMBEDDING)
            print('modelo embedding descarregado')
        except Exception as erro:
            print(f"Não foi possível descarregar o modelo embedding: {erro}")

        try:
            fc.descarregar_modelo(MODELO_CONVERSA)
            print('modelo de consulta descarregado')
        except Exception as erro:
            print(f"Não foi possível descarregar o modelo de consulta: {erro}")

    return respostas, recuperador
