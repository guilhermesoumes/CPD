# Desenvolvimento

## Ambiente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

O código usa imports absolutos a partir da raiz. Execute comandos a partir de `CPDv4/`.

## Convencoes atuais

- nomes e interface em portugues;
- `pathlib.Path` para caminhos;
- checks declarativos com `ConfiguracaoVerificacao`;
- número de página humano, iniciado em 1;
- código de saída curto e estavel por disciplina;
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
- validação da rodovia e persistencia;
- recuperação e classificação visual de ART;
- isolamento da configuração em código-fonte e PyInstaller;
- repeticao da mesma verificação para vários PDFs.

## Empacotamento

Instale o PyInstaller separadamente e execute:

```powershell
pyinstaller --onefile --noconsole app.py `
  --add-data "checks;checks" `
  --add-data "scripts;scripts" `
  --add-data "figs;figs" `
  --add-data "templates;templates"
```

Valide o executável em uma máquina limpa. O pacote não inclui LM Studio nem os modelos. Configuração e histórico permanecem no diretório de dados do usuário.

## Dependências

`requirements.txt` registra as bibliotecas importadas diretamente. Valide mudancas sempre em um ambiente limpo, sem depender de pacotes transitivos.

## Entrega

Antes de publicar:

1. resolva ou aceite formalmente os itens de alta prioridade da revisão técnica;
2. atualize `CHANGELOG.md`;
3. execute as validações e o roteiro manual;
4. confirme licença, política de dados e licenças de terceiros;
5. teste os modelos e identificadores na versão alvo do LM Studio.
