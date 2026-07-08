"""Verificação de conteúdo mínimo do estudo de tráfego."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Estudo de Tráfego",
    codigo_saida="ETRF",
    tipo_modelo="estudo",
    perguntas=[
        {"pergunta": "O documento apresenta delimitação das zonas de tráfego?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta informações sobre coleta de dados existentes de tráfego?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta pesquisas complementares?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta determinação do tráfego atual e futuro?", "informacao_adicional": ""},
        {"pergunta": "O documento possui Anotação de Responsabilidade Técnica?", "informacao_adicional": '''A Anotação de Responsabilidade Técnica é um documento obrigatório no Brasil para registrar, junto ao CREA (Conselho Regional de Engenharia e Agronomia), a responsabilidade técnica de um profissional habilitado sobre uma obra ou serviço nas áreas de engenharia, agronomia, geologia, geografia e meteorologia.
        Conteúdo básico de uma ART:
        - Identificação do profissional: nome, número de registro no Crea, CPF.
        - Identificação do contratante: pessoa física ou jurídica, com dados completos.
        - Descrição da obra ou serviço: tipo, local, características e escopo.
        - Atividades técnicas: detalhamento das tarefas e responsabilidades assumidas.
        - Datas: início e término previstos.
        - Valor do contrato: quando aplicável.
        - Assinaturas: do profissional e, em alguns casos, do contratante.'''}
    ],
)


def principal() -> None:
    """Executa a verificação configurada para o estudo de tráfego."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
