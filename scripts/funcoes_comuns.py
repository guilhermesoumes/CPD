"""Funções compartilhadas de configuração, normalização e caminhos de saída."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from threading import Event

import requests

from typing import Any

from scripts.configuracao import (
    CHAVE_API,
    CONTEXTO_MODELO,
    MODELOS_CONHECIDOS,
    TIMEOUT_MODELO,
    URL_API_MODELOS,
)

RAIZ_PROJETO = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
MODELOS_CARREGADOS: set[str] = set()


class ProcessamentoInterrompido(Exception):
    """Indica que o usuario solicitou a interrupcao do processamento."""


def verificar_interrupcao(cancelamento_evento: Event | None) -> None:
    """Interrompe o fluxo quando o evento cooperativo estiver sinalizado."""

    if cancelamento_evento and cancelamento_evento.is_set():
        raise ProcessamentoInterrompido("Processamento interrompido pelo usuario.")


def caminho_configuracao_usuario() -> Path:
    """Retorna o arquivo persistente de configuracao da aplicacao."""

    if sys.platform == "win32":
        pasta_base = Path.home() / "AppData" / "Local"
    else:
        pasta_base = Path.home() / ".local" / "share"

    pasta_aplicacao = pasta_base / "CPD-DNIT"
    pasta_aplicacao.mkdir(parents=True, exist_ok=True)

    caminho_config = pasta_aplicacao / "config.json"

    print("USUÁRIO ATUAL:", Path.home())
    print("PASTA DA APLICAÇÃO:", pasta_aplicacao)
    print("ARQUIVO DE CONFIGURAÇÃO:", caminho_config)
    
    return pasta_aplicacao / "config.json"

# retorna caminho da pasta ou arquivo considerando também pacotes PyInstaller
def resolve_caminho(caminho_relativo: str) -> str:
    return str(RAIZ_PROJETO / caminho_relativo)

# puxa informações de um aquivo 
def carregar_configuracao(arquivo_configuracao: str | Path) -> dict:
    caminho = Path(arquivo_configuracao)

    if caminho.exists():
        with caminho.open("r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    return {}

# cria a pasta de saída dos resultados
def garantir_diretorios_saida(pasta: str | Path) -> None:
    Path(pasta).mkdir(parents=True, exist_ok=True)

# formatar valor de lote
def padronizar_lote(valor: str) -> str:
    texto = str(valor).strip()
    correspondencia = re.match(r"^(\d+)([A-Za-z]?)$", texto)
    if not correspondencia:
        return texto
    numero, letra = correspondencia.groups()
    return f"{numero.zfill(2)}{letra.upper()}"

# cria o nome do próximo relatório 
def proximo_nome_relatorio(diretorio_saida: str | Path, ano: str, codigo_rodovia: str, codigo_disciplina: str, codigo_lote: str) -> str:
    caminho_saida = Path(diretorio_saida)

    # cria a pasta 
    caminho_saida.mkdir(parents=True, exist_ok=True)

    # cria padrão de nomenclatura
    padrao = re.compile(
        rf"RAC-(\d{{3}})-{ano}_BR-{re.escape(codigo_rodovia)}_{re.escape(codigo_disciplina)}_LT-{re.escape(codigo_lote)}",
        re.IGNORECASE,
    )

    # conta quantos arquivos estão na pasta
    versoes = [
        int(correspondencia.group(1))
        for arquivo in caminho_saida.iterdir()
        if arquivo.is_file() and (correspondencia := padrao.match(arquivo.name))
    ]

    # número da próxima versão
    proxima_versao = max(versoes) + 1 if versoes else 1

    # retorna o texto com o nome da próxima versão de RAC
    return f"RAC-{proxima_versao:03d}-{ano}_BR-{codigo_rodovia}_{codigo_disciplina}_LT-{codigo_lote}"

def carregar_modelo(
    modelo: str,
    timeout: int = TIMEOUT_MODELO,
) -> dict[str, Any]:
    """
    Carrega um modelo no LM Studio usando a API REST.
    """

    headers = {
        "Authorization": f"Bearer {CHAVE_API}",
        "Content-Type": "application/json",
        }

    dados: dict[str, Any] = {
        "model": modelo,
        "context_length": CONTEXTO_MODELO,
        "echo_load_config": True,
    }

    resposta = requests.post(
        f"{URL_API_MODELOS}/load",
        headers=headers,
        json=dados,
        timeout=timeout,
    )

    resposta.raise_for_status()
    MODELOS_CARREGADOS.add(modelo)
    return resposta.json()

def descarregar_modelo(
    modelo: str,
    timeout: int = TIMEOUT_MODELO,
) -> dict[str, Any]:
    """
    Descarrega um modelo no LM Studio usando a API REST.
    """

    headers = {
        "Authorization": f"Bearer {CHAVE_API}",
        "Content-Type": "application/json",
        }

    dados = {
        "instance_id": modelo
        }

    resposta = requests.post(
        f"{URL_API_MODELOS}/unload",
        headers=headers,
        json=dados,
        timeout=timeout
    )

    resposta.raise_for_status()
    MODELOS_CARREGADOS.discard(modelo)
    return resposta.json()


def descarregar_modelos_carregados(modelos: list[str] | tuple[str, ...] | None = None) -> None:
    """Tenta descarregar os modelos conhecidos sem interromper o fechamento do app."""

    modelos_para_descarregar = tuple(dict.fromkeys(
        list(modelos or ()) + list(MODELOS_CARREGADOS) + list(MODELOS_CONHECIDOS)
    ))

    for modelo in modelos_para_descarregar:
        try:
            descarregar_modelo(modelo, timeout=10)
            print(f"Modelo descarregado: {modelo}")
        except Exception as erro:
            print(f"Nao foi possivel descarregar o modelo {modelo}: {erro}")
