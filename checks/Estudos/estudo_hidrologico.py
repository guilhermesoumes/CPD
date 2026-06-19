# -*- coding: utf-8 -*-
from scripts.check_runner import CheckConfig, run_content_check


CHECK_CONFIG = CheckConfig(
    discipline_name="Estudo Hidrológico",
    output_code="EHID",
    template_kind="estudo",
    questions=[
        "O documento apresenta uma caracterização do local?",
        "O documento apresenta o levantamento das estações hidrometereológicas?",
        "O documento apresenta delimitações da bacias de projeto?",
        "O documento apresenta determinação da chuva/precipitação de projeto e intensidades de projeto?",
        "O documento apresenta cadastro das obras existentes?",
        "O documento apresenta determinação das vazões de projeto (quando houver pontes e bueiros)?",
        "O documento apresenta estudo hidráulico das Obras de Artes Especiais - OAEs (quando houver ponte)?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
    ],
)


def main() -> None:
    run_content_check(CHECK_CONFIG)
