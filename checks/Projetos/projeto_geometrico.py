"""Verificação de conteúdo mínimo do projeto geométrico."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Geometria",
    codigo_saida="PGMT",
    tipo_modelo="projeto",
    perguntas=[
        "O documento apresenta informações sobre seção transversal tipo?",
        "O documento apresenta um Mapa de Situação?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "O documento apresenta quadro de características técnicas e operacionais?",
        "O projeto planimétrico, ou em planta, está na escala de 1:2000?",
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o projeto geométrico."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
