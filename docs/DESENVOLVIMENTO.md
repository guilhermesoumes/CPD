# Desenvolvimento

## Ambiente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

O código usa imports absolutos a partir da raiz. Execute comandos a partir da pasta raiz do projeto.

## Convenções atuais

- nomes e interface em português;
- `pathlib.Path` para caminhos;
- checks declarativos com `ConfiguracaoVerificacao`;
- número de página iniciado em 1;
- código de saída curto e estável por disciplina;
- cancelamento por `ProcessamentoInterrompido`;
- recursos empacotados resolvidos por `sys._MEIPASS`.

## Adicionar uma verificação

Crie um arquivo em `checks/estudos` ou `checks/projetos`:

```python
"""Verificação de conteúdo mínimo da disciplina."""

from scripts.executor_verificacoes import (
    ConfiguracaoVerificacao,
    executar_verificacao_conteudo,
)


CONFIGURACAO_VERIFICACAO = ConfiguracaoVerificacao(
    nome_disciplina="Nome da disciplina",
    codigo_saida="COD",
    tipo_modelo="projeto",  # "estudo" ou "projeto"
    perguntas=[
        {
            "pergunta": "O documento apresenta o item esperado?",
            "informacao_adicional": "Criterios ou sinonimos relevantes.",
        },
    ],
)


def principal() -> None:
    executar_verificacao_conteudo(CONFIGURACAO_VERIFICACAO)
```

O nome do arquivo aparece automaticamente na interface. O executor adiciona a pergunta de ART automaticamente; não crie um check separado para essa finalidade.

## Regras para perguntas

- Use uma pergunta objetiva por requisito.
- Coloque sinônimos e critérios em `informacao_adicional`.
- Não solicite conhecimento externo: o prompt limita a resposta ao contexto recuperado.
- Preserve o formato de dicionário com as duas chaves.
- Não inclua a pergunta de ART; ela é acrescentada pelo executor.

## Validação

Não há testes automatizados. Antes de uma entrega, execute no mínimo:

```powershell
python -m compileall -q app.py scripts checks templates
python -m pip check
```

O teste manual deve cobrir: inicialização sem LM Studio, status conectado, validação de campos, um PDF curto, vários PDFs, interrupção durante OCR e perguntas, incremento de versão, abertura do RAC e fechamento com processamento ativo.

Casos recomendados para futuros testes unitários:

- `padronizar_lote` e `proximo_nome_relatorio`;
- parsing das respostas e cálculo de pontuação;
- filtragem de OCR e metadados de página;
- validação da rodovia;
- recuperação e classificação visual de ART;
- repetição da mesma verificação para vários PDFs.

## Empacotamento

Instale o PyInstaller separadamente e execute:

```powershell
.\.venv\Scripts\pyinstaller.exe --clean --noconfirm CPD-DNIT.spec
```

Este arquivo descreve como transformar um projeto Python em um executável, incluindo arquivos, bibliotecas, ícone e configurações.

Há também outra opção utilizando diretamente o Pyinstaller, porém esta forma apresentou erros por não importar as bibliotecas 'chromadb.api.rust', 'chromadb_rust_bindings' e 'chromadb.telemetry.product.posthog' no arquivo executável, necessárias para o correto funcionamento do programa:

```powershell
pyinstaller --onefile --noconsole app.py `
  --name "CPD-DNIT" `
  --icon "figs\logo_icone.ico" `
  --add-data "checks;checks" `
  --add-data "scripts;scripts" `
  --add-data "figs;figs" `
  --add-data "templates;templates"
```

Valide o executável em uma máquina limpa. O pacote não inclui LM Studio nem os modelos. Configuração e histórico permanecem no diretório de dados do usuário.

## Dependências

`requirements.txt` registra as bibliotecas importadas diretamente. Valide mudancas sempre em um ambiente limpo, sem depender de pacotes transitivos.
