"""Verificação de conteúdo mínimo do estudo geotécnico."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Estudo Geotécnico",
    codigo_saida="EGTC",
    tipo_modelo="estudo",
    perguntas=[
        "O documento apresenta investigações geotécnicas e ensaios de laboratório?",
        "O documento apresenta croqui de ocorrência de materiais?",
        "O documento apresenta histórico do pavimento existente?",
        "O documento apresenta dados de avaliação estrutural?",
        "O documento apresenta investigações geotécnicas e ensaios de laboratório?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?"
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o estudo geotécnico."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
