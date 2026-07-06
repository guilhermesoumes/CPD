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
        {"pergunta": "O documento apresenta justificativa do traçado adotado?", "informacao_adicional": ""},
        {"pergunta": "O documento possui Anotação de Responsabilidade Técnica (ART)?", "informacao_adicional": '''A Anotação de Responsabilidade Técnica é um documento obrigatório no Brasil para registrar, junto ao CREA (Conselho Regional de Engenharia e Agronomia), a responsabilidade técnica de um profissional habilitado sobre uma obra ou serviço nas áreas de engenharia, agronomia, geologia, geografia e meteorologia.
        Conteúdo básico de uma ART:
        - Identificação do profissional: nome, número de registro no Crea, CPF.
        - Identificação do contratante: pessoa física ou jurídica, com dados completos.
        - Descrição da obra ou serviço: tipo, local, características e escopo.
        - Atividades técnicas: detalhamento das tarefas e responsabilidades assumidas.
        - Datas: início e término previstos.
        - Valor do contrato: quando aplicável.
        - Assinaturas: do profissional e, em alguns casos, do contratante.'''}
            ])

# Importação dos dados da disciplina no verificador
def principal() -> None:
    """Executa a verificação configurada para o estudo de traçado."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
