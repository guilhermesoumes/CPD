# Manual do Usuário - CPD-DNIT

## 1. Apresentacao

O CPD-DNIT é um programa desktop de apoio à conferência de completude de relatórios técnicos rodoviários. Ele analisa arquivos PDF, procura evidências relacionadas aos itens de uma disciplina e produz um Relatório da Avaliação de Completude (RAC).

O programa utiliza Inteligência Artificial executada localmente. O resultado auxilia o trabalho do analista, mas não substitui leitura técnica, verificação normativa, validação de cálculos ou decisão profissional.

## 2. Funcionalidades

O programa permite:

- cadastrar dados do processo, contrato, rodovia, segmento, lote e analista;
- manter histórico local de Processo e Edital por contrato;
- selecionar um ou vários PDFs em uma execução;
- escolher verificações de Estudos Preliminares, Projeto Básico ou Projeto Executivo;
- transcrever páginas por OCR visual;
- localizar evidências para perguntas especificas de cada disciplina;
- identificar páginas com Anotação de Responsabilidade Técnica (ART);
- calcular um percentual indicativo de completude;
- gerar um RAC separado e versionado para cada PDF;
- interromper cooperativamente uma execução em andamento;
- indicar se o servidor local do LM Studio esta acessível.

O programa não realiza verificação de QR Code.

## 3. Requisitos para utilização

Antes de iniciar, confirme:

1. Python 3.11 ou superior instalado, caso use o código-fonte.
2. Dependências instaladas por `pip install -r requirements.txt`.
3. LM Studio aberto com o servidor local ativo na porta `1234`.
4. Modelos locais disponíveis:
   - `glm-ocr`;
   - `text-embedding-qwen3-embedding-0.6b`;
   - `google/gemma-3n-e4b`;
   - `google/gemma-4-e2b`.
5. PDFs legíveis e não protegidos contra abertura.
6. Espaco livre para arquivos temporários, índices vetoriais e RACs.

O indicador verde informa que o servidor respondeu. Ele não confirma, sozinho, que todos os modelos necessários estão instalados e funcionais.

## 4. Inicialização

No PowerShell, a partir da pasta do projeto:

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

A tela de abertura é exibida antes da janela principal. Os dados da utilização anterior são restaurados do perfil local do usuário.

## 5. Preenchimento dos campos

| Campo | Obrigatório | Orientação |
|---|---:|---|
| Contrato | Não | Identificação usada também para recuperar Processo e Edital |
| Processo | Sim | Número ou identificação administrativa do processo |
| Edital | Não | Identificação do edital relacionado |
| Modalidade de contratação | Não | Modalidade aplicável ao empreendimento |
| Rodovia | Sim | Formato obrigatório `000/UF`, por exemplo `040/DF` |
| Segmento | Não | Trecho analisado da rodovia |
| Extensão | Sim | Extensão do segmento ou projeto |
| Lote | Sim | Número ou identificação; valores numericos recebem dois dígitos |
| Tipo de projeto | Não | Duplicacao, Implantacao, Manutenção, Misto, OAE, Proarte, Reabilitacao ou Restauracao |
| Fase | Sim | Estudos Preliminares, Projeto Básico ou Projeto Executivo |
| Número da análise | Não | Referência administrativa exibida no RAC |
| Número do último relatório | Não | Referência exibida no RAC; não define a versão do arquivo |
| Analista | Sim | Nome do responsável pela conferência |

Campos obrigatórios sem preenchimento ficam destacados. A Rodovia deve conter três algarismos, barra e sigla da UF em letras maiúsculas.

## 6. Histórico de contratos

Ao informar um contrato já utilizado, o programa pode sugerir o valor salvo. Quando uma sugestao e selecionada, Processo e Edital associados são recuperados. Ao executar uma nova avaliação, os dados do contrato atual são incluidos ou atualizados no histórico.

O histórico fica somente no computador do usuário, no arquivo:

```text
%USERPROFILE%\AppData\Local\CPD-DNIT\config.json
```

Esse arquivo não possui criptografia. Evite armazenar informações sigilosas que não sejam necessárias ao relatório.

## 7. Seleção dos documentos

1. Use o controle de seleção de PDFs.
2. Escolha um ou vários arquivos.
3. Confira os nomes apresentados na interface.
4. Selecione a pasta de resultados.

Cada PDF e processado integralmente e gera seu próprio RAC. Não mova, renomeie ou exclua os documentos enquanto a avaliação estiver em andamento.

## 8. Escolha da verificação

### Estudos Preliminares

- Estudo Geológico;
- Estudo Geotécnico;
- Estudo Hidrológico;
- Estudo de Traçado;
- Estudo de Tráfego.

