# -*- coding: utf-8 -*-
from funcs.check_runner import CheckConfig, run_content_check


CONFIG = CheckConfig(
    discipline_name="Pavimentação",
    output_code="PPAV",
    template_kind="projeto",
    predecessor_disciplines=["Estudo de Tráfego", "Estudo Geotécnico", "Projeto Geométrico", "Projeto Terraplenagem"],
    questions=[
        "O mapa de localização da obra foi apresentado?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "Foi apresentado o quadro resumo das composições e das quantidades de serviço?",
        "O dimensionamento do pavimento foi feito pelo Método da Resistência, Método da Resiliência ou análises mecanísticas?",
        "Foi apresentado o nome e as características principais do software utilizado para o dimensionamento do pavimento?",
    ],
)


def main():
    run_content_check(CONFIG)
