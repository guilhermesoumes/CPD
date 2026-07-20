# Revisão técnica

Revisão estática atualizada em 20 de julho de 2026. Não foram feitas chamadas reais aos modelos nem validação visual da interface ou do RAC.

## Correções aplicadas

- unificacao do arquivo de configuração usado por interface, executor e relatório;
- lista local de perguntas por PDF, sem mutação da configuração declarativa;
- remoção do check duplicado `checks/estudos/ART.py`;
- remoção do módulo de QR Code que não integrava o fluxo principal;
- inclusão do modelo visual de ART no ciclo de descarregamento;
- centralizacao de endpoints, modelos, chave, contexto e timeouts;
- contratos de tipo corrigidos para perguntas, respostas e páginas de ART;
- dependências diretas declaradas e testes unitários para funções puras.

## Achados pendentes

### Pontuação depende de parsing textual

O RAC interpreta a resposta do modelo por expressões regulares e considera `SIM` dentro do último item. Variacoes podem gerar resultado incorreto. O caminho mais robusto e exigir resposta estruturada e valida-la antes do relatório.

### Erros internos são mostrados ao usuário

A caixa de erro recebe traceback completo. Para distribuição, registre detalhes em arquivo de log e apresente uma mensagem operacional curta, com identificador do erro.

### Configuração técnica não é externa

Os parâmetros estão centralizados em `scripts/configuracao.py`, mas ainda exigem alteração de código. Variáveis de ambiente ou configuração validada permitiriam trocar porta e modelos sem nova compilação.

### Processamento depende integralmente do servidor local

Não há modo degradado quando um modelo esta ausente nem verificação inicial individual dos quatro modelos. O indicador confirma apenas que o endpoint `/v1/models` respondeu.

## Lacunas de qualidade

- a suíte cobre apenas contratos puros; o pipeline de IA não possui clientes simulados;
- nenhum pipeline de integração contínua, lint ou verificador de tipos;
- nenhum teste de contrato com a versão alvo do LM Studio;
- nenhuma política formal de logs, retenção ou limpeza de índices em falhas;
- nenhuma licença do projeto ou inventario formal de terceiros;
- nenhum limite de tamanho ou páginas e nenhum tratamento específico de PDF protegido;
- `CHANGELOG.md` possui entradas historicas com nomes da estrutura anterior.

## Ordem recomendada

1. estruturar a resposta do modelo e validar seu schema;
2. simular os clientes do LM Studio em testes de pipeline;
3. adicionar lint, tipos e integração contínua;
4. endurecer erros, logs e configuração externa;
5. executar aceitação com documentos representativos e revisão humana.