### Projeto Básico e Projeto Executivo

- Contenção;
- Geometria;
- Obras Complementares;
- Pavimentação;
- Sinalização;
- Terraplanagem.

Projeto Básico e Projeto Executivo usam o mesmo conjunto de perguntas. A fase escolhida é registrada nos metadados do RAC.

A verificação de ART é automática e ocorre em conjunto com qualquer disciplina; ela não aparece como opção separada.

## 9. Execução e interrupção

Clique em **Executar** depois de preencher os campos e selecionar a verificação. O botão muda para **Interromper**, e uma barra indica atividade.

O processamento inclui OCR de todas as páginas, indexação, perguntas da disciplina, verificação visual de ART e geração do RAC. O tempo depende principalmente de quantidade de páginas, resolução, hardware e velocidade dos modelos.

Ao clicar em **Interromper**, o programa sinaliza o cancelamento. Uma requisição que já foi enviada ao modelo não e encerrada imediatamente; a parada acontece no próximo ponto de controle. Fechar a janela também solicita interrupção e tenta descarregar os modelos.

## 10. Resultado gerado

Os RACs seguem esta estrutura:

```text
<pasta escolhida>/<rodovia>_LT<lote>/<disciplina>/
RAC-<versao>-<ano>_BR-<rodovia>_<codigo>_LT-<lote>.pdf
```

O programa procura os RACs existentes da mesma disciplina, rodovia, lote e ano. A próxima versão é o maior número encontrado acrescido de um.

O RAC apresenta:

- dados informados na interface;
- documento analisado e disciplina;
- tempo aproximado de processamento;
- perguntas verificadas;
- indicacao Sim ou Não;
- trechos recuperados e páginas citadas;
- item adicional referente a ART;
- percentual geral de completude;
- aviso de responsabilidade humana.

## 11. Interpretacao correta

O percentual é calculado pela proporção de respostas cuja conclusão foi interpretada como `SIM`. Ele representa presença aparente de conteúdo, não qualidade técnica.

Antes de utilizar o RAC em uma decisão:

1. abra o PDF original;
2. confira cada página citada;
3. verifique se o trecho responde realmente ao requisito;
4. avalie normas, escopo contratual e critérios técnicos aplicáveis;
5. registre correções humanas quando a IA estiver equivocada.

## 12. Limitacoes

- A IA pode produzir falsos positivos, falsos negativos ou páginas incorretas.
- OCR perde qualidade em digitalizações ruins, páginas giradas, tabelas densas e textos pequenos.
- Linhas repetidas mais de três vezes podem ser descartadas como cabeçalho ou rodapé.
- A recuperação usa apenas uma parte do conteúdo considerado mais relevante.
- O formato textual da resposta influencia o percentual e a montagem da tabela.
- A ART é localizada primeiro por busca semântica; páginas não recuperadas podem deixar de ser classificadas.
- Não há validação de assinatura, autenticidade, registro profissional ou QR Code.
- Não há conferência de memória de cálculo, dimensionamento ou aderencia normativa completa.
- PDFs protegidos, corrompidos ou muito extensos podem falhar ou consumir muitos recursos.
- A operação depende do LM Studio e dos quatro modelos configurados.
- Chamadas de modelo em andamento não possuem cancelamento instantaneo.
- O programa não possui mecanismo de revisão humana embutido no RAC.

## 13. Solução de problemas

| Situação | Procedimento sugerido |
|---|---|
| LM Studio desconectado | Inicie o servidor e confirme `http://127.0.0.1:1234/v1` |
| Modelo não encontrado | Confira o identificador e a disponibilidade no LM Studio |
| Campo Rodovia invalido | Use o formato `000/UF`, com UF maiuscula |
| Nenhum texto útil extraído | Verifique legibilidade, integridade e orientação do PDF |
| Resultado sem evidências | Confira manualmente o documento e a adequação da disciplina |
| RAC não gerado | Leia a mensagem de erro e confira a pasta de destino |
| Execução muito demorada | Aguarde a página ou chamada atual; use PDFs menores para diagnóstico |
| Interrupção demora | Espere a requisição atual ao modelo finalizar |

## 14. Boas práticas

- Trabalhe com copias dos PDFs originais.
- Comece com um documento curto para validar o ambiente.
- Mantenha os identificadores dos modelos estaveis.
- Revise todos os RACs antes de distribuir.
- Preserve documento original, RAC e configuração usada na avaliação.
- Não trate o percentual como aprovação automática.

## 15. Suporte técnico

Ao relatar um problema, informe a etapa em que ocorreu, disciplina, quantidade de páginas, mensagem apresentada, versão do Python, versão do LM Studio e modelos utilizados. Não envie documentos sigilosos sem autorização.
