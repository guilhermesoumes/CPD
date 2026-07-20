# CPD-DNIT

Aplicação desktop para apoiar a avaliação de completude de relatórios técnicos de obras rodoviárias. O CPD-DNIT processa PDFs com modelos locais, recupera evidências por RAG e gera o Relatório da Avaliação de Completude (RAC) em PDF.

> A avaliação produzida por IA é apoio à conferência. A conclusão e a responsabilidade técnica permanecem humanas.

## Visão geral

O fluxo executado para cada PDF é:

1. renderização de todas as páginas a 200 DPI;
2. OCR visual com `glm-ocr`;
3. remoção de linhas repetidas e indexação no Chroma;
4. recuperação MMR das evidências para cada pergunta da disciplina;
5. resposta estruturada pelo modelo `google/gemma-3n-e4b`;
6. localização e classificação visual de páginas de ART com `google/gemma-4-e2b`;
7. geração e versionamento do RAC em PDF.

O processamento ocorre em uma thread para manter a interface responsiva. A interrupção é cooperativa: uma chamada ao modelo que já começou termina antes que o cancelamento seja observado.

## Requisitos

- Windows, ambiente principal de uso e empacotamento;
- Python 3.11 ou superior;
- LM Studio com servidor local ativo em `http://127.0.0.1:1234`;
- modelos locais `glm-ocr`, `text-embedding-qwen3-embedding-0.6b`, `google/gemma-3n-e4b` e `google/gemma-4-e2b`;
- memória e armazenamento proporcionais ao tamanho dos PDFs.

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

No LM Studio, habilite o servidor local e deixe disponíveis os quatro modelos listados acima. A aplicação usa a API compatível com OpenAI em `/v1` e os endpoints nativos de carga e descarga em `/api/v1/models/load` e `/unload`.

## Execução

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

Na interface:

1. informe os metadados do contrato e do projeto;
2. escolha um ou mais PDFs;
3. selecione o diretório de resultados;
4. escolha a fase e o módulo de verificação;
5. clique em **Executar**.

Os campos obrigatórios são Processo, Rodovia no formato `000/UF`, Extensão, Lote, Fase, Número da análise, Número do último relatório e Analista. O contrato pode ser reutilizado pelo histórico local de Processo e Edital.

## Saída

Cada entrada gera um RAC independente:

```text
<resultados>/<rodovia>_LT<lote>/<disciplina>/
RAC-<versao>-<ano>_BR-<rodovia>_<codigo>_LT-<lote>.pdf
```

Exemplo:

```text
resultados/345-DF_LT01/Geometria/RAC-001-2026_BR-345-DF_PGMT_LT-01.pdf
```

A versão é o maior número de RAC compatível já existente no diretório, acrescido de um. `vectorstores/` é temporário e pode ser recriado a cada execução.

## Documentação

- [Guia do usuário](docs/GUIA_DO_USUARIO.md): campos, operação, resultados e resolução de problemas.
- [Manual do usuário](docs/MANUAL_DO_USUARIO.md): referência completa para operação, funcionalidades e limitacoes.
- [Nota técnica](docs/NOTA_TECNICA.md): descrição técnica formal do sistema.
- [Arquitetura](docs/ARQUITETURA.md): componentes, fluxo de dados, persistencia e integrações.
- [Desenvolvimento](docs/DESENVOLVIMENTO.md): ambiente, convencoes, extensão, validação e empacotamento.
- [Catálogo de verificações](docs/VERIFICACOES.md): disciplinas, códigos e regras para novos módulos.
- [Revisão técnica](docs/REVISAO_TECNICA.md): achados, riscos conhecidos e lacunas de teste.
- [Histórico de alterações](CHANGELOG.md): registro cronológico existente.

## Estrutura

```text
CPDv4/
|-- app.py                     # interface e controle da execução
|-- checks/                    # declaracoes das verificacoes
|   |-- estudos/
|   `-- projetos/
|-- scripts/                   # OCR, RAG, ART e orquestração
|-- templates/relatorio_pdf.py # geração do RAC
|-- figs/                      # identidade visual
|-- vectorstores/              # indices temporarios, ignorados pelo Git
|-- docs/                      # documentação do projeto
|-- config.example.json
`-- requirements.txt
```

## Estado do projeto

O projeto possui uma suíte unitária inicial, mas ainda não dispõe de CI, licença nem configuração parametrizável para modelos e endpoints. Consulte a revisão técnica antes de distribuir ou usar em fluxo de produção.
