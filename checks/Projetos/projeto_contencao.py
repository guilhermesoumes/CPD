# -*- coding: utf-8 -*-
from funcs.check_runner import CheckConfig, run_content_check


CHECK_CONFIG = CheckConfig(
    discipline_name="Contenção",
    output_code="PCTC",
    template_kind="projeto",
    predecessor_disciplines=["Estudo Geológico", "Estudo Geotécnico", "Projeto Geométrico"],
    questions=[
        "O documento apresenta informações sobre seção transversal tipo?",
        "O documento apresenta um Mapa de Situação?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "Há descrição quanto à localização da obra?",
        "O documento apresenta investigações geotécnicas que caracterizam o solo de fundação?",
        "O documento apresenta as coordenadas de localização da obra?",
        "Foi informada a agressividade do meio ambiente adotada para o projeto?",
    ],
)


def main() -> None:
    run_content_check(CHECK_CONFIG)
