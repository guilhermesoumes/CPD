# -*- coding: utf-8 -*-
from funcs.check_runner import CheckConfig, run_content_check


CONFIG = CheckConfig(
    discipline_name="Estudo Geológico",
    output_code="EGLG",
    template_kind="estudo",
    questions=[
        "O documento apresenta mapa de localização ou situação da área estudada?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "O documento apresenta caracterização geológica da área de estudo?",
        "O documento apresenta identificação de unidades geológicas ou litologias?",
        "O documento apresenta conclusões ou recomendações geológicas para o projeto?",
    ],
)


def main():
    run_content_check(CONFIG)
