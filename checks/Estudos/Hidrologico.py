# -*- coding: utf-8 -*-
from funcs.check_runner import CheckConfig, run_content_check


CONFIG = CheckConfig(
    discipline_name="Estudo Hidrológico",
    output_code="EHID",
    template_kind="estudo",
    questions=[
        "O documento apresenta mapa de localização ou situação da bacia estudada?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "O documento apresenta dados pluviométricos ou séries históricas utilizadas?",
        "O documento apresenta metodologia de cálculo de vazões ou tempos de recorrência?",
        "O documento apresenta resultados ou conclusões hidrológicas para o projeto?",
    ],
)


def main():
    run_content_check(CONFIG)
