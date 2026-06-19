# CPD-DNIT - Avaliacao de Completude com IA

Aplicativo desktop em Python para apoiar a conferencia de conteudo minimo em relatorios tecnicos de entregas rodoviarias em BIM. A ferramenta recebe PDFs, aplica perguntas por disciplina usando RAG com modelo local exposto pelo LM Studio e gera relatorios PDF de avaliacao de completude.

## O que o sistema faz

- Cadastra dados do processo, rodovia, lote, fase, analista e arquivos de entrada.
- Seleciona diretamente um ou mais relatorios PDF para analise.
- Executa verificacoes por disciplina a partir das pastas `checks/estudos` e `checks/projetos`.
- Usa RAG para procurar evidencias nos documentos e responder perguntas de conteudo minimo.
- Gera um RAC em PDF no diretorio de resultados, organizado por BR, lote e disciplina.
- Usa o arquivo RAP `.xlsx` de forma opcional para incluir a situacao de disciplinas antecessoras.

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
|   |-- logo_icone.ico
|   `-- logo_interface
|-- funcs/
|   |-- common_functions.py
|   |-- check_runner.py
|   `-- rag_engine.py
|-- checks/
|   |-- estudos/
|   |   |-- estudo_geologico.py
|   |   |-- estudo_geotecnico.py
|   |   |-- estudo_hidrologico.py
|   |   |-- estudo_tracado.py
|   |   `-- estudo_trafego.py
|   |-- projetos/
|   |   |-- projeto_contencao.py
|   |   |-- projeto_geometrico.py
|   |   |-- projeto_obras_complementares.py
|   |   |-- projeto_pavimentacao.py
|   |   |-- projeto_sinalizacao.py
|   |   `-- projeto_terraplanagem.py
|   `-- templates/
|       |-- pdf_report.py
|       |-- relatorio_estudo.py
|       |-- relatorio_projeto.py
|       `-- fonts/
`-- scripts/
    `-- perguntas_ia.py
```

## Componentes principais

- `app.py`: interface CustomTkinter, validacao de campos, persistencia de configuracao e execucao dinamica dos scripts.
- `funcs/rag_engine.py`: extrai texto dos PDFs, remove linhas repetidas, cria embeddings no Chroma e consulta o LLM.
- `funcs/check_runner.py`: executor comum das disciplinas. Le configuracoes, roda perguntas, calcula indicadores e chama o template de PDF.
- `funcs/common_functions.py`: funcoes utilitarias de caminhos, configuracao, status, padronizacao de lote e versionamento de saida.
- `checks/estudos/*.py`: verificacoes de estudos preliminares, sempre no padrao `estudo_nome_da_disciplina.py`.
- `checks/projetos/*.py`: verificacoes de projetos, sempre no padrao `projeto_nome_da_disciplina.py`.
- `checks/templates/pdf_report.py`: template central do RAC em PDF.
- `checks/templates/relatorio_estudo.py` e `checks/templates/relatorio_projeto.py`: wrappers pequenos que selecionam o tipo de relatorio.

## Padrao dos scripts de verificacao

Cada verificacao deve expor uma constante `CHECK_CONFIG` e uma funcao `main()`. A interface carrega automaticamente arquivos `.py` das pastas de verificacao conforme a fase selecionada.

```python
# -*- coding: utf-8 -*-
from scripts.check_runner import CheckConfig, run_content_check


CHECK_CONFIG = CheckConfig(
    discipline_name="Nome da Disciplina",
    output_code="CODIGO",
    template_kind="projeto",  # ou "estudo"
    predecessor_disciplines=["Disciplina Antecessora"],
    questions=[
        "Pergunta objetiva sobre conteudo minimo?",
    ],
)


def main() -> None:
    run_content_check(CHECK_CONFIG)
```

## Saida gerada

Os relatorios sao gravados em:

```text
<diretorio-resultados>/<BR-UF>_LT<lote>/<disciplina>/RAC-<versao>-<ano>_BR-<BR-UF>_<codigo>_LT-<lote>.pdf
```

Exemplo:

```text
Export_RAC/345-DF_LT01/Geometria/RAC-001-2026_BR-345-DF_PGMT_LT-01.pdf
```

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

- `config.json` guarda dados locais da ultima execucao e nao deve ser versionado; use `config.example.json` como referencia.
- `vectorstores/` e temporario e foi incluido no `.gitignore`.
- `__pycache__` e arquivos `.pyc` sao artefatos gerados e nao devem ser versionados.
- Os unicos assets de `figs/` usados pela aplicacao sao `logo_icone.ico` e `logo_interface`.
- O RAP e opcional para a analise de conteudo; quando informado, entra como apoio na etapa de disciplinas antecessoras.
- O fluxo de templates foi centralizado para evitar divergencia visual entre relatorios de estudo e projeto.
