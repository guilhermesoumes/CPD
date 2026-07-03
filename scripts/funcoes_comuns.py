"""Funções compartilhadas de configuração, normalização e caminhos de saída."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from urllib.parse import urlparse
import requests

import subprocess

from typing import Any

RAIZ_PROJETO = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))

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
        ) -> dict[str, Any]:
    """
    Carrega um modelo no LM Studio usando a API REST.
    """

    headers = {
        "Authorization": "Bearer lm-studio",
        "Content-Type": "application/json",
        }

    dados: dict[str, Any] = {
        "model": modelo,
        "context_length": 20000,
        "echo_load_config": True,
    }

    resposta = requests.post(
        f"http://127.0.0.1:1234/api/v1/models/load",
        headers=headers,
        json=dados,
        timeout=300
    )

    resposta.raise_for_status()
    return resposta.json()

def descarregar_modelo(
        modelo: str
        ) -> dict[str, Any]:
    """
    Descarrega um modelo no LM Studio usando a API REST.
    """

    headers = {
        "Authorization": "Bearer lm-studio",
        "Content-Type": "application/json",
        }

    dados = {
        "instance_id": modelo
        }

    resposta = requests.post(
        f"http://127.0.0.1:1234/api/v1/models/unload",
        headers=headers,
        json=dados,
        timeout=300
    )

    resposta.raise_for_status()
    return resposta.json()