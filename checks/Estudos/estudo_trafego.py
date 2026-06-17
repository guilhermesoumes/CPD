# -*- coding: utf-8 -*-
from funcs.check_runner import CheckConfig, run_content_check


CHECK_CONFIG = CheckConfig(
    discipline_name="Estudo de Tráfego",
    output_code="ETRF",
    template_kind="estudo",
    questions=[
        "O documento apresenta mapa de localização ou situação do trecho estudado?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "O documento apresenta contagens volumétricas ou dados de tráfego utilizados?",
        "O documento apresenta composição da frota ou classificação veicular?",
        "O documento apresenta projeções de tráfego ou VMD para o horizonte de projeto?",
    ],
)


def main() -> None:
    run_content_check(CHECK_CONFIG)
