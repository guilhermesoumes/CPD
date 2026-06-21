"""Verificação de conteúdo mínimo do projeto de pavimentação."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Pavimentação",
    codigo_saida="PPAV",
    tipo_modelo="projeto",
    perguntas=[
        "O mapa de localização da obra foi apresentado?",
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "Foi apresentado o quadro resumo das composições e das quantidades de serviço?",
        "O dimensionamento do pavimento foi feito pelo Método da Resistência, Método da Resiliência ou análises mecanísticas?",
        "Foi apresentado o nome e as características principais do software utilizado para o dimensionamento do pavimento?",
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o projeto de pavimentação."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
