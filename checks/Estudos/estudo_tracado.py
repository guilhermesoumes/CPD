# -*- coding: utf-8 -*-
from scripts.check_runner import CheckConfig, run_content_check


CHECK_CONFIG = CheckConfig(
    discipline_name="Estudo de Traçado",
    output_code="ETRC",
    template_kind="estudo",
    predecessor_disciplines=["Estudo Geológico", "Estudo Topográfico", "Estudo de Tráfego"],
    questions=[
        "O documento apresenta prancha com elementos geométricos?",
        "O documento apresenta informações sobre seção transversal tipo?",
        "O documento apresenta classificação da rodovia?",
        "O documento apresenta quadro de características técnicas e operacionais?",
        "O documento apresenta cadastro de interferências?",
        "O documento apresenta justificativa do traçado adotado?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?"
    ],
)


def main() -> None:
    run_content_check(CHECK_CONFIG)
