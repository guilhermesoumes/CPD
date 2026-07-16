"""Verificação de conteúdo mínimo do projeto de contenção."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Contenção",
    codigo_saida="PCTC",
    tipo_modelo="projeto",
    perguntas=[
        {"pergunta": "O documento apresenta informações sobre seção transversal tipo?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta um Mapa de Situação?", "informacao_adicional": ""},
        {"pergunta": "Há descrição quanto à localização da obra?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta investigações geotécnicas que caracterizam o solo de fundação?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta as coordenadas de localização da obra?", "informacao_adicional": ""},
        {"pergunta": "Foi informada a agressividade do meio ambiente adotada para o projeto?", "informacao_adicional": ""}
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o projeto de contenção."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
