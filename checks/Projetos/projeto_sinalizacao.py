# -*- coding: utf-8 -*-
from funcs.check_runner import CheckConfig, run_content_check


CHECK_CONFIG = CheckConfig(
    discipline_name="Sinalização",
    output_code="PSIN",
    template_kind="projeto",
    predecessor_disciplines=["Estudo de Tráfego", "Projeto Geométrico", "Projeto de Pavimentação"],
    questions=[
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "O mapa de localização da obra foi apresentado?",
        "Foi apresentado o quadro resumo das composições e das quantidades de serviço?",
        "Há indicação dos segmentos homogêneos por estaqueamento e georreferenciamento?",
        "Há identificação de pontos notáveis, como rios, OAEs, locais de passagem de fauna etc.?",
    ],
)


def main() -> None:
    run_content_check(CHECK_CONFIG)
