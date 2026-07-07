"""Verificação de conteúdo mínimo do projeto de contenção."""
from scripts.executor_verificacoes import ConfiguracaoVerificacao, executar_verificacao_conteudo


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Contenção",
    codigo_saida="PCTC",
    tipo_modelo="projeto",
    perguntas=[
        {"pergunta": "O documento apresenta informações sobre seção transversal tipo?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta um Mapa de Situação?", "informacao_adicional": ""},
        {"pergunta": "Há descrição quanto à localização da obra?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta investigações geotécnicas que caracterizam o solo de fundação?", "informacao_adicional": ""},
        {"pergunta": "O documento apresenta as coordenadas de localização da obra?", "informacao_adicional": ""},
        {"pergunta": "Foi informada a agressividade do meio ambiente adotada para o projeto?", "informacao_adicional": ""},
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
    """Executa a verificação configurada para o projeto de contenção."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
