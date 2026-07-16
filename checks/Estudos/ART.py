"""Verificação de conteúdo mínimo do estudo de tráfego."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo

CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Estudo de Tráfego",
    codigo_saida="ETRF",
    tipo_modelo="estudo",
    perguntas=[
        {"pergunta": "O documento apresenta Responável Técnico?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta Dados do Contrato?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta Dados da Obra/Serviço?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta dados de Atividade Técnica?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta Anotação de Responsabilidade Técnica (ART)?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta Anotação de Responsabilidade Técnica?", "informacao_adicional": ""},
        {"pergunta": "O documento possui Anotação de Responsabilidade Técnica?", "informacao_adicional": 
        '''Busque por informações como:
        1. Responsável técnico
        2. Dados do contrato
        3. Dados da Obra/Serviço
        4. Atividade Técnica'''}
    ],
)

def principal() -> None:
    """Executa a verificação configurada para o estudo de tráfego."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
    
