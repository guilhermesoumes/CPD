"""Verificação de conteúdo mínimo do estudo de traçado."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo

# Dados da disciplina
CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Estudo de Traçado",
    codigo_saida="ETRC",
    tipo_modelo="estudo",
    perguntas=[
        {"pergunta": "O documento apresenta prancha com elementos geométricos?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta informações sobre seção transversal tipo?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta classificação da rodovia?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta quadro de características técnicas e operacionais?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta cadastro de interferências?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta justificativa do traçado adotado?", "informacao_adicional": ""}
            ])

# Importação dos dados da disciplina no verificador
def principal() -> None:
    """Executa a verificação configurada para o estudo de traçado."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
