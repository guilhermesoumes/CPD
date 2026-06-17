# -*- coding: utf-8 -*-
from funcs.check_runner import CheckConfig, run_content_check


CHECK_CONFIG = CheckConfig(
    discipline_name="Estudo Geotécnico",
    output_code="EGTC",
    template_kind="estudo",
    questions=[
        "O documento apresenta mapa de localização ou situação da área estudada?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "O documento apresenta plano ou descrição das investigações geotécnicas?",
        "O documento apresenta resultados de sondagens, ensaios ou caracterização de solos?",
        "O documento apresenta conclusões ou recomendações geotécnicas para o projeto?",
    ],
)


def main() -> None:
    run_content_check(CHECK_CONFIG)
