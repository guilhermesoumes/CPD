from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

import funcs.common_functions as fc
from funcs.rag_engine import answer_questions


@dataclass(frozen=True)
class CheckConfig:
    discipline_name: str
    output_code: str
    questions: list[str]
    template_kind: str
    predecessor_disciplines: list[str] | None = None


def _load_rap_table(rap_path: str | None, disciplines: list[str] | None):
    if not rap_path or not Path(rap_path).exists() or not disciplines:
        return None, 0, 0, 0, 0, None

    table = pd.read_excel(rap_path, sheet_name="GERAL")
    table = table[table["DISCIPLINA"].isin(disciplines)]
    table = table[["DISCIPLINA", "CONDIÇÃO"]]
    table["STATUS"] = table["CONDIÇÃO"].apply(fc.classificar_status)

    total = len(table)
    approved = list(table["CONDIÇÃO"]).count("Aprovado")
    approved_with_notes = list(table["CONDIÇÃO"]).count("Aprovado com Ressalva")
    rejected = list(table["CONDIÇÃO"]).count("Reprovado")
    percent = round(100 * (approved + approved_with_notes) / total, 1) if total else 0

    return table, approved, total, approved_with_notes, rejected, percent


def _content_percent(answers: list[str]) -> float:
    if not answers:
        return 0
    positives = sum(1 for answer in answers if "SIM" in answer.upper())
    return round(100 * positives / len(answers), 1)


def _output_dir(config: CheckConfig, app_config: dict) -> Path:
    root = Path(app_config["diretorio-resultados"])
    br = app_config["rodovia"].replace("/", "-")
    lote = app_config["lote"]
    return root / f"{br}_LT{lote}" / config.discipline_name


def run_content_check(config: CheckConfig) -> None:
    config_file = fc.resource_path("config.json")
    app_config = fc.load_config(config_file)

    pdf_files = app_config.get("arquivos-para-analisar") or []
    if not pdf_files:
        raise ValueError("Nenhum PDF foi selecionado para analise.")

    output_dir = _output_dir(config, app_config)
    fc.ensure_output_dirs(str(output_dir))

    rap_data = _load_rap_table(
        app_config.get("arquivo-rap"),
        config.predecessor_disciplines,
    )
    e1_tabela, e1_ap, e1_tot, e1_rs, e1_rp, e1_pct = rap_data

    if config.template_kind == "estudo":
        import checks.Templates.Template_pdf_estudo as template
    else:
        import checks.Templates.Template_pdf_projeto as template

    for pdf_file in pdf_files:
        answers = answer_questions(pdf_file, config.questions)
        content_pct = _content_percent(answers)
        conf_values = [content_pct]
        if e1_pct is not None:
            conf_values.append(e1_pct)
        conf_geral = round(sum(conf_values) / len(conf_values), 1)

        br = app_config["rodovia"].replace("/", "-")
        lote = app_config["lote"]
        output_name = fc.prox_versao(
            str(output_dir),
            str(datetime.now().year),
            br,
            config.output_code,
            lote,
        )

        template.gerar_pdf(
            pdf_path=str(output_dir / f"{output_name}.pdf"),
            disciplina=config.discipline_name,
            relatorio_de_analise=Path(pdf_file).name,
            conf_geral=f"{conf_geral}%",
            e1_tabela=e1_tabela,
            e1_ap=e1_ap,
            e1_tot=e1_tot,
            e1_rs=e1_rs,
            e1_rp=e1_rp,
            e1_pct=e1_pct,
            e3_perguntas=config.questions,
            e3_respostas=answers,
        )
