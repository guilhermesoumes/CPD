"""Verificação de conteúdo mínimo do estudo de tráfego."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Estudo de Tráfego",
    codigo_saida="ETRF",
    tipo_modelo="estudo",
    perguntas=[
        "O documento apresenta delimitação das zonas de tráfego?",
        "O documento apresenta informações sobre coleta de dados existentes de tráfego?",
        "O documento apresenta pesquisas complementares?",
        "O documento apresenta determinação do tráfego atual e futuro?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?"
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o estudo de tráfego."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
