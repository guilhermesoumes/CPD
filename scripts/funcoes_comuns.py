"""Funções compartilhadas de configuração, normalização e caminhos de saída."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


RAIZ_PROJETO = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))


def caminho_recurso(caminho_relativo: str) -> str:
    """Resolve um caminho relativo considerando também pacotes PyInstaller."""

    return str(RAIZ_PROJETO / caminho_relativo)


def carregar_configuracao(arquivo_configuracao: str | Path) -> dict:
    """Lê um arquivo JSON de configuração ou devolve um dicionário vazio."""

    caminho = Path(arquivo_configuracao)
    if caminho.exists():
        with caminho.open("r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    return {}


def garantir_diretorios_saida(pasta: str | Path) -> None:
    """Cria a árvore de diretórios de saída quando ela ainda não existe."""

    Path(pasta).mkdir(parents=True, exist_ok=True)


def padronizar_lote(valor: str) -> str:
    """Formata lotes numéricos com dois dígitos e sufixo opcional maiúsculo."""

    texto = str(valor).strip()
    correspondencia = re.match(r"^(\d+)([A-Za-z]?)$", texto)
    if not correspondencia:
        return texto
    numero, letra = correspondencia.groups()
    return f"{numero.zfill(2)}{letra.upper()}"


def proximo_nome_relatorio(diretorio_saida: str | Path, ano: str, codigo_rodovia: str, codigo_disciplina: str, codigo_lote: str) -> str:
    """Cria o nome do próximo RAC a partir das versões existentes no diretório."""

    caminho_saida = Path(diretorio_saida)
    caminho_saida.mkdir(parents=True, exist_ok=True)

    padrao = re.compile(
        rf"RAC-(\d{{3}})-{ano}_BR-{re.escape(codigo_rodovia)}_{re.escape(codigo_disciplina)}_LT-{re.escape(codigo_lote)}",
        re.IGNORECASE,
    )
    versoes = [
        int(correspondencia.group(1))
        for arquivo in caminho_saida.iterdir()
        if arquivo.is_file() and (correspondencia := padrao.match(arquivo.name))
    ]
    proxima_versao = max(versoes) + 1 if versoes else 1
    return f"RAC-{proxima_versao:03d}-{ano}_BR-{codigo_rodovia}_{codigo_disciplina}_LT-{codigo_lote}"
