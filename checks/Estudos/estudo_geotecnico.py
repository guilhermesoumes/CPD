# -*- coding: utf-8 -*-
from scripts.check_runner import CheckConfig, run_content_check


CHECK_CONFIG = CheckConfig(
    discipline_name="Estudo Geotécnico",
    output_code="EGTC",
    template_kind="estudo",
    questions=[
        "O documento apresenta investigações geotécnicas e ensaios de laboratório?",
        "O documento apresenta croqui de ocorrência de materiais?",
        "O documento apresenta histórico do pavimento existente?",
        "O documento apresenta dados de avaliação estrutural?",
        "O documento apresenta investigações geotécnicas e ensaios de laboratório?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?"
    ],
)


def main() -> None:
    run_content_check(CHECK_CONFIG)
