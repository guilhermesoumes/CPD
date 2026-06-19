# -*- coding: utf-8 -*-
from scripts.check_runner import CheckConfig, run_content_check


CHECK_CONFIG = CheckConfig(
    discipline_name="Estudo de Tráfego",
    output_code="ETRF",
    template_kind="estudo",
    questions=[
        "O documento apresenta delimitação das zonas de tráfego?",
        "O documento apresenta informações sobre coleta de dados existentes de tráfego?",
        "O documento apresenta pesquisas complementares?",
        "O documento apresenta determinação do tráfego atual e futuro?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?"
    ],
)


def main() -> None:
    run_content_check(CHECK_CONFIG)
