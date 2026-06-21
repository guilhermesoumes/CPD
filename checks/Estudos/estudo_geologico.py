"""Verificação de conteúdo mínimo do estudo geológico."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Estudo Geológico",
    codigo_saida="EGEO",
    tipo_modelo="estudo",
    perguntas=[
        "O documento apresenta a concepção do estudo realizado?",
        "O documento apresenta mapeamento geológico?",
        "O documento apresenta o plano de sondagem?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?"
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o estudo geológico."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
