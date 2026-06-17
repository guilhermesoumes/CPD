# -*- coding: utf-8 -*-
from funcs.check_runner import CheckConfig, run_content_check


CONFIG = CheckConfig(
    discipline_name="Obras Complementares",
    output_code="POBC",
    template_kind="projeto",
    predecessor_disciplines=["Projeto Geométrico", "Projeto de Pavimentação"],
    questions=[
        "O mapa de localização da obra foi apresentado?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "Foi apresentado o quadro resumo das composições e das quantidades de serviço?",
        "Foi apresentado o cadastro fotográfico contendo os elementos e dispositivos das obras complementares?",
    ],
)


def main():
    run_content_check(CONFIG)
