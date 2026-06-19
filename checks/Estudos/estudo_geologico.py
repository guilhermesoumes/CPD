# -*- coding: utf-8 -*-
from scripts.check_runner import CheckConfig, run_content_check


CHECK_CONFIG = CheckConfig(
    discipline_name="Estudo Geológico",
    output_code="EGEO",
    template_kind="estudo",
    questions=[
        "O documento apresenta a concepção do estudo realizado?",
        "O documento apresenta mapeamento geológico?",
        "O documento apresenta o plano de sondagem?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?"
    ],
)


def main() -> None:
    run_content_check(CHECK_CONFIG)
