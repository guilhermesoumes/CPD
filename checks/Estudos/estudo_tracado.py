"""Verificação de conteúdo mínimo do estudo de traçado."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Estudo de Traçado",
    codigo_saida="ETRC",
    tipo_modelo="estudo",
    perguntas=[
        "O documento apresenta prancha com elementos geométricos?",
        "O documento apresenta informações sobre seção transversal tipo?",
        "O documento apresenta classificação da rodovia?",
        "O documento apresenta quadro de características técnicas e operacionais?",
        "O documento apresenta cadastro de interferências?",
        "O documento apresenta justificativa do traçado adotado?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?"
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o estudo de traçado."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
