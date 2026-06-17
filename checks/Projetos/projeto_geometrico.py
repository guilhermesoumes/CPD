# -*- coding: utf-8 -*-
from funcs.check_runner import CheckConfig, run_content_check


CHECK_CONFIG = CheckConfig(
    discipline_name="Geometria",
    output_code="PGMT",
    template_kind="projeto",
    predecessor_disciplines=["Estudo Topográfico", "Estudo de Tráfego", "Estudo de Traçado", "Estudo Geotécnico"],
    questions=[
        "O documento apresenta informações sobre seção transversal tipo?",
        "O documento apresenta um Mapa de Situação?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "O documento apresenta quadro de características técnicas e operacionais?",
        "O projeto planimétrico, ou em planta, está na escala de 1:2000?",
    ],
)


def main() -> None:
    run_content_check(CHECK_CONFIG)
