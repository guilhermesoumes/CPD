from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import time

from xml.sax.saxutils import escape

import scripts.funcoes_comuns as fc
from scripts.mecanismo_rag import responder_perguntas


# classe com os dados da disciplina a ser verificada
@dataclass(frozen=True)
class ConfiguracaoVerificacao:
    nome_disciplina: str
    codigo_saida: str
    tipo_modelo: str
    perguntas: list[str]


# cria caminho para próximo relatório
def _caminho_proximo_relatorio(diretorio_saida: Path, configuracao_verificacao: ConfiguracaoVerificacao, configuracao_aplicacao: dict) -> Path:
    codigo_rodovia = configuracao_aplicacao["rodovia"].replace("/", "-")
    codigo_lote = configuracao_aplicacao["lote"]
    nome_saida = fc.proximo_nome_relatorio(
        str(diretorio_saida),
        str(datetime.now().year),
        codigo_rodovia,
        configuracao_verificacao.codigo_saida,
        codigo_lote,
    )
    return diretorio_saida / f"{nome_saida}.pdf"


# gatilho para ativar gerador de relatório com base no tipo de relatório
def _gerar_relatorio(configuracao_verificacao: ConfiguracaoVerificacao, **dados_relatorio) -> None:
    tipos_relatorio = {"estudo": "Estudo", "projeto": "Projeto"}
    try:
        tipo_relatorio = tipos_relatorio[configuracao_verificacao.tipo_modelo]
    except KeyError as erro:
        raise ValueError(
            f"Tipo de modelo inválido: {configuracao_verificacao.tipo_modelo}"
        ) from erro

    from templates.relatorio_pdf import gerar_relatorio_pdf

    gerar_relatorio_pdf(tipo_relatorio=tipo_relatorio, **dados_relatorio)


# monta o diretório de exportação dos resultados
def _diretorio_resultado(configuracao_verificacao: ConfiguracaoVerificacao, configuracao_aplicacao: dict) -> Path:
    raiz_resultados = Path(configuracao_aplicacao["diretorio-resultados"])
    codigo_rodovia = configuracao_aplicacao["rodovia"].replace("/", "-")
    codigo_lote = configuracao_aplicacao["lote"]
    return raiz_resultados / f"{codigo_rodovia}_LT{codigo_lote}" / configuracao_verificacao.nome_disciplina


# executa a análise dos PDFs configurados e grava um RAC para cada arquivo
def executar_verificacao_conteudo(configuracao_verificacao: ConfiguracaoVerificacao) -> None:
    configuracao_aplicacao = fc.carregar_configuracao(fc.resolve_caminho("config.json"))

    arquivos_pdf = configuracao_aplicacao.get("arquivos-para-analisar") or []
    if not arquivos_pdf:
        raise ValueError("Nenhum PDF foi selecionado para análise.")

    diretorio_saida = _diretorio_resultado(configuracao_verificacao, configuracao_aplicacao)
    fc.garantir_diretorios_saida(str(diretorio_saida))

    for arquivo_pdf in arquivos_pdf:
        inicio_modelo = time.perf_counter()
        respostas = responder_perguntas(arquivo_pdf, configuracao_verificacao.perguntas) # lista com respostas sobre o aquivo
        fim_modelo = time.perf_counter()

        tempo_total_do_modelo = fim_modelo - inicio_modelo

        tempo_total_do_modelo = f"O tempo total para tratamento do documento foi de aproximadamente {(tempo_total_do_modelo/60):.2f}min"
        _gerar_relatorio(
            configuracao_verificacao,
            caminho_pdf=str(_caminho_proximo_relatorio(diretorio_saida, configuracao_verificacao, configuracao_aplicacao)),
            nome_disciplina=configuracao_verificacao.nome_disciplina,
            relatorio_analisado=Path(arquivo_pdf).name,
            tempo_de_processamento = tempo_total_do_modelo,
            pontuacao_geral="",
            perguntas=configuracao_verificacao.perguntas,
            respostas=respostas, # respostas tratadas é a lista com os itens 2. de cada pergunta. É o que compõe a coluna 3.
        )
