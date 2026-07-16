"""Verificação de conteúdo mínimo do projeto de sinalização."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Sinalização",
    codigo_saida="PSIN",
    tipo_modelo="projeto",
    perguntas=[
        {"pergunta": "O mapa de localização da obra foi apresentado?", "informacao_adicional": ""},
        {"pergunta": "Foi apresentado o quadro resumo das composições e das quantidades de serviço?", "informacao_adicional": ""},
        {"pergunta": "Há indicação dos segmentos homogêneos por estaqueamento e georreferenciamento?", "informacao_adicional": ""},
        {"pergunta": "Há identificação de pontos notáveis, como rios, OAEs, locais de passagem de fauna etc.?", "informacao_adicional": ""}
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o projeto de sinalização."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
