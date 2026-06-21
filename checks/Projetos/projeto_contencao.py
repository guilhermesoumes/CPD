"""Verificação de conteúdo mínimo do projeto de contenção."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Contenção",
    codigo_saida="PCTC",
    tipo_modelo="projeto",
    perguntas=[
        "O documento apresenta informações sobre seção transversal tipo?",
        "O documento apresenta um Mapa de Situação?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "Há descrição quanto à localização da obra?",
        "O documento apresenta investigações geotécnicas que caracterizam o solo de fundação?",
        "O documento apresenta as coordenadas de localização da obra?",
        "Foi informada a agressividade do meio ambiente adotada para o projeto?",
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o projeto de contenção."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
