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
        {"pergunta": "Há identificação de pontos notáveis, como rios, OAEs, locais de passagem de fauna etc.?", "informacao_adicional": ""},
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
    """Executa a verificação configurada para o projeto de sinalização."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
