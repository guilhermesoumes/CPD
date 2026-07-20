# Guia do usuário

## Finalidade

O CPD-DNIT confere se um PDF apresenta itens mínimos de uma disciplina rodoviária. Ele não valida cálculos, dimensionamento, autenticidade documental ou conformidade normativa integral.

## Preparacao

1. Abra o LM Studio.
2. Confirme que o servidor esta ativo na porta `1234`.
3. Disponibilize os modelos exigidos no README.
4. Inicie `python app.py`.

O indicador no rodapé consulta `GET /v1/models` a cada 10 segundos. Verde indica que a API respondeu; isso não garante que todos os modelos estejam instalados.

## Campos

| Campo | Obrigatório | Uso |
|---|---:|---|
| Contrato | Não | Identificação e chave do histórico local |
| Processo | Sim | Metadado do RAC |
| Edital | Não | Metadado do RAC |
| Modalidade de contratação | Não | Metadado do RAC |
| Rodovia | Sim | Deve seguir `000/UF`; compoe pasta e nome do RAC |
| Segmento | Não | Metadado do RAC |
| Extensão | Sim | Metadado do RAC |
| Lote | Sim | Normalizado com dois dígitos quando numérico |
| Tipo de projeto | Não | Classificação apresentada no RAC |
| Fase | Sim | Define o catálogo Estudos ou Projetos |
| Número da análise | Sim | Metadado do RAC |
| Número do último relatório | Sim | Metadado do RAC; não controla o versionamento do arquivo |
| Analista | Sim | Metadado do RAC |

Ao sair do campo Contrato, Processo e Edital podem ser recuperados do histórico. Ao executar, o par atual é salvo ou atualizado.

## Arquivos e verificação

- A seleção aceita vários PDFs; um RAC é criado para cada PDF.
- **Estudos Preliminares** lista os arquivos de `checks/estudos`.
- **Projeto Básico** e **Projeto Executivo** usam o mesmo catálogo em `checks/projetos`.
- O nome exibido na lista é o nome do arquivo Python, não o nome amigável da disciplina.

## Durante a execução

O botão **Executar** muda para **Interromper**. Ao interromper, aguarde a chamada atual ao modelo terminar. Fechar a janela também sinaliza cancelamento e tenta descarregar os modelos conhecidos.

Não altere ou remova os PDFs de entrada enquanto o processamento estiver ativo. PDFs longos podem exigir bastante tempo porque cada página é renderizada e enviada ao OCR.

## Interpretacao do RAC

O relatório contém:

- metadados informados na interface;
- percentual de conformidade, calculado pela quantidade de respostas cuja conclusão contém `SIM`;
- pergunta, resposta, trecho comprobatório e página;
- tempo aproximado de processamento;
- identificação adicional de ART.

O percentual depende do formato textual devolvido pelo modelo. Evidências e páginas devem ser conferidas no documento original.

## Dados locais

No Windows, a interface grava preferências e histórico em:

```text
%USERPROFILE%\AppData\Local\CPD-DNIT\config.json
```

Interface, processamento e relatório usam o mesmo arquivo no perfil do usuário.

## Problemas comuns

| Sintoma | Acao |
|---|---|
| LM Studio desconectado | Inicie o servidor local e confirme a porta `1234` |
| Erro ao carregar modelo | Verifique o identificador exato e se o modelo esta instalado |
| Nenhum PDF selecionado | Selecione ao menos um arquivo antes de executar |
| BR invalida | Use três dígitos, barra e UF maiuscula, por exemplo `040/DF` |
| Nenhum texto útil extraído | Confira legibilidade, integridade e orientação das páginas |
| RAC não aparece | Confira o diretório configurado e a mensagem de erro exibida |
| Cancelamento demora | Aguarde a requisição de modelo em andamento terminar |
