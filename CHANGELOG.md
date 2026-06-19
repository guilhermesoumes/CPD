# Changelog

## 2026-06-17

### Reorganizacao inicial

- Inicializado repositorio Git em `C:\AmbienteDeTeste\CPDv3`.
- Criado `funcs/rag_engine.py` para centralizar extracao de PDF, limpeza de texto, criacao de embeddings, recuperacao e consulta ao LLM.
- Criado `funcs/check_runner.py` para padronizar execucao das verificacoes, calculo de conformidade e geracao dos RACs.
- Substituidos scripts longos de `checks/estudos` e `checks/projetos` por wrappers declarativos com `CheckConfig`.
- Mantido `scripts/perguntas_ia.py` como wrapper de compatibilidade para chamadas antigas.
- Corrigido versionamento de nomes em `funcs/common_functions.py` para considerar o codigo real da disciplina.
- Atualizado `requirements.txt` para conter apenas dependencias usadas pelo projeto reorganizado.
- Atualizado `.gitignore` para ignorar `*.pyc`, `vectorstores/` e `config.json`.
- Ajustado `Template_pdf_projeto.py` para aceitar a etapa de relacao de documentos gerais como opcional.
- Criado `config.example.json` sem caminhos locais para documentar a estrutura esperada de configuracao.

### Validacao e limpeza

- Removidos `__pycache__` e arquivos `.pyc` gerados.
- Rodada verificacao de sintaxe com `python -m py_compile` em todos os scripts Python.
- Preparado commit inicial apos validacao.

## 2026-06-17 - Padronizacao de scripts e templates

- Renomeados os scripts de `checks/estudos` para o padrao `estudo_<disciplina>.py`.
- Renomeados os scripts de `checks/projetos` para o padrao `projeto_<disciplina>.py`.
- Padronizada a estrutura interna dos scripts com `CHECK_CONFIG` e `main() -> None`.
- Criado `checks/templates/pdf_report.py` como template central dos RACs.
- Criados `checks/templates/relatorio_estudo.py` e `checks/templates/relatorio_projeto.py` como wrappers de tipo de relatorio.
- Removidos os templates antigos `Template_pdf_estudo.py` e `Template_pdf_projeto.py`.
- Corrigida a resolucao de caminhos para usar a raiz real do projeto, em vez do diretorio corrente do terminal.
- Removidas as imagens nao utilizadas `figs/icone.png` e `figs/logo_icone.jpeg`.
- Atualizados `README.md` e `requirements.txt` para refletir a estrutura atual.
