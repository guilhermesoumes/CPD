# CPD-DNIT - Avaliacao de Completude com IA

Aplicativo desktop em Python para apoiar a conferencia de conteudo minimo em relatorios tecnicos de entregas rodoviarias em BIM. A ferramenta recebe PDFs, aplica perguntas por disciplina usando RAG com modelo local exposto pelo LM Studio e gera relatorios PDF de avaliacao de completude.

## O que o sistema faz

- Permite cadastrar dados do processo, rodovia, lote, fase, analista e arquivos de entrada.
- Seleciona diretamente um ou mais relatorios PDF para analise.
- Executa verificacoes por disciplina a partir das pastas `checks/Estudos` e `checks/Projetos`.
- Usa RAG para procurar evidencias nos documentos e responder perguntas de conteudo minimo.
- Gera um RAC em PDF no diretorio de resultados, organizado por BR, lote e disciplina.
- Opcionalmente usa o arquivo RAP `.xlsx` para incluir a situacao de disciplinas antecessoras.

## Fluxo de uso

1. Inicie o LM Studio e exponha uma API local compativel com OpenAI em `http://127.0.0.1:1234/v1`.
2. Carregue no LM Studio:
   - modelo de chat: `google/gemma-3n-e4b`;
   - modelo de embedding: `text-embedding-qwen3-embedding-0.6b`.
3. Execute o aplicativo com `python app.py`.
4. Preencha os dados obrigatorios, selecione os PDFs e o diretorio de resultados.
5. Selecione a fase e a verificacao desejada.
6. Clique em `Executar`.

## Estrutura do projeto

```text
CPDv3/
|-- app.py
|-- config.example.json
|-- requirements.txt
|-- README.md
|-- CHANGELOG.md
|-- figs/
|   |-- icone.png
|   |-- logo_dnit_scan.ico
|   |-- logo_dnit_scan.jpeg
|   `-- logo_dnit_scan_v2.jpeg
|-- funcs/
|   |-- common_functions.py
|   |-- check_runner.py
|   `-- rag_engine.py
|-- checks/
|   |-- Estudos/
|   |   |-- Geologico.py
|   |   |-- Geotecnico.py
|   |   |-- Hidrologico.py
|   |   |-- Tracado.py
|   |   `-- Trafego.py
|   |-- Projetos/
|   |   |-- Contencao.py
|   |   |-- Geometrico.py
|   |   |-- Obras_complementares.py
|   |   |-- Pavimentacao.py
|   |   |-- Sinalizacao.py
|   |   `-- Terraplanagem.py
|   `-- Templates/
|       |-- Template_pdf_estudo.py
|       |-- Template_pdf_projeto.py
|       `-- fonts/
`-- teste_com_IA/
    `-- Perguntas_IA.py
```

## Componentes principais

- `app.py`: interface CustomTkinter, validacao de campos, persistencia de configuracao e execucao dos scripts.
- `funcs/rag_engine.py`: extrai texto dos PDFs, remove linhas repetidas, cria embeddings no Chroma e consulta o LLM.
- `funcs/check_runner.py`: executor comum das disciplinas. Le configuracoes, roda perguntas, calcula indicadores e chama o template de PDF.
- `funcs/common_functions.py`: funcoes utilitarias de caminhos, configuracao, status e versionamento de saida.
- `checks/*/*.py`: wrappers declarativos por disciplina. Cada arquivo define nome, codigo RAC, template e perguntas.
- `checks/Templates/*.py`: templates ReportLab para relatorios de estudo e projeto.

## Como adicionar uma nova verificacao

Crie um arquivo `.py` em `checks/Estudos` ou `checks/Projetos` seguindo o padrao:

```python
# -*- coding: utf-8 -*-
from funcs.check_runner import CheckConfig, run_content_check

CONFIG = CheckConfig(
    discipline_name="Nome da Disciplina",
    output_code="CODIGO",
    template_kind="projeto",  # ou "estudo"
    predecessor_disciplines=["Disciplina Antecessora"],
    questions=[
        "Pergunta objetiva sobre conteudo minimo?",
    ],
)


def main():
    run_content_check(CONFIG)
```

A interface carrega automaticamente arquivos `.py` dessas pastas conforme a fase selecionada.

## Instalacao

```powershell
cd C:\AmbienteDeTeste\CPDv3
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## Empacotamento com PyInstaller

```powershell
pyinstaller --onefile --noconsole app.py --add-data "checks;checks" --add-data "config.json;." --add-data "funcs;funcs" --add-data "figs;figs"
```

## Observacoes tecnicas

- O diretorio `vectorstores/` e temporario e foi incluido no `.gitignore`.
- `config.json` guarda dados locais da ultima execucao e nao deve ser versionado; use `config.example.json` como referencia.
- `__pycache__` e arquivos `.pyc` sao artefatos gerados e nao devem ser versionados.
- O RAP e opcional para a analise de conteudo; quando informado, entra como apoio na etapa de disciplinas antecessoras.
- A performance principal melhora porque o fluxo RAG fica centralizado e os scripts de disciplina deixam de recriar logica duplicada.


