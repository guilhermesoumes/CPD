# -*- coding: utf-8 -*-
from funcs.check_runner import CheckConfig, run_content_check


CONFIG = CheckConfig(
    discipline_name="Terraplanagem",
    output_code="PTER",
    template_kind="projeto",
    predecessor_disciplines=["Estudo Topográfico", "Estudo de Traçado", "Estudo Geotécnico", "Projeto Geométrico"],
    questions=[
        "O mapa de localização da obra foi apresentado?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "Foi apresentado o quadro resumo das composições e das quantidades de serviço?",
        "O documento apresenta os cálculos dos volumes considerando o fator de homogeneização?",
        "O documento apresenta os critérios adotados para a classificação dos materiais?",
        "O documento possui apresentação do quadro de orientação de terraplenagem?",
        "O documento possui planta de locação e distribuição de caixas de empréstimo?",
    ],
)


def main():
    run_content_check(CONFIG)
