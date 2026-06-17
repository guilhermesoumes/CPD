# Changelog

## 2026-06-17

### Reorganizacao inicial

- Inicializado repositorio Git em `C:\AmbienteDeTeste\CPDv3`.
- Criado `funcs/rag_engine.py` para centralizar extracao de PDF, limpeza de texto, criacao de embeddings, recuperacao e consulta ao LLM.
- Criado `funcs/check_runner.py` para padronizar execucao das verificacoes, calculo de conformidade e geracao dos RACs.
- Substituidos scripts longos de `checks/Estudos` e `checks/Projetos` por wrappers declarativos com `CheckConfig`.
- Mantido `teste_com_IA/Perguntas_IA.py` como wrapper de compatibilidade para chamadas antigas.
- Corrigido versionamento de nomes em `funcs/common_functions.py` para considerar o codigo real da disciplina.
- Atualizado `requirements.txt` para conter apenas dependencias usadas pelo projeto reorganizado.
- Atualizado `.gitignore` para ignorar `*.pyc`, `vectorstores/` e `config.json`.
- Ajustado `Template_pdf_projeto.py` para aceitar a etapa de relacao de documentos gerais como opcional.
- Criado `config.example.json` sem caminhos locais para documentar a estrutura esperada de configuracao.

### Validacao e limpeza

- Removidos `__pycache__` e arquivos `.pyc` gerados.
- Rodada verificacao de sintaxe com `python -m py_compile` em todos os scripts Python.
- Preparado commit inicial apos validacao.


