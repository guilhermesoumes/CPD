# -*- coding: utf-8 -*-
from funcs.check_runner import CheckConfig, run_content_check


CHECK_CONFIG = CheckConfig(
    discipline_name="Estudo de Traçado",
    output_code="ETRC",
    template_kind="estudo",
    predecessor_disciplines=["Estudo Geológico", "Estudo Topográfico", "Estudo de Tráfego"],
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
