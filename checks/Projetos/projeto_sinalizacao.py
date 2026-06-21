"""Verificação de conteúdo mínimo do projeto de sinalização."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Sinalização",
    codigo_saida="PSIN",
    tipo_modelo="projeto",
    perguntas=[
        "O documento possui Anotação de Responsabilidade Técnica (ART)?",
        "O mapa de localização da obra foi apresentado?",
        "Foi apresentado o quadro resumo das composições e das quantidades de serviço?",
        "Há indicação dos segmentos homogêneos por estaqueamento e georreferenciamento?",
        "Há identificação de pontos notáveis, como rios, OAEs, locais de passagem de fauna etc.?",
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o projeto de sinalização."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
