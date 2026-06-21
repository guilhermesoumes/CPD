"""Verificação de conteúdo mínimo do projeto de terraplanagem."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Terraplanagem",
    codigo_saida="PTER",
    tipo_modelo="projeto",
    perguntas=[
        "O mapa de localização da obra foi apresentado?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "Foi apresentado o quadro resumo das composições e das quantidades de serviço?",
        "O documento apresenta os cálculos dos volumes considerando o fator de homogeneização?",
        "O documento apresenta os critérios adotados para a classificação dos materiais?",
        "O documento possui apresentação do quadro de orientação de terraplenagem?",
        "O documento possui planta de locação e distribuição de caixas de empréstimo?",
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o projeto de terraplanagem."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
