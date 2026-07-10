"""Implementa a recuperação de contexto em PDF e a consulta ao modelo local."""

from __future__ import annotations

import re
import shutil

from pathlib import Path
from threading import Event


from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from scripts.extracao_texto_pdf import pdf_para_documentos

import scripts.funcoes_comuns as fc



# configuração do LM Studio
URL_BASE_API_PADRAO = "http://127.0.0.1:1234/v1"
CHAVE_API_PADRAO = "lm-studio"
MODELO_VETORIZACAO_PADRAO = "text-embedding-qwen3-embedding-0.6b"
MODELO_CONVERSA_PADRAO = "google/gemma-3n-e4b"

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
    if cancelamento_evento and cancelamento_evento.is_set():
        raise fc.ProcessamentoInterrompido("Processamento interrompido pelo usuario.")

# recebe doc langchain, define caminho do vectorstore e define os parâmetros do recuperador
def construir_recuperador(
    caminho_pdf: str | Path,
    raiz_persistencia: str | Path = "vectorstores",
    cancelamento_evento: Event | None = None,
):
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
    _verificar_interrupcao(cancelamento_evento)

    recuperador = armazenamento_vetorial.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 25, "fetch_k": 50, "lambda_mult": 0.9},
    )

    # retorna vectorstore com parâmetros
    return recuperador, diretorio_persistencia

# recebe embeddings, define modelo de LLM, cria estrutura para perguntas e ativa o LLM
def responder_perguntas(
    caminho_pdf: str | Path,
    perguntas: list[dict[str:str, str:str]],
    cancelamento_evento: Event | None = None,
    ) -> list[str]:
    # recebe o banco de vetores e passa o prompt
    recuperador, pasta_vectorstore = construir_recuperador(
        caminho_pdf,
        cancelamento_evento=cancelamento_evento,
    )
    instrucoes = ChatPromptTemplate.from_template(PROMPT)

    # define modelo de LLM
    modelo_linguagem = ChatOpenAI(
        model=MODELO_CONVERSA_PADRAO,
        openai_api_base=URL_BASE_API_PADRAO,
        openai_api_key=CHAVE_API_PADRAO,
        temperature=0,
    )
    cadeia = instrucoes | modelo_linguagem | StrOutputParser()

    # faz as perguntas
    respostas = []
    print("\nembedding ok\n")

    try:
        for pergunta in perguntas:
            _verificar_interrupcao(cancelamento_evento)
            resultados = recuperador.invoke(pergunta['pergunta'] + "\n" + pergunta['informacao_adicional'])
            _verificar_interrupcao(cancelamento_evento)
            contexto = "\n\n".join(
                f"Página: {documento.metadata.get('page')}; Conteúdo: {documento.page_content}"
                for documento in resultados
            )

            respostas.append(cadeia.invoke({"contexto": contexto, "pergunta": pergunta["pergunta"], "informacao_adicional": pergunta["informacao_adicional"]}))
            _verificar_interrupcao(cancelamento_evento)
    finally:
        try:
            fc.descarregar_modelo(MODELO_VETORIZACAO_PADRAO)
            print('modelo embedding descarregado')
        except Exception as erro:
            print(f"Não foi possível descarregar o modelo embedding: {erro}")

        try:
            fc.descarregar_modelo(MODELO_CONVERSA_PADRAO)
            print('modelo de consulta descarregado')
        except Exception as erro:
            print(f"Não foi possível descarregar o modelo de consulta: {erro}")

    return respostas
