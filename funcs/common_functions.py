from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from pathlib import Path


PROJECT_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))


def resource_path(relative_path: str) -> str:
    return str(PROJECT_ROOT / relative_path)


def load_config(config_file: str | Path) -> dict:
    path = Path(config_file)
    if path.exists():
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def get_info(config_file: str | Path, info: str):
    return load_config(config_file).get(info)


def ensure_output_dirs(folder: str | Path) -> None:
    Path(folder).mkdir(parents=True, exist_ok=True)


def normalize_text(value: str | None) -> str:
    text = "" if value is None else str(value)
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return without_accents.strip().lower()


def norm(value: str | None) -> str:
    return normalize_text(value)


def classificar_status(status_texto: str):
    status = normalize_text(status_texto)
    if "reprovado" in status:
        return ("-", "-", "✖")
    if "aprovado" in status and "ressalva" in status:
        return ("-", "⚠️", "-")
    if "aprovado" in status:
        return ("✔", "-", "-")
    return ("-", "-", "-")


def truefalse_to_vx(status_texto: bool | str):
    if status_texto is False:
        return "✖"
    if status_texto is True:
        return "✔"
    return status_texto


def exists_file_with_ext(directory: Path, extensions: tuple[str, ...]) -> bool:
    if not directory.exists():
        return False
    normalized_extensions = tuple(ext.lower() for ext in extensions)
    return any(file.is_file() and file.suffix.lower() in normalized_extensions for file in directory.iterdir())


def padronizar_lote(value: str) -> str:
    text = str(value).strip()
    match = re.match(r"^(\d+)([A-Za-z]?)$", text)
    if not match:
        return text
    number, letter = match.groups()
    return f"{number.zfill(2)}{letter.upper()}"


def next_report_name(output_dir: str | Path, year: str, road_code: str, discipline_code: str, lot_code: str) -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    pattern = re.compile(
        rf"RAC-(\d{{3}})-{year}_BR-{re.escape(road_code)}_{re.escape(discipline_code)}_LT-{re.escape(lot_code)}",
        re.IGNORECASE,
    )
    versions = [
        int(match.group(1))
        for file in output_path.iterdir()
        if file.is_file() and (match := pattern.match(file.name))
    ]
    next_version = max(versions) + 1 if versions else 1
    return f"RAC-{next_version:03d}-{year}_BR-{road_code}_{discipline_code}_LT-{lot_code}"


def prox_versao(dir_saida: str, ano, br: str, disciplina, lote: str) -> str:
    return next_report_name(dir_saida, str(ano), br, disciplina, lote)


def path_rap_excel(folder: str | Path) -> str:
    try:
        for file in Path(folder).iterdir():
            if file.is_file() and file.suffix.lower() == ".xlsx" and file.name.lower().startswith("rap"):
                return str(file)
    except FileNotFoundError:
        return ""
    return ""
