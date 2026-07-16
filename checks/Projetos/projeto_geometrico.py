"""Verificação de conteúdo mínimo do projeto geométrico."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Geometria",
    codigo_saida="PGMT",
    tipo_modelo="projeto",
    perguntas=[
        {"pergunta": "O documento apresenta informações sobre seção transversal tipo?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta um Mapa de Situação?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta quadro de características técnicas e operacionais?", "informacao_adicional": ""},
        {"pergunta": "O projeto planimétrico, ou em planta, está na escala de 1:2000?", "informacao_adicional": ""}
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o projeto geométrico."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
