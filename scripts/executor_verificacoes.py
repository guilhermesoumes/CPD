"""Orquestracao das verificacoes de completude e geracao dos RACs."""

from __future__ import annotations

import shutil
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Event
from typing import Literal, TypedDict

import scripts.funcoes_comuns as fc
from scripts.mecanismo_rag import responder_perguntas
from scripts.verificacao_ART import verificar_art
from scripts.status_processamento import informar


class PerguntaVerificacao(TypedDict):
    """Estrutura declarativa de uma pergunta enviada ao RAG."""

    pergunta: str
    informacao_adicional: str


@dataclass(frozen=True)
class ConfiguracaoVerificacao:
    """Metadados e perguntas que definem uma disciplina."""

    nome_disciplina: str
    codigo_saida: str
    tipo_modelo: Literal["estudo", "projeto"]
    perguntas: list[PerguntaVerificacao]


PERGUNTA_ART: PerguntaVerificacao = {
    "pergunta": "O documento apresenta Anotacao de Responsabilidade Tecnica (ART)?",
    "informacao_adicional": "",
}

_cancelamento_evento: Event | None = None


def definir_cancelamento_evento(cancelamento_evento: Event | None) -> None:
    """Define o evento cooperativo usado pela execucao atual."""

    global _cancelamento_evento
    _cancelamento_evento = cancelamento_evento


def _verificar_interrupcao() -> None:
    fc.verificar_interrupcao(_cancelamento_evento)


def _diretorio_resultado(
    configuracao: ConfiguracaoVerificacao,
    dados_aplicacao: dict,
) -> Path:
    """Monta o diretorio de exportacao da disciplina."""

    raiz_resultados = Path(dados_aplicacao["diretorio-resultados"])
    codigo_rodovia = dados_aplicacao["rodovia"].replace("/", "-")
    codigo_lote = dados_aplicacao["lote"]
    return raiz_resultados / f"{codigo_rodovia}_LT{codigo_lote}" / configuracao.nome_disciplina


def _caminho_proximo_relatorio(
    diretorio_saida: Path,
    configuracao: ConfiguracaoVerificacao,
    dados_aplicacao: dict,
) -> Path:
    """Retorna o caminho versionado do proximo RAC."""

    nome_saida = fc.proximo_nome_relatorio(
        diretorio_saida,
        str(datetime.now().year),
        dados_aplicacao["rodovia"].replace("/", "-"),
        configuracao.codigo_saida,
        dados_aplicacao["lote"],
    )
    return diretorio_saida / f"{nome_saida}.pdf"


def _gerar_relatorio(configuracao: ConfiguracaoVerificacao, **dados_relatorio) -> None:
    """Seleciona o tipo visual e delega a composicao do RAC."""

    tipos_relatorio = {"estudo": "Estudo", "projeto": "Projeto"}
    from templates.relatorio_pdf import gerar_relatorio_pdf

    gerar_relatorio_pdf(
        tipo_relatorio=tipos_relatorio[configuracao.tipo_modelo],
        **dados_relatorio,
    )


def _resposta_art(paginas_art: list[int]) -> str:
    """Converte as paginas classificadas como ART para o formato do RAC."""

    if not paginas_art:
        return "1. Nao\n2. -\n3. Nao"

    evidencias = "\n".join(
        f"- Trecho: ART identificada, na pagina: {pagina}"
        for pagina in paginas_art
    )
    return f"1. Sim\n2. {evidencias}\n3. Sim"


def executar_verificacao_conteudo(configuracao: ConfiguracaoVerificacao) -> None:
    """Executa a disciplina para cada PDF configurado e gera um RAC por entrada."""

    dados_aplicacao = fc.carregar_configuracao(fc.caminho_configuracao_usuario())
    arquivos_pdf = dados_aplicacao.get("arquivos-para-analisar") or []
    if not arquivos_pdf:
        raise ValueError("Nenhum PDF foi selecionado para analise.")

    diretorio_saida = _diretorio_resultado(configuracao, dados_aplicacao)
    fc.garantir_diretorios_saida(diretorio_saida)

    pasta_vectorstores = Path(fc.resolve_caminho("vectorstores"))
    shutil.rmtree(pasta_vectorstores, ignore_errors=True)

    total_arquivos = len(arquivos_pdf)
    for indice_arquivo, arquivo_pdf in enumerate(arquivos_pdf, start=1):
        _verificar_interrupcao()
        inicio = time.perf_counter()
        informar(
            "Preparação",
            f"Processando arquivo {indice_arquivo} de {total_arquivos}",
            arquivo=Path(arquivo_pdf).name,
        )

        # A configuracao declarativa permanece intacta entre PDFs e execucoes.
        perguntas = [dict(pergunta) for pergunta in configuracao.perguntas]
        respostas, recuperador = responder_perguntas(
            arquivo_pdf,
            perguntas,
            cancelamento_evento=_cancelamento_evento,
        )

        paginas_art = verificar_art(
            caminho_pdf=arquivo_pdf,
            cancelamento_evento=_cancelamento_evento,
            recuperador=recuperador,
        )
        perguntas.append(dict(PERGUNTA_ART))
        respostas.append(_resposta_art(paginas_art))

        _verificar_interrupcao()
        duracao_minutos = (time.perf_counter() - inicio) / 60
        tempo_processamento = (
            "Tempo de processamento do documento foi de aproximadamente "
            f"{duracao_minutos:.2f}min"
        )

        informar("Geração do relatório", "Montando o arquivo RAC", arquivo=Path(arquivo_pdf).name)
        _gerar_relatorio(
            configuracao,
            caminho_pdf=str(
                _caminho_proximo_relatorio(
                    diretorio_saida,
                    configuracao,
                    dados_aplicacao,
                )
            ),
            nome_disciplina=configuracao.nome_disciplina,
            relatorio_analisado=Path(arquivo_pdf),
            tempo_de_processamento=tempo_processamento,
            perguntas=[item["pergunta"] for item in perguntas],
            respostas=respostas,
        )
        informar(
            "Arquivo concluído",
            f"Arquivo {indice_arquivo} de {total_arquivos} concluído",
            arquivo=Path(arquivo_pdf).name,
        )
