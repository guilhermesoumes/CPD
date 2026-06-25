"""Orquestra a análise de conteúdo e a geração dos relatórios RAC."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from xml.sax.saxutils import escape

import scripts.funcoes_comuns as fc
from scripts.mecanismo_rag import responder_perguntas


@dataclass(frozen=True)
class ConfiguracaoVerificacao:
    """Define os dados necessários para verificar uma disciplina."""

    nome_disciplina: str
    codigo_saida: str
    tipo_modelo: str
    perguntas: list[str]


def _diretorio_resultado(configuracao_verificacao: ConfiguracaoVerificacao, configuracao_aplicacao: dict) -> Path:
    """Monta o diretório de saída da disciplina e do lote analisado."""

    raiz_resultados = Path(configuracao_aplicacao["diretorio-resultados"])
    codigo_rodovia = configuracao_aplicacao["rodovia"].replace("/", "-")
    codigo_lote = configuracao_aplicacao["lote"]
    return raiz_resultados / f"{codigo_rodovia}_LT{codigo_lote}" / configuracao_verificacao.nome_disciplina


def _caminho_proximo_relatorio(diretorio_saida: Path, configuracao_verificacao: ConfiguracaoVerificacao, configuracao_aplicacao: dict) -> Path:
    """Gera o caminho do relatório com o próximo número de versão disponível."""

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


def _gerar_relatorio(configuracao_verificacao: ConfiguracaoVerificacao, **dados_relatorio) -> None:
    """Encaminha os dados analisados ao gerador único de relatório PDF."""

    tipos_relatorio = {"estudo": "Estudo", "projeto": "Projeto"}
    try:
        tipo_relatorio = tipos_relatorio[configuracao_verificacao.tipo_modelo]
    except KeyError as erro:
        raise ValueError(
            f"Tipo de modelo inválido: {configuracao_verificacao.tipo_modelo}"
        ) from erro

    from checks.templates.relatorio_pdf import gerar_relatorio_pdf

    gerar_relatorio_pdf(tipo_relatorio=tipo_relatorio, **dados_relatorio)

def executar_verificacao_conteudo(configuracao_verificacao: ConfiguracaoVerificacao) -> None:
    """Executa a análise dos PDFs configurados e grava um RAC para cada arquivo."""

    arquivo_configuracao = fc.caminho_recurso("config.json")
    configuracao_aplicacao = fc.carregar_configuracao(arquivo_configuracao)

    arquivos_pdf = configuracao_aplicacao.get("arquivos-para-analisar") or []
    if not arquivos_pdf:
        raise ValueError("Nenhum PDF foi selecionado para análise.")

    diretorio_saida = _diretorio_resultado(configuracao_verificacao, configuracao_aplicacao)
    fc.garantir_diretorios_saida(str(diretorio_saida))
    
    def preparar_texto_reportlab(texto: str) -> str:
        """Escapa texto livre preservando as quebras aceitas pelo ReportLab."""

        texto = re.sub(r"<br\s*/?>", "<br/>", texto, flags=re.I)

        marcador = "__BR_TEMP__"
        texto = texto.replace("<br/>", marcador)

        texto = escape(texto)

        texto = texto.replace(marcador, "<br/>")

        return texto


    def preparar_resposta_para_reportlab(resposta: str) -> str: # passa resposta a resposta da lista de repostas
        """Extrai e formata a parte descritiva de uma resposta do modelo."""

        blocos = re.findall(r"\d+\.\s*(.*?)(?=\n\d+\.|$)", resposta, flags=re.S) # quebra a resposta em 3 partes: sim ou não, trecho e conclusão com sim ou não.

        if len(blocos) >= 2: # sempre maior que 2
            texto = blocos[1] # bloco = trecho que comprova
        else:
            texto = resposta

        texto = texto.replace("'''", "")
        texto = texto.strip()
        texto = re.sub(r"\n{3,}", "\n\n", texto)
        texto = texto.replace("\n", "<br/>")

        # termina com texto do trecho tratado

        return preparar_texto_reportlab(texto) # retorna um texto tratado com o trecho que comprova


    for arquivo_pdf in arquivos_pdf:
        respostas = responder_perguntas(arquivo_pdf, configuracao_verificacao.perguntas) # lista com respostas sobre o aquivo
        #print("respostas:")
        #print(respostas)

        respostas_tratadas = [ # lista apenas com o trecho que comprova de cada pergunta, ou seja, apenas com os itens 2 das perguntas
            preparar_resposta_para_reportlab(resposta)
            for resposta in respostas
        ]
        #print("respostas_tratadas:")
        #print(respostas_tratadas)
        _gerar_relatorio(
            configuracao_verificacao,
            caminho_pdf=str(_caminho_proximo_relatorio(diretorio_saida, configuracao_verificacao, configuracao_aplicacao)),
            nome_disciplina=configuracao_verificacao.nome_disciplina,
            relatorio_analisado=Path(arquivo_pdf).name,
            pontuacao_geral="",
            perguntas=configuracao_verificacao.perguntas,
            respostas=respostas, # respostas tratadas é a lista com os itens 2. de cada pergunta. É o que compõe a coluna 3.
        )
