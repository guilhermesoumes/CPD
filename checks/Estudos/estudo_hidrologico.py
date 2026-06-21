"""Verificação de conteúdo mínimo do estudo hidrológico."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Estudo Hidrológico",
    codigo_saida="EHID",
    tipo_modelo="estudo",
    perguntas=[
        "O documento apresenta uma caracterização do local?",
        "O documento apresenta o levantamento das estações hidrometereológicas?",
        "O documento apresenta delimitações da bacias de projeto?",
        "O documento apresenta determinação da chuva/precipitação de projeto e intensidades de projeto?",
        "O documento apresenta cadastro das obras existentes?",
        "O documento apresenta determinação das vazões de projeto (quando houver pontes e bueiros)?",
        "O documento apresenta estudo hidráulico das Obras de Artes Especiais - OAEs (quando houver ponte)?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o estudo hidrológico."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
