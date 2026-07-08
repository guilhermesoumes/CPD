# CPD-DNIT - Avaliacao de Completude com IA

Aplicacao desktop em Python para apoiar a conferencia de conteudo minimo em relatorios tecnicos de obras rodoviarias. O sistema analisa PDFs por disciplina, extrai texto com OCR via modelo local, recupera evidencias com RAG, consulta modelos locais pelo LM Studio e gera o Relatorio da Avaliacao de Completude (RAC) em PDF.

## Situacao atual

- Interface desktop em `customtkinter`, com persistencia local em `config.json`.
- Execucao em segundo plano para manter a interface responsiva.
- Botao unico de execucao: **Executar** inicia a verificacao e muda para **Interromper** durante o processamento.
- Interrupcao cooperativa do RAG entre paginas do OCR, criacao do vectorstore, perguntas e PDFs.
- Identificacao de QR Code nas paginas citadas como evidencias da pergunta de ART.
- Descarregamento dos modelos conhecidos ao final das consultas e ao fechar a aplicacao.
- `vectorstores/` e recriado durante a indexacao e tratado como artefato temporario.
- Verificacoes disponiveis para estudos preliminares e projetos basico/executivo.

## Funcionalidades

- Cadastro dos dados do processo, contrato, rodovia, lote, fase e analista.
- Selecao de um ou mais relatorios PDF por execucao.
- Verificacoes especificas por disciplina.
- OCR por pagina usando o modelo `glm-ocr`.
- Verificacao de QR Code nas paginas onde a ART foi localizada.
- Extracao, filtragem de linhas repetidas e recuperacao de contexto por MMR.
- Consulta a modelos locais por API compativel com a API da OpenAI.
- Geracao automatica do RAC, com controle incremental de versao.
- Cancelamento da execucao em andamento pelo proprio botao de acao.

## Requisitos

- Python 3.11 ou superior.
- LM Studio ou outro servidor local compativel com a API da OpenAI.
- Modelo OCR `glm-ocr`.
- Modelo de conversa `google/gemma-3n-e4b`.
- Modelo de vetorizacao `text-embedding-qwen3-embedding-0.6b`.
- OpenCV e NumPy para deteccao de QR Code em paginas renderizadas do PDF.

Por padrao, a aplicacao acessa a API em `http://127.0.0.1:1234/v1` e usa endpoints do LM Studio em `http://127.0.0.1:1234/api/v1/models/load` e `/unload`. Modelos e endereco podem ser ajustados nas constantes de `scripts/mecanismo_rag.py`, `scripts/extracao_texto_pdf.py` e `scripts/funcoes_comuns.py`.

## Instalacao

No PowerShell, a partir da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Execucao

1. Inicie o servidor local do LM Studio.
2. Ative o ambiente virtual.
3. Execute `python app.py`.
4. Preencha os campos obrigatorios.
5. Selecione os PDFs e o diretorio de resultados.
6. Escolha a fase e a verificacao.
7. Clique em **Executar**.

Durante a analise, o botao muda para **Interromper**. A parada acontece assim que a chamada atual ao modelo termina e o fluxo alcanca o proximo ponto de verificacao. Ao fechar o programa, a aplicacao tenta descarregar `glm-ocr`, `text-embedding-qwen3-embedding-0.6b` e `google/gemma-3n-e4b`.

## Estrutura

```text
CPDv4/
|-- app.py
|-- config.example.json
|-- requirements.txt
|-- README.md
|-- CHANGELOG.md
|-- figs/
|   |-- logo_icone.ico
|   `-- logo_interface.jpeg
|-- scripts/
|   |-- executor_verificacoes.py
|   |-- extracao_texto_pdf.py
|   |-- funcoes_comuns.py
|   `-- mecanismo_rag.py
|-- checks/
|   |-- estudos/
|   |   |-- estudo_geologico.py
|   |   |-- estudo_geotecnico.py
|   |   |-- estudo_hidrologico.py
|   |   |-- estudo_tracado.py
|   |   `-- estudo_trafego.py
|   `-- projetos/
|       |-- projeto_contencao.py
|       |-- projeto_geometrico.py
|       |-- projeto_obras_complementares.py
|       |-- projeto_pavimentacao.py
|       |-- projeto_sinalizacao.py
|       `-- projeto_terraplanagem.py
|-- templates/
|   |-- relatorio_pdf.py
|   `-- fonts/
`-- vectorstores/
```

## Componentes

- `app.py`: interface, persistencia da configuracao, validacao, controle de execucao/interrupcao e fechamento.
- `scripts/executor_verificacoes.py`: orquestra a analise dos PDFs, chama o RAG e solicita a geracao do RAC.
- `scripts/extracao_texto_pdf.py`: converte paginas do PDF em imagens temporarias, aplica OCR e monta documentos para indexacao.
- `scripts/mecanismo_rag.py`: cria a base vetorial Chroma, recupera contexto e consulta o modelo de conversa.
- `scripts/funcoes_comuns.py`: caminhos, configuracao, padronizacao de lote, versionamento e carga/descarga de modelos.
- `checks/estudos` e `checks/projetos`: metadados e perguntas de cada disciplina.
- `templates/relatorio_pdf.py`: composicao visual e geracao do RAC.

## Como adicionar uma verificacao

Crie um arquivo `.py` em `checks/estudos` ou `checks/projetos`:

```python
"""Verificacao de conteudo minimo de uma disciplina."""

from scripts.executor_verificacoes import (
    ConfiguracaoVerificacao,
    executar_verificacao_conteudo,
)


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Nome da disciplina",
    codigo_saida="COD",
    tipo_modelo="projeto",  # ou "estudo"
    perguntas=[
        {
            "pergunta": "O documento apresenta o conteudo esperado?",
            "informacao_adicional": "",
        }
    ],
)


def principal() -> None:
    """Executa a verificacao da disciplina."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
```

A interface lista automaticamente os arquivos da pasta correspondente a fase escolhida.

## Saida

```text
<diretorio-resultados>/<BR-UF>_LT<lote>/<disciplina>/RAC-<versao>-<ano>_BR-<BR-UF>_<codigo>_LT-<lote>.pdf
```

Exemplo:

```text
resultados/345-DF_LT01/Geometria/RAC-001-2026_BR-345-DF_PGMT_LT-01.pdf
```

## Empacotamento

```powershell
pyinstaller --onefile --noconsole app.py `
  --add-data "checks;checks" `
  --add-data "scripts;scripts" `
  --add-data "figs;figs" `
  --add-data "templates;templates"
```

## Observacoes

- A IA e uma ferramenta de apoio; a decisao tecnica final continua sendo humana.
- Chamadas ja em andamento ao LM Studio nao sao abortadas instantaneamente; a interrupcao ocorre no proximo ponto cooperativo do fluxo.
- `config.json`, `vectorstores/`, `__pycache__/` e arquivos `.pyc` sao artefatos locais e nao devem ser versionados.
