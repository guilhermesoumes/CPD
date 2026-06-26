# CPD-DNIT — Avaliação de Completude com IA

Aplicação desktop em Python para apoiar a conferência de conteúdo mínimo em relatórios técnicos de obras rodoviárias. O sistema analisa PDFs por disciplina, recupera evidências com RAG, consulta modelos locais pelo LM Studio e gera o Relatório da Avaliação de Completude (RAC) em PDF.

## Funcionalidades

- Cadastro dos dados do processo, contrato, rodovia, lote, fase e analista.
- Seleção de um ou mais relatórios PDF por execução.
- Verificações específicas para estudos e projetos.
- Extração de texto, remoção de linhas repetidas e recuperação de contexto por MMR.
- Consulta a modelos locais por uma API compatível com a API da OpenAI.
- Geração automática do RAC, com controle incremental de versão.

## Requisitos

- Python 3.11 ou superior.
- LM Studio ou outro servidor compatível com a API da OpenAI.
- Modelo de conversa `google/gemma-3n-e4b`.
- Modelo de vetorização `text-embedding-qwen3-embedding-0.6b`.

Por padrão, a aplicação acessa a API em `http://127.0.0.1:1234/v1`. Modelos e endereço podem ser alterados nas constantes de `scripts/mecanismo_rag.py`.

## Instalação

No PowerShell, a partir da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Execução

1. Inicie o servidor local e carregue os dois modelos.
2. Ative o ambiente virtual.
3. Execute `python app.py`.
4. Preencha os campos obrigatórios.
5. Selecione os PDFs e o diretório de resultados.
6. Escolha a fase e a verificação e clique em **Executar**.

Os dados da última execução ficam em `config.json`. Esse arquivo é local e não deve ser versionado; `config.example.json` contém a estrutura de referência.

## Estrutura

```text
CPD3/
├── app.py
├── config.example.json
├── requirements.txt
├── README.md
├── figs/
│   ├── logo_icone.ico
│   └── logo_interface.jpeg
├── scripts/
│   ├── executor_verificacoes.py
│   ├── funcoes_comuns.py
│   └── mecanismo_rag.py
└── checks/
    ├── Estudos/
    │   ├── estudo_geologico.py
    │   ├── estudo_geotecnico.py
    │   ├── estudo_hidrologico.py
    │   ├── estudo_tracado.py
    │   └── estudo_trafego.py
    ├── Projetos/
    │   ├── projeto_contencao.py
    │   ├── projeto_geometrico.py
    │   ├── projeto_obras_complementares.py
    │   ├── projeto_pavimentacao.py
    │   ├── projeto_sinalizacao.py
    │   └── projeto_terraplanagem.py
    └── Templates/
        ├── relatorio_pdf.py
        └── fonts/
```

## Componentes

- `app.py`: interface, persistência da configuração, validação e carregamento dinâmico.
- `scripts/executor_verificacoes.py`: consulta o RAG, calcula indicadores e solicita o RAC.
- `scripts/mecanismo_rag.py`: extrai o PDF, cria a base vetorial e consulta os modelos.
- `scripts/funcoes_comuns.py`: caminhos, configuração, lote e versionamento.
- `checks/estudos` e `checks/projetos`: perguntas e metadados de cada disciplina.
- `templates/relatorio_pdf.py`: composição visual e geração do RAC.

## Como adicionar uma verificação

Crie um arquivo `.py` em `checks/Estudos` ou `checks/Projetos`:

```python
"""Verificação de conteúdo mínimo de uma disciplina."""

from scripts.executor_verificacoes import (
    ConfiguracaoVerificacao,
    executar_verificacao_conteudo,
)


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Nome da disciplina",
    codigo_saida="COD",
    tipo_modelo="projeto",  # ou "estudo"
    perguntas=["O documento apresenta o conteúdo esperado?"],
)


def principal() -> None:
    """Executa a verificação da disciplina."""

    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
```

A interface lista automaticamente os arquivos da pasta correspondente à fase escolhida.

## Saída

```text
<diretório-resultados>/<BR-UF>_LT<lote>/<disciplina>/RAC-<versão>-<ano>_BR-<BR-UF>_<código>_LT-<lote>.pdf
```

Exemplo:

```text
resultados/345-DF_LT01/Geometria/RAC-001-2026_BR-345-DF_PGMT_LT-01.pdf
```

O diretório `vectorstores/` é recriado durante a indexação e contém somente dados temporários.

## Empacotamento

```powershell
pyinstaller --onefile --noconsole app.py `
  --add-data "checks;checks" `
  --add-data "scripts;scripts" `
  --add-data "figs;figs"
```

## Observações

- A IA é uma ferramenta de apoio; a decisão técnica final continua sendo humana.
- Parâmetros exigidos por bibliotecas externas permanecem em inglês para preservar compatibilidade.
- `config.json`, `vectorstores/`, `__pycache__/` e arquivos `.pyc` são artefatos locais.
