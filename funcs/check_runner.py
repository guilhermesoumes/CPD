from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

import funcs.common_functions as common
from funcs.rag_engine import answer_questions


@dataclass(frozen=True)
class CheckConfig:
    discipline_name: str
    output_code: str
    template_kind: str
    questions: list[str]
    predecessor_disciplines: list[str] | None = None


def _load_rap_summary(rap_path: str | None, disciplines: list[str] | None):
    if not rap_path or not Path(rap_path).exists() or not disciplines:
        return None, 0, 0, 0, 0, None

    table = pd.read_excel(rap_path, sheet_name="GERAL")
    table = table[table["DISCIPLINA"].isin(disciplines)]
    table = table[["DISCIPLINA", "CONDIÇÃO"]]
    table["STATUS"] = table["CONDIÇÃO"].apply(common.classificar_status)

    total = len(table)
    approved = list(table["CONDIÇÃO"]).count("Aprovado")
    approved_with_notes = list(table["CONDIÇÃO"]).count("Aprovado com Ressalva")
    rejected = list(table["CONDIÇÃO"]).count("Reprovado")
    percent = round(100 * (approved + approved_with_notes) / total, 1) if total else 0

    return table, approved, total, approved_with_notes, rejected, percent


def _answer_is_positive(answer: str) -> bool:
    matches = re.findall(r"\b(SIM|NÃO|NAO)\b", answer.upper())
    return bool(matches and matches[-1] == "SIM")


def _content_score(answers: list[str]) -> float:
    if not answers:
        return 0
    positive_answers = sum(1 for answer in answers if _answer_is_positive(answer))
    return round(100 * positive_answers / len(answers), 1)


def _result_directory(check_config: CheckConfig, app_config: dict) -> Path:
    result_root = Path(app_config["diretorio-resultados"])
    road_code = app_config["rodovia"].replace("/", "-")
    lot_code = app_config["lote"]
    return result_root / f"{road_code}_LT{lot_code}" / check_config.discipline_name


def _next_report_path(output_dir: Path, check_config: CheckConfig, app_config: dict) -> Path:
    road_code = app_config["rodovia"].replace("/", "-")
    lot_code = app_config["lote"]
    output_name = common.prox_versao(
        str(output_dir),
        str(datetime.now().year),
        road_code,
        check_config.output_code,
        lot_code,
    )
    return output_dir / f"{output_name}.pdf"


def _generate_report(check_config: CheckConfig, **report_data) -> None:
    if check_config.template_kind == "estudo":
        from checks.Templates.relatorio_estudo import generate_study_report

        generate_study_report(**report_data)
        return

    if check_config.template_kind == "projeto":
        from checks.Templates.relatorio_projeto import generate_project_report

        generate_project_report(**report_data)
        return

    raise ValueError(f"Tipo de template inválido: {check_config.template_kind}")


def run_content_check(check_config: CheckConfig) -> None:
    config_file = common.resource_path("config.json")
    app_config = common.load_config(config_file)

    pdf_files = app_config.get("arquivos-para-analisar") or []
    if not pdf_files:
        raise ValueError("Nenhum PDF foi selecionado para análise.")

    output_dir = _result_directory(check_config, app_config)
    common.ensure_output_dirs(str(output_dir))

    rap_table, rap_approved, rap_total, rap_with_notes, rap_rejected, rap_percent = _load_rap_summary(
        app_config.get("arquivo-rap"),
        check_config.predecessor_disciplines,
    )

    for pdf_file in pdf_files:
        answers = answer_questions(pdf_file, check_config.questions)
        content_score = _content_score(answers)
        score_values = [content_score]
        if rap_percent is not None:
            score_values.append(rap_percent)
        general_score = round(sum(score_values) / len(score_values), 1)

        _generate_report(
            check_config,
            pdf_path=str(_next_report_path(output_dir, check_config, app_config)),
            discipline_name=check_config.discipline_name,
            analyzed_report=Path(pdf_file).name,
            general_score=f"{general_score}%",
            questions=check_config.questions,
            answers=answers,
            rap_table=rap_table,
            rap_approved=rap_approved,
            rap_total=rap_total,
            rap_with_notes=rap_with_notes,
            rap_rejected=rap_rejected,
            rap_percent=rap_percent,
        )
