"""Verificação de conteúdo mínimo do estudo geotécnico."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Estudo Geotécnico",
    codigo_saida="EGTC",
    tipo_modelo="estudo",
    perguntas=[
        {"pergunta": "O documento apresenta investigações geotécnicas e ensaios de laboratório?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta croqui de ocorrência de materiais?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta histórico do pavimento existente?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta dados de avaliação estrutural?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta investigações geotécnicas e ensaios de laboratório?", "informacao_adicional": ""}
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o estudo geotécnico."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
