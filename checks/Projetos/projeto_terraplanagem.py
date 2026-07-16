"""Verificação de conteúdo mínimo do projeto de terraplanagem."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Terraplanagem",
    codigo_saida="PTER",
    tipo_modelo="projeto",
    perguntas=[
        {"pergunta": "O mapa de localização da obra foi apresentado?", "informacao_adicional": ""},
        {"pergunta": "Foi apresentado o quadro resumo das composições e das quantidades de serviço?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta os cálculos dos volumes considerando o fator de homogeneização?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta os critérios adotados para a classificação dos materiais?", "informacao_adicional": ""},
        {"pergunta": "O documento possui apresentação do quadro de orientação de terraplenagem?", "informacao_adicional": ""},
        {"pergunta": "O documento possui planta de locação e distribuição de caixas de empréstimo?", "informacao_adicional": ""}
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o projeto de terraplanagem."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
