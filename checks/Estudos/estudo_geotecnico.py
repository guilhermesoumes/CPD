"""Verificação de conteúdo mínimo do estudo geotécnico."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Estudo Geotécnico",
    codigo_saida="EGTC",
    tipo_modelo="estudo",
    perguntas=[
        {"pergunta": "O documento apresenta investigações geotécnicas e ensaios de laboratório?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta croqui de ocorrência de materiais?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta histórico do pavimento existente?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta dados de avaliação estrutural?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta investigações geotécnicas e ensaios de laboratório?", "informacao_adicional": ""},
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
    """Executa a verificação configurada para o estudo geotécnico."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
