"""Verificação de conteúdo mínimo do projeto de obras complementares."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Obras Complementares",
    codigo_saida="POBC",
    tipo_modelo="projeto",
    perguntas=[
        {"pergunta": "O mapa de localização da obra foi apresentado?", "informacao_adicional": ""},
        {"pergunta": "Foi apresentado o quadro resumo das composições e das quantidades de serviço?", "informacao_adicional": ""},
        {"pergunta": "Foi apresentado o cadastro fotográfico contendo os elementos e dispositivos das obras complementares?", "informacao_adicional": ""}
    ],
)


def principal() -> None:
    """Executa a verificação configurada para obras complementares."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
