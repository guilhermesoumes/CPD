"""Implementa a recuperação de contexto em PDF e a consulta ao modelo local."""

from __future__ import annotations

import re
import shutil

from pathlib import Path


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

# recebe doc langchain, define caminho do vectorstore e define os parâmetros do recuperador
def construir_recuperador(caminho_pdf: str | Path, raiz_persistencia: str | Path = "vectorstores"):
    # recebe texto do pdf
    documentos = pdf_para_documentos(caminho_pdf)

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

    recuperador = armazenamento_vetorial.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 20, "fetch_k": 40, "lambda_mult": 0.9},
    )

    # retorna vectorstore com parâmetros
    return recuperador, diretorio_persistencia

# recebe embeddings, define modelo de LLM, cria estrutura para perguntas e ativa o LLM
def responder_perguntas(caminho_pdf: str | Path, perguntas: list[str]) -> list[str]:
    # recebe o banco de vetores e passa o prompt
    recuperador, pasta_vectorstore = construir_recuperador(caminho_pdf)
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
    respostas: list[str] = []
    print("\nembedding ok\n")
    try:
        for pergunta in perguntas:
            resultados = recuperador.invoke(pergunta)
            print("\npergunta feita\n")

            contexto = "\n\n".join(
                f"Pagina: {documento.metadata.get('page')}; Conteúdo: {documento.page_content}"
                for documento in resultados
            )

            respostas.append(cadeia.invoke({"contexto": contexto, "pergunta": pergunta}))
    finally:
        del modelo_linguagem
        del cadeia
        #shutil.rmtree(pasta_vectorstore, ignore_errors=True)

        fc.descarregar_modelo(MODELO_VETORIZACAO_PADRAO)
        print('modelo embedding descarregado')

        fc.descarregar_modelo(MODELO_CONVERSA_PADRAO)
        print('modelo de consulta descarregado')


    return respostas
